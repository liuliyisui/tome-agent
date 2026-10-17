"""Draft-first session: quality failures are pending work, never silent approval.

Working snapshots are wrapped and are NOT FileStore formal checkpoints.
Only jointly checked memory proposals enter the working reliable-fact bank.
"""
import copy
from dataclasses import dataclass, field
import json
from pathlib import Path
import re

from .domain import ContractError, Snapshot, apply_chapter, canonical, digest, fields, text
from .runtime import ContextBuilder


def evidence_segments(draft):
    text(draft, "draft")
    rows = []
    for match in re.finditer(r"[^\r\n]+", draft):
        for offset in range(match.start(), match.end(), 300):
            end = min(offset + 300, match.end())
            rows.append({"id": f"e{len(rows)+1:04d}", "start": offset, "end": end, "text": draft[offset:end]})
    return rows


def normalize_memory(result, state, plan, draft):
    fields(result, ("changes",), ("no_change_reason",))
    changes = result["changes"]
    if not isinstance(changes, list) or len(changes) > 128:
        raise ContractError("Memory changes must be a list with at most 128 candidates")
    if not changes:
        text(result.get("no_change_reason"), "Empty memory requires no_change_reason and independent review")
    catalog = {row["id"]: row["text"] for row in evidence_segments(draft)}
    normalized = []
    for index, candidate in enumerate(changes):
        try:
            fields(candidate, ("action", "subject", "attribute", "value", "expected_revision", "reason"),
                   ("quote", "evidence_id"))
            row = copy.deepcopy(candidate)
            if ("quote" in row) == ("evidence_id" in row):
                raise ContractError("Supply exactly one quote or evidence_id")
            if "evidence_id" in row:
                identifier = row.pop("evidence_id")
                if not isinstance(identifier, str) or identifier not in catalog:
                    raise ContractError("Unknown evidence_id; select from current evidence_segments")
                row["quote"] = catalog[identifier]
            normalized.append(row)
        except ContractError as exc:
            raise ContractError(f"Memory candidate {index}: {exc}") from None
    # Keep all existing stable-name, exact-quote, version and atomicity checks.
    apply_chapter(state, plan, draft, normalized, "memory-validation", "memory-validation")
    return {"changes": normalized, "no_change_reason": result.get("no_change_reason")}


def validate_review(result, context):
    fields(result, ("approved", "issues", "suggestions", "memory_check"))
    if type(result["approved"]) is not bool or not isinstance(result["issues"], list):
        raise ContractError("Invalid review decision")
    if not isinstance(result["suggestions"], list):
        raise ContractError("Suggestions must be a list")
    for suggestion in result["suggestions"]:
        text(suggestion, "suggestion")
    assessment = result["memory_check"]
    fields(assessment, ("status", "reason"))
    if assessment["status"] not in ("sufficient", "missing", "uncertain"):
        raise ContractError("Invalid memory_check status")
    text(assessment["reason"], "Independent memory review reason")
    kinds = {
        "fact_conflict": ("fact_", "past_", "draft_"), "world_rule": ("constraint_",),
        "causality": ("fact_", "past_", "draft_"), "unsupported_memory": ("memory_",),
        "memory_omission": ("draft_", "fact_"),
    }
    for issue in result["issues"]:
        fields(issue, ("kind", "description", "draft_quote", "basis_ref", "basis_quote"))
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
    can_approve = not result["issues"] and assessment["status"] == "sufficient"
    if result["approved"] != can_approve:
        raise ContractError("Review decision inconsistent with hard issues or memory_check")
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
        context = ContextBuilder().build(self.state)
        context.update(instruction=instruction, execution_mode="DRAFT_FIRST_NOT_FORMAL",
                       unresolved_chapters=[r["chapter_number"] for r in self.rows if r["status"] != "DRAFT_CHECKED"],
                       fact_bank_status="Last checked facts; may be stale after unresolved draft chapters. Do not treat silence as proof of no change.")
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
            try:
                review = self.agents["reviewer"].run(review_context, trace,
                    validator=lambda value: validate_review(value, review_context))
                row.update(issues=review["issues"], suggestions=review["suggestions"], memory_check=review["memory_check"])
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
        if draft is not None and row["status"] != "DRAFT_CHECKED":
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
