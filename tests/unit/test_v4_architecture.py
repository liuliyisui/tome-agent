import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from tome_agent.state import NarrativeState, Workspace
from tome_agent.submissions import submit_groups, attribute_history
from tome_agent.agent import ChapterAgent, Response, Limits
from tome_agent.offline import entry, group, tool, ScriptedModel, demo
from tome_backend.checkpoints import save_checkpoint, load_checkpoint
from tome_agent.planning import OutlinePlanner


class SubmissionTests(unittest.TestCase):
    def test_dependent_component_rolls_back_narrative_and_facts(self):
        state = NarrativeState()
        a = group("a", [entry(2, "有两支")], upsert_character_state=[{"name": "林舟", "description": "出发"}])
        b = group("b", [entry(1, "不存在", subject="别人")], depends_on=["a"])
        self.assertFalse(submit_groups(state, {"groups": [a, b]}, 1, "有两支")["ok"])
        self.assertFalse(state.facts)
        self.assertFalse(state.characters)
        self.assertEqual(len(state.pending), 2)

    def test_unrelated_success_and_pending_repair(self):
        state = NarrativeState()
        good = group("good", [entry(2, "有两支")])
        bad = group("bad", [entry(1, "错误", subject="另一人")])
        submit_groups(state, {"groups": [good, bad]}, 1, "有两支")
        self.assertEqual(len(state.facts), 1)
        self.assertFalse(submit_groups(state, {"groups": []}, 1, "有两支")["ok"])
        fixed = group("bad", [entry(1, "有两支", subject="另一人", action="defer")])
        self.assertTrue(submit_groups(state, {"groups": [fixed]}, 1, "有两支")["ok"])
        self.assertEqual(len(state.facts), 1)

    def test_same_subject_auto_merges(self):
        state = NarrativeState()
        a = group("a", [entry(2, "有两支")])
        b = group("b", [entry(1, "错误", key="location")])
        submit_groups(state, {"groups": [a, b]}, 1, "有两支")
        self.assertFalse(state.facts)

    def test_replay_does_not_duplicate_audit(self):
        state = NarrativeState()
        request = {"groups": [group("a", [entry(2, "有两支")])]}
        submit_groups(state, request, 1, "有两支")
        saved = deepcopy(state)
        self.assertTrue(submit_groups(state, request, 1, "有两支")["ok"])
        self.assertEqual(state, saved)
        changed = deepcopy(request)
        changed["groups"][0]["entries"][0]["value"] = 3
        self.assertFalse(submit_groups(state, changed, 1, "有两支")["ok"])
        self.assertEqual(state.facts, saved.facts)

    def test_history_replacement_evidence_and_source_checks(self):
        state = NarrativeState()
        submit_groups(state, {"groups": [group("a", [entry(2, "有两支")])]}, 1, "有两支")
        submit_groups(state, {"groups": [group("a", [entry(1, "剩一支", 1, "update")])]}, 2, "剩一支")
        rows = attribute_history(state, "林舟", "fire_starter_count", {1: "有两支", 2: "剩一支"})
        self.assertEqual(rows[0]["value"], 2)
        self.assertEqual(rows[0]["archived_by"]["chapter"], 2)
        with self.assertRaises(ValueError):
            attribute_history(state, "林舟", "fire_starter_count", {1: "改写", 2: "剩一支"})

    def test_uncertain_subjective_personality_and_time_guards(self):
        for changes in ({"epistemic_status": "uncertain"}, {"epistemic_status": "subjective"},
                        {"category": "personality", "support_basis": "single_observation"},
                        {"temporal_scope": "historical", "time_anchor": "current"}):
            with self.subTest(changes=changes):
                state = NarrativeState()
                self.assertFalse(submit_groups(state, {"groups": [group("a", [entry(2, "有两支", **changes)])]}, 1, "有两支")["ok"])
                self.assertFalse(state.facts)

    def test_retirement_and_reactivation(self):
        state = NarrativeState()
        for number, proposal in [(1, entry(2, "火折")),
                (2, entry(None, "火折", 1, "retire")), (3, entry(1, "火折", 2, "update"))]:
            self.assertTrue(submit_groups(state, {"groups": [group("a", [proposal])]}, number, "火折")["ok"])
        self.assertEqual(len(state.history), 2)
        self.assertEqual(state.view()["facts"][0]["revision"], 3)

    def test_time_anchor_cannot_change_in_place(self):
        state = NarrativeState()
        submit_groups(state, {"groups": [group("a", [entry(2, "火折")])]}, 1, "火折")
        result = submit_groups(state, {"groups": [group("a", [entry(1, "火折", 1, "update",
            temporal_scope="historical", time_anchor="before_departure")])]}, 2, "火折")
        self.assertFalse(result["ok"])
        self.assertFalse(state.history)


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "book.json"
        self.workspace = Workspace("测试", "出发", [{"title": "一", "goal": "出发", "target_units": 3}])

    def test_whole_book_demo_and_checkpoint(self):
        workspace = demo(self.path)
        self.assertEqual(load_checkpoint(self.path), workspace)
        self.assertEqual(len(workspace.chapters), 2)
        self.assertEqual(len(workspace.state.history), 1)
        self.assertTrue(workspace.state.future_requirements)

    def test_pending_done_does_not_promote(self):
        save_checkpoint(self.workspace, self.path)
        old = self.path.read_bytes()
        model = ScriptedModel([tool("write", {"text": "有火折"}),
            tool("update", {"groups": [group("a", [entry(2, "不存在")])]}), Response("DONE")])
        agent = ChapterAgent(model)
        with self.assertRaises(ValueError):
            agent.run(self.workspace, self.path)
        self.assertEqual(self.path.read_bytes(), old)
        self.assertFalse(self.workspace.chapters)
        self.assertTrue(agent.last_attempt["working"]["state"]["pending"])

    def test_failed_attempt_resumes_same_pending_group(self):
        agent = ChapterAgent(ScriptedModel([tool("write", {"text": "有火折"}),
            tool("update", {"groups": [group("a", [entry(2, "不存在")])]}), Response("DONE")]))
        with self.assertRaises(ValueError):
            agent.run(self.workspace, self.path)
        attempt = json.loads(Path(str(self.path) + ".attempt.json").read_text(encoding="utf-8"))
        agent.model = ScriptedModel([tool("update", {"groups": [group("a", [entry(2, "有火折")])]}), Response("DONE")])
        finished = agent.run(self.workspace, self.path, attempt)
        self.assertEqual(finished.chapters[1], "有火折")
        self.assertFalse(finished.state.pending)

    def test_source_bound_correction_is_rejected(self):
        model = ScriptedModel([tool("write", {"text": "有火折"}),
            tool("update", {"groups": [group("a", [entry(2, "有火折")])]}),
            tool("correct", {"chapter": 1, "old": "有火折", "new": "没火折"}), Response("DONE")])
        agent = ChapterAgent(model)
        result = agent.run(self.workspace, self.path)
        self.assertEqual(result.chapters[1], "有火折")
        correction = next(t for t in agent.last_attempt["trace"] if t.get("tool") == "correct")
        self.assertFalse(correction["result"]["ok"])

    def test_truncation_cannot_commit(self):
        agent = ChapterAgent(ScriptedModel([Response("DONE", finish_reason="length")]))
        with self.assertRaises(ValueError):
            agent.run(self.workspace, self.path)
        self.assertFalse(self.path.exists())

    def test_budget_and_fingerprint(self):
        save_checkpoint(self.workspace, self.path)
        with self.assertRaises(ValueError):
            load_checkpoint(self.path, "different")
        agent = ChapterAgent(ScriptedModel([tool("write", {"text": "有火折"}),
            tool("update", {"groups": []})]), Limits(max_turns=2))
        with self.assertRaises(ValueError):
            agent.run(self.workspace, self.path)
        self.assertFalse(load_checkpoint(self.path).chapters)

    def test_four_stage_planning_and_cache(self):
        model = ScriptedModel([Response(json.dumps({"content": stage})) for stage in ("premise", "synopsis", "acts")]
            + [Response(json.dumps([{"title": "一", "goal": "出发"}]))])
        planner = OutlinePlanner(model)
        workspace = planner.generate("测试", "出发", 1, 100, {"model": "offline"}, self.path)
        self.assertEqual(len(model.requests), 4)
        cached = planner.generate("测试", "出发", 1, 100, {"model": "offline"}, self.path)
        self.assertEqual(workspace, cached)
        self.assertEqual(len(model.requests), 4)


if __name__ == "__main__":
    unittest.main()
