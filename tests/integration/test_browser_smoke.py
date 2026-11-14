"""Browser smoke tests for the local UI.

Skipped unless Playwright and its Chromium build are installed. Install with:

    code/backend/.venv/Scripts/python.exe -m pip install playwright
    code/backend/.venv/Scripts/python.exe -m playwright install chromium

The suite never calls the model: it only exercises page load, book creation,
the cost-estimate dialog, deletion and refresh persistence.
"""

import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from inf_backend import official_pricing, service, settings
from inf_backend.web import WebServer

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - optional dependency
    sync_playwright = None

TITLE = "浏览器冒烟作品"


@unittest.skipUnless(sync_playwright, "Install playwright to run browser smoke tests")
class BrowserSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        try:
            cls.browser = cls.playwright.chromium.launch()
        except Exception as exc:  # browser binary missing
            cls.playwright.stop()
            raise unittest.SkipTest(f"Chromium is not installed: {exc}") from None

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.books_patch = patch.object(service, "BOOKS", Path(self.folder.name))
        self.books_patch.start()
        self.data_patch = patch.object(
            service, "DATA", Path(self.folder.name) / "test-data"
        )
        self.data_patch.start()
        self.settings_patch = patch.object(
            settings, "BACKEND_ROOT", Path(self.folder.name)
        )
        self.settings_patch.start()
        self.prices_patch = patch.object(
            official_pricing,
            "get_table",
            return_value={
                "models": official_pricing.SNAPSHOT,
                "checked_at": "2026-11-07",
                "status": "verified_snapshot",
            },
        )
        self.prices_patch.start()
        self.key_patch = patch.dict(
            os.environ,
            {
                "DEEPSEEK_API_KEY": "sk-" + "a" * 32,
                "DATABASE_URL": "",
                "TOME_PROVIDER": "",
            },
        )
        self.key_patch.start()
        self.server = WebServer(("127.0.0.1", 0))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"
        self.page = self.browser.new_page()
        self.page.goto(self.base)
        # init() reads /api/config before the create button is usable.
        self.page.wait_for_function(
            "document.getElementById('connection-text').textContent.includes('已就绪')"
        )

    def tearDown(self):
        self.page.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.key_patch.stop()
        self.books_patch.stop()
        self.data_patch.stop()
        self.settings_patch.stop()
        self.prices_patch.stop()
        self.folder.cleanup()

    def open_library(self):
        page = self.page
        page.click("#my-works")
        page.wait_for_selector("#works-view")
        return page

    def open_create_dialog(self):
        page = self.open_library()
        page.click("#works-create")
        page.wait_for_selector("#create-dialog[open]")

    def fill_create_form(self):
        page = self.page
        page.fill('input[name="title"]', TITLE)
        page.fill('textarea[name="prompt"]', "一名图书管理员在闭馆后听见书页自己翻动。")
        page.fill('input[name="chapters"]', "1")
        page.fill('input[name="target_units"]', "500")

    def test_create_style_displays_recommendations_and_live_limits(self):
        self.open_create_dialog()
        self.page.locator("#create-dialog .create-style summary").first.click()
        instructions = self.page.locator('textarea[name="style_instructions"]')
        reference = self.page.locator('textarea[name="style_reference"]')
        instruction_hint = instructions.locator("..").locator("small")
        reference_hint = reference.locator("..").locator("small")
        self.assertIn("50～300", instruction_hint.inner_text())
        self.assertIn("1,000～3,000", reference_hint.inner_text())
        instructions.fill("短句" * 1001)
        reference.fill("参考" * 3001)
        self.assertEqual(len(instructions.input_value()), 2000)
        self.assertEqual(len(reference.input_value()), 6000)
        self.assertIn("2000 / 2,000", instruction_hint.inner_text())
        self.assertIn("6000 / 6,000", reference_hint.inner_text())

    def test_home_and_empty_library(self):
        page = self.page
        self.assertEqual(page.title(), "Tome · 故事工作室")
        page.wait_for_selector("#welcome")

        page = self.open_library()
        page.wait_for_selector(".works-empty")
        self.assertIn("书架还是空的", page.inner_text(".works-empty"))
        self.assertEqual(page.text_content("#book-count").strip(), "0")

    def test_model_configuration_accepts_compatible_base_url(self):
        model_environment = {
            key: value
            for key, value in os.environ.items()
            if key not in ("TOME_PROVIDER", "TOME_MODEL", "TOME_ENDPOINT")
        }
        with (
            patch.dict(os.environ, model_environment, clear=True),
            patch("inf_backend.web.test_model_connection", return_value=True),
        ):
            self.page.click("#open-settings")
            self.page.click("#open-model-settings")
            self.page.click(".provider-add")
            self.page.fill("#model-provider", "测试供应商")
            self.page.get_by_label("Base URL").fill("https://example.com/v1/")
            self.page.fill("#model-name", "qwen-plus")
            self.page.fill("#api-key-input", "fake-model-key")
            with self.page.expect_response(
                lambda response: (
                    response.url.endswith("/api/model-config")
                    and response.request.method == "POST"
                )
            ) as pending:
                self.page.click("#api-key-save")
            response = pending.value
            self.assertTrue(response.ok)
            self.assertEqual(
                response.json()["endpoint"], "https://example.com/v1/chat/completions"
            )
            self.page.wait_for_selector("#api-key-dialog:not([open])", state="attached")
            with self.page.expect_response("**/api/model-config"):
                self.page.reload()
            self.page.click("#open-settings")
            self.page.click("#open-model-settings")
            self.assertEqual(
                self.page.get_by_label("Base URL").input_value(),
                "https://example.com/v1/chat/completions",
            )

    def test_cancel_skill_picker_keeps_create_dialog_and_draft(self):
        self.open_create_dialog()
        self.page.fill('input[name="title"]', "未完成的故事")
        self.page.fill('textarea[name="prompt"]', "夜里的图书馆")
        self.page.locator('#create-dialog input[type="file"]').dispatch_event(
            "cancel", {"bubbles": True}
        )
        self.assertTrue(self.page.locator("#create-dialog[open]").count())
        self.assertEqual(self.page.input_value('input[name="title"]'), "未完成的故事")
        self.assertEqual(
            self.page.input_value('textarea[name="prompt"]'), "夜里的图书馆"
        )
        self.page.keyboard.press("Escape")
        self.assertFalse(self.page.locator("#create-dialog[open]").count())

    def test_create_estimate_delete_and_refresh(self):
        page = self.page
        self.open_create_dialog()
        self.fill_create_form()
        page.click("#create-submit")

        page.wait_for_selector("#book-workspace")
        self.assertEqual(page.inner_text("#book-title"), TITLE)
        self.assertEqual(page.inner_text("#stat-chapters").strip(), "0 / 1")
        self.assertEqual(page.text_content("#book-count").strip(), "1")

        page.click("#generate")
        page.wait_for_selector("#estimate-dialog[open]", timeout=10000)
        self.assertIn(TITLE, page.inner_text("#estimate-scope"))
        self.assertIn("¥", page.inner_text("#estimate-cost"))
        self.assertNotEqual(page.inner_text("#estimate-input").strip(), "")
        page.click("#estimate-cancel")
        self.assertFalse(page.locator("#estimate-dialog[open]").count())

        page.click("details.book-menu summary")
        page.click("button[data-delete]")
        page.wait_for_selector("#delete-dialog[open]")
        self.assertIn(TITLE, page.inner_text("#delete-book-title"))
        page.click("#delete-confirm")
        page.wait_for_selector(".works-empty")
        self.assertEqual(page.text_content("#book-count").strip(), "0")
        self.assertEqual(page.text_content("#trash-count").strip(), "1")

        page.reload()
        page.wait_for_function(
            "document.getElementById('connection-text').textContent.includes('已就绪')"
        )
        page = self.open_library()
        page.wait_for_selector(".works-empty")
        self.assertEqual(page.text_content("#book-count").strip(), "0")

    def test_create_generate_save_and_reload_offline(self):
        """Scenario: a writer creates a book and recovers the generated chapter."""
        from memory_runtime.test_completion import Faults

        model = Faults()
        with (
            patch.object(service, "DATA", Path(self.folder.name) / "test-data"),
            patch.object(service, "_gateway", return_value=(model, None)),
        ):
            self.open_create_dialog()
            self.fill_create_form()
            self.page.click("#create-submit")
            self.page.wait_for_selector("#book-workspace")
            self.page.click("#generate")
            self.page.wait_for_selector("#estimate-dialog[open]")
            self.page.click("#estimate-continue")
            self.page.wait_for_function(
                "() => document.querySelector('#stat-chapters')?.textContent.includes('1 / 1')",
                timeout=30000,
            )
            self.page.wait_for_function(
                "() => document.querySelector('#book-list .book-row.selected small')?.textContent.includes('1 / 1')",
                timeout=4000,
            )
            self.page.wait_for_function(
                "() => Number(document.querySelector('#stat-units')?.textContent.replace(/,/g, '')) > 0",
                timeout=4000,
            )
            self.assertIn("甲", self.page.inner_text("#chapter-body"))
            self.assertTrue(any(request.role == "writer" for request in model.requests))
            book_id = self.page.locator("#export").get_attribute("href").split("/")[3]
            self.page.wait_for_load_state("networkidle")
            self.page.reload()
            self.page.wait_for_selector("#my-works")
            self.page.click("#my-works")
            self.page.locator(f'[data-book="{book_id}"]').first.click()
            self.page.wait_for_selector("#book-workspace")
            self.assertIn("甲", self.page.inner_text("#chapter-body"))
            self.page.wait_for_load_state("networkidle")

    def test_regeneration_requires_feedback_and_preserves_draft_on_failure(self):
        from memory_runtime.test_completion import Faults
        from tome_writer.models import ModelReply

        class RevisionModel(Faults):
            fail_revision = False

            def complete(self, request):
                revision = request.payload.get("chapter_revision")
                if request.role == "writer" and revision:
                    if self.fail_revision:
                        raise RuntimeError("simulated writer outage")
                    self.requests.append(request)
                    return ModelReply(
                        "甲把来信折好。雨声渐急，他决定当面问清楚。" * 85,
                        1,
                        1,
                        0,
                    )
                return super().complete(request)

        model = RevisionModel()
        with patch.object(service, "_gateway", return_value=(model, None)):
            self.open_create_dialog()
            self.fill_create_form()
            self.page.click("#create-submit")
            self.page.click("#generate")
            self.page.click("#estimate-continue")
            button = self.page.get_by_role("button", name="重新生成本章")
            button.wait_for()
            self.page.wait_for_function(
                "() => document.querySelector('#chapter-body')?.textContent.includes('走廊')"
            )
            old_text = self.page.inner_text("#chapter-body")
            book_id = self.page.locator("#export").get_attribute("href").split("/")[3]
            endpoint = f"{self.base}/api/books/{book_id}/chapters/1/regenerate"
            response = self.page.request.post(endpoint, data={"confirmed": True})
            self.assertEqual(response.status, 400)
            self.assertEqual(self.page.inner_text("#chapter-body"), old_text)

            model.fail_revision = True
            button.click()
            feedback = self.page.get_by_label("作者意见（必填）")
            submit = self.page.locator("#regenerate-submit")
            self.assertTrue(submit.is_disabled())
            feedback.fill("   ")
            self.assertTrue(submit.is_disabled())
            feedback.fill("保留来信，删掉走廊描写")
            submit.click()
            self.page.wait_for_function(
                "() => document.body.textContent.includes('第1章未生成正文')"
            )
            self.assertEqual(self.page.inner_text("#chapter-body"), old_text)
            saved = self.page.request.get(f"{self.base}/api/books/{book_id}").json()
            self.assertIn("走廊", saved["state"]["chapters"][0]["text"])

            model.fail_revision = False
            button.click()
            feedback.fill("保留来信，删掉走廊描写")
            submit.click()
            self.page.wait_for_function(
                "() => document.querySelector('#chapter-body')?.textContent.includes('把来信折好')"
            )
            revisions = [
                request
                for request in model.requests
                if request.payload.get("chapter_revision")
            ]
            self.assertEqual(
                {request.role for request in revisions}, {"planner", "writer"}
            )
            for request in revisions:
                revision = request.payload["chapter_revision"]
                self.assertEqual(revision["author_feedback"], "保留来信，删掉走廊描写")
                self.assertIn("走廊", revision["previous_draft"])
