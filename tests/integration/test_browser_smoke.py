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

from inf_backend import official_pricing, service
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
        self.key_patch = patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-" + "a" * 32})
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

    def test_home_and_empty_library(self):
        page = self.page
        self.assertEqual(page.title(), "Tome · 故事工作室")
        page.wait_for_selector("#welcome")

        page = self.open_library()
        page.wait_for_selector(".works-empty")
        self.assertIn("书架还是空的", page.inner_text(".works-empty"))
        self.assertEqual(page.text_content("#book-count").strip(), "0")

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
