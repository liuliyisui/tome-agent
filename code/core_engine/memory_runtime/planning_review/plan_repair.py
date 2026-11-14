"""A separate, bounded agent that patches only identified failed actions."""

import copy
import re

from tome_writer.domain import ContractError, canonical, strict_json
from tome_writer.models import ModelRequest


def reference_subject(selector, choices, records):
    if isinstance(selector, dict):
        if "record_subject" in selector:
            return selector["record_subject"]
        selector = {
            k: v
            for k, v in selector.items()
            if k not in ("record_kind", "record_subject", "record_property_name")
        }
        if len(selector) != 1:
            return None
        key, value = next(iter(selector.items()))
        if key == "record_choice" and type(value) is int and 1 <= value <= len(choices):
            selector = choices[value - 1]
        elif key in ("ref", "reference_id", "id"):
            return reference_subject(value, choices, records)
        else:
            return None
    return next(
        (r.get("subject") for r in records if r.get("reference_id") == selector), None
    )


def protect_targets(original, replacement, choices, records):
    if replacement.get("statement") != original.get("statement"):
        raise ContractError("Local state repair cannot rewrite the event statement")
    for index, old in enumerate(original.get("changes", [])):
        if index >= len(replacement.get("changes", [])):
            raise ContractError("Local repair removed a protected state change")
        new = replacement["changes"][index]
        before = old.get("subject") or next(
            (
                reference_subject(old[f], choices, records)
                for f in ("fact_ref", "intention_ref")
                if f in old
            ),
            None,
        )
        after = new.get("subject") or next(
            (
                reference_subject(new[f], choices, records)
                for f in ("fact_ref", "intention_ref")
                if f in new
            ),
            None,
        )
        if before and after and before != after:
            raise ContractError(
                "Repair selected another subject instead of preserving target " + before
            )
        target = old.get("fact_ref")
        if isinstance(target, dict) and target.get("record_property_name"):
            declared = target["record_property_name"]
            original_row = next(
                (
                    r
                    for r in records
                    if r.get("subject") == before
                    and declared in (r.get("property_name"), r.get("attribute_label"))
                ),
                {},
            )
            allowed = {
                v
                for v in (
                    declared,
                    original_row.get("property_name"),
                    original_row.get("attribute_label"),
                )
                if v
            }
            replacement = new.get("fact_ref", {})
            replacement_property = (
                replacement.get("record_property_name")
                if isinstance(replacement, dict)
                else None
            )
            replacement_property = replacement_property or new.get("property_name")
            if replacement_property not in allowed:
                raise ContractError(
                    "Repair changed the protected target property " + declared
                )


def repair(
    gateway, proposal, choices, details, trace, *, reference_records=(), validator=None
):
    allowed = set()

    def locate(value):
        if isinstance(value, dict):
            path = value.get("path", "")
            match = re.search(r"scenes\[(\d+)\]\.beats\[(\d+)\]", path)
            if match:
                allowed.add(tuple(map(int, match.groups())))
            for child in value.values():
                locate(child)
        elif isinstance(value, list):
            for child in value:
                locate(child)

    locate(details)
    if not allowed:
        raise ContractError("No action locator available for local repair")
    payload = {
        "proposal": proposal,
        "reference_choices": choices,
        "errors": details,
        "reference_records": copy.deepcopy(reference_records),
        "allowed_action_positions": [list(v) for v in sorted(allowed)],
        "output_contract": {
            "patches": [
                {
                    "scene_index": 0,
                    "beat_index": 0,
                    "replacement": "完整公开动作对象；不含程序编号",
                }
            ]
        },
    }
    from .reference_choices import formal_operation_catalogue

    payload["operation_schemas"] = formal_operation_catalogue()
    if len(canonical(payload).encode("utf-8")) > 96000:
        raise ContractError("Local repair input exceeds its budget")
    # This is an independent role, not another request to the original planner.
    system = (
        "你是结构化状态局部修复员，不构思新剧情。只修allowed_action_positions列出的动作。"
        "输出JSON patches数组，每项scene_index、beat_index（0基）和replacement完整公开动作。"
        "statement逐字保留，原changes顺序及各项主体不变，可修操作类别、引用和必要依赖，并在末尾补充实际状态。"
        "reference_records含主体/属性/值，不能只挑类型合格编号，更不能把批次的变化写进某个人的态度。"
        "计划修改用revise_intention/intention_ref；新的已发生状态另用establish_fact/current_state。"
        "引用按目录或本章位置，不造编号，不删除正确变更。"
    )
    for attempt in range(2):
        if len(canonical(payload).encode("utf-8")) > 96000:
            raise ContractError("Local repair input exceeds its budget")
        response = gateway.complete(
            ModelRequest("state_repair", system, payload, 16384)
        )
        entry = {
            "role": "state_repair",
            "attempt": attempt + 1,
            "raw_output": response.content,
            "finish_reason": response.finish_reason,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": response.cost_usd,
        }
        trace.append(entry)
        try:
            if response.finish_reason not in ("stop", None):
                raise ContractError("Incomplete state repair reply")
            from .pipeline import normalize

            result, _ = normalize(strict_json(response.content))
            if (
                not isinstance(result, dict)
                or set(result) != {"patches"}
                or not isinstance(result["patches"], list)
                or not result["patches"]
            ):
                raise ContractError("Repair must return nonempty patches")
            updated = copy.deepcopy(proposal)
            seen = set()
            for row in result["patches"]:
                if not isinstance(row, dict) or set(row) != {
                    "scene_index",
                    "beat_index",
                    "replacement",
                }:
                    raise ContractError("Invalid repair patch fields")
                pos = (row["scene_index"], row["beat_index"])
                if (
                    any(type(i) is not int for i in pos)
                    or pos not in allowed
                    or pos in seen
                ):
                    raise ContractError(
                        "Repair cannot change an unlisted or duplicate action"
                    )
                if not isinstance(row["replacement"], dict):
                    raise ContractError("Repair replacement must be an action")
                protect_targets(
                    proposal["scenes"][pos[0]]["beats"][pos[1]],
                    row["replacement"],
                    choices,
                    reference_records,
                )
                updated["scenes"][pos[0]]["beats"][pos[1]] = copy.deepcopy(
                    row["replacement"]
                )
                seen.add(pos)
            if validator is not None:
                validator(updated)
            entry["status"] = "REPAIRED"
            return updated
        except (ContractError, TypeError, KeyError, IndexError) as exc:
            entry.update(status="REJECTED", error=str(exc))
            if attempt:
                raise ContractError(
                    "Local state repair remained invalid: " + str(exc)
                ) from exc
            payload["repair_feedback"] = {
                "error": str(exc),
                "details": getattr(exc, "repair_details", {}),
                "previous_output": response.content,
            }
