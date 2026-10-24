"""Real PostgreSQL tests. Each test owns a disposable schema, never existing tables."""
import copy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from inf_backend import database as db, service, library
from inf_backend.migrate import import_books, recover_jobs
from inf_backend.settings import Settings
from inf_writer.domain import Snapshot


@unittest.skipUnless(os.environ.get("TOME_TEST_DATABASE_URL"), "Set TOME_TEST_DATABASE_URL for real PostgreSQL tests")
class PostgreSQLTests(unittest.TestCase):
    def setUp(self):
        import psycopg
        from psycopg import sql
        from psycopg.conninfo import make_conninfo
        self.schema = "tome_test_" + uuid4().hex
        self.base = os.environ["TOME_TEST_DATABASE_URL"]
        with psycopg.connect(self.base) as c:
            c.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
        self.addCleanup(self.drop_schema)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {"DATABASE_URL": make_conninfo(self.base, options="-csearch_path=" + self.schema)})
        self.env.start()
        self.addCleanup(self.env.stop)
        p = patch.object(service, "BOOKS", self.root / "books")
        p.start()
        self.addCleanup(p.stop)
        service.BOOKS.mkdir()
        db.initialize()
        db.initialize()  # schema init is repeatable

    def drop_schema(self):
        import psycopg
        from psycopg import sql
        with psycopg.connect(self.base) as c:
            c.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema)))

    def create(self, book_id="pg-book"):
        return service.create_book(book_id, "数据库测试", "守住灯塔", 3, 3000, settings=Settings(api_key="FAKE"))

    def test_roundtrip_chapter_versions_and_rollback(self):
        self.create()
        state = db.row("pg-book")["state"]
        state["chapters"] = [{"number": 1, "title": "灯塔", "text": "灯亮了。"}]
        db.save("pg-book", state, "longform", "run/checkpoint.json", {"input_tokens": 11, "output_tokens": 9})
        db.save("pg-book", state, "longform", "run/checkpoint.json")
        revised = copy.deepcopy(state)
        revised["chapters"][0]["text"] = "灯又亮了。"
        db.save("pg-book", revised, "longform", "run/checkpoint2.json")
        self.assertEqual(service.load_book("pg-book")["state"], revised)
        with db.connect() as c:
            self.assertEqual(c.execute("SELECT count(*) AS n FROM tome_chapter_versions").fetchone()["n"], 2)
            self.assertEqual(c.execute("SELECT count(*) AS n FROM tome_usage").fetchone()["n"], 1)
        invalid = copy.deepcopy(revised)
        invalid["chapters"].append({"number": 0, "title": "", "text": "invalid"})
        with self.assertRaises(db.DatabaseUnavailable):
            db.save("pg-book", invalid, "longform")
        self.assertEqual(service.load_book("pg-book")["state"], revised)
        self.assertEqual(service.last_usage("pg-book")["input_tokens"], 11)

    def test_style_trash_restore_and_title_confirmed_purge(self):
        self.create()
        value = {"instructions": "简洁", "reference": "海风。"}
        service.save_writing_style("pg-book", value)
        self.assertEqual(service.load_writing_style("pg-book"), value)
        library.pin_book("pg-book", True)
        self.assertTrue(library.is_pinned("pg-book"))
        token = library.delete_book("pg-book")["restore_token"]
        self.assertEqual(service.list_books(), [])
        self.assertEqual(library.list_deleted_books()[0]["title"], "数据库测试")
        library.restore_book(token)
        self.assertIn("pg-book", service.list_books())
        token = library.delete_book("pg-book")["restore_token"]
        with self.assertRaises(ValueError):
            library.permanently_delete_book(token, "wrong")
        library.permanently_delete_book(token, "数据库测试")
        self.assertEqual(library.list_deleted_books(), [])

    def test_session_lock_and_persisted_job_recovery(self):
        self.create()
        folder = service.book_path("pg-book")
        with service.operation_lock(folder):
            with self.assertRaises(ValueError):
                with service.operation_lock(folder):
                    pass
        db.job("job-one", {"book_id": "pg-book", "status": "running", "count": 2})
        self.assertEqual(db.latest_job("pg-book")["job_id"], "job-one")
        self.assertEqual(recover_jobs()["interrupted"], 1)
        self.assertEqual(db.job("job-one")["status"], "interrupted")
        db.job("job-two", {"book_id": "pg-book", "status": "running"})
        with self.assertRaises(db.DatabaseUnavailable):
            db.job("job-three", {"book_id": "pg-book", "status": "running"})

    def test_legacy_import_is_atomic_idempotent_and_preserves_files(self):
        with patch.dict(os.environ, {"DATABASE_URL": ""}):
            self.create("from-files")
            folder = service.book_path("from-files")
            service.save_writing_style("from-files", {"instructions": "简洁", "reference": ""})
            original = {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob("*") if p.is_file()}
        self.assertFalse(import_books(service.BOOKS)["applied"])
        self.assertEqual(import_books(service.BOOKS, True)["imported"], 1)
        self.assertEqual(import_books(service.BOOKS, True)["skipped"], 1)
        self.assertEqual(service.load_book("from-files")["metadata"]["title"], "数据库测试")
        self.assertEqual(original, {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob("*") if p.is_file()})
        service.save_writing_style("from-files", {"instructions": "已更新", "reference": ""})
        with self.assertRaises(ValueError):
            import_books(service.BOOKS, True)
        self.assertEqual(service.load_writing_style("from-files")["instructions"], "已更新")

    def test_postgresql_failures_are_not_silent_file_fallback(self):
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://invalid:secret@127.0.0.1:1/tome"}):
            with self.assertRaises(db.DatabaseUnavailable) as caught:
                service.list_books()
        self.assertNotIn("secret", str(caught.exception))

    def test_generation_persists_chapters_and_resume_pointer(self):
        from types import SimpleNamespace
        self.create()
        class Session:
            def __init__(inner, run, gateway, plan, book=None):
                inner.book = copy.deepcopy(book) if book else {"chapters": [], "memory": {}, "pending": []}
                inner.latest_checkpoint = run / "checkpoint.json"
                inner.latest_checkpoint.parent.mkdir(parents=True)
                inner.latest_checkpoint.write_text("{}", encoding="utf-8")
            def write_next(inner, instruction):
                n = len(inner.book["chapters"]) + 1
                inner.book["chapters"].append({"number": n, "title": "灯塔", "text": "灯亮了。"})
                return {"status": "COMMITTED"}
        budget = SimpleNamespace(calls=3, input_tokens=90, output_tokens=30, cost_upper_usd=.01)
        cfg = Settings(api_key="FAKE")
        with patch.object(service, "WritingSession", Session), patch.object(service, "_gateway", return_value=(object(), budget)):
            service.generate("pg-book", count=1, settings=cfg)
            first = db.row("pg-book")
            with patch.object(service, "load_resume", return_value=first["state"]) as resume:
                service.generate("pg-book", count=1, settings=cfg)
                self.assertEqual(resume.call_args.args[0], (service.book_path("pg-book") / first["checkpoint"]).resolve())
        self.assertEqual(len(service.load_book("pg-book")["state"]["chapters"]), 2)
        self.assertIn("灯亮了。", service.export_markdown(service.load_book("pg-book")))
        with db.connect() as c:
            self.assertEqual(c.execute("SELECT count(*) AS n FROM tome_chapters").fetchone()["n"], 2)

    def test_web_reads_database_and_jobs_after_server_restart(self):
        import json
        import threading
        from urllib.request import build_opener, ProxyHandler
        from inf_backend.web import WebServer
        self.create()
        db.job("saved-job", {"book_id": "pg-book", "status": "completed", "count": 1})
        server = WebServer(("127.0.0.1", 0))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = build_opener(ProxyHandler({}))
            base = f"http://127.0.0.1:{server.server_port}"
            with client.open(base + "/api/books") as response:
                self.assertEqual(json.load(response)["books"][0]["metadata"]["title"], "数据库测试")
            with client.open(base + "/api/books/pg-book") as response:
                self.assertEqual(json.load(response)["job"]["job_id"], "saved-job")
            with client.open(base + "/api/jobs/saved-job") as response:
                self.assertEqual(json.load(response)["status"], "completed")
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
