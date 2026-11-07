"""Material provenance survives planning, wire selection and writer routes."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import write_novel as cli
from inf_writer.domain import canonical, digest
from inf_writer.models import ModelReply
from memory_runtime.evidence_access import context as material_context
from memory_runtime.narrative_planning import (
    context,
    normalize,
    publish,
    verify_ledger,
    writer_contract,
)
from memory_runtime.test_event_first import ROOT, EventLocal, event_config
from memory_runtime.writing import WritingSession


class EvidenceAccessTests(unittest.TestCase):
    def source_book(self):
        path = (
            ROOT
            / "runs/event_first_30000_20261028_human_scene_a/working/checkpoint_0066.json"
        )
        return json.loads(path.read_text(encoding="utf-8"))["book"]

    def test_material_and_observation_conditions_roundtrip_without_new_fact_mutations(
        self,
    ):
        material = {
            "material_name": "甲的手抄件",
            "derived_from": "乙持有的原本",
            "acquisition_method": "甲逐栏手抄",
            "access_status": "甲持抄件，乙持原本",
            "retained_information": ["抄写的文字"],
            "unavailable_information": ["原作者笔压与原纸纹"],
        }
        requirement = {
            "material_name": "甲的手抄件",
            "required_information": ["原作者笔压"],
            "available_basis": "抄件不保留该信息",
            "missing_condition": "需另行取得原本，改查交接人",
        }
        design, notes = normalize(
            {
                "evidence_profiles": [
                    {"topic": "文书", "available_materials": [material]}
                ],
                "inference_links": [
                    {"question": "谁签的", "observation_requirements": [requirement]}
                ],
                "threads": [],
            },
            1,
        )
        self.assertFalse(notes)
        self.assertEqual(
            design["evidence_profiles"][0]["available_materials"], [material]
        )
        self.assertEqual(
            design["inference_links"][0]["observation_requirements"], [requirement]
        )
        text = "甲手抄文字，原本仍留乙处。"
        chapter = {
            "number": 1,
            "text": text,
            "sha256": digest(text),
            "narrative_plan": design,
        }
        book = {"chapters": [chapter], "writing_state": {"facts": {}}}
        state = copy.deepcopy(book["writing_state"])
        publish(book, chapter, design)
        verify_ledger(book)
        wire = material_context(json.loads(canonical(book)))
        self.assertEqual(
            wire["evidence_materials"][0]["available_materials"], [material]
        )
        self.assertEqual(book["writing_state"], state)
        packet = {
            "stage_packets": [
                {
                    "stage": 0,
                    "commit": {"scenes": [{"purpose": "查经手人", "beats": []}]},
                }
            ],
            "narrative_plan": design,
        }
        bridge = writer_contract(packet, {"packet_indexes": [0]}, 1, 1, "")
        self.assertEqual(
            bridge["evidence_profiles"][0]["available_materials"], [material]
        )
        self.assertEqual(
            bridge["inference_links"][0]["observation_requirements"], [requirement]
        )

    def test_actual_old_profiles_are_unknown_not_originals_with_literal_acquisition_sources(
        self,
    ):
        book = self.source_book()
        original = copy.deepcopy(book)
        view = material_context(book)
        row = next(
            r
            for r in view["evidence_materials"]
            if r["topic"] == "第二回借调审批单底稿与借出签收单"
        )
        self.assertEqual(row["description_status"], "NOT_RECORDED")
        self.assertIn("实际领走", row["document_identity"]["document_role"])
        self.assertEqual(row["available_materials"], [])
        self.assertIn(
            "原件未取，只抄栏目。", "".join(p["quote"] for p in row["source_passages"])
        )
        self.assertLessEqual(len(canonical(view).encode("utf-8")), 9000)
        for row in view["evidence_materials"]:
            for source in row["source_passages"]:
                chapter = book["chapters"][source["chapter"] - 1]
                self.assertEqual(source["chapter_sha256"], digest(chapter["text"]))
                self.assertEqual(
                    source["quote"], chapter["text"][source["start"] : source["end"]]
                )
        self.assertEqual(book, original)

    def test_missing_current_design_and_budget_trimming_keep_material_access_sources(
        self,
    ):
        from memory_runtime.input_budget import fit, size

        book = self.source_book()
        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            session = WritingSession(
                Path(folder) / "session",
                EventLocal(),
                cli.validate_config(event_config(15)),
                book=book,
            )
            wire = session.context("接着查", "签收单")
        self.assertTrue(
            wire["narrative_continuity"]["evidence_access"]["evidence_materials"]
        )
        access = copy.deepcopy(wire["narrative_continuity"]["evidence_access"])
        minimal = {
            "narrative_continuity": wire["narrative_continuity"],
            "recent_chapters": [{"number": 1, "text": "旧前情" * 15000}],
        }
        bounded = fit(
            minimal,
            size({"narrative_continuity": {"evidence_access": access}}) + 1000,
        )
        self.assertEqual(bounded["narrative_continuity"]["evidence_access"], access)

    def test_fallback_and_length_adjustment_retain_access_view(self):
        from memory_runtime.completion import continue_prose
        from memory_runtime.length_control import adjust

        book = self.source_book()
        expected = context(book, 10)["evidence_access"]

        class Provider:
            def __init__(self):
                self.requests = []

            def complete(self, r):
                self.requests.append(copy.deepcopy(r))
                return ModelReply("甲收起抄件，转去找经手人。" * 10, 1, 1, 0)

        provider = Provider()
        task = {"unit_number": 1, "total_units": 1}
        continue_prose(provider, book, "继续", 10, [], stage_task=task)
        adjust("甲收起抄件。", 100, book, 10, provider, [], stage_task=task)
        self.assertEqual(len(provider.requests), 2)
        for request in provider.requests:
            self.assertEqual(
                request.payload["narrative_continuity"]["evidence_access"], expected
            )

    def test_newer_prose_is_supplied_even_if_old_material_description_claims_held(self):
        first = "甲拿着文书原件核对。"
        last = "甲已把文书原件交还乙，只留下手抄文字。"
        profile = {
            "topic": "文书",
            "available_materials": [
                {"material_name": "原件", "access_status": "甲持有"}
            ],
        }
        design = {"evidence_profiles": [profile], "threads": []}
        chapter = {
            "number": 1,
            "text": first,
            "sha256": digest(first),
            "narrative_plan": design,
        }
        book = {"chapters": [chapter]}
        publish(book, chapter, design)
        book["chapters"].append({"number": 2, "text": last, "sha256": digest(last)})
        view = material_context(book)
        row = view["evidence_materials"][0]
        self.assertTrue(
            any(
                s["chapter"] == 2 and s["quote"] == last for s in row["source_passages"]
            )
        )
        self.assertEqual(row["description_status"], "DECLARED_IN_PLAN")

    def revised_session(self, folder, mode):
        from memory_runtime.test_stage_repair import public_plan

        class Provider(EventLocal):
            def __init__(self):
                super().__init__()
                self.plans = 0
                self.writes = 0

            def complete(self, request):
                if request.role == "planner":
                    self.requests.append(copy.deepcopy(request))
                    self.plans += 1
                    if mode == "planning_failure" and self.plans > 1:
                        return ModelReply("{}", 1, 1, 0)
                    p = public_plan()
                    first = p["scenes"][0]["beats"][0]
                    first["statement"] = (
                        "甲改查经手人。" if self.plans > 1 else "甲错误地把抄件当原件。"
                    )
                    first["changes"][0].update(
                        property_name="核对方法",
                        value="改查经手人" if self.plans > 1 else "抄件能证明原字",
                    )
                    p["scenes"].append(
                        {
                            "purpose": "收起材料",
                            "participants": ["甲"],
                            "beats": [
                                {
                                    "statement": "甲收起抄件。",
                                    "assertion_scope": "performed_action",
                                    "requires": [],
                                    "changes": [],
                                }
                            ],
                        }
                    )
                    return ModelReply(canonical(p), 1, 1, 0)
                if request.role == "writer":
                    self.requests.append(copy.deepcopy(request))
                    if request.payload.get("output_mode") == "plain_prose":
                        return ModelReply("甲收起抄件，改查经手人。", 1, 1, 0)
                    self.writes += 1
                    if self.writes == 1 or mode == "repeated_revision":
                        return ModelReply(
                            canonical(
                                {
                                    "event_revision_request": "抄件不保留原始特征，须改查证行动。"
                                }
                            ),
                            1,
                            1,
                            0,
                        )
                    text = "".join(
                        b["statement"]
                        for s in request.payload["frozen_events"]["scenes"]
                        for b in s["beats"]
                    )
                    return ModelReply(canonical({"new_stage_text": text}), 1, 1, 0)
                return super().complete(request)

        provider = Provider()
        return WritingSession(
            folder, provider, cli.validate_config(event_config(1))
        ), provider

    def test_first_stage_revision_replans_and_commits_only_revised_candidate(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            session, provider = self.revised_session(Path(folder) / "book", "replan")
            row = session.write_next("继续")
            self.assertIsNone(row["stop_reason"])
            self.assertEqual(provider.plans, 2)
            self.assertEqual(
                session.book["writing_state"]["facts"]["n0001r0001"]["value"],
                "改查经手人",
            )
            self.assertNotIn("错误地", session.book["chapters"][0]["text"])
            second = [r for r in provider.requests if r.role == "planner"][1]
            self.assertIn("event_revision_request", second.payload)
            from memory_runtime.writing import load_resume

            self.assertEqual(
                load_resume(session.latest_checkpoint, session.plan), session.book
            )

    def test_old_unwritten_plan_is_replanned_on_observation_policy_change(self):
        from memory_runtime.evidence_access import OBSERVATION_POLICY_VERSION

        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            session, provider = self.revised_session(Path(folder) / "book", "replan")
            original = copy.deepcopy(session.book["writing_state"])
            packet = session._prepare_events("继续", 1, [])
            old_hash = packet["commit"]["sha256"]
            session.book["prepared_events"]["1"].pop("evidence_observation_policy")
            revised = session._prepare_events("继续", 1, [])
            self.assertEqual(provider.plans, 2)
            self.assertNotEqual(revised["commit"]["sha256"], old_hash)
            self.assertEqual(
                revised["evidence_observation_policy"], OBSERVATION_POLICY_VERSION
            )
            self.assertEqual(session.book["writing_state"], original)
            self.assertIn(
                "event_revision_request",
                [r for r in provider.requests if r.role == "planner"][1].payload,
            )

    def test_current_policy_reuses_prepared_plan_without_extra_call(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            session, provider = self.revised_session(Path(folder) / "book", "replan")
            original = session._prepare_events("继续", 1, [])
            cached = session._prepare_events("继续", 1, [])
            self.assertEqual(original, cached)
            self.assertEqual(provider.plans, 1)

    def test_repeated_stage_revision_keeps_prose_and_queues_state_without_disputed_plan(
        self,
    ):
        self.assert_revision_fallback("repeated_revision")

    def test_failed_replanning_keeps_prose_and_queues_state_without_disputed_plan(self):
        self.assert_revision_fallback("planning_failure")

    def assert_revision_fallback(self, mode):
        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            session, provider = self.revised_session(Path(folder) / "book", mode)
            with patch.object(session, "attempt_state_repair"):
                row = session.write_next("继续")
            self.assertIsNone(row["stop_reason"])
            self.assertEqual(len(session.book["chapters"]), 1)
            self.assertIn("改查经手人", session.book["chapters"][0]["text"])
            self.assertEqual(session.book["writing_state"]["facts"], {})
            self.assertEqual(
                session.book["chapters"][0]["event_plan_status"], "unavailable"
            )
            self.assertEqual(
                session.book["state_repair_jobs"]["1"]["status"], "PENDING"
            )
            self.assertLessEqual(provider.plans, 5)
            from memory_runtime.writing import load_resume

            self.assertEqual(
                load_resume(session.latest_checkpoint, session.plan), session.book
            )


if __name__ == "__main__":
    unittest.main()
