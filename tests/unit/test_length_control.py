"""Length-control tolerance boundaries and degradation paths.

``adjust`` keeps a draft when its Han-character count already lies inside the
10% tolerance band and only calls the model outside it.  These tests pin that
rule at both edges and verify that every failure path returns the original
draft instead of losing prose.
"""

import unittest
from unittest.mock import patch

from memory_runtime import length_control


class Reply:
    def __init__(self, content, finish_reason="stop"):
        self.content = content
        self.finish_reason = finish_reason
        self.input_tokens = 1
        self.output_tokens = 1
        self.cost_usd = 0.0


class FakeGateway:
    def __init__(self, reply=None, error=None):
        self.reply = reply
        self.error = error
        self.requests = []

    def complete(self, request):
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return self.reply


def han(text, count):
    return text * count


def book(constraints=None):
    return {
        "goal": "写一个寻找灯塔的故事",
        "constraints": constraints or [],
        "prepared_events": {},
        "narrative_planning": {},
    }


class LengthControlTests(unittest.TestCase):
    def adjust(self, draft, target, gateway):
        trace = []
        with (
            patch("memory_runtime.narrative_planning.context", return_value={}),
            patch(
                "memory_runtime.narrative_planning.advance_writer_context",
                return_value={},
            ),
        ):
            result = length_control.adjust(draft, target, book(), 1, gateway, trace)
        return result, trace

    def test_count_is_number_of_han_characters_only(self):
        cases = (
            ("", 0),
            ("你", 1),
            ("你好", 2),
            ("你好，世界！", 4),
            ("abc123", 0),
            ("你好abc", 2),
            ("㐀", 1),
            ("\U00020000", 0),
        )
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(length_control.han_count(text), expected)

    def test_lower_tolerance_boundary_is_kept(self):
        draft = han("汉", 900)
        gateway = FakeGateway(Reply(draft))
        result, trace = self.adjust(draft, 1000, gateway)
        self.assertEqual(result[0], draft)
        self.assertEqual(result[1]["adjustment"], "not_needed")
        self.assertEqual(gateway.requests, [])
        self.assertEqual(trace, [])

    def test_just_below_lower_boundary_triggers_adjustment(self):
        draft = han("汉", 899)
        gateway = FakeGateway(Reply(han("汉", 1000)))
        result, _ = self.adjust(draft, 1000, gateway)
        self.assertEqual(len(gateway.requests), 1)
        self.assertEqual(result[1]["adjustment"], "accepted")

    def test_upper_tolerance_boundary_is_kept(self):
        draft = han("汉", 1100)
        gateway = FakeGateway(Reply(draft))
        result, _ = self.adjust(draft, 1000, gateway)
        self.assertEqual(result[0], draft)
        self.assertEqual(result[1]["adjustment"], "not_needed")
        self.assertEqual(gateway.requests, [])

    def test_just_above_upper_boundary_triggers_adjustment(self):
        draft = han("汉", 1101)
        gateway = FakeGateway(Reply(han("汉", 1000)))
        result, _ = self.adjust(draft, 1000, gateway)
        self.assertEqual(len(gateway.requests), 1)
        self.assertEqual(result[1]["adjustment"], "accepted")

    def test_tiny_target_uses_a_non_empty_band(self):
        for actual in (1, 2):
            with self.subTest(actual=actual):
                draft = han("汉", actual)
                gateway = FakeGateway(Reply(draft))
                result, _ = self.adjust(draft, 1, gateway)
                self.assertEqual(result[1]["adjustment"], "not_needed")
                self.assertEqual(gateway.requests, [])

    def test_reply_closer_to_target_is_accepted(self):
        draft = han("汉", 500)
        improved = han("汉", 1000)
        result, trace = self.adjust(draft, 1000, FakeGateway(Reply(improved)))
        self.assertEqual(result[0], improved)
        self.assertEqual(result[1]["after"], 1000)
        self.assertEqual(result[1]["adjustment"], "accepted")
        self.assertEqual(trace[0]["mode"], "length_adjustment")

    def test_reply_further_from_target_is_discarded(self):
        draft = han("汉", 500)
        worse = han("汉", 400)
        result, _ = self.adjust(draft, 1000, FakeGateway(Reply(worse)))
        self.assertEqual(result[0], draft)
        self.assertEqual(result[1]["adjustment"], "kept_original_no_improvement")

    def test_overflowing_context_keeps_original_without_calling_model(self):
        draft = han("汉", 500)
        gateway = FakeGateway(Reply(han("汉", 1000)))
        trace = []
        with (
            patch("memory_runtime.narrative_planning.context", return_value={}),
            patch(
                "memory_runtime.narrative_planning.advance_writer_context",
                return_value={},
            ),
        ):
            result = length_control.adjust(
                draft,
                1000,
                book([han("约", 90000)]),
                1,
                gateway,
                trace,
            )
        self.assertEqual(result[0], draft)
        self.assertEqual(result[1]["adjustment"], "kept_original_context_limit")
        self.assertEqual(gateway.requests, [])

    def test_model_failure_keeps_original(self):
        draft = han("汉", 500)
        gateway = FakeGateway(error=RuntimeError("offline"))
        result, _ = self.adjust(draft, 1000, gateway)
        self.assertEqual(result[0], draft)
        self.assertEqual(result[1]["adjustment"], "kept_original_failure")
        self.assertEqual(result[1]["error_type"], "RuntimeError")

    def test_incomplete_reply_keeps_original(self):
        draft = han("汉", 500)
        gateway = FakeGateway(Reply(han("汉", 1000), finish_reason="length"))
        result, _ = self.adjust(draft, 1000, gateway)
        self.assertEqual(result[0], draft)
        self.assertEqual(result[1]["adjustment"], "kept_original_incomplete_reply")
        self.assertEqual(result[1]["finish_reason"], "length")

    def test_empty_reply_keeps_original(self):
        draft = han("汉", 500)
        result, _ = self.adjust(draft, 1000, FakeGateway(Reply("   ")))
        self.assertEqual(result[0], draft)
        self.assertEqual(result[1]["adjustment"], "kept_original_no_improvement")


if __name__ == "__main__":
    unittest.main()
