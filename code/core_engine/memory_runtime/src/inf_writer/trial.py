"""Bounded real-writing trial helpers. No credential discovery on import."""
import json
import re
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from .agents import build_agents
from .domain import ContractError, Snapshot, canonical, digest, strict_json
from .models import Budget, ModelGateway
from .runtime import Coordinator
from .storage import FileStore


def save_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def load_authorized_nst_secret(path):
    """Read only the exact user-authorized dotenv; never eval/import NST code."""
    values = {}
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", line)
        if not match:
            continue
        name, value = match.groups()
        if name not in ("DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL", "DEEPSEEK_MODEL"):
            continue
        if name in values:
            raise ContractError("Duplicate authorized credential configuration field")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        values[name] = value
    if not values.get("DEEPSEEK_API_KEY"):
        raise ContractError("Authorized credential field is missing")
    if values.get("DEEPSEEK_MODEL") != "deepseek-flash":
        raise ContractError("Model differs from verified trial pricing; stop before requests")
    url = urlsplit(values.get("DEEPSEEK_BASE_URL", ""))
    if (url.scheme != "https" or url.hostname != "api.deepseek.com" or url.username
            or url.password or url.query or url.fragment or url.port not in (None, 443)
            or url.path.rstrip("/") not in ("", "/v1", "/beta")):
        raise ContractError("Credential target is not the verified official DeepSeek endpoint")
    prefix = "/beta" if url.path.rstrip("/") == "/beta" else ""
    return values["DEEPSEEK_API_KEY"], "https://api.deepseek.com" + prefix + "/chat/completions", "deepseek-flash"


class RecordedProvider:
    def __init__(self, provider, output):
        self.provider, self.output, self.calls = provider, Path(output), 0

    def complete(self, request):
        # A conservative byte limit bounds local inputs before any HTTP request.
        encoded = canonical({"system": request.system, "payload": request.payload}).encode("utf-8")
        if len(encoded) > 120_000:
            raise ContractError("Trial request input exceeds 120000-byte safety bound")
        self.calls += 1
        prefix = self.output / f"call_{self.calls:03d}"
        save_new(prefix.with_suffix(".request.json"), {
            "at": datetime.now().astimezone().isoformat(), "role": request.role,
            "system": request.system, "payload": request.payload,
            "max_output_tokens": request.max_output_tokens, "input_bytes": len(encoded),
        })
        print(json.dumps({"event": "request", "number": self.calls, "role": request.role}, ensure_ascii=False), flush=True)
        try:
            reply = self.provider.complete(request)
        except Exception as exc:
            # Do not serialize arbitrary exception messages or provider repr/secrets.
            save_new(prefix.with_suffix(".error.json"), {"type": type(exc).__name__, "usage_unknown": True})
            raise
        save_new(prefix.with_suffix(".response.json"), asdict(reply))
        return reply


def run_trial(output, provider, plan):
    if plan.get("execution_mode") == "draft_first":
        return run_draft_trial(output, provider, plan)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    save_new(output / "execution.json", {"started_at": datetime.now().astimezone().isoformat(), "plan_sha256": digest(canonical(plan))})
    store = FileStore(output / "states")
    store.initialize(Snapshot("novel", plan["goal"], plan["constraints"]))
    budget = Budget(max_calls=plan["max_calls"], max_cost_usd=plan["max_cost_usd"], max_seconds=1800)
    recorder = RecordedProvider(provider, output)
    agents = build_agents(ModelGateway(recorder, budget, reserve_per_call=0.06))
    for agent in agents.values():
        agent.max_output_tokens = 8192
    coordinator = Coordinator(store, agents)
    outcomes = []
    started = time.monotonic()
    for chapter in range(1, plan["chapters"] + 1):
        feedback = ""
        for attempt in (1, 2):
            state = store.load("novel")
            written = sum(len(re.findall(r"[\u3400-\u9fff]", ch["text"])) for ch in state.chapters)
            remaining = plan["chapters"] - chapter + 1
            target = max(1100, min(1800, (plan["target_han_chars"] - written + remaining - 1) // remaining))
            instruction = (
                f"全书共{plan['chapters']}章，现在写第{chapter}章。正文目标约{target}个汉字（不计标点），"
                "用完整场景、动作和对话展开，不要用梗概代替正文。规划应控制本章节奏，不提前结束全书。"
                "若是最后一章，应完成主要冲突的解决与人物选择的后果，不另启未完成主线。"
                "记忆只存后续写作需要的明确事实；每项quote必须逐字引用本章正文，不能概括或改写引句。"
                + feedback
            )
            outcome = coordinator.write_next("novel", f"chapter{chapter}_attempt{attempt}", instruction)
            outcomes.append(asdict(outcome))
            save_new(output / f"chapter_{chapter:02d}_attempt_{attempt}.json", asdict(outcome))
            print(json.dumps({"event": "chapter", "number": chapter, "attempt": attempt,
                              "status": outcome.status, "calls": budget.calls,
                              "cost_upper_usd": budget.cost_upper_usd}, ensure_ascii=False), flush=True)
            if outcome.status in ("COMMITTED", "ALREADY_COMMITTED"):
                break
            if outcome.error and any(marker in outcome.error for marker in ("ProviderError", "budget", "deadline", "reservation")):
                break  # No blind network retry or spending beyond budget.
            feedback = " 上一次未提交；请根据以下程序/审核反馈修正，但不要改写已接受章节：" + str(outcome.error or outcome.issues)
        else:
            break
        if outcome.status not in ("COMMITTED", "ALREADY_COMMITTED"):
            break
    state = store.load("novel")
    prose = "# " + plan["title"] + "\n\n" + "\n\n".join(
        f"## 第{ch['number']}章 {ch['title']}\n\n{ch['text']}" for ch in state.chapters)
    with (output / "正文.md").open("x", encoding="utf-8") as stream:
        stream.write(prose + "\n")
    han = sum(len(re.findall(r"[\u3400-\u9fff]", ch["text"])) for ch in state.chapters)
    result = {"scope": "FUNCTIONAL_TRIAL_NOT_COMPARATIVE_EXPERIMENT", "model": plan["model"],
              "chapters": len(state.chapters), "target_chapters": plan["chapters"],
              "han_chars": han, "target_han_chars": plan["target_han_chars"],
              "non_whitespace_body_chars": sum(len(re.sub(r"\s", "", ch["text"])) for ch in state.chapters),
              "all_chapters_committed": len(state.chapters) == plan["chapters"],
              "length_target_met": han >= plan["target_han_chars"],
              "calls": budget.calls, "recorded_provider_calls": recorder.calls,
              "input_tokens": budget.input_tokens, "output_tokens": budget.output_tokens,
              "cost_upper_usd_estimate_not_bill": budget.cost_upper_usd,
              "max_cost_usd": plan["max_cost_usd"], "elapsed_seconds": time.monotonic() - started,
              "active_facts": len(state.active_facts()), "archived_versions": len(state.history),
              "outcomes": outcomes, "story_sha256": digest(prose + "\n")}
    save_new(output / "result.json", result)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


def run_draft_trial(output, provider, plan, *, resume_from=None):
    """Produce prose despite quality failures, without approving failed memory."""
    from .drafting import DraftSession
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    maximum = plan.get("max_chapters", plan["chapters"])
    if type(maximum) is not int or not plan["chapters"] <= maximum <= 30:
        raise ContractError("Draft chapter cap must cover nominal chapters and be at most 30")
    initial = Snapshot("novel", plan["goal"], plan["constraints"])
    prior_rows, inherited = [], []
    if resume_from is not None:
        parent = Path(resume_from).resolve()
        if output.resolve().is_relative_to(parent) or parent.is_relative_to(output.resolve()):
            raise ContractError("Continuation must not overlap the original run")
        previous = strict_json((parent / "result.json").read_text(encoding="utf-8"))
        count = previous["chapters"]
        if type(count) is not int or not 0 < count < plan["chapters"]:
            raise ContractError("Continuation requires an incomplete nonempty draft")
        for number in range(1, count + 1):
            record = strict_json((parent / "working" / f"draft_chapter_{number:03d}.json").read_text(encoding="utf-8"))
            state = Snapshot.from_dict(record["state"])
            row = record["chapter"]
            if (record["mode"] != "DRAFT_FIRST_NOT_FORMAL" or len(state.chapters) != number
                    or state.goal != plan["goal"] or state.constraints != plan["constraints"]
                    or state.chapters[:-1] != initial.chapters or row["chapter_number"] != number
                    or row["status"] not in ("DRAFT_CHECKED", "DRAFT_UNCHECKED")
                    or row != previous["outcomes"][number - 1]):
                raise ContractError("Inconsistent continuation checkpoint or story settings")
            prior_rows.append(row)
            inherited.append(record)
            initial = state
    save_new(output / "execution.json", {"started_at": datetime.now().astimezone().isoformat(),
             "execution_mode": "draft_first", "plan_sha256": digest(canonical(plan)),
             "inherited_chapters": len(prior_rows), "resume_from": str(resume_from) if resume_from else None})
    budget = Budget(max_calls=plan["max_calls"], max_cost_usd=plan["max_cost_usd"], max_seconds=1800)
    recorder = RecordedProvider(provider, output)
    agents = build_agents(ModelGateway(recorder, budget, reserve_per_call=0.06),
                          review_contract_version=plan.get('review_contract_version',0),
                          review_transport_version=plan.get('review_transport_version',0))
    for agent in agents.values():
        agent.max_output_tokens = 8192
    session = DraftSession(output / "working", initial, agents, rows=prior_rows)
    session.output.mkdir(parents=True, exist_ok=True)
    for record in inherited:
        save_new(session.output / f"draft_chapter_{record['chapter']['chapter_number']:03d}.json", record)
    started, stop = time.monotonic(), None
    for number in range(len(initial.chapters) + 1, maximum + 1):
        written = sum(len(re.findall(r"[\u3400-\u9fff]", chapter["text"])) for chapter in session.state.chapters)
        if number > plan["chapters"] and written >= plan["target_han_chars"]:
            break
        remaining = max(1, plan["chapters"] - number + 1)
        target = max(1100, min(2200, (plan["target_han_chars"] - written + remaining - 1) // remaining))
        instruction = (
            f"当前优先完成连续草稿，目标{plan['target_han_chars']}汉字，名义{plan['chapters']}章，现在是第{number}章。"
            f"本章正文目标约{target}汉字（不计标点），用完整场景和对话，不用梗概。"
            "保持与已写草稿的情节衔接；unresolved_chapters仅代表未解决问题，不能假称前文通过审核。"
            "不要在名义最后一章之前结束主线；到最后一章应解决主要冲突。"
            "如果超过名义章数，补写与既有结局相容的后续场景，不推翻已写事实或靠重复原句凑长度。"
        )
        row = session.write_next(instruction)
        print(json.dumps({"event": "draft_chapter", "number": number, "status": row["status"],
                          "calls": budget.calls, "cost_upper_usd": budget.cost_upper_usd}, ensure_ascii=False), flush=True)
        if row["stop_reason"] or row["status"] == "NO_DRAFT":
            stop = row["stop_reason"] or "NO_USABLE_DRAFT"
            break
    state = session.state
    prose = "# " + plan["title"] + "\n\n> 草稿优先试写；待修问题另见问题清单，不表示已通过质量审核。\n\n"
    prose += "\n\n".join(f"## 第{chapter['number']}章 {chapter['title']}\n\n{chapter['text']}"
                           for chapter in state.chapters)
    with (output / "正文.md").open("x", encoding="utf-8") as stream:
        stream.write(prose + "\n")
    pending = [row for row in session.rows if row["status"] != "DRAFT_CHECKED"]
    save_new(output / "问题清单.json", {"scope": "unresolved model/program reports, not verified error counts", "chapters": pending})
    han = sum(len(re.findall(r"[\u3400-\u9fff]", chapter["text"])) for chapter in state.chapters)
    length_met = han >= plan["target_han_chars"]
    if stop is None and not length_met:
        stop = "CHAPTER_CAP_BEFORE_LENGTH_TARGET"
    result = {"scope": "FUNCTIONAL_DRAFT_TRIAL_NOT_QUALITY_EXPERIMENT", "execution_mode": "draft_first",
              "model": plan["model"], "chapters": len(state.chapters), "target_chapters": plan["chapters"],
              "max_chapters": maximum, "han_chars": han, "target_han_chars": plan["target_han_chars"],
              "length_target_met": length_met, "draft_completed": length_met and len(state.chapters) >= plan["chapters"],
              "all_chapters_committed": False, "formal_chapters": 0,
              "checked_draft_chapters": sum(row["status"] == "DRAFT_CHECKED" for row in session.rows),
              "pending_draft_chapters": len(pending), "quality_gate_passed": not pending and length_met,
              "stop_reason": stop, "calls": budget.calls, "recorded_provider_calls": recorder.calls,
              "input_tokens": budget.input_tokens, "output_tokens": budget.output_tokens,
              "cost_upper_usd_estimate_not_bill": budget.cost_upper_usd, "max_cost_usd": plan["max_cost_usd"],
              "elapsed_seconds": time.monotonic() - started, "active_facts": len(state.active_facts()),
              "inherited_chapters": len(inherited), "usage_scope": "this invocation only; parent usage is separate",
              "archived_versions": len(state.history), "outcomes": session.rows, "story_sha256": digest(prose + "\n")}
    save_new(output / "result.json", result)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result
