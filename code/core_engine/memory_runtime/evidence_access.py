"""Bound source views for existing evidence profiles, not a new fact ledger."""

import copy

from inf_writer.domain import canonical, digest

OBSERVATION_POLICY_VERSION = "material_access_v1"


OBSERVATION_POLICY = (
    "先区分物件原件、派生材料和人物当前实际能接触的载体，再安排观察与推理。"
    "available_materials是规划描述，不自动认证取得或持有；source_passages是已保存原文，"
    "原文中的取得、退还、遗失及观察限制优先，后来的实际变化优先于旧描述。"
    "document_identity区分不同原始物件的用途与所记事件；不能因都叫复印件、摘录或清单就并成同一件。"
    "原件去向按已写的实际取得与转移记录，不能把拟清运、拟递交当作已完成；未知处保留未知。"
    "未登记载体不等于默认持有原件；先从原文确定，无法确定就保留未知并改变调查行动。"
    "每项观察要求的特征必须由当前载体保留：转述或手抄保留的是所述内容，"
    "手描只能留下描摹者的线条，不能据此鉴定原作者运笔、墨色、笔压、纸纹、涂改层次。"
    "照片可保留可见图像，但清晰度、色彩和拍摄范围有限，不能凭照片触摸厚度或恢复未摄区域；"
    "扫描、复印、录音、节录等也按具体制作方式区分保留与丢失的信息，不笼统视为原件。"
    "缺少观察条件时可追查原件、可靠影像、经手人或别的独立证据，"
    "也可让人物察觉推测不成立、改变行动或发生争执；不能临时补造已拍照、已取得原件。"
    "“像”“待核”“不能定论”只是结论强度，不能使不成立的观察变得成立。"
    "人物可以犯错或欺骗，但若作为剧情中的错误，应有视角和后果，不把错误观察当叙述者确认的发现。"
)


def _grams(value):
    text = "".join(c for c in value.casefold() if c.isalnum())
    return {text[i : i + 2] for i in range(max(0, len(text) - 1))}


def _rank_passages(chapters, numbers, query):
    ranked = []
    for n in numbers:
        c = chapters.get(n)
        if not c:
            continue
        offset = 0
        for paragraph in c["text"].split("\n\n"):
            score = len(query & _grams(paragraph))
            if score:
                ranked.append((n, score, offset, len(paragraph)))
            offset += len(paragraph) + 2
    return sorted(ranked, reverse=True)


def _source_passages(book, row):
    """One source endpoint plus a relevant distinct source window, verbatim."""
    chapters = {c["number"]: c for c in book.get("chapters", [])}
    number = row["last_planned_chapter"]
    chapter = chapters.get(number)
    result = []

    def add(c, start, end):
        if start >= end:
            return
        if any(
            r["chapter"] == c["number"] and start < r["end"] and end > r["start"]
            for r in result
        ):
            return
        result.append(
            {
                "chapter": c["number"],
                "chapter_sha256": digest(c["text"]),
                "start": start,
                "end": end,
                "quote": c["text"][start:end],
                "scope": "Literal prose; not certification of a character statement",
            }
        )

    if chapter:
        add(chapter, max(0, len(chapter["text"]) - 420), len(chapter["text"]))
    profile = row["latest_profile"]
    query = _grams(
        row["topic"] + " " + canonical(profile.get("available_materials", []))
    )
    numbers = set(sorted(chapters)[-2:] + [row["introduced_in_chapter"], number])
    for n, _, start, length in _rank_passages(chapters, numbers, query):
        before = len(result)
        c = chapters[n]
        left = max(0, start - 40)
        add(c, left, min(len(c["text"]), left + min(420, length + 80)))
        if len(result) > before:
            break
    return result


def context(book, limit=9000):
    """Derived request view; missing metadata and omitted profiles stay explicit."""
    rows = book.get("narrative_planning", {}).get("evidence_profiles", {})
    selected = []
    missing = 0
    base = {
        "policy": OBSERVATION_POLICY,
        "scope": "Read-only view of existing evidence profiles and saved prose, not new world facts",
    }
    for row in sorted(rows.values(), key=lambda r: -r["last_planned_chapter"]):
        profile = row["latest_profile"]
        materials = profile.get("available_materials", [])
        view = {
            "topic": row["topic"],
            "description_status": "DECLARED_IN_PLAN" if materials else "NOT_RECORDED",
            "document_identity": {
                k: profile[k]
                for k in ("document_role", "creation_context", "pertains_to")
                if k in profile
            },
            "available_materials": copy.deepcopy(materials),
            "source_passages": _source_passages(book, row),
        }
        if (
            len(
                canonical(
                    dict(
                        base,
                        evidence_materials=selected + [view],
                        omitted_profile_count=len(rows),
                    )
                ).encode("utf-8")
            )
            <= limit
        ):
            selected.append(view)
        else:
            missing += 1
    return dict(base, evidence_materials=selected, omitted_profile_count=missing)
