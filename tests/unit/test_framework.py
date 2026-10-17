import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tome_agent.domain import Chapter, ChapterPlan, Story
from tome_agent.pipeline import commit_chapter
from tome_backend.storage import load_story


class FrameworkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "story.json"
        self.story = Story("测试", "测试故事", [ChapterPlan(1, "一", "出发"), ChapterPlan(2, "二", "变化")])

    def proposal(self, chapter=1, revision=0, value="2", quote="有两支火折"):
        return dict(subject="林舟", key="inventory", value=value, chapter=chapter,
                    quote=quote, expected_revision=revision)

    def first(self):
        return commit_chapter(self.story, Chapter(1, "一", "林舟有两支火折。"),
                              [self.proposal()], self.path)

    def test_history_and_resume(self):
        first = self.first()
        second = commit_chapter(first, Chapter(2, "二", "现在只剩一支。"),
            [self.proposal(2, 1, "1", "只剩一支")], self.path)
        loaded = load_story(self.path)
        self.assertEqual(loaded, second)
        self.assertEqual(loaded.next_chapter, 3)
        self.assertEqual(loaded.facts[0].value, "1")
        self.assertEqual(loaded.history[0].value, "2")
        self.assertEqual(first.facts[0].value, "2")

    def test_bad_evidence_leaves_disk_and_memory_unchanged(self):
        first = self.first()
        old = self.path.read_bytes()
        with self.assertRaises(ValueError):
            commit_chapter(first, Chapter(2, "二", "只剩一支。"),
                [self.proposal(2, 1, "1", "不存在的引文")], self.path)
        self.assertEqual(self.path.read_bytes(), old)
        self.assertEqual(len(first.chapters), 1)

    def test_stale_revision_rejected(self):
        first = self.first()
        with self.assertRaises(ValueError):
            commit_chapter(first, Chapter(2, "二", "只剩一支。"),
                [self.proposal(2, 0, "1", "只剩一支")], self.path)

    def test_failed_replace_preserves_snapshot(self):
        first = self.first()
        old = self.path.read_bytes()
        with patch("tome_backend.storage.os.replace", side_effect=OSError("disk failure")):
            with self.assertRaises(OSError):
                commit_chapter(first, Chapter(2, "二", "继续前行。"), [], self.path)
        self.assertEqual(self.path.read_bytes(), old)
        self.assertEqual(list(self.path.parent.glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
