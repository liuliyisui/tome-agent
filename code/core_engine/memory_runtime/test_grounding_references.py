"""Program-owned source references remove model quotation transcription failures."""

import copy
import json
import unittest
from unittest.mock import patch

from inf_writer.domain import ContractError, canonical, digest, evidence_segments
from inf_writer.models import ModelReply

from memory_runtime.engine import MemoryEngine
from memory_runtime.event_first import project_memory
from memory_runtime.projection_grounding import _decision, ground, verify_grounding
from memory_runtime.test_projection_grounding import ROOT, Grounded, chapter


def source_only(rows):
    rows = copy.deepcopy(rows)
    for row in rows:
        for support in row.get("support", []):
            support.pop("quote", None)
    return rows


class GroundingReferenceTests(unittest.TestCase):
    def test_actual_chapter_nine_source_choice_commits_in_one_reply(self):
        run = ROOT / "runs/event_first_30000_20261028_threads_b"
        book = json.loads((run / "final_state.json").read_text(encoding="utf-8"))
        original = copy.deepcopy(book["memory"])
        raw = json.loads(
            json.loads((run / "call_256.response.json").read_text(encoding="utf-8"))[
                "content"
            ]
        )
        selected = [r for r in raw["decisions"] if r["candidate_position"] == 19]
        ref = "event:c0009.a0015"
        segment = evidence_segments(book["chapters"][8]["text"])[21]["text"]
        self.assertNotIn(selected[0]["support"][0]["quote"], segment)
        calls = []

        class Replay:
            def complete(self, request):
                calls.append(request)
                self_test.assertEqual(
                    request.payload["support_protocol"], "source_reference_only_v2"
                )
                prior = request.payload["prior_supported_interpretations"]["19"]
                self_test.assertNotIn("quote", prior["support"][0])
                return ModelReply(
                    canonical({"decisions": source_only(selected)}), 1, 1, 0
                )

        self_test = self
        trace = []
        result = ground(
            original, book["chapters"], 9, Replay(), trace, reconsider_absent=True
        )
        self.assertEqual(len(calls), 1)
        self.assertNotIn("9", result["projection_omissions"])
        decision = result["projection_grounding"]["9"]["decisions"][ref]
        self.assertEqual(decision["stored_claim"], segment)
        self.assertIn("掌心在封皮上压了一下", decision["stored_claim"])
        self.assertFalse(result["projection_grounding"]["9"]["binding_repairs"])
        self.assertEqual(trace[0]["reviewed_positions"], [19])
        self.assertTrue(trace[0]["source_bindings"])
        self.assertTrue(verify_grounding(result, book["chapters"]))
        self.assertEqual(original, book["memory"])

    def test_reference_binding_keeps_attribution_negation_and_original_text(self):
        c = chapter()
        c["text"] = "有人说甲已经签字，核实后发现并未签字。"
        c["sha256"] = digest(c["text"])
        c["realization_template"] = c["text"]
        memory = project_memory(MemoryEngine.empty(), [c], 1, [])
        p = Grounded(lambda rows, n: {"decisions": source_only(rows)})
        trace = []
        result = ground(memory, [c], 1, p, trace)
        decisions = result["projection_grounding"]["1"]["decisions"].values()
        self.assertTrue(all(d["stored_claim"] == c["text"] for d in decisions))
        self.assertTrue(verify_grounding(result, [c]))
        self.assertEqual(p.ground_calls, 1)

    def test_invalid_boolean_and_missing_positions_stay_pending(self):
        for bad in (True, 0, -1, 999, None):
            with self.subTest(position=bad):
                c = chapter()
                memory = project_memory(MemoryEngine.empty(), [c], 1, [])

                def reply(rows, n):
                    rows = source_only(rows)
                    for row in rows:
                        row["support"][0]["evidence_position"] = bad
                    return {"decisions": rows}

                trace = []
                result = ground(memory, [c], 1, Grounded(reply), trace)
                self.assertTrue(result["projection_omissions"])
                self.assertFalse(any(e.get("reviewed_positions") for e in trace))
                self.assertTrue(verify_grounding(result, [c]))

    def test_saved_quotes_and_legacy_invented_quotes_remain_strict(self):
        raw = {
            "candidate_position": 1,
            "outcome": "matched",
            "support": [{"evidence_position": 1, "quote": "甲已经签字。"}],
            "reason": "原文",
        }
        with self.assertRaises(ContractError):
            _decision(raw, {1: {"kind": "state"}}, [{"text": "甲没有签字。"}])
        with self.assertRaises(ContractError):
            _decision(
                dict(raw, support=[{"evidence_position": 1}]),
                {1: {"kind": "state"}},
                [{"text": "甲没有签字。"}],
            )

    def test_failed_store_is_not_counted_as_effective_review(self):
        c = chapter()
        memory = project_memory(MemoryEngine.empty(), [c], 1, [])
        p = Grounded(lambda rows, n: {"decisions": source_only(rows)})
        trace = []
        with patch(
            "memory_runtime.projection_grounding._store",
            side_effect=ContractError("offline storage rejection"),
        ):
            result = ground(memory, [c], 1, p, trace)
        self.assertTrue(any(e["validated_positions"] for e in trace))
        self.assertFalse(any(e["reviewed_positions"] for e in trace))
        self.assertTrue(result["projection_omissions"])
        self.assertTrue(verify_grounding(result, [c]))


if __name__ == "__main__":
    unittest.main()
