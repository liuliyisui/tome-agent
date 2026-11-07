"""Exercise real compiled graphs with deterministic providers; no remote LLM."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inf_writer.agents import build_agents
from inf_writer.domain import ContractError, Snapshot, canonical
from inf_writer.models import Budget, ModelGateway, ModelReply
from inf_writer.runtime import Coordinator
from inf_writer.storage import FileStore
from memory_runtime.test_writing import Local, config
from memory_runtime.writing import WritingSession, load_resume


class EventProvider(Local):
    def __init__(self, revise=False, interrupt=False):
        super().__init__()
        self.revise = revise
        self.interrupt = interrupt

    def complete(self, request):
        if request.role == 'planner':
            self.requests.append(copy.deepcopy(request))
            self.number = request.payload['chapter_number']
            value = dict(number=self.number, title='来信', brief='读信', future_updates=[],
                scenes=[dict(purpose='调查', participants=['甲'], beats=[dict(
                    statement='甲读了来信。', assertion_scope='performed_action',
                    requires=[], changes=[])])])
            return ModelReply(canonical(value), 1, 1, 0)
        if request.role == 'writer':
            self.requests.append(copy.deepcopy(request))
            if self.interrupt:
                raise KeyboardInterrupt()
            if self.revise:
                self.revise = False
                return ModelReply(canonical(dict(event_revision_request='调整读信场景')), 1, 1, 0)
            return ModelReply(canonical(dict(text='甲读了来信。')), 1, 1, 0)
        return super().complete(request)


class LangGraphTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def session(self, provider, event=True, name='run', book=None):
        return WritingSession(self.root / name, provider,
            dict(config(3), event_first=event), book=book)

    @staticmethod
    def nodes(session):
        return [r['node'] for r in session.last_graph_trace if r.get('role') == 'orchestration']

    def test_live_session_is_a_compiled_graph_and_event_route_saves_one_chapter(self):
        provider = EventProvider()
        session = self.session(provider)
        self.assertEqual(type(session.graph).__module__, 'langgraph.graph.state')
        row = session.write_next('继续')
        self.assertIsNone(row['stop_reason'], row)
        self.assertEqual(self.nodes(session), ['event_planner', 'event_writer', 'event_commit', 'memory', 'reviewer'])
        self.assertEqual(len(session.book['chapters']), 1)
        self.assertEqual(session.book['memory']['processed_through'], 1)
        self.assertEqual([r.role for r in provider.requests if r.role in ('planner', 'writer')], ['planner', 'writer'])
        saved = json.loads(session.latest_checkpoint.read_text(encoding='utf-8'))
        self.assertEqual(saved['orchestration'], 'langgraph')
        self.assertEqual(saved['runtime_sha256']['orchestration']['framework'], 'langgraph')

    def test_revision_conditional_edge_returns_to_planner_before_any_commit(self):
        provider = EventProvider(revise=True)
        session = self.session(provider)
        row = session.write_next('继续')
        self.assertIsNone(row['stop_reason'], row)
        self.assertEqual(self.nodes(session), ['event_planner', 'event_writer', 'event_planner', 'event_writer', 'event_commit', 'memory', 'reviewer'])
        self.assertEqual(len(session.book['chapters']), 1)
        planners = [r for r in provider.requests if r.role == 'planner']
        self.assertEqual(len(planners), 2)
        self.assertIn('event_revision_request', planners[1].payload)

    def test_legacy_route_preserves_prose_when_memory_service_fails(self):
        session = self.session(Local(fail='memory'), event=False)
        row = session.write_next('继续')
        self.assertEqual(self.nodes(session), ['legacy_planner', 'legacy_writer', 'legacy_commit', 'memory', 'reviewer'])
        self.assertNotEqual(row['status'], 'NO_DRAFT')
        self.assertEqual(session.book['pending'], [1])
        self.assertEqual(len(session.book['chapters']), 1)
        restored = load_resume(session.latest_checkpoint, session.plan)
        self.assertEqual(restored['chapters'], session.book['chapters'])

    def test_interrupt_reuses_prepared_events_without_repeating_planner(self):
        session = self.session(EventProvider(interrupt=True))
        with self.assertRaises(KeyboardInterrupt):
            session.write_next('继续')
        self.assertEqual(session.book['chapters'], [])
        book = load_resume(session.latest_checkpoint, session.plan)
        replacement = EventProvider()
        resumed = self.session(replacement, name='resumed', book=book)
        row = resumed.write_next('继续')
        self.assertIsNone(row['stop_reason'], row)
        self.assertFalse(any(r.role == 'planner' for r in replacement.requests))
        self.assertEqual(len(resumed.book['chapters']), 1)

    def test_pending_recovery_enters_memory_without_regenerating_prose(self):
        provider = Local(fail='memory_once')
        session = self.session(provider, event=False)
        session.write_next('继续')
        prose = copy.deepcopy(session.book['chapters'])
        calls = len([r for r in provider.requests if r.role in ('planner', 'writer')])
        session.finish_pending()
        self.assertEqual(self.nodes(session), ['memory', 'reviewer'])
        self.assertEqual(session.book['pending'], [])
        self.assertEqual(session.book['chapters'], prose)
        self.assertEqual(len([r for r in provider.requests if r.role in ('planner', 'writer')]), calls)

    def test_failed_atomic_event_save_does_not_publish_candidate(self):
        session = self.session(EventProvider())
        original = copy.deepcopy(session.book)
        save = session._save

        def fail(trace, reason):
            if reason == 'DRAFT_SAVED_MEMORY_PENDING':
                raise OSError('simulated disk failure')
            return save(trace, reason)

        with patch.object(session, '_save', side_effect=fail):
            row = session.write_next('继续')
        self.assertEqual(row['status'], 'NO_DRAFT')
        self.assertEqual(session.book['chapters'], [])
        self.assertEqual(session.book['writing_state'], original['writing_state'])
        self.assertIn('1', session.book['prepared_events'])

    def test_modified_runtime_checkpoint_remains_rejected(self):
        session = self.session(EventProvider())
        session.write_next('继续')
        path = session.latest_checkpoint
        saved = json.loads(path.read_text(encoding='utf-8'))
        saved['runtime_sha256']['orchestration']['version'] = 'other-version'
        path.write_text(json.dumps(saved), encoding='utf-8')
        with self.assertRaises(ContractError):
            load_resume(path, session.plan)

    def test_strict_review_branch_never_commits_rejected_candidate(self):
        class Strict:
            def __init__(self): self.requests = []
            def complete(self, request):
                self.requests.append(request)
                values = dict(planner=dict(number=1, title='来信', brief='读信', future_updates=[]),
                    writer=dict(text='甲读了来信。'), memory=dict(changes=[]),
                    reviewer=dict(approved=False, issues=['拒绝测试']))
                return ModelReply(canonical(values[request.role]), 0, 0, 0)
        provider = Strict()
        store = FileStore(self.root / 'strict')
        store.initialize(Snapshot('demo', '写故事'))
        runner = Coordinator(store, build_agents(ModelGateway(provider, Budget(max_calls=10))))
        self.assertIn('reject', runner.graph.get_graph().nodes)
        result = runner.write_next('demo', 'request-1')
        self.assertEqual(result.status, 'REJECTED', result.error)
        self.assertEqual(store.load('demo').chapters, [])
        self.assertEqual([r.role for r in provider.requests], ['planner', 'writer', 'memory', 'reviewer'])


if __name__ == '__main__':
    unittest.main()
