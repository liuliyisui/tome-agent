import json
import os
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, build_opener, ProxyHandler

from inf_backend import service, official_pricing, settings
from inf_backend.web import WebServer
from inf_backend.settings import Settings
from inf_writer.domain import apply_chapter, digest
from inf_writer.storage import FileStore


class WebIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.books_patch = patch.object(service, "BOOKS", Path(self.folder.name))
        self.books_patch.start()
        self.prices_patch = patch.object(official_pricing, "get_table", return_value={
            "models": official_pricing.SNAPSHOT, "checked_at": "2026-10-24", "status": "verified_snapshot"})
        self.prices_patch.start()
        self.server = WebServer(("127.0.0.1", 0))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"
        self.client = build_opener(ProxyHandler({}))

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.books_patch.stop()
        self.prices_patch.stop()
        self.folder.cleanup()

    def request(self, path, data=None, headers=None):
        if path.endswith("/generate") and data == {}:
            estimate = self.request(path.removesuffix("/generate") + "/estimate", {})
            data = {"estimate_id": estimate["estimate_id"], "confirmed": True}
        body = None if data is None else json.dumps(data).encode()
        req = Request(self.base + path, body, headers={"Content-Type": "application/json", **(headers or {})})
        with self.client.open(req, timeout=5) as response:
            raw = response.read()
            return json.loads(raw) if response.headers["Content-Type"].startswith("application/json") else raw.decode()

    def wait_job(self, job_id):
        end = time.monotonic() + 5
        while time.monotonic() < end:
            job = self.request("/api/jobs/" + job_id)
            if job["status"] != "running":
                self.assertEqual(job["status"], "completed", job)
                return
            time.sleep(.01)
        self.fail("generation timed out")

    def save_legacy_chapter(self, book_id):
        store = FileStore(service.BOOKS)
        state = store.load(book_id)
        state = apply_chapter(state, {"number": 1, "title": "首章", "brief": "旧存档测试", "future_updates": []},
                              "旧版正文。", [], "legacy-fixture", digest("legacy-fixture"))
        store.commit(state, expected_revision=0)

    def test_demo_entry_and_endpoint_removed_and_old_samples_hidden(self):
        self.assertNotIn('id="demo"', self.request("/"))
        with self.assertRaises(HTTPError) as error:
            self.request("/api/demo", {})
        self.assertEqual(error.exception.code, 404)
        service.create_book("old-demo", "旧演示", "测试", 2, 1000,
                            settings=Settings(api_key="", model="offline-demo"))
        self.assertEqual(self.request("/api/books")["books"], [])
        with self.assertRaises(HTTPError) as error:
            self.request("/api/books/old-demo")
        self.assertEqual(error.exception.code, 404)

    def test_vue_assets_are_local_and_keep_strict_script_policy(self):
        html = self.request("/")
        self.assertIn('src="/vue.runtime.global.prod.js"', html)
        self.assertIn('src="/vue-components.js"', html)
        self.assertIn("createTomeLibrary", self.request("/vue-components.js"))
        with self.client.open(self.base + "/vue.runtime.global.prod.js", timeout=5) as response:
            self.assertTrue(response.headers["Content-Type"].startswith("text/javascript"))
            self.assertNotIn("unsafe-eval", response.headers["Content-Security-Policy"])
            self.assertIn("Vue", response.read().decode())

    def test_create_validation_and_missing_book(self):
        with self.assertRaises(HTTPError) as error:
            self.request("/api/books", {"title": "", "prompt": "idea", "chapters": 3, "target_units": 500})
        self.assertEqual(error.exception.code, 400)
        book = self.request("/api/books", {"title": "新书", "prompt": "故事构想", "chapters": 3, "target_units": 500})
        self.assertEqual(book["metadata"]["title"], "新书")
        with self.assertRaises(HTTPError) as error:
            self.request("/api/books/missing-book")
        self.assertEqual(error.exception.code, 404)

    def test_first_run_api_configuration_is_private_persistent_and_one_time(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(settings, "BACKEND_ROOT", Path(folder)), patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""}, clear=True):
            path = Path(folder) / ".env"
            path.write_text("# keep settings\nDEEPSEEK_MODEL=deepseek-chat\nDEEPSEEK_API_KEY=\n", encoding="utf-8")
            self.assertFalse(self.request("/api/config")["configured"])
            key = "sk-" + "TEST_ONLY_" * 3
            for value in ("", "bad", key + "\nINJECTED=yes"):
                with self.assertRaises(HTTPError) as error:
                    self.request("/api/config", {"api_key": value})
                self.assertEqual(error.exception.code, 400)
            with self.assertRaises(HTTPError) as error:
                self.request("/api/config", {"api_key": key}, {"Origin": "https://other.example"})
            self.assertEqual(error.exception.code, 403)
            self.assertFalse(self.request("/api/config")["configured"])
            result = self.request("/api/config", {"api_key": key})
            self.assertEqual(result, {"configured": True, "model": "deepseek-chat"})
            self.assertNotIn(key, json.dumps(self.request("/api/config")))
            self.assertEqual(Settings.load().api_key, key)
            self.assertIn("# keep settings", path.read_text(encoding="utf-8"))
            with self.assertRaises(HTTPError) as error:
                self.request("/api/config", {"api_key": "sk-" + "OTHER_TEST_" * 3})
            self.assertEqual(error.exception.code, 400)
            self.assertEqual(Settings.load().api_key, key)

    def test_pin_delete_restore_and_block_deleting_running_book(self):
        payload = {"title": "书架测试", "prompt": "故事", "chapters": 3, "target_units": 3000}
        first = self.request("/api/books", payload)["state"]["project_id"]
        self.assertEqual(self.request("/api/books/trash")["books"], [])
        second = self.request("/api/books", {**payload, "title": "置顶作品"})["state"]["project_id"]
        self.assertEqual(self.request(f"/api/books/{second}/pin", {"pinned": True}), {"pinned": True})
        shelf = self.request("/api/books")["books"]
        self.assertEqual(shelf[0]["id"], second)
        self.assertTrue(shelf[0]["pinned"])
        self.request(f"/api/books/{second}/pin", {"pinned": False})
        self.assertFalse(next(b for b in self.request("/api/books")["books"] if b["id"] == second)["pinned"])
        self.server.busy.add(first)
        try:
            with self.assertRaises(HTTPError) as error:
                self.request(f"/api/books/{first}/delete", {"confirmed": True})
            self.assertEqual(error.exception.code, 400)
            self.assertTrue(service.book_path(first).exists())
        finally:
            self.server.busy.discard(first)
        with self.assertRaises(HTTPError):
            self.request(f"/api/books/{first}/delete", {"confirmed": False})
        original = (service.book_path(first) / "state.json").read_bytes() if (service.book_path(first) / "state.json").exists() else None
        deleted = self.request(f"/api/books/{first}/delete", {"confirmed": True})
        trash = self.request("/api/books/trash")["books"]
        self.assertEqual(len(trash), 1)
        self.assertEqual(trash[0]["title"], "书架测试")
        self.assertEqual(trash[0]["restore_token"], deleted["restore_token"])
        self.assertEqual(self.request("/api/books/trash")["books"], trash)
        self.assertEqual([b["id"] for b in self.request("/api/books")["books"]], [second])
        with self.assertRaises(HTTPError) as error:
            self.request(f"/api/books/{first}")
        self.assertEqual(error.exception.code, 404)
        restored = self.request("/api/books/restore", {"restore_token": deleted["restore_token"]})
        self.assertEqual(self.request("/api/books/trash")["books"], [])
        self.assertEqual(restored["state"]["project_id"], first)
        if original is not None:
            self.assertEqual((service.book_path(first) / "state.json").read_bytes(), original)
        self.assertFalse((service.book_path(first) / "operation.lock").exists())
        self.assertFalse((service.book_path(first) / "deleted-book.json").exists())
        with self.assertRaises(HTTPError):
            self.request("/api/books/restore", {"restore_token": "../../bad"})

    def test_permanent_delete_endpoint_requires_confirmation_and_correct_title(self):
        book = self.request("/api/books", {"title": "可删除测试作品", "prompt": "故事", "chapters": 3, "target_units": 3000})
        book_id = book["state"]["project_id"]
        token = self.request(f"/api/books/{book_id}/delete", {"confirmed": True})["restore_token"]
        for payload in ({"restore_token": token, "confirmation_title": "可删除测试作品", "confirmed": False},
                        {"restore_token": token, "confirmation_title": "错误标题", "confirmed": True}):
            with self.assertRaises(HTTPError) as error:
                self.request("/api/books/trash/purge", payload)
            self.assertEqual(error.exception.code, 400)
            self.assertEqual(len(self.request("/api/books/trash")["books"]), 1)
        result = self.request("/api/books/trash/purge", {"restore_token": token, "confirmation_title": "可删除测试作品", "confirmed": True})
        self.assertEqual(result, {"purged": True})
        self.assertEqual(self.request("/api/books/trash")["books"], [])
        with self.assertRaises(HTTPError) as error:
            self.request("/api/books/restore", {"restore_token": token})
        self.assertEqual(error.exception.code, 404)

    def test_estimate_is_offline_and_generation_requires_confirmation(self):
        book = self.request("/api/books", {"title": "预估测试", "prompt": "故事", "chapters": 5, "target_units": 10000})
        book_id = book["state"]["project_id"]
        with patch.object(service, "_gateway") as gateway:
            estimate = self.request(f"/api/books/{book_id}/estimate", {"count": 1})
            self.assertGreater(estimate["total_tokens"], 0)
            expected = (estimate["input_tokens"] * estimate["prices"]["input"] + estimate["output_tokens"] * estimate["prices"]["output"]) / 1_000_000
            self.assertAlmostEqual(estimate["estimated_cost_cny"], expected)
            self.assertEqual(estimate["pricing"]["currency"], "CNY")
            self.assertIn("参考价", estimate["pricing"]["warning"])
            gateway.assert_not_called()
            with self.assertRaises(HTTPError) as error:
                self.request(f"/api/books/{book_id}/generate", {"estimate_id": estimate["estimate_id"], "confirmed": False})
            self.assertEqual(error.exception.code, 400)
            gateway.assert_not_called()
        self.assertEqual(self.server.jobs, {})
        with self.assertRaises(HTTPError) as error:
            self.request(f"/api/books/{book_id}/estimate", {"count": 1, "prices": {"input": 0, "output": 0}})
        self.assertEqual(error.exception.code, 400)
        with self.assertRaises(HTTPError) as error:
            self.request(f"/api/books/{book_id}/estimate", {"count": 3, "approved_first": True})
        self.assertEqual(error.exception.code, 400)
        self.request(f"/api/books/{book_id}/style", {"instructions": "短句", "reference": ""})
        with self.assertRaises(HTTPError) as error:
            self.request(f"/api/books/{book_id}/generate", {"estimate_id": estimate["estimate_id"], "confirmed": True})
        self.assertEqual(error.exception.code, 400)

    def test_confirmed_batch_passes_count_and_tracks_progress(self):
        book = self.request("/api/books", {"title": "批量测试", "prompt": "故事", "chapters": 5, "target_units": 10000})
        book_id = book["state"]["project_id"]
        state = {"chapters": [{"number": 1, "title": "首章", "text": "首章正文。"}], "memory": {"items": {}}, "pending": []}

        def batch(*args, **kwargs):
            self.assertEqual(kwargs["count"], 3)
            kwargs["progress"]({"completed": 2, "current_chapter": 4})

        with patch.object(service, "load_book", return_value={"metadata": book["metadata"], "state": state}), \
                patch("inf_backend.web.Settings.load", return_value=Settings(api_key="FAKE_TEST_KEY")), \
                patch.object(service, "generate", side_effect=batch) as generate:
            with self.assertRaises(HTTPError):
                self.request(f"/api/books/{book_id}/estimate", {"count": 3})
            estimate = self.request(f"/api/books/{book_id}/estimate", {"count": 3, "approved_first": True})
            job = self.request(f"/api/books/{book_id}/generate", {"estimate_id": estimate["estimate_id"], "confirmed": True})
            self.wait_job(job["job_id"])
            result = self.request(f"/api/jobs/{job['job_id']}")
            self.assertEqual(result["count"], 3)
            self.assertEqual(result["completed"], 3)
            generate.assert_called_once()

    def test_create_edit_reload_and_clear_writing_style(self):
        style = {"instructions": "短句、对白自然。", "reference": "他推开门，雨已经停了。"}
        book = self.request("/api/books", {"title": "文风作品", "prompt": "故事", "chapters": 3,
                                          "target_units": 3000, "style": style})
        book_id = book["state"]["project_id"]
        self.assertEqual(book["style"], style)
        changed = {"instructions": "改用第一人称。", "reference": ""}
        self.assertEqual(self.request(f"/api/books/{book_id}/style", changed)["style"], changed)
        self.assertEqual(self.request(f"/api/books/{book_id}")["style"], changed)
        with self.assertRaises(HTTPError) as error:
            self.request(f"/api/books/{book_id}/style", {"instructions": [], "reference": ""})
        self.assertEqual(error.exception.code, 400)
        self.assertEqual(self.request(f"/api/books/{book_id}")["style"], changed)
        empty = {"instructions": "", "reference": ""}
        self.request(f"/api/books/{book_id}/style", empty)
        self.assertEqual(self.request(f"/api/books/{book_id}")["style"], empty)

    def test_refresh_recovers_job_and_duplicate_submit_reuses_it(self):
        book = self.request("/api/books", {"title": "任务恢复", "prompt": "测试故事", "chapters": 3, "target_units": 3000})
        book_id = book["state"]["project_id"]
        release = threading.Event()

        def blocked(*args, **kwargs):
            if not release.wait(5):
                raise RuntimeError("test generation timed out")
            kwargs["progress"]({"completed": 1, "current_chapter": 1})

        with patch.object(service, "generate", side_effect=blocked) as generate, \
                patch("inf_backend.web.Settings.load", return_value=Settings(api_key="FAKE_TEST_KEY")):
            try:
                first = self.request(f"/api/books/{book_id}/generate", {})
                reloaded = self.request(f"/api/books/{book_id}")
                self.assertEqual(reloaded["job"]["status"], "running")
                self.assertEqual(reloaded["job"]["job_id"], first["job_id"])
                second = self.request(f"/api/books/{book_id}/generate", {})
                self.assertEqual(second["job_id"], first["job_id"])
            finally:
                release.set()
            self.wait_job(first["job_id"])
            generate.assert_called_once()
        completed = self.request(f"/api/books/{book_id}")
        self.assertEqual(completed["job"]["status"], "completed")
        self.assertEqual(completed["job"]["completed"], 1)

    def test_reject_cross_origin_and_path_escape(self):
        with self.assertRaises(HTTPError) as error:
            self.request("/api/books", {}, {"Origin": "https://example.com"})
        self.assertEqual(error.exception.code, 403)
        with self.assertRaises(HTTPError) as error:
            self.request("/../backend/.env")
        self.assertEqual(error.exception.code, 404)
        with self.assertRaises(HTTPError) as error:
            self.request("/api/config", headers={"Host": "attacker.example"})
        self.assertEqual(error.exception.code, 403)

    def test_longform_view_and_generation_use_new_engine(self):
        book = self.request("/api/books", {"title": "新版作品", "prompt": "故事构想", "chapters": 3, "target_units": 500})
        book_id = book["state"]["project_id"]
        state = {"chapters": [{"number": 1, "title": "开端", "text": "许闻发现档案。"}],
                 "pending": [], "memory": {"items": {"fact-1": {
                     "id": "fact-1", "subject": "许闻", "attribute": "discovery", "claim": "发现档案", "status": "active",
                     "tier": "working", "revision": 1, "kind": "event", "sources": [{"chapter_number": 1, "quote": "许闻发现档案。"}]}}}}
        with patch.object(service, "load_book", return_value={"metadata": book["metadata"], "state": state}), \
                patch("inf_backend.web.Settings.load", return_value=Settings(api_key="FAKE_TEST_KEY")), \
                patch.object(service, "generate") as generate:
            view = self.request(f"/api/books/{book_id}")
            self.assertEqual(view["mode"], "longform")
            self.assertEqual(view["state"]["project_id"], book_id)
            self.assertEqual(view["state"]["facts"]["fact-1"]["value"], "发现档案")
            self.assertEqual(view["state"]["memory_tiers"]["working"], 1)
            self.assertEqual(self.request("/api/books")["books"][0]["chapters"], 1)
            job = self.request(f"/api/books/{book_id}/generate", {})
            self.wait_job(job["job_id"])
            generate.assert_called_once()

    def test_legacy_prose_cannot_be_overwritten_by_new_engine(self):
        cfg = Settings(api_key="FAKE_TEST_KEY")
        service.create_book("legacy-book", "旧版作品", "故事", 3, 1000, settings=cfg)
        self.save_legacy_chapter("legacy-book")
        self.assertEqual(self.request("/api/books/legacy-book")["mode"], "legacy")
        with self.assertRaises(HTTPError) as error:
            self.request("/api/books/legacy-book/generate", {})
        self.assertEqual(error.exception.code, 400)
        self.assertEqual(len(service.load_book("legacy-book")["state"].chapters), 1)


if __name__ == "__main__":
    unittest.main()
