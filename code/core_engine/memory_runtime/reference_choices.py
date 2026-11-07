"""Model selects locations/choices; the program creates and binds identifiers."""

import copy
import re

from inf_writer.domain import ContractError, strict_json

REFERENCE_FIELDS = {
    "fact_ref",
    "intention_ref",
    "learned_record_ref",
    "source_action_ref",
    "created_by_action_ref",
    "derived_from_object_ref",
    "dated_event_ref",
    "observed_object_ref",
    "evidence_carrier_ref",
}
RECORD_KINDS = {
    "establish_fact": "fact_record",
    "record_character_knowledge": "character_knowledge",
    "record_dated_event": "dated_event_record",
    "register_evidence_object": "evidence_object",
    "record_observation": "observation_record",
    "record_receipt": "receipt_record",
    "resolve_person_identity": "person_identity_record",
    "record_check_progress": "check_progress_record",
}
FIELD_KINDS = {
    "fact_ref": ["fact_record"],
    "intention_ref": ["pending_intention"],
    "source_action_ref": ["chapter_action"],
    "created_by_action_ref": ["chapter_action"],
    "derived_from_object_ref": ["evidence_object"],
    "dated_event_ref": ["dated_event_record"],
    "observed_object_ref": ["evidence_object"],
    "evidence_carrier_ref": ["evidence_object"],
    "involved_object_refs": ["evidence_object"],
    "follows_dated_event_refs": ["dated_event_record"],
}


CONTRACT = (
    "编号由程序生成。scenes和beats不要填id，新建记录不要填record_id。"
    "已有引用选{record_choice:N}（reference_choices中从1开始的位置），或原样选该目录的一项；不得填写目录外编号。"
    "本章动作引用用{action_position:N}（所有场景动作按顺序从1计数）；"
    "source_action_ref用{current_action:true}指当前动作。"
    "本章新记录引用用{record_position:[场景序号,动作序号,变更序号]}，均从1开始。"
    "requires各项及所有_ref字段都用这些选择器，引用列表同样如此；null仍可用于无来源的直接观察。"
    "引用须符合schema指定的记录类别，对应索引见reference_choices_by_kind；没有物件时先register_evidence_object，用record_position引用，不能用事实记录代替物件。"
    "选择位置不会证明事件已发生，程序仍检查定义顺序、类型及版本。"
    "修改已有事实的fact_ref必须用身份选择器{record_subject:人物或对象原名,record_property_name:目录中的property_name或attribute_label}，可直接复制记录的update_selector；"
    "程序按主体与属性共同定位，不必数record_choice。必须唯一匹配；找不到则建立该主体的新属性，不借用别人的属性。"
    "若同时填record_choice与上述身份字段，三者必须一致；岗位变化必须选岗位属性，不能写入抄件递交。"
)


def formal_operation_catalogue():
    from .event_contract import planner_catalogue

    schemas = planner_catalogue()
    for schema in schemas.values():
        for field in ("required", "optional"):
            if field in schema:
                schema[field] = [
                    v for v in schema[field] if v not in ("record_id", "operation_id")
                ]
    schemas["record_observation"].setdefault("reference_contract", {})[
        "observed_object_ref"
    ] = {"allowed_record_kinds": FIELD_KINDS["observed_object_ref"]}
    for schema in schemas.values():
        for field in schema["required"] + schema.get("optional", []):
            if field in FIELD_KINDS:
                schema.setdefault("reference_contract", {})[field] = {
                    "allowed_record_kinds": FIELD_KINDS[field],
                    "instruction": "只选这些类别；计划修订用revise_intention，实际新状态用establish_fact，不把意图编号填进fact_ref。",
                }
    return schemas


def validate_formal_input(proposal):
    """Validate the public language before allocating any identifiers."""
    issues = []
    schemas = formal_operation_catalogue()

    def node(value, required, optional, path):
        if not isinstance(value, dict):
            issues.append({"path": path, "error": "Expected an object"})
            return False
        missing = set(required) - set(value)
        extra = set(value) - set(required) - set(optional)
        if missing or extra:
            issues.append(
                {
                    "path": path,
                    "error": "Public fields missing or unexpected",
                    "missing_fields": sorted(missing),
                    "unexpected_fields": sorted(extra),
                    "required_fields": list(required),
                    "optional_fields": list(optional),
                }
            )
        return not missing and not extra

    def sequence(value, path):
        if not isinstance(value, list):
            issues.append({"path": path, "error": "Expected an array"})
            return []
        return value

    if node(
        proposal,
        ("number", "title", "brief", "future_updates", "scenes"),
        ("time_calculations",),
        "plan",
    ):
        for si, scene in enumerate(sequence(proposal["scenes"], "scenes")):
            sp = f"scenes[{si}]"
            if not node(scene, ("purpose", "participants", "beats"), (), sp):
                continue
            for bi, action in enumerate(sequence(scene["beats"], sp + ".beats")):
                bp = sp + f".beats[{bi}]"
                if not node(
                    action,
                    ("statement", "assertion_scope", "requires", "changes"),
                    (),
                    bp,
                ):
                    continue
                sequence(action["requires"], bp + ".requires")
                for ci, row in enumerate(sequence(action["changes"], bp + ".changes")):
                    rp = bp + f".changes[{ci}]"
                    operation = row.get("operation") if isinstance(row, dict) else None
                    if not isinstance(operation, str) or operation not in schemas:
                        issues.append(
                            {
                                "path": rp + ".operation",
                                "error": "Choose a public operation",
                                "allowed_values": list(schemas),
                            }
                        )
                        continue
                    schema = schemas[operation]
                    if node(row, schema["required"], schema.get("optional", []), rp):
                        for field, allowed in schema.get(
                            "operational_values", {}
                        ).items():
                            if field in row and row[field] not in allowed:
                                issues.append(
                                    {
                                        "path": rp + "." + field,
                                        "error": "Choose an operational value",
                                        "submitted_value": row[field],
                                        "allowed_values": allowed,
                                    }
                                )
    if issues:
        error = ContractError(
            "Public planning protocol rejected " + str(len(issues)) + " field(s)"
        )
        error.repair_details = {
            "code": "PUBLIC_PROTOCOL_ERRORS",
            "interface_contract_version": 3,
            "issues": issues,
            "instruction": "只按公开字段和选项修正；编号由程序生成，不能通过添加id或旧type字段切换协议。",
        }
        raise error


def compile_plan(
    proposal,
    choices,
    chapter,
    *,
    reference_records=(),
    id_namespace="",
    require_target_identity=False,
):
    validate_formal_input(proposal)
    return _compile_plan(
        proposal,
        choices,
        chapter,
        reference_records=reference_records,
        id_namespace=id_namespace,
        require_target_identity=require_target_identity,
    )


def compile_independent_stages(
    proposal, choices, chapter, *, reference_records=(), require_target_identity=False
):
    """Keep allocated IDs stable while quarantining scenes with bad selectors."""
    validate_formal_input(proposal)
    errors = []
    result = _compile_plan(
        proposal,
        choices,
        chapter,
        stage_errors=errors,
        reference_records=reference_records,
        require_target_identity=require_target_identity,
    )
    invalid = {r["stage"] for r in errors}
    result["scenes"] = [s for i, s in enumerate(result["scenes"]) if i not in invalid]
    return result, errors


def _compile_plan(
    proposal,
    choices,
    chapter,
    *,
    stage_errors=None,
    reference_records=(),
    id_namespace="",
    require_target_identity=False,
):
    result = copy.deepcopy(proposal)
    actions = {}
    records = {}
    record_number = 0
    directory = {r.get("reference_id"): r for r in reference_records}
    scenes = result.get("scenes", [])
    if not isinstance(scenes, list):
        return result
    for si, scene in enumerate(scenes, 1):
        if not isinstance(scene, dict):
            continue
        scene.setdefault("id", id_namespace + f"s{si:04d}")
        for bi, action in enumerate(
            scene.get("beats", []) if isinstance(scene.get("beats"), list) else [], 1
        ):
            if not isinstance(action, dict):
                continue
            number = len(actions) + 1
            action.setdefault("id", id_namespace + f"a{number:04d}")
            actions[number] = (
                "chapter_action:" + action["id"]
                if isinstance(action["id"], str)
                else None
            )
            for ci, row in enumerate(
                action.get("changes", [])
                if isinstance(action.get("changes"), list)
                else [],
                1,
            ):
                if (
                    not isinstance(row, dict)
                    or not isinstance(row.get("operation"), str)
                    or row["operation"] not in RECORD_KINDS
                ):
                    continue
                record_number += 1
                row.setdefault(
                    "record_id", id_namespace + f"n{chapter:04d}r{record_number:04d}"
                )
                kind = (
                    "pending_intention"
                    if action.get("assertion_scope") == "proposed_action"
                    or row.get("fact_class") == "planned_intention"
                    else RECORD_KINDS[row["operation"]]
                )
                if isinstance(row["record_id"], str):
                    ref = kind + ":" + row["record_id"]
                    records[(si, bi, ci)] = ref
                    directory[ref] = {
                        "subject": row.get("subject"),
                        "property_name": row.get("property_name"),
                        "record_kind": kind,
                    }

    def resolve(value, current, depth=0):
        if depth > 8:
            raise ContractError("Reference selector wrapper nesting exceeds limit")
        # Every reference is bound against the closed directory or local slots.
        if value is None:
            return value
        if isinstance(value, str) and value.strip().startswith("{"):
            stripped = value.strip()
            if stripped.endswith("}") and stripped[1:-1].strip() in choices:
                # Cosmetic braces around an exact supplied identifier add no
                # authority. Unknown identifiers still cannot bind.
                return resolve(stripped[1:-1].strip(), current, depth + 1)
            normalized = re.sub(
                r"([{,]\s*)(record_choice|action_position|record_position|current_action)\s*:",
                r'\1"\2":',
                value.strip(),
            )
            try:
                parsed = strict_json(normalized)
            except ContractError as invalid:
                raise ContractError(
                    "Malformed reference selector; use a selector object"
                ) from invalid
            if not isinstance(parsed, dict):
                raise ContractError("Reference selector must be an object")
            return resolve(parsed, current, depth + 1)
        if isinstance(value, str):
            if value in choices:
                return choices[choices.index(value)]
            raise ContractError(
                "Choose a directory entry or local position; free-text reference IDs are disabled"
            )
        if isinstance(value, dict) and (
            "record_kind" in value
            or "record_subject" in value
            or "record_property_name" in value
        ):
            selectors = {
                k: v
                for k, v in value.items()
                if k not in ("record_kind", "record_subject", "record_property_name")
            }
            if (
                not selectors
                and "record_subject" in value
                and "record_property_name" in value
            ):
                matches = [
                    ref
                    for ref, row in directory.items()
                    if row.get("subject") == value["record_subject"]
                    and value["record_property_name"]
                    in (row.get("property_name"), row.get("attribute_label"))
                    and (
                        "record_kind" not in value
                        or row.get("record_kind", ref.split(":", 1)[0])
                        == value["record_kind"]
                    )
                ]
                if len(matches) != 1:
                    raise ContractError(
                        "Subject/property reference must uniquely match an existing record"
                    )
                return matches[0]
            if len(selectors) != 1:
                raise ContractError("Reference metadata requires one selector")
            bound = resolve(selectors, current, depth + 1)
            if bound is None:
                raise ContractError("Reference metadata cannot describe null")
            if (
                "record_kind" in value
                and value["record_kind"] != bound.split(":", 1)[0]
            ):
                raise ContractError(
                    "Read-only reference kind differs from selected record"
                )
            if "record_subject" in value and value["record_subject"] != directory.get(
                bound, {}
            ).get("subject"):
                raise ContractError(
                    "Read-only reference subject differs from selected record"
                )
            if "record_property_name" in value and value[
                "record_property_name"
            ] not in (
                directory.get(bound, {}).get("property_name"),
                directory.get(bound, {}).get("attribute_label"),
            ):
                raise ContractError(
                    "Read-only reference property differs from selected record"
                )
            return bound
        if not isinstance(value, dict) or len(value) != 1:
            raise ContractError(
                "Reference must select exactly one directory entry or local position"
            )
        key, index = next(iter(value.items()))
        bound = None
        if key in ("ref", "reference_id", "id"):
            return resolve(index, current, depth + 1)
        if key == "record_choice" and type(index) is int and 1 <= index <= len(choices):
            bound = choices[index - 1]
        elif key == "action_position" and type(index) is int:
            bound = actions.get(index)
        elif key == "current_action" and index is True:
            bound = actions.get(current)
        elif (
            key == "record_position"
            and isinstance(index, list)
            and len(index) == 3
            and all(type(i) is int and i > 0 for i in index)
        ):
            bound = records.get(tuple(index))
        if bound is None:
            error = ContractError(
                "Reference selection is outside the supplied directory"
            )
            error.repair_details = {
                "submitted_selector": value,
                "record_choice_count": len(choices),
                "action_position_count": len(actions),
                "instruction": "选择输入目录中真实存在的项；不得补造编号。",
            }
            raise error
        return bound

    def field_reference(value, current, field):
        if (
            require_target_identity
            and field == "fact_ref"
            and not (
                isinstance(value, dict)
                and isinstance(value.get("record_subject"), str)
                and isinstance(value.get("record_property_name"), str)
            )
        ):
            raise ContractError(
                "Fact updates require record_subject and record_property_name; use the subject/property identity selector"
            )
        bound = resolve(value, current)
        kinds = FIELD_KINDS.get(field)
        missing_object = field == "observed_object_ref" and bound is None
        wrong_kind = bool(
            kinds and bound is not None and bound.split(":", 1)[0] not in kinds
        )
        if missing_object or wrong_kind:
            error = ContractError(
                "Reference must select the record kind allowed by this field"
            )
            selected_kind = bound.split(":", 1)[0] if bound else None
            guidance = (
                "选中了意图，不是当前事实。修改原安排用revise_intention/intention_ref；"
                "正文达成新的实际状态另用establish_fact/current_state，保留同一主体，不能换到另一人的事实。"
                if selected_kind == "pending_intention" and field == "fact_ref"
                else "物件引用只能选证据载体；没有候选则登记正文支持的真实载体。"
                if "evidence_object" in kinds
                else "按字段允许类别选择同一目标记录，不能只为类型通过而改到其他主体。"
            )
            error.repair_details = {
                "field": field,
                "submitted_selector": value,
                "allowed_record_kinds": kinds,
                "selected_reference": bound,
                "selected_record": copy.deepcopy(directory.get(bound)),
                "allowed_choice_indices": [
                    i for i, v in enumerate(choices, 1) if v.split(":", 1)[0] in kinds
                ],
                "repair_guidance": guidance,
            }
            raise error
        return bound

    def located(value, current, path, field=None):
        # requires is a polymorphic existence dependency, not an operation's
        # typed reference field. Models sometimes wrap its selector in a
        # known *_ref label. Preserve the selected identity and its real kind;
        # do not reinterpret that label as an invented selector key.
        if field is None and isinstance(value, dict) and len(value) == 1:
            wrapper = next(iter(value))
            if wrapper in REFERENCE_FIELDS:
                value = value[wrapper]
        try:
            return (
                field_reference(value, current, field)
                if field
                else resolve(value, current)
            )
        except ContractError as error:
            details = copy.deepcopy(getattr(error, "repair_details", {}))
            details.update(path=path, submitted_selector=value)
            details.setdefault("record_choice_count", len(choices))
            details.setdefault(
                "accepted_shapes",
                [
                    {"record_choice": 1},
                    {"current_action": True},
                    {"record_position": [1, 1, 1]},
                ],
            )
            error.repair_details = details
            raise

    current = 0
    for si, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            continue
        for bi, action in enumerate(
            scene.get("beats", []) if isinstance(scene.get("beats"), list) else []
        ):
            if not isinstance(action, dict):
                continue
            current += 1
            prefix = f"scenes[{si}].beats[{bi}]"
            try:
                if isinstance(action.get("requires"), list):
                    converted = []
                    for ri, value in enumerate(action["requires"]):
                        path = prefix + f".requires[{ri}]"
                        if isinstance(value, dict) and len(value) == 1:
                            ref, revision = next(iter(value.items()))
                            if ref in choices:
                                if type(revision) is not int or revision < 1:
                                    raise ContractError(
                                        "Dependency record revision must be a positive integer"
                                    )
                                value = {
                                    "reference_id": ref,
                                    "record_revision": revision,
                                }
                        versioned = isinstance(value, dict) and set(value) == {
                            "reference_id",
                            "record_revision",
                        }
                        if versioned:
                            value = copy.deepcopy(value)
                            value["reference_id"] = located(
                                value["reference_id"], current, path
                            )
                            converted.append(value)
                        else:
                            converted.append(
                                {"reference_id": located(value, current, path)}
                            )
                    action["requires"] = converted
                for ci, row in enumerate(
                    action.get("changes", [])
                    if isinstance(action.get("changes"), list)
                    else []
                ):
                    if not isinstance(row, dict):
                        continue
                    for field in REFERENCE_FIELDS:
                        if field in row:
                            row[field] = located(
                                row[field],
                                current,
                                prefix + f".changes[{ci}]." + field,
                                field,
                            )
                    for field in ("involved_object_refs", "follows_dated_event_refs"):
                        if isinstance(row.get(field), list):
                            row[field] = [
                                located(
                                    v,
                                    current,
                                    prefix + f".changes[{ci}].{field}[{i}]",
                                    field,
                                )
                                for i, v in enumerate(row[field])
                            ]
            except ContractError as exc:
                if stage_errors is None:
                    raise
                if not any(r["stage"] == si for r in stage_errors):
                    stage_errors.append(
                        {
                            "stage": si,
                            "status": "DEFERRED",
                            "scene_id": scene["id"],
                            "error": str(exc),
                            "details": copy.deepcopy(
                                getattr(exc, "repair_details", {})
                            ),
                            "proposed_scene": copy.deepcopy(proposal["scenes"][si]),
                        }
                    )
    return result
