"""Bind paraphrased saved prose to structured memory without certifying a plan.

The model selects local evidence positions. The program fetches literal quotes and owns IDs,
source hashes and writes. Unsupported plans remain explicit content gaps.
"""

import copy
from collections import Counter

from tome_writer.domain import (
    ContractError,
    canonical,
    digest,
    evidence_segments,
    fields,
    strict_json,
)
from tome_writer.models import ModelRequest
from tome_writer.tiered_memory import apply_delta

SUPPORTED_OUTCOMES = ("matched", "partial")

SYSTEM = (
    "你整理实际正文的结构化记忆，不审核或改写正文。候选是写作计划，不是事实。"
    "逐项按正文判断，返回JSON decisions数组，每项candidate_position,outcome,support,reason；kind=task且matched或partial时加task_status。"
    "outcome选matched/partial/absent/uncertain。matched表示正文表达对应信息；partial表示同一主体同一事项部分写出，必须另填unsupported_details字符串，说明未写出或不同的细节；"
    "support为[{evidence_position:整数}]，可选多段，必须足以独立表达实际信息；不要输出quote或重新抄写原话。"
    "程序依据位置取回对应完整证据原文合成记忆claim，不抄候选句、不概括，不补正文没写的细节。"
    "引文保留人物、指代所需上下文、否定、猜测及来源。人物说法不提升为客观真相。"
    "matched表示候选核心状态及其进度均得到支持；仅部分实际信息对应时用partial，并明确unsupported_details，不能用matched掩盖尚未完成的环节。"
    "动作措辞或展开方式不同不等于没写。实际主体、对象和行为已表达时应绑定原文，不要求候选整句逐字复现。"
    "kind表示记忆组织方式，不要求正文出现属性名；操作结果、核查结论可支持state，不能仅因正文以动作叙述就判uncertain。"
    "subject是候选记录的归属者或涉及对象，不强制等于引文说话者。"
    "例如人物在场询问、听到别人转述而获得线索，可绑定为该人物所得的knowledge；引文仍保留原说话人及未核实性质。"
    "不能仅因不是subject亲口说就判absent，也不能把subject不在场且未获知的话硬记给他。按上下文区分谁说、谁听到、说的是谁。"
    "state也可记录别人对该主体施加的要求、限制或任命；不要求该主体自己说出要求。"
    "部分对应时保存原文支持的最小实际信息：只说晚上将盘库就记将盘库，不补成已有结果；"
    "人物说抄件已交出只支持该人物的说法，接收人和登记过程未写明就不能补上。"
    "但候选属性若属于另一主体或另一个事项（如把梁策岗位填入许闻抄件递交），必须absent，不能借部分匹配掩盖错绑。"
    "同一事项只写出将来盘库而没有已有结果，用partial保存将来盘库的原话；不能因结果没写就把这句原话丢掉。"
    "只自述“抄件交出去了”而接收人未写，用partial保存自述，不补接收人或登记。"
    "对写成、交中间人、转递、送达、接收、受理、回应等多环节事项，逐段判断正文实际到哪一步。"
    "例如候选写已向某单位提交或获受理，正文只写交给同事转递：这是同一事项的部分进展，"
    "用partial保留已交中间人的原文，unsupported_details注明单位接收/受理尚未确认，不因后段未写就把整项判absent。"
    "既要检查planned_claim也要检查planned_value的完成范围；措辞不同不算遗漏，完成阶段不同则保留差异。"
    "不强制正式回执；叙述或对话明确确认收到、受理即可作为对应阶段证据。"
    "未确认接收不等于没有收到，不能补写否定事实；打算转交也不等于已交给中间人。"
    "同一事项完全未发生选absent，无法确认选uncertain，两者support=[]并说明原因。"
    "task_status选planned/completed/cancelled，以本章末实际状态为准；其他kind不输出状态，程序生成，不填写completed。"
    "kind=task的matched项必须有task_status字段，不能只写在reason里。"
    "选择器只填输入目录位置，不能编造编号。每个候选恰好一次。不输出其它字段。"
)


def pending_chapters(memory):
    return sorted(
        int(n) for n, refs in memory.get("projection_omissions", {}).items() if refs
    )


def qualify_state_view(book, view):
    """Keep repair targets addressable without presenting rejected plan values as facts."""
    result = copy.deepcopy(view)
    memory = book.get("memory", {})
    for row in result.get("records", []):
        if row.get("record_kind") != "fact_record":
            continue
        number = str(row.get("chapter"))
        ref = "facts:" + row["record_id"]
        decision = (
            memory.get("projection_grounding", {})
            .get(number, {})
            .get("decisions", {})
            .get(ref, {})
        )
        if decision.get("outcome") not in ("absent", "uncertain", "partial"):
            continue
        row["projection_status"] = decision["outcome"]
        if "value" in row:
            row["unconfirmed_plan_value"] = row.pop("value")
        elif "recorded_value" in row:
            row["unconfirmed_plan_value"] = row.pop("recorded_value")
        row["reference_usage"] = (
            "此版本未获正文支持，仅保留主体/属性身份供纠正；不得用计划值作为已发生前提。实际进展看有来源的正文记忆。"
        )
        if decision.get("stored_claim"):
            row["actual_prose_claim"] = decision["stored_claim"]
        if decision.get("outcome") == "partial":
            row["unconfirmed_plan_details"] = decision["unsupported_details"]
    return result


def _store(memory, chapters, number, row, support, status, *, projection_position):
    segments = evidence_segments(chapters[number - 1]["text"])
    refs = list(
        {
            (number, r["evidence_position"]): {
                "chapter_number": number,
                "evidence_id": segments[r["evidence_position"] - 1]["id"],
            }
            for r in support
        }.values()
    )
    claim = "\n".join(r["quote"] for r in support)
    old = next(
        (
            v
            for v in memory["items"].values()
            if (v["subject"], v["attribute"], v["kind"])
            == (row["subject"], row["attribute"], row["kind"])
            and v["status"] != "superseded"
        ),
        None,
    )
    token = "prose-grounding:" + digest(
        canonical([number, row["ref"], support, status])
    )
    old_order = (
        old.get(
            "structured_prose_order",
            [max(s["chapter_number"] for s in old["sources"]), 0],
        )
        if old
        else None
    )
    if old and (
        old_order > [number, projection_position]
        or (old["claim"], old["status"]) == (claim, status)
    ):
        # Late repairs must never roll a newer state/task back. Preserve the
        # validated earlier observation as an archived version of the same ID.
        from tome_writer.tiered_memory import empty_memory

        op = {
            "op": "add",
            "subject": row["subject"],
            "attribute": row["attribute"],
            "kind": row["kind"],
            "claim": claim,
            "status": status,
            "source_refs": refs,
        }
        isolated = apply_delta(empty_memory(), {"changes": [op]}, chapters, token)
        archived = next(iter(isolated["items"].values()))
        archived.update(
            id=old["id"],
            revision=old["revision"],
            structured_prose_order=[number, projection_position],
            provenance_scope="model_bound_saved_prose_not_plan_certification",
        )
        result = copy.deepcopy(memory)
        if token not in result["receipts"]:
            result["history"].append(
                {
                    "item": archived,
                    "transaction_id": token,
                    "reason": "Late/unchanged prose observation; newer current state retained",
                }
            )
            result["receipts"][token] = isolated["receipts"][token]
            result["revision"] += 1
        return result, old["id"], claim
    if old:
        op = {
            "op": "update",
            "id": old["id"],
            "expected_revision": old["revision"],
            "reason": "Actual saved prose, not simulated event state",
            "claim": claim,
            "status": status,
            "source_refs": refs,
        }
    else:
        op = {
            "op": "add",
            "subject": row["subject"],
            "attribute": row["attribute"],
            "kind": row["kind"],
            "claim": claim,
            "status": status,
            "source_refs": refs,
        }
    result = apply_delta(memory, {"changes": [op]}, chapters, token)
    item = (
        result["items"][old["id"]]
        if old
        else next(
            v
            for v in result["items"].values()
            if (v["subject"], v["attribute"], v["kind"], v["claim"], v["status"])
            == (row["subject"], row["attribute"], row["kind"], claim, status)
        )
    )
    item["provenance_scope"] = "model_bound_saved_prose_not_plan_certification"
    item["structured_prose_order"] = [number, projection_position]
    label = row.get("canonical_record", {}).get("attribute_label") or row.get(
        "proposed_record", {}
    ).get("attribute")
    if label is not None:
        result.setdefault("attribute_labels", {})[row["attribute"]] = label
    return result, item["id"], claim


def _decision(value, by_position, segments, *, quote_repairs=None):
    fields(
        value,
        ("candidate_position", "outcome", "support", "reason"),
        ("task_status", "unsupported_details"),
    )
    value = copy.deepcopy(value)
    position = value["candidate_position"]
    if type(position) is not int or position not in by_position:
        raise ContractError("Select an existing candidate_position integer")
    if value["outcome"] not in ("matched", "partial", "absent", "uncertain"):
        raise ContractError("Unknown grounding outcome")
    if not isinstance(value["reason"], str) or not value["reason"].strip():
        raise ContractError("Grounding reason required")
    if not isinstance(value["support"], list):
        raise ContractError("support must be a list")
    if value["outcome"] == "partial" and (
        not isinstance(value.get("unsupported_details"), str)
        or not value["unsupported_details"].strip()
    ):
        raise ContractError("Partial grounding requires unsupported_details")
    if value["outcome"] != "partial" and "unsupported_details" in value:
        raise ContractError("Only partial grounding accepts unsupported_details")
    if value["outcome"] not in SUPPORTED_OUTCOMES:
        if value["support"] or value.get("task_status") is not None:
            raise ContractError("Unconfirmed plans cannot supply facts")
        value["status"] = None
        return value
    if by_position[position]["kind"] == "task":
        if value.get("task_status") not in ("planned", "completed", "cancelled"):
            raise ContractError("Tasks require task_status planned/completed/cancelled")
        value["status"] = value["task_status"]
    else:
        if value.get("task_status") is not None:
            raise ContractError("Only tasks accept task_status")
        value["status"] = "active"
    if not value["support"]:
        raise ContractError("Matched memory needs valid status and source quotes")
    for source in value["support"]:
        fields(source, ("evidence_position", "quote"))
        n = source["evidence_position"]
        quote = source["quote"]
        if type(n) is not int or not 1 <= n <= len(segments):
            raise ContractError("Unknown evidence_position")
        if (
            isinstance(quote, str)
            and quote not in segments[n - 1]["text"]
            and quote_repairs is not None
        ):
            # Only model-added boundary quotation marks may be removed for
            # lookup. Fetch the entire selected source paragraph so attribution,
            # qualifications and negation survive; never store transformed text.
            core = quote.strip().strip("“”‘’\"'")
            actual = segments[n - 1]["text"]
            if core != quote and len(core) >= 8 and actual.count(core) == 1:
                source["quote"] = actual
                quote_repairs.append(
                    {
                        "candidate_position": position,
                        "evidence_position": n,
                        "submitted_quote": quote,
                        "bound_quote": actual,
                        "source_sha256": digest(actual),
                        "rule": "UNIQUE_LITERAL_BODY_FETCH_SELECTED_EVIDENCE",
                    }
                )
                quote = actual
        if (
            not isinstance(quote, str)
            or not quote.strip()
            or quote not in segments[n - 1]["text"]
        ):
            raise ContractError(
                "Quote must occur verbatim in selected saved prose evidence"
            )
    return value


def _bind_support_references(value, segments):
    """Live wire references become literal sources; saved decisions stay strict."""
    result = copy.deepcopy(value)
    bindings = []
    if not isinstance(result, dict) or not isinstance(result.get("support"), list):
        return result, bindings
    for source in result["support"]:
        if not isinstance(source, dict) or "quote" in source:
            continue  # Legacy quotes still require exact validation.
        fields(source, ("evidence_position",))
        position = source["evidence_position"]
        if type(position) is not int or not 1 <= position <= len(segments):
            raise ContractError("Unknown evidence_position")
        source["quote"] = segments[position - 1]["text"]
        bindings.append(
            {
                "candidate_position": result.get("candidate_position"),
                "evidence_position": position,
                "source_sha256": digest(source["quote"]),
                "rule": "PROGRAM_OWNED_EVIDENCE_SEGMENT",
            }
        )
    return result, bindings


def _reference_only_interpretation(value):
    """Do not feed a rejected model quotation back as the repair target."""
    result = copy.deepcopy(value)
    for source in result.get("support", []):
        if isinstance(source, dict):
            source.pop("quote", None)
    return result


def ground(memory, chapters, number, gateway, trace, *, reconsider_absent=False):
    """Bounded per-row repair, durable accepted peers; no prose failure on errors."""
    from .event_first import verify

    chapter = chapters[number - 1]
    commit = verify(chapter["event_commit"])
    if digest(chapter["text"]) != chapter["sha256"]:
        raise ContractError("Saved prose hash mismatch")
    if memory.get("canonical_commits", {}).get(str(number)) != commit["sha256"]:
        raise ContractError("Grounding requires matching committed chapter")
    result = copy.deepcopy(memory)
    omitted = set(result.get("projection_omissions", {}).get(str(number), []))
    if not omitted:
        return result
    journal = result.setdefault("projection_grounding", {}).setdefault(
        str(number),
        {
            "schema": "inf-prose-grounding-v1",
            "chapter_sha256": chapter["sha256"],
            "commit_sha256": commit["sha256"],
            "decisions": {},
        },
    )
    if reconsider_absent:
        journal["reconsideration_passes"] = journal.get("reconsideration_passes", 0) + 1
    if (
        journal["chapter_sha256"] != chapter["sha256"]
        or journal["commit_sha256"] != commit["sha256"]
    ):
        raise ContractError("Grounding source identity changed")
    segments = evidence_segments(chapter["text"])
    binding_repairs = journal.setdefault("binding_repairs", {})
    choices = {
        i: r
        for i, r in enumerate(commit["memory_projection"], 1)
        if r["ref"] in omitted
        and journal["decisions"].get(r["ref"], {}).get("outcome")
        not in SUPPORTED_OUTCOMES
        and (
            reconsider_absent
            or r["ref"] in binding_repairs
            or journal["decisions"].get(r["ref"], {}).get("outcome") != "absent"
        )
    }
    positions = list(choices)
    for start in range(0, len(positions), 24):
        pending = positions[start : start + 24]
        previous_errors = []
        positive = {
            i: copy.deepcopy(binding_repairs[choices[i]["ref"]])
            for i in pending
            if choices[i]["ref"] in binding_repairs
        }
        negative_conflicts = set()
        for attempt in range(3):
            if not pending:
                break
            independent = attempt == 2
            requested = (
                [i for i in pending if i in negative_conflicts]
                if independent
                else list(pending)
            )
            if not requested:
                break
            payload = {
                "chapter_number": number,
                "subject_binding_policy": "记录归属者/涉及对象与原文说话者分别判断；知识可以来自听到的转述，须保留归因和不确定性。",
                "progress_binding_policy": "同一事项分开已发生步骤与尚未确认步骤；部分进展用partial绑定实际原文，不能因终点未写判整项absent，也不能推成已完成终点。",
                "candidates": [
                    {
                        "candidate_position": i,
                        "subject": choices[i]["subject"],
                        "attribute": choices[i]["attribute"],
                        "property_label": choices[i]
                        .get("canonical_record", {})
                        .get("attribute_label", choices[i]["attribute"]),
                        "planned_value": choices[i]
                        .get("canonical_record", {})
                        .get("value"),
                        "kind": choices[i]["kind"],
                        "planned_claim": choices[i]["claim"],
                        "allowed_task_status": ["planned", "completed", "cancelled"]
                        if choices[i]["kind"] == "task"
                        else [],
                        "matched_required_fields": [
                            "candidate_position",
                            "outcome",
                            "support",
                            "reason",
                        ]
                        + (["task_status"] if choices[i]["kind"] == "task" else []),
                    }
                    for i in requested
                ],
                "evidence": [
                    {"evidence_position": i, "text": s["text"]}
                    for i, s in enumerate(segments, 1)
                ],
                "support_protocol": "source_reference_only_v2",
                "output_contract": {
                    "required": ["decisions"],
                    "matched_task_example": {
                        "candidate_position": 1,
                        "outcome": "matched",
                        "support": [{"evidence_position": 1}],
                        "reason": "正文支持此任务",
                        "task_status": "planned",
                    },
                    "instruction": "位置、状态须按实际输入选择；只选位置，原文由程序取回，不返回quote；task_status不能遗漏。",
                },
                "instruction": "正文是唯一事实来源。候选整句无需逐字出现。仅整理记忆，禁止要求重写正文。",
            }
            if reconsider_absent:
                payload["negative_match_policy"] = (
                    "这是独立重新核对。以前的未找到只是模型判断，可能漏读；重新阅读全部证据，不因旧结论而跳过。"
                )
            if positive:
                payload["prior_supported_interpretations"] = {
                    str(i): _reference_only_interpretation(positive[i])
                    for i in requested
                    if i in positive
                }
                payload["repair_scope"] = (
                    "只修证据位置/字段绑定，保留已识别内容，不重抄引文；不能因为引文格式错误改称正文没写。"
                )
            if independent:
                payload["independent_semantic_review"] = True
                payload["repair_scope"] = (
                    "独立重读全部正文，重新判断此前正向解释是否成立；可明确否定，但须给正文依据，不能把格式错误当作未发生。"
                )
            if previous_errors:
                payload["repair_errors"] = previous_errors
            entry = {
                "role": "prose_memory_grounding",
                "chapter": number,
                "attempt": attempt + 1,
                "positions": requested,
                "mode": "independent_semantic_review"
                if independent
                else "bind_or_repair",
            }
            trace.append(entry)
            errors = []
            accepted = {}
            committed = set()
            try:
                if (
                    len(
                        canonical({"system": SYSTEM, "payload": payload}).encode(
                            "utf-8"
                        )
                    )
                    > 96000
                ):
                    raise ContractError(
                        "Grounding request exceeds explicit input bound"
                    )
                reply = gateway.complete(ModelRequest("memory", SYSTEM, payload, 8192))
                entry.update(
                    raw_output=reply.content, finish_reason=reply.finish_reason
                )
                if reply.finish_reason not in (None, "stop"):
                    raise ContractError("Incomplete grounding response")
                from .pipeline import normalize

                parsed, notes = normalize(strict_json(reply.content))
                entry["normalizations"] = notes
                fields(parsed, ("decisions",))
                if not isinstance(parsed["decisions"], list):
                    raise ContractError("decisions must be a list")
                counts = _position_counts(parsed["decisions"])
                for raw in parsed["decisions"]:
                    try:
                        repairs = []
                        bound, bindings = _bind_support_references(raw, segments)
                        decision = _decision(
                            bound,
                            {i: choices[i] for i in requested},
                            segments,
                            quote_repairs=repairs,
                        )
                        i = decision["candidate_position"]
                        if counts[i] != 1:
                            raise ContractError("Duplicate candidate decision")
                        if (
                            decision["outcome"] == "absent"
                            and i in positive
                            and not independent
                        ):
                            negative_conflicts.add(i)
                            raise ContractError(
                                "Negative reinterpretation requires independent semantic review; format failure is not absence"
                            )
                        accepted[i] = decision
                        if bindings:
                            entry.setdefault("source_bindings", []).extend(bindings)
                        if repairs:
                            entry.setdefault("quote_repairs", []).extend(repairs)
                    except (ContractError, TypeError, KeyError) as exc:
                        i = (
                            raw.get("candidate_position")
                            if isinstance(raw, dict)
                            else None
                        )
                        if (
                            type(i) is int
                            and i in requested
                            and counts[i] == 1
                            and raw.get("outcome") in SUPPORTED_OUTCOMES
                        ):
                            positive.setdefault(i, copy.deepcopy(raw))
                        errors.append(
                            {
                                "candidate_position": raw.get("candidate_position")
                                if isinstance(raw, dict)
                                else None,
                                "error": str(exc),
                            }
                        )
            except Exception as exc:
                errors.append(
                    str(exc) if isinstance(exc, ContractError) else type(exc).__name__
                )
            for i in sorted(accepted):
                decision = accepted[i]
                row = choices[i]
                saved = copy.deepcopy(decision)
                if decision["outcome"] in SUPPORTED_OUTCOMES:
                    positive.setdefault(
                        i,
                        {
                            k: copy.deepcopy(v)
                            for k, v in decision.items()
                            if k != "status"
                        },
                    )
                try:
                    if decision["outcome"] in SUPPORTED_OUTCOMES:
                        result, mid, claim = _store(
                            result,
                            chapters,
                            number,
                            row,
                            decision["support"],
                            decision["status"],
                            projection_position=i,
                        )
                        saved.update(memory_id=mid, stored_claim=claim)
                    # apply_delta copies the journal; always rebind after writes.
                    current_journal = result["projection_grounding"][str(number)]
                    prior = current_journal["decisions"].get(row["ref"])
                    if prior and prior != saved:
                        current_journal.setdefault("decision_revisions", []).append(
                            {"ref": row["ref"], "previous": copy.deepcopy(prior)}
                        )
                    current_journal["decisions"][row["ref"]] = saved
                    committed.add(i)
                    if decision["outcome"] in ("matched", "partial", "absent"):
                        positive.pop(i, None)
                except (ContractError, TypeError, KeyError) as exc:
                    errors.append(str(exc))
                    continue
                if decision["outcome"] in ("matched", "partial", "absent"):
                    pending.remove(i)
            current_journal = result["projection_grounding"][str(number)]
            for i in requested:
                ref = choices[i]["ref"]
                if i in positive:
                    current_journal.setdefault("binding_repairs", {})[ref] = (
                        copy.deepcopy(positive[i])
                    )
                else:
                    current_journal.setdefault("binding_repairs", {}).pop(ref, None)
            entry.update(
                status="GROUNDED" if not pending else "PARTIAL",
                errors=errors,
                pending_positions=list(pending),
                validated_positions=sorted(accepted),
                reviewed_positions=sorted(committed),
            )
            previous_errors = errors + [f"Unresolved candidate positions: {pending}"]
    decisions = result["projection_grounding"][str(number)]["decisions"]
    remaining = [
        r["ref"]
        for r in commit["memory_projection"]
        if r["ref"] in omitted
        and decisions.get(r["ref"], {}).get("outcome") not in SUPPORTED_OUTCOMES
    ]
    if remaining:
        result.setdefault("projection_omissions", {})[str(number)] = remaining
    else:
        result.get("projection_omissions", {}).pop(str(number), None)
    gaps = [ref for ref, d in decisions.items() if d["outcome"] == "absent"]
    if gaps:
        result.setdefault("projection_content_gaps", {})[str(number)] = gaps
    else:
        result.get("projection_content_gaps", {}).pop(str(number), None)
    differences = {
        ref: d["unsupported_details"]
        for ref, d in decisions.items()
        if d["outcome"] == "partial"
    }
    if differences:
        result.setdefault("projection_plan_differences", {})[str(number)] = differences
    else:
        result.get("projection_plan_differences", {}).pop(str(number), None)
    return result


def _position_counts(rows):
    return Counter(
        r.get("candidate_position")
        for r in rows
        if isinstance(r, dict) and type(r.get("candidate_position")) is int
    )


def retryable_chapters(memory):
    return [
        n
        for n in pending_chapters(memory)
        if any(
            ref
            in memory.get("projection_grounding", {})
            .get(str(n), {})
            .get("binding_repairs", {})
            or memory.get("projection_grounding", {})
            .get(str(n), {})
            .get("decisions", {})
            .get(ref, {})
            .get("outcome")
            != "absent"
            for ref in memory["projection_omissions"][str(n)]
        )
    ]


def verify_grounding(memory, chapters):
    """Check source bindings and retained memory versions on restore."""
    versions = list(memory["items"].values()) + [
        h["item"] for h in memory.get("history", [])
    ]
    for chapter in chapters[: memory.get("processed_through", 0)]:
        if "event_commit" not in chapter or chapter.get("prose_policy") != "unchecked":
            continue
        key = str(chapter["number"])
        rows = chapter["event_commit"]["memory_projection"]
        decisions = (
            memory.get("projection_grounding", {}).get(key, {}).get("decisions", {})
        )
        omitted = set(memory.get("projection_omissions", {}).get(key, []))
        refs = {r["ref"] for r in rows}
        if omitted - refs:
            raise ContractError("Unknown omitted structured memory reference")
        for row in rows:
            outcome = decisions.get(row["ref"], {}).get("outcome")
            if outcome in SUPPORTED_OUTCOMES and row["ref"] in omitted:
                raise ContractError("Matched structured memory still marked missing")
            if (
                row["claim"] not in chapter["text"]
                and outcome not in SUPPORTED_OUTCOMES
                and row["ref"] not in omitted
            ):
                raise ContractError(
                    "Missing structured memory cannot be marked complete"
                )
        absent = {ref for ref, d in decisions.items() if d["outcome"] == "absent"}
        if set(memory.get("projection_content_gaps", {}).get(key, [])) != absent:
            raise ContractError("Content-gap dispositions changed")
        differences = {
            ref: d["unsupported_details"]
            for ref, d in decisions.items()
            if d["outcome"] == "partial"
        }
        if memory.get("projection_plan_differences", {}).get(key, {}) != differences:
            raise ContractError("Partial projection differences changed")
    for key, journal in memory.get("projection_grounding", {}).items():
        chapter = chapters[int(key) - 1]
        if (
            journal["chapter_sha256"] != digest(chapter["text"])
            or journal["commit_sha256"] != chapter["event_commit"]["sha256"]
        ):
            raise ContractError("Structured prose memory source mismatch")
        rows = dict(enumerate(chapter["event_commit"]["memory_projection"], 1))
        segments = evidence_segments(chapter["text"])
        for ref, raw in journal.get("binding_repairs", {}).items():
            pos = raw.get("candidate_position") if isinstance(raw, dict) else None
            if (
                type(pos) is not int
                or pos not in rows
                or rows[pos]["ref"] != ref
                or raw.get("outcome") not in SUPPORTED_OUTCOMES
            ):
                raise ContractError("Invalid pending positive interpretation")
        for ref, decision in journal["decisions"].items():
            normalized = _decision(
                {
                    k: v
                    for k, v in decision.items()
                    if k not in ("memory_id", "stored_claim", "status")
                },
                rows,
                segments,
            )
            if normalized["status"] != decision["status"]:
                raise ContractError("Structured memory status mismatch")
            row = rows[decision["candidate_position"]]
            if row["ref"] != ref:
                raise ContractError("Structured memory candidate binding changed")
            if decision["outcome"] not in SUPPORTED_OUTCOMES:
                continue
            claim = "\n".join(s["quote"] for s in decision["support"])
            required = {
                segments[s["evidence_position"] - 1]["id"] for s in decision["support"]
            }
            if decision["stored_claim"] != claim or not any(
                v["id"] == decision["memory_id"]
                and v["claim"] == claim
                and v["subject"] == row["subject"]
                and v["attribute"] == row["attribute"]
                and v["kind"] == row["kind"]
                and v["status"] == decision["status"]
                and required
                <= {
                    s["evidence_id"]
                    for s in v["sources"]
                    if s["chapter_number"] == int(key)
                    and s["chapter_sha256"] == chapter["sha256"]
                    and s["quote"]
                    == next(
                        (e["text"] for e in segments if e["id"] == s["evidence_id"]),
                        None,
                    )
                }
                for v in versions
            ):
                raise ContractError("Structured prose memory record missing or changed")
    return True
