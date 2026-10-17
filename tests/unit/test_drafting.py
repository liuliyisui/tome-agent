"""Draft-first policy tests; no real model or credentials."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "code" / "core_engine"))
from inf_writer.drafting import DraftSession, evidence_segments, normalize_memory, validate_review
from inf_writer.agents import build_agents
from inf_writer.domain import ContractError, Snapshot
from inf_writer.models import Budget, ModelGateway, ModelReply

BODY = "艾岚的眼睛是灰色。她在灯塔前等候守卫。"


class DraftFixture:
    def __init__(self, bad_memory=False, reject=False, empty=False, missing=False, bad_review=False):
        self.requests = []
        self.bad_memory, self.reject, self.empty = bad_memory, reject, empty
        self.missing, self.bad_review = missing, bad_review

    def complete(self, request):
        self.requests.append(copy.deepcopy(request))
        if request.role == "planner":
            data = {"number": request.payload["chapter_number"], "title": "灯塔", "brief": "灯塔的故事", "future_updates": []}
        elif request.role == "writer":
            data = {"text": BODY}
        elif request.role == "memory":
            data = {"changes": [{"action": "store", "subject": "艾岚", "attribute": "eye_color", "value": "灰色",
                "expected_revision": None, "evidence_id": "bad" if self.bad_memory else "e0001", "reason": "正文明确眼色"}]}
            if request.payload["active_facts"] or self.empty:
                data = {"changes": [], "no_change_reason": "眼色与当前档案一致，没有新增状态。"}
        else:
            issue = {"kind": "world_rule", "description": "固定模拟硬问题，不是模型语义评价",
                     "draft_quote": "灰色", "basis_ref": "constraint_1", "basis_quote": "固定测试约束"}
            data = {"approved": not (self.reject or self.missing), "issues": [issue] if self.reject else [],
                    "suggestions": ["可以增加对话"], "memory_check": {
                        "status": "missing" if self.missing else "sufficient", "reason": "固定模拟记忆复核"}}
            if self.bad_review:
                data["issues"] = [dict(issue, basis_ref="future_plan_1")]
                data["approved"] = False
        return ModelReply(json.dumps(data, ensure_ascii=False), 0, 0, 0)


class DraftingTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[2] / "code" / "backend" / "data" / "test-tmp"
        root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)

    def session(self, model, max_calls=40):
        budget = Budget(max_calls=max_calls, max_cost_usd=0)
        session = DraftSession(Path(self.temp.name), Snapshot("draft", "写灯塔", ["固定测试约束"]),
                               build_agents(ModelGateway(model, budget)))
        return session, budget

    def test_evidence_ids_resolve_exact_text(self):
        self.assertEqual(evidence_segments(BODY)[0]["text"], BODY)
        proposal = {"number": 1, "title": "灯塔", "brief": "等待", "future_updates": []}
        result = {"changes": [{"action": "store", "subject": "艾岚", "attribute": "eye_color", "value": "灰色",
            "expected_revision": None, "evidence_id": "e0001", "reason": "正文明确"}]}
        normalized = normalize_memory(result, Snapshot("draft", "故事"), proposal, BODY)
        self.assertEqual(normalized["changes"][0]["quote"], BODY)
        self.assertNotIn("evidence_id", normalized["changes"][0])

    def test_empty_without_reason_is_rejected(self):
        with self.assertRaises(ContractError):
            normalize_memory({"changes": []}, Snapshot("draft", "故事"),
                {"number": 1, "title": "灯塔", "brief": "等待", "future_updates": []}, BODY)

    def test_memory_repair_succeeds_without_rewriting_body(self):
        class CorrectOnRetry(DraftFixture):
            def complete(self, request):
                self.bad_memory = request.role == "memory" and not any(r.role == "memory" for r in self.requests)
                return super().complete(request)
        model = CorrectOnRetry()
        session, _ = self.session(model)
        self.assertEqual(session.write_next("写第一章")["status"], "DRAFT_CHECKED")
        self.assertEqual(sum(r.role == "writer" for r in model.requests), 1)
        memories = [r for r in model.requests if r.role == "memory"]
        self.assertEqual(len(memories), 2)
        self.assertEqual(memories[0].payload["current_draft"], memories[1].payload["current_draft"])
        self.assertIn("repair", memories[1].payload)

    def test_legacy_nonverbatim_quote_still_rejected(self):
        change = {"action": "store", "subject": "艾岚", "attribute": "eye_color", "value": "灰色",
                  "expected_revision": None, "quote": "她的眼睛是灰的。", "reason": "概括不是原文"}
        with self.assertRaises(ContractError):
            normalize_memory({"changes": [change]}, Snapshot("draft", "故事"),
                {"number": 1, "title": "灯塔", "brief": "等待", "future_updates": []}, BODY)

    def test_no_automatic_translation_of_invalid_attribute(self):
        change = {"action": "store", "subject": "艾岚", "attribute": "眼睛颜色", "value": "灰色",
                  "expected_revision": None, "evidence_id": "e0001", "reason": "要修正字段"}
        with self.assertRaises(ContractError):
            normalize_memory({"changes": [change]}, Snapshot("draft", "故事"),
                {"number": 1, "title": "灯塔", "brief": "等待", "future_updates": []}, BODY)

    def test_bad_memory_repairs_only_memory_then_continues(self):
        model = DraftFixture(bad_memory=True)
        session, _ = self.session(model)
        first = session.write_next("写第一章")
        second = session.write_next("继续第二章")
        self.assertEqual(first["status"], "DRAFT_UNCHECKED")
        self.assertEqual(second["chapter_number"], 2)
        self.assertEqual(len(session.state.chapters), 2)
        self.assertEqual(session.state.active_facts(), [])
        self.assertEqual(sum(r.role == "writer" for r in model.requests), 2)
        self.assertEqual(sum(r.role == "memory" for r in model.requests), 4)
        self.assertTrue(model.requests[-4].payload["unresolved_chapters"])

    def test_rejected_prose_is_kept_but_memory_not_promoted(self):
        session, _ = self.session(DraftFixture(reject=True))
        row = session.write_next("写第一章")
        self.assertEqual(row["status"], "DRAFT_UNCHECKED")
        self.assertEqual(session.state.chapters[0]["text"], BODY)
        self.assertEqual(session.state.active_facts(), [])
        self.assertTrue(row["issues"])

    def test_suggestions_alone_do_not_block_memory(self):
        session, _ = self.session(DraftFixture())
        row = session.write_next("写第一章")
        self.assertEqual(row["status"], "DRAFT_CHECKED")
        self.assertTrue(row["suggestions"])
        self.assertEqual(session.state.active_facts()[0]["value"], "灰色")

    def test_empty_proposal_gets_separate_memory_review(self):
        session, _ = self.session(DraftFixture(empty=True, missing=True))
        row = session.write_next("写第一章")
        self.assertEqual(row["status"], "DRAFT_UNCHECKED")
        self.assertIn("missing", json.dumps(row))

    def test_legitimate_no_change_chapter_is_allowed(self):
        session, _ = self.session(DraftFixture())
        session.write_next("写第一章")
        self.assertEqual(session.write_next("第二章眼色不变")["status"], "DRAFT_CHECKED")
        self.assertEqual(len(session.state.active_facts()), 1)

    def test_unfounded_review_exhaustion_does_not_stop_story(self):
        model = DraftFixture(bad_review=True)
        session, _ = self.session(model)
        self.assertEqual(session.write_next("一")["status"], "DRAFT_UNCHECKED")
        self.assertEqual(session.write_next("二")["chapter_number"], 2)
        self.assertEqual(sum(r.role == "reviewer" for r in model.requests), 4)

    def test_budget_stop_keeps_generated_draft(self):
        session, budget = self.session(DraftFixture(), max_calls=2)
        row = session.write_next("一")
        self.assertEqual(row["status"], "DRAFT_UNCHECKED")
        self.assertEqual(row["stop_reason"], "RESOURCE_OR_TRANSPORT")
        self.assertEqual(len(session.state.chapters), 1)
        self.assertEqual(budget.calls, 2)

    def test_no_draft_does_not_fabricate_a_chapter(self):
        session, _ = self.session(DraftFixture(), max_calls=1)
        row = session.write_next("一")
        self.assertEqual(row["status"], "NO_DRAFT")
        self.assertEqual(session.state.chapters, [])

    def test_working_checkpoint_explicitly_not_formal(self):
        session, _ = self.session(DraftFixture(reject=True))
        session.write_next("一")
        saved = json.loads((Path(self.temp.name) / "draft_chapter_001.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["mode"], "DRAFT_FIRST_NOT_FORMAL")
        self.assertEqual(saved["state"]["facts"], {})

    def test_plan_cannot_be_used_as_a_hard_fact_reference(self):
        context = {"current_draft": BODY, "hard_references": {"constraint_1": "固定测试约束"}}
        review = {"approved": False, "issues": [{"kind": "world_rule", "description": "未来计划",
            "draft_quote": "灰色", "basis_ref": "future_plan_1", "basis_quote": "计划"}],
            "suggestions": [], "memory_check": {"status": "sufficient", "reason": "复核"}}
        with self.assertRaises(ContractError):
            validate_review(review, context)


if __name__ == "__main__":
    unittest.main()
