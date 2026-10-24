"""Windows portable launcher; frontend and server run entirely on loopback."""
import argparse
import json
import logging
import os
from pathlib import Path
import sys
import threading
import webbrowser


def data_home():
    return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "TomeAgent"


def read_state(path):
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        port = state["port"]
        if type(port) is int and 1 <= port <= 65535:
            return state
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return {}


def acquire_lock(path):
    import msvcrt
    stream = path.open("a+b")
    stream.seek(0, 2)
    if stream.tell() == 0:
        stream.write(b"0")
        stream.flush()
    stream.seek(0)
    try:
        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        stream.close()
        return None
    return stream


def launcher_window(server, url, home):
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.title("Tome · 故事工作室")
    root.geometry("460x300")
    root.resizable(False, False)
    root.configure(bg="#f7f7ef")
    tk.Label(root, text="Tome 故事工作室", font=("Microsoft YaHei", 23), fg="#285849", bg="#f7f7ef").pack(pady=(28, 10))
    tk.Label(root, text="创作服务已启动\n在浏览器中开始你的下一个故事", font=("Microsoft YaHei", 11), bg="#f7f7ef", fg="#66785e").pack()
    tk.Button(root, text="打开工作室", font=("Microsoft YaHei", 12), bg="#285849", fg="white", width=24,
              command=lambda: webbrowser.open(url)).pack(pady=17)
    tk.Button(root, text="打开作品与配置目录", command=lambda: os.startfile(home)).pack()
    tk.Label(root, text="使用期间请保留此窗口；关闭窗口会停止本地服务。", bg="#f7f7ef", fg="#87917c", font=("Microsoft YaHei", 9)).pack(pady=15)

    def close():
        with server.job_lock:
            busy = bool(server.busy)
        if busy:
            messagebox.showinfo("正在创作", "作品正在生成，请等待任务结束后再退出。", parent=root)
        else:
            root.destroy()
    root.protocol("WM_DELETE_WINDOW", close)
    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, help="Use an isolated user data directory")
    parser.add_argument("--port", type=int, help="Local port; 0 selects a free port")
    parser.add_argument("--headless", action="store_true", help="Run without launcher window")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    home = (args.data_dir or data_home()).resolve()
    home.mkdir(parents=True, exist_ok=True)
    os.environ["TOME_DATA_HOME"] = str(home)
    logging.basicConfig(filename=home / "desktop.log", level=logging.WARNING,
                        format="%(asctime)s %(levelname)s %(message)s")
    # Windowed builds have no standard streams. Keep HTTP/request and engine
    # diagnostics in the local log, rather than failing on print()/stderr.write().
    if sys.stdout is None:
        sys.stdout = (home / "runtime.log").open("a", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = sys.stdout
    state_path = home / "desktop.json"
    lock = acquire_lock(home / "desktop.lock")
    if lock is None:
        state = read_state(state_path)
        if state and not args.no_browser:
            webbrowser.open(f"http://127.0.0.1:{state['port']}/")
        return
    server = None
    worker = None
    try:
        # Import after choosing data storage: the package never reads the
        # developer's .env or bundles any saved books.
        from inf_backend.web import WebServer
        previous = read_state(state_path)
        port = args.port if args.port is not None else previous.get("port", 18765)
        try:
            server = WebServer(("127.0.0.1", port))
        except OSError:
            server = WebServer(("127.0.0.1", 0))
        url = f"http://127.0.0.1:{server.server_port}/"
        state_path.write_text(json.dumps({"port": server.server_port, "pid": os.getpid()}), encoding="utf-8")
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        if not args.no_browser:
            webbrowser.open(url)
        if args.headless:
            worker.join()
        else:
            launcher_window(server, url, home)
    except KeyboardInterrupt:
        pass
    except Exception:
        logging.exception("Desktop startup failed")
        if not args.headless:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, f"启动失败，请查看日志：\n{home / 'desktop.log'}", "Tome", 0x10)
        raise
    finally:
        if server:
            if worker and worker.is_alive():
                server.shutdown()
                worker.join(timeout=3)
            server.server_close()
        if state_path.exists():
            state_path.unlink()
        lock.close()


if __name__ == "__main__":
    main()
