"""Source-bound meaning labels and effective views, independent of tiers."""

from .domain import ContractError, canonical, digest
from .memory_temporality import annotated, time_view

CLAIM_TYPES = (
    "current_state",
    "historical_event",
    "character_statement",
    "character_belief",
    "intention",
    "task",
    "mixed",
    "unclassified",
)
EPISTEMIC_STATES = (
    "narration_confirmed",
    "reported_unverified",
    "hypothesis",
    "uncertain",
    "mixed",
    "not_assessed",
)


def content_key(row):
    # Tier moves, task lifecycle and revision counters do not rewrite a claim.
    return digest(
        canonical(
            {
                k: row.get(k)
                for k in ("subject", "attribute", "kind", "claim", "sources")
            }
        )
    )


def valid_annotation(row):
    value = row.get("meaning_annotation")
    return bool(
        isinstance(value, dict)
        and value.get("content_sha256") == content_key(row)
        and value.get("sha256")
        == digest(canonical({k: v for k, v in value.items() if k != "sha256"}))
    )


def meaning_view(row, *, historical=False):
    item = annotated(row)
    parts = {p["id"]: p for p in item["temporality"]["parts"]}
    scope = time_view(row)["time_scope"]
    units = []
    if valid_annotation(row):
        for unit in row["meaning_annotation"]["units"]:
            spans = [parts[i] for i in unit["part_ids"]]
            live = [p for p in spans if p["scope"] == "current"]
            validity = (
                "historical"
                if historical
                else "current"
                if len(live) == len(spans)
                else "historical"
                if not live
                else "mixed"
            )
            conflicts = sorted(
                {r for p in spans for r in p.get("meaning_conflict_ids", [])}
            )
            units.append(
                {
                    "claim_type": unit["claim_type"],
                    "epistemic_status": unit["epistemic_status"],
                    "perspective_owner": unit["perspective_owner"],
                    "text": "；".join(p["text"] for p in spans),
                    "perspective_resolution": "source_bound"
                    if unit["perspective_owner"]
                    else "unknown"
                    if unit["claim_type"] in ("character_statement", "character_belief")
                    else "not_applicable",
                    "part_ids": unit["part_ids"],
                    "validity": validity,
                    "conflict_ids": conflicts,
                    "usable_as_current_fact": validity == "current"
                    and not conflicts
                    and unit["claim_type"] in ("current_state", "historical_event")
                    and unit["epistemic_status"] == "narration_confirmed"
                    and unit["perspective_owner"] is None,
                }
            )
    task_parts = [
        parts[i]
        for u in (
            row.get("meaning_annotation", {}).get("units", [])
            if valid_annotation(row)
            else []
        )
        if u["claim_type"] in ("intention", "task")
        for i in u["part_ids"]
    ]
    task_state = "not_applicable"
    if row["kind"] == "task" or task_parts:
        if row["status"] in ("completed", "cancelled"):
            task_state = row["status"]
        elif task_parts and all(p["scope"] == "historical" for p in task_parts):
            relations = {
                p.get("meaning_relation", p.get("relation")) for p in task_parts
            }
            task_state = (
                "completed"
                if relations <= {"completes", "completed"}
                else "cancelled"
                if relations <= {"cancels"}
                else "superseded"
            )
        elif task_parts and any(p["scope"] == "historical" for p in task_parts):
            task_state = "partial"
        else:
            task_state = "planned" if row["kind"] == "task" else "unresolved"
    if row["kind"] == "prose_excerpt":
        return {
            "assessed": False,
            "claim_type": "raw_excerpt",
            "epistemic_status": "raw_source",
            "validity": "historical" if historical else scope,
            "task_state": "not_applicable",
            "usable_as_current_fact": False,
            "reading_rule": "原文证据片段，可能含旧状态、猜测和计划；不得整体当作当前事实。",
        }
    return {
        "assessed": valid_annotation(row),
        "validity": "historical" if historical else scope,
        "task_state": task_state,
        "units": units,
        "previous_content_sha256": row.get("meaning_previous_version", {}).get(
            "content_sha256"
        ),
        "usable_as_current_fact": bool(units)
        and all(u["usable_as_current_fact"] for u in units),
        "reading_rule": "按各含义单元的说话人、证实程度和有效状态使用；层级不表示真假或是否完成。",
    }


def pending_ids(memory):
    pending = {
        i
        for i, r in memory["items"].items()
        if r["kind"] not in ("prose_excerpt", "legacy") and not valid_annotation(r)
    }
    pending.update(
        i
        for job in memory.get("meaning_review_jobs", {}).values()
        for i in job["memory_ids"]
        if i in memory["items"]
    )
    return sorted(pending)


def verify_meanings(memory, chapters):
    """Verify bindings/coverage, not the model's semantic judgment."""
    versions = list(memory["items"].values()) + [
        h["item"] for h in memory.get("history", [])
    ]
    for row in versions:
        value = row.get("meaning_annotation")
        if not value or value.get("content_sha256") != content_key(row):
            continue
        if value.get("sha256") != digest(
            canonical({k: v for k, v in value.items() if k != "sha256"})
        ):
            raise ContractError("Meaning annotation integrity mismatch")
        parts = annotated(row)["temporality"]["parts"]
        ids = [p["id"] for p in parts]
        covered = []
        for unit in value["units"]:
            if (
                unit["claim_type"] not in CLAIM_TYPES
                or unit["epistemic_status"] not in EPISTEMIC_STATES
            ):
                raise ContractError("Unknown meaning label")
            selected = unit["part_ids"]
            covered.extend(selected)
            if not selected or any(i not in ids for i in selected):
                raise ContractError("Meaning unit references unknown parts")
            positions = [ids.index(i) for i in selected]
            if positions != list(range(min(positions), max(positions) + 1)):
                raise ContractError(
                    "Meaning unit must preserve contiguous source order"
                )
            owner = unit["perspective_owner"]
            if owner is not None and (
                not isinstance(owner, str)
                or not owner.strip()
                or not any(
                    owner in s
                    for s in [row["subject"]]
                    + [v["quote"] for v in row.get("sources", [])]
                )
            ):
                raise ContractError("Perspective owner has no source binding")
        if covered != ids or len(covered) != len(set(covered)):
            raise ContractError("Meaning annotation must cover every part exactly once")
    for identifier, relation in memory.get("meaning_relations", {}).items():
        expected = (
            "meaning_"
            + digest(
                canonical(
                    {
                        k: v
                        for k, v in relation.items()
                        if k not in ("reason", "semantic_certification", "resolved_by")
                    }
                )
            )[:24]
        )
        if identifier != expected:
            raise ContractError("Meaning relation integrity mismatch")
        if (
            relation.get("resolved_by")
            and relation["resolved_by"] not in memory["meaning_relations"]
        ):
            raise ContractError("Meaning conflict resolution missing")
        for name in ("earlier", "later"):
            binding = relation[name]
            if not any(
                r["id"] == binding["memory_id"]
                and content_key(r) == binding["content_sha256"]
                and set(binding["part_ids"])
                <= {p["id"] for p in annotated(r)["temporality"]["parts"]}
                for r in versions
            ):
                raise ContractError("Meaning relation source version missing")
        for source in relation["evidence"]:
            n = source["chapter_number"]
            if (
                not 1 <= n <= len(chapters)
                or source["chapter_sha256"] != digest(chapters[n - 1]["text"])
                or source["quote"] not in chapters[n - 1]["text"]
            ):
                raise ContractError("Meaning relation evidence changed")
    return True
