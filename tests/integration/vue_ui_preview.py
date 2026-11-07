"""Isolated manual browser fixture for Vue interactions; never calls a model.

Run with PYTHONPATH=code/core_engine;code/backend and open localhost:8766.
All fixture books and configuration are disposable temporary files.
"""
import argparse
import copy
import os
from pathlib import Path
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--unconfigured", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="tome-vue-ui-") as directory:
        os.environ["TOME_DATA_HOME"] = directory
        os.environ.pop("DEEPSEEK_API_KEY", None)
        if not args.unconfigured:
            Path(directory, ".env").write_text("DEEPSEEK_API_KEY=sk-VUE_TEST_ONLY_NOT_REAL\n", encoding="utf-8")
        from inf_backend import service, library, official_pricing
        from inf_backend.web import WebServer, Handler
        from inf_backend.settings import Settings
        metrics = {"generation_calls": 0, "chapters_written": 0}
        states = {}

        def empty_state():
            return {"chapters": [], "memory": {"items": {}}, "pending": []}

        def add_chapter(state):
            number = len(state["chapters"]) + 1
            text = f"这是第{number}章的测试正文。\n角色拿起钥匙，走向下一段故事。"
            state["chapters"].append({"number": number, "title": f"测试章节{number}", "text": text})
            state["memory"]["items"][f"fact-{number}"] = {
                "id": f"fact-{number}", "subject": f"角色{number}", "attribute": "item", "claim": "持有钥匙",
                "status": "active", "tier": "working", "revision": number, "kind": "event",
                "sources": [{"chapter_number": number, "quote": "角色拿起钥匙。"}]}

        def load_book(book_id):
            return {"metadata": service._metadata(book_id), "state": copy.deepcopy(states.setdefault(book_id, empty_state()))}

        def generate(book_id, *, count, progress, **options):
            metrics["generation_calls"] += 1
            state = states.setdefault(book_id, empty_state())
            for index in range(count):
                progress({"completed": index, "current_chapter": len(state["chapters"]) + 1})
                time.sleep(.7)
                add_chapter(state)
                metrics["chapters_written"] += 1
                progress({"completed": index + 1, "current_chapter": len(state["chapters"])})

        service.load_book = load_book
        service.generate = generate
        official_pricing.get_table = lambda: {"models": official_pricing.SNAPSHOT, "checked_at": "test-fixture", "status": "verified_snapshot"}
        fixture_settings = Settings(api_key="VUE_TEST_ONLY")
        service.create_book("vue-ui-main", "Vue迁移测试作品", "仅用于界面测试，不调用模型", 5, 5000,
                            settings=fixture_settings, style={"instructions": "简洁短句。", "reference": "测试片段。"})
        states["vue-ui-main"] = empty_state()
        add_chapter(states["vue-ui-main"])
        add_chapter(states["vue-ui-main"])
        service.create_book("vue-ui-trash", "废案箱测试作品", "测试恢复及确认框", 2, 1000, settings=fixture_settings)
        library.delete_book("vue-ui-trash")

        class PreviewHandler(Handler):
            def do_GET(self):
                if self.path == "/__test__/metrics":
                    self.reply(200, metrics)
                else:
                    super().do_GET()

        server = WebServer(("127.0.0.1", args.port))
        server.RequestHandlerClass = PreviewHandler
        print(f"Isolated Vue UI fixture: http://127.0.0.1:{server.server_port}/ (no model calls)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
