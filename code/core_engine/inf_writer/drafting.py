"""Draft-first session: quality failures are pending work, never silent approval.

Working snapshots are wrapped and are NOT FileStore formal checkpoints.
Strict modes promote only jointly checked proposals. Opt-in light draft mode
updates its working memory for retained prose after mechanical validation,
independently of editorial review. Neither is a semantic correctness proof.
"""
import copy
from dataclasses import dataclass, field
import json
from pathlib import Path
import re

from .domain import ContractError, Snapshot, apply_chapter, canonical, digest, fields, identity, text
from .domain import evidence_segments, checked_support, validate_support_review
from .runtime import ContextBuilder


class DuplicateMemoryError(ContractError):
    """Reject the whole proposal, with evidence-preserving hints for one repair."""
    def __init__(self, groups):
        labels = "; ".join(f"{g['subject']}.{g['attribute']} indices={g['indices']}" for g in groups)
        super().__init__("At most one final change per attribute per chapter; " + labels)
        self.repair_details = {
            "code": "DUPLICATE_MEMORY_ATTRIBUTE", "index_base": 0,
            "groups": copy.deepcopy(groups),
            "guidance": [
                "数组顺序不是故事时间。依据正文判断章末状态，不能直接取最后一条。",
                "同一宽泛知识/怀疑属性可能含不同信息；合并仍有效内容，不能为了去重只保留最后一条。",
                "确属不同语义的事实可用语义明确且稳定的属性分别表达，不用编号后缀绕过检查。",
                "保留重要中间事件或其后果的证据，最终值与全部合并信息都需正文支持。",
                "已有属性用原revision的一次update，新属性才store；不要构造章内连续版本。",
                "返回完整changes，保留不相关且正确的候选。程序没有选择、合并或提交任何候选。",
            ],
        }


def normalize_memory(result, state, plan, draft):
    fields(result, ("changes",), ("no_change_reason",))
    changes = result["changes"]
    if not isinstance(changes, list) or len(changes) > 128:
        raise ContractError("Memory changes must be a list with at most 128 candidates")
    if not changes:
        text(result.get("no_change_reason"), "Empty memory requires no_change_reason and independent review")
    catalog = {row["id"]: row["text"] for row in evidence_segments(draft)}
    normalized, grouped, errors = [], {}, []
    for index, candidate in enumerate(changes):
        try:
            from .memory_action_contract import check_memory_action
            check_memory_action(candidate, state, index, changes)
            is_patch = isinstance(candidate,dict) and 'claim_ops' in candidate
            if is_patch:
                from .claim_updates import resolve_patch
                row = resolve_patch(candidate,state,draft)
            else:
                from .memory_output_contract import derive_value
                row = derive_value(candidate,draft)
                fields(row, ("action", "subject", "attribute", "value", "expected_revision", "reason"),
                       ("quote", "evidence_id", "support"))
            if not is_patch and sum(name in row for name in ('quote','evidence_id','support')) != 1:
                raise ContractError("Supply exactly one quote, evidence_id or support")
            if not is_patch and 'support' in row:
                row['support'] = checked_support(row['support'], draft, row['value'], retire=row['action']=='retire')
            if "evidence_id" in row:
                identifier = row.pop("evidence_id")
                if not isinstance(identifier, str) or identifier not in catalog:
                    raise ContractError("Unknown evidence_id; select from current evidence_segments")
                row["quote"] = catalog[identifier]
            # Diagnose against the unchanged input state, never auto-convert actions.
            key = identity(row["subject"], row["attribute"])
            old = state.facts.get(key)
            label = f"{row['subject']}.{row['attribute']}"
            if row["action"] == "store" and (old is not None or row["expected_revision"] is not None):
                if old is not None:
                    raise ContractError(f"{label} already exists with revision={old['revision']}; "
                                        "use update for a changed value and match that revision, or omit an unchanged fact")
                raise ContractError(f"New attribute {label} requires store with expected_revision=null")
            if row["action"] in ("update", "retire") and (old is None or
                    type(row["expected_revision"]) is not int or row["expected_revision"] != old["revision"]):
                current = old["revision"] if old is not None else "absent"
                raise ContractError(f"{label}: current revision={current}, proposed revision={row['expected_revision']}; "
                                    "update/retire must match an existing attribute revision; do not invent one")
            group = grouped.setdefault(key, {"subject": row["subject"], "attribute": row["attribute"],
                "indices": [], "candidates": [],
                "current": {name: copy.deepcopy(old[name]) for name in ("value", "revision", "status")} if old else None})
            group["indices"].append(index)
            group["candidates"].append(copy.deepcopy(candidate))
            normalized.append(row)
        except ContractError as exc:
            from .memory_output_contract import candidate_error
            errors.append(candidate_error(candidate,index,exc,draft))
    duplicates = [group for group in grouped.values() if len(group["indices"]) > 1]
    if errors:
        error=ContractError(f"Memory candidate {errors[0]['candidate_index']}: {errors[0]['error']}")
        if len(errors)==1 and not duplicates:
            error.repair_details=errors[0]
        else:
            # Raw previous_output already contains the batch; avoid duplicating it per error.
            compact=copy.deepcopy(errors)
            for detail in compact:
                detail.pop('candidates',None)
            error.repair_details=dict(code='MEMORY_BATCH_ERRORS',index_base=0,candidate_errors=compact)
            if duplicates:error.repair_details['duplicate_groups']=duplicates
        raise error from None
    if duplicates:
        raise DuplicateMemoryError(duplicates)
    # Keep all existing stable-name, exact-quote, version and atomicity checks.
    apply_chapter(state, plan, draft, normalized, "memory-validation", "memory-validation")
    return {"changes": normalized, "no_change_reason": result.get("no_change_reason")}


def validate_review(result, context):
    if context.get('review_mode')=='light_memory':
        from .light_memory import prepare_review,validate_light_review
        return validate_light_review(result,prepare_review(context),resolved=True)
    if context.get('review_policy_version')==5:
        from .judgment_review import validate_resolved
        return validate_resolved(result,context)
    fields(result, ("approved", "issues", "suggestions", "memory_check"), ('support_checks','coverage_checks') if context.get('review_policy_version') in (3,4,5) else ('support_checks',))
    validate_support_review(result, context)
    if type(result["approved"]) is not bool or not isinstance(result["issues"], list):
        raise ContractError("Invalid review decision")
    if not isinstance(result["suggestions"], list):
        raise ContractError("Suggestions must be a list")
    for suggestion in result["suggestions"]:
        text(suggestion, "suggestion")
    assessment = result["memory_check"]
    split=context.get('review_policy_version') in (2,3,4,5)
    if split:
        from .review_state import validate_coverage
        validate_coverage(result)
    else:
        fields(assessment, ("status", "reason"))
        if assessment["status"] not in ("sufficient", "missing", "uncertain"):
            raise ContractError("Invalid memory_check status")
        text(assessment["reason"], "Independent memory review reason")
    kinds = {
        "fact_conflict": ("fact_", "past_", "draft_"), "world_rule": ("constraint_",),
        "causality": ("fact_", "past_", "draft_"), "unsupported_memory": ("memory_",),
        "memory_omission": ("draft_", "fact_"),
    }
    policy=context.get('review_policy_version') in (1,2,3,4,5)
    for index,issue in enumerate(result["issues"]):
        try:
            fields(issue, ("kind", "description", "draft_quote", "basis_ref", "basis_quote"),('omission',) if policy else ())
            kind, ref = issue["kind"], issue["basis_ref"]
            if not isinstance(kind, str) or kind not in kinds or not isinstance(ref, str) or not ref.startswith(kinds[kind]):
                raise ContractError("Hard issue needs a supported kind and appropriate factual reference, not a future plan")
            if ref not in context["hard_references"]:
                raise ContractError("Hard issue cites an unavailable reference")
            if text(issue["draft_quote"], "draft quote") not in context["current_draft"]:
                raise ContractError("Hard issue quote not in current draft")
            if text(issue["basis_quote"], "basis quote") not in context["hard_references"][ref]:
                raise ContractError("Hard issue basis_quote not in cited reference")
            text(issue["description"], "hard issue description")
            if policy and kind=='memory_omission':
                from .review_policy import validate_omission
                validate_omission(issue,context)
        except ContractError as exc:
            if not policy:raise
            from .review_policy import issue_error
            raise issue_error(exc,issue,index,context) from None
    if split:
        if context.get('review_policy_version') in (3,4,5):
            from .semantic_review import validate
            validate(result,context)
        from .review_state import validate_state
        return validate_state(result)
    if policy:
        from .review_policy import validate_missing_status
        validate_missing_status(result)
    can_approve = not result["issues"] and assessment["status"] == "sufficient"
    if result["approved"] != can_approve:
        from .review_contract import review_decision_error
        raise review_decision_error(result)
    return result


def resource_failure(exc):
    return type(exc).__name__ == "ProviderError" or any(
        word in str(exc).lower() for word in ("budget/deadline", "exceeded reservation", "input exceeds", "transport"))


@dataclass
class DraftSession:
    output: Path
    state: Snapshot
    agents: dict
    rows: list = field(default_factory=list)

    def write_next(self, instruction):
        number = len(self.state.chapters) + 1
        trace = []
        row = {"chapter_number": number, "status": "NO_DRAFT", "issues": [], "suggestions": [],
               "errors": [], "memory_promoted": False, "stop_reason": None}
        context = ContextBuilder(include_fact_sources=not getattr(self.agents['planner'],'compact_narrative',False)).build(self.state)
        context.update(instruction=instruction, execution_mode="DRAFT_FIRST_NOT_FORMAL",
                       unresolved_chapters=[r["chapter_number"] for r in self.rows if r["status"] != "DRAFT_CHECKED"],
                       fact_bank_status="Last checked facts; may be stale after unresolved draft chapters. Do not treat silence as proof of no change.")
        timely_memory = getattr(self.agents['reviewer'],'review_mode',None)=='light_memory'
        if timely_memory:
            context['fact_bank_status']='Working memory updated from retained drafts after mechanical checks; prose review is separate. Extraction can fail or be mistaken; silence is not proof of no change.'
        proposal, draft, candidate, memory = None, None, None, None
        try:
            def check_plan(value):
                if value["number"] != number:
                    raise ContractError("Plan must address the next draft chapter")
                # Validate future patch restrictions before spending a writer call.
                apply_chapter(self.state, value, "plan-validation", [], "plan-validation", "plan-validation")
                return value
            try:
                proposal = self.agents["planner"].run(context, trace, validator=check_plan)
            except Exception as exc:
                if resource_failure(exc):
                    raise
                row["errors"].append("planner: " + str(exc))
                proposal = {"number": number, "title": f"续写{number}", "brief": instruction, "future_updates": []}
            writing_context = {**context, "chapter_plan": proposal}
            draft = self.agents["writer"].run(writing_context, trace)["text"]
            memory_context = {**writing_context, "current_draft": draft, "evidence_segments": evidence_segments(draft)}
            try:
                memory = self.agents["memory"].run(memory_context, trace,
                    validator=lambda value: normalize_memory(value, self.state, proposal, draft))
                candidate = apply_chapter(self.state, proposal, draft, memory["changes"], f"draft{number}", digest(instruction))
            except Exception as exc:
                row["errors"].append("memory: " + str(exc))
                if resource_failure(exc):
                    raise
            references = {f"constraint_{i}": item for i, item in enumerate(self.state.constraints, 1)}
            references.update({f"fact_{i}": canonical(item) for i, item in enumerate(self.state.active_facts(), 1)})
            references.update({f"draft_{item['id']}": item["text"] for item in evidence_segments(draft)})
            for chapter in context["recent_chapters"]:
                # An unchecked past chapter is narrative context, not a factual authority.
                prior = next((item for item in self.rows if item["chapter_number"] == chapter["number"]), None)
                if prior and prior["status"] == "DRAFT_CHECKED":
                    references[f"past_{chapter['number']}"] = chapter["text"]
            changes = memory["changes"] if memory is not None else []
            references.update({f"memory_{i}": canonical(item) for i, item in enumerate(changes, 1)})
            review_context = {**memory_context, "memory_changes": changes,
                "memory_no_change_reason": memory.get("no_change_reason") if memory else None,
                "memory_extraction_failed": memory is None, "hard_references": references}
            if getattr(self.agents['reviewer'],'review_mode',None)=='light_memory':
                review_context['review_mode']='light_memory'
                row['review_scope']='STORY_REVIEW_AND_MECHANICAL_MEMORY_ONLY'
                row['memory_semantic_review']='not_checked'
            if getattr(self.agents['reviewer'],'review_contract_version',0)==1:
                from .review_contract import prepare_review_context
                review_context=prepare_review_context(review_context)
                if getattr(self.agents['reviewer'],'review_policy_version',0) in (1,2,3,4,5):
                    from .review_policy import prepare_policy_context
                    review_context['review_policy_version']=self.agents['reviewer'].review_policy_version
                    review_context=prepare_policy_context(review_context)
            try:
                review = self.agents["reviewer"].run(review_context, trace,
                    validator=lambda value: validate_review(value, review_context))
                row.update(issues=review["issues"], suggestions=review["suggestions"], memory_check=review["memory_check"])
                if review_context.get('review_policy_version') in (2,3,4,5):
                    from .review_state import support_summary
                    row['support_summary']=support_summary(review)
                if review_context.get('review_policy_version') in (3,4,5):
                    row['coverage_checks']=copy.deepcopy(review['coverage_checks'])
                    if review_context.get('review_policy_version')==4:
                        from .locator_review import coverage_locations
                        row['coverage_locations']=coverage_locations(review,review_context)
                if candidate is not None and review["approved"] and not row["errors"]:
                    self.state = candidate
                    row.update(status="DRAFT_CHECKED", memory_promoted=bool(changes))
            except Exception as exc:
                row["errors"].append("reviewer: " + str(exc))
                if resource_failure(exc):
                    raise
        except Exception as exc:
            row["errors"].append(type(exc).__name__ + ": " + str(exc))
            row["stop_reason"] = "RESOURCE_OR_TRANSPORT" if resource_failure(exc) else "NO_USABLE_DRAFT"
        # A retained draft is the story being continued. In light mode, its
        # mechanically valid memory must not remain stale because an unrelated
        # editorial review rejected or failed. Never promote a failed proposal.
        if timely_memory and candidate is not None:
            self.state = candidate
            row['memory_promoted'] = bool(memory['changes'])
            row['memory_update_status'] = 'APPLIED' if memory['changes'] else 'NO_CHANGE'
        elif timely_memory:
            row['memory_update_status'] = 'FAILED' if draft is not None else 'NOT_RUN'
        if draft is not None and row["status"] != "DRAFT_CHECKED":
            if not (timely_memory and candidate is not None):
                self.state = apply_chapter(self.state, proposal, draft, [], f"draft{number}", digest(instruction))
            row["status"] = "DRAFT_UNCHECKED"
        self.rows.append(row)
        record = {"mode": "DRAFT_FIRST_NOT_FORMAL", "state": self.state.to_dict(),
                  "chapter": row, "model_calls": trace, "unresolved_chapters": context["unresolved_chapters"] +
                  ([number] if row["status"] == "DRAFT_UNCHECKED" else [])}
        self.output = Path(self.output)
        self.output.mkdir(parents=True, exist_ok=True)
        with (self.output / f"draft_chapter_{number:03d}.json").open("x", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
        return row
