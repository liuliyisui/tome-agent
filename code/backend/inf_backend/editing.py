"""Local manuscript edits committed as validated prose-grounded checkpoints."""

from uuid import uuid4

from memory_runtime.event_first import project_memory
from memory_runtime.narrative_planning import publish
from memory_runtime.writing import WritingSession
from tome_writer.domain import canonical, digest

from . import database, proofreading, service


def chapters_of(book):
    state = book["state"]
    return state["chapters"] if isinstance(state, dict) else state.chapters


def validate_draft(number, data, chapters):
    if type(number) is not int or not 1 <= number <= len(chapters):
        raise ValueError("章节号超出范围")
    title, text = data.get("title"), data.get("text")
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 100:
        raise ValueError("章节标题须为 1 到 100 个字符")
    if not isinstance(text, str) or not text.strip() or len(text) > 200000:
        raise ValueError("正文不能为空，每章最多 200000 个字符")
    if any(0xD800 <= ord(c) <= 0xDFFF or c == "\x00" for c in title + text):
        raise ValueError("正文包含无法保存的字符")
    return {"number": number, "title": title.strip(), "text": text}


def review_draft(book_id, number, data):
    book = service.load_book(book_id)
    draft = validate_draft(number, data, chapters_of(book))
    return proofreading.inspect([draft])


def review_book(book_id):
    return proofreading.inspect(chapters_of(service.load_book(book_id)))


def require_review(report, data):
    if report["revision"] != data.get("review_revision"):
        raise ValueError("内容已改变，请重新进行本地复查")
    if report["blocked"]:
        raise ValueError("发现疑似密钥或私钥，请移除后重新复查")
    if report["total"] and data.get("acknowledged") is not True:
        raise ValueError("请先核实复查提示，再勾选确认")


def _source_chapter(old, title, text, state, edited):
    state_hash = digest(canonical(state))
    body = {
        "version": 1,
        "chapter": old["number"],
        "base_state_sha256": state_hash,
        "state_sha256": state_hash,
        "proposal_sha256": digest(
            canonical({"title": title, "text_sha256": digest(text)})
        ),
        "scenes": [],
        "computed_times": [],
        "memory_projection": [],
        "identifier_normalizations": [],
        "stage_transactions": [],
        "stage_reports": [],
        "event_plan_status": "unavailable",
    }
    commit = {**body, "sha256": digest(canonical(body))}
    return {
        "number": old["number"],
        "title": title,
        "text": text,
        "sha256": digest(text),
        "event_commit": commit,
        "realization_template": text,
        "prose_encoding": "literal",
        "prose_policy": "unchecked",
        "quantity_sources": [],
        "time_calculations": [],
        "event_plan_status": "unavailable",
        "author_edited": edited,
        "source_policy": "AUTHOR_TEXT_REPLACES_PRIOR_EVENT_PLAN",
    }


def rebuild_session(book_id, plan, chapters, replacement=None):
    run = service.book_path(book_id) / "longform-runs" / ("run-manual-" + uuid4().hex)
    session = WritingSession(run, object(), plan)
    for original in chapters:
        n = original["number"]
        edited = replacement is not None and n == replacement["number"]
        value = replacement if edited else original
        chapter = _source_chapter(
            original,
            value["title"],
            value["text"],
            session.book["writing_state"],
            edited or original.get("author_edited", False),
        )
        session.book["chapters"].append(chapter)
        session.book["plan"][str(n)] = {
            "number": n,
            "title": chapter["title"],
            "brief": "以作者保存的正文为依据。",
        }
        publish(session.book, chapter, {})
        session.book["memory"] = project_memory(
            session.book["memory"], session.book["chapters"], n, []
        )
        session.book["outcomes"].append(
            {
                "chapter_number": n,
                "status": "DRAFT_UNCHECKED",
                "memory_update_status": "APPLIED",
                "memory_promoted": True,
                "story_review_status": "DISABLED",
                "issues": [],
                "suggestions": [],
                "stop_reason": None,
            }
        )
    # Persist the empty base and final snapshot only, avoiding one growing copy
    # of the whole manuscript per chapter on every small local edit.
    session._save([], "MEMORY_COMMITTED")
    service._load_compatible_checkpoint(session.latest_checkpoint, plan)
    return session


def save_chapter(book_id, number, data):
    with service.operation_lock(service.book_path(book_id)):
        current = service.load_book(book_id)
        old_chapters = chapters_of(current)
        draft = validate_draft(number, data, old_chapters)
        if data.get("base_revision") != proofreading.revision(old_chapters):
            raise ValueError("作品已更新，请刷新后重新对照修改；当前草稿仍可复制保留")
        report = proofreading.inspect([draft])
        require_review(report, data)
        old = old_chapters[number - 1]
        if old["title"] == draft["title"] and old["text"] == draft["text"]:
            return {"saved": True, "changed": False, "review": report}
        plan = service._longform_plan(current["metadata"])
        # A revised event can invalidate facts established before it (for
        # example an earlier owner or a character's alive status). Rebuild the
        # source view for the whole book, rather than keep those stale values
        # as current canonical state. Original checkpoints remain untouched.
        session = rebuild_session(book_id, plan, old_chapters, draft)
        run = session.output
        old_pointer = (
            database.row(book_id).get("checkpoint")
            if database.enabled()
            else service.strict_json(
                service._longform_pointer(book_id).read_text(encoding="utf-8")
            )["checkpoint"]
            if service._longform_pointer(book_id).exists()
            else None
        )
        service._atomic_json(
            run / "manual-edit.json",
            {
                "chapter": number,
                "previous_checkpoint": old_pointer,
                "previous_revision": data["base_revision"],
                "review": report,
                "source": "local-author-edit",
            },
        )
        service._save_generation_checkpoint(book_id, session, len(old_chapters), None)
        service._save_writing_note(
            book_id,
            session.book,
            number,
            {
                "model": "",
                "style_instructions": "",
                "reference_used": False,
                "skills": [],
                "author_feedback": "作者在本地工作台手动修改。",
            },
            old,
        )
        return {
            "saved": True,
            "changed": True,
            "review": report,
            "memory_synced_through": len(old_chapters),
        }


def reviewed_export(book_id, data):
    book = service.load_book(book_id)
    report = proofreading.inspect(chapters_of(book))
    require_review(report, data)
    return service.export_markdown(book)
