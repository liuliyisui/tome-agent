"""Chapter titles must never echo writing instructions like 续写XXX."""

import unittest

from inf_writer.agents import validate
from inf_writer.domain import chapter_plan, sanitize_title
from memory_runtime.completion import unplanned_packet


class SanitizeTitleTests(unittest.TestCase):
    def test_strips_instruction_echo_prefixes(self):
        cases = {
            "续写第3章：暗流": "暗流",
            "续写第三章 暗流": "暗流",
            "请续写：风起": "风起",
            "继续写 新的开始": "新的开始",
            "续写《山河录》": "山河录",
            "接着创作第十二章 北境": "北境",
            "  续写暗流涌动  ": "暗流涌动",
            "续写下一章": "下一章",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(sanitize_title(raw, 7), expected)

    def test_fully_echoed_title_falls_back_to_chapter_label(self):
        self.assertEqual(sanitize_title("续写", 4), "第4章")
        self.assertEqual(sanitize_title("续写2", 2), "第2章")
        self.assertEqual(sanitize_title("续写第二章", 2), "第2章")
        self.assertEqual(sanitize_title("请继续写", 9), "第9章")
        self.assertEqual(sanitize_title("续写", None), "未命名章节")

    def test_keeps_normal_titles_untouched(self):
        for title in (
            "暗流涌动",
            "北境来信",
            "旧约",
            "风起云涌的日子",
            "第100章的约定",
        ):
            self.assertEqual(sanitize_title(title, 3), title)


class ChapterPlanTests(unittest.TestCase):
    def test_chapter_plan_sanitizes_title_without_mutating_input(self):
        original = {"number": 5, "title": "续写第5章", "brief": "推进主线"}
        plan = chapter_plan(original)
        self.assertEqual(plan["title"], "第5章")
        self.assertEqual(original["title"], "续写第5章")

    def test_planner_validate_sanitizes_current_and_future_titles(self):
        result = validate(
            "planner",
            {
                "number": 2,
                "title": "续写：夺权",
                "brief": "宫廷转折",
                "future_updates": [
                    {"number": 3, "title": "继续写第三章：远行", "brief": "北上"}
                ],
            },
        )
        self.assertEqual(result["title"], "夺权")
        self.assertEqual(result["future_updates"][0]["title"], "远行")


class UnplannedPacketTests(unittest.TestCase):
    def test_fallback_title_is_plain_chapter_label(self):
        packet = unplanned_packet({}, 6, "继续写下一章")
        self.assertEqual(packet["proposal"]["title"], "第6章")


if __name__ == "__main__":
    unittest.main()
