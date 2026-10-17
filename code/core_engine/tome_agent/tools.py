"""Tome-specific wire schemas; no direct NST checkpoint/wire compatibility."""
from .submissions import CATEGORIES, SUPPORT


def obj(properties):
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


def array(items):
    return {"type": "array", "items": items}


def chapter_tools():
    string = {"type": "string"}
    entry = obj({
        "subject": string, "key": {"type": "string", "description": "Stable attribute name, e.g. eye_color; never embed the value in the key."},
        "action": {"type": "string", "enum": ["store", "update", "retire", "omit", "defer"]},
        "value": {"type": ["string", "number", "boolean", "null"]},
        "temporal_scope": {"type": "string", "enum": ["current", "historical"]},
        "time_anchor": string, "expected_revision": {"type": ["integer", "null"]},
        "category": {"type": "string", "enum": sorted(CATEGORIES)},
        "epistemic_status": {"type": "string", "enum": ["objective", "subjective", "uncertain"]},
        "support_basis": {"type": "string", "enum": sorted(SUPPORT)},
        "quote": string, "reason": string, "consequence": string})
    group = obj({"id": string, "depends_on": array(string), "entries": array(entry),
        "upsert_character_state": array(obj({"name": string, "description": string})),
        "add_past_event": array(obj({"key": string, "description": string})),
        "add_future_requirement": array(obj({"key": string, "description": string})),
        "resolve_future_requirement": array(obj({"key": string}))})
    schemas = {"read": obj({"chapter": {"type": "integer"}}),
        "search": obj({"query": string}),
        "correct": obj({"chapter": {"type": "integer"}, "old": string, "new": string}),
        "write": obj({"text": string}), "update": obj({"groups": array(group)})}
    return [{"type": "function", "function": {"name": name,
        "description": description, "parameters": schemas[name]}}
        for name, description in {
            "read": "Read one prior chapter within the read budget.",
            "search": "Search prior chapters for literal text and return bounded excerpts.",
            "correct": "Replace exact prose only if no accepted memory group binds that source.",
            "write": "Submit a complete chapter draft subject to target length bounds.",
            "update": "Submit single-entry memory proposals and narrative changes in atomic dependency groups. Repair pending groups before DONE."
        }.items()]
