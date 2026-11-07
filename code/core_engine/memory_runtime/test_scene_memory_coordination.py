"""Regressions for scene stitching, wrong record targets and repair starvation."""

import copy
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from inf_writer.domain import ContractError
from memory_runtime.engine import MemoryEngine
from memory_runtime.narrative_planning import design_units
from memory_runtime.reference_choices import compile_plan
from memory_runtime.test_event_first import ROOT


class CoordinationTests(unittest.TestCase):
    def test_local_repair_cannot_switch_to_another_property_of_the_same_person(self):
        from memory_runtime.plan_repair import protect_targets

        action = {
            "statement": "梁策回仓库。",
            "changes": [
                {
                    "operation": "change_fact_value",
                    "fact_ref": {
                        "record_subject": "梁策",
                        "record_property_name": "岗位",
                    },
                    "new_value": "仓库",
                }
            ],
        }
        repaired = copy.deepcopy(action)
        repaired["changes"][0]["fact_ref"]["record_property_name"] = "态度"
        with self.assertRaises(ContractError):
            protect_targets(action, repaired, [], [])
        protect_targets(action, copy.deepcopy(action), [], [])

    def test_partial_grounding_keeps_actual_quote_and_unwritten_details_separate(self):
        from memory_runtime.event_first import project_memory
        from memory_runtime.projection_grounding import ground, verify_grounding
        from memory_runtime.test_projection_grounding import Grounded, chapter

        c = chapter("甲说：“我明天登记。”")
        memory = project_memory(MemoryEngine.empty(), [c], 1, [])

        def partial(rows, attempt):
            return {
                "decisions": [
                    dict(
                        r,
                        outcome="partial",
                        unsupported_details="正文只写明天登记，尚未实际登记",
                    )
                    for r in rows
                ]
            }

        result = ground(memory, [c], 1, Grounded(partial), [])
        self.assertFalse(result.get("projection_omissions"))
        self.assertTrue(result["projection_plan_differences"]["1"])
        self.assertTrue(verify_grounding(result, [c]))
        self.assertTrue(all(r["claim"] == c["text"] for r in result["items"].values()))
        changed = copy.deepcopy(result)
        changed["projection_plan_differences"] = {}
        with self.assertRaises(ContractError):
            verify_grounding(changed, [c])

    def test_rejected_job_value_is_not_exposed_as_xuwens_current_state(self):
        from memory_runtime.projection_grounding import qualify_state_view

        book = json.loads(
            (
                ROOT
                / "runs/event_first_30000_20261025_scene_progress_a/final_state.json"
            ).read_text(encoding="utf-8")
        )
        row = {
            "record_kind": "fact_record",
            "record_id": "n0012r0013",
            "subject": "许闻",
            "property_name": "抄件递交",
            "chapter": 14,
            "value": "梁策回仓库",
        }
        original = copy.deepcopy(row)
        result = qualify_state_view(book, {"records": [row]})["records"][0]
        self.assertNotIn("value", result)
        self.assertEqual(result["projection_status"], "absent")
        self.assertEqual(result["unconfirmed_plan_value"], "梁策回仓库")
        self.assertEqual(row, original)

    def test_actual_fourth_chapter_does_not_split_an_ungrouped_encounter(self):
        book = json.loads(
            (
                ROOT
                / "runs/event_first_30000_20261025_scene_progress_a/final_state.json"
            ).read_text(encoding="utf-8")
        )
        chapter = book["chapters"][3]
        design = chapter["narrative_plan"]
        self.assertNotIn("scene_blocks", design)
        packets = [
            {"stage": i, "commit": c}
            for i, c in enumerate(chapter["event_commit"]["stage_transactions"])
        ]
        original = copy.deepcopy(packets)
        units = design_units(packets, 2000, 400, design)
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0]["packet_indexes"], list(range(len(packets))))
        self.assertEqual(packets, original)
        large = design_units(packets * 5, 8000, 400, {})
        self.assertGreater(len(large), 1)
        self.assertEqual(sum(u["target_han_chars"] for u in large), 8000)

    def test_actual_wrong_document_target_cannot_accept_a_job_update(self):
        request = json.loads(
            (
                ROOT
                / "runs/event_first_30000_20261025_scene_progress_a/call_160.request.json"
            ).read_text(encoding="utf-8")
        )
        rows = request["payload"]["event_plan_state"]["records"]
        choices = request["payload"]["reference_choices"]
        wrong = next(r for r in rows if r["record_id"] == "n0012r0013")
        right = next(
            r
            for r in rows
            if r["subject"] == "梁策" and r.get("attribute_label") == "岗位变动"
        )
        change = {
            "operation": "change_fact_value",
            "fact_ref": {"record_subject": "梁策", "record_property_name": "岗位变动"},
            "new_value": "暂回仓库清点",
        }
        plan = {
            "number": 14,
            "title": "调岗",
            "brief": "调岗",
            "future_updates": [],
            "scenes": [
                {
                    "purpose": "调岗",
                    "participants": ["梁策", "老吴"],
                    "beats": [
                        {
                            "statement": "老吴要求梁策回仓库。",
                            "assertion_scope": "performed_action",
                            "requires": [],
                            "changes": [change],
                        }
                    ],
                }
            ],
        }
        result = compile_plan(
            plan, choices, 14, reference_records=rows, require_target_identity=True
        )
        self.assertEqual(
            result["scenes"][0]["beats"][0]["changes"][0]["fact_ref"],
            right["reference_id"],
        )
        change["fact_ref"]["record_choice"] = choices.index(wrong["reference_id"]) + 1
        with self.assertRaises(ContractError):
            compile_plan(
                plan, choices, 14, reference_records=rows, require_target_identity=True
            )
        change["fact_ref"] = {"record_choice": choices.index(wrong["reference_id"]) + 1}
        with self.assertRaises(ContractError):
            compile_plan(
                plan, choices, 14, reference_records=rows, require_target_identity=True
            )
        change["fact_ref"] = {
            "record_subject": "梁策",
            "record_property_name": "不存在的属性",
        }
        with self.assertRaises(ContractError):
            compile_plan(
                plan, choices, 14, reference_records=rows, require_target_identity=True
            )

    def test_bounded_negative_rechecks_reach_every_chapter(self):
        memory = {
            "projection_omissions": {str(n): ["missing"] for n in range(1, 5)},
            "projection_grounding": {
                str(n): {"decisions": {"missing": {"outcome": "absent"}}}
                for n in range(1, 5)
            },
        }
        seen = []

        def revisit(value, chapters, number, gateway, trace, **kwargs):
            result = copy.deepcopy(value)
            seen.append(number)
            row = result["projection_grounding"][str(number)]
            row["reconsideration_passes"] = row.get("reconsideration_passes", 0) + 1
            return result

        engine = MemoryEngine(None)
        engine.layers = SimpleNamespace(run=lambda value, *args, **kwargs: (value, {}))
        with (
            patch("memory_runtime.projection_grounding.ground", side_effect=revisit),
            patch(
                "memory_runtime.meaning_organizer.organize",
                side_effect=lambda value, *args: value,
            ),
        ):
            chapters = [
                {
                    "title": "章",
                    "event_commit": {"memory_projection": [{"ref": "missing"}]},
                }
                for _ in range(4)
            ]
            first = engine.repair_structured_memory(
                memory, chapters, [], max_chapters=2
            )
            engine.repair_structured_memory(first, chapters, [], max_chapters=2)
        self.assertEqual(seen, [1, 2, 3, 4])
        self.assertNotIn("reconsideration_passes", memory["projection_grounding"]["1"])


if __name__ == "__main__":
    unittest.main()
