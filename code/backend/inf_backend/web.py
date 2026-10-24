"""Loopback-only web UI. Run with python -m inf_backend.web."""
import argparse
import json
import logging
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

from inf_writer.memory_temporality import current_claim, has_current_content

from . import service
from .settings import Settings
from . import generation

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


def serialize(book):
    raw = book["state"]
    if not isinstance(raw, dict):
        state = raw.to_dict()
        mode = "legacy" if state["chapters"] else "longform"
    else:
        memory = raw.get("memory", {})
        facts = {}
        for key, item in memory.get("items", {}).items():
            if item.get("status") != "active" or not has_current_content(item):
                continue
            sources = item.get("sources", [])
            facts[key] = {"subject": item["subject"], "attribute": item["attribute"],
                          "value": current_claim(item), "revision": item["revision"],
                          "status": "active", "tier": item.get("tier"),
                          "source": sources[-1] if sources else {"chapter_number": "—", "quote": ""}}
        state = {"chapters": raw["chapters"], "revision": len(raw["chapters"]),
                 "facts": facts, "pending": raw.get("pending", []),
                 "memory_tiers": {tier: sum(i.get("tier") == tier for i in memory.get("items", {}).values())
                                  for tier in ("working", "recent", "long")}}
        mode = "longform"
    state["project_id"] = book["id"]
    return {"metadata": book["metadata"], "state": state, "mode": mode}


def load_view(book_id):
    if service._metadata(book_id)["model"]["model"] == "offline-demo":
        raise FileNotFoundError("离线演示已移除")
    return {**serialize({**service.load_book(book_id), "id": book_id}),
            "style": service.load_writing_style(book_id)}


class WebServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address):
        super().__init__(address, Handler)
        self.jobs = {}
        self.busy = set()
        self.estimates = {}
        self.job_lock = threading.Lock()

    def job_for_book(self, book_id):
        with self.job_lock:
            for job_id, job in reversed(list(self.jobs.items())):
                if job["book_id"] == book_id:
                    return {**job, "job_id": job_id}
        return None

    def prepare_generation(self, book_id, data):
        if "prices" in data:
            raise ValueError("单价由官方价表自动匹配，无需手动填写")
        result = generation.estimate(book_id, data.get("count", 1), data.get("approved_first", False))
        estimate_id = uuid4().hex
        with self.job_lock:
            self.estimates = {k: v for k, v in self.estimates.items() if v["expires_at"] > time.time()}
            self.estimates[estimate_id] = {**result, "expires_at": time.time() + 600}
        return {**result, "estimate_id": estimate_id}

    def start_generation(self, book_id, data):
        with self.job_lock:
            if book_id in self.busy:
                for job_id, job in self.jobs.items():
                    if job["book_id"] == book_id and job["status"] == "running":
                        return {"job_id": job_id}
            estimate = self.estimates.get(data.get("estimate_id"))
        if data.get("confirmed") is not True or not estimate or estimate["book_id"] != book_id or estimate["expires_at"] < time.time():
            raise ValueError("请先查看本次 token 和费用预估，再点击继续生成")
        if estimate["signature"] != generation.signature(book_id):
            raise ValueError("作品或文风已更新，请重新查看费用预估后再确认")
        count = estimate["count"]
        current_price = generation.official_pricing.quote(service._metadata(book_id)["model"]["model"])
        if current_price["period"] != estimate["pricing"]["period"] or current_price["rates"] != estimate["prices"]:
            raise ValueError("官方单价或峰谷时段已变化，请关闭确认框后重新预估再确认")
        book = service.load_book(book_id)
        view = serialize({**book, "id": book_id})
        if view["mode"] == "legacy":
            raise ValueError("此作品是旧版章节存档，可阅读和导出。请新建作品使用新版引擎，避免覆盖旧正文。")
        if len(view["state"]["chapters"]) >= book["metadata"]["target_chapters"]:
            raise ValueError("全书章节已完成")
        settings = Settings.load()
        with self.job_lock:
            if book_id in self.busy:
                for job_id, job in self.jobs.items():
                    if job["book_id"] == book_id and job["status"] == "running":
                        return {"job_id": job_id}
            job_id = uuid4().hex
            self.busy.add(book_id)
            started_at = time.time()
            self.estimates.pop(data["estimate_id"], None)
            self.jobs[job_id] = {"status": "running", "book_id": book_id, "started_at": started_at,
                                 "count": count, "completed": 0, "current_chapter": estimate["first_chapter"]}

        def progress(update):
            with self.job_lock:
                self.jobs[job_id].update(update)

        def run():
            try:
                options = {"settings": settings, "count": count}
                with service.operation_lock(service.book_path(book_id)):
                    service.generate(book_id, progress=progress, **options)
                progress({"completed": count})
                result = {"status": "completed", "book_id": book_id}
            except Exception as exc:
                result = {"status": "failed", "book_id": book_id, "error": str(exc)}
            with self.job_lock:
                self.jobs[job_id] = {**self.jobs[job_id], **result, "started_at": started_at}
                self.busy.discard(book_id)

        threading.Thread(target=run, daemon=True).start()
        return {"job_id": job_id}


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, data, content_type="application/json; charset=utf-8", attachment=False):
        body = json.dumps(data, ensure_ascii=False).encode() if content_type.startswith("application/json") else data
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'")
        if attachment:
            self.send_header("Content-Disposition", 'attachment; filename="manuscript.md"')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.dispatch(False)

    def do_POST(self):
        self.dispatch(True)

    def dispatch(self, post):
        host = self.headers.get("Host", "")
        allowed = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        if host not in allowed or (post and self.headers.get("Origin", f"http://{host}") != f"http://{host}"):
            self.reply(403, {"error": "仅允许本机同源访问"})
            return
        path = urlsplit(self.path).path
        try:
            data = {}
            if post:
                if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                    self.reply(415, {"error": "请求必须使用 JSON"})
                    return
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 65536:
                    raise ValueError("请求大小无效")
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError("请求必须是 JSON 对象")
            if not post and path == "/api/config":
                cfg = Settings.load(require_key=False)
                self.reply(200, {"configured": bool(cfg.api_key.strip()), "model": cfg.model})
            elif not post and path == "/api/books":
                books = []
                for book_id in service.list_books():
                    try:
                        book = load_view(book_id)
                        books.append({"id": book_id, "metadata": book["metadata"],
                                      "chapters": len(book["state"]["chapters"]),
                                      "units": sum(service.count_units(c["text"]) for c in book["state"]["chapters"])})
                    except (ValueError, OSError):
                        books.append({"id": book_id, "error": "存档无法读取"})
                self.reply(200, {"books": books})
            elif post and path == "/api/books":
                book_id = service.new_book_id()
                service.create_book(book_id,
                    data.get("title"), data.get("prompt"), data.get("chapters"), data.get("target_units"),
                    style=data.get("style"))
                self.reply(201, load_view(book_id))
            elif not post and path.startswith("/api/jobs/"):
                with self.server.job_lock:
                    job = self.server.jobs.get(path.removeprefix("/api/jobs/"))
                self.reply(200 if job else 404, job or {"error": "任务不存在；服务可能已重启，请刷新作品"})
            elif path.startswith("/api/books/"):
                parts = path.strip("/").split("/")
                book_id = parts[2]
                if post and len(parts) == 4 and parts[3] == "generate":
                    self.reply(202, self.server.start_generation(book_id, data))
                elif post and len(parts) == 4 and parts[3] == "estimate":
                    self.reply(200, self.server.prepare_generation(book_id, data))
                elif post and len(parts) == 4 and parts[3] == "style":
                    with self.server.job_lock:
                        if book_id in self.server.busy:
                            raise ValueError("当前章节正在生成，请在完成后保存文风设定")
                        style = service.save_writing_style(book_id, data)
                    self.reply(200, {"style": style})
                elif not post and len(parts) == 3:
                    self.reply(200, {**load_view(book_id), "job": self.server.job_for_book(book_id)})
                elif not post and len(parts) == 4 and parts[3] == "export":
                    body = service.export_markdown(service.load_book(book_id)).encode()
                    self.reply(200, body, "text/markdown; charset=utf-8", attachment=True)
                else:
                    self.reply(404, {"error": "接口不存在"})
            elif not post and path in ("/", "/app.js", "/style.css"):
                name = "index.html" if path == "/" else path[1:]
                mime = {"index.html": "text/html", "app.js": "text/javascript", "style.css": "text/css"}[name]
                self.reply(200, (FRONTEND / name).read_bytes(), mime + "; charset=utf-8")
            else:
                self.reply(404, {"error": "页面不存在"})
        except FileNotFoundError:
            self.reply(404, {"error": "作品或文件不存在"})
        except (ValueError, TypeError) as exc:
            self.reply(400, {"error": str(exc)})
        except Exception:
            logging.exception("Web request failed")
            self.reply(500, {"error": "操作失败，请检查本地服务日志"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = WebServer(("127.0.0.1", args.port))
    print(f"Tome Agent: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
