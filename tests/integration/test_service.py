import tempfile
import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from inf_backend import service
from inf_backend.settings import Settings
from inf_writer.demo import DemoModel
from inf_writer.models import Budget, ModelGateway, ModelReply, ModelRequest


class ServiceIntegrationTests(unittest.TestCase):
    def test_default_generation_entry_uses_stable_longform_runtime(self):
        self.assertIs(service.generate, service.generate_longform)

    def test_configured_token_prices_reserve_cost_without_rejecting_paid_reply(self):
        cfg = Settings(api_key="FAKE_TEST_KEY", input_usd_per_million=1, output_usd_per_million=2)
        gateway, budget = service._gateway(cfg)
        gateway.provider = Mock()
        gateway.provider.complete.return_value = ModelReply("正文", 100, 100, .0003)
        self.assertEqual(gateway.complete(ModelRequest("writer", "system", {})).content, "正文")
        self.assertAlmostEqual(budget.cost_upper_usd, .0003)

    def test_batch_persists_each_chapter_before_later_failure(self):
        cfg = Settings(api_key="FAKE_TEST_KEY")
        with tempfile.TemporaryDirectory() as folder, patch.object(service, "BOOKS", Path(folder)):
            service.create_book("batch-book", "批量测试", "故事", 3, 3000, settings=cfg)

            class FakeSession:
                def __init__(self, output, gateway, plan, book=None):
                    self.output = Path(output)
                    self.output.mkdir(parents=True)
                    self.book = {"chapters": []}
                    self.latest_checkpoint = self.output / "checkpoint-0.json"
                    self.latest_checkpoint.write_text(json.dumps(self.book), encoding="utf-8")

                def write_next(self, instruction):
                    if self.book["chapters"]:
                        return {"status": "NO_DRAFT", "chapter_number": 2, "errors": ["模拟失败"]}
                    self.book["chapters"].append({"number": 1, "title": "首章", "text": "保存的正文。"})
                    self.latest_checkpoint = self.output / "checkpoint-1.json"
                    self.latest_checkpoint.write_text(json.dumps(self.book), encoding="utf-8")
                    return {"status": "DRAFT_UNCHECKED"}

            saved_progress = []

            def progress(update):
                if update["completed"]:
                    pointer = json.loads(service._longform_pointer("batch-book").read_text(encoding="utf-8"))
                    checkpoint = service.book_path("batch-book") / pointer["checkpoint"]
                    saved_progress.append(update.copy())
                    self.assertEqual(len(json.loads(checkpoint.read_text(encoding="utf-8"))["chapters"]), 1)

            with patch.object(service, "WritingSession", FakeSession):
                with self.assertRaisesRegex(RuntimeError, "第2章"):
                    service.generate("batch-book", count=3, gateway=object(), settings=cfg, progress=progress)
            self.assertTrue(saved_progress)

    def test_markdown_export_indents_each_paragraph_without_mutating_saved_prose(self):
        original = "第一段。\r\n\r\n    第二段。\n\u3000\u3000第三段。\u2028第四段。"
        state = {"chapters": [{"number": 1, "title": "开篇", "text": original}]}
        book = {"metadata": {"title": "测试作品"}, "state": state}
        exported = service.export_markdown(book)
        self.assertEqual(exported,
            "# 测试作品\n\n## 第1章 开篇\n\n\u3000\u3000第一段。\n\n\u3000\u3000第二段。\n\n\u3000\u3000第三段。\n\n\u3000\u3000第四段。\n")
        self.assertEqual(state["chapters"][0]["text"], original)

    def test_create_generate_and_export_with_offline_model(self):
        settings = Settings(api_key="FAKE_TEST_KEY")
        budget = Budget(max_calls=8, max_cost_usd=0)
        gateway = ModelGateway(DemoModel(), budget)
        local_tmp = Path(__file__).resolve().parents[2] / "code" / "backend" / "data"
        local_tmp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=local_tmp) as folder, patch.object(service, "BOOKS", Path(folder)):
            created = service.create_book(
                "demo-book", "守灯人", "身份核验故事", 2, 1000, settings=settings
            )
            self.assertEqual(created["metadata"]["title"], "守灯人")
            completed = service.generate_legacy(
                "demo-book", count=2, gateway=gateway, budget=budget, settings=settings
            )
            self.assertEqual(len(completed["state"].chapters), 2)
            self.assertEqual(completed["state"].active_facts()[0]["value"], "金色")
            exported = service.export_markdown(completed)
            self.assertIn("# 守灯人", exported)
            self.assertIn("## 第2章", exported)
            self.assertIn("\n\n\u3000\u3000艾岚", exported)
            self.assertEqual(budget.calls, 8)


if __name__ == "__main__":
    unittest.main()
