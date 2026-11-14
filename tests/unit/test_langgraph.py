"""Exercise real compiled graphs with deterministic providers; no remote LLM."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from memory_runtime.test_writing import Local, config
from memory_runtime.writing import WritingSession, load_resume
from tome_writer.agents import build_agents
from tome_writer.domain import ContractError, Snapshot, canonical
from tome_writer.models import Budget, ModelGateway, ModelReply
from tome_writer.runtime import Coordinator
from tome_writer.storage import FileStore


class EventProvider(Local):
    def __init__(self, revise=False, interrupt=False):
        super().__init__()
        self.revise = revise
        self.interrupt = interrupt

    def complete(self, request):
        if request.role == "planner":
            self.requests.append(copy.deepcopy(request))
            self.number = request.payload["chapter_number"]
            value = {
                "number": self.number,
                "title": "来信",
                "brief": "读信",
                "future_updates": [],
                "scenes": [
                    {
                        "purpose": "调查",
                        "participants": ["甲"],
                        "beats": [
                            {
                                "statement": "甲读了来信。",
                                "assertion_scope": "performed_action",
                                "requires": [],
                                "changes": [],
                            }
                        ],
                    }
                ],
            }
            return ModelReply(canonical(value), 1, 1, 0)
        if request.role == "writer":
            self.requests.append(copy.deepcopy(request))
            if self.interrupt:
                raise KeyboardInterrupt()
            if self.revise:
                self.revise = False
                return ModelReply(
                    canonical({"event_revision_request": "调整读信场景"}), 1, 1, 0
                )
            return ModelReply(canonical({"text": "甲读了来信。"}), 1, 1, 0)
        return super().complete(request)


class LangGraphTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def session(self, provider, event=True, name="run", book=None):
        return WritingSession(
            self.root / name, provider, dict(config(3), event_first=event), book=book
        )

    @staticmethod
    def nodes(session):
        return [
            r["node"]
            for r in session.last_graph_trace
            if r.get("role") == "orchestration"
        ]

    def test_live_session_is_a_compiled_graph_and_event_route_saves_one_chapter(self):
        provider = EventProvider()
        session = self.session(provider)
        self.assertEqual(type(session.graph).__module__, "langgraph.graph.state")
        row = session.write_next("继续")
        self.assertIsNone(row["stop_reason"], row)
        self.assertEqual(
            self.nodes(session),
            ["event_planner", "event_writer", "event_commit", "memory", "reviewer"],
        )
        self.assertEqual(len(session.book["chapters"]), 1)
        self.assertEqual(session.book["memory"]["processed_through"], 1)
        self.assertEqual(
            [r.role for r in provider.requests if r.role in ("planner", "writer")],
            ["planner", "writer"],
        )
        saved = json.loads(session.latest_checkpoint.read_text(encoding="utf-8"))
        self.assertEqual(saved["orchestration"], "langgraph")
        self.assertEqual(
            saved["runtime_sha256"]["orchestration"]["framework"], "langgraph"
        )

    def test_revision_conditional_edge_returns_to_planner_before_any_commit(self):
        provider = EventProvider(revise=True)
        session = self.session(provider)
        row = session.write_next("继续")
        self.assertIsNone(row["stop_reason"], row)
        self.assertEqual(
            self.nodes(session),
            [
                "event_planner",
                "event_writer",
                "event_planner",
                "event_writer",
                "event_commit",
                "memory",
                "reviewer",
            ],
        )
        self.assertEqual(len(session.book["chapters"]), 1)
        planners = [r for r in provider.requests if r.role == "planner"]
        self.assertEqual(len(planners), 2)
        self.assertIn("event_revision_request", planners[1].payload)

    def test_legacy_route_preserves_prose_when_memory_service_fails(self):
        session = self.session(Local(fail="memory"), event=False)
        row = session.write_next("继续")
        self.assertEqual(
            self.nodes(session),
            ["legacy_planner", "legacy_writer", "legacy_commit", "memory", "reviewer"],
        )
        self.assertNotEqual(row["status"], "NO_DRAFT")
        self.assertEqual(session.book["pending"], [1])
        self.assertEqual(len(session.book["chapters"]), 1)
        restored = load_resume(session.latest_checkpoint, session.plan)
        self.assertEqual(restored["chapters"], session.book["chapters"])

    def test_interrupt_reuses_prepared_events_without_repeating_planner(self):
        session = self.session(EventProvider(interrupt=True))
        with self.assertRaises(KeyboardInterrupt):
            session.write_next("继续")
        self.assertEqual(session.book["chapters"], [])
        book = load_resume(session.latest_checkpoint, session.plan)
        replacement = EventProvider()
        resumed = self.session(replacement, name="resumed", book=book)
        row = resumed.write_next("继续")
        self.assertIsNone(row["stop_reason"], row)
        self.assertFalse(any(r.role == "planner" for r in replacement.requests))
        self.assertEqual(len(resumed.book["chapters"]), 1)

    def test_pending_recovery_enters_memory_without_regenerating_prose(self):
        provider = Local(fail="memory_once")
        session = self.session(provider, event=False)
        session.write_next("继续")
        prose = copy.deepcopy(session.book["chapters"])
        calls = len([r for r in provider.requests if r.role in ("planner", "writer")])
        session.finish_pending()
        self.assertEqual(self.nodes(session), ["memory", "reviewer"])
        self.assertEqual(session.book["pending"], [])
        self.assertEqual(session.book["chapters"], prose)
        self.assertEqual(
            len([r for r in provider.requests if r.role in ("planner", "writer")]),
            calls,
        )

    def test_failed_atomic_event_save_does_not_publish_candidate(self):
        session = self.session(EventProvider())
        original = copy.deepcopy(session.book)
        save = session._save

        def fail(trace, reason):
            if reason == "DRAFT_SAVED_MEMORY_PENDING":
                raise OSError("simulated disk failure")
            return save(trace, reason)

        with patch.object(session, "_save", side_effect=fail):
            row = session.write_next("继续")
        self.assertEqual(row["status"], "NO_DRAFT")
        self.assertEqual(session.book["chapters"], [])
        self.assertEqual(session.book["writing_state"], original["writing_state"])
        self.assertIn("1", session.book["prepared_events"])

    def test_modified_runtime_checkpoint_remains_rejected(self):
        session = self.session(EventProvider())
        session.write_next("继续")
        path = session.latest_checkpoint
        saved = json.loads(path.read_text(encoding="utf-8"))
        saved["runtime_sha256"]["orchestration"]["version"] = "other-version"
        path.write_text(json.dumps(saved), encoding="utf-8")
        with self.assertRaises(ContractError):
            load_resume(path, session.plan)

    def test_reviewed_old_runtime_resumes_and_unknown_changes_are_rejected(self):
        session = self.session(EventProvider())
        session.write_next("继续")
        path = session.latest_checkpoint
        saved = json.loads(path.read_text(encoding="utf-8"))
        runtime = saved["runtime_sha256"]
        runtime["memory_runtime"]["writing.py"] = (
            "0c2766414351d40a678edcc9b5e3af881ca0e6d85a21fcc87fcebb0ee0b91d19"
        )
        runtime["memory_runtime"]["test_regression.py"] = (
            "951ce0598085e687988ab30fee10d14c5cf8e734009e3a17e0eff7dbd3ea21f0"
        )
        runtime["entrypoints"]["check_memory.py"] = (
            "f68f288c068dbc4c432ce18407fe565ef65f8aa1b3fe53824377e1172f3fe6da"
        )
        path.write_text(json.dumps(saved, ensure_ascii=False), encoding="utf-8")
        book = load_resume(path, session.plan)
        resumed = self.session(EventProvider(), name="old-resumed", book=book)
        self.assertIsNone(resumed.write_next("继续")["stop_reason"])
        self.assertEqual(len(resumed.book["chapters"]), 2)
        tampered = copy.deepcopy(saved)
        tampered["book"]["chapters"][0]["text"] = "被修改的内容"
        path.write_text(json.dumps(tampered, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(ContractError):
            load_resume(path, session.plan)

    def test_backend_recovers_changed_runtime_only_after_full_validation(self):
        from inf_backend.service import _load_compatible_checkpoint

        session = self.session(EventProvider())
        session.write_next("继续")
        path = session.latest_checkpoint
        saved = json.loads(path.read_text(encoding="utf-8"))
        saved["runtime_sha256"]["memory_runtime"]["writing.py"] = "new-runtime"
        path.write_text(json.dumps(saved, ensure_ascii=False), encoding="utf-8")
        unchanged = path.read_bytes()
        restored = _load_compatible_checkpoint(path, session.plan)
        self.assertEqual(path.read_bytes(), unchanged)
        resumed = self.session(EventProvider(), name="dynamic-resume", book=restored)
        self.assertIsNone(resumed.write_next("继续")["stop_reason"])
        self.assertEqual(len(resumed.book["chapters"]), 2)
        saved["book"]["chapters"][0]["text"] = "损坏的正文"
        path.write_text(json.dumps(saved, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(ContractError):
            _load_compatible_checkpoint(path, session.plan)
        from tome_writer.domain import digest

        saved["book"]["chapters"][0]["text"] = restored["chapters"][0]["text"]
        saved["book"]["memory"]["processed_through"] = 999
        saved["book_sha256"] = digest(canonical(saved["book"]))
        path.write_text(json.dumps(saved, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(ContractError):
            _load_compatible_checkpoint(path, session.plan)

    def test_checkpoint_from_before_test_classification_resumes(self):
        session = self.session(Local(), event=False)
        session.write_next("继续")
        path = session.latest_checkpoint
        saved = json.loads(path.read_text(encoding="utf-8"))
        runtime = saved["runtime_sha256"]
        runtime["memory_runtime"]["__init__.py"] = (
            "975bd3f06cd496a8bd99d99467758577b900f26dbeedaa777540bf6a5cf7033e"
        )
        runtime["memory_runtime"]["writing.py"] = (
            "4dfe525d3bd41eb370a9aa1399685a2aa157e7ff7199493dc697475c8391a2ee"
        )
        runtime["memory_runtime"]["test_regression.py"] = (
            "1938a437a45c925674f21360c7b35d0a955975fb929ba74bea7937c6dfb1fd19"
        )
        runtime["entrypoints"]["check_memory.py"] = (
            "a8cc33a3b15635d5ce1cfb6e7a2a9eae338eda4e3223342c55b4f4ad43d679af"
        )
        path.write_text(json.dumps(saved, ensure_ascii=False), encoding="utf-8")
        book = load_resume(path, session.plan)
        resumed = self.session(
            Local(), event=False, name="classified-resume", book=book
        )
        resumed.write_next("继续")
        self.assertEqual(len(resumed.book["chapters"]), 2)
        runtime["memory_runtime"]["writing.py"] = "unknown"
        path.write_text(json.dumps(saved, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(ContractError):
            load_resume(path, session.plan)

    def test_strict_review_branch_never_commits_rejected_candidate(self):
        class Strict:
            def __init__(self):
                self.requests = []

            def complete(self, request):
                self.requests.append(request)
                values = {
                    "planner": {
                        "number": 1,
                        "title": "来信",
                        "brief": "读信",
                        "future_updates": [],
                    },
                    "writer": {"text": "甲读了来信。"},
                    "memory": {"changes": []},
                    "reviewer": {"approved": False, "issues": ["拒绝测试"]},
                }
                return ModelReply(canonical(values[request.role]), 0, 0, 0)

        provider = Strict()
        store = FileStore(self.root / "strict")
        store.initialize(Snapshot("demo", "写故事"))
        runner = Coordinator(
            store, build_agents(ModelGateway(provider, Budget(max_calls=10)))
        )
        self.assertIn("reject", runner.graph.get_graph().nodes)
        result = runner.write_next("demo", "request-1")
        self.assertEqual(result.status, "REJECTED", result.error)
        self.assertEqual(store.load("demo").chapters, [])
        self.assertEqual(
            [r.role for r in provider.requests],
            ["planner", "writer", "memory", "reviewer"],
        )


if __name__ == "__main__":
    unittest.main()
