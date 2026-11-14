"""Bound request views without editing stored prose or canonical facts."""

import copy

from tome_writer.domain import canonical, digest


def size(value):
    return len(canonical(value).encode("utf-8"))


def select_qualified_state(view, limit=14000):
    """Select whole, fully decorated rows BEFORE creating reference choices.

    Meaning labels can dwarf the undecorated typed record. Budgeting that old
    representation and enriching it later does not bound the actual request.
    Stored state and its validation directory remain complete.
    """
    result = copy.deepcopy(view)
    rows = result["records"]
    result["records"] = []
    result["selection_scope"] = (
        "Whole records with meaning labels; before reference choice allocation; stored state unchanged"
    )
    for row in rows:
        if size(dict(result, records=result["records"] + [row])) <= limit:
            result["records"].append(row)
        else:
            result["omitted_count"] = result.get("omitted_count", 0) + 1
    return result


def fit(context, limit):
    if size(context) <= limit:
        return context
    result = copy.deepcopy(context)
    changes = []
    before = size(result)
    for chapter in result.get("recent_chapters", []):
        raw = chapter["text"].encode("utf-8")
        if len(raw) > 12000:
            chapter["source_sha256"] = chapter.get("sha256", digest(chapter["text"]))
            chapter["excerpt"] = True
            chapter["text"] = raw[-12000:].decode("utf-8", errors="ignore")
            chapter["sha256"] = digest(chapter["text"])
            changes.append(
                {
                    "field": "recent_chapters",
                    "chapter": chapter["number"],
                    "view": "last_12000_utf8_bytes",
                }
            )
    result["input_selection"] = {
        "original_bytes": before,
        "limit_bytes": limit,
        "stored_sources_unchanged": True,
        "changes": changes,
    }
    # Coverage diagnostics grow with the entire book. They are not reference
    # directories: keep counts in bounded requests, and all IDs in checkpoints.
    for owner, path, keys in (
        (
            result.get("memory_coverage", {}),
            "memory_coverage",
            ("omitted_ids", "source_evidence_omitted"),
        ),
        (result.get("historical_memory", {}), "historical_memory", ("omitted_ids",)),
    ):
        for key in keys:
            values = owner.get(key)
            if (
                size(result) > limit
                and isinstance(values, list)
                and size(values) > 1024
            ):
                owner[key + "_count"] = len(values)
                owner[key] = []
                changes.append(
                    {
                        "field": path + "." + key,
                        "omitted_diagnostic_entries": len(values),
                        "scope": "request_view_only; counts retained",
                    }
                )
    # Remove whole optional retrieval rows, never typed state or choice entries.
    lists = [
        (
            "historical_memory.items",
            result.get("historical_memory", {}).get("items", []),
        ),
        ("resolved_intentions", result.get("resolved_intentions", [])),
        ("source_evidence", result.get("source_evidence", [])),
        ("retrieved_prose_evidence", result.get("retrieved_prose_evidence", [])),
        ("retrieved_memory", result.get("retrieved_memory", [])),
        ("organized_memory", result.get("organized_memory", [])),
        (
            "narrative_continuity.recent_designs",
            result.get("narrative_continuity", {}).get("recent_designs", []),
        ),
        (
            "narrative_continuity.evidence_profiles",
            result.get("narrative_continuity", {}).get("evidence_profiles", []),
        ),
        (
            "narrative_continuity.threads",
            result.get("narrative_continuity", {}).get("threads", []),
        ),
        ("recent_chapters", result.get("recent_chapters", [])),
    ]
    for label, rows in lists:
        if not isinstance(rows, list):
            continue
        removed = 0
        while rows and size(result) > limit:
            rows.pop(0 if label == "recent_chapters" else -1)
            removed += 1
        if removed:
            changes.append(
                {"field": label, "omitted_rows": removed, "scope": "request_view_only"}
            )
            if label == "retrieved_memory" and "memory_coverage" in result:
                coverage = result["memory_coverage"]
                kept = [r["memory_id"] for r in rows if "memory_id" in r]
                added = [i for i in coverage.get("selected_ids", []) if i not in kept]
                if "omitted_ids_count" in coverage:
                    coverage["omitted_ids_count"] += len(added)
                else:
                    coverage["omitted_ids"] = list(
                        dict.fromkeys(coverage.get("omitted_ids", []) + added)
                    )
                coverage["selected_ids"] = kept
        if size(result) <= limit:
            return result
    return result
