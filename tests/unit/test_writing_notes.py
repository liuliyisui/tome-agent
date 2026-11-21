"""Notes must describe saved evidence without inventing successful revisions."""

import copy
import tempfile
import unittest
from pathlib import Path

from inf_backend import writing_notes


def chapter(number=1, text="甲收好来信。\n他推门离开。", title="来信"):
    return {
        "number": number,
        "title": title,
        "text": text,
        "event_commit": {
            "scenes": [
                {"purpose": "推进调查", "beats": [{"statement": "甲读了来信。"}]}
            ]
        },
    }


def book(chapters):
    return {
        "state": {
            "chapters": chapters,
            "plan": {"1": {"brief": "读信后决定出发"}},
            "outcomes": [
                {
                    "chapter_number": 1,
                    "memory_update_status": "APPLIED",
                    "story_review_status": "DISABLED",
                }
            ],
        }
    }


class WritingNotesTests(unittest.TestCase):
    def test_summary_uses_saved_plot_and_does_not_claim_review_passed(self):
        value = book([chapter()])
        original = copy.deepcopy(value)
        note = writing_notes.for_book(value, {})["1"]
        self.assertEqual(note["brief"], "读信后决定出发")
        self.assertEqual(note["scenes"][0]["purpose"], "推进调查")
        self.assertEqual(note["scenes"][0]["events"], ["甲读了来信。"])
        self.assertIn("未启用", note["review"])
        self.assertEqual(note["context"], {})
        self.assertIn("历史章节", note["provenance"])
        self.assertEqual(value, original)

    def test_generation_context_is_snapshotted_and_bound_to_text_and_title(self):
        value = chapter()
        context = {
            "model": "old-model",
            "style_instructions": "短句",
            "skills": ["悬疑"],
        }
        record = writing_notes.capture(value, context)
        context["model"] = "new-model"
        note = writing_notes.summarize(value, {}, record)
        self.assertEqual(note["context"]["model"], "old-model")
        self.assertEqual(note["operation"], "generate")
        self.assertIsNone(note["comparison"])
        for field in ("text", "title"):
            changed = {**value, field: value[field] + "新"}
            self.assertEqual(
                writing_notes.summarize(changed, {}, record)["context"], {}
            )

    def test_regeneration_has_real_diff_and_preserves_feedback(self):
        old = chapter(text="保留的段落。\n原来的对话。\n离开。")
        new = chapter(text="保留的段落。\n新的对白。\n离开。\n新增尾声。", title="出发")
        record = writing_notes.capture(new, {"author_feedback": "修改对白"}, old)
        diff = record["comparison"]
        self.assertEqual((diff["updated"], diff["added"], diff["removed"]), (1, 1, 0))
        self.assertEqual(diff["examples"][0]["before"], "原来的对话。")
        self.assertTrue(diff["title_changed"])
        self.assertEqual(record["context"]["author_feedback"], "修改对白")

    def test_identical_revision_does_not_invent_changes(self):
        value = chapter()
        diff = writing_notes.compare(value, value)
        self.assertFalse(diff["text_changed"])
        self.assertEqual(diff["examples"], [])
        self.assertEqual(diff["updated"], 0)

    def test_whitespace_only_revision_is_identified(self):
        value = chapter(text="第一段。\n第二段。")
        diff = writing_notes.compare(value, chapter(text="  第一段。\r\n\r\n第二段。"))
        self.assertTrue(diff["format_only"])
        self.assertEqual(diff["updated"], 0)

    def test_examples_are_limited_and_deletions_have_no_new_paragraph(self):
        old = chapter(text="\n".join(f"原段{i}" for i in range(10)))
        new = chapter(
            text="\n".join(f"新段{i}" if i % 2 else f"原段{i}" for i in range(10))
        )
        self.assertEqual(len(writing_notes.compare(old, new)["examples"]), 3)
        diff = writing_notes.compare(
            chapter(text="删除。\n保留。"), chapter(text="保留。")
        )
        self.assertEqual(diff["removed"], 1)
        self.assertIsNone(diff["examples"][0]["new_paragraph"])

    def test_length_reports_can_be_null_or_rejected(self):
        value = {
            **chapter(),
            "event_stage_sources": [
                {"length_report": None},
                {"length_report": {"adjustment": "accepted"}},
                {"length_report": {"adjustment": "kept_original_failure"}},
            ],
        }
        changes = writing_notes.summarize(value, {})["adjustments"]
        self.assertEqual(len(changes), 2)
        self.assertIn("未采用", changes[1])

    def test_missing_or_corrupt_sidecar_falls_back_to_existing_records(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "notes.json"
            self.assertEqual(writing_notes.read(path), {})
            for content in ("{broken", "[]", '{"version":9,"chapters":{}}'):
                path.write_text(content, encoding="utf-8")
                self.assertEqual(writing_notes.read(path), {})

    def test_new_revision_prunes_notes_for_invalidated_later_chapters(self):
        c1, c2 = chapter(), chapter(2)
        stored = {
            "1": writing_notes.capture(c1, {}),
            "2": writing_notes.capture(c2, {}),
        }
        revised = chapter(text="新的第一章。")
        updated = writing_notes.update(
            stored, {"chapters": [revised]}, 1, {"author_feedback": "重写"}, c1
        )
        self.assertEqual(set(updated["chapters"]), {"1"})
        self.assertEqual(updated["chapters"]["1"]["operation"], "regenerate")
        self.assertEqual(set(stored), {"1", "2"})

    def test_excerpt_and_scene_limits_keep_long_notes_bounded(self):
        value = chapter()
        value["event_commit"]["scenes"] *= 8
        state = {"plan": {"1": {"brief": "甲" * 900}}}
        note = writing_notes.summarize(value, state)
        self.assertEqual(len(note["scenes"]), 6)
        self.assertEqual(note["scenes_omitted"], 2)
        self.assertLessEqual(len(note["brief"]), 501)


if __name__ == "__main__":
    unittest.main()
