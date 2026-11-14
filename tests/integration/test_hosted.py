"""Exercise registration, session boundaries and hosted data persistence."""

import http.client
import json
import tempfile
import threading
import unittest

from inf_backend.hosted import HostedServer

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


class HostedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.server = HostedServer(
            ("127.0.0.1", 0), "https://tome.example", self.temp.name
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=10)

    def request(
        self,
        path,
        data=None,
        cookie=None,
        origin="https://tome.example",
        host="tome.example",
    ):
        conn = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_port, timeout=30
        )
        headers = {"Host": host}
        if cookie:
            headers["Cookie"] = cookie
        if data is not None:
            headers.update({"Origin": origin, "Content-Type": "application/json"})
        try:
            conn.request(
                "POST" if data is not None else "GET",
                path,
                json.dumps(data) if data is not None else None,
                headers,
            )
            response = conn.getresponse()
            payload = response.read()
            return response.status, payload, response.getheader("Set-Cookie")
        finally:
            conn.close()

    def register(self, name):
        code, _, cookie = self.request(
            "/_account/register", {"username": name, "password": "strong-pass-123"}
        )
        self.assertEqual(code, 200)
        self.assertIn("HttpOnly", cookie)
        self.assertIn("Secure", cookie)
        return cookie.split(";", 1)[0]

    def test_auth_boundaries_and_user_isolation(self):
        self.assertEqual(self.request("/api/books")[0], 401)
        self.assertEqual(
            self.request("/_account/register", {}, origin="https://attacker.example")[
                0
            ],
            403,
        )
        self.assertEqual(self.request("/", host="attacker.example")[0], 403)
        first = self.register("writer_one")
        second = self.register("writer_two")
        code, body, _ = self.request(
            "/api/books",
            {"title": "私人作品", "prompt": "测试", "chapters": 1, "target_units": 500},
            first,
        )
        self.assertEqual(code, 201)
        book_id = json.loads(body)["state"]["project_id"]
        self.assertEqual(self.request(f"/api/books/{book_id}", cookie=second)[0], 404)
        self.assertEqual(
            json.loads(self.request("/api/books", cookie=second)[1])["books"], []
        )
        code, _, _ = self.request(
            "/api/model-config",
            {
                "provider": "compatible",
                "model": "x",
                "endpoint": "https://untrusted.example/chat/completions",
                "api_key": "sk-test",
            },
            first,
        )
        self.assertEqual(code, 400)
        self.assertEqual(self.request(f"/api/books/{book_id}", cookie=first)[0], 200)
        self.assertEqual(self.request("/_account/logout", {}, first)[0], 200)
        self.assertEqual(self.request("/api/books", cookie=first)[0], 401)

    def test_credentials_survive_account_store_reopen(self):
        cookie = self.register("writer_one")
        self.assertIsNotNone(
            self.server.accounts.resolve_session(cookie.split("=", 1)[1])
        )
        self.assertEqual(
            self.request(
                "/_account/login",
                {"username": "writer_one", "password": "wrong password"},
            )[0],
            401,
        )
        self.assertEqual(
            self.request(
                "/_account/login",
                {"username": "writer_one", "password": "strong-pass-123"},
            )[0],
            200,
        )

    def test_data_survives_service_restart(self):
        cookie = self.register("writer_one")
        code, body, _ = self.request(
            "/api/books",
            {
                "title": "重启后保留",
                "prompt": "测试",
                "chapters": 1,
                "target_units": 500,
            },
            cookie,
        )
        self.assertEqual(code, 201)
        book_id = json.loads(body)["state"]["project_id"]
        self.stop_server()
        self.server = HostedServer(
            ("127.0.0.1", 0), "https://tome.example", self.temp.name
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.assertEqual(self.request(f"/api/books/{book_id}", cookie=cookie)[0], 200)

    @unittest.skipUnless(sync_playwright, "Install playwright for browser tests")
    def test_browser_can_register_open_studio_and_log_out(self):
        # Chromium treats localhost as secure; production requires HTTPS.
        self.server.host = f"127.0.0.1:{self.server.server_port}"
        self.server.origin = f"http://{self.server.host}"
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(self.server.origin)
                self.assertEqual(page.title(), "登录 · Tome 故事工作室")
                self.assertEqual(
                    page.locator('input[name="password"]').get_attribute("minlength"),
                    "8",
                )
                self.assertNotEqual(
                    page.locator(".panel").evaluate(
                        "e => getComputedStyle(e).backgroundColor"
                    ),
                    "rgba(0, 0, 0, 0)",
                )
                page.get_by_role("button", name="显示密码").click()
                self.assertEqual(
                    page.locator('input[name="password"]').get_attribute("type"), "text"
                )
                page.get_by_role("button", name="隐藏密码").click()
                page.locator('input[name="username"]').fill("browser_writer")
                page.locator('input[name="password"]').fill("eight888")
                page.get_by_role("button", name="注册").click()
                page.wait_for_selector("#my-works")
                page.wait_for_selector("#settings-dialog .hosted-logout", state="attached")
                self.assertEqual(page.locator("#settings-dialog .hosted-logout").count(), 1)
                self.assertFalse(page.get_by_role("button", name="退出登录").is_visible())
                page.get_by_role("button", name="关闭模型服务设置").click()
                page.locator("#open-settings").click()
                self.assertTrue(page.get_by_role("button", name="退出登录").is_visible())
                for theme in ("light", "dark"):
                    page.locator(f'input[name="theme"][value="{theme}"]').check()
                    model = page.locator("#open-model-settings").bounding_box()
                    logout = page.locator(".hosted-logout").bounding_box()
                    self.assertAlmostEqual(model["width"], logout["width"], places=1)
                    self.assertAlmostEqual(model["height"], logout["height"], places=1)
                page.get_by_role("button", name="退出登录").click()
                page.wait_for_selector('input[name="username"]')
            finally:
                browser.close()
