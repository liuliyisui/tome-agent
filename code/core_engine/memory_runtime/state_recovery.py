"""Append-only source-bound state recovery; failed plans are never replayed."""

import copy

from inf_writer.domain import (
    ContractError,
    canonical,
    digest,
    evidence_segments,
    fields,
    strict_json,
)
from inf_writer.models import ModelRequest

SYSTEM = (
    "你从已保存正文补录章末实际状态，不改正文、不沿用失败规划。输出JSON participants字符串数组、actions数组。"
    "actions每项仅evidence_position、quote、changes。位置选evidence目录，quote逐字摘录其中能支持变更的原文，"
    "changes按operation_schemas使用公开操作；没有动作编号和记录编号，由程序分配。"
    "必须提取本章明确的重要最终状态、任务变化、人物所知和责任归属；不为通过而只交空变更。"
    "当前事实与计划严格分开，修订旧计划用revise_intention/intention_ref，已发生的新状态用establish_fact/current_state。"
    "已有同主体同属性事实用change_fact_value/fact_ref。所有已有引用从reference_records按主体、属性、值选择。"
    "fact_ref必须含record_subject与record_property_name，可复制记录的update_selector；程序按人物和属性共同绑定，不能选别人的属性。"
    "人物自述内容可记为character_belief，不凭说法断言客观事实。不得覆盖来源章节之后的新状态。"
    "如果较晚状态已覆盖旧变化，保留较晚状态，只提取旧章仍需保留的事件或知识。"
    "只能使用给定正文与记录，不写推测的新结局，不输出原文以外的statement。"
)


def transactions(book):
    """Event history including recovery commits at their actual append point."""
    repairs = book.get("state_recovery_commits", [])
    for chapter in book["chapters"]:
        if "event_commit" in chapter:
            yield chapter["number"], chapter["event_commit"]
        for entry in repairs:
            if entry["after_chapter"] == chapter["number"]:
                yield entry["source_chapter"], entry["commit"]


def verify_recoveries(book):
    from .event_first import verify

    for key, job in book.get("state_repair_jobs", {}).items():
        number = int(key)
        if (
            not 1 <= number <= len(book["chapters"])
            or job.get("chapter_sha256") != book["chapters"][number - 1]["sha256"]
        ):
            raise ContractError("Pending state recovery source mismatch")
    prior = 0
    for seq, entry in enumerate(book.get("state_recovery_commits", []), 1):
        if (
            entry["sequence"] != seq
            or type(entry["after_chapter"]) is not int
            or not 1
            <= entry["source_chapter"]
            <= entry["after_chapter"]
            <= len(book["chapters"])
            or entry["after_chapter"] < prior
        ):
            raise ContractError("Invalid state recovery order")
        prior = entry["after_chapter"]
        chapter = book["chapters"][entry["source_chapter"] - 1]
        if entry["source_sha256"] != digest(chapter["text"]):
            raise ContractError("State recovery prose hash mismatch")
        commit = verify(entry["commit"])
        if commit["chapter"] != entry["source_chapter"]:
            raise ContractError("Recovery chapter identity mismatch")
        beats = [b for s in commit["scenes"] for b in s["beats"]]
        if len(beats) != len(entry["bindings"]):
            raise ContractError("Recovery event coverage mismatch")
        segments = evidence_segments(chapter["text"])
        for beat, binding in zip(beats, entry["bindings"], strict=False):
            pos = binding["evidence_position"]
            quote = binding["quote"]
            if (
                type(pos) is not int
                or not 1 <= pos <= len(segments)
                or not quote
                or quote not in segments[pos - 1]["text"]
                or beat["statement"] != quote
            ):
                raise ContractError("Recovery event lacks actual prose source")
        receipt = (
            book["memory"].get("state_recovery_projection", {}).get(commit["sha256"])
        )
        if not receipt or receipt["source_sha256"] != entry["source_sha256"]:
            raise ContractError("Recovered state lacks memory projection")
        versions = list(book["memory"]["items"].values()) + [
            h["item"] for h in book["memory"].get("history", [])
        ]
        if len(receipt["records"]) != len(commit["memory_projection"]):
            raise ContractError("Recovery memory coverage missing")
        for binding, row in zip(
            receipt["records"], commit["memory_projection"], strict=False
        ):
            if binding["projection_ref"] != row["ref"] or not any(
                v["id"] == binding["memory_id"]
                and v["claim"] == row["claim"]
                and v["subject"] == row["subject"]
                and v["attribute"] == row["attribute"]
                and v["kind"] == row["kind"]
                and any(
                    s["chapter_number"] == chapter["number"]
                    and s["chapter_sha256"] == chapter["sha256"]
                    and row["claim"] in s["quote"]
                    for s in v["sources"]
                )
                for v in versions
            ):
                raise ContractError("Recovery memory source changed")


def directory(book, query):
    from .continuity import context_view
    from .event_references import catalogue, public_state_view
    from .meaning_organizer import reference_meanings

    meanings = reference_meanings(book)
    plans = catalogue(book)["plans"]
    plans = {
        i: r
        for i, r in plans.items()
        if meanings.get("pending_intention:" + i, {}).get("task_state")
        not in ("completed", "cancelled", "superseded")
    }
    view = public_state_view(context_view(book["writing_state"], query, plans=plans))
    from .projection_grounding import qualify_state_view

    view = qualify_state_view(book, view)
    records = view["records"]
    for i, r in enumerate(records, 1):
        r["record_choice"] = i
        if r["record_kind"] == "fact_record":
            r["update_selector"] = {
                "record_subject": r["subject"],
                "record_property_name": r["property_name"],
            }
    return records, [r["reference_id"] for r in records]


def _packet(book, number, value, records, choices, sequence):
    from .event_first import prepare
    from .event_references import catalogue
    from .reference_choices import compile_plan

    fields(value, ("participants", "actions"))
    if (
        not isinstance(value["participants"], list)
        or not value["participants"]
        or any(not isinstance(p, str) or not p.strip() for p in value["participants"])
    ):
        raise ContractError("Recovery participants must be nonempty names")
    if not isinstance(value["actions"], list) or not value["actions"]:
        raise ContractError("Recovery needs source-bound actions")
    chapter = book["chapters"][number - 1]
    segments = evidence_segments(chapter["text"])
    beats = []
    bindings = []
    by_ref = {r["reference_id"]: r for r in records}
    for action in value["actions"]:
        fields(action, ("evidence_position", "quote", "changes"))
        pos = action["evidence_position"]
        quote = action["quote"]
        if (
            type(pos) is not int
            or not 1 <= pos <= len(segments)
            or not isinstance(quote, str)
            or not quote.strip()
            or quote not in segments[pos - 1]["text"]
        ):
            raise ContractError("Recovery quote must occur in selected saved prose")
        if not isinstance(action["changes"], list):
            raise ContractError("Recovery changes must be a list")
        for change in action["changes"]:
            for field in ("fact_ref", "intention_ref"):
                selector = change.get(field)
                selected = None
                if isinstance(selector, str):
                    selected = by_ref.get(selector)
                elif (
                    isinstance(selector, dict)
                    and type(selector.get("record_choice")) is int
                    and 1 <= selector["record_choice"] <= len(records)
                ):
                    selected = records[selector["record_choice"] - 1]
                if selected and selected.get("chapter", 0) > number:
                    raise ContractError(
                        "Older recovery cannot overwrite a newer record"
                    )
        beats.append(
            {
                "statement": quote,
                "assertion_scope": "performed_action",
                "requires": [],
                "changes": copy.deepcopy(action["changes"]),
            }
        )
        bindings.append({"evidence_position": pos, "quote": quote})
    if not any(b["changes"] for b in beats):
        raise ContractError("Empty state extraction cannot clear a recovery job")
    public = {
        "number": number,
        "title": chapter["title"],
        "brief": "由已保存正文补录实际状态",
        "future_updates": [],
        "scenes": [
            {
                "purpose": "原文状态补录",
                "participants": value["participants"],
                "beats": beats,
            }
        ],
    }
    compiled = compile_plan(
        public,
        choices,
        number,
        reference_records=records,
        id_namespace=f"recovery{sequence:04d}_",
        require_target_identity=True,
    )
    for scene in compiled["scenes"]:
        for action in scene["beats"]:
            for change in action["changes"]:
                for field in ("fact_ref", "intention_ref"):
                    selected = by_ref.get(change.get(field))
                    if selected and selected.get("chapter", 0) > number:
                        raise ContractError(
                            "Older recovery cannot overwrite a newer record"
                        )
    packet = prepare(
        book["writing_state"], compiled, number, references=catalogue(book)
    )
    return packet, bindings


def recover(book, number, gateway, trace):
    """Two output attempts; caller publishes only after the whole transaction."""
    from .reference_choices import FIELD_KINDS, formal_operation_catalogue

    chapter = book["chapters"][number - 1]
    if digest(chapter["text"]) != chapter["sha256"]:
        raise ContractError("Saved chapter hash mismatch")
    if (
        book.get("state_repair_jobs", {}).get(str(number), {}).get("chapter_sha256")
        != chapter["sha256"]
    ):
        raise ContractError("Pending state recovery source mismatch")
    records, choices = directory(book, chapter["text"])
    sequence = len(book.get("state_recovery_commits", [])) + 1
    payload = {
        "source_chapter": number,
        "latest_chapter": len(book["chapters"]),
        "evidence": [
            {"evidence_position": i, "text": s["text"]}
            for i, s in enumerate(evidence_segments(chapter["text"]), 1)
        ],
        "reference_records": records,
        "reference_choices": choices,
        "reference_choices_by_field": {
            k: [i for i, r in enumerate(records, 1) if r["record_kind"] in v]
            for k, v in FIELD_KINDS.items()
        },
        "operation_schemas": formal_operation_catalogue(),
        "output_example": {
            "participants": ["正文中的人物"],
            "actions": [
                {
                    "evidence_position": 1,
                    "quote": "输入中真实的逐字引文",
                    "changes": [
                        {
                            "operation": "establish_fact",
                            "subject": "实际主体",
                            "property_name": "实际属性",
                            "value": "正文支持的章末状态",
                            "fact_class": "current_state",
                        }
                    ],
                }
            ],
        },
    }
    for attempt in range(2):
        if (
            len(canonical({"system": SYSTEM, "payload": payload}).encode("utf-8"))
            > 96000
        ):
            raise ContractError("Recovery input exceeds bound")
        entry = {"role": "state_recovery", "chapter": number, "attempt": attempt + 1}
        trace.append(entry)
        try:
            reply = gateway.complete(
                ModelRequest("state_repair", SYSTEM, payload, 16384)
            )
            entry.update(raw_output=reply.content, finish_reason=reply.finish_reason)
            if reply.finish_reason not in ("stop", None):
                raise ContractError("Incomplete state recovery response")
            from .pipeline import normalize

            value, _ = normalize(strict_json(reply.content))
            packet, bindings = _packet(book, number, value, records, choices, sequence)
            candidate = copy.deepcopy(book)
            commit = packet["commit"]
            memory = candidate["memory"]
            receipts = []
            by_beat = {
                b["id"]: binding
                for b, binding in zip(
                    [b for s in commit["scenes"] for b in s["beats"]],
                    bindings,
                    strict=False,
                )
            }
            from .projection_grounding import _store

            for i, row in enumerate(commit["memory_projection"], 1):
                support = [by_beat[row["beat_id"]]]
                memory, mid, _ = _store(
                    memory,
                    candidate["chapters"],
                    number,
                    row,
                    support,
                    row.get("status", "active"),
                    projection_position=1000000 + sequence * 10000 + i,
                )
                receipts.append({"projection_ref": row["ref"], "memory_id": mid})
            memory.setdefault("state_recovery_projection", {})[commit["sha256"]] = {
                "source_sha256": chapter["sha256"],
                "records": receipts,
            }
            from .meaning_organizer import organize

            memory = organize(
                memory,
                candidate["chapters"],
                len(candidate["chapters"]),
                gateway,
                trace,
            )
            from .pipeline import LayerAgent

            memory, _ = LayerAgent.intake(
                memory, candidate["chapters"], f"state-recovery-intake:{sequence}"
            )
            candidate["memory"] = memory
            candidate["writing_state"] = packet["candidate_state"]
            candidate.setdefault("state_recovery_commits", []).append(
                {
                    "sequence": sequence,
                    "after_chapter": len(candidate["chapters"]),
                    "source_chapter": number,
                    "source_sha256": chapter["sha256"],
                    "commit": commit,
                    "bindings": bindings,
                    "scope": "Model-extracted source-bound state; not a semantic completeness certificate",
                }
            )
            candidate["chapters"][number - 1]["state_recovery_status"] = "reconciled"
            candidate.setdefault("completed_state_repair_jobs", {})[str(number)] = {
                "status": "RECONCILED",
                "recovery_commit_sha256": commit["sha256"],
                "source_sha256": chapter["sha256"],
                "source_failure": copy.deepcopy(
                    candidate["state_repair_jobs"].pop(str(number))
                ),
            }
            verify_recoveries(candidate)
            entry.update(status="RECONCILED", commit_sha256=commit["sha256"])
            return candidate
        except Exception as exc:
            entry.update(
                status="DEFERRED",
                error=str(exc)
                if isinstance(exc, ContractError)
                else type(exc).__name__,
            )
            if attempt:
                raise ContractError(
                    "Saved prose state recovery remains pending"
                ) from exc
            payload["repair_feedback"] = {
                "error": entry["error"],
                "details": getattr(exc, "repair_details", {}),
            }
            if entry.get("raw_output"):
                payload["repair_feedback"]["previous_output"] = entry["raw_output"]
