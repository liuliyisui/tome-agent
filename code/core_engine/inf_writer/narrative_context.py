"""Opt-in wire projection only. Never prunes stored facts, evidence or history."""

import copy
import json

from .domain import ContractError, canonical, strict_json

MAX_REQUEST_BYTES = 120000
REPAIR_HEADROOM_BYTES = 24000


def project_facts(facts):
    # Preserve identity, values, revisions, status and patch capability marker.
    from .light_memory import lean_facts

    return lean_facts(facts)


def prepare_context(context):
    payload = copy.deepcopy(context)
    if "active_facts" in payload:
        payload["active_facts"] = project_facts(payload["active_facts"])
    return payload


def parse_planner_json(raw):
    """Recover only a complete strict object followed by one surplus brace."""
    try:
        return strict_json(raw), []
    except ContractError as original:
        stripped = raw.strip()
        try:
            _, end = json.JSONDecoder().raw_decode(stripped)
        except (ValueError, TypeError):
            raise original from None
        if stripped[end:].strip() != "}":
            raise original from None
        parsed = strict_json(stripped[:end])
        if not isinstance(parsed, dict):
            raise original from None
        return parsed, [
            {
                "rule": "planner_surplus_closing_brace",
                "removed_suffix": "}",
                "scope": "Complete strict object retained; raw reply unchanged",
            }
        ]


def normalize_planner_metadata(parsed):
    if not isinstance(parsed, dict):
        return parsed, []
    result = copy.deepcopy(parsed)
    notes = []
    if "type" in result:
        if result["type"] != "json_object":
            raise ContractError("Planner optional type must be exactly json_object")
        result.pop("type")
        notes.append(
            {
                "rule": "planner_json_object_type",
                "field": "type",
                "value": "json_object",
            }
        )
    narrative_fields = (
        "story_question",
        "chapter_change",
        "character_choice",
        "setting_notes",
        "scene_blocks",
        "scene_entry",
        "threads",
        "evidence_profiles",
        "inference_links",
        "recurring_details",
    )
    for key in narrative_fields:
        if key not in result:
            continue
        design = result.setdefault("narrative_plan", {})
        if not isinstance(design, dict):
            raise ContractError(
                "Misplaced narrative fields require an object narrative_plan"
            )
        if key in design and design[key] != result[key]:
            raise ContractError(
                "Conflicting nested and top-level narrative field: " + key
            )
        design[key] = result.pop(key)
        notes.append(
            {
                "rule": "planner_narrative_field_relocated",
                "field": key,
                "destination": "narrative_plan." + key,
            }
        )
    # Unknown fields and every event operation still pass strict validation.
    return result, notes


def event_role_context(context, role):
    """Separate the editable planner schema from the frozen realization API."""
    result = copy.deepcopy(context)
    if role == "writer" and "frozen_events" in result:
        for key in (
            "event_first_contract",
            "state_record_contract",
            "calculation_contract",
            "reference_choices",
            "reference_selection_contract",
            "reference_choices_by_kind",
            "reference_choices_by_field",
        ):
            result.pop(key, None)
        tokens = [
            "[[event:" + b["id"] + "]]"
            for s in result["frozen_events"]["scenes"]
            for b in s["beats"]
        ]
        contract = {
            "required": ["text"],
            "optional": ["type"],
            "alternatives": [{"required": ["event_revision_request"], "optional": []}],
            "example": {"text": "\n\n".join(tokens)},
            "ordered_event_tokens": tokens,
            "instruction": "输出一个JSON对象，正文全部放在text字符串里，段落用JSON换行转义。不输出clauses、events、title或其他列表。优先按示例各使用一次事件占位符；完整逐字且唯一、有序的冻结事件原句也可由程序绑定，不能改写或重复事件。实际须展开完整场景。需要新事实则只输出event_revision_request字符串。",
        }
    elif role == "planner" and "event_first_contract" in result:
        contract = {
            "required": ["number", "title", "brief", "future_updates", "scenes"],
            "optional": ["time_calculations", "type", "narrative_plan"],
            "instruction": "输出一个完整JSON对象。future_updates没有变更也必须输出空数组；scenes是本章事件方案，不写正文。",
        }
    else:
        return result
    result["output_contract"] = contract
    if role == "writer" and result.get("prose_content_checks") == "disabled":
        contract["instruction"] = (
            "输出JSON text正文。按事件方案展开故事，数值复述优先使用quantity_sources给出的token，保留近似和来源。event占位符是可选的原句引用；没有逐事件覆盖、原句复述次数或算术表达的正文校验。不得修改数据结构；需要变更事件方案可输出event_revision_request。"
        )
        result["frozen_events"]["authority"] = (
            "Writing plan reference; prose content is unchecked. Data references remain exact."
        )
        contract["example"] = {
            "text": "完整场景正文。数值复述可使用quantity_sources提供的引用。"
        }
        contract.pop("ordered_event_tokens", None)
    if role == "writer" and "stage_task" in result:
        contract["required"] = ["new_stage_text"]
        contract["example"] = {"new_stage_text": "仅本写作单元的新增场景正文。"}
        contract["instruction"] = (
            "输出JSON new_stage_text，内容仅为stage_task新增正文，previous_prose_tail只读；若当前方案需要不具备的材料条件或改变关键事件，改为仅输出event_revision_request字符串，不同时交正文。不得返回整章稿或其他阶段。"
        )
    return result


def output_error_details(parsed, contract, existing=None):
    details = copy.deepcopy(existing) if isinstance(existing, dict) else {}
    details["expected_output_contract"] = copy.deepcopy(contract)
    if isinstance(parsed, dict):
        required = set(contract["required"])
        allowed = required | set(contract.get("optional", []))
        details.update(
            actual_fields=sorted(parsed),
            missing_fields=sorted(required - set(parsed)),
            unexpected_fields=sorted(set(parsed) - allowed),
        )
    return details


def prepare_repair(payload, error, previous_output, details=None):
    result = copy.deepcopy(payload)
    # Only previous prose is omitted in a format-only repair. Keep every current
    # fact, rule, plan and instruction; keep the entire erroneous reply verbatim.
    omitted = []
    if "recent_chapters" in result:
        result.pop("recent_chapters")
        omitted.append("recent_chapters")
    result["narrative_repair_policy"] = {
        "format_only": True,
        "omitted_context_fields": omitted,
        "facts_truncated": False,
        "previous_output_truncated": False,
    }
    result["repair"] = {
        "error": str(error),
        "previous_output": previous_output,
        "instruction": "只修输出格式和所列契约错误，不重写剧情或正文，不改已正确字段；完整保留事实、原稿内容和规划语义。近期正文仅在本次格式修复中省略，原文仍保存在本地。",
    }
    if isinstance(details, dict):
        result["repair"]["details"] = copy.deepcopy(details)
    if "frozen_events" in result:
        result["repair"]["instruction"] = (
            "仅修JSON和正文表达契约，包括已冻结事件占位符的覆盖、顺序与计算引用；保留其他正确表达，不修改冻结事件。若需要改变事件，输出event_revision_request，不直接改事实。"
        )
        if result.get("prose_content_checks") == "disabled":
            result["repair"]["instruction"] = (
                "只修JSON字段和数据引用格式，保留正文；不执行内容、事件覆盖、原句次数或数字合理性检查。"
            )
    if "stage_task" in result:
        result["repair"]["instruction"] += (
            "previous_output是尚未保存的本单元原稿，不是已写前情。完整重发同一段正文，逐字保留内容，只修外层格式；不得接着原稿往下续写。"
        )
    return result


def transport_info(prompt, payload, attempt):
    size = len(canonical({"system": prompt, "payload": payload}).encode("utf-8"))
    limit = MAX_REQUEST_BYTES if attempt else MAX_REQUEST_BYTES - REPAIR_HEADROOM_BYTES
    result = {
        "input_bytes": size,
        "limit_bytes": limit,
        "repair_headroom_bytes": REPAIR_HEADROOM_BYTES,
        "omitted_context_fields": payload.get("narrative_repair_policy", {}).get(
            "omitted_context_fields", []
        ),
        "fact_sources_included": False,
    }
    if size > limit:
        error = ContractError(
            f"input exceeds narrative {'repair' if attempt else 'initial with repair reserve'} bound: {size}>{limit} bytes; no facts or previous output truncated"
        )
        error.repair_details = result
        raise error
    return result
