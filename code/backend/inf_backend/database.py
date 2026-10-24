"""PostgreSQL repository. Configured database failures never fall back to files."""
from contextlib import contextmanager
import os
from pathlib import Path

from .settings import BACKEND_ROOT, _dotenv


def url():
    return os.environ.get("DATABASE_URL", _dotenv(BACKEND_ROOT / ".env").get("DATABASE_URL", ""))


def enabled():
    return bool(url().strip())


class DatabaseUnavailable(RuntimeError):
    pass


@contextmanager
def connect():
    if not enabled():
        raise DatabaseUnavailable("请配置 DATABASE_URL")
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError:
        raise DatabaseUnavailable("请先安装 code/backend/requirements.txt 中的依赖") from None
    try:
        with psycopg.connect(url(), connect_timeout=5, row_factory=dict_row) as conn:
            yield conn
    except psycopg.Error:
        # Connection strings and SQL parameter values can contain credentials/prose.
        raise DatabaseUnavailable("数据库操作失败，请检查 PostgreSQL 服务、连接配置和初始化状态") from None


def jsonb(value):
    from psycopg.types.json import Jsonb
    return Jsonb(value)


def initialize():
    with connect() as conn:
        conn.execute("SELECT pg_advisory_xact_lock(731592024)")
        conn.execute((Path(__file__).parent / "schema.sql").read_text(encoding="utf-8"))


def row(book_id, conn=None, deleted=False):
    if conn is None:
        with connect() as c:
            return row(book_id, c, deleted)
    result = conn.execute("SELECT * FROM tome_books WHERE id=%s", (book_id,)).fetchone()
    if result is None or (result["deleted_at"] and not deleted):
        raise FileNotFoundError("作品不存在")
    return result


def create(book_id, metadata, state, style, *, conn=None):
    if conn is None:
        with connect() as c:
            return create(book_id, metadata, state, style, conn=c)
    if conn.execute("SELECT 1 FROM tome_books WHERE id=%s", (book_id,)).fetchone():
        raise ValueError("数据库中作品已存在；迁移不会覆盖")
    conn.execute("""INSERT INTO tome_books(id,metadata,state,state_kind,style)
        VALUES(%s,%s,%s,'snapshot',%s)""",
        (book_id, jsonb(metadata), jsonb(state), jsonb(style)))
    save(book_id, state, "snapshot", conn=conn)


def save(book_id, state, kind, checkpoint=None, usage=None, *, conn=None):
    if conn is None:
        with connect() as c:
            return save(book_id, state, kind, checkpoint, usage, conn=c)
    old = conn.execute("SELECT id FROM tome_books WHERE id=%s AND deleted_at IS NULL FOR UPDATE", (book_id,)).fetchone()
    if not old:
        raise FileNotFoundError("作品不存在")
    conn.execute("""UPDATE tome_books SET state=%s,state_kind=%s,checkpoint=%s,
        last_usage=COALESCE(%s,last_usage),updated_at=now() WHERE id=%s""",
        (jsonb(state), kind, checkpoint, jsonb(usage) if usage is not None else None, book_id))
    if usage is not None and checkpoint is not None:
        conn.execute("""INSERT INTO tome_usage(book_id,checkpoint,payload) VALUES(%s,%s,%s)
            ON CONFLICT(book_id,checkpoint) DO UPDATE SET payload=excluded.payload""",
                     (book_id, checkpoint, jsonb(usage)))
    for chapter in state.get("chapters", []):
        number, text = chapter["number"], chapter["text"]
        title = chapter.get("title", "")
        old = conn.execute("SELECT title,body,version FROM tome_chapters WHERE book_id=%s AND number=%s",
                           (book_id, number)).fetchone()
        if old and old["body"] == text and old["title"] == title:
            continue
        version = old["version"] + 1 if old else 1
        conn.execute("""INSERT INTO tome_chapters(book_id,number,title,body,version) VALUES(%s,%s,%s,%s,%s)
            ON CONFLICT(book_id,number) DO UPDATE SET title=excluded.title,body=excluded.body,version=excluded.version""",
            (book_id, number, title, text, version))
        conn.execute("INSERT INTO tome_chapter_versions(book_id,number,version,title,body) VALUES(%s,%s,%s,%s,%s)",
                     (book_id, number, version, title, text))


def books():
    with connect() as conn:
        return [r["id"] for r in conn.execute("""SELECT id FROM tome_books
            WHERE deleted_at IS NULL AND metadata->'model'->>'model' <> 'offline-demo'
            ORDER BY pinned DESC,created_at,id""")]


def style(book_id, value=None):
    with connect() as conn:
        found = row(book_id, conn)
        if value is not None:
            conn.execute("UPDATE tome_books SET style=%s,updated_at=now() WHERE id=%s", (jsonb(value), book_id))
            return value
        return found["style"]


@contextmanager
def lock(name):
    # Session lock, held across requests without keeping a transaction open.
    with connect() as conn:
        conn.autocommit = True
        if not conn.execute("SELECT pg_try_advisory_lock(hashtextextended(%s,0)) AS ok", (name,)).fetchone()["ok"]:
            raise ValueError("此作品有操作正在进行")
        try:
            yield
        finally:
            conn.execute("SELECT pg_advisory_unlock(hashtextextended(%s,0))", (name,))


def job(job_id, value=None):
    with connect() as conn:
        if value is not None:
            conn.execute("""INSERT INTO tome_jobs(id,book_id,payload,status) VALUES(%s,%s,%s,%s)
                ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,status=excluded.status,updated_at=now()""",
                (job_id, value["book_id"], jsonb(value), value["status"]))
            return value
        found = conn.execute("SELECT payload FROM tome_jobs WHERE id=%s", (job_id,)).fetchone()
        return found["payload"] if found else None


def latest_job(book_id):
    with connect() as conn:
        found = conn.execute("SELECT id,payload FROM tome_jobs WHERE book_id=%s ORDER BY created_at DESC,id DESC LIMIT 1",
                             (book_id,)).fetchone()
        return {**found["payload"], "job_id": found["id"]} if found else None


def storage_key(book_id):
    with connect() as conn:
        found = conn.execute("SELECT storage_key FROM tome_books WHERE id=%s", (book_id,)).fetchone()
        return (found["storage_key"] if found else None) or book_id
