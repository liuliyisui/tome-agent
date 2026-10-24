"""Local shelf preferences and recoverable book deletion."""
from datetime import datetime, timezone
import re
from uuid import uuid4

from inf_writer.domain import strict_json
from . import service


def checked_folder(book_id):
    folder = service.book_path(book_id)
    if folder.is_symlink() or folder.resolve().parent != service.BOOKS.resolve():
        raise ValueError("作品目录不安全")
    if not folder.is_dir():
        raise FileNotFoundError("作品不存在")
    return folder


def is_pinned(book_id):
    try:
        data = strict_json((checked_folder(book_id) / "shelf.json").read_text(encoding="utf-8"))
        return isinstance(data, dict) and data.get("pinned") is True
    except (OSError, ValueError):
        return False


def pin_book(book_id, pinned):
    if type(pinned) is not bool:
        raise ValueError("置顶状态须为布尔值")
    with service.operation_lock(service.BOOKS):
        folder = checked_folder(book_id)
        service._atomic_json(folder / "shelf.json", {"pinned": pinned})
    return {"pinned": pinned}


def trash_root():
    root = service.BOOKS / ".trash"
    if root.is_symlink() or root.resolve().parent != service.BOOKS.resolve():
        raise ValueError("回收目录不安全")
    return root


def delete_book(book_id):
    with service.operation_lock(service.BOOKS):
        folder = checked_folder(book_id)
        root = trash_root()
        root.mkdir(exist_ok=True)
        token = uuid4().hex
        destination = root / token
        with service.operation_lock(folder):
            service._atomic_json(folder / "deleted-book.json", {
                "book_id": book_id, "deleted_at": datetime.now(timezone.utc).isoformat()})
            folder.rename(destination)
            # The lock moved with the directory; remove only our own lock.
            (destination / "operation.lock").unlink()
    return {"deleted": True, "book_id": book_id, "restore_token": token}


def restore_book(token):
    if not isinstance(token, str) or not re.fullmatch(r"[a-f0-9]{32}", token):
        raise ValueError("恢复标识无效")
    with service.operation_lock(service.BOOKS):
        root = trash_root()
        folder = root / token
        if folder.is_symlink() or folder.resolve().parent != root.resolve():
            raise ValueError("恢复目录不安全")
        record = strict_json((folder / "deleted-book.json").read_text(encoding="utf-8"))
        destination = service.book_path(record["book_id"])
        if destination.exists():
            raise ValueError("同名作品目录已存在，不能覆盖")
        folder.rename(destination)
        (destination / "deleted-book.json").unlink()
    return record["book_id"]
