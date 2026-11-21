"""Scenario-based end-to-end flow for the long-form writing studio.

Main flow: create a book, generate two chapters, then export Markdown.
Alternate flow: a later chapter fails and the committed chapters stay
recoverable.  The model is replaced by a deterministic session fake, so the
test verifies the product workflow rather than generation quality.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inf_backend import service
from inf_backend.settings import Settings


class SuccessfulSession:
    def __init__(self, run, gateway, plan, book=None):
        self.run = Path(run)
        self.run.mkdir(parents=True, exist_ok=True)
        self.book = book or {"chapters": []}
        self.chapter_length_target = None
        self.book.setdefault("chapters", [])
        self.latest_checkpoint = self.run / "checkpoint_0.json"
        self.save()

    def save(self):
        self.latest_checkpoint.write_text(
            json.dumps(self.book, ensure_ascii=False), encoding="utf-8"
        )

    def write_next(self, instruction):
        number = len(self.book["chapters"]) + 1
        self.book["chapters"].append(
            {
                "number": number,
                "title": f"第{number}章",
                "text": f"这是第{number}章的第一段。\n\n这是第{number}章的第二段。",
            }
        )
        self.latest_checkpoint = self.run / f"checkpoint_{number}.json"
        self.save()
        return {"status": "DRAFT_UNCHECKED", "chapter_number": number}


class FailingSecondChapter(SuccessfulSession):
    def write_next(self, instruction):
        number = len(self.book["chapters"]) + 1
        if number == 2:
            return {
                "status": "NO_DRAFT",
                "chapter_number": number,
                "errors": ["模型连接超时"],
            }
        return super().write_next(instruction)


class StoryFlowEndToEndTests(unittest.TestCase):
    def setUp(self):
        self._folder = tempfile.TemporaryDirectory()
        self.books = Path(self._folder.name)
        self._patches = [
            patch.object(service, "BOOKS", self.books),
            patch.object(service.database, "enabled", return_value=False),
            patch.object(service, "StoryClosure", **{"return_value.instruction.return_value": ""}),
        ]
        for item in self._patches:
            item.start()
        self.settings = Settings(api_key="fake")
        self.book_id = "story-flow"

    def tearDown(self):
        for item in reversed(self._patches):
            item.stop()
        self._folder.cleanup()

    def create(self):
        return service.create_book(
            self.book_id,
            "灯塔手记",
            "一个人沿着海岸寻找旧灯塔",
            3,
            3000,
            settings=self.settings,
        )

    def checkpoint(self):
        book_path = self.books / self.book_id
        pointer = json.loads(
            (book_path / "longform-current.json").read_text(encoding="utf-8")
        )
        return json.loads(
            (book_path / pointer["checkpoint"]).read_text(encoding="utf-8")
        )

    def test_main_flow_create_generate_and_export_markdown(self):
        created = self.create()
        self.assertEqual(created["metadata"]["target_chapters"], 3)

        with patch.object(service, "WritingSession", SuccessfulSession):
            result = service.generate(
                self.book_id,
                count=2,
                gateway=object(),
                settings=self.settings,
            )

        chapters = result["state"]["chapters"]
        self.assertEqual([item["number"] for item in chapters], [1, 2])
        self.assertEqual(self.checkpoint()["chapters"], chapters)

        markdown = service.export_markdown(result)
        self.assertIn("# 灯塔手记", markdown)
        self.assertIn("## 第1章 第1章", markdown)
        self.assertIn("## 第2章 第2章", markdown)
        self.assertIn("　　这是第1章的第一段。", markdown)
        self.assertIn("　　这是第2章的第二段。", markdown)

    def test_closure_runs_for_each_saved_chapter_and_is_checkpointed(self):
        self.create()

        class Closure:
            def __init__(self, session):
                self.session = session
                self.session.book["story_closure"] = {"observed": []}

            def initialize(self):
                pass

            def instruction(self):
                return " 收束提示。"

            def observe(self, chapter):
                self.session.book["story_closure"]["observed"].append(chapter["number"])
                self.session.save()

        with (
            patch.object(service, "WritingSession", SuccessfulSession),
            patch.object(service, "StoryClosure", Closure),
        ):
            result = service.generate(self.book_id, count=2, gateway=object(), settings=self.settings)

        self.assertEqual(result["state"]["story_closure"]["observed"], [1, 2])
        self.assertEqual(self.checkpoint()["story_closure"]["observed"], [1, 2])

    def test_real_session_uses_closure_and_resumes_saved_state(self):
        from memory_runtime.story_closure import StoryClosure
        from memory_runtime.test_event_first import EventLocal
        from memory_runtime.test_story_closure import ClosureLocal
        from tools.testing.archived_plan_fixture import compile_archived_plan

        class EventClosure(ClosureLocal, EventLocal):
            pass

        self.create()
        provider = EventClosure()
        with (
            patch.object(service, "StoryClosure", StoryClosure),
            patch("memory_runtime.reference_choices.compile_plan", side_effect=compile_archived_plan),
        ):
            first = service.generate(self.book_id, gateway=provider, settings=self.settings)
            second = service.generate(self.book_id, gateway=provider, settings=self.settings)

        self.assertEqual(len(second["state"]["chapters"]), 2)
        self.assertTrue(first["state"]["story_closure"]["obligations"])
        self.assertEqual(len([r for r in provider.requests if r.role == "closure_planner"]), 1)
        self.assertFalse(any(r.role == "reviewer" for r in provider.requests))
        self.assertEqual(
            service.load_longform(self.book_id)["state"]["story_closure"],
            second["state"]["story_closure"],
        )

    def test_alternate_flow_failure_keeps_committed_chapters(self):
        self.create()
        with patch.object(service, "WritingSession", FailingSecondChapter):
            with self.assertRaisesRegex(RuntimeError, "第2章未生成正文"):
                service.generate(
                    self.book_id,
                    count=2,
                    gateway=object(),
                    settings=self.settings,
                )

        saved = self.checkpoint()
        self.assertEqual([item["number"] for item in saved["chapters"]], [1])
        self.assertEqual(
            saved["chapters"][0]["text"], "这是第1章的第一段。\n\n这是第1章的第二段。"
        )

    def test_chapter_count_cannot_exceed_remaining_chapters(self):
        self.create()
        with patch.object(service, "WritingSession", SuccessfulSession):
            for count in (0, 4):
                with self.subTest(count=count):
                    with self.assertRaises(ValueError):
                        service.generate(
                            self.book_id,
                            count=count,
                            gateway=object(),
                            settings=self.settings,
                        )
        self.assertEqual(list(self.books.glob(self.book_id + "/longform-runs/*")), [])


if __name__ == "__main__":
    unittest.main()
