import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from inf_backend import service
from inf_backend.settings import Settings
from inf_writer.models import ModelReply, ModelRequest
from memory_runtime.writing import WritingSession


class WritingStyleTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.books_patch = patch.object(service, "BOOKS", Path(self.folder.name))
        self.books_patch.start()

    def tearDown(self):
        self.books_patch.stop()
        self.folder.cleanup()

    def create(self, style=None):
        return service.create_book("style-book", "故事", "一个故事", 3, 3000,
                                   settings=Settings(api_key="FAKE_TEST_KEY"), style=style)

    def test_style_persists_without_changing_resume_plan_or_existing_checkpoint(self):
        book = self.create()
        self.assertEqual(service.load_writing_style("style-book"), {"instructions": "", "reference": ""})
        plan = service._longform_plan(book["metadata"])
        session = WritingSession(service.book_path("style-book") / "longform-runs" / "test", Mock(), plan)
        checkpoint = session.latest_checkpoint
        before = checkpoint.read_bytes()
        service._atomic_json(service._longform_pointer("style-book"), {
            "checkpoint": checkpoint.relative_to(service.book_path("style-book")).as_posix()})
        style = {"instructions": "短句，克制，避免说教。", "reference": "风停了。他收好信，推门出去。"}
        service.save_writing_style("style-book", style)
        self.assertEqual(service.load_writing_style("style-book"), style)
        self.assertEqual(service.load_book("style-book")["state"]["chapters"], [])
        self.assertEqual(checkpoint.read_bytes(), before)
        self.assertEqual(service._longform_plan(book["metadata"]), plan)
        service.save_writing_style("style-book", {"instructions": "", "reference": ""})
        self.assertEqual(service.load_book("style-book")["state"]["chapters"], [])

    def test_every_writer_request_gets_style_without_mutating_other_roles(self):
        style = {"instructions": "对白自然。", "reference": "他没有回头。"}
        gateway = Mock()
        gateway.complete.return_value = ModelReply("正文", 0, 0, 0)
        styled = service.StyleGateway(gateway, style)
        for payload in ({"chapter_number": 1}, {"output_mode": "plain_prose", "current_draft": "草稿"}, {"repair": {"attempt": 1}}):
            request = ModelRequest("writer", "输出JSON", payload)
            styled.complete(request)
            forwarded = gateway.complete.call_args.args[0]
            self.assertEqual(forwarded.payload["writing_style"], style)
            self.assertNotIn("writing_style", request.payload)
            self.assertIn("不续写或照抄", forwarded.system)
            self.assertEqual(forwarded.max_output_tokens, request.max_output_tokens)
        for role in ("planner", "memory", "reviewer"):
            request = ModelRequest(role, "system", {})
            styled.complete(request)
            self.assertIs(gateway.complete.call_args.args[0], request)

    def test_create_validates_style_before_writing_and_rejects_active_changes(self):
        with self.assertRaises(ValueError):
            self.create({"instructions": "x" * 2001, "reference": ""})
        self.assertFalse(service.book_path("style-book").exists())
        style = {"instructions": "叙述简洁。", "reference": ""}
        self.create(style)
        self.assertEqual(service.load_writing_style("style-book"), style)
        with service.operation_lock(service.book_path("style-book")):
            with self.assertRaises(ValueError):
                service.save_writing_style("style-book", {"instructions": "不能保存", "reference": ""})
        self.assertEqual(service.load_writing_style("style-book"), style)


if __name__ == "__main__":
    unittest.main()
