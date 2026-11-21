"""Browser smoke tests for the local UI.

Skipped unless Playwright and its Chromium build are installed. Install with:

    code/backend/.venv/Scripts/python.exe -m pip install playwright
    code/backend/.venv/Scripts/python.exe -m playwright install chromium

The suite never calls the model: it only exercises page load, book creation,
the cost-estimate dialog, deletion and refresh persistence.
"""

import json
import os
import tempfile
import threading
import time
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
    def test_brand_returns_home_and_refresh_stays_home(self):
        service.create_book("home-link", "返回首页测试", "故事", 3, 3000)
        self.open_library()
        self.page.locator('[data-book="home-link"]').click()
        self.page.get_by_role("heading", name="返回首页测试").wait_for()
        self.page.get_by_role("link", name="Tome 首页").click()
        self.page.wait_for_function(
            "() => document.querySelector('#tome-app > div')?.classList.contains('home-view')"
        )
        self.page.reload()
        self.page.wait_for_function(
            "() => document.querySelector('#tome-app > div')?.classList.contains('home-view')"
        )
        self.assertFalse(self.page.locator("#book-title").is_visible())

    def test_reload_restores_open_book(self):
        service.create_book("resume-view", "刷新测试", "故事", 3, 3000)
        self.open_library()
        self.page.locator('[data-book="resume-view"]').click()
        self.page.get_by_role("heading", name="刷新测试").wait_for()
        self.page.add_init_script("""(() => {
            const original = window.fetch;
            window.fetch = async (...args) => {
                if (String(args[0]) === '/api/config')
                    await new Promise(resolve => setTimeout(resolve, 1200));
                return original(...args);
            };
        })();""")
        self.page.reload(wait_until="domcontentloaded")
        root = self.page.locator("#tome-app > div")
        root.wait_for(state="attached")
        self.assertTrue(root.is_hidden())
        self.page.get_by_role("heading", name="刷新测试").wait_for()
        self.assertTrue(root.is_visible())
        self.assertTrue(self.page.locator("#book-title").is_visible())

    def test_reload_restores_selected_chapter(self):
        service.create_book("resume-chapter", "章节测试", "故事", 3, 3000)

        def chapters(route):
            response = route.fetch()
            data = response.json()
            data["state"]["chapters"] = [
                {"number": 1, "title": "第一章", "text": "第一章正文"},
                {"number": 2, "title": "第二章", "text": "第二章正文"},
            ]
            route.fulfill(response=response, body=json.dumps(data, ensure_ascii=False))

        self.page.route("**/api/books/resume-chapter", chapters)
        self.open_library()
        self.page.locator('[data-book="resume-chapter"]').click()
        self.page.get_by_role("button", name="下一章", exact=True).first.click()
        self.assertIn("第二章正文", self.page.locator("#chapter-body").inner_text())
        self.page.reload()
        self.page.wait_for_function(
            "() => document.querySelector('#chapter-body')?.textContent.includes('第二章正文')"
        )
        self.page.wait_for_load_state("networkidle")

    def test_book_page_shows_unresolved_closure(self):
        service.create_book("closure-ui", "收束测试", "故事", 3, 3000)

        def add_closure(route):
            response = route.fetch()
            data = response.json()
            data["state"]["story_closure"] = {
                "status": "UNRESOLVED",
                "mainline_passed": True,
                "pending_threads": [{"topic": "失踪的信", "reason": "去向尚未交代"}],
            }
            route.fulfill(response=response, body=json.dumps(data, ensure_ascii=False))

        self.page.route("**/api/books/closure-ui", add_closure)
        self.open_library()
        self.page.locator('[data-book="closure-ui"]').click()
        panel = self.page.get_by_label("故事收束状态")
        self.assertFalse(panel.evaluate("el => el.open"))
        panel.locator("summary").click()
        self.assertTrue(panel.evaluate("el => el.open"))
        self.assertIn("还有重要线索需要处理", panel.inner_text())
        self.assertIn("失踪的信", panel.inner_text())
        self.assertIn("去向尚未交代", panel.inner_text())
        self.assertEqual(
            panel.evaluate("el => el.parentElement.className"), "writing-aside"
        )
        for heading in ("文风设定", "写作 Skill"):
            section = self.page.locator("details.style-panel").filter(
                has=self.page.get_by_role("heading", name=heading)
            )
            self.assertFalse(section.evaluate("el => el.open"))
            section.locator("summary").click()
            self.assertTrue(section.evaluate("el => el.open"))

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

    @staticmethod
    def _await_generate(mock, timeout=5.0):
        """service.generate 在后台线程中调用，轮询直到它被记录。"""
        deadline = time.time() + timeout
        while mock.call_args is None and time.time() < deadline:
            time.sleep(0.05)
        return mock.call_args

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

    def test_privacy_prompt_requires_confirmation_and_hides_sensitive_values(self):
        with patch.object(service, "generate") as generate:
            self.open_create_dialog()
            self.fill_create_form()
            self.page.fill(
                'textarea[name="prompt"]', "写一封给 writer@example.test 的信"
            )
            self.page.click("#create-submit")
            self.page.click("#generate")
            self.page.wait_for_selector("#estimate-dialog[open] .privacy-review")
            panel = self.page.locator("#estimate-dialog .privacy-review")
            self.assertIn("邮箱地址", panel.inner_text())
            self.assertNotIn("writer@example.test", panel.inner_text())
            button = self.page.locator("#estimate-continue")
            self.assertTrue(button.is_disabled())
            generate.assert_not_called()
            checkbox = panel.get_by_role("checkbox")
            checkbox.focus()
            self.page.keyboard.press("Space")
            self.assertTrue(button.is_enabled())
            button.click()
            self.page.wait_for_selector(
                "#estimate-dialog:not([open])", state="attached"
            )
            self.assertTrue(self._await_generate(generate).kwargs["privacy_confirmed"])

    def test_privacy_secret_blocks_generation_even_in_dark_theme(self):
        self.page.emulate_media(color_scheme="dark")
        with patch.object(service, "generate") as generate:
            self.open_create_dialog()
            self.fill_create_form()
            self.page.fill(
                'textarea[name="prompt"]',
                "误粘贴 sk-FAKE_SECRET_ONLY_FOR_TESTS_1234567890",
            )
            self.page.click("#create-submit")
            self.page.click("#generate")
            panel = self.page.locator("#estimate-dialog .privacy-blocked")
            panel.wait_for()
            self.assertIn("疑似密钥", panel.inner_text())
            self.assertNotIn("FAKE_SECRET", panel.inner_text())
            self.assertEqual(panel.get_by_role("checkbox").count(), 0)
            self.assertTrue(self.page.locator("#estimate-continue").is_disabled())
            generate.assert_not_called()

    def test_regeneration_feedback_privacy_check_can_be_reviewed_and_reset(self):
        from memory_runtime.test_completion import Faults

        with patch.object(service, "_gateway", return_value=(Faults(), None)):
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
            with patch.object(service, "generate") as generate:
                button.click()
                feedback = self.page.locator("#regenerate-feedback")
                feedback.fill("给 writer@example.test 写信")
                self.page.click("#regenerate-submit")
                panel = self.page.locator("#regenerate-dialog .privacy-review")
                panel.wait_for()
                self.assertIn("本次作者意见", panel.inner_text())
                self.assertNotIn("writer@example.test", panel.inner_text())
                self.assertTrue(self.page.locator("#regenerate-submit").is_disabled())
                generate.assert_not_called()
                panel.get_by_role("checkbox").check()
                self.assertTrue(self.page.locator("#regenerate-submit").is_enabled())
                feedback.fill("只调整对白")
                self.assertEqual(
                    self.page.locator("#regenerate-dialog .privacy-review").count(), 0
                )
                self.page.click("#regenerate-submit")
                self.page.wait_for_selector(
                    "#regenerate-dialog:not([open])", state="attached"
                )
                self.assertIs(
                    self._await_generate(generate).kwargs["privacy_confirmed"], False
                )

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
        self.assertEqual(page.locator("#estimate-dialog .privacy-review").count(), 0)
        self.assertTrue(page.locator("#estimate-continue").is_enabled())
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

    def test_trash_opens_while_list_request_is_pending(self):
        page = self.open_library()
        page.wait_for_load_state("networkidle")
        intercepted = []
        shelf_requests = []
        page.route("**/api/books/trash", lambda route: intercepted.append(route))

        def track_shelf(route):
            shelf_requests.append(route.request.url)
            route.continue_()

        page.route("**/api/books", track_shelf)
        with page.expect_request("**/api/books/trash"):
            page.click("#trash-open")
        page.locator("#trash-dialog[open]").wait_for(timeout=2000)
        page.locator("#trash-loading").wait_for()
        self.assertEqual(page.locator(".trash-empty").count(), 0)
        page.keyboard.press("Escape")
        page.locator("#trash-dialog").wait_for(state="hidden")

        # Reopening during an outstanding refresh reuses it.
        page.click("#trash-open")
        page.locator("#trash-loading").wait_for()
        self.assertEqual(len(intercepted), 1)
        intercepted.pop().fulfill(status=503, json={"error": "暂时不可用"})
        page.locator(".trash-load-error").wait_for()
        with page.expect_request("**/api/books/trash"):
            page.get_by_role("button", name="重试", exact=True).click()
        intercepted.pop().fulfill(
            json={
                "books": [
                    {
                        "title": "旧稿",
                        "restore_token": "test-token",
                        "deleted_at": "2026-11-21T00:00:00Z",
                    }
                ]
            }
        )
        page.locator(".trash-book", has_text="旧稿").wait_for()
        self.assertEqual(page.locator("#trash-loading").count(), 0)
        self.assertEqual(page.text_content("#trash-count").strip(), "1")
        self.assertEqual(shelf_requests, [])

    def test_book_menu_escapes_shelf_clipping_and_keeps_pin_keyboard_actions(self):
        self.page.set_viewport_size({"width": 1280, "height": 600})
        for number in range(8):
            service.create_book(
                f"menu-book-{number}",
                f"浮层测试作品{number}",
                "测试",
                2,
                2000,
                settings=settings.Settings(api_key="FAKE_TEST_KEY"),
            )
        page = self.page
        page.reload()
        page.click("#my-works")
        trigger = page.locator("#book-list .book-row").last.locator("summary")
        trigger_id = trigger.get_attribute("id")
        trigger = page.locator("#" + trigger_id)
        menu_id = trigger.get_attribute("aria-controls")
        book_id = menu_id.removeprefix("book-actions-")
        trigger.scroll_into_view_if_needed()
        trigger.click()
        menu = page.locator("#" + menu_id)
        menu.wait_for()
        self.assertTrue(menu.evaluate("el => el.parentElement === document.body"))
        menu_box = menu.bounding_box()
        shelf_box = page.locator("#book-list").bounding_box()
        self.assertGreater(
            menu_box["y"] + menu_box["height"], shelf_box["y"] + shelf_box["height"]
        )
        delete_button = menu.locator("[data-delete]")
        self.assertTrue(
            delete_button.evaluate(
                "el => {const r=el.getBoundingClientRect();return el.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))}"
            )
        )
        page.keyboard.press("Escape")
        menu.wait_for(state="detached")
        self.assertEqual(trigger.get_attribute("aria-expanded"), "false")
        self.assertEqual(
            page.evaluate("() => document.activeElement.id"),
            trigger_id,
        )
        trigger.click()
        menu.locator("[data-pin]").click()
        menu.wait_for(state="detached")
        page.locator(f'#book-list [data-book="{book_id}"] .pin-mark').wait_for()
        trigger.click()
        menu.wait_for()
        page.click("#my-works")
        menu.wait_for(state="detached")
        page.wait_for_load_state("networkidle")

    def test_shelf_scrolls_only_for_real_book_content(self):
        page = self.page
        page.set_viewport_size({"width": 1280, "height": 900})
        for number in range(3):
            service.create_book(
                f"scroll-book-{number}",
                f"滚动测试{number}",
                "测试",
                2,
                2000,
                settings=settings.Settings(api_key="FAKE_TEST_KEY"),
            )
        page.reload()
        page.click("#my-works")
        page.wait_for_function(
            "() => document.querySelectorAll('#book-list .book-row').length === 3"
        )
        shelf = page.locator("#book-list")
        self.assertTrue(shelf.evaluate("el => el.scrollHeight <= el.clientHeight + 1"))
        for number in range(3, 18):
            service.create_book(
                f"scroll-book-{number}",
                f"滚动测试{number}",
                "测试",
                2,
                2000,
                settings=settings.Settings(api_key="FAKE_TEST_KEY"),
            )
        page.click("#my-works")
        page.wait_for_function(
            "() => document.querySelectorAll('#book-list .book-row').length === 18"
        )
        self.assertTrue(shelf.evaluate("el => el.scrollHeight > el.clientHeight"))
        gap = shelf.evaluate(
            "el => {el.scrollTop=el.scrollHeight;return el.getBoundingClientRect().bottom-el.lastElementChild.getBoundingClientRect().bottom}"
        )
        self.assertLessEqual(abs(gap), 1.5)
        page.set_viewport_size({"width": 375, "height": 812})
        self.assertTrue(shelf.evaluate("el => el.scrollHeight <= el.clientHeight + 1"))
        page.wait_for_load_state("networkidle")

    def test_local_editor_restores_draft_applies_review_and_exports_new_prose(self):
        from memory_runtime.test_completion import Faults

        with patch.object(service, "_gateway", return_value=(Faults(), None)):
            self.open_create_dialog()
            self.fill_create_form()
            self.page.click("#create-submit")
            self.page.click("#generate")
            self.page.click("#estimate-continue")
            self.page.wait_for_function(
                "() => document.querySelector('#chapter-body')?.textContent.includes('走廊')"
            )
        page = self.page
        page.locator("#edit-chapter").click()
        editor = page.locator("#chapter-edit-text")
        editor.fill("他迫不急待地走出武馆。")
        page.get_by_role("button", name="本地复查", exact=True).click()
        page.get_by_role("button", name="采用建议：迫不及待", exact=True).click()
        self.assertEqual(editor.input_value().strip(), "他迫不及待地走出武馆。")
        page.reload()
        page.click("#my-works")
        page.locator("[data-book]").first.click()
        page.click("#edit-chapter")
        self.assertEqual(editor.input_value().strip(), "他迫不及待地走出武馆。")
        page.get_by_role("button", name="复查并保存", exact=True).click()
        page.locator("#chapter-editor").wait_for(state="detached")
        self.assertIn("他迫不及待地走出武馆。", page.inner_text("#chapter-body"))
        page.click("#export")
        page.locator("#export-review-dialog[open]").wait_for()
        with page.expect_download() as pending:
            page.click("#confirm-reviewed-export")
        downloaded = Path(pending.value.path()).read_text(encoding="utf-8")
        self.assertIn("他迫不及待地走出武馆。", downloaded)
        self.assertNotIn("本地规则未发现问题", downloaded)
        page.wait_for_load_state("networkidle")

    def test_local_editor_locates_private_information_and_blocks_secret(self):
        from memory_runtime.test_completion import Faults

        with patch.object(service, "_gateway", return_value=(Faults(), None)):
            self.open_create_dialog()
            self.fill_create_form()
            self.page.click("#create-submit")
            self.page.click("#generate")
            self.page.click("#estimate-continue")
            self.page.wait_for_function(
                "() => document.querySelector('#chapter-body')?.textContent.includes('走廊')"
            )
        page = self.page
        page.click("#edit-chapter")
        editor = page.locator("#chapter-edit-text")
        editor.fill(
            "\n".join(f"甲在第{i}天走过武馆。" for i in range(200))
            + "\n他迫不急待地出发。"
        )
        editor.evaluate("el => {el.setSelectionRange(0,0);el.scrollTop=0}")
        page.get_by_role("button", name="本地复查", exact=True).click()
        page.locator(".editor-workspace .proofreading-results").get_by_role(
            "button", name="定位修改", exact=True
        ).click()
        self.assertGreater(
            page.locator(".editor-scroll").evaluate("el => el.scrollTop"), 0
        )
        editor.fill("😀开场。\n电话 13800138000。")
        page.get_by_role("button", name="本地复查", exact=True).click()
        panel = page.locator(".editor-workspace .proofreading-results")
        panel.wait_for()
        self.assertNotIn("13800138000", panel.inner_text())
        panel.get_by_role("button", name="定位修改", exact=True).click()
        self.assertEqual(
            editor.evaluate("el => el.value.slice(el.selectionStart,el.selectionEnd)"),
            "13800138000",
        )
        self.assertTrue(
            page.get_by_role("button", name="复查并保存", exact=True).is_disabled()
        )
        panel.get_by_role("checkbox").check()
        self.assertTrue(
            page.get_by_role("button", name="复查并保存", exact=True).is_enabled()
        )
        editor.fill("误贴 sk-FAKE_SECRET_FOR_LOCAL_REVIEW_1234567890")
        page.get_by_role("button", name="本地复查", exact=True).click()
        page.locator(".editor-workspace .message-danger").wait_for()
        self.assertTrue(
            page.get_by_role("button", name="复查并保存", exact=True).is_disabled()
        )
        page.set_viewport_size({"width": 375, "height": 812})
        self.assertFalse(
            page.evaluate("() => document.documentElement.scrollWidth > innerWidth")
        )
        page.wait_for_load_state("networkidle")

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
            notes = self.page.locator(".writing-notes")
            notes.wait_for()
            notes.get_by_text("查看章节安排", exact=True).click()
            self.assertNotIn("修改说明", notes.inner_text())
            self.assertNotIn("完成记录", notes.inner_text())
            self.assertNotIn("本次写作要求", notes.inner_text())
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
            notes = self.page.locator(".writing-notes")
            if not notes.locator(".writing-notes-details").evaluate("el => el.open"):
                notes.get_by_text("查看章节安排与修改对照").click()
            self.assertIn("本次作者意见：保留来信，删掉走廊描写", notes.inner_text())
            self.assertIn("与原稿相比", notes.inner_text())
            self.assertGreater(notes.locator(".revision-example").count(), 0)
            self.page.reload()
            self.page.click("#my-works")
            self.page.locator(f'[data-book="{book_id}"]').first.click()
            notes = self.page.locator(".writing-notes")
            notes.get_by_text("查看章节安排与修改对照").click()
            self.assertIn("保留来信，删掉走廊描写", notes.inner_text())
            self.assertNotIn(
                "写作摘要与修改说明", self.page.inner_text("#chapter-body")
            )
            self.page.set_viewport_size({"width": 375, "height": 812})
            self.assertFalse(
                self.page.evaluate("document.documentElement.scrollWidth > innerWidth")
            )
            self.page.wait_for_load_state("networkidle")
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

    def test_memory_folders_search_and_chapter_directory(self):
        """Search/navigation is local, literal and keyboard usable under the page CSP."""
        import json

        service.create_book(
            "directory-test",
            "目录测试",
            "测试",
            12,
            2000,
            settings=settings.Settings(api_key="FAKE_TEST_KEY"),
        )
        rows = [
            {
                "number": n,
                "title": "雷火武馆的退师之日" if n == 1 else f"归途与重逢{n}",
                "text": "  🦊韩老三递出了[a+b]。\\n\\n  林渊说：<img src=x onerror=alert(1)>。"
                if n == 4
                else "韩老三在雷火武馆等候。",
            }
            for n in range(1, 9)
        ]

        def fact(subject, attribute, number=1, kind="state", quote="韩老三"):
            return {
                "subject": subject,
                "attribute": attribute,
                "value": quote,
                "kind": kind,
                "status": "active",
                "revision": 1,
                "source": {"chapter_number": number, "quote": quote},
            }

        data = {
            "metadata": {
                "title": "目录测试",
                "prompt": "测试",
                "target_chapters": 12,
                "target_units": 2000,
                "model": {"model": "offline-test"},
            },
            "mode": "longform",
            "style": {},
            "skills": [],
            "edit_revision": "test",
            "writing_notes": {},
            "state": {
                "project_id": "directory-test",
                "chapters": rows,
                "revision": 8,
                "facts": {
                    "person": fact("韩老三", "身份"),
                    "relation": fact("林渊与夏老爷的关系", "关系"),
                    "place": fact("雷火武馆", "地点"),
                    "prose": fact(
                        "prose:c0004.a", "excerpt", 4, "prose_excerpt", "林渊说"
                    ),
                    "event": fact("event:c0001.a", "event", kind="event"),
                },
            },
        }
        page = self.page
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.route(
            "**/api/books/directory-test",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(data, ensure_ascii=False),
            ),
        )
        page.reload()
        page.click("#my-works")
        page.locator('[data-book="directory-test"]').first.click()
        page.locator("#chapter-picker-trigger").wait_for()
        self.assertEqual(page.locator("#chapter-tabs select").count(), 0)
        self.assertEqual(page.locator(".memory-folder").count(), 4)
        self.assertNotIn("event:", page.inner_text(".memory-directory"))
        page.get_by_text("人物卡", exact=True).click()
        page.locator(".memory-topics button", has_text="韩老三").click()
        self.assertIn("韩老三", page.inner_text(".memory-selected-title"))
        page.locator("#facts .fact-locate").click()
        self.assertEqual(page.inner_text("#chapter-body mark"), "韩老三")

        page.click("#chapter-picker-trigger")
        page.locator("#chapter-filter").wait_for()
        self.assertNotEqual(
            page.locator("#chapter-directory").evaluate(
                "(menu) => getComputedStyle(menu).backgroundColor"
            ),
            "rgba(0, 0, 0, 0)",
        )
        trigger = page.locator("#chapter-picker-trigger").bounding_box()
        menu = page.locator("#chapter-directory").bounding_box()
        self.assertAlmostEqual(menu["x"], trigger["x"], delta=1)
        self.assertAlmostEqual(menu["width"], trigger["width"], delta=1)
        page.fill("#chapter-filter", "4")
        self.assertEqual(page.locator(".chapter-directory-list button").count(), 1)
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        page.wait_for_function(
            "() => document.querySelector('#chapter-body h3').textContent.includes('第4章')"
        )
        self.assertEqual(page.locator("#chapter-directory").count(), 0)
        self.assertEqual(page.locator("#chapter-body img").count(), 0)
        self.assertIn("<img", page.inner_text("#chapter-body"))
        page.click("#chapter-picker-trigger")
        page.keyboard.press("Escape")
        self.assertEqual(page.locator("#chapter-directory").count(), 0)
        self.assertEqual(
            page.evaluate("document.activeElement.id"), "chapter-picker-trigger"
        )

        page.locator(".book-search>summary").click()
        page.fill("#book-search-query", "[a+b]")
        page.press("#book-search-query", "Enter")
        page.locator(".search-result").wait_for()
        self.assertEqual(page.locator(".search-result").count(), 1)
        page.click(".search-result")
        self.assertEqual(page.inner_text("#chapter-body mark"), "[a+b]")
        page.fill("#book-search-query", "重逢4")
        page.press("#book-search-query", "Enter")
        page.click(".search-result")
        self.assertEqual(page.inner_text("#chapter-body h3 mark"), "重逢4")
        page.fill("#book-search-query", "韩老三")
        page.press("#book-search-query", "Enter")
        self.assertEqual(page.locator(".search-result").count(), 8)
        page.locator(".search-result").first.click()
        self.assertIn("第1章", page.inner_text("#chapter-body h3"))
        page.fill("#book-search-query", "没有这句话")
        page.press("#book-search-query", "Enter")
        self.assertIn("没有找到匹配文字", page.inner_text(".book-search-results"))
        page.fill("#memory-filter", "林渊")
        self.assertEqual(page.locator(".memory-topics button").count(), 1)
        self.assertIn("人物关系", page.inner_text(".memory-directory"))
        page.fill("#memory-filter", "")
        page.screenshot(
            path=str(Path(os.environ["TEMP"]) / "tome-memory-search-light.png"),
            full_page=True,
        )
        page.emulate_media(color_scheme="dark")
        page.set_viewport_size({"width": 390, "height": 844})
        page.click("#chapter-picker-trigger")
        picker = page.locator("#chapter-directory").bounding_box()
        self.assertGreaterEqual(picker["x"], 0)
        self.assertLessEqual(picker["x"] + picker["width"], 390)
        page.fill("#chapter-filter", "重逢")
        self.assertEqual(page.locator(".chapter-directory-list button").count(), 7)
        page.screenshot(
            path=str(Path(os.environ["TEMP"]) / "tome-chapter-directory-mobile.png")
        )
        page.keyboard.press("Escape")
        self.assertFalse(
            page.evaluate("document.documentElement.scrollWidth > innerWidth")
        )
        page.wait_for_load_state("networkidle")
        self.assertEqual(errors, [])

    def test_large_generation_batch_warns_and_can_be_cancelled_or_confirmed(self):
        """Four chapters prompt for confirmation; three chapters remain unchanged."""
        import json

        service.create_book(
            "batch-warning",
            "批量提醒测试",
            "测试",
            6,
            2000,
            settings=settings.Settings(api_key="FAKE_TEST_KEY"),
        )
        from inf_backend.web import load_view

        book = load_view("batch-warning")
        book["state"]["chapters"] = [
            {"number": 1, "title": "开始", "text": "已保存的正文。"}
        ]
        page = self.page
        submitted = []
        page.route("**/api/books/batch-warning", lambda route: route.fulfill(json=book))

        def estimate(route):
            count = route.request.post_data_json["count"]
            route.fulfill(
                json={
                    "book_id": "batch-warning",
                    "estimate_id": "test-estimate",
                    "count": count,
                    "first_chapter": 2,
                    "last_chapter": count + 1,
                    "pricing": {},
                    "safety": {"blocked": False},
                }
            )

        def generate(route):
            submitted.append(json.loads(route.request.post_data))
            route.fulfill(json={"job_id": "batch-test-job"})

        page.route("**/api/books/batch-warning/estimate", estimate)
        page.route("**/api/books/batch-warning/generate", generate)
        page.route(
            "**/api/jobs/batch-test-job",
            lambda route: route.fulfill(
                json={"status": "completed", "count": 4, "completed": 4}
            ),
        )
        page.reload()
        page.click("#my-works")
        page.locator('[data-book="batch-warning"]').first.click()
        page.check("#approve-first")
        page.fill("#generation-count", "3")
        self.assertEqual(page.locator("#batch-size-warning").count(), 0)
        page.click("#generate")
        page.locator("#estimate-dialog[open]").wait_for()
        self.assertEqual(page.locator("#estimate-batch-warning").count(), 0)
        page.click("#estimate-cancel")
        page.fill("#generation-count", "4")
        self.assertIn("章节数较多", page.inner_text("#batch-size-warning"))
        page.click("#generate")
        page.locator("#estimate-batch-warning").wait_for()
        self.assertIn("是否继续生成", page.inner_text("#estimate-batch-warning"))
        self.assertEqual(submitted, [])
        self.assertEqual(page.inner_text("#estimate-cancel"), "返回调整")
        page.click("#estimate-cancel")
        self.assertEqual(page.input_value("#generation-count"), "4")
        self.assertEqual(submitted, [])
        page.click("#generate")
        page.locator("#estimate-batch-warning").wait_for()
        page.click("#estimate-continue")
        page.locator("#estimate-dialog[open]").wait_for(state="hidden")
        self.assertEqual(len(submitted), 1)
        self.assertTrue(submitted[0]["confirmed"])
        page.wait_for_load_state("networkidle")
