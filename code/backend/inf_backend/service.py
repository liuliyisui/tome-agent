"""UI services backed by INF's planner/writer/memory/reviewer transaction."""

import base64
import binascii
import json
import os
import re
import tempfile
import time
from collections import Counter
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from memory_runtime.writing import WritingSession, load_resume
from tome_writer.chat_provider import ChatCompletionProvider
from tome_writer.domain import (
    ContractError,
    Snapshot,
    canonical,
    digest,
    project_id,
    sanitize_title,
    strict_json,
)
from tome_writer.models import Budget, ModelGateway
from tome_writer.storage import FileStore

from . import database
from .settings import BACKEND_ROOT, Settings

DATA = BACKEND_ROOT / "data"
BOOKS = DATA / "inf_books"


def count_units(value):
    return len(re.findall(r"[\u3400-\u9fff]", value)) + len(
        re.findall(r"[A-Za-z0-9]+", value)
    )


def new_book_id():
    return "book-" + uuid4().hex


def book_path(book_id):
    project_id(book_id)
    if database.enabled():
        key = database.storage_key(book_id)
        if key != book_id and not re.fullmatch(r"\.trash/[a-f0-9]{32}", key):
            raise ValueError("检查点目录不安全")
        folder = BOOKS / key
        if not folder.resolve().is_relative_to(BOOKS.resolve()) or folder.is_symlink():
            raise ValueError("检查点目录不安全")
        return folder
    return BOOKS / book_id


def _atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".inf-meta-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(canonical(value) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _process_alive(pid):
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.OpenProcess.restype = ctypes.c_void_p
        kernel32.OpenProcess.argtypes = (ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong)
        kernel32.CloseHandle.argtypes = (ctypes.c_void_p,)
        # Never use os.kill on Windows: any signal other than Ctrl-C terminates.
        handle = kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            return (
                bool(kernel32.GetExitCodeProcess(handle, ctypes.byref(code)))
                and code.value == 259
            )
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _stale_lock(lock):
    """A lock left by a killed process is recoverable; a live owner is not."""
    try:
        raw = lock.read_text(encoding="utf-8").strip()
    except OSError:
        return False
    try:
        pid = int(raw)
    except ValueError:
        pid = None
    if pid is not None:
        return not _process_alive(pid)
    try:
        return time.time() - lock.stat().st_mtime > 60
    except OSError:
        return False


@contextmanager
def operation_lock(folder):
    folder = Path(folder)
    if database.enabled():
        with database.lock("tome:" + str(folder.resolve())):
            yield
        return
    folder.mkdir(parents=True, exist_ok=True)
    lock = folder / "operation.lock"
    try:
        handle = lock.open("x", encoding="utf-8")
    except FileExistsError:
        if not _stale_lock(lock):
            raise ValueError(
                "此作品有操作正在进行；确认没有运行任务后才能清理 operation.lock"
            ) from None
        lock.unlink(missing_ok=True)
        try:
            handle = lock.open("x", encoding="utf-8")
        except FileExistsError:
            raise ValueError(
                "此作品有操作正在进行；确认没有运行任务后才能清理 operation.lock"
            ) from None
    try:
        with handle:
            handle.write(str(os.getpid()))
        yield
    finally:
        lock.unlink(missing_ok=True)


def _metadata(book_id):
    project_id(book_id)
    if database.enabled():
        return database.row(book_id)["metadata"]
    path = book_path(book_id) / "metadata.json"
    data = strict_json(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "title",
        "prompt",
        "target_chapters",
        "target_units",
        "model",
    }
    if (
        not isinstance(data, dict)
        or set(data) != required
        or data["schema_version"] != 1
    ):
        raise ValueError("作品元数据格式不受支持")
    return data


def load_book(book_id):
    if database.enabled():
        project_id(book_id)
        record = database.row(book_id)
        state = (
            record["state"]
            if record["state_kind"] == "longform"
            else Snapshot.from_dict(record["state"])
        )
        return {"metadata": record["metadata"], "state": state}
    if (book_path(book_id) / "longform-current.json").exists():
        return load_longform(book_id)
    return {"metadata": _metadata(book_id), "state": FileStore(BOOKS).load(book_id)}


def cover_path(book_id):
    _metadata(book_id)
    folder = book_path(book_id)
    if folder.is_symlink() or getattr(folder, "is_junction", lambda: False)():
        raise ValueError("作品目录不安全")
    if folder.exists() and not folder.is_dir():
        raise ValueError("作品目录不可用")
    if not folder.exists() and not database.enabled():
        raise FileNotFoundError("作品目录不存在")
    path = folder / "cover.image"
    if path.is_symlink():
        raise ValueError("封面路径不安全")
    return path


def cover_type(data):
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    raise ValueError("请选择 PNG、JPEG 或 WebP 图片")


def cover_version(book_id):
    path = cover_path(book_id)
    return path.stat().st_mtime_ns if path.is_file() else None


def save_cover(book_id, value):
    if not isinstance(value, str) or len(value) > 2_800_000:
        raise ValueError("封面图片不能超过 2 MB")
    try:
        data = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error):
        raise ValueError("封面图片格式无效") from None
    if not data or len(data) > 2 * 1024 * 1024:
        raise ValueError("封面图片不能超过 2 MB")
    cover_type(data)
    with operation_lock(BOOKS):
        path = cover_path(book_id)
        if database.enabled():
            path.parent.mkdir(parents=True, exist_ok=True)
            path = cover_path(book_id)
        fd, temporary = tempfile.mkstemp(prefix=".cover-", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as output:
                output.write(data)
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return cover_version(book_id)


def validate_writing_style(value):
    if not isinstance(value, dict) or set(value) != {"instructions", "reference"}:
        raise ValueError("文风设定须包含文风要求和参考片段")
    result = {}
    for key, limit in (("instructions", 2000), ("reference", 6000)):
        if not isinstance(value[key], str) or len(value[key]) > limit:
            raise ValueError(
                f"{'文风要求' if key == 'instructions' else '参考片段'}须为不超过{limit}字的文本"
            )
        result[key] = value[key].strip()
    return result


def load_writing_style(book_id):
    if database.enabled():
        return validate_writing_style(database.style(book_id))
    path = book_path(book_id) / "writing-style.json"
    if not path.exists():
        return {"instructions": "", "reference": ""}
    return validate_writing_style(strict_json(path.read_text(encoding="utf-8")))


def save_writing_style(book_id, value):
    _metadata(book_id)
    style = validate_writing_style(value)
    with operation_lock(book_path(book_id)):
        if database.enabled():
            return database.style(book_id, style)
        _atomic_json(book_path(book_id) / "writing-style.json", style)
    return style


class StyleGateway:
    """Apply the saved prose style to every writer call, including length edits.

    Keep style outside the frozen writing plan so editing it does not invalidate
    existing checkpoint plan hashes. Planner/memory requests remain untouched.
    """

    def __init__(self, gateway, style):
        self.gateway = gateway
        self.style = validate_writing_style(style)

    def complete(self, request):
        if request.role == "writer" and any(self.style.values()):
            request = replace(
                request,
                system=request.system
                + "\n正文写法遵循 writing_style 中的文风要求。参考片段仅用于学习叙述节奏、句式、对白和描写方式；不将其中的人物、事件或事实写入本故事，不续写或照抄参考片段。保持原有输出格式和故事事实约束。",
                payload={**request.payload, "writing_style": dict(self.style)},
            )
        return self.gateway.complete(request)


def list_skills():
    path = DATA / "skills.json"
    return strict_json(path.read_text(encoding="utf-8")) if path.exists() else []


def install_skill(name, content):
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
        raise ValueError("技能名称须为 1 到 80 个字符")
    if not isinstance(content, str) or not 1 <= len(content.strip()) <= 12000:
        raise ValueError("技能内容须为 1 到 12000 个字符")
    item = {"id": uuid4().hex, "name": name.strip(), "content": content.strip()}
    with operation_lock(DATA):
        skills = list_skills()
        if len(skills) >= 100:
            raise ValueError("技能数量已达到上限")
        _atomic_json(DATA / "skills.json", [*skills, item])
    return item


def load_book_skills(book_id):
    _metadata(book_id)
    path = book_path(book_id) / "skills.json"
    return strict_json(path.read_text(encoding="utf-8")) if path.exists() else []


def validate_skill_selection(ids):
    if (
        not isinstance(ids, list)
        or len(ids) > 5
        or any(not isinstance(x, str) for x in ids)
        or len(set(ids)) != len(ids)
    ):
        raise ValueError("最多选择 5 个不同技能")
    available = {item["id"] for item in list_skills()}
    if any(x not in available for x in ids):
        raise ValueError("所选技能不存在")
    return ids


def save_book_skills(book_id, ids):
    _metadata(book_id)
    validate_skill_selection(ids)
    with operation_lock(book_path(book_id)):
        _atomic_json(book_path(book_id) / "skills.json", ids)
    return ids


class SkillGateway:
    def __init__(self, gateway, skills):
        self.gateway = gateway
        self.skills = skills

    def complete(self, request):
        if request.role == "writer" and self.skills:
            request = replace(
                request,
                system=request.system
                + "\n参考 writing_skills 中的写作要求，遵守原有输出格式和故事事实约束。",
                payload={**request.payload, "writing_skills": self.skills},
            )
        return self.gateway.complete(request)


def create_book(
    book_id,
    title,
    prompt,
    chapters,
    target_units,
    settings=None,
    style=None,
    skills=None,
):
    project_id(book_id)
    if (
        not isinstance(title, str)
        or not title.strip()
        or not isinstance(prompt, str)
        or not prompt.strip()
    ):
        raise ValueError("作品名称和故事构想不能为空")
    if type(chapters) is not int or not 1 <= chapters <= 100:
        raise ValueError("章节数必须在 1 到 100 之间")
    if type(target_units) is not int or not 500 <= target_units <= 200000:
        raise ValueError("目标篇幅必须在 500 到 200000 之间")
    style = (
        validate_writing_style(style)
        if style is not None
        else {"instructions": "", "reference": ""}
    )
    selected_skills = validate_skill_selection(skills) if skills is not None else []
    folder = book_path(book_id)
    if folder.exists():
        raise ValueError("作品已存在")
    cfg = settings or Settings.load(require_key=False)
    state = Snapshot(
        book_id,
        prompt.strip(),
        [f"全书目标{chapters}章", f"目标篇幅约{target_units}字"],
    )
    metadata = {
        "schema_version": 1,
        "title": title.strip(),
        "prompt": prompt.strip(),
        "target_chapters": chapters,
        "target_units": target_units,
        "model": cfg.public_config(),
    }
    if database.enabled():
        database.create(book_id, metadata, state.to_dict(), style)
        if selected_skills:
            save_book_skills(book_id, selected_skills)
        return load_book(book_id)
    FileStore(BOOKS).initialize(state)
    _atomic_json(folder / "metadata.json", metadata)
    if any(style.values()):
        _atomic_json(folder / "writing-style.json", style)
    if selected_skills:
        save_book_skills(book_id, selected_skills)
    return load_book(book_id)


def _gateway(settings):
    provider = ChatCompletionProvider(
        endpoint=settings.endpoint,
        model=settings.model,
        api_key=settings.api_key,
        input_usd_per_million=settings.input_usd_per_million,
        output_usd_per_million=settings.output_usd_per_million,
        allow_remote=True,
        timeout_seconds=settings.timeout,
        thinking_enabled=settings.thinking,
        token_limit_field="max_completion_tokens"
        if settings.provider == "openai"
        else "max_tokens",
    )
    budget = Budget(
        max_calls=settings.max_calls,
        max_cost_usd=settings.max_cost_usd,
        max_seconds=max(120.0, settings.timeout * settings.max_calls),
    )
    reservation = (
        1_048_576 * settings.input_usd_per_million
        + 32768 * settings.output_usd_per_million
    ) / 1_000_000
    return ModelGateway(provider, budget, reserve_per_call=reservation), budget


def _longform_plan(meta):
    return {
        "title": meta["title"],
        "goal": meta["prompt"],
        "constraints": [
            f"全书目标{meta['target_chapters']}章",
            f"目标篇幅约{meta['target_units']}字",
            "保持人物、时间、物品和因果关系连续",
        ],
        "chapters": meta["target_chapters"],
        "max_chapters": meta["target_chapters"],
        "target_han_chars": meta["target_units"],
        "event_first": True,
        "story_review_enabled": False,
    }


def _longform_pointer(book_id):
    return book_path(book_id) / "longform-current.json"


def _heal_chapter_titles(book):
    """Normalize titles saved before instruction-echo sanitization existed.

    Chapter and plan titles carry no integrity digest, so they can be
    rewritten safely; prepared (not yet written) event proposals are left
    untouched because their digests are already committed.
    """
    for chapter in book.get("chapters", []):
        chapter["title"] = sanitize_title(chapter["title"], chapter.get("number"))
    for entry in book.get("plan", {}).values():
        entry["title"] = sanitize_title(entry["title"], entry.get("number"))
    return book


def _load_longform_book(book_id, plan):
    if database.enabled():
        record = database.row(book_id)
        if record["state_kind"] != "longform":
            if record["state"].get("chapters"):
                raise ValueError("旧版章节存档仅供阅读和导出，请新建作品")
            return None
        relative = record["checkpoint"]
        if not relative:
            raise ValueError("长文本存档缺少恢复检查点")
        checkpoint = (book_path(book_id) / relative).resolve()
        if not checkpoint.is_relative_to(book_path(book_id).resolve()):
            raise ValueError("检查点路径不安全")
        return load_resume(checkpoint, plan)
    pointer = _longform_pointer(book_id)
    if not pointer.exists():
        return None
    record = strict_json(pointer.read_text(encoding="utf-8-sig"))
    if not isinstance(record, dict) or set(record) != {"checkpoint"}:
        raise ValueError("长文本检查点索引格式不正确")
    checkpoint = (book_path(book_id) / record["checkpoint"]).resolve()
    root = book_path(book_id).resolve()
    if checkpoint == root or not checkpoint.is_relative_to(root):
        raise ValueError("长文本检查点路径不安全")
    return _heal_chapter_titles(load_resume(checkpoint, plan))


def _checkpoint_paths(book_id):
    runs = book_path(book_id) / "longform-runs"
    if not runs.exists():
        return []
    return sorted(
        runs.glob("run-*/checkpoint_*.json"),
        key=lambda path: (path.stat().st_mtime, path.name),
    )


def validate_author_feedback(value):
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= 2000:
        raise ValueError("请填写 1 到 2000 字的作者意见")
    return value.strip()


def regeneration_scope(chapters, number, confirmed):
    current = len(chapters)
    if type(number) is not int or not 1 <= number <= current:
        raise ValueError("章节号超出范围")
    dropped = current - number + 1
    if confirmed is not True:
        raise ValueError(f"重新生成第{number}章会替换该章及之后共{dropped}章，请先确认")
    return {"number": number, "chapters": current, "dropped": dropped}


def _regeneration_boundary(book_id, plan, prefix):
    def chapter_hashes(chapters):
        return [
            (chapter["sha256"], chapter.get("event_commit", {}).get("sha256"))
            for chapter in chapters
        ]

    expected = chapter_hashes(prefix)
    reasons = (
        ("MEMORY_COMMITTED", "DRAFT_SAVED_MEMORY_PENDING")
        if prefix
        else ("EMPTY_START",)
    )
    root = book_path(book_id).resolve()
    for path in reversed(_checkpoint_paths(book_id)):
        try:
            if not path.resolve().is_relative_to(root):
                continue
            record = strict_json(path.read_text(encoding="utf-8-sig"))
            if record["reason"] not in reasons:
                continue
            saved = record["book"]["chapters"]
            if chapter_hashes(saved) == expected:
                return load_resume(path, plan)
        except (KeyError, TypeError, ValueError, OSError, ContractError):
            continue
    raise ValueError("找不到与本作品前文章节一致的可恢复检查点")


class RegenerationGateway:
    """Apply one chapter's revision to planning and every prose pass."""

    def __init__(self, gateway, feedback, chapter):
        self.gateway = gateway
        draft = chapter["text"]
        self.revision = {
            "author_feedback": feedback,
            "previous_title": chapter["title"],
            "previous_draft": draft
            if len(draft) <= 8000
            else (draft[:4000] + "\n[原稿中段省略]\n" + draft[-4000:]),
        }

    def complete(self, request):
        if request.role in ("planner", "writer"):
            request = replace(
                request,
                system=request.system
                + "\n按 chapter_revision.author_feedback 修改当前章节。原稿仅供对照，未重写的前文章节是连续性依据。"
                "在遵守已确定的事实、事件和输出格式的前提下，作者本次意见优先于常驻文风和技能。",
                payload={**request.payload, "chapter_revision": self.revision},
            )
        return self.gateway.complete(request)


def generate_longform(
    book_id,
    count=1,
    gateway=None,
    budget=None,
    settings=None,
    progress=None,
    *,
    regenerate_number=None,
    confirmed=False,
    author_feedback="",
):
    """Generate chapters with the event-first, three-tier-memory runtime.

    This is the backend integration point for the future frontend.  Each call
    writes a new checkpoint directory so an interrupted run never overwrites
    the last recoverable state.
    """
    meta = _metadata(book_id)
    plan = _longform_plan(meta)
    previous = _load_longform_book(book_id, plan)
    original_chapter = None
    if regenerate_number is not None:
        author_feedback = validate_author_feedback(author_feedback)
        chapters = previous["chapters"] if previous else []
        regeneration_scope(chapters, regenerate_number, confirmed)
        if count != 1:
            raise ValueError("每次只能重新生成一章")
        original_chapter = chapters[regenerate_number - 1]
        previous = _regeneration_boundary(
            book_id, plan, chapters[: regenerate_number - 1]
        )
    written = len(previous["chapters"]) if previous else 0
    remaining = meta["target_chapters"] - written
    if type(count) is not int or not 1 <= count <= remaining:
        raise ValueError("本次章节数超出剩余范围")
    cfg = settings or Settings.for_book(meta["model"])
    if cfg.public_config() != meta["model"]:
        raise ValueError("当前模型配置与创建作品时不一致")
    stream_provider = None
    if gateway is None:
        gateway, budget = _gateway(replace(cfg, max_calls=cfg.max_calls * count))
        if (
            progress
            and cfg.provider in ("deepseek", "openai")
            and isinstance(gateway, ModelGateway)
            and isinstance(gateway.provider, ChatCompletionProvider)
        ):
            from .streaming import ProseProgressProvider, describe_prose_request

            stream_provider = ProseProgressProvider(
                gateway.provider,
                progress,
                count_units,
                lambda request: describe_prose_request(
                    session.book, request, count_units
                ),
            )
            gateway.provider = stream_provider
    gateway = StyleGateway(gateway, load_writing_style(book_id))
    selected = set(load_book_skills(book_id))
    skills = [item for item in list_skills() if item["id"] in selected]
    if len(skills) != len(selected):
        raise ValueError("已选择的技能不存在，请重新选择")
    gateway = SkillGateway(gateway, skills)
    if original_chapter is not None:
        gateway = RegenerationGateway(gateway, author_feedback, original_chapter)
    run = book_path(book_id) / "longform-runs" / ("run-" + uuid4().hex)
    session = WritingSession(run, gateway, plan, book=previous)
    _atomic_json(
        run / "skills-used.json",
        [
            {"id": item["id"], "name": item["name"], "sha256": digest(item["content"])}
            for item in skills
        ],
    )
    failure = None
    for _ in range(count):
        if stream_provider:
            stream_provider.reset_chapter()
        number = len(session.book["chapters"]) + 1
        if progress:
            progress(
                {
                    "completed": len(session.book["chapters"]) - written,
                    "current_chapter": number,
                    "live_units": None,
                    "live_phase": "planning",
                }
            )
        used = sum(count_units(chapter["text"]) for chapter in session.book["chapters"])
        slots = max(1, meta["target_chapters"] - number + 1)
        target = max(300, (meta["target_units"] - used + slots - 1) // slots)
        session.chapter_length_target = target
        instruction = (
            f"作品《{meta['title']}》，现在创作第{number}章；本章约{target}字。"
            "先规划可验证的场景事件，再写完整正文；保持人物、时间、物品和因果连续。"
        )
        try:
            outcome = session.write_next(instruction)
        finally:
            if original_chapter is None or len(session.book["chapters"]) > written:
                _save_generation_checkpoint(book_id, session, written, budget)
        if progress:
            progress(
                {
                    "completed": len(session.book["chapters"]) - written,
                    "current_chapter": number,
                }
            )
        if outcome["status"] == "NO_DRAFT":
            failure = outcome
            break
    if failure is not None:
        detail = json.dumps(failure.get("errors", []), ensure_ascii=False)
        raise RuntimeError(f"第{failure['chapter_number']}章未生成正文：{detail}")
    return {"metadata": meta, "state": session.book}


def _save_generation_checkpoint(book_id, session, written, budget):
    checkpoint = session.latest_checkpoint.resolve()
    relative = checkpoint.relative_to(book_path(book_id).resolve()).as_posix()
    usage = (
        None
        if budget is None
        else {
            "calls": budget.calls,
            "input_tokens": budget.input_tokens,
            "output_tokens": budget.output_tokens,
            "estimated_cost_upper_usd": budget.cost_upper_usd,
            "chapters_completed": len(session.book["chapters"]) - written,
        }
    )
    _atomic_json(_longform_pointer(book_id), {"checkpoint": relative})
    if budget is not None:
        _atomic_json(
            book_path(book_id) / "last-usage.json",
            {
                "calls": budget.calls,
                "input_tokens": budget.input_tokens,
                "output_tokens": budget.output_tokens,
                "estimated_cost_upper_usd": budget.cost_upper_usd,
                "chapters_completed": len(session.book["chapters"]) - written,
            },
        )
    if database.enabled():
        database.save(book_id, session.book, "longform", relative, usage)


def load_longform(book_id):
    if database.enabled():
        return load_book(book_id)
    meta = _metadata(book_id)
    plan = _longform_plan(meta)
    try:
        state = _load_longform_book(book_id, plan)
    except ContractError as exc:
        if str(exc) != "写作运行时版本不一致，不能直接恢复旧检查点":
            raise
        pointer = strict_json(
            _longform_pointer(book_id).read_text(encoding="utf-8-sig")
        )
        if not isinstance(pointer, dict) or set(pointer) != {"checkpoint"}:
            raise ValueError("长文本检查点索引格式不正确") from exc
        root = book_path(book_id).resolve()
        checkpoint = (root / pointer["checkpoint"]).resolve()
        if checkpoint == root or not checkpoint.is_relative_to(root):
            raise ValueError("长文本检查点路径不安全") from exc
        record = strict_json(checkpoint.read_text(encoding="utf-8-sig"))
        state = record.get("book")
        if (
            record.get("schema") != "inf-writing-checkpoint-v1"
            or record.get("writing_plan_sha256") != digest(canonical(plan))
            or not isinstance(state, dict)
            or record.get("book_sha256") != digest(canonical(state))
            or not isinstance(state.get("chapters"), list)
        ):
            raise ValueError("旧版存档完整性校验失败") from exc
        return {"metadata": meta, "state": state, "read_only": True}
    return {"metadata": meta, "state": state}


# 默认生成入口直接使用经过五万字实测的长文本流程。
generate = generate_longform


def export_markdown(book):
    meta, state = book["metadata"], book["state"]
    chapters = state["chapters"] if isinstance(state, dict) else state.chapters
    sections = [f"# {meta['title']}"]
    for chapter in chapters:
        paragraphs = [
            line.strip() for line in chapter["text"].splitlines() if line.strip()
        ]
        # Full-width spaces keep a two-character indent in plain text and
        # Markdown without triggering Markdown's four-ASCII-space code blocks.
        prose = "\n\n".join("\u3000\u3000" + paragraph for paragraph in paragraphs)
        sections.append(f"## 第{chapter['number']}章 {chapter['title']}\n\n{prose}")
    return "\n\n".join(sections) + "\n"


def list_books():
    if database.enabled():
        return database.books()
    books = []
    for path in sorted(BOOKS.glob("*/metadata.json")):
        try:
            if _metadata(path.parent.name)["model"]["model"] == "offline-demo":
                continue
        except (OSError, ValueError, KeyError):
            pass
        books.append(path.parent.name)
    return books


def last_usage(book_id):
    if database.enabled():
        return database.row(book_id)["last_usage"]
    path = book_path(book_id) / "last-usage.json"
    return strict_json(path.read_text(encoding="utf-8")) if path.exists() else None


def book_labels(book_ids):
    titles = {}
    for book_id in book_ids:
        try:
            titles[book_id] = _metadata(book_id)["title"]
        except Exception:
            titles[book_id] = f"无法读取的作品（{book_id}）"
    counts = Counter(titles.values())
    return {
        key: f"{title}（{key}）" if counts[title] > 1 else title
        for key, title in titles.items()
    }
