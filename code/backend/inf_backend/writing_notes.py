"""Reader-facing summaries from saved plans and verifiable revision records.

No additional model calls and no reconstruction of private model reasoning.
The optional context sidecar is matched to chapter content before display.
"""

import difflib
import re
from pathlib import Path

from tome_writer.domain import canonical, digest, strict_json

VERSION = 1


def excerpt(value, limit=360):
    if not isinstance(value, str):
        return ""
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit] + ("…" if len(value) > limit else "")


def fingerprint(chapter):
    return digest(canonical({key: chapter.get(key, "") for key in ("title", "text")}))


def paragraphs(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def compare(original, chapter):
    if original is None:
        return None
    before = paragraphs(original["text"])
    after = paragraphs(chapter["text"])
    counts = {"updated": 0, "added": 0, "removed": 0}
    examples = []
    for tag, a, b, c, d in difflib.SequenceMatcher(None, before, after).get_opcodes():
        if tag == "equal":
            continue
        common = min(b - a, d - c) if tag == "replace" else 0
        counts["updated"] += common
        counts["added"] += d - c - common
        counts["removed"] += b - a - common
        if len(examples) < 3:
            examples.append(
                {
                    "before": excerpt("\n".join(before[a:b]), 200),
                    "after": excerpt("\n".join(after[c:d]), 200),
                    "old_paragraph": a + 1 if b > a else None,
                    "new_paragraph": c + 1 if d > c else None,
                }
            )
    return {
        **counts,
        "examples": examples,
        "title_changed": original["title"] != chapter["title"],
        "previous_title": original["title"]
        if original["title"] != chapter["title"]
        else "",
        "text_changed": original["text"] != chapter["text"],
        "format_only": original["text"] != chapter["text"] and before == after,
    }


def capture(chapter, context, original=None):
    return {
        "fingerprint": fingerprint(chapter),
        "operation": "regenerate" if original is not None else "generate",
        "context": dict(context),
        "comparison": compare(original, chapter),
    }


def read(path):
    try:
        data = strict_json(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return (
        data.get("chapters", {})
        if isinstance(data, dict)
        and data.get("version") == VERSION
        and isinstance(data.get("chapters"), dict)
        else {}
    )


def update(stored, book, number, context, original=None):
    chapters = book["chapters"]
    result = {
        str(c["number"]): stored[str(c["number"])]
        for c in chapters
        if str(c["number"]) in stored
    }
    chapter = next(c for c in chapters if c["number"] == number)
    result[str(number)] = capture(chapter, context, original)
    return {"version": VERSION, "chapters": result}


def _length_changes(chapter):
    reports = [chapter.get("length_report", {})]
    reports.extend(
        item.get("length_report", {}) for item in chapter.get("event_stage_sources", [])
    )
    reports = [report for report in reports if isinstance(report, dict)]
    changes = []
    accepted = [r for r in reports if r.get("adjustment") == "accepted"]
    if accepted:
        changes.append(f"记录到 {len(accepted)} 次篇幅调整，修改稿已被采用。")
    kept = [
        r for r in reports if str(r.get("adjustment", "")).startswith("kept_original_")
    ]
    if kept:
        changes.append(f"另有 {len(kept)} 次篇幅调整未采用，保留对应原稿。")
    return changes


def summarize(chapter, state, stored=None):
    number = chapter["number"]
    stored = (
        stored
        if isinstance(stored, dict)
        and stored.get("fingerprint") == fingerprint(chapter)
        else {}
    )
    context = stored.get("context", {})
    context = context if isinstance(context, dict) else {}
    plan = state.get("plan", {}).get(str(number), {})
    outcome = next(
        (r for r in state.get("outcomes", []) if r.get("chapter_number") == number), {}
    )
    scenes = []
    for scene in chapter.get("event_commit", {}).get("scenes", [])[:6]:
        scenes.append(
            {
                "purpose": excerpt(scene.get("purpose")),
                "events": [
                    excerpt(beat.get("statement"), 180)
                    for beat in scene.get("beats", [])[:3]
                    if excerpt(beat.get("statement"))
                ],
            }
        )
    memory = {
        "APPLIED": "本章记忆更新已应用。",
        "PENDING": "本章记忆仍待更新。",
        "NOT_RUN": "本章尚无记忆更新记录。",
    }.get(outcome.get("memory_update_status"), "本章未保留明确的记忆更新状态。")
    review = {
        "DISABLED": "本次未启用独立正文审核，仍需作者检查。",
        "PENDING": "独立正文审核尚未完成。",
        "REPORTED": "已有独立审核记录，摘要不代表所有问题已解决。",
    }.get(outcome.get("story_review_status"), "没有可确认的独立正文审核结果。")
    return {
        "version": VERSION,
        "brief": excerpt(plan.get("brief"), 500),
        "scenes": scenes,
        "scenes_omitted": max(
            0, len(chapter.get("event_commit", {}).get("scenes", [])) - len(scenes)
        ),
        "operation": stored.get("operation"),
        "context": context,
        "comparison": stored.get("comparison"),
        "adjustments": _length_changes(chapter),
        "memory": memory,
        "review": review,
        "provenance": "依据已保存的章节规划与操作记录整理；写作要求是本次输入，具体落实情况请对照正文。"
        if stored
        else "历史章节未保留当次写作配置与修改对照，仅展示现存的规划和状态记录。",
    }


def for_book(book, stored):
    state = book["state"]
    state = state if isinstance(state, dict) else state.to_dict()
    return {
        str(chapter["number"]): summarize(
            chapter, state, stored.get(str(chapter["number"]))
        )
        for chapter in state["chapters"]
    }
