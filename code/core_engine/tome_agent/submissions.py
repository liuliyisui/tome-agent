"""Single-entry proposals, dependency components and versioned fact ledger."""
from copy import deepcopy
import re
from .state import canonical, digest

NARRATIVE = ("upsert_character_state", "add_past_event", "add_future_requirement",
             "resolve_future_requirement")
ENTRY_FIELDS = {"subject", "key", "action", "value", "temporal_scope", "time_anchor",
                "expected_revision", "category", "epistemic_status", "support_basis",
                "quote", "reason", "consequence"}
CATEGORIES = {"behavior_constraint", "causal_constraint", "quantity_time", "world_rule",
              "obligation", "personality", "emotion", "transient_detail"}
SUPPORT = {"explicit_statement", "repeated_events", "explicit_transition", "single_observation", "uncertain"}


def identity(subject, key):
    return canonical([subject, key])


def entry_errors(entry, text):
    errors = []
    if not isinstance(entry, dict):
        return ["Entry must be an object"]
    if set(entry) != ENTRY_FIELDS:
        errors.append("Entry fields do not match protocol")
    for key in ("subject", "key", "quote", "reason", "consequence", "time_anchor"):
        if not isinstance(entry.get(key), str) or not entry[key].strip():
            errors.append(f"Nonempty {key} required")
    key = entry.get("key")
    if not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", key):
        errors.append("Stable lower_snake_case key required")
    if isinstance(entry.get("subject"), str) and entry["subject"] != entry["subject"].strip():
        errors.append("Subject must be trimmed")
    quote = entry.get("quote")
    if not isinstance(quote, str) or not quote.strip() or quote not in text:
        errors.append("Quote must occur in accepted current prose")
    action = entry.get("action")
    if action not in ("store", "update", "retire", "omit", "defer"):
        errors.append("Unknown action")
    scope, anchor = entry.get("temporal_scope"), entry.get("time_anchor")
    if scope not in ("current", "historical") or (scope == "current") != (anchor == "current"):
        errors.append("Invalid time scope/anchor")
    rev = entry.get("expected_revision")
    if action in ("store", "omit", "defer") and rev is not None:
        errors.append("New/omitted/deferred entries require null revision")
    if action in ("update", "retire") and (type(rev) is not int or rev < 1):
        errors.append("Update/retire require a positive revision")
    if entry.get("category") not in CATEGORIES:
        errors.append("Unknown category")
    if entry.get("epistemic_status") not in ("objective", "subjective", "uncertain"):
        errors.append("Unknown epistemic status")
    if entry.get("support_basis") not in SUPPORT:
        errors.append("Unknown support basis")
    value = entry.get("value")
    if value is not None and type(value) not in (str, int, float, bool):
        errors.append("Value must be a JSON scalar")
    writing = action in ("store", "update", "retire")
    if writing and ((action == "retire") != (value is None)):
        errors.append("Only retirement may write null")
    if writing:
        if entry.get("epistemic_status") == "uncertain" or entry.get("support_basis") == "uncertain":
            errors.append("Uncertain proposals must omit or defer")
        if entry.get("epistemic_status") == "subjective" and not str(key).startswith("belief_"):
            errors.append("Subjective facts require observer subject and belief_ key")
        if entry.get("category") == "personality" and entry.get("support_basis") == "single_observation":
            errors.append("Single observation cannot establish durable personality")
    try:
        canonical(entry)
    except (TypeError, ValueError):
        errors.append("Invalid/nonfinite JSON")
    return errors


def apply_entry(state, entry, chapter, text):
    if entry["action"] in ("omit", "defer"):
        return
    slot = identity(entry["subject"], entry["key"])
    old = state.facts.get(slot)
    action = entry["action"]
    if action == "store" and old is not None:
        raise ValueError("Identity already exists; use current revision")
    if action != "store":
        if old is None or old["revision"] != entry["expected_revision"]:
            raise ValueError("Missing identity or stale revision")
        if (old["temporal_scope"], old["time_anchor"]) != (entry["temporal_scope"], entry["time_anchor"]):
            raise ValueError("Time anchor cannot change in place")
        if old["status"] == "retired" and (action != "update" or chapter <= old["evidence"]["chapter"]):
            raise ValueError("Reactivation requires an update in a later chapter")
    evidence = {"chapter": chapter, "source_hash": digest(text), "quote": entry["quote"]}
    if old is not None:
        archived = deepcopy(old)
        archived["archived_by"] = {**evidence, "reason": entry["reason"]}
        archived["archive_action"] = "retire" if action == "retire" else "replace"
        state.history.append(archived)
    state.facts[slot] = {k: deepcopy(entry[k]) for k in ("subject", "key", "value", "temporal_scope",
        "time_anchor", "category", "epistemic_status", "support_basis", "reason", "consequence")}
    state.facts[slot].update(revision=old["revision"] + 1 if old else 1,
        status="retired" if action == "retire" else "active", evidence=evidence,
        perspective_owner=entry["subject"] if entry["epistemic_status"] == "subjective" else "")


def resources(group):
    result = set()
    def norm(s):
        return " ".join(s.split()).casefold()
    for entry in group["entries"]:
        if isinstance(entry, dict) and isinstance(entry.get("subject"), str):
            result.add(("character", norm(entry["subject"])))
    for item in group["upsert_character_state"]:
        if isinstance(item, dict) and isinstance(item.get("name"), str):
            result.add(("character", norm(item["name"])))
    for field in NARRATIVE[1:]:
        for item in group[field]:
            if isinstance(item, dict) and isinstance(item.get("key"), str):
                result.add(("event" if field == "add_past_event" else "requirement", norm(item["key"])))
    return result


def components(groups):
    by_id = {g["id"]: g for g in groups}
    edges = {gid: set(g["depends_on"]) for gid, g in by_id.items()}
    for g in groups:
        for other in groups:
            if g["id"] != other["id"] and resources(g) & resources(other):
                edges[g["id"]].add(other["id"])
    for gid in list(edges):
        for other in list(edges[gid]):
            edges[other].add(gid)
    seen = set()
    for gid in by_id:
        if gid in seen:
            continue
        queue, part = [gid], set()
        while queue:
            item = queue.pop()
            if item not in part:
                part.add(item)
                queue.extend(edges[item] - part)
        seen |= part
        yield [g for g in groups if g["id"] in part]


def apply_narrative(state, group, chapter):
    for field in NARRATIVE:
        for item in group[field]:
            if not isinstance(item, dict):
                raise ValueError("Narrative operation must be an object")
            if field == "upsert_character_state":
                if set(item) != {"name", "description"}:
                    raise ValueError("Character requires name/description")
                if not all(isinstance(v, str) and v.strip() for v in item.values()):
                    raise ValueError("Character fields must be nonempty")
                key = " ".join(item["name"].split()).casefold()
                state.characters[key] = {**item, "chapter": chapter}
            else:
                expected = {"key"} if field == "resolve_future_requirement" else {"key", "description"}
                if set(item) != expected or not all(isinstance(v, str) and v.strip() for v in item.values()):
                    raise ValueError("Event/requirement requires key and, for additions, description")
                bucket = state.past_events if field == "add_past_event" else state.future_requirements
                key = " ".join(item["key"].split()).casefold()
                if field == "resolve_future_requirement":
                    if key not in bucket or bucket[key].get("resolved"):
                        raise ValueError("Requirement missing or already resolved")
                    bucket[key] = {**bucket[key], "resolved": True, "resolved_chapter": chapter}
                else:
                    if key in bucket:
                        raise ValueError("Event/requirement key already exists")
                    bucket[key] = {**item, "chapter": chapter, "resolved": False}


def submit_groups(state, payload, chapter, text):
    """Independent components stage; pending survives empty/unrelated submissions."""
    try:
        canonical(payload)
        if not isinstance(payload, dict) or set(payload) != {"groups"} or not isinstance(payload["groups"], list):
            raise ValueError("Expected only groups array")
        groups = payload["groups"]
        ids = []
        for g in groups:
            if not isinstance(g, dict) or set(g) != {"id", "depends_on", "entries", *NARRATIVE}:
                raise ValueError("Group fields do not match protocol")
            if not isinstance(g["id"], str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", g["id"]):
                raise ValueError("Invalid group id")
            if any(not isinstance(g[k], list) for k in ("depends_on", "entries", *NARRATIVE)):
                raise ValueError("Group operations must be arrays")
            ids.append(g["id"])
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate group ids")
        for g in groups:
            deps = g["depends_on"]
            if any(not isinstance(d, str) or d not in ids or d == g["id"] for d in deps) or len(set(deps)) != len(deps):
                raise ValueError("Dependencies must reference other groups in this request")
    except (ValueError, TypeError) as exc:
        return {"ok": False, "error": str(exc), "pending": sorted(state.pending)}
    results = []
    for part in components(groups):
        trial, errors, replayed = deepcopy(state), [], True
        for g in part:
            slot = f"{chapter}:{g['id']}"
            receipt = {"chapter": chapter, "source_hash": digest(text), "payload_hash": digest(canonical(g))}
            if slot in state.receipts:
                if state.receipts[slot] != receipt:
                    errors.append({"group": g["id"], "error": "Successful group is immutable"})
                continue
            replayed = False
            seen = set()
            for i, entry in enumerate(g["entries"]):
                issues = entry_errors(entry, text)
                if not issues:
                    pair = identity(entry["subject"], entry["key"])
                    if pair in seen:
                        issues.append("Duplicate candidate identity")
                    seen.add(pair)
                if issues:
                    errors.append({"group": g["id"], "entry": i, "errors": issues})
                else:
                    try:
                        apply_entry(trial, entry, chapter, text)
                    except ValueError as exc:
                        errors.append({"group": g["id"], "entry": i, "error": str(exc)})
            try:
                apply_narrative(trial, g, chapter)
            except ValueError as exc:
                errors.append({"group": g["id"], "error": str(exc)})
            trial.receipts[slot] = receipt
            trial.pending.pop(slot, None)
        if errors:
            for g in part:
                slot = f"{chapter}:{g['id']}"
                if slot not in state.receipts:
                    state.pending[slot] = {"proposal": deepcopy(g), "errors": errors, "source_hash": digest(text)}
        else:
            state.__dict__.update(deepcopy(trial.__dict__))
        results.append({"groups": [g["id"] for g in part], "errors": errors,
                        "status": "pending" if errors else "replayed" if replayed else "accepted"})
    audit = {"chapter": chapter, "source_hash": digest(text), "payload": deepcopy(payload), "results": results}
    if any(r["status"] != "replayed" for r in results) and audit not in state.attempts:
        state.attempts.append(audit)
    return {"ok": not state.pending and not any(r["errors"] for r in results),
            "results": results, "pending": sorted(state.pending)}


def attribute_history(state, subject, key, chapters, limit=5):
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("History limit must be 1..100")
    rows = sorted((f for f in state.history if (f["subject"], f["key"]) == (subject, key)),
                  key=lambda f: f["revision"], reverse=True)[:limit]
    for fact in rows:
        state.check_evidence(fact["evidence"], chapters)
        state.check_evidence(fact["archived_by"], chapters)
    return deepcopy(rows)
