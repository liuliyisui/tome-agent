"""Authenticated single-instance gateway for the hosted writing studio."""

import argparse
import http.client
import json
import os
import threading
import time
from collections import deque
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .accounts import AccountStore
from .hosted_workers import WorkerPool, WorkerUnavailable
from .logging_setup import configure_logging, log_failure, logger

LOGIN_PAGE = """<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tome 登录</title><body><main><h1>Tome 故事工作室</h1>
<p>使用账号密码登录，模型 API Key 在登录后单独配置。</p>
<p>用户名为 3～32 位英文字母、数字或下划线；密码为 15～128 位。</p>
<form id="account"><label>用户名 <input name="username" autocomplete="username" required></label>
<label>密码 <input name="password" type="password" minlength="15" maxlength="128"
autocomplete="current-password" required></label>
<button name="action" value="login">登录</button>
<button name="action" value="register">注册</button></form><p id="message"></p>
<script>
document.querySelector('#account').addEventListener('submit', async event => {
  event.preventDefault(); const form = event.currentTarget;
  const action = event.submitter.value;
  try { const response = await fetch('/_account/' + action, {method:'POST',
    headers:{'Content-Type':'application/json'}, body:JSON.stringify({
      username:form.username.value, password:form.password.value})});
    const result = await response.json();
    if (response.ok) location.assign('/');
    else document.querySelector('#message').textContent = result.error;
  } catch (_) { document.querySelector('#message').textContent = '连接失败，请稍后重试'; }
});</script></main></body></html>"""

LOGOUT_SCRIPT = """const b=document.createElement('button');b.type='button';b.textContent='退出登录';
b.addEventListener('click',async()=>{await fetch('/_account/logout',{method:'POST'});location.assign('/');});
const place=()=>{const target=document.querySelector('dialog[open]')||document.body;
  if(b.parentNode!==target)target.prepend(b);};
new MutationObserver(place).observe(document.documentElement,{subtree:true,childList:true,
  attributes:true,attributeFilter:['open']});place();""".encode()


class HostedServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, origin, data_home, worker_limit=3):
        parsed = urlsplit(origin)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.path not in ("", "/")
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("TOME_PUBLIC_ORIGIN 必须是 HTTPS 网站地址")
        self.origin = f"https://{parsed.netloc}"
        self.host = parsed.netloc.lower()
        home = Path(data_home).resolve()
        home.mkdir(parents=True, exist_ok=True)
        self.accounts = AccountStore(home / "accounts.sqlite3")
        self.workers = WorkerPool(home / "users", limit=worker_limit)
        self.auth_slots = threading.BoundedSemaphore(2)
        self.auth_attempts = deque()
        self.auth_lock = threading.Lock()
        self.model_hosts = {
            host.strip().lower()
            for host in os.environ.get(
                "TOME_MODEL_HOSTS",
                "api.deepseek.com,api.openai.com,dashscope.aliyuncs.com,"
                "open.bigmodel.cn,api.moonshot.cn,api.siliconflow.cn",
            ).split(",")
            if host.strip()
        }
        super().__init__(address, HostedHandler)

    def allow_auth(self):
        now = time.monotonic()
        with self.auth_lock:
            while self.auth_attempts and self.auth_attempts[0] < now - 60:
                self.auth_attempts.popleft()
            if len(self.auth_attempts) >= 60:
                return False
            self.auth_attempts.append(now)
            return True

    def server_close(self):
        super().server_close()
        self.workers.close()


class HostedHandler(BaseHTTPRequestHandler):
    def log_message(self, _format, *_args):
        # Request paths, cookies, and query strings may contain private data.
        pass

    def respond(
        self, code, body, content_type="application/json; charset=utf-8", cookie=None
    ):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'",
        )
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def session(self):
        try:
            cookie = SimpleCookie(self.headers.get("Cookie", ""))
            return cookie["tome_session"].value if "tome_session" in cookie else ""
        except Exception:
            return ""

    def do_GET(self):
        self.dispatch(False)

    def do_POST(self):
        self.dispatch(True)

    def dispatch(self, post):
        if self.headers.get("Host", "").lower() != self.server.host:
            self.respond(403, {"error": "访问地址不匹配"})
            return
        if post and self.headers.get("Origin", "") != self.server.origin:
            self.respond(403, {"error": "请求来源无效"})
            return
        path = urlsplit(self.path).path
        try:
            if path == "/healthz" and not post:
                self.respond(200, {"status": "ok"})
                return
            if post and path in {"/_account/login", "/_account/register"}:
                self.account(path)
                return
            token = self.session()
            user_id = self.server.accounts.resolve_session(token)
            if post and path == "/_account/logout":
                self.server.accounts.revoke_session(token)
                self.respond(
                    200,
                    {"ok": True},
                    cookie="tome_session=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Strict",
                )
                return
            if not user_id:
                if not post and path == "/":
                    self.respond(200, LOGIN_PAGE.encode(), "text/html; charset=utf-8")
                else:
                    self.respond(401, {"error": "请先登录"})
                return
            if not post and path == "/_account/logout.js":
                self.respond(200, LOGOUT_SCRIPT, "text/javascript; charset=utf-8")
                return
            self.proxy(user_id, post, path)
        except (ValueError, json.JSONDecodeError):
            self.respond(400, {"error": "请求格式或内容无效"})
        except WorkerUnavailable:
            self.respond(503, {"error": "服务繁忙，请稍后重试"})
        except Exception as exc:
            log_failure("Hosted request", exc)
            self.respond(500, {"error": "操作失败，请稍后重试"})

    def read_body(self, limit):
        raw_length = self.headers.get("Content-Length", "0")
        if not raw_length.isdecimal() or int(raw_length) > limit:
            raise ValueError("请求大小无效")
        return self.rfile.read(int(raw_length))

    def account(self, path):
        if not self.server.allow_auth() or not self.server.auth_slots.acquire(
            blocking=False
        ):
            self.respond(429, {"error": "请求过于频繁，请稍后重试"})
            return
        try:
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("请求格式无效")
            data = json.loads(self.read_body(4096))
            if not isinstance(data, dict):
                raise ValueError("请求格式无效")
            username, password = data.get("username"), data.get("password")
            if path.endswith("register"):
                user_id = self.server.accounts.register(username, password)
            else:
                user_id = self.server.accounts.authenticate(username, password)
                if not user_id:
                    self.respond(401, {"error": "用户名或密码错误"})
                    return
            token = self.server.accounts.create_session(user_id)
            self.respond(
                200,
                {"ok": True},
                cookie=f"tome_session={token}; Path=/; Max-Age=86400; HttpOnly; Secure; SameSite=Strict",
            )
        finally:
            self.server.auth_slots.release()

    def proxy(self, user_id, post, path):
        body = self.read_body(2_800_100) if post else None
        if post and path in ("/api/model-config", "/api/model-test"):
            config = json.loads(body)
            if not isinstance(config, dict):
                raise ValueError("请求格式无效")
            if config.get("provider") == "compatible":
                endpoint = urlsplit(config.get("endpoint", ""))
                if endpoint.hostname not in self.server.model_hosts:
                    raise ValueError("模型服务商未在服务器允许列表中")
        port = self.server.workers.get(user_id)
        host = f"127.0.0.1:{port}"
        headers = {"Host": host}
        if post:
            headers["Origin"] = f"http://{host}"
            headers["Content-Type"] = self.headers.get("Content-Type", "")
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=60)
        try:
            connection.request("POST" if post else "GET", self.path, body, headers)
            response = connection.getresponse()
            payload = response.read()
            if not post and path == "/" and response.status == 200:
                payload = payload.replace(
                    b"</body>", b'<script src="/_account/logout.js"></script></body>'
                )
            self.send_response(response.status)
            for name in (
                "Content-Type",
                "Content-Disposition",
                "Content-Security-Policy",
                "X-Content-Type-Options",
            ):
                value = response.getheader(name)
                if value:
                    self.send_header(name, value)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)
        finally:
            connection.close()
            self.server.workers.release(user_id)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    origin = os.environ["TOME_PUBLIC_ORIGIN"]
    home = os.environ["TOME_DATA_HOME"]
    worker_limit = int(os.environ.get("TOME_WORKER_LIMIT", "3"))
    if not 1 <= worker_limit <= 8:
        raise ValueError("TOME_WORKER_LIMIT 必须在 1 到 8 之间")
    configure_logging(Path(home) / "logs", "hosted.log")
    server = HostedServer(("127.0.0.1", args.port), origin, home, worker_limit)
    logger.info("Hosted server started")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        logger.info("Hosted server stopped")


if __name__ == "__main__":
    main()
