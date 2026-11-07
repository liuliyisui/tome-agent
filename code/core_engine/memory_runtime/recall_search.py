"""Bounded question decomposition and diverse retrieval from stored memory.

Query planning supplies search terms, never facts. No original prose is opened.
The final answer and its citations still use only selected stored records.
"""

import re

from inf_writer.domain import ContractError, canonical, fields, strict_json
from inf_writer.memory_meaning import valid_annotation
from inf_writer.models import ModelRequest

SYSTEM = (
    "把用户的记忆问题拆成1至3个独立检索意图。只输出JSON searches数组；每项query字符串、focus字符串。"
    "focus只能action_history/earliest/latest/balanced。query只写检索词，保留人物或物件名，可加入动作的近义表达，不能编造答案。"
    "问行动是否真正发生时用action_history，检索实际过程的不同表述，而非只找后来禁令、计划或岗位状态。"
    "问最初态度用earliest；问最终岗位或正式结论用latest。多问句分开，历史行动不能被后来的禁止或停止安排覆盖。"
    "每个意图query最多240字符，给出正反两面的检索词；不知道的名字、时间或结论不补造。"
)
FOCI = ("action_history", "earliest", "latest", "balanced")


def searches(value):
    fields(value, ("searches",))
    rows = value["searches"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 3:
        raise ContractError("Choose one to three search intents")
    result = []
    for row in rows:
        fields(row, ("query", "focus"))
        if (
            not isinstance(row["query"], str)
            or not row["query"].strip()
            or len(row["query"]) > 240
            or row["focus"] not in FOCI
        ):
            raise ContractError("Invalid memory search intent")
        if row not in result:
            result.append(row)
    return result


def meaningful(memory):
    return any(
        valid_annotation(r)
        and any(
            u["claim_type"] not in ("unclassified", "mixed")
            for u in r["meaning_annotation"]["units"]
        )
        for r in memory["items"].values()
    )


def selection(memory, question, gateway, trace, label, select, *, max_bytes=36000):
    base = select(memory, question, max_bytes=max_bytes)
    if not meaningful(memory):
        return base
    entry = {"role": "memory_lookup", "label": label}
    trace.append(entry)
    try:
        reply = gateway.complete(
            ModelRequest(
                "memory_lookup",
                SYSTEM,
                {
                    "question": question,
                    "output_contract": {
                        "searches": [
                            {
                                "query": "人物/动作/对象的检索词",
                                "focus": "action_history",
                            }
                        ]
                    },
                },
                1024,
            )
        )
        entry["raw_output"] = reply.content
        if reply.finish_reason not in ("stop", None):
            raise ContractError("Incomplete lookup response")
        queries = searches(strict_json(reply.content))
        pools = [
            select(memory, row["query"], max_bytes=12000, focus=row["focus"])
            for row in queries
        ]
    except Exception as exc:
        entry.update(status="DEFERRED", error_type=type(exc).__name__)
        return base
    chosen = []
    ids = set()
    quotas = []

    def add(rows, budget):
        start = len(canonical(chosen).encode("utf-8"))
        count = 0
        for row in rows:
            if row["id"] in ids:
                continue
            size = len(canonical(chosen + [row]).encode("utf-8"))
            if size <= max_bytes and size - start <= budget:
                chosen.append(row)
                ids.add(row["id"])
                count += 1
        return count

    # Keep the latest-state witnesses, then reserve independent space for
    # history/earliest searches before filling from the original ranking.
    add(base["items"][:4], max_bytes // 6)
    quota = max_bytes // (len(pools) + 1)
    for pool in pools:
        quotas.append(add(pool["items"], quota))
    add(base["items"], max_bytes)
    entry.update(status="RETRIEVED", searches=queries, selected_per_search=quotas)
    return dict(
        base,
        items=chosen,
        selected_ids=[r["id"] for r in chosen],
        omitted_ids=sorted(set(memory["items"]) - ids),
        bytes=len(canonical(chosen).encode("utf-8")),
        lookup_searches=queries,
        action_search_ids=list(
            dict.fromkeys(
                i
                for query, pool in zip(queries, pools, strict=False)
                if query["focus"] == "action_history"
                for i in pool["selected_ids"]
            )
        ),
        retrieval="bounded independent search intents plus latest-state witnesses",
    )


def source_windows(memory, selection, bindings, *, max_bytes=24000):
    """Supply narrative context around action matches, using stored quotes only.

    A later reprimand may contain the action's name while the action itself is
    described indirectly several paragraphs earlier. Ranked isolated hits are
    insufficient evidence for occurrence/negation questions.
    """
    chapters = {}
    for mid in selection.get("action_search_ids", []):
        for s in memory["items"][mid].get("sources", []):
            chapters.setdefault(s["chapter_number"], set()).add(s["evidence_id"])
    ranked = sorted(chapters, key=lambda n: (-len(chapters[n]), -n))[:3]
    catalog = {}
    for mid, row in memory["items"].items():
        if row["kind"] != "prose_excerpt":
            continue
        for s in row.get("sources", []):
            if s["chapter_number"] in ranked:
                catalog.setdefault(
                    (s["chapter_number"], s["evidence_id"]), (mid, row, s)
                )
    windows = []
    alias_number = 0
    for chapter in ranked:
        window = {
            "chapter_number": chapter,
            "paragraphs": [],
            "scope": "Stored source context; distinguish narration, speech, guesses and plans",
        }
        for (number, eid), (mid, row, source) in sorted(catalog.items()):
            if number != chapter:
                continue
            alias = "s" + str(alias_number + 1).zfill(3)
            paragraph = {
                "memory_id": alias,
                "evidence_id": eid,
                "quote": source["quote"],
            }
            candidate = windows + [
                dict(window, paragraphs=window["paragraphs"] + [paragraph])
            ]
            if len(canonical(candidate).encode("utf-8")) > max_bytes:
                continue
            window["paragraphs"].append(paragraph)
            alias_number += 1
            bindings[alias] = {"memory_id": mid, "view": "source", "tier": row["tier"]}
        if window["paragraphs"]:
            windows.append(window)
    return windows


def literal_score(row, item, query):
    """Search the evidence text, not repeated labels or reading instructions."""
    runs = re.findall(r"[\u3400-\u9fff]+|[a-z0-9_]+", query.lower())
    pairs = {r[i : i + 2] for r in runs for i in range(len(r) - 1)}
    triples = {r[i : i + 3] for r in runs for i in range(len(r) - 2)}
    literal = " ".join(
        [row["subject"], row["claim"]] + [s["quote"] for s in item.get("sources", [])]
    ).lower()
    return sum(p in literal for p in pairs) + 3 * sum(t in literal for t in triples)
