"""Authenticated single-instance gateway for the hosted writing studio."""

import argparse
import base64
import hashlib
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

LOGIN_STYLE = """
:root{color-scheme:light;--ink:#193d32;--muted:#63775f;--line:#d9dfcf;--paper:#f8f7f2;--field:#fffefa}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,"Microsoft YaHei",sans-serif}
main{min-height:100vh;display:grid;grid-template-columns:minmax(0,1fr) minmax(340px,480px);gap:70px;align-items:center;max-width:1120px;margin:auto;padding:64px 44px}
.intro{padding:30px 0}.brand{font-size:13px;letter-spacing:.22em;color:var(--muted)}.mark{width:46px;height:2px;background:#ba9665;margin:36px 0 25px}
h1{font-family:Georgia,"Songti SC",serif;font-size:clamp(38px,5vw,62px);font-weight:400;line-height:1.2;margin:0 0 22px;letter-spacing:.03em}
.intro p{color:var(--muted);line-height:1.9;max-width:390px;margin:0}.panel{background:#fffefa;border:1px solid var(--line);padding:40px;border-radius:8px;box-shadow:0 14px 45px rgba(28,51,38,.05)}
.panel h2{font-family:Georgia,"Songti SC",serif;font-size:28px;font-weight:400;margin:0 0 10px}.hint{color:var(--muted);font-size:14px;line-height:1.7;margin:0 0 28px}
label{display:block;font-size:14px;font-weight:600;margin:20px 0 8px}input{width:100%;min-width:0;padding:13px 14px;border:1px solid #ccd6c4;border-radius:5px;background:var(--field);color:var(--ink);font:inherit;outline:none}
input:focus-visible,button:focus-visible{outline:3px solid #bc9d6f;outline-offset:2px}.password-row{display:flex;gap:8px}.password-row button{white-space:nowrap;border:1px solid #ccd6c4;background:transparent;color:var(--ink);padding:0 14px;border-radius:5px;cursor:pointer}
.field-hint{display:block;color:var(--muted);font-size:12px;line-height:1.6;margin-top:7px}.actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:26px}.actions button{min-height:48px;border-radius:5px;border:1px solid #285645;cursor:pointer;font:inherit;font-weight:600}.primary{background:#285645;color:white}.secondary{background:transparent;color:#285645}.actions button:disabled{opacity:.6;cursor:wait}
#message{min-height:1.5em;color:#a33329;font-size:14px;margin:14px 0 0}.note{font-size:12px;color:var(--muted);line-height:1.7;margin:20px 0 0}
.admin-user{margin-bottom:18px}
@media(max-width:720px){main{display:block;padding:34px 20px}.intro{padding:0 0 28px}.mark{margin:22px 0 18px}h1{font-size:38px}.panel{padding:28px 22px}}
"""
LOGIN_STYLE_HASH = base64.b64encode(
    hashlib.sha256(LOGIN_STYLE.encode()).digest()
).decode()
LOGIN_PAGE = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>登录 · Tome 故事工作室</title><style>{LOGIN_STYLE}</style></head><body><main>
<section class="intro"><div class="brand">TOME · 故事工作室</div><div class="mark"></div>
<h1>让故事，<br>从这里继续。</h1><p>登录你的创作空间，保存灵感与章节，让每个故事都有继续的地方。</p></section>
<section class="panel" aria-labelledby="account-title"><h2 id="account-title">进入工作室</h2>
<p class="hint" id="account-hint">使用已有账号登录，继续你的创作。</p>
<form id="account"><label for="username">用户名</label>
<input id="username" name="username" autocomplete="username" minlength="3" maxlength="32" pattern="[A-Za-z0-9_]+" required aria-describedby="username-hint">
<span id="username-hint" class="field-hint">3～32 位英文字母、数字或下划线。</span>
<label for="password">密码</label><div class="password-row"><input id="password" name="password" type="password" minlength="8" maxlength="128" autocomplete="current-password" required aria-describedby="password-hint">
<button id="show-password" type="button" aria-label="显示密码" aria-pressed="false">显示</button></div>
<span id="password-hint" class="field-hint">请输入你的账号密码。</span>
<div class="actions"><button id="submit-account" class="primary" type="submit">登录</button><button id="switch-account" class="secondary" type="button">注册账号</button></div>
<p id="message" role="alert" aria-live="polite"></p></form>
<p class="note">模型 API Key 在登录后单独配置，请妥善保管账号信息。</p></section>
</main><script>
const password = document.querySelector('#password');
const toggle = document.querySelector('#show-password');
const switchAccount = document.querySelector('#switch-account');
const submitAccount = document.querySelector('#submit-account');
let accountMode = 'login';
switchAccount.addEventListener('click', () => {{
  accountMode = accountMode === 'login' ? 'register' : 'login';
  const registering = accountMode === 'register';
  document.querySelector('#account-title').textContent = registering ? '创建账号' : '进入工作室';
  document.querySelector('#account-hint').textContent = registering ? '注册账号，开启你的创作空间。' : '使用已有账号登录，继续你的创作。';
  document.querySelector('#password-hint').textContent = registering ? '密码为 8～16 位，建议使用 12 位以上的独立密码。' : '请输入你的账号密码。';
  document.title = (registering ? '注册' : '登录') + ' · Tome 故事工作室';
  submitAccount.textContent = registering ? '创建账号' : '登录';
  switchAccount.textContent = registering ? '返回登录' : '注册账号';
  password.autocomplete = registering ? 'new-password' : 'current-password';
  password.value = ''; document.querySelector('#message').textContent = '';
}});
toggle.addEventListener('click', () => {{
  const show = password.type === 'password'; password.type = show ? 'text' : 'password';
  toggle.textContent = show ? '隐藏' : '显示';
  toggle.setAttribute('aria-label', show ? '隐藏密码' : '显示密码');
  toggle.setAttribute('aria-pressed', String(show));
}});
document.querySelector('#account').addEventListener('submit', async event => {{
  event.preventDefault(); const form = event.currentTarget;
  const action = accountMode;
  const buttons = form.querySelectorAll('.actions button');
  const message = document.querySelector('#message'); message.textContent = '';
  if (action === 'register' && Array.from(password.value).length > 16) {{
    message.textContent = '注册密码长度须为 8 至 16 位'; return;
  }}
  buttons.forEach(button => button.disabled = true);
  try {{ const response = await fetch('/_account/' + action, {{method:'POST',
    headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{
      username:form.username.value, password:form.password.value}})}});
    const result = await response.json();
    if (response.ok) location.assign('/');
    else message.textContent = result.error || '操作失败，请重试';
  }} catch (_) {{ message.textContent = '连接失败，请稍后重试'; }}
  finally {{ buttons.forEach(button => button.disabled = false); }}
}});</script></body></html>"""

LOGOUT_SCRIPT = """const b=document.createElement('button');b.type='button';b.textContent='退出登录';
b.className='outline hosted-logout';
b.addEventListener('click',async()=>{await fetch('/_account/logout',{method:'POST'});location.assign('/');});
fetch('/_admin/me').then(r=>r.json()).then(info=>{if(!info.admin)return;
 const a=document.createElement('a');a.className='outline hosted-logout';a.href='/_admin';a.textContent='账号管理';
 const mount=()=>{const target=document.querySelector('#settings-dialog #open-model-settings');
 if(target && a.parentNode!==target.parentNode)target.after(a);};
 new MutationObserver(mount).observe(document.documentElement,{subtree:true,childList:true});mount();}).catch(()=>{});
const place=()=>{const target=document.querySelector('#settings-dialog #open-model-settings');
  if(target && b.parentNode!==target.parentNode)target.after(b);};
new MutationObserver(place).observe(document.documentElement,{subtree:true,childList:true});place();""".encode()

ADMIN_PAGE = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>账号管理 · Tome</title>
<style>{LOGIN_STYLE}</style></head><body><main><section class="intro"><div class="brand">TOME · 故事工作室</div>
<div class="mark"></div><h1>账号管理</h1><p>管理工作室的用户账号。</p></section>
<section class="panel"><h2>用户列表</h2><p class="hint">禁用账号或重置密码后，该用户需要重新登录。作品会保留。</p>
<div id="users"></div><p id="message" role="alert"></p><a href="/">返回工作室</a></section></main>
<script>
const message=document.querySelector('#message');
async function load(){{const response=await fetch('/_admin/users');if(!response.ok){{message.textContent='无法加载用户';return;}}
 const data=await response.json(), root=document.querySelector('#users');root.replaceChildren();
 for(const user of data.users){{const row=document.createElement('div'); row.className='admin-user';
 const name=document.createElement('strong');name.textContent=user.username+(user.disabled?'（已禁用）':'');row.append(name);
 if(!user.is_admin){{const actions=document.createElement('div');actions.className='actions';
 const state=document.createElement('button');state.className='secondary';state.textContent=user.disabled?'启用':'禁用';
 state.onclick=async()=>{{if(!confirm('确认'+state.textContent+'该账号？'))return;await update('/_admin/status',{{username:user.username,disabled:!user.disabled}});}};
 const reset=document.createElement('button');reset.className='secondary';reset.textContent='重置密码';
 reset.onclick=async()=>{{const password=prompt('请输入新的 8～16 位密码');if(password===null)return;
 if(Array.from(password).length<8||Array.from(password).length>16){{message.textContent='密码长度须为 8 至 16 位';return;}}
 await update('/_admin/password',{{username:user.username,password}});}};
 actions.append(state,reset);row.append(actions);}}root.append(row);}}}}
async function update(path,data){{try{{const response=await fetch(path,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(data)}});
 const result=await response.json();message.textContent=response.ok?'操作成功':(result.error||'操作失败');if(response.ok)await load();
 }}catch(_){{message.textContent='连接失败，请稍后重试';}}}}load();</script></body></html>""".encode()


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
        admin_name = os.environ.get("TOME_ADMIN_USERNAME", "")
        self.admin_name = self.accounts._username(admin_name) if admin_name else None
        if self.admin_name and not any(
            user["username"] == self.admin_name and not user["disabled"]
            for user in self.accounts.list_users()
        ):
            raise ValueError("指定的管理员账号不存在或已禁用")
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
            f"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'sha256-{LOGIN_STYLE_HASH}'; frame-ancestors 'none'; base-uri 'none'",
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
            if path.startswith("/_admin"):
                is_admin = bool(
                    self.server.admin_name
                    and self.server.accounts.username_for(user_id)
                    == self.server.admin_name
                )
                if path == "/_admin/me" and not post:
                    self.respond(200, {"admin": is_admin})
                    return
                if not is_admin:
                    self.respond(403, {"error": "无权访问"})
                    return
                if path == "/_admin" and not post:
                    self.respond(200, ADMIN_PAGE, "text/html; charset=utf-8")
                    return
                if path == "/_admin/users" and not post:
                    users = self.server.accounts.list_users()
                    for user in users:
                        user["is_admin"] = user["username"] == self.server.admin_name
                    self.respond(200, {"users": users})
                    return
                if post and path in ("/_admin/status", "/_admin/password"):
                    data = json.loads(self.read_body(4096))
                    if not isinstance(data, dict):
                        raise ValueError("无效请求")
                    name = self.server.accounts._username(data.get("username"))
                    if name == self.server.admin_name:
                        self.respond(400, {"error": "不能操作管理员账号"})
                        return
                    if path == "/_admin/status":
                        self.server.accounts.set_disabled(name, data.get("disabled"))
                    else:
                        self.server.accounts.reset_password(name, data.get("password"))
                    self.respond(200, {"ok": True})
                    return
                self.respond(404, {"error": "未找到"})
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
                try:
                    user_id = self.server.accounts.register(username, password)
                except ValueError as exc:
                    allowed = {
                        "用户名须为 3 至 32 位字母、数字或下划线",
                        "注册密码长度须为 8 至 16 位",
                        "用户名已被使用",
                    }
                    message = str(exc)
                    self.respond(
                        400,
                        {
                            "error": message
                            if message in allowed
                            else "请求格式或内容无效"
                        },
                    )
                    return
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
