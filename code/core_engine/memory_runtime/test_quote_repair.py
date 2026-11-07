"""Quote-format recovery must not become a false narrative absence."""

import copy
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from inf_writer.domain import ContractError, canonical
from inf_writer.models import ModelReply
from memory_runtime.engine import MemoryEngine
from memory_runtime.event_first import project_memory
from memory_runtime.projection_grounding import (
    _decision,
    ground,
    retryable_chapters,
    verify_grounding,
)
from memory_runtime.test_projection_grounding import ROOT, Grounded, chapter
from memory_runtime.writing import WritingSession


class QuoteRepairTests(unittest.TestCase):
    def test_actual_four_false_negatives_bind_first_reply_in_one_call(self):
        run = ROOT / "runs/joint_6000_20261026_b"
        book = json.loads((run / "final_state.json").read_text(encoding="utf-8"))
        raw = json.loads(
            json.loads((run / "call_022.response.json").read_text(encoding="utf-8"))[
                "content"
            ]
        )
        expected = set(book["memory"]["projection_omissions"]["3"])
        original = copy.deepcopy(book["memory"])

        class Replay:
            calls = 0

            def complete(self, request):
                self.calls += 1
                selected = {
                    r["candidate_position"] for r in request.payload["candidates"]
                }
                return ModelReply(
                    canonical(
                        {
                            "decisions": [
                                d
                                for d in raw["decisions"]
                                if d["candidate_position"] in selected
                            ]
                        }
                    ),
                    1,
                    1,
                    0,
                )

        provider = Replay()
        trace = []
        result = ground(
            original, book["chapters"], 3, provider, trace, reconsider_absent=True
        )
        self.assertEqual(provider.calls, 1)
        self.assertNotIn("3", result.get("projection_omissions", {}))
        self.assertGreaterEqual(len(trace[0]["quote_repairs"]), 7)
        for ref in expected:
            self.assertIn(
                result["projection_grounding"]["3"]["decisions"][ref]["outcome"],
                ("matched", "partial"),
            )
        self.assertTrue(verify_grounding(result, book["chapters"]))
        self.assertEqual(original, book["memory"])

    def test_negative_format_retry_requires_an_independent_semantic_review(self):
        c = chapter()
        memory = project_memory(MemoryEngine.empty(), [c], 1, [])

        def behavior(rows, attempt):
            if attempt == 1:
                for row in rows:
                    row["support"][0]["quote"] = "无法在原文定位的内容"
            else:
                rows = [
                    {
                        "candidate_position": r["candidate_position"],
                        "outcome": "absent",
                        "support": [],
                        "reason": "独立核对确认初判不成立",
                    }
                    for r in rows
                ]
            return {"decisions": rows}

        provider = Grounded(behavior)
        trace = []
        result = ground(memory, [c], 1, provider, trace)
        self.assertEqual(provider.ground_calls, 3)
        self.assertTrue(provider.requests[2].payload["independent_semantic_review"])
        self.assertFalse(trace[1]["reviewed_positions"])
        self.assertTrue(result["projection_content_gaps"])
        self.assertTrue(verify_grounding(result, [c]))

    def test_failed_independent_review_leaves_a_retryable_binding_job(self):
        c = chapter()
        memory = project_memory(MemoryEngine.empty(), [c], 1, [])

        def behavior(rows, attempt):
            if attempt == 1:
                for row in rows:
                    row["support"][0]["quote"] = "无法定位"
                return {"decisions": rows}
            if attempt == 2:
                return {
                    "decisions": [
                        {
                            "candidate_position": r["candidate_position"],
                            "outcome": "absent",
                            "support": [],
                            "reason": "错误地因引文失败否定",
                        }
                        for r in rows
                    ]
                }
            return RuntimeError("unavailable")

        result = ground(memory, [c], 1, Grounded(behavior), [])
        self.assertEqual(retryable_chapters(result), [1])
        self.assertFalse(result.get("projection_content_gaps"))
        self.assertTrue(result["projection_grounding"]["1"]["binding_repairs"])
        self.assertTrue(verify_grounding(result, [c]))

    def test_quote_recovery_keeps_negation_and_rejects_ambiguous_or_invented_text(self):
        text = "有人说甲已经在回执上签字，核实后发现并未签字。"
        raw = {
            "candidate_position": 1,
            "outcome": "matched",
            "reason": "原文说法",
            "support": [{"evidence_position": 1, "quote": "“甲已经在回执上签字”"}],
        }
        repairs = []
        result = _decision(
            raw, {1: {"kind": "state"}}, [{"text": text}], quote_repairs=repairs
        )
        self.assertEqual(result["support"][0]["quote"], text)
        self.assertIn("并未", result["support"][0]["quote"])
        for evidence in ("甲已经在回执上签字，甲已经在回执上签字。", "甲没有签字。"):
            with self.assertRaises(ContractError):
                _decision(
                    raw,
                    {1: {"kind": "state"}},
                    [{"text": evidence}],
                    quote_repairs=[],
                )
        # Restore validates exact saved quotes; it never silently repairs them.
        with self.assertRaises(ContractError):
            _decision(raw, {1: {"kind": "state"}}, [{"text": text}])

    def test_final_catchup_covers_all_chapters_and_reports_unreviewed_failures(self):
        memory = {
            "projection_omissions": {str(n): ["missing"] for n in range(1, 5)},
            "projection_grounding": {
                str(n): {"decisions": {"missing": {"outcome": "absent"}}}
                for n in range(1, 5)
            },
        }
        chapters = [
            {"title": "章", "event_commit": {"memory_projection": [{"ref": "missing"}]}}
            for _ in range(4)
        ]
        seen = []

        def revisit(value, chapters, number, gateway, trace, **kwargs):
            result = copy.deepcopy(value)
            seen.append(number)
            result["projection_grounding"][str(number)]["reconsideration_passes"] = 1
            trace.append(
                {
                    "role": "prose_memory_grounding",
                    "reviewed_positions": [] if number == 3 else [1],
                }
            )
            return result

        engine = MemoryEngine(None)
        engine.layers = SimpleNamespace(run=lambda value, *args, **kwargs: (value, {}))
        session = object.__new__(WritingSession)
        session.book = {"memory": memory, "chapters": chapters}
        session.engine = engine
        session._save = lambda *args: None
        with (
            patch("memory_runtime.projection_grounding.ground", side_effect=revisit),
            patch(
                "memory_runtime.meaning_organizer.organize",
                side_effect=lambda value, *args: value,
            ),
        ):
            session.finish_structured_memory()
        self.assertEqual(seen, [1, 2, 3, 4])
        coverage = session.book["memory"]["projection_recheck_coverage"]
        self.assertEqual(coverage["reviewed_chapters"], [1, 2, 4])
        self.assertEqual(coverage["unreviewed_chapters"], [3])


if __name__ == "__main__":
    unittest.main()
