"""Local shelf preferences and recoverable book deletion."""
from datetime import datetime, timezone
import re
import shutil
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
    if root.is_symlink() or getattr(root, "is_junction", lambda: False)() or root.resolve().parent != service.BOOKS.resolve():
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


def list_deleted_books():
    root = trash_root()
    books = []
    for folder in root.iterdir() if root.exists() else []:
        if not re.fullmatch(r"[a-f0-9]{32}", folder.name) or folder.is_symlink() or not folder.is_dir():
            continue
        if folder.resolve().parent != root.resolve():
            continue
        try:
            record = strict_json((folder / "deleted-book.json").read_text(encoding="utf-8"))
            service.book_path(record["book_id"])
            metadata = strict_json((folder / "metadata.json").read_text(encoding="utf-8"))
            books.append({"restore_token": folder.name, "book_id": record["book_id"],
                          "title": metadata.get("title") or record["book_id"],
                          "deleted_at": record.get("deleted_at", "")})
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return sorted(books, key=lambda book: book["deleted_at"], reverse=True)


def permanently_delete_book(token, confirmation_title):
    if not isinstance(token, str) or not re.fullmatch(r"[a-f0-9]{32}", token):
        raise ValueError("删除标识无效")
    with service.operation_lock(service.BOOKS):
        root = trash_root().resolve()
        folder = root / token
        if folder.is_symlink() or folder.resolve().parent != root or not folder.is_dir():
            raise ValueError("只能彻底删除废案箱内的作品")
        record = strict_json((folder / "deleted-book.json").read_text(encoding="utf-8"))
        service.book_path(record["book_id"])
        metadata = strict_json((folder / "metadata.json").read_text(encoding="utf-8"))
        title = metadata.get("title") or record["book_id"]
        if not isinstance(confirmation_title, str) or confirmation_title != title:
            raise ValueError("请输入完整作品名称以确认彻底删除")
        # Never follow symlinks or Windows junctions out of the selected trash
        # directory. Verify all resolved paths before the recursive deletion.
        pending = [folder]
        while pending:
            path = pending.pop()
            resolved = path.resolve()
            if path.is_symlink() or getattr(path, "is_junction", lambda: False)() or not resolved.is_relative_to(folder.resolve()):
                raise ValueError("作品包含不安全的链接，无法彻底删除")
            if path.is_dir():
                pending.extend(path.iterdir())
        shutil.rmtree(folder)
    return {"purged": True}
