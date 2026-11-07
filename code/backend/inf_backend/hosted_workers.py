"""Run each hosted account's existing local service in an isolated process."""

import http.client
import json
import os
import queue
import re
import subprocess
import sys
import sysconfig
import threading
import time
from pathlib import Path


class WorkerUnavailable(RuntimeError):
    pass


class WorkerPool:
    """Keep per-user data and model settings in separate persistent directories."""

    def __init__(self, root, limit=3):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.limit = limit
        self.workers = {}
        self.readers = {}
        self.used = {}
        self.inflight = {}
        self.closed = False
        self.lock = threading.Lock()

    def get(self, user_id):
        if not isinstance(user_id, str) or not re.fullmatch(r"[0-9a-f]{32}", user_id):
            raise ValueError("无效用户")
        with self.lock:
            if self.closed:
                raise WorkerUnavailable("用户服务已关闭")
            for key, (process, _) in list(self.workers.items()):
                if process.poll() is not None:
                    self.readers.pop(key).join(timeout=10)
                    self.workers.pop(key)
                    self.used.pop(key, None)
                    self.inflight.pop(key, None)
            if user_id in self.workers:
                self.used[user_id] = time.monotonic()
                self.inflight[user_id] += 1
                return self.workers[user_id][1]
            if len(self.workers) >= self.limit:
                self._evict_idle()
                if len(self.workers) >= self.limit:
                    raise WorkerUnavailable("服务繁忙，请稍后重试")
            home = self.root / user_id
            home.mkdir(mode=0o700, exist_ok=True)
            if home.is_symlink() or home.resolve().parent != self.root:
                raise ValueError("用户目录不安全")
            allowed = {
                "PATH",
                "SYSTEMROOT",
                "WINDIR",
                "TEMP",
                "TMP",
                "LANG",
                "LC_ALL",
                "SSL_CERT_FILE",
                "SSL_CERT_DIR",
            }
            env = {
                key: value
                for key, value in os.environ.items()
                if key.upper() in allowed
            }
            env["HOME"] = str(home)
            code = Path(__file__).resolve().parents[2]
            paths = [str(code / "backend"), str(code / "core_engine")]
            executable = sys.executable
            if os.name == "nt":
                # Windows venv launchers can spawn a second interpreter that
                # outlives the launcher when it is terminated.
                executable = sys._base_executable
                paths.append(sysconfig.get_paths()["purelib"])
            env["PYTHONPATH"] = os.pathsep.join(paths)
            env["PYTHONUNBUFFERED"] = "1"
            env["TOME_DATA_HOME"] = str(home)
            env["DATABASE_URL"] = ""
            process = subprocess.Popen(
                [executable, "-m", "inf_backend.web", "--port", "0"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            lines = queue.Queue()

            def read_output():
                try:
                    for line in process.stdout:
                        if line.startswith("Tome Agent: http://127.0.0.1:"):
                            lines.put(line.strip())
                finally:
                    process.stdout.close()

            reader = threading.Thread(target=read_output, daemon=True)
            reader.start()
            try:
                line = lines.get(timeout=20)
                match = re.fullmatch(r"Tome Agent: http://127\.0\.0\.1:(\d+)", line)
                if not match or process.poll() is not None:
                    raise WorkerUnavailable("用户服务启动失败")
                port = int(match.group(1))
            except (queue.Empty, WorkerUnavailable):
                if process.poll() is None:
                    process.terminate()
                process.wait(timeout=10)
                reader.join(timeout=10)
                raise WorkerUnavailable("用户服务启动失败，请稍后重试") from None
            self.workers[user_id] = (process, port)
            self.readers[user_id] = reader
            self.used[user_id] = time.monotonic()
            self.inflight[user_id] = 1
            return port

    def release(self, user_id):
        with self.lock:
            if user_id in self.inflight:
                self.inflight[user_id] = max(0, self.inflight[user_id] - 1)
                self.used[user_id] = time.monotonic()

    def _evict_idle(self):
        for key in sorted(self.workers, key=self.used.get):
            if self.inflight[key] or time.monotonic() - self.used[key] < 300:
                continue
            process, port = self.workers[key]
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
            try:
                conn.request("GET", "/api/_internal/worker-status")
                response = conn.getresponse()
                if response.status != 200 or json.loads(response.read())["busy"]:
                    continue
            except (OSError, ValueError, KeyError):
                continue
            finally:
                conn.close()
            process.terminate()
            process.wait(timeout=10)
            self.readers.pop(key).join(timeout=10)
            self.workers.pop(key)
            self.used.pop(key)
            self.inflight.pop(key)
            return

    def close(self):
        with self.lock:
            self.closed = True
            for key, (process, _) in self.workers.items():
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=10)
                self.readers[key].join(timeout=10)
            self.workers.clear()
            self.readers.clear()
            self.used.clear()
            self.inflight.clear()
