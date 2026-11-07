"""Transport completeness, incremental scope, budgets, and basic endings."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import write_novel as cli
from inf_writer.domain import ContractError, canonical, digest
from inf_writer.models import ModelReply
from memory_runtime.continuity import empty
from memory_runtime.length_control import adjust
from memory_runtime.stage_planning import prepare_stages
from memory_runtime.story_budget import chapter_budget, closing_start, writing_units
from memory_runtime.story_closure import StoryClosure
from memory_runtime.test_event_first import EventLocal, beat, event_config, proposal
from memory_runtime.writing import (
    WritingSession,
    load_resume,
    verify_stage_realizations,
)


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=cli.ROOT / "runs")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_real_three_truncated_adjustments_keep_the_complete_original(self):
        root = cli.ROOT / "runs/event_first_30000_20261024_c"
        for number in (20, 37, 88):
            q = json.loads(
                (root / f"call_{number:03d}.request.json").read_text(encoding="utf-8")
            )
            r = json.loads(
                (root / f"call_{number:03d}.response.json").read_text(encoding="utf-8")
            )

            class Replay:
                def __init__(self, reply):
                    self.reply = reply

                def complete(self, request):
                    return ModelReply(**self.reply)

            draft = q["payload"]["current_draft"]
            book = {"goal": "小说", "constraints": []}
            saved, report = adjust(
                draft, 1, book, q["payload"]["chapter_number"], Replay(r), []
            )
            self.assertEqual(saved, draft)
            self.assertEqual(report["adjustment"], "kept_original_incomplete_reply")

    def test_overspending_does_not_turn_later_scenes_into_one_character(self):
        plan = {"chapters": 15, "target_han_chars": 30000}
        budget = chapter_budget(plan, [{"text": "甲" * 5000} for _ in range(9)], 10)
        self.assertTrue(budget["budget_conflict"])
        self.assertGreaterEqual(budget["target"], 1000)
        units = writing_units(9, budget["target"], budget["minimum_scene_han"])
        self.assertGreater(min(u["target_han_chars"] for u in units), 1)
        self.assertEqual(sum(u["target_han_chars"] for u in units), budget["target"])
        self.assertEqual(
            [i for u in units for i in u["packet_indexes"]], list(range(9))
        )

    def test_ending_reserve_survives_early_budget_pressure(self):
        plan = {"chapters": 15, "target_han_chars": 30000}
        first = chapter_budget(plan, [], 1)
        self.assertEqual(closing_start(plan), 12)
        self.assertEqual(first["ending_reserve_han"], 9000)
        closing = chapter_budget(plan, [{"text": "甲" * 26000}], 12)
        self.assertGreaterEqual(closing["target"], 2250)
        self.assertTrue(closing["budget_conflict"])

    def prepared(self):
        raw = proposal()
        raw["brief"] = "整章从开头写到结尾的完整故事"
        raw["scenes"] = [
            {
                "id": f"s{i:04d}",
                "purpose": purpose,
                "participants": ["甲"],
                "beats": [beat(identifier=f"b{i}", statement=statement, changes=[])],
            }
            for i, purpose, statement in [
                (1, "只开门", "甲推开门。"),
                (2, "只递信", "甲递出信。"),
                (3, "只离开", "甲关门离开。"),
            ]
        ]
        return prepare_stages(empty(), raw, 1, {})

    def test_incremental_payload_and_grouped_transactions_roundtrip(self):
        class Incremental(EventLocal):
            def complete(self, request):
                if request.role == "writer":
                    self.requests.append(copy.deepcopy(request))
                    if "current_draft" in request.payload:
                        return ModelReply(request.payload["current_draft"], 1, 1, 0)
                    return ModelReply(
                        canonical({"new_stage_text": "甲推开门，递出信后关门离开。"}),
                        1,
                        1,
                        0,
                    )
                return super().complete(request)

        provider = Incremental()
        session = WritingSession(
            self.root / "book", provider, cli.validate_config(event_config(1))
        )
        session.chapter_length_target = 1000
        session.book["length_budget"] = {"chapters": {"1": {"minimum_scene_han": 600}}}
        session.book["prepared_events"]["1"] = self.prepared()
        row = session.write_next("整章目标30000字，必须从头写到结尾")
        self.assertIsNone(row["stop_reason"])
        writers = [
            r
            for r in provider.requests
            if r.role == "writer" and "frozen_events" in r.payload
        ]
        self.assertEqual(len(writers), 1)
        p = writers[0].payload
        self.assertNotIn("earlier_stage_prose", p)
        self.assertNotIn("30000", p["instruction"])
        self.assertNotIn("整章从开头", p["chapter_plan"]["brief"])
        self.assertEqual(p["stage_task"]["target_han_chars"], 1000)
        self.assertEqual(p["output_contract"]["required"], ["new_stage_text"])
        chapter = session.book["chapters"][0]
        self.assertEqual(len(chapter["event_stage_sources"]), 1)
        self.assertEqual(
            len(chapter["event_stage_sources"][0]["source_commit_sha256s"]), 3
        )
        self.assertEqual(len(chapter["event_commit"]["stage_transactions"]), 3)
        load_resume(session.latest_checkpoint, session.plan)

    def test_unit_source_reordering_is_rejected(self):
        packet = self.prepared()
        from memory_runtime.writing_units import combined_commit

        commits = [p["commit"] for p in packet["stage_packets"]]
        packet["stage_realizations"] = [
            {
                "stage": 0,
                "text": "甲递信后离开。",
                "sha256": digest("甲递信后离开。"),
                "source_stages": [0, 1, 2],
                "source_commit_sha256s": [c["sha256"] for c in commits],
                "commit_sha256": combined_commit(commits)["sha256"],
            }
        ]
        verify_stage_realizations(packet)
        packet["stage_realizations"][0]["source_commit_sha256s"].reverse()
        with self.assertRaises(ContractError):
            verify_stage_realizations(packet)

    def test_stage_adjustment_never_requests_a_whole_chapter_rewrite(self):
        requests = []

        class Shorten:
            def complete(self, r):
                requests.append(r)
                return ModelReply("甲" * 100, 1, 1, 0)

        adjust(
            "甲" * 200,
            100,
            {"goal": "小说", "constraints": []},
            1,
            Shorten(),
            [],
            stage_task={"purpose": "递信"},
        )
        self.assertIn("本单元", requests[0].payload["instruction"])
        self.assertNotIn("将本章", requests[0].payload["instruction"])

    def closure(self, ending, ended=True):
        requests = []

        class Closure:
            def complete(self, r):
                requests.append(r)
                if r.role == "closure_planner":
                    return ModelReply(
                        canonical(
                            {
                                "obligations": [
                                    {
                                        "question": "勇者与恶龙的冲突如何结束？",
                                        "acceptance": "主线有明确终局，开放式也可。",
                                    }
                                ]
                            }
                        ),
                        1,
                        1,
                        0,
                    )
                rows = [
                    {
                        "id": o["id"],
                        "status": "resolved" if ended else "pending",
                        "reason": "正文结果",
                        "evidence": [{"source_choice": 1}] if ended else [],
                    }
                    for o in r.payload["obligations"]
                ]
                return ModelReply(
                    canonical(
                        {
                            "obligations": rows,
                            "new_obligations": [],
                            "mainline_ended": ended and r.payload["final_check"],
                        }
                    ),
                    1,
                    1,
                    0,
                )

        session = SimpleNamespace(
            plan={"goal": "勇者斗恶龙", "constraints": [], "chapters": 4},
            gateway=Closure(),
            book={"goal": "勇者斗恶龙", "chapters": []},
            _save=lambda *args: None,
        )
        controller = StoryClosure(session)
        controller.initialize()
        for i in range(1, 5):
            chapter = {"number": i, "text": "勇者出发调查恶龙。" if i < 4 else ending}
            session.book["chapters"].append(chapter)
            controller.observe(chapter)
            if i < 4:
                self.assertFalse(any(r.role == "closure_reviewer" for r in requests))
        return controller, requests

    def test_victory_defeat_and_open_terminal_are_basic_endings(self):
        for ending in (
            "恶龙战败，勇者回乡。",
            "勇者战败，城池沦陷，远征结束。",
            "双方停战，勇者退隐，恶龙未来去向留白。",
        ):
            controller, requests = self.closure(ending)
            self.assertTrue(controller.passed())
            self.assertEqual(sum(r.role == "closure_reviewer" for r in requests), 1)
            prompt = next(r.system for r in requests if r.role == "closure_reviewer")
            self.assertIn("开放式结局可以通过", prompt)
            self.assertIn("或保持或", prompt)

    def test_stopping_before_the_decisive_conflict_is_not_an_ending(self):
        controller, _ = self.closure("勇者拔剑，准备明天挑战恶龙。", ended=False)
        self.assertFalse(controller.passed())

    def test_optional_threads_are_preserved_without_twelve_item_storage_cap(self):
        controller, _ = self.closure("双方签订停战约定，冲突终止。")
        for i in range(20):
            controller.add_obligations(
                [{"question": f"支线{i}", "acceptance": "将来可展开"}]
            )
        controller.refresh_status()
        self.assertEqual(len(controller.state["obligations"]), 21)
        self.assertTrue(controller.passed())

    def test_plain_transport_continues_from_saved_fragment_without_restarting(self):
        from memory_runtime.completion import continue_prose

        requests = []
        snapshots = []

        class Partial:
            def complete(self, r):
                requests.append(r)
                if len(requests) == 1:
                    return ModelReply("甲递出信，乙", 1, 1, 0, "length")
                return ModelReply("接过信后离开。", 1, 1, 0, "stop")

        book = {"goal": "递信", "constraints": [], "chapters": []}
        result = continue_prose(
            Partial(),
            book,
            "递信",
            1,
            [],
            stage_task={"unit_number": 1},
            save_progress=lambda: snapshots.append(copy.deepcopy(book)),
        )
        self.assertEqual(result, "甲递出信，乙接过信后离开。")
        self.assertEqual(requests[-1].payload["incomplete_prose_tail"], "甲递出信，乙")
        self.assertTrue(snapshots[0]["prose_fragments"])
        self.assertFalse(book["prose_fragments"])

    def test_bounded_incomplete_output_keeps_raw_data_and_only_complete_sentences(self):
        from memory_runtime.completion import continue_prose

        class ForeverPartial:
            def complete(self, r):
                return ModelReply("甲递信。尚未", 1, 1, 0, "length")

        book = {"goal": "递信", "constraints": [], "chapters": []}
        text = continue_prose(ForeverPartial(), book, "递信", 1, [])
        self.assertTrue(text.endswith("。"))
        self.assertTrue(book["prose_fragments"])
        self.assertEqual(
            book["prose_output_warnings"][0]["reason"],
            "OUTPUT_LIMIT_AFTER_BOUNDED_CONTINUATION",
        )

    def test_partial_stage_resume_skips_whole_stage_regeneration(self):
        class TailOnly(EventLocal):
            def complete(self, r):
                if r.role == "writer":
                    self.requests.append(copy.deepcopy(r))
                    self.assert_tail = r.payload.get("incomplete_prose_tail")
                    return ModelReply("把信递出后离开。", 1, 1, 0)
                return super().complete(r)

        provider = TailOnly()
        session = WritingSession(
            self.root / "resume", provider, cli.validate_config(event_config(1))
        )
        session.book["prepared_events"]["1"] = self.prepared()
        session.book["prose_fragments"] = {
            "1:1": {
                "chapter": 1,
                "unit": 1,
                "status": "PENDING",
                "text": "甲推开门，",
                "sha256": digest("甲推开门，"),
            }
        }
        row = session.write_next("递信")
        self.assertIsNone(row["stop_reason"])
        self.assertEqual(provider.requests[0].role, "writer")
        self.assertEqual(
            provider.requests[0].payload["incomplete_prose_tail"], "甲推开门，"
        )
        self.assertTrue(
            session.book["chapters"][0]["text"].startswith("甲推开门，把信递出后离开。")
        )
        load_resume(session.latest_checkpoint, session.plan)


if __name__ == "__main__":
    unittest.main()
