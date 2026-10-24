"""Shelf operations backed by PostgreSQL; checkpoints stay in their original folders."""
from datetime import datetime, timezone
import re
import shutil
from uuid import uuid4
from . import database as db


def is_pinned(book_id):
    return db.row(book_id)["pinned"]


def pin_book(book_id, pinned):
    if type(pinned) is not bool:
        raise ValueError("置顶状态须为布尔值")
    with db.connect() as conn:
        db.row(book_id, conn)
        conn.execute("UPDATE tome_books SET pinned=%s WHERE id=%s", (pinned, book_id))
    return {"pinned": pinned}


def delete_book(book_id):
    from . import service
    with service.operation_lock(service.book_path(book_id)), db.connect() as conn:
        db.row(book_id, conn)
        if conn.execute("SELECT 1 FROM tome_jobs WHERE book_id=%s AND status='running'", (book_id,)).fetchone():
            raise ValueError("作品正在生成，或有待恢复的中断任务")
        token = uuid4().hex
        conn.execute("UPDATE tome_books SET deleted_at=now(),restore_token=%s WHERE id=%s", (token, book_id))
    return {"deleted": True, "book_id": book_id, "restore_token": token}


def checked_token(conn, token):
    if not isinstance(token, str) or not re.fullmatch(r"[a-f0-9]{32}", token):
        raise ValueError("废案箱标识无效")
    found = conn.execute("SELECT * FROM tome_books WHERE restore_token=%s FOR UPDATE", (token,)).fetchone()
    if not found:
        raise FileNotFoundError("废案不存在")
    return found


def restore_book(token):
    with db.connect() as conn:
        found = checked_token(conn, token)
        conn.execute("UPDATE tome_books SET deleted_at=NULL,restore_token=NULL WHERE id=%s", (found["id"],))
        return found["id"]


def list_deleted_books():
    with db.connect() as conn:
        return [{"restore_token": x["restore_token"], "book_id": x["id"],
                 "title": x["metadata"]["title"], "deleted_at": x["deleted_at"].isoformat()}
                for x in conn.execute("SELECT * FROM tome_books WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC")]


def permanently_delete_book(token, confirmation_title):
    from . import service
    with db.connect() as conn:
        found = checked_token(conn, token)
        if confirmation_title != found["metadata"]["title"]:
            raise ValueError("请输入完整作品名称以确认彻底删除")
        folder = service.book_path(found["id"])
        root = service.BOOKS.resolve()
        if folder.is_symlink() or folder.resolve().parent not in (root, root / ".trash"):
            raise ValueError("作品目录不安全")
        pending = [folder] if folder.exists() else []
        while pending:
            path = pending.pop()
            if path.is_symlink() or getattr(path, "is_junction", lambda: False)() or not path.resolve().is_relative_to(folder.resolve()):
                raise ValueError("作品包含不安全的链接")
            if path.is_dir():
                pending.extend(path.iterdir())
        # Explicit title-confirmed purge only. Soft delete never moves checkpoint files.
        if folder.exists():
            shutil.rmtree(folder)
        conn.execute("DELETE FROM tome_books WHERE id=%s", (found["id"],))
    return {"purged": True}
