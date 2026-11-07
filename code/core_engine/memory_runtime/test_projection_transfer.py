"""Ground actual intermediate delivery without fabricating final receipt."""

import copy
import json
import unittest

from inf_writer.domain import canonical
from inf_writer.models import ModelReply
from memory_runtime.projection_grounding import (
    ground,
    qualify_state_view,
    verify_grounding,
)
from memory_runtime.test_event_first import ROOT


class TransferGroundingTests(unittest.TestCase):
    def source(self):
        return json.loads(
            (
                ROOT / "runs/evidence_access_20261028_d/legacy_repaired_state.json"
            ).read_text(encoding="utf-8")
        )

    def provider(self, *, omit_details=False):
        class Provider:
            def __init__(self):
                self.requests = []

            def complete(self, r):
                self.requests.append(copy.deepcopy(r))
                assert [c["candidate_position"] for c in r.payload["candidates"]] == [3]
                value = {
                    "candidate_position": 3,
                    "outcome": "partial",
                    "support": [{"evidence_position": i} for i in (2, 3, 6)],
                    "reason": "说明已写好并交老周转递，最终单位接收未确认",
                }
                if not omit_details:
                    value["unsupported_details"] = (
                        "只确认交给老周转递；档案科是否收到或回应尚未确认，不表示未收到。"
                    )
                return ModelReply(canonical({"decisions": [value]}), 1, 1, 0)

        return Provider()

    def test_actual_chapter7_backfill_stores_intermediate_transfer_and_retains_unconfirmed_end(
        self,
    ):
        book = self.source()
        before = copy.deepcopy(book)
        provider = self.provider()
        result = ground(
            book["memory"], book["chapters"], 7, provider, [], reconsider_absent=True
        )
        self.assertEqual(len(provider.requests), 1)
        self.assertNotIn("7", result.get("projection_omissions", {}))
        self.assertNotIn("7", result.get("projection_content_gaps", {}))
        decision = result["projection_grounding"]["7"]["decisions"]["facts:n0007r0001"]
        self.assertEqual(decision["outcome"], "partial")
        self.assertIn("中午老周进来取报纸，他把这张纸递过去", decision["stored_claim"])
        self.assertIn("老周把纸折成两折", decision["stored_claim"])
        self.assertNotIn("已向档案科补递", decision["stored_claim"])
        self.assertIn("facts:n0007r0001", result["projection_plan_differences"]["7"])
        self.assertTrue(
            any(
                r["ref"] == "facts:n0007r0001" and r["previous"]["outcome"] == "absent"
                for r in result["projection_grounding"]["7"]["decision_revisions"]
            )
        )
        self.assertTrue(verify_grounding(result, book["chapters"]))
        self.assertEqual(book, before)
        for key, row in before["memory"]["items"].items():
            self.assertEqual(result["items"][key], row)
        for key, journal in before["memory"]["projection_grounding"].items():
            if key != "7":
                self.assertEqual(result["projection_grounding"][key], journal)

    def test_future_state_view_hides_overstated_value_and_exposes_actual_progress_and_limit(
        self,
    ):
        book = self.source()
        book["memory"] = ground(
            book["memory"],
            book["chapters"],
            7,
            self.provider(),
            [],
            reconsider_absent=True,
        )
        row = {
            "record_kind": "fact_record",
            "record_id": "n0007r0001",
            "subject": "许闻",
            "chapter": 7,
            "value": "已向档案科补递书面说明",
        }
        wire = qualify_state_view(book, {"records": [row]})["records"][0]
        self.assertNotIn("value", wire)
        self.assertEqual(wire["projection_status"], "partial")
        self.assertEqual(wire["unconfirmed_plan_value"], row["value"])
        self.assertIn("交给老周", wire["unconfirmed_plan_details"])
        self.assertIn("递过去", wire["actual_prose_claim"])
        self.assertEqual(row["value"], "已向档案科补递书面说明")

    def test_partial_without_explicit_unsupported_details_cannot_clear_gap(self):
        book = self.source()
        result = ground(
            book["memory"],
            book["chapters"],
            7,
            self.provider(omit_details=True),
            [],
            reconsider_absent=True,
        )
        self.assertEqual(result["projection_omissions"]["7"], ["facts:n0007r0001"])
        self.assertEqual(
            result["projection_grounding"]["7"]["decisions"]["facts:n0007r0001"][
                "outcome"
            ],
            "absent",
        )
        self.assertTrue(verify_grounding(result, book["chapters"]))

    def test_absent_for_unrelated_matter_is_not_forced_to_partial(self):
        book = self.source()

        class Provider:
            def complete(self, r):
                return ModelReply(
                    canonical(
                        {
                            "decisions": [
                                {
                                    "candidate_position": 3,
                                    "outcome": "absent",
                                    "support": [],
                                    "reason": "独立复核仍判断该属性没有对应事项",
                                }
                            ]
                        }
                    ),
                    1,
                    1,
                    0,
                )

        result = ground(
            book["memory"], book["chapters"], 7, Provider(), [], reconsider_absent=True
        )
        self.assertEqual(result["projection_omissions"]["7"], ["facts:n0007r0001"])
        self.assertTrue(verify_grounding(result, book["chapters"]))


if __name__ == "__main__":
    unittest.main()
