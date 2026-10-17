"""Bounded chapter tool loop over a disposable workspace; transport injected."""
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
import re
from .state import canonical, digest, Workspace
from .submissions import submit_groups
from .checkpoints import save_checkpoint
from .storage import save_payload


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class Response:
    content: str = ""
    calls: list[ToolCall] = None
    finish_reason: str = "stop"
    usage: dict = None
    reasoning_content: str | None = None


class Model(Protocol):
    def complete(self, messages: list[dict], tools: list[dict]) -> Response: ...


@dataclass
class Limits:
    max_turns: int = 30
    read_calls: int = 8
    search_calls: int = 8
    correct_calls: int = 3
    fact_bytes: int = 12000
    read_chars: int = 12000
    min_length_ratio: float = .8
    max_length_ratio: float = 1.3


def count_units(text):
    return len(re.findall(r"[\u3400-\u9fff]|[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*", text))


GUIDANCE = """按冻结大纲逐章写作。先read/search相关前文，再write完整正文，再update故事状态，最后仅回复DONE。
update使用groups；每个候选只填写一次entry。使用稳定属性key，值改变时update，程序归档旧版本。
只引用本章接受正文。计划不是完成；历史不是当前；主观认知使用认知者subject和belief_键。
未提及不是删除。单次观察不能建立长期人格。不确定用defer，短暂无关内容用omit。
依赖变化同组或depends_on相连，失败修复原group id；pending未清不得DONE。
update成功后正文不可再修改。不能通过改前文规避事实约束。引文存在不代表语义正确。
read/search/correct预算有限。工具失败时依据反馈修正，不伪造成功。
"""


class ChapterAgent:
    def __init__(self, model: Model, limits=None):
        self.model = model
        self.limits = limits or Limits()
        self.last_attempt = None
        self._running = False

    def run(self, workspace: Workspace, checkpoint: Path, resume_attempt=None):
        if self._running:
            raise ValueError("Concurrent chapters are unsupported")
        workspace.validate()
        number = len(workspace.chapters) + 1
        if number > len(workspace.outline):
            raise ValueError("Story outline already complete")
        from .tools import chapter_tools
        limits = self.limits
        official_hash = digest(canonical(workspace.to_dict()))
        trial = deepcopy(workspace)
        draft, updated, messages, trace = None, False, [], []
        counters = dict(read=0, search=0, correct=0)
        turns = 0
        if resume_attempt:
            if resume_attempt["base_hash"] != official_hash or resume_attempt["number"] != number:
                raise ValueError("Attempt does not match official checkpoint")
            trial = Workspace.from_dict(resume_attempt["working"])
            if trial.fingerprint() != workspace.fingerprint():
                raise ValueError("Attempt configuration changed")
            draft, updated = resume_attempt["draft"], resume_attempt["updated"]
            messages, trace = deepcopy(resume_attempt["messages"]), deepcopy(resume_attempt["trace"])
            counters, turns = deepcopy(resume_attempt["counters"]), resume_attempt["turns"]
            sources = {**trial.chapters, **({number: draft} if draft else {})}
            trial.state.check_sources(sources)
        else:
            messages = [{"role": "system", "content": GUIDANCE}, {"role": "user", "content": canonical({
                "story": workspace.prompt, "outline": workspace.outline,
                "chapter": workspace.outline[number-1], "number": number,
                "state": workspace.state.view(limits.fact_bytes),
                "length_unit": "CJK characters plus ASCII words"})}]
        attempt_path = Path(str(checkpoint) + ".attempt.json")

        def snapshot(status, error=None):
            self.last_attempt = {"status": status, "error": error, "base_hash": official_hash,
                "number": number, "working": trial.to_dict(), "draft": draft, "updated": updated,
                "messages": deepcopy(messages), "trace": deepcopy(trace),
                "counters": deepcopy(counters), "turns": turns}
            save_payload(self.last_attempt, attempt_path)

        def dispatch(call):
            nonlocal draft, updated
            args = call.arguments
            if not isinstance(args, dict):
                raise ValueError("Tool arguments must be an object")
            name = call.name
            if name in counters:
                counters[name] += 1
                budget = getattr(limits, name + "_calls")
                if counters[name] > budget:
                    raise ValueError(f"{name} budget exceeded")
            if name == "read":
                if set(args) != {"chapter"} or type(args["chapter"]) is not int or args["chapter"] not in trial.chapters:
                    raise ValueError("read requires an existing prior chapter")
                text = trial.chapters[args["chapter"]]
                return {"ok": True, "text": text[:limits.read_chars], "truncated": len(text) > limits.read_chars}
            if name == "search":
                if set(args) != {"query"} or not isinstance(args["query"], str) or not args["query"].strip():
                    raise ValueError("search requires nonempty query")
                hits = []
                for n, text in sorted(trial.chapters.items()):
                    index = text.casefold().find(args["query"].casefold())
                    if index >= 0:
                        hits.append({"chapter": n, "excerpt": text[max(0,index-100):index+300]})
                return {"ok": True, "hits": hits[:10]}
            if name == "correct":
                if set(args) != {"chapter", "old", "new"} or type(args["chapter"]) is not int:
                    raise ValueError("correct requires chapter, old, new")
                n = args["chapter"]
                if not isinstance(args["old"], str) or not args["old"] or not isinstance(args["new"], str):
                    raise ValueError("Exact nonempty old and string new required")
                source = draft if n == number else trial.chapters.get(n)
                if source is None or source.count(args["old"]) != 1:
                    raise ValueError("Correction must match exactly once")
                if any(r["chapter"] == n for r in trial.state.receipts.values()):
                    raise ValueError("Source-bound prose requires explicit memory review before editing")
                changed = source.replace(args["old"], args["new"], 1)
                if n == number:
                    draft, updated = changed, False
                else:
                    trial.chapters[n] = changed
                return {"ok": True}
            if name == "write":
                if set(args) != {"text"} or not isinstance(args["text"], str) or not args["text"].strip():
                    raise ValueError("write requires complete nonempty text")
                if any(r["chapter"] == number for r in trial.state.receipts.values()):
                    raise ValueError("Accepted memory groups bind the current prose")
                target = workspace.outline[number-1].get("target_units", workspace.config.get("chapter_target_units", 1000))
                actual = count_units(args["text"])
                if not limits.min_length_ratio * target <= actual <= limits.max_length_ratio * target:
                    return {"ok": False, "error": "Length outside target range", "actual": actual,
                            "target": target, "min": limits.min_length_ratio*target, "max": limits.max_length_ratio*target}
                draft, updated = args["text"], False
                return {"ok": True, "units": actual}
            if name == "update":
                if draft is None:
                    raise ValueError("Accepted write required before update")
                trial.state.check_sources({**trial.chapters, number: draft})
                result = submit_groups(trial.state, args, number, draft)
                updated = result["ok"]
                return result
            raise ValueError("Unknown tool")

        self._running = True
        try:
            while turns < limits.max_turns:
                response = self.model.complete(deepcopy(messages), chapter_tools())
                turns += 1
                calls = response.calls or []
                if response.finish_reason not in ("stop", "tool_calls"):
                    raise ValueError("Truncated or incomplete model response")
                if calls and (response.finish_reason != "tool_calls" or len({c.id for c in calls}) != len(calls)):
                    raise ValueError("Invalid tool response")
                message = {"role": "assistant", "content": response.content}
                if response.reasoning_content is not None:
                    message["reasoning_content"] = response.reasoning_content
                if calls:
                    message["tool_calls"] = [{"id": c.id, "type": "function", "function": {
                        "name": c.name, "arguments": canonical(c.arguments)}} for c in calls]
                messages.append(message)
                trace.append({"turn": turns, "usage": response.usage, "finish_reason": response.finish_reason})
                if not calls:
                    if response.content.strip() != "DONE" or draft is None or not updated or trial.state.pending:
                        raise ValueError("Completion requires accepted write, successful update, no pending and DONE")
                    trial.chapters[number] = draft
                    trial.validate()
                    trial.state.view(limits.fact_bytes)
                    snapshot("READY_TO_COMMIT")
                    save_checkpoint(trial, checkpoint)
                    self.last_attempt["status"] = "COMPLETED"
                    # Official checkpoint is authoritative; the attempt is not promoted separately.
                    return trial
                for call in calls:
                    try:
                        result = dispatch(call)
                    except (ValueError, KeyError, TypeError) as exc:
                        result = {"ok": False, "error": str(exc)}
                    messages.append({"role": "tool", "tool_call_id": call.id, "content": canonical(result)})
                    trace.append({"tool": call.name, "arguments": deepcopy(call.arguments), "result": deepcopy(result)})
                snapshot("IN_PROGRESS")
            raise ValueError("Chapter turn budget exhausted")
        except Exception as exc:
            snapshot("FAILED", str(exc))
            raise
        finally:
            self._running = False
