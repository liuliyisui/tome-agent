"""Continuous scene grouping and persistent source-bound narrative intent."""

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import write_novel as cli
from inf_writer.domain import ContractError, canonical, digest
from inf_writer.models import ModelReply
from memory_runtime.narrative_planning import (
    context,
    design_units,
    handoff,
    normalize,
    publish,
    verify_ledger,
    writer_contract,
)
from memory_runtime.test_event_first import ROOT, EventLocal, event_config
from memory_runtime.writing import WritingSession, load_resume


class NarrativePlanningTests(unittest.TestCase):
    def test_chapter_progress_advances_from_actual_prose_not_opening_plan(self):
        from memory_runtime.narrative_planning import advance_writer_context

        book = {
            "chapters": [
                {
                    "number": 13,
                    "text": "许闻空手等回话。",
                    "sha256": digest("许闻空手等回话。"),
                }
            ]
        }
        payload = {
            "narrative_plan": {"scene_entry": {"opening_action": "去领取回话"}},
            "chapter_plan": {
                "narrative_plan": {"scene_entry": {"opening_action": "领取"}}
            },
            "stage_task": {
                "scene_continuity": {"scene_entry": {"opening_action": "领取"}}
            },
        }
        original = copy.deepcopy(payload)
        first = advance_writer_context(copy.deepcopy(payload), book, 14, "")
        self.assertEqual(first["chapter_handoff"]["source_chapter"], 13)
        self.assertIn("scene_entry", first["narrative_plan"])
        text = "行政科把书面回话递给许闻。他收进夹子，走出门。"
        result = advance_writer_context(payload, book, 14, text)
        self.assertEqual(result["chapter_handoff"]["source_chapter"], 14)
        self.assertEqual(result["chapter_handoff"]["prefix_sha256"], digest(text))
        self.assertEqual(result["previous_prose_tail"]["text"], text)
        self.assertNotIn("scene_entry", result["narrative_plan"])
        self.assertNotIn("scene_entry", result["chapter_plan"]["narrative_plan"])
        self.assertNotIn("scene_entry", result["stage_task"]["scene_continuity"])
        self.assertIn("scene_entry", original["narrative_plan"])

    def test_written_scene_coverage_not_reissued_as_current_work(self):
        packets = self.real_packets(14)
        prepared = {
            "stage_packets": packets,
            "narrative_plan": {"scene_entry": {"opening_action": "领取文书"}},
        }
        result = writer_contract(
            prepared, {"packet_indexes": [1]}, 2, 3, "已领取文书，许闻夹在腋下。"
        )
        self.assertEqual(
            [r["writing_status"] for r in result["chapter_event_outline"]],
            ["written", "current", "not_started"],
        )
        self.assertEqual(result["scene_entry"], {})
        self.assertEqual(
            prepared["narrative_plan"]["scene_entry"]["opening_action"], "领取文书"
        )

    def test_actual_repeated_document_case_uses_latest_unit_and_retains_prior_receipt(
        self,
    ):
        from memory_runtime.narrative_planning import advance_writer_context

        book = json.loads(
            (
                ROOT / "runs/event_first_30000_20261025_causality_a/final_state.json"
            ).read_text(encoding="utf-8")
        )
        chunks = book["chapters"][13]["event_stage_sources"]
        self.assertGreaterEqual(len(chunks), 3)
        earlier = "\n\n".join(c["text"] for c in chunks[:2])
        book["chapters"] = book["chapters"][:13]
        result = advance_writer_context({}, book, 14, earlier)
        self.assertEqual(result["chapter_handoff"]["prefix_sha256"], digest(earlier))
        self.assertEqual(result["chapter_handoff"]["closing_text"], earlier[-1600:])
        exposed = (
            result["current_chapter_progress"]["opening_text"]
            + result["previous_prose_tail"]["text"]
        )
        self.assertIn("回话", exposed)
        self.assertEqual(
            result["current_chapter_progress"]["omitted_middle_characters"], 0
        )

    def test_progress_is_bounded_and_survives_optional_history_removal(self):
        from memory_runtime.input_budget import fit, size
        from memory_runtime.narrative_planning import advance_writer_context

        text = "甲已收下文书。" * 1500 + "乙在门外等候。"
        payload = {
            "recent_chapters": [
                {"number": 1, "text": "旧场景" * 30000, "sha256": "historical"}
            ]
        }
        advance_writer_context(payload, {"chapters": []}, 2, text)
        progress = copy.deepcopy(payload["current_chapter_progress"])
        bounded = fit(payload, 27000)
        self.assertLessEqual(size(bounded), 27000)
        self.assertEqual(bounded["current_chapter_progress"], progress)
        self.assertEqual(len(progress["opening_text"]), 2000)
        self.assertEqual(bounded["previous_prose_tail"]["text"], text[-4000:])
        self.assertEqual(progress["omitted_middle_characters"], len(text) - 6000)

    def test_fallback_and_length_edit_share_progress_without_mutating_saved_prose(self):
        from memory_runtime.completion import continue_prose
        from memory_runtime.length_control import adjust

        text = "许闻已经拿到书面回话，正等梁策。"
        book = {
            "goal": "完成小说",
            "constraints": [],
            "chapters": [],
            "prepared_events": {
                "14": {
                    "narrative_plan": {"scene_entry": {"opening_action": "领取回话"}},
                    "stage_realizations": [{"text": text}],
                }
            },
        }

        class Provider:
            def __init__(self):
                self.requests = []

            def complete(self, r):
                self.requests.append(copy.deepcopy(r))
                return ModelReply("梁策沿走廊走来。" * 15, 1, 1, 0)

        provider = Provider()
        task = {
            "unit_number": 2,
            "scene_continuity": {"scene_entry": {"opening_action": "领取回话"}},
        }
        original = copy.deepcopy(book["prepared_events"])
        continue_prose(provider, book, "继续", 14, [], stage_task=task)
        adjust("梁策来了。", 100, book, 14, provider, [], stage_task=task)
        self.assertEqual(len(provider.requests), 2)
        for request in provider.requests:
            self.assertEqual(
                request.payload["chapter_handoff"]["prefix_sha256"], digest(text)
            )
            self.assertNotIn("scene_entry", request.payload["narrative_plan"])
            self.assertNotIn(
                "scene_entry", request.payload["stage_task"]["scene_continuity"]
            )
        self.assertEqual(
            provider.requests[-1].payload["revision_scope"]["mode"],
            "replace_current_unit_only",
        )
        self.assertEqual(book["prepared_events"], original)

    def test_truncated_fallback_advances_to_its_own_saved_fragment(self):
        from memory_runtime.completion import continue_prose

        text = "文书已经领取。"
        fragment = "梁策走到楼梯口。"
        book = {
            "goal": "小说",
            "constraints": [],
            "chapters": [],
            "prepared_events": {"2": {"stage_realizations": [{"text": text}]}},
        }

        class Provider:
            def __init__(self):
                self.requests = []

            def complete(self, r):
                self.requests.append(copy.deepcopy(r))
                return ModelReply(
                    fragment if len(self.requests) == 1 else "他招了招手。",
                    1,
                    1,
                    0,
                    finish_reason="length" if len(self.requests) == 1 else "stop",
                )

        provider = Provider()
        result = continue_prose(
            provider, book, "接着写", 2, [], stage_task={"unit_number": 2}
        )
        self.assertEqual(result, fragment + "他招了招手。")
        self.assertEqual(
            provider.requests[1].payload["chapter_handoff"]["prefix_sha256"],
            digest(text + "\n\n" + fragment),
        )

    def test_local_reference_repair_preserves_independent_narrative_design(self):
        from memory_runtime.test_stage_repair import public_plan

        class Provider(EventLocal):
            def complete(self, r):
                if r.role == "planner":
                    self.requests.append(copy.deepcopy(r))
                    p = public_plan()
                    p["scenes"][0]["beats"][0]["requires"] = [{"record_choice": 999}]
                    p["narrative_plan"] = {
                        "scene_entry": {
                            "previous_completion": "上一场已结束",
                            "opening_action": "接着办新事",
                        },
                        "evidence_profiles": [
                            {"topic": "当前申请单", "creation_context": "当前行政办理"}
                        ],
                    }
                    return ModelReply(canonical(p), 1, 1, 0)
                return super().complete(r)

        def repair(gateway, proposal, choices, details, trace, **kwargs):
            fixed = copy.deepcopy(proposal)
            self.assertNotIn("narrative_plan", fixed)
            fixed["scenes"][0]["beats"][0]["requires"] = []
            kwargs["validator"](fixed)
            return fixed

        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as temp:
            s = WritingSession(
                Path(temp) / "session", Provider(), cli.validate_config(event_config(1))
            )
            with patch("memory_runtime.plan_repair.repair", side_effect=repair):
                prepared = s._prepare_events("继续", 1, [])
            self.assertEqual(
                prepared["narrative_plan"]["scene_entry"]["opening_action"],
                "接着办新事",
            )
            self.assertEqual(
                prepared["narrative_plan"]["evidence_profiles"][0]["creation_context"],
                "当前行政办理",
            )
            load_resume(s.latest_checkpoint, s.plan)

    def test_actual_stale_forecasts_are_archived_but_not_execution_instructions(self):
        run = ROOT / "runs/event_first_30000_20261025_memory_b"
        cfg = json.loads(
            (
                ROOT
                / "docs/verification/event_first_30000_20261025_memory_b/test_config.json"
            ).read_text(encoding="utf-8")
        )
        for completed, forbidden in (
            (8, "副站长在事故当晚正是运行班接报人"),
            (13, "以被停岗人员的身份去交还旧图室钥匙"),
        ):
            records = [
                json.loads(p.read_text(encoding="utf-8"))
                for p in sorted((run / "working").glob("checkpoint_*.json"))
            ]
            book = next(
                r["book"]
                for r in reversed(records)
                if len(r["book"]["chapters"]) == completed
                and not r["book"].get("prepared_events")
            )
            original = copy.deepcopy(book)
            session = object.__new__(WritingSession)
            session.book = book
            session.plan = cli.validate_config(cfg)
            view = session.context("按已写事实继续", "许闻 梁策")
            self.assertNotIn("planned_next_chapters", view)
            self.assertNotIn(forbidden, canonical(view["future_outline_goals"]))
            self.assertIn(forbidden, canonical(book["plan"]))
            self.assertEqual(book, original)
            self.assertEqual(view["chapter_handoff"]["source_chapter"], completed)

    def test_document_roles_and_inference_gaps_survive_without_becoming_facts(self):
        profile = {
            "topic": "本次调阅申请退回单",
            "document_role": "驳回本次申请",
            "creation_context": "当前行政办理",
            "pertains_to": "本次申请，不是旧事故报告",
            "date_fields": [
                {
                    "field": "签收日",
                    "meaning": "当前文书流转收件日",
                    "time_frame": "现在",
                }
            ],
            "supports": ["当前申请被退回"],
            "does_not_support": ["事故当晚有人收到报信"],
            "missing_links": ["独立旧接报登记"],
        }
        raw = {
            "evidence_profiles": [None, profile],
            "inference_links": [
                {
                    "question": "旧事故是否有人接报",
                    "observation": "当前申请退回",
                    "proposed_conclusion": "现有证据不足",
                    "missing_links": ["旧报告与具体签收的对应关系"],
                    "not_established": "不能拿当前签收推旧事件",
                }
            ],
        }
        design, notes = normalize(raw, 1)
        self.assertTrue(notes)
        self.assertEqual(design["evidence_profiles"], [profile])
        text = "当前申请被退回。"
        c = {
            "number": 1,
            "text": text,
            "sha256": digest(text),
            "narrative_plan": design,
        }
        book = {"chapters": [c]}
        publish(book, c, design)
        self.assertTrue(context(book, 2)["evidence_profiles"])
        self.assertIn("不能拿当前签收", canonical(context(book, 2)))
        self.assertNotIn("writing_state", book)
        verify_ledger(book)

    def test_profile_history_keeps_original_identity_and_rejects_tampering(self):
        book = {"chapters": []}
        for n, source in ((1, "当前申请生成"), (2, "仍是本次申请；历史件另查")):
            design, _ = normalize(
                {
                    "evidence_profiles": [
                        {"topic": "退回单", "creation_context": source}
                    ]
                },
                1,
            )
            text = "记录" + str(n)
            c = {
                "number": n,
                "text": text,
                "sha256": digest(text),
                "narrative_plan": design,
            }
            book["chapters"].append(c)
            publish(book, c, design)
        row = next(iter(book["narrative_planning"]["evidence_profiles"].values()))
        self.assertEqual(row["first_profile"]["creation_context"], "当前申请生成")
        self.assertEqual(len(row["updates"]), 2)
        verify_ledger(book)
        row["latest_profile"]["creation_context"] = "事故原始件"
        with self.assertRaises(ContractError):
            verify_ledger(book)

    def test_actual_key_handoff_is_pinned_even_when_recent_chapters_are_omitted(self):
        from memory_runtime.input_budget import fit, size

        book = json.loads(
            (
                ROOT / "runs/event_first_30000_20261025_memory_b/final_state.json"
            ).read_text(encoding="utf-8")
        )
        book["chapters"] = book["chapters"][:13]
        ending = handoff(book)
        self.assertIn("收进抽屉", ending["closing_text"])
        self.assertIn("旧图室两把", ending["closing_text"])
        payload = {
            "chapter_handoff": ending,
            "recent_chapters": [
                {"number": 1, "text": "旧前情" * 10000, "sha256": "test"}
            ],
        }
        bounded = fit(payload, 9000)
        self.assertLessEqual(size(bounded), 9000)
        self.assertEqual(bounded["chapter_handoff"], ending)

    def test_scene_entry_and_competing_authors_are_retained_as_planning_only(self):
        design, _ = normalize(
            {
                "scene_entry": {
                    "previous_completion": "钥匙已交，老常持有",
                    "opening_action": "确认回执",
                    "repeat_reason": "无再次交割",
                },
                "threads": [
                    {
                        "topic": "同一夹页签名的作者",
                        "competing_explanations": ["林：字形猜测", "周：运笔相似未证"],
                        "next_step": "先核是否同一痕迹",
                    }
                ],
            },
            1,
        )
        self.assertEqual(design["scene_entry"]["opening_action"], "确认回执")
        self.assertEqual(len(design["threads"][0]["competing_explanations"]), 2)

    def test_fallback_titles_reuse_failed_plan_metadata_without_changing_prose(self):
        from memory_runtime.chapter_titles import assign

        chapter = {
            "number": 5,
            "title": "续写5",
            "text": "甲把材料交给乙。",
            "sha256": digest("甲把材料交给乙。"),
        }
        book = {"chapters": [chapter], "plan": {"5": {"title": "续写5"}}}
        trace = [
            {
                "role": "planner",
                "raw_output": canonical({"number": 5, "title": "交接之后"}),
            }
        ]

        class Never:
            def complete(self, r):
                raise AssertionError("Existing title should be reused")

        self.assertTrue(assign(book, chapter, Never(), trace))
        self.assertEqual(chapter["title"], "交接之后")
        self.assertEqual(chapter["text"], "甲把材料交给乙。")
        self.assertEqual(book["chapter_title_jobs"], {})

    def test_title_outage_is_nonblocking_and_metadata_can_be_retried(self):
        from memory_runtime.chapter_titles import assign

        chapter = {
            "number": 1,
            "title": "续写1",
            "text": "甲离开办公室。",
            "sha256": digest("甲离开办公室。"),
        }
        book = {"chapters": [chapter]}

        class Offline:
            def complete(self, r):
                raise RuntimeError("offline")

        class Title:
            def complete(self, r):
                return ModelReply(canonical({"title": "门外"}), 1, 1, 0)

        self.assertFalse(assign(book, chapter, Offline(), []))
        self.assertEqual(chapter["title"], "")
        self.assertEqual(chapter["text"], "甲离开办公室。")
        self.assertTrue(book["chapter_title_jobs"])
        self.assertTrue(assign(book, chapter, Title(), []))
        verify_ledger(book)
        chapter["title_source"]["chapter_sha256"] = "tampered"
        with self.assertRaises(ContractError):
            verify_ledger(book)

    def real_packets(self, number):
        b = json.loads(
            (
                ROOT / "runs/event_first_30000_20261024_d_resume/final_state.json"
            ).read_text(encoding="utf-8")
        )
        c = b["chapters"][number - 1]
        commit = c["event_commit"]
        return [
            {"stage": r["stage"], "commit": p}
            for r, p in zip(
                [r for r in commit["stage_reports"] if r["status"] == "PREPARED"],
                commit["stage_transactions"],
                strict=False,
            )
        ]

    def test_real_fourteenth_meeting_stays_in_one_writing_unit(self):
        packets = self.real_packets(14)
        design, notes = normalize(
            {
                "scene_blocks": [
                    {"event_scene_positions": [1]},
                    {"event_scene_positions": [2, 3]},
                ]
            },
            3,
        )
        units = design_units(packets, 2400, 400, design)
        self.assertEqual([u["packet_indexes"] for u in units], [[0, 1, 2]])
        self.assertEqual(units[0]["scene_block_positions"], [1, 2])
        self.assertEqual(sum(u["target_han_chars"] for u in units), 2400)
        from memory_runtime.writing_units import combined_commit

        composite = combined_commit(
            [packets[i]["commit"] for i in units[0]["packet_indexes"]]
        )
        self.assertEqual(len(composite["stage_transactions"]), 3)

    def test_actual_short_chapters_keep_layout_and_all_state_transactions_in_one_call(
        self,
    ):
        from memory_runtime.writing_units import combined_commit

        book = json.loads(
            (
                ROOT / "runs/event_first_30000_20261028_threads_b/final_state.json"
            ).read_text(encoding="utf-8")
        )
        for number in (9, 14, 15):
            with self.subTest(chapter=number):
                chapter = book["chapters"][number - 1]
                commit = chapter["event_commit"]
                stages = [
                    r["stage"]
                    for r in commit["stage_reports"]
                    if r["status"] == "PREPARED"
                ]
                packets = [
                    {"stage": s, "commit": c}
                    for s, c in zip(stages, commit["stage_transactions"], strict=False)
                ]
                original = copy.deepcopy(packets)
                design = chapter["narrative_plan"]
                units = design_units(packets, 2000, 400, design)
                self.assertEqual(len(units), 1)
                selected = [packets[i]["commit"] for i in units[0]["packet_indexes"]]
                self.assertEqual(selected, commit["stage_transactions"])
                merged = combined_commit(selected)
                self.assertEqual(merged["stage_transactions"], selected)
                bridge = writer_contract(
                    {"stage_packets": packets, "narrative_plan": design},
                    units[0],
                    1,
                    1,
                    "",
                )
                self.assertEqual(
                    bridge["physical_scene_blocks"], design["scene_blocks"]
                )
                self.assertEqual(
                    bridge["chapter_intent"]["character_choice"],
                    design["character_choice"],
                )
                self.assertTrue(
                    all(
                        r["writing_status"] == "current"
                        for r in bridge["chapter_event_outline"]
                    )
                )
                self.assertEqual(packets, original)

    def test_large_chapter_respects_scene_boundaries_and_deferred_stage_numbers(self):
        packets = [{"stage": i} for i in (0, 2, 3, 4)]
        design = {
            "scene_blocks": [
                {"event_scene_positions": [1, 2]},
                {"event_scene_positions": [3, 4]},
                {"event_scene_positions": [5]},
            ]
        }
        units = design_units(packets, 8000, 400, design)
        self.assertGreater(len(units), 1)
        self.assertEqual([i for u in units for i in u["packet_indexes"]], [0, 1, 2, 3])
        self.assertTrue(
            any(1 in u["packet_indexes"] and 2 in u["packet_indexes"] for u in units)
        )
        self.assertEqual(sum(u["target_han_chars"] for u in units), 8000)

    def test_real_eleventh_conversation_is_written_together(self):
        packets = self.real_packets(11)
        design, _ = normalize(
            {"scene_blocks": [{"event_scene_positions": [1, 2, 3]}]}, 3
        )
        units = design_units(packets, 1800, 400, design)
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0]["packet_indexes"], [0, 1, 2])

    def test_real_short_run_boundary_overlap_is_normalized_with_raw_retained(self):
        from memory_runtime.writing_units import join_fragment

        b = json.loads(
            (ROOT / "runs/narrative_3000_20261025_a/final_state.json").read_text(
                encoding="utf-8"
            )
        )
        chunks = b["chapters"][0]["event_stage_sources"]
        self.assertEqual(len(chunks), 2)
        cleaned, report = join_fragment(chunks[0]["text"], chunks[1]["text"])
        self.assertGreater(report["removed_characters"], 0)
        self.assertEqual(chunks[1]["text"][report["removed_characters"] :], cleaned)
        self.assertEqual(
            ("\n\n".join([chunks[0]["text"], cleaned])).count(
                "夜里她锁门前，门缝底下压着"
            ),
            1,
        )

    def test_seam_normalization_keeps_short_dialogue_semantic_repeats_and_whole_duplicate(
        self,
    ):
        from memory_runtime.writing_units import join_fragment

        for previous, raw in [
            ("“好。”", "“好。”\n\n他离开了。"),
            ("甲已经站在门内。", "甲走进门内，又回过头。"),
            ("甲" * 80, "甲" * 80),
        ]:
            self.assertEqual(join_fragment(previous, raw)[0], raw)

    def test_ninth_chapter_deadline_is_visible_before_its_later_stage(self):
        packets = self.real_packets(9)
        bridge = writer_contract(
            {"stage_packets": packets},
            {"packet_indexes": [0]},
            1,
            4,
            "杯子已经放在桌上。",
        )
        self.assertIn("下周", canonical(bridge["chapter_event_outline"]))
        self.assertFalse(bridge["may_end_current_scene"])
        self.assertEqual(bridge["previous_prose_sha256"], digest("杯子已经放在桌上。"))

    def test_invalid_optional_grouping_falls_back_without_losing_transactions(self):
        packets = self.real_packets(14)
        for raw in (
            "wrong",
            {"scene_blocks": [{"event_scene_positions": [1, 1, 3]}]},
            {"scene_blocks": [{"event_scene_positions": [True, 2, 3]}]},
        ):
            with self.subTest(raw=raw):
                design, notes = normalize(raw, 3)
                self.assertTrue(notes)
                units = design_units(packets, 2000, 400, design)
                self.assertEqual(
                    [i for u in units for i in u["packet_indexes"]], [0, 1, 2]
                )

    def test_thread_resolution_requires_saved_source_and_keeps_prior_updates(self):
        first = {
            "number": 1,
            "text": "甲收到威胁便条。",
            "sha256": digest("甲收到威胁便条。"),
        }
        book = {"chapters": [first]}
        publish(
            book,
            first,
            {
                "threads": [
                    {
                        "topic": "威胁便条",
                        "next_step": "查来源",
                        "resolution_quote": "已经查清了",
                    }
                ]
            },
        )
        row = next(iter(book["narrative_planning"]["threads"].values()))
        self.assertEqual(row["status"], "open")
        second = {
            "number": 2,
            "text": "便条来自乙，甲决定交给警方。",
            "sha256": digest("便条来自乙，甲决定交给警方。"),
        }
        book["chapters"].append(second)
        publish(
            book,
            second,
            {
                "threads": [
                    {
                        "topic": "威胁便条",
                        "resolution_chapter": 2,
                        "resolution_quote": second["text"],
                    }
                ]
            },
        )
        row = next(iter(book["narrative_planning"]["threads"].values()))
        self.assertEqual(row["status"], "addressed")
        self.assertEqual(len(row["updates"]), 2)
        self.assertEqual(row["resolution"]["chapter_sha256"], second["sha256"])

    def test_bounded_planning_view_preserves_stored_threads(self):
        c = {"number": 1, "text": "甲开始调查。", "sha256": digest("甲开始调查。")}
        book = {"chapters": [c]}
        publish(
            book,
            c,
            {
                "threads": [
                    {"topic": f"线索{i}", "next_step": "查证" * 100} for i in range(80)
                ]
            },
        )
        snapshot = copy.deepcopy(book)
        view = context(book, 10)
        self.assertGreater(view["omitted_thread_count"], 0)
        self.assertEqual(book, snapshot)
        self.assertTrue(
            all(r["chapters_since_introduced"] == 9 for r in view["threads"])
        )

    def test_formal_launcher_groups_scenes_and_persists_design_for_next_planning(self):
        class Provider(EventLocal):
            def complete(self, r):
                if r.role == "planner":
                    self.requests.append(copy.deepcopy(r))
                    n = r.payload["chapter_number"]
                    scenes = [
                        {
                            "purpose": p,
                            "participants": ["甲", "乙"],
                            "beats": [
                                {
                                    "statement": s,
                                    "assertion_scope": "performed_action",
                                    "requires": [],
                                    "changes": [],
                                }
                            ],
                        }
                        for p, s in (
                            ("陈述", "甲在会议室递交便条。"),
                            ("回应", "乙在同一场会谈中接收材料。"),
                            ("离场", "两人沿走廊离开。"),
                        )
                    ]
                    return ModelReply(
                        canonical(
                            {
                                "number": n,
                                "title": "会谈",
                                "brief": "交材料并作选择",
                                "future_updates": [],
                                "scenes": scenes,
                                "narrative_plan": {
                                    "scene_blocks": [
                                        {
                                            "event_scene_positions": [1, 2],
                                            "setting": "会议室",
                                        },
                                        {
                                            "event_scene_positions": [3],
                                            "setting": "走廊",
                                        },
                                    ],
                                    "threads": [
                                        {"topic": "威胁便条", "next_step": "追查来源"}
                                    ],
                                    "chapter_change": "从私人怀疑转成公开承担风险",
                                    "character_choice": "甲明知公开可能失去保护仍提交材料",
                                },
                            }
                        ),
                        1,
                        1,
                        0,
                    )
                if r.role == "writer":
                    self.requests.append(copy.deepcopy(r))
                    if "current_draft" in r.payload:
                        return ModelReply(r.payload["current_draft"], 1, 1, 0)
                    text = "".join(
                        b["statement"]
                        for s in r.payload["frozen_events"]["scenes"]
                        for b in s["beats"]
                    )
                    return ModelReply(canonical({"new_stage_text": text}), 1, 1, 0)
                return super().complete(r)

        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as temp:
            from memory_runtime.length_control import han_count

            provider = Provider()
            cfg = dict(
                event_config(1),
                target_han_chars=han_count(
                    "甲在会议室递交便条。乙在同一场会谈中接收材料。两人沿走廊离开。"
                ),
            )
            with (
                patch.object(cli, "read_secret", return_value="offline"),
                patch.object(cli, "ChatCompletionProvider", return_value=provider),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                result = cli.launch(cfg, Path(temp) / "book")
            self.assertTrue(result["draft_completed"])
            book = load_resume(result["resume_checkpoint"], cli.validate_config(cfg))
            self.assertEqual(
                [
                    len(s["source_commit_sha256s"])
                    for s in book["chapters"][0]["event_stage_sources"]
                ],
                [3],
            )
            session = WritingSession(
                Path(temp) / "next", provider, cli.validate_config(cfg), book=book
            )
            self.assertEqual(
                session.context("继续追查", "便条")["narrative_continuity"]["threads"][
                    0
                ]["topic"],
                "威胁便条",
            )
            writers = [
                r
                for r in provider.requests
                if r.role == "writer"
                and "stage_task" in r.payload
                and "current_draft" not in r.payload
            ]
            self.assertEqual(len(writers), 1)
            self.assertIn("scene_continuity", writers[0].payload["stage_task"])
            continuity = writers[0].payload["stage_task"]["scene_continuity"]
            self.assertEqual(
                continuity["chapter_intent"]["character_choice"],
                "甲明知公开可能失去保护仍提交材料",
            )
            self.assertEqual(len(continuity["physical_scene_blocks"]), 2)
            self.assertEqual(
                len(book["chapters"][0]["event_commit"]["stage_transactions"]), 3
            )
            damaged = json.loads(
                Path(result["resume_checkpoint"]).read_text(encoding="utf-8")
            )
            damaged["book"]["chapters"][0]["narrative_plan"]["character_choice"] = (
                "篡改计划"
            )
            damaged["book_sha256"] = digest(canonical(damaged["book"]))
            path = Path(temp) / "damaged.json"
            path.write_text(canonical(damaged), encoding="utf-8")
            with self.assertRaises(ContractError):
                load_resume(path, cli.validate_config(cfg))


if __name__ == "__main__":
    unittest.main()
