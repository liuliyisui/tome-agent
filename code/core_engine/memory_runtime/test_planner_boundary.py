"""Real planner wire failures, repaired without dropping events or clues."""

import copy
import json
import unittest

from inf_writer.agents import JsonAgent, validate
from inf_writer.domain import ContractError
from inf_writer.models import ModelReply
from inf_writer.narrative_context import normalize_planner_metadata, parse_planner_json
from memory_runtime.reference_choices import compile_plan
from memory_runtime.test_event_first import ROOT


class PlannerBoundaryTests(unittest.TestCase):
    def test_actual_previously_rejected_replies_reach_state_preparation(self):
        from memory_runtime.event_first import normalize_plan, prepare
        from memory_runtime.event_references import catalogue

        run = ROOT / "runs/joint_6000_20261026_a"
        request = json.loads(
            (run / "call_014.request.json").read_text(encoding="utf-8")
        )["payload"]
        snapshots = (
            json.loads(p.read_text(encoding="utf-8"))["book"]
            for p in sorted((run / "working").glob("checkpoint_*.json"), reverse=True)
        )
        book = next(
            b
            for b in snapshots
            if len(b["chapters"]) == 1 and not b.get("prepared_events")
        )
        before = copy.deepcopy(book["writing_state"])
        for number in (15, 16, 17, 18):
            value, _ = parse_planner_json(self.raw(number))
            value, _ = normalize_planner_metadata(value)
            value.pop("narrative_plan", None)
            compiled = compile_plan(
                value,
                request["reference_choices"],
                2,
                reference_records=request["event_plan_state"]["records"],
                require_target_identity=True,
            )
            normalized, _ = normalize_plan(
                compiled, book["writing_state"], 2, references=catalogue(book)
            )
            if number in (15, 16):
                with self.assertRaises(ContractError):
                    prepare(
                        book["writing_state"], normalized, 2, references=catalogue(book)
                    )
            else:
                self.assertEqual(
                    len(
                        prepare(
                            book["writing_state"],
                            normalized,
                            2,
                            references=catalogue(book),
                        )["commit"]["scenes"]
                    ),
                    3,
                )
        self.assertEqual(book["writing_state"], before)

    def test_known_reference_wrappers_preserve_identity_and_explicit_revision(self):
        plan = {
            "number": 1,
            "title": "章",
            "brief": "动作",
            "future_updates": [],
            "scenes": [
                {
                    "purpose": "调查",
                    "participants": ["甲"],
                    "beats": [
                        {
                            "statement": "甲核对材料。",
                            "assertion_scope": "performed_action",
                            "requires": [],
                            "changes": [],
                        }
                    ],
                }
            ],
        }
        ref = "evidence_object:existing"
        action = plan["scenes"][0]["beats"][0]
        for value in (dict(**{ref: 3}), "{" + ref + "}"):
            action["requires"] = [value]
            result = compile_plan(plan, [ref], 1)
            dependency = result["scenes"][0]["beats"][0]["requires"][0]
            self.assertEqual(dependency["reference_id"], ref)
            if isinstance(value, dict):
                self.assertEqual(dependency["record_revision"], 3)
        for value in (
            "{evidence_object:invented}",
            {ref: True},
            {ref: 0},
            {"evidence_object:invented": 1},
        ):
            action["requires"] = [value]
            with self.subTest(value=value), self.assertRaises(ContractError):
                compile_plan(plan, [ref], 1)

    def raw(self, number):
        return json.loads(
            (
                ROOT / f"runs/joint_6000_20261026_a/call_{number:03d}.response.json"
            ).read_text(encoding="utf-8")
        )["content"]

    def test_actual_four_valid_plans_keep_every_event_and_misplaced_thread(self):
        for number in (15, 16, 17, 18):
            raw = self.raw(number)
            parsed, parse_notes = parse_planner_json(raw)
            original = copy.deepcopy(parsed)
            normalized, notes = normalize_planner_metadata(parsed)
            validate("planner", normalized)
            self.assertEqual(normalized["scenes"], original["scenes"])
            self.assertEqual(normalized["future_updates"], original["future_updates"])
            self.assertEqual(
                normalized["narrative_plan"]["threads"], original["threads"]
            )
            self.assertEqual(parsed, original)
            self.assertNotIn("threads", normalized)
            self.assertTrue(notes)
            self.assertEqual(bool(parse_notes), number == 15)

    def test_complete_object_rejects_duplicate_keys_second_objects_and_text(self):
        for raw in (
            '{"number":1,"number":2}}',
            "{}{}",
            "{}解释",
            "{} }}",
            "[]}",
            '{"number":1',
        ):
            with self.subTest(raw=raw), self.assertRaises(ContractError):
                parse_planner_json(raw)

    def test_conflicting_designs_and_unknown_fields_are_not_silently_removed(self):
        with self.assertRaises(ContractError):
            normalize_planner_metadata(
                {"narrative_plan": {"threads": ["甲"]}, "threads": ["乙"]}
            )
        value, _ = normalize_planner_metadata(
            {
                "number": 1,
                "title": "章",
                "brief": "内容",
                "future_updates": [],
                "unexpected": "不能删除",
            }
        )
        with self.assertRaises(ContractError):
            validate("planner", value)

    def test_actual_incomplete_first_reply_still_requires_scenes(self):
        parsed, _ = parse_planner_json(self.raw(14))
        with self.assertRaises(ContractError):
            compile_plan(parsed, [], 2)

    def test_formal_agent_records_both_normalizations_without_an_extra_call(self):
        raw = self.raw(15)

        class Reply:
            def __init__(self):
                self.calls = 0

            def complete(self, r):
                self.calls += 1
                return ModelReply(raw, 1, 1, 0)

        provider = Reply()
        trace = []
        result = JsonAgent(
            "planner", provider, compact_narrative=True, max_format_retries=0
        ).run({}, trace)
        self.assertTrue(result["scenes"])
        self.assertEqual(provider.calls, 1)
        self.assertEqual(trace[0]["raw_output"], raw)
        self.assertEqual(
            {n["rule"] for n in trace[0]["normalizations"]},
            {"planner_surplus_closing_brace", "planner_narrative_field_relocated"},
        )


if __name__ == "__main__":
    unittest.main()
