"""Nonblocking, per-unit meaning labels and source-bound memory relations."""

import copy
import re

from inf_writer.domain import (
    ContractError,
    canonical,
    digest,
    fields,
    strict_json,
)
from inf_writer.memory_meaning import (
    CLAIM_TYPES,
    EPISTEMIC_STATES,
    content_key,
    meaning_view,
    pending_ids,
    valid_annotation,
)
from inf_writer.memory_temporality import annotated, has_current_content
from inf_writer.models import ModelRequest
from inf_writer.tiered_memory import apply_delta

RELATIONS = (
    "supersedes",
    "refutes",
    "completes",
    "cancels",
    "supports",
    "conflicts",
    "same_topic",
)
SYSTEM = (
    "你整理记忆含义与关系，不审核或重写小说。输出一个JSON annotations数组和relations数组。"
    "annotations每项memory_choice、units、reason；units每项part_choices（连续位置数组）、claim_type、epistemic_status、perspective_owner。"
    "每条被标注记录的全部parts恰好覆盖一次，各单元保留上下文和否定范围；不同人物说法、猜测、计划和已发生事实分别成单元。"
    "claim_type:current_state当前状态/historical_event已发生事件/character_statement人物说法/character_belief人物认识/"
    "intention意图/task待办/mixed混合/unclassified无法判断。"
    "叙述确认某猜测已被证据排除，属于已发生事实；不要仅因句中含猜测二字就标成人物猜测。"
    "epistemic_status:narration_confirmed叙述确认/reported_unverified人物报告未核实/hypothesis猜测/uncertain不确定/mixed混合/not_assessed未判断。"
    "perspective_owner是原文说话人或认识持有人，不是断言对象；没有人物视角或此记录绑定原文无法确定姓名时填null，不能借用其它记录补出姓名。"
    "有人说已完成不等于客观完成；明确决定取消可取消旧安排，先做别的、没再提或时间过去不能当取消。"
    "relations每项earlier_memory_choice、later_memory_choice、relation_type、earlier_part_choices、later_part_choices、evidence_choices、reason。"
    "以上choices均为本次提供的整数位置或整数数组，绝不填对象、evidence_id或chapter_number。"
    "evidence_choices只能从later记录的source_evidence_choices中选；retirement_evidence_units列出能用于替代/否定/完成/取消的已确认事实单元。"
    "relation_type:supersedes新状态替代旧状态/refutes新证据否定旧认识/completes实际完成原任务/cancels明确取消原任务/"
    "supports支持/conflicts尚无法判定的冲突/same_topic仅同一话题。"
    "替代/否定/完成/取消只作用于选中的完整含义单元，不能把整段其它仍有效信息一起作废。"
    "它们须有later记录绑定的较晚原文证据，后来一条猜测不能推翻此前确认事实。真正发生过的历史事件不能因后续进展被抹除。"
    "缺标签的关系端点先在annotations中标注。只覆盖annotation_required_choices及必要端点，locked_annotation_choices不要再次输出。"
    "accepted_units提供已接受单元的part_choices，关系必须选择其中完整单元，不能只摘取半句。"
    "relationship_review是上轮未接受的关系建议，重新依据原文判断；可返回修正关系，依据不足则relations=[]，不能为补齐任务编造关系。"
    "没有可靠替代关系则relations=[]，保留未知与冲突，不编造完成或事实，不靠换标签升级证实程度。"
)


def _positions(values, count):
    if (
        not isinstance(values, list)
        or not values
        or any(type(v) is not int or not 1 <= v <= count for v in values)
        or len(set(values)) != len(values)
    ):
        raise ContractError("Choose existing unique integer positions")
    return sorted(values)


def _annotate(row, units, reason):
    if (
        not isinstance(units, list)
        or not units
        or not isinstance(reason, str)
        or not reason.strip()
    ):
        raise ContractError("Meaning units and reason required")
    parts = annotated(row)["temporality"]["parts"]
    result = []
    covered = []
    normalizations = []
    for unit in units:
        fields(
            unit,
            ("part_choices", "claim_type", "epistemic_status", "perspective_owner"),
        )
        positions = _positions(unit["part_choices"], len(parts))
        if positions != list(range(positions[0], positions[-1] + 1)):
            raise ContractError("Meaning units must be contiguous")
        if (
            unit["claim_type"] not in CLAIM_TYPES
            or unit["epistemic_status"] not in EPISTEMIC_STATES
        ):
            raise ContractError("Unknown meaning label")
        owner = unit["perspective_owner"]
        certainty = unit["epistemic_status"]
        if owner is not None:
            if not isinstance(owner, str) or not owner.strip():
                raise ContractError("Perspective owner must be a name or null")
            if not any(
                owner in v
                for v in [row["subject"]] + [s["quote"] for s in row.get("sources", [])]
            ):
                normalizations.append(
                    {
                        "rule": "unbound_perspective_to_unknown",
                        "proposed_name": owner,
                        "part_choices": positions,
                    }
                )
                owner = None
                certainty = "uncertain"
        if (
            unit["claim_type"] == "character_statement"
            and unit["epistemic_status"] == "narration_confirmed"
        ):
            raise ContractError(
                "A character statement cannot itself certify its content"
            )
        covered.extend(positions)
        result.append(
            {
                "part_ids": [parts[i - 1]["id"] for i in positions],
                "claim_type": unit["claim_type"],
                "epistemic_status": certainty,
                "perspective_owner": owner,
            }
        )
    if sorted(covered) != list(range(1, len(parts) + 1)):
        raise ContractError("Annotate every part exactly once")
    result.sort(
        key=lambda u: next(
            i for i, p in enumerate(parts) if p["id"] == u["part_ids"][0]
        )
    )
    annotation = {
        "schema": "memory-meaning-v1",
        "content_sha256": content_key(row),
        "units": result,
        "reason": reason,
        "semantic_certification": False,
    }
    if normalizations:
        annotation["normalizations"] = normalizations
    return dict(annotation, sha256=digest(canonical(annotation)))


def _whole_units(row, positions):
    parts = annotated(row)["temporality"]["parts"]
    ids = {parts[i - 1]["id"] for i in _positions(positions, len(parts))}
    if not valid_annotation(row):
        raise ContractError("Relation endpoint needs a current meaning annotation")
    for unit in row["meaning_annotation"]["units"]:
        shared = ids.intersection(unit["part_ids"])
        if shared and shared != set(unit["part_ids"]):
            raise ContractError(
                "Relation must select whole meaning units, preserving negation and context"
            )
    return ids


def _relation(memory, raw, bindings, evidence, chapters):
    fields(
        raw,
        (
            "earlier_memory_choice",
            "later_memory_choice",
            "relation_type",
            "earlier_part_choices",
            "later_part_choices",
            "evidence_choices",
            "reason",
        ),
    )
    left = raw["earlier_memory_choice"]
    right = raw["later_memory_choice"]
    kind = raw["relation_type"]
    if (
        type(left) is not int
        or type(right) is not int
        or left not in bindings
        or right not in bindings
        or left == right
    ):
        raise ContractError("Relation must select two distinct supplied memory choices")
    if (
        kind not in RELATIONS
        or not isinstance(raw["reason"], str)
        or not raw["reason"].strip()
    ):
        raise ContractError("Invalid meaning relation")
    earlier = memory["items"][bindings[left]]
    later = memory["items"][bindings[right]]
    old_ids = _whole_units(earlier, raw["earlier_part_choices"])
    new_ids = _whole_units(later, raw["later_part_choices"])
    proofs = [
        evidence[i - 1] for i in _positions(raw["evidence_choices"], len(evidence))
    ]
    later_sources = {
        (s["chapter_number"], s["evidence_id"], s["chapter_sha256"])
        for s in later["sources"]
    }
    if any(
        (s["chapter_number"], s["evidence_id"], s["chapter_sha256"])
        not in later_sources
        for s in proofs
    ):
        raise ContractError("Relation evidence must belong to the later record")
    chapters_used = {s["chapter_number"] for s in proofs}
    if len(chapters_used) != 1:
        raise ContractError("One relation uses one evidence chapter")
    as_of = next(iter(chapters_used))
    if as_of < max(s["chapter_number"] for s in earlier["sources"]):
        raise ContractError("Older evidence cannot retire newer information")
    relation = {
        "earlier": {
            "memory_id": earlier["id"],
            "content_sha256": content_key(earlier),
            "part_ids": sorted(old_ids),
        },
        "later": {
            "memory_id": later["id"],
            "content_sha256": content_key(later),
            "part_ids": sorted(new_ids),
        },
        "relation_type": kind,
        "evidence": proofs,
        "reason": raw["reason"],
        "semantic_certification": False,
    }
    identifier = (
        "meaning_"
        + digest(
            canonical(
                {
                    k: v
                    for k, v in relation.items()
                    if k not in ("reason", "semantic_certification")
                }
            )
        )[:24]
    )
    if identifier in memory.get("meaning_relations", {}):
        return memory
    if kind in ("supersedes", "refutes", "completes", "cancels", "conflicts"):
        live = {p["id"]: p for p in annotated(later)["temporality"]["parts"]}
        if any(live[i]["scope"] != "current" for i in new_ids):
            raise ContractError("Later relation units must still be current")
    if kind == "conflicts":
        live = {p["id"]: p for p in annotated(earlier)["temporality"]["parts"]}
        if any(live[i]["scope"] != "current" for i in old_ids):
            raise ContractError("Historical units cannot create a current conflict")
    destructive = kind in ("supersedes", "refutes", "completes", "cancels")
    old_units = [
        u
        for u in earlier["meaning_annotation"]["units"]
        if set(u["part_ids"]) & old_ids
    ]
    new_units = [
        u for u in later["meaning_annotation"]["units"] if set(u["part_ids"]) & new_ids
    ]
    if destructive:
        if any(
            u["epistemic_status"] != "narration_confirmed"
            or u["perspective_owner"] is not None
            or u["claim_type"] not in ("current_state", "historical_event")
            for u in new_units
        ):
            raise ContractError(
                "Unverified statements or guesses cannot retire prior information"
            )
        if kind == "completes" and any(
            u["claim_type"] in ("intention", "task") for u in new_units
        ):
            raise ContractError("A future plan cannot prove task completion")
        if any(u["claim_type"] == "historical_event" for u in old_units):
            raise ContractError("Later progress cannot erase a historical event")
        if kind in ("completes", "cancels") and any(
            u["claim_type"] not in ("intention", "task") for u in old_units
        ):
            raise ContractError("Task lifecycle can only retire task/intent units")
        if kind == "supersedes" and earlier["subject"] != later["subject"]:
            raise ContractError("State replacement must preserve the subject")
        current = {p["id"]: p for p in annotated(earlier)["temporality"]["parts"]}
        if any(current[i]["scope"] != "current" for i in old_ids):
            raise ContractError("Selected old meaning unit is already historical")
        operation = {
            "op": "reconcile",
            "id": earlier["id"],
            "expected_revision": earlier["revision"],
            "reason": raw["reason"],
            "as_of_chapter": as_of,
            "resolutions": [
                {
                    "part_ids": sorted(old_ids),
                    "replacement_ids": [later["id"]],
                    "relation": "completed" if kind == "completes" else "superseded",
                    "source_refs": [
                        {
                            "chapter_number": s["chapter_number"],
                            "evidence_id": s["evidence_id"],
                        }
                        for s in proofs
                    ],
                    "reason": raw["reason"],
                }
            ],
        }
        result = apply_delta(memory, {"changes": [operation]}, chapters, identifier)
        for part in result["items"][earlier["id"]]["temporality"]["parts"]:
            if part["id"] in old_ids:
                part["meaning_relation"] = kind
                part["meaning_relation_id"] = identifier
    else:
        result = copy.deepcopy(memory)
        result["revision"] += 1
        if kind == "conflicts":
            for row, ids in ((earlier, old_ids), (later, new_ids)):
                item = annotated(result["items"][row["id"]])
                for part in item["temporality"]["parts"]:
                    if part["id"] in ids:
                        part.setdefault("meaning_conflict_ids", []).append(identifier)
                result["items"][row["id"]] = item
    result.setdefault("meaning_relations", {})[identifier] = relation
    if destructive:
        for conflict_id, conflict in result["meaning_relations"].items():
            if conflict["relation_type"] != "conflicts" or conflict.get("resolved_by"):
                continue
            retired = next(
                (
                    e
                    for e in (conflict["earlier"], conflict["later"])
                    if e["memory_id"] == earlier["id"]
                    and e["content_sha256"] == content_key(earlier)
                    and set(e["part_ids"]) <= old_ids
                ),
                None,
            )
            if not retired:
                continue
            conflict["resolved_by"] = identifier
            for endpoint in (conflict["earlier"], conflict["later"]):
                item = result["items"][endpoint["memory_id"]]
                if content_key(item) != endpoint["content_sha256"]:
                    continue
                item = annotated(item)
                for p in item["temporality"]["parts"]:
                    p["meaning_conflict_ids"] = [
                        i for i in p.get("meaning_conflict_ids", []) if i != conflict_id
                    ]
                result["items"][item["id"]] = item
    return result


def _batch(memory, chapters, number, focus):
    terms = set(
        re.findall(
            r"[\u3400-\u9fff]{2}|[a-z0-9_]+",
            " ".join(memory["items"][i]["claim"] for i in focus).lower(),
        )
    )
    subjects = {memory["items"][i]["subject"] for i in focus}
    older = [
        r
        for i, r in memory["items"].items()
        if i not in focus
        and r["kind"] not in ("prose_excerpt", "legacy")
        and r.get("sources")
        and max(s["chapter_number"] for s in r["sources"]) <= number
        and has_current_content(r)
    ]
    older.sort(
        key=lambda r: (
            -(
                8 * (r["subject"] in subjects)
                + 5 * (r["kind"] == "task")
                + sum(t in r["claim"].lower() for t in terms)
            ),
            r["id"],
        )
    )
    rows = []
    proofs = {}
    bindings = {}
    peers = [
        i
        for job in memory.get("meaning_review_jobs", {}).values()
        if set(job["memory_ids"]) & set(focus)
        for i in job["memory_ids"]
        if i not in focus
    ]
    identifiers = list(dict.fromkeys(focus + peers + [r["id"] for r in older]))[:20]
    for identifier in identifiers:
        row = memory["items"][identifier]
        parts = annotated(row)["temporality"]["parts"]
        value = {
            "memory_choice": len(rows) + 1,
            "subject": row["subject"],
            "attribute": memory.get("attribute_labels", {}).get(
                row["attribute"], row["attribute"]
            ),
            "storage_kind": row["kind"],
            "claim": row["claim"],
            "source_chapters": sorted({s["chapter_number"] for s in row["sources"]}),
            "parts": [
                {"part_choice": i, "text": p["text"], "scope": p["scope"]}
                for i, p in enumerate(parts, 1)
            ],
            "meaning": meaning_view(row),
        }
        added = {}
        for source in row["sources"]:
            n = source["chapter_number"]
            if not 1 <= n <= number or source["chapter_sha256"] != digest(
                chapters[n - 1]["text"]
            ):
                continue
            added[(n, source["evidence_id"])] = copy.deepcopy(source)
        if not added:
            continue
        merged = dict(proofs)
        merged.update(added)
        if (
            len(
                canonical(
                    {"records": rows + [value], "evidence": list(merged.values())}
                ).encode("utf-8")
            )
            > 70000
        ):
            if not rows:
                raise ContractError(
                    "A meaning record exceeds the organization view budget"
                )
            continue
        rows.append(value)
        bindings[len(rows)] = identifier
        proofs = merged
    return rows, bindings, list(proofs.values())


def _refresh_records(payload, memory, bindings):
    evidence_choices = {
        (s["chapter_number"], s["evidence_id"], s["chapter_sha256"]): s[
            "evidence_choice"
        ]
        for s in payload["evidence"]
    }
    for row in payload["memory_records"]:
        item = memory["items"][bindings[row["memory_choice"]]]
        row["meaning"] = meaning_view(item)
        row["source_evidence_choices"] = [
            evidence_choices[
                (s["chapter_number"], s["evidence_id"], s["chapter_sha256"])
            ]
            for s in item["sources"]
            if (s["chapter_number"], s["evidence_id"], s["chapter_sha256"])
            in evidence_choices
        ]
        positions = {
            p["id"]: n for n, p in enumerate(annotated(item)["temporality"]["parts"], 1)
        }
        row["accepted_units"] = (
            [
                {
                    "part_choices": [positions[i] for i in u["part_ids"]],
                    "claim_type": u["claim_type"],
                    "epistemic_status": u["epistemic_status"],
                    "perspective_owner": u["perspective_owner"],
                }
                for u in item["meaning_annotation"]["units"]
            ]
            if valid_annotation(item)
            else []
        )
        row["retirement_evidence_units"] = [
            u["part_choices"]
            for u in row["accepted_units"]
            if u["claim_type"] in ("current_state", "historical_event")
            and u["epistemic_status"] == "narration_confirmed"
            and u["perspective_owner"] is None
        ]


def _organize(memory, chapters, number, gateway, trace, *, max_batches=3):
    """Publish valid peers; bounded failures remain explicit and nonblocking."""
    result = copy.deepcopy(memory)
    attempted = set()
    for batch_index in range(max_batches):
        pending = [
            i
            for i in pending_ids(result)
            if i not in attempted
            and result["items"][i].get("sources")
            and max(s["chapter_number"] for s in result["items"][i]["sources"])
            <= number
        ]
        pending.sort(
            key=lambda i: (
                -max(s["chapter_number"] for s in result["items"][i]["sources"]),
                i,
            )
        )
        if not pending:
            break
        focus = pending[:10]
        attempted.update(focus)
        try:
            rows, bindings, evidence = _batch(result, chapters, number, focus)
        except Exception as exc:
            trace.append(
                {
                    "role": "memory_organization",
                    "status": "DEFERRED",
                    "error_type": type(exc).__name__,
                }
            )
            continue
        required = [
            i
            for i, mid in bindings.items()
            if mid in focus and not valid_annotation(result["items"][mid])
        ]
        reviews = {
            i: j
            for i, j in result.get("meaning_review_jobs", {}).items()
            if set(j["memory_ids"]) <= set(bindings.values())
        }
        if not required and not reviews:
            continue
        payload = {
            "completed_chapter": number,
            "memory_records": rows,
            "annotation_required_choices": required,
            "evidence": [dict(s, evidence_choice=i) for i, s in enumerate(evidence, 1)],
            "output_contract": {
                "annotations": [
                    {
                        "memory_choice": 1,
                        "units": [
                            {
                                "part_choices": [1],
                                "claim_type": "intention",
                                "epistemic_status": "narration_confirmed",
                                "perspective_owner": None,
                            }
                        ],
                        "reason": "根据实际原文",
                    }
                ],
                "relations": [],
            },
        }
        payload["relation_output_fields"] = {
            "earlier_memory_choice": "integer",
            "later_memory_choice": "integer",
            "relation_type": list(RELATIONS),
            "earlier_part_choices": "integer array: whole accepted units",
            "later_part_choices": "integer array: whole accepted units",
            "evidence_choices": "integer array from later.source_evidence_choices",
            "reason": "string",
        }
        locked = {
            i for i, mid in bindings.items() if valid_annotation(result["items"][mid])
        }
        payload["locked_annotation_choices"] = sorted(locked)
        payload["relationship_review"] = [
            {
                "memory_choices": [
                    i for i, mid in bindings.items() if mid in job["memory_ids"]
                ],
                "error": job["error"],
                "relation_type": job["relation_type"],
            }
            for job in reviews.values()
        ]
        _refresh_records(payload, result, bindings)
        relation_errors = []
        for attempt in range(2):
            entry = {
                "role": "memory_organization",
                "chapter": number,
                "batch": batch_index + 1,
                "attempt": attempt + 1,
            }
            trace.append(entry)
            errors = []
            relation_errors = []
            try:
                if (
                    len(
                        canonical({"system": SYSTEM, "payload": payload}).encode(
                            "utf-8"
                        )
                    )
                    > 96000
                ):
                    raise ContractError("Meaning organization input exceeds bound")
                reply = gateway.complete(ModelRequest("memory", SYSTEM, payload, 16384))
                entry.update(
                    raw_output=reply.content, finish_reason=reply.finish_reason
                )
                if reply.finish_reason not in ("stop", None):
                    raise ContractError("Incomplete organization response")
                from .pipeline import normalize

                parsed, _ = normalize(strict_json(reply.content))
                try:
                    fields(parsed, ("annotations", "relations"))
                except ContractError as exc:
                    if not isinstance(parsed, dict) or not {
                        "annotations",
                        "relations",
                    } <= set(parsed):
                        raise
                    errors.append({"scope": "response_fields", "error": str(exc)})
                if not isinstance(parsed["annotations"], list) or not isinstance(
                    parsed["relations"], list
                ):
                    raise ContractError("Organization arrays required")
                counts = {}
                for raw in parsed["annotations"]:
                    if isinstance(raw, dict) and type(raw.get("memory_choice")) is int:
                        counts[raw["memory_choice"]] = (
                            counts.get(raw["memory_choice"], 0) + 1
                        )
                for raw in parsed["annotations"]:
                    try:
                        fields(raw, ("memory_choice", "units", "reason"))
                        choice = raw["memory_choice"]
                        if (
                            type(choice) is not int
                            or choice not in bindings
                            or counts[choice] != 1
                        ):
                            raise ContractError("Unknown or duplicate memory choice")
                        row = result["items"][bindings[choice]]
                        annotation = _annotate(row, raw["units"], raw["reason"])
                        if choice in locked:
                            if annotation["units"] != row.get(
                                "meaning_annotation", {}
                            ).get("units"):
                                raise ContractError(
                                    "Cannot overwrite an accepted annotation"
                                )
                            continue
                        result["items"][row["id"]]["meaning_annotation"] = annotation
                        locked.add(choice)
                        result["revision"] += 1
                    except (ContractError, TypeError, KeyError) as exc:
                        errors.append(
                            {
                                "scope": "annotation",
                                "memory_choice": raw.get("memory_choice")
                                if isinstance(raw, dict)
                                else None,
                                "error": str(exc),
                            }
                        )
                for raw in parsed["relations"]:
                    try:
                        result = _relation(result, raw, bindings, evidence, chapters)
                    except (ContractError, TypeError, KeyError, IndexError) as exc:
                        errors.append(
                            {
                                "scope": "relation",
                                "earlier_memory_choice": raw.get(
                                    "earlier_memory_choice"
                                )
                                if isinstance(raw, dict)
                                else None,
                                "later_memory_choice": raw.get("later_memory_choice")
                                if isinstance(raw, dict)
                                else None,
                                "error": str(exc),
                            }
                        )
                        if isinstance(raw, dict):
                            mids = [
                                bindings[i]
                                for i in (
                                    raw.get("earlier_memory_choice"),
                                    raw.get("later_memory_choice"),
                                )
                                if type(i) is int and i in bindings
                            ]
                            if len(set(mids)) == 2:
                                relation_errors.append(
                                    {
                                        "memory_ids": mids,
                                        "relation_type": raw.get("relation_type"),
                                        "error": str(exc),
                                    }
                                )
            except Exception as exc:
                errors.append(
                    {
                        "scope": "response",
                        "error": str(exc)
                        if isinstance(exc, ContractError)
                        else type(exc).__name__,
                    }
                )
            missing = [
                c
                for c in required
                if not valid_annotation(result["items"][bindings[c]])
            ]
            entry.update(
                status="ORGANIZED" if not missing and not errors else "PARTIAL",
                errors=errors,
                pending_choices=missing,
            )
            if not missing and not errors:
                for identifier, job in reviews.items():
                    result.setdefault("meaning_review_history", []).append(
                        {"job": job, "outcome": "RECONSIDERED", "chapter": number}
                    )
                    result.get("meaning_review_jobs", {}).pop(identifier, None)
                break
            payload["annotation_required_choices"] = missing
            payload["locked_annotation_choices"] = sorted(locked)
            payload["repair_errors"] = errors + [
                {"missing_annotation_choices": missing}
            ]
            _refresh_records(payload, result, bindings)
        for job in relation_errors:
            identifier = "meaning_review_" + digest(canonical(job))[:24]
            result.setdefault("meaning_review_jobs", {})[identifier] = job
    result["meaning_pending_ids"] = pending_ids(result)
    result["meaning_processing_scope"] = (
        "Model meaning labels and explicit evidence relations; not semantic certification"
    )
    return result


def organize(memory, chapters, number, gateway, trace, *, max_batches=3):
    """Organization outages must never discard saved prose or stop writing."""
    try:
        result = _organize(
            memory, chapters, number, gateway, trace, max_batches=max_batches
        )
        from .pipeline import LayerAgent

        result, moves = LayerAgent.intake(
            result, chapters, "meaning-intake-" + digest(canonical(result))[:24]
        )
        if moves:
            trace.append(
                {"role": "memory_meaning_intake", "status": "APPLIED", "moves": moves}
            )
        return result
    except Exception as exc:
        trace.append(
            {
                "role": "memory_organization",
                "status": "DEFERRED",
                "error_type": type(exc).__name__,
            }
        )
        result = copy.deepcopy(memory)
        result["meaning_pending_ids"] = pending_ids(result)
        return result


def reference_meanings(book):
    """Link effective memory meanings to existing state/reference identities."""
    from .event_references import reference_id
    from .identifiers import record_identifier
    from .state_recovery import transactions

    memory = book["memory"]
    index = {}
    views = {}
    for item in list(memory["items"].values()) + [
        h["item"] for h in memory.get("history", [])
    ]:
        for source in item.get("sources", []):
            key = (
                source["chapter_number"],
                item["subject"],
                item["attribute"],
                item["kind"],
                item["claim"],
            )
            index.setdefault(key, set()).add(item["id"])
    for number, commit in transactions(book):
        events = {b["id"]: b["event_id"] for s in commit["scenes"] for b in s["beats"]}
        grounded = memory.get("projection_grounding", {}).get(str(number), {})
        recovery = memory.get("state_recovery_projection", {}).get(commit["sha256"], {})
        recovery_ids = {
            r["projection_ref"]: r["memory_id"] for r in recovery.get("records", [])
        }
        for row in commit["memory_projection"]:
            ref = None
            if row["kind"] == "task" and row.get("status") == "planned":
                identifier = row.get("proposed_record", {}).get(
                    "id"
                ) or record_identifier("plan:" + events[row["beat_id"]])
                ref = reference_id("plan", identifier)
            elif "canonical_record" in row:
                record = row["canonical_record"]
                ref = reference_id(record["type"], record["id"])
            if ref is None:
                continue
            mids = set(
                index.get(
                    (
                        number,
                        row["subject"],
                        row["attribute"],
                        row["kind"],
                        row["claim"],
                    ),
                    set(),
                )
            )
            if grounded.get("commit_sha256") == commit["sha256"]:
                decision = grounded.get("decisions", {}).get(row["ref"], {})
                if decision.get("outcome") in ("matched", "partial"):
                    mids.add(decision["memory_id"])
            if row["ref"] in recovery_ids:
                mids.add(recovery_ids[row["ref"]])
            candidates = [memory["items"][i] for i in mids if i in memory["items"]]
            if not candidates:
                continue
            item = max(
                candidates,
                key=lambda r: (max(s["chapter_number"] for s in r["sources"]), r["id"]),
            )
            view = meaning_view(item)
            if view["assessed"] or view["task_state"] in ("completed", "cancelled"):
                views[ref] = dict(view, memory_id=item["id"])
    return views
