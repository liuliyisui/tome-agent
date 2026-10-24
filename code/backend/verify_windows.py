"""Smoke-test the packaged EXE with isolated disposable data and no model calls."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.request import build_opener, ProxyHandler, Request


def verify(executable):
    executable = Path(executable).resolve()
    client = build_opener(ProxyHandler({}))
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("DEEPSEEK_", "INF_", "TOME_", "PYTHON"))}
    env["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")
    with tempfile.TemporaryDirectory(prefix="tome-windows-smoke-") as temporary:
        home = Path(temporary) / "用户数据"
        home.mkdir()
        state_path = home / "desktop.json"
        process = None

        def start():
            proc = subprocess.Popen([str(executable), "--headless", "--no-browser", "--port", "0", "--data-dir", str(home)],
                                    env=env, cwd=temporary, creationflags=subprocess.CREATE_NO_WINDOW)
            end = time.monotonic() + 30
            while time.monotonic() < end:
                if proc.poll() is not None:
                    raise AssertionError(f"EXE exited during startup: {proc.returncode}")
                if state_path.exists():
                    state = json.loads(state_path.read_text(encoding="utf-8"))
                    if state.get("pid") == proc.pid:
                        return proc, f"http://127.0.0.1:{state['port']}"
                time.sleep(.1)
            proc.terminate()
            proc.wait(timeout=10)
            raise AssertionError("EXE did not start within 30 seconds")

        def request(base, path, payload=None):
            data = None if payload is None else json.dumps(payload).encode()
            with client.open(Request(base + path, data=data, headers={"Content-Type": "application/json"}), timeout=10) as response:
                body = response.read()
                return json.loads(body) if response.headers["Content-Type"].startswith("application/json") else body.decode("utf-8")

        try:
            process, base = start()
            assert request(base, "/api/config")["configured"] is False
            assert "api-key-dialog" in request(base, "/")
            assert "openApiConfig" in request(base, "/app.js")
            assert "createTomeLibrary" in request(base, "/vue-components.js")
            assert "Vue" in request(base, "/vue.runtime.global.prod.js")
            assert "--green" in request(base, "/style.css")
            key = "sk-" + "PACKAGED_TEST_ONLY_" * 2
            result = request(base, "/api/config", {"api_key": key})
            assert result["configured"] is True and key not in json.dumps(result)
            book = request(base, "/api/books", {"title": "打包验证作品", "prompt": "验证数据保存，不调用模型", "chapters": 2, "target_units": 1000})
            book_id = book["state"]["project_id"]
            state = state_path.read_text(encoding="utf-8")
            duplicate = subprocess.run([str(executable), "--headless", "--no-browser", "--data-dir", str(home)],
                                       env=env, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
            assert duplicate.returncode == 0
            assert state_path.read_text(encoding="utf-8") == state
            process.terminate()
            process.wait(timeout=10)
            process, base = start()
            assert request(base, "/api/config")["configured"] is True
            assert request(base, f"/api/books/{book_id}")["metadata"]["title"] == "打包验证作品"
            assert request(base, "/api/books")["books"][0]["id"] == book_id
            print("PASS: standalone EXE, frontend assets, first-run setup, isolated data, single instance, restart persistence; no model calls")
        finally:
            if process and process.poll() is None:
                process.terminate()
                process.wait(timeout=10)


if __name__ == "__main__":
    import sys
    verify(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent / "data" / "dist" / "TomeAgent" / "TomeAgent.exe")
