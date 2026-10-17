"""UI/CLI application services; no provider calls until explicitly requested."""
import json
import os
from collections import Counter
from uuid import uuid4
from contextlib import contextmanager
from pathlib import Path
from tome_agent.agent import ChapterAgent, Limits
from .checkpoints import load_checkpoint, save_checkpoint
from tome_agent.planning import OutlinePlanner
from .providers.deepseek import DeepSeekModel, Settings, PROJECT_ROOT
from tome_agent.runner import StoryRunner
from .storage import save_payload

BOOKS = PROJECT_ROOT / "data" / "books"


@contextmanager
def operation_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.parent / "operation.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ValueError("此作品有操作正在进行。如进程异常退出，请确认没有运行中的任务后删除operation.lock") from None
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(str(os.getpid()))
        yield
    finally:
        lock.unlink(missing_ok=True)


def book_path(book_id):
    import re
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", book_id):
        raise ValueError("作品ID只能包含英文字母、数字、下划线和短横线")
    return BOOKS / book_id / "book.json"


def new_model():
    return DeepSeekModel(Settings.load())


def record_usage(model, path):
    save_payload({"requests": model.requests, "total_tokens": model.total_tokens,
                  "calls": model.usage_log, "budget_scope": "this operation, not cumulative book billing"}, Path(path))


def create_book(book_id, title, prompt, chapters, target_units, model=None):
    path = book_path(book_id)
    if path.exists():
        raise ValueError("作品ID已存在，请选择新ID")
    if not title.strip() or not prompt.strip():
        raise ValueError("标题和故事构想不能为空")
    model = model or new_model()
    try:
        with operation_lock(path):
            if path.exists():
                raise ValueError("作品ID已存在")
            workspace = OutlinePlanner(model).generate(title, prompt, chapters, target_units,
                model.settings.public_config(), path.parent / "outline-cache.json")
            save_checkpoint(workspace, path)
            return workspace
    finally:
        record_usage(model, path.parent / "planning-usage.json")


def generate(book_id, count=1, resume=False, max_turns=30, model=None):
    path = book_path(book_id)
    workspace = load_checkpoint(path)
    model = model or new_model()
    if workspace.config != model.settings.public_config():
        raise ValueError("当前模型配置与作品创建时不一致，请恢复原配置后续写")
    try:
        with operation_lock(path):
            return StoryRunner(ChapterAgent(model, Limits(max_turns=max_turns))).run(
                workspace, path, chapter_limit=count, resume_attempt=resume)
    finally:
        record_usage(model, path.parent / "generation-usage.json")


def export_markdown(workspace):
    return f"# {workspace.title}\n\n" + "\n\n".join(
        f"## 第{n}章 {workspace.outline[n-1]['title']}\n\n{text}"
        for n, text in sorted(workspace.chapters.items()))


def update_outline(book_id, outline):
    with operation_lock(book_path(book_id)):
        workspace = load_checkpoint(book_path(book_id))
        if workspace.chapters or Path(str(book_path(book_id)) + ".attempt.json").exists():
            raise ValueError("已开始生成的作品不能直接改冻结大纲，请另建作品")
        workspace.outline = outline
        workspace.validate()
        save_checkpoint(workspace, book_path(book_id))
        return workspace


def list_books():
    return sorted(p.parent.name for p in BOOKS.glob("*/book.json")) if BOOKS.exists() else []


def new_book_id():
    """Storage identity is independent of the author's title."""
    return "book-" + uuid4().hex


def book_labels(book_ids):
    """Read titles without changing or migrating existing workspaces."""
    titles = {}
    for book_id in book_ids:
        try:
            data = json.loads(book_path(book_id).read_text(encoding="utf-8"))
            title = data["workspace"]["title"]
            if not isinstance(title, str) or not title.strip():
                raise ValueError("Missing title")
            titles[book_id] = title
        except (OSError, ValueError, KeyError, TypeError):
            titles[book_id] = f"无法读取的作品（{book_id}）"
    counts = Counter(titles.values())
    return {book_id: f"{title}（{book_id}）" if counts[title] > 1 or title == "新建作品" else title
            for book_id, title in titles.items()}
