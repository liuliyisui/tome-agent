"""UI services backed by INF's planner/writer/memory/reviewer transaction."""
import json
import os
import re
import tempfile
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from inf_writer.agents import build_agents
from inf_writer.chat_provider import ChatCompletionProvider
from inf_writer.domain import Snapshot, canonical, project_id, strict_json
from inf_writer.models import Budget, ModelGateway
from inf_writer.runtime import Coordinator
from inf_writer.storage import FileStore
from memory_runtime.writing import WritingSession, load_resume

from .settings import BACKEND_ROOT, Settings

DATA = BACKEND_ROOT / "data"
BOOKS = DATA / "inf_books"


def count_units(value):
    return len(re.findall(r"[\u3400-\u9fff]", value)) + len(re.findall(r"[A-Za-z0-9]+", value))


def new_book_id():
    return "book-" + uuid4().hex


def book_path(book_id):
    project_id(book_id)
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


@contextmanager
def operation_lock(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    lock = folder / "operation.lock"
    try:
        handle = lock.open("x", encoding="utf-8")
    except FileExistsError:
        raise ValueError("此作品有操作正在进行；确认没有运行任务后才能清理 operation.lock") from None
    try:
        with handle:
            handle.write(str(os.getpid()))
        yield
    finally:
        lock.unlink(missing_ok=True)


def _metadata(book_id):
    path = book_path(book_id) / "metadata.json"
    data = strict_json(path.read_text(encoding="utf-8"))
    required = {"schema_version", "title", "prompt", "target_chapters", "target_units", "model"}
    if not isinstance(data, dict) or set(data) != required or data["schema_version"] != 1:
        raise ValueError("作品元数据格式不受支持")
    return data


def load_book(book_id):
    if (book_path(book_id) / "longform-current.json").exists():
        return load_longform(book_id)
    return {"metadata": _metadata(book_id), "state": FileStore(BOOKS).load(book_id)}


def create_book(book_id, title, prompt, chapters, target_units, settings=None):
    project_id(book_id)
    if not isinstance(title, str) or not title.strip() or not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("作品名称和故事构想不能为空")
    if type(chapters) is not int or not 1 <= chapters <= 100:
        raise ValueError("章节数必须在 1 到 100 之间")
    if type(target_units) is not int or not 500 <= target_units <= 200000:
        raise ValueError("目标篇幅必须在 500 到 200000 之间")
    folder = book_path(book_id)
    if folder.exists():
        raise ValueError("作品已存在")
    cfg = settings or Settings.load(require_key=False)
    state = Snapshot(book_id, prompt.strip(), [f"全书目标{chapters}章", f"目标篇幅约{target_units}字"])
    FileStore(BOOKS).initialize(state)
    metadata = {"schema_version": 1, "title": title.strip(), "prompt": prompt.strip(),
                "target_chapters": chapters, "target_units": target_units, "model": cfg.public_config()}
    _atomic_json(folder / "metadata.json", metadata)
    return load_book(book_id)


def _gateway(settings):
    provider = ChatCompletionProvider(
        endpoint=settings.endpoint, model=settings.model, api_key=settings.api_key,
        input_usd_per_million=settings.input_usd_per_million,
        output_usd_per_million=settings.output_usd_per_million,
        allow_remote=True, timeout_seconds=settings.timeout,
        thinking_enabled=settings.thinking,
    )
    budget = Budget(max_calls=settings.max_calls, max_cost_usd=settings.max_cost_usd,
                    max_seconds=max(120.0, settings.timeout * settings.max_calls))
    return ModelGateway(provider, budget, reserve_per_call=0.0), budget


def generate_legacy(book_id, count=1, gateway=None, budget=None, settings=None):
    current = load_book(book_id)
    meta, state = current["metadata"], current["state"]
    remaining = meta["target_chapters"] - len(state.chapters)
    if type(count) is not int or not 1 <= count <= remaining:
        raise ValueError("本次章节数超出剩余范围")
    cfg = settings or Settings.load()
    if cfg.public_config() != meta["model"]:
        raise ValueError("当前模型配置与创建作品时不一致")
    if gateway is None:
        gateway, budget = _gateway(cfg)
    coordinator = Coordinator(FileStore(BOOKS), build_agents(gateway))
    with operation_lock(book_path(book_id)):
        for _ in range(count):
            state = FileStore(BOOKS).load(book_id)
            number = len(state.chapters) + 1
            target = max(300, (meta["target_units"] - sum(count_units(c["text"]) for c in state.chapters))
                         // max(1, meta["target_chapters"] - len(state.chapters)))
            instruction = (f"作品《{meta['title']}》，全书共{meta['target_chapters']}章。"
                           f"现在创作第{number}章，正文目标约{target}个中文字；保持前文连续并推进核心冲突。")
            outcome = coordinator.write_next(book_id, f"chapter-{number}-{uuid4().hex}", instruction)
            if outcome.status not in ("COMMITTED", "ALREADY_COMMITTED"):
                detail = json.dumps(outcome.issues, ensure_ascii=False) if outcome.issues else outcome.error or outcome.status
                raise RuntimeError(f"第{number}章未通过 INF 审核：{detail}")
    if budget is not None:
        _atomic_json(book_path(book_id) / "last-usage.json", {
            "calls": budget.calls, "input_tokens": budget.input_tokens,
            "output_tokens": budget.output_tokens, "estimated_cost_upper_usd": budget.cost_upper_usd,
        })
    return load_book(book_id)


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


def _load_longform_book(book_id, plan):
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
    return load_resume(checkpoint, plan)


def generate_longform(book_id, count=1, gateway=None, budget=None, settings=None):
    """Generate chapters with the event-first, three-tier-memory runtime.

    This is the backend integration point for the future frontend.  Each call
    writes a new checkpoint directory so an interrupted run never overwrites
    the last recoverable state.
    """
    meta = _metadata(book_id)
    plan = _longform_plan(meta)
    previous = _load_longform_book(book_id, plan)
    written = len(previous["chapters"]) if previous else 0
    remaining = meta["target_chapters"] - written
    if type(count) is not int or not 1 <= count <= remaining:
        raise ValueError("本次章节数超出剩余范围")
    cfg = settings or Settings.load()
    if cfg.public_config() != meta["model"]:
        raise ValueError("当前模型配置与创建作品时不一致")
    if gateway is None:
        gateway, budget = _gateway(cfg)
    run = book_path(book_id) / "longform-runs" / ("run-" + uuid4().hex)
    session = WritingSession(run, gateway, plan, book=previous)
    failure = None
    for _ in range(count):
        number = len(session.book["chapters"]) + 1
        used = sum(count_units(chapter["text"]) for chapter in session.book["chapters"])
        slots = max(1, meta["target_chapters"] - number + 1)
        target = max(300, (meta["target_units"] - used + slots - 1) // slots)
        session.chapter_length_target = target
        instruction = (
            f"作品《{meta['title']}》，现在创作第{number}章；本章约{target}字。"
            "先规划可验证的场景事件，再写完整正文；保持人物、时间、物品和因果连续。"
        )
        outcome = session.write_next(instruction)
        if outcome["status"] == "NO_DRAFT":
            failure = outcome
            break
    checkpoint = session.latest_checkpoint.resolve()
    relative = checkpoint.relative_to(book_path(book_id).resolve()).as_posix()
    _atomic_json(_longform_pointer(book_id), {"checkpoint": relative})
    if budget is not None:
        _atomic_json(book_path(book_id) / "last-usage.json", {
            "calls": budget.calls, "input_tokens": budget.input_tokens,
            "output_tokens": budget.output_tokens, "estimated_cost_upper_usd": budget.cost_upper_usd,
        })
    if failure is not None:
        detail = json.dumps(failure.get("errors", []), ensure_ascii=False)
        raise RuntimeError(f"第{failure['chapter_number']}章未生成正文：{detail}")
    return {"metadata": meta, "state": session.book}


def load_longform(book_id):
    meta = _metadata(book_id)
    state = _load_longform_book(book_id, _longform_plan(meta))
    return {"metadata": meta, "state": state}


# 默认生成入口直接使用经过五万字实测的长文本流程。
generate = generate_longform


def export_markdown(book):
    meta, state = book["metadata"], book["state"]
    chapters = state["chapters"] if isinstance(state, dict) else state.chapters
    return f"# {meta['title']}\n\n" + "\n\n".join(
        f"## 第{chapter['number']}章 {chapter['title']}\n\n{chapter['text']}" for chapter in chapters)


def list_books():
    return sorted(p.parent.name for p in BOOKS.glob("*/metadata.json")) if BOOKS.exists() else []


def book_labels(book_ids):
    titles = {}
    for book_id in book_ids:
        try:
            titles[book_id] = _metadata(book_id)["title"]
        except Exception:
            titles[book_id] = f"无法读取的作品（{book_id}）"
    counts = Counter(titles.values())
    return {key: f"{title}（{key}）" if counts[title] > 1 else title for key, title in titles.items()}
