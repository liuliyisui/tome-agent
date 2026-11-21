"""Real checkpoint edits and continuation with deterministic model fixtures."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inf_backend import editing, proofreading, service
from inf_backend.settings import Settings
from tests.unit.test_langgraph import EventProvider
from tome_writer.domain import canonical


class LocalEditingTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.patch = patch.object(service, "BOOKS", Path(self.folder.name))
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.config = Settings(api_key="FAKE_TEST_KEY")
        service.create_book(
            "edited-book", "测试作品", "调查来信", 4, 4000, settings=self.config
        )
        service.generate(
            "edited-book", count=2, gateway=EventProvider(), settings=self.config
        )

    def data(self, number=1, text="甲把红色玉佩交给乙。乙离开武馆。"):
        book = service.load_book("edited-book")
        data = {
            "title": "作者修改稿",
            "text": text,
            "base_revision": proofreading.revision(editing.chapters_of(book)),
        }
        report = editing.review_draft("edited-book", number, data)
        return {**data, "review_revision": report["revision"], "acknowledged": True}

    def test_edit_preserves_later_prose_rebuilds_memory_and_supports_continuation(self):
        old = service.load_book("edited-book")
        pointer = service._longform_pointer("edited-book")
        old_path = (
            service.book_path("edited-book")
            / json.loads(pointer.read_text())["checkpoint"]
        )
        old_bytes = old_path.read_bytes()
        data = self.data()
        result = editing.save_chapter("edited-book", 1, data)
        saved = service.load_book("edited-book")
        self.assertEqual(saved["state"]["chapters"][0]["text"], data["text"])
        self.assertEqual(
            saved["state"]["chapters"][1]["text"], old["state"]["chapters"][1]["text"]
        )
        self.assertEqual(saved["state"]["memory"]["processed_through"], 2)
        quotes = [
            source["quote"]
            for item in saved["state"]["memory"]["items"].values()
            for source in item.get("sources", [])
            if source.get("chapter_number") == 1
        ]
        self.assertTrue(quotes)
        self.assertTrue(all(quote in data["text"] for quote in quotes))
        self.assertEqual(old_path.read_bytes(), old_bytes)
        self.assertEqual(result["memory_synced_through"], 2)
        model = EventProvider()
        service.generate("edited-book", gateway=model, settings=self.config)
        planner = next(r for r in model.requests if r.role == "planner")
        self.assertIn(data["text"], canonical(planner.payload))
        self.assertEqual(len(service.load_book("edited-book")["state"]["chapters"]), 3)

    def test_editing_second_chapter_keeps_other_prose_without_stale_event_state(self):
        old = service.load_book("edited-book")
        editing.save_chapter("edited-book", 2, self.data(2))
        new = service.load_book("edited-book")
        self.assertEqual(
            new["state"]["chapters"][0]["text"], old["state"]["chapters"][0]["text"]
        )
        self.assertEqual(
            new["state"]["chapters"][0]["title"], old["state"]["chapters"][0]["title"]
        )
        self.assertTrue(
            all(
                item["kind"] == "prose_excerpt"
                for item in new["state"]["memory"]["items"].values()
            )
        )
        self.assertEqual(new["state"]["memory"]["processed_through"], 2)

    def test_stale_editor_and_stale_review_are_rejected_without_publishing(self):
        draft = self.data()
        pointer = service._longform_pointer("edited-book").read_bytes()
        draft["text"] += "后来，雨停了。"
        with self.assertRaisesRegex(ValueError, "重新进行本地复查"):
            editing.save_chapter("edited-book", 1, draft)
        self.assertEqual(service._longform_pointer("edited-book").read_bytes(), pointer)
        draft = self.data()
        draft["base_revision"] = "stale"
        with self.assertRaisesRegex(ValueError, "作品已更新"):
            editing.save_chapter("edited-book", 1, draft)

    def test_secret_and_unacknowledged_warnings_cannot_be_submitted(self):
        data = self.data(text="误贴 sk-FAKE_SECRET_ONLY_1234567890")
        with self.assertRaisesRegex(ValueError, "疑似密钥"):
            editing.save_chapter("edited-book", 1, data)
        data = self.data(text="他迫不急待地出发。")
        data["acknowledged"] = False
        with self.assertRaisesRegex(ValueError, "核实复查提示"):
            editing.save_chapter("edited-book", 1, data)

    def test_failed_publish_leaves_the_original_pointer_and_prose_intact(self):
        original_atomic = service._atomic_json
        pointer = service._longform_pointer("edited-book")
        old_bytes = pointer.read_bytes()

        def fail(path, value):
            if Path(path) == pointer:
                raise OSError("simulated disk error")
            return original_atomic(path, value)

        with (
            patch.object(service, "_atomic_json", side_effect=fail),
            self.assertRaises(OSError),
        ):
            editing.save_chapter("edited-book", 1, self.data())
        self.assertEqual(pointer.read_bytes(), old_bytes)
        self.assertEqual(len(service.load_book("edited-book")["state"]["chapters"]), 2)

    def test_regeneration_after_manual_edit_rebuilds_a_valid_prefix_without_old_snapshots(
        self,
    ):
        data = self.data()
        editing.save_chapter("edited-book", 1, data)
        manual_runs = list(
            service.book_path("edited-book").glob(
                "longform-runs/run-manual-*/manual-edit.json"
            )
        )
        self.assertEqual(len(manual_runs), 1)
        self.assertEqual(len(list(manual_runs[0].parent.glob("checkpoint_*.json"))), 2)
        service.generate(
            "edited-book",
            gateway=EventProvider(),
            settings=self.config,
            regenerate_number=2,
            confirmed=True,
            author_feedback="保留第一章作者修改稿，改写第二章。",
        )
        revised = service.load_book("edited-book")
        self.assertEqual(len(revised["state"]["chapters"]), 2)
        self.assertEqual(revised["state"]["chapters"][0]["text"], data["text"])

    def test_reviewed_export_uses_current_revision(self):
        report = editing.review_book("edited-book")
        output = editing.reviewed_export(
            "edited-book", {"review_revision": report["revision"], "acknowledged": True}
        )
        self.assertIn("测试作品", output)
        with self.assertRaisesRegex(ValueError, "重新进行本地复查"):
            editing.reviewed_export(
                "edited-book", {"review_revision": "old", "acknowledged": True}
            )


if __name__ == "__main__":
    unittest.main()
