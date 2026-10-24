"""Offline closure contracts and real runner integration; no API credentials."""
import contextlib
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from memory_runtime.test_writing import Local, config, cli, ROOT
from inf_writer.domain import canonical
from inf_writer.models import ModelReply
from memory_runtime.story_closure import StoryClosure, evidence_sources, phase, CHUNK_CHARS


class ClosureLocal(Local):
    def __init__(self, mode='resolved', resolve_at=1):
        super().__init__()
        self.mode = mode
        self.resolve_at = resolve_at

    def complete(self, request):
        p = request.payload
        if request.role == 'closure_planner':
            self.requests.append(copy.deepcopy(request))
            rows = [] if self.mode == 'empty' else [dict(question='记录完成了吗', acceptance='正文明确写出完成')]
            return ModelReply(canonical(dict(obligations=rows)), 1, 1, 0)
        if request.role == 'closure_reviewer':
            self.requests.append(copy.deepcopy(request))
            if self.mode == 'outage':
                raise RuntimeError('offline outage')
            resolved = self.mode != 'pending' and p['chapter'] >= self.resolve_at
            evidence = [dict(chapter=p['chapter'], quote=p['saved_prose'][:30])] if resolved else []
            if self.mode == 'fabricated':
                evidence = [dict(chapter=p['chapter'], quote='正文没有这句')]
            rows = [dict(id=r['id'], status='resolved' if resolved else 'pending',
                reason='离线夹具设定', evidence=evidence) for r in p['obligations']]
            if self.mode == 'omitted':
                rows = []
            additions = [dict(question=f"新核心问题{p['chapter']}", acceptance='正文交代')] if self.mode == 'new' else []
            return ModelReply(canonical(dict(obligations=rows, new_obligations=additions,
                ending_closed=resolved and p['final_check'])), 1, 1, 0)
        return super().complete(request)


class ClosureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT/'runs')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_book(self, provider, cap=2, event_first=False):
        cfg = dict(config(1), max_chapters=cap, closure_enabled=True, event_first=event_first)
        with patch.object(cli, 'read_secret', return_value='offline'), \
                patch.object(cli, 'ChatCompletionProvider', return_value=provider), \
                contextlib.redirect_stdout(io.StringIO()):
            return cli.launch(cfg, self.root/'book')

    def test_default_enabled_and_boolean_validation(self):
        cfg = config(); cfg.pop('closure_enabled')
        self.assertTrue(cli.validate_config(cfg)['closure_enabled'])
        with self.assertRaises(ValueError):
            cli.validate_config(dict(cfg, closure_enabled='yes'))

    def test_length_does_not_mean_finished(self):
        result = self.run_book(ClosureLocal('pending'))
        self.assertTrue(result['generation_completed'])
        self.assertFalse(result['draft_completed'])
        self.assertEqual(result['stop_reason'], 'STORY_UNRESOLVED')
        self.assertEqual(result['chapters'], 2)

    def test_resolution_with_real_prose_evidence(self):
        result = self.run_book(ClosureLocal())
        self.assertTrue(result['draft_completed'])
        self.assertEqual(result['chapters'], 1)
        self.assertEqual(result['story_closure_status'], 'MODEL_PASSED')
        self.assertFalse(result['quality_gate_passed'])

    def test_recovery_uses_only_existing_chapter_cap(self):
        provider = ClosureLocal(resolve_at=2)
        result = self.run_book(provider)
        self.assertEqual(result['chapters'], 2)
        self.assertTrue(result['draft_completed'])
        planners = [r for r in provider.requests if r.role == 'planner']
        self.assertIn('尚需交代', planners[-1].payload['instruction'])
        self.assertEqual(planners[-1].payload['story_closure']['phase'], 'finale')

    def test_invalid_or_unavailable_review_never_passes(self):
        for mode in ('fabricated', 'outage', 'empty', 'omitted'):
            with self.subTest(mode=mode):
                # Each run needs a distinct output directory.
                self.root = Path(self.temp.name)/mode
                result = self.run_book(ClosureLocal(mode))
                self.assertFalse(result['draft_completed'])
                self.assertEqual(result['stop_reason'], 'STORY_CLOSURE_UNVERIFIED')

    def test_new_central_question_prevents_false_ending(self):
        result = self.run_book(ClosureLocal('new'))
        self.assertFalse(result['draft_completed'])

    def test_event_first_keeps_general_review_off_but_checks_ending(self):
        from memory_runtime.test_event_first import EventLocal
        from tools.testing.archived_plan_fixture import compile_archived_plan
        class EventClosure(ClosureLocal, EventLocal):
            pass
        provider = EventClosure()
        with patch('memory_runtime.reference_choices.compile_plan', side_effect=compile_archived_plan):
            result = self.run_book(provider, event_first=True)
        self.assertTrue(result['draft_completed'])
        self.assertFalse(result['story_review_enabled'])
        self.assertTrue(any(r.role == 'closure_reviewer' for r in provider.requests))
        self.assertFalse(any(r.role == 'reviewer' for r in provider.requests))
        writer = next(r for r in provider.requests if r.role == 'writer')
        self.assertIn('story_closure', writer.payload)

    def test_phase_schedule(self):
        plan = dict(chapters=20)
        self.assertEqual(phase(plan, 1), 'development')
        self.assertEqual(phase(plan, 17), 'closing')
        self.assertEqual(phase(plan, 20), 'finale')

    def test_long_chapter_is_chunked_and_checkpointed(self):
        class Session:
            plan = dict(goal='完成记录', constraints=[], chapters=1, closure_enabled=True)
            gateway = ClosureLocal()
            book = dict(chapters=[])
            def _save(self, trace, reason): pass
        session = Session(); controller = StoryClosure(session); controller.initialize()
        chapter = dict(number=1, text='甲的记录完成。' * (CHUNK_CHARS//6))
        session.book['chapters'].append(chapter); controller.observe(chapter)
        requests = [r for r in session.gateway.requests if r.role == 'closure_reviewer']
        self.assertGreater(len(requests), 1)
        self.assertTrue(all(len(r.payload['saved_prose']) <= CHUNK_CHARS+600 for r in requests))
        self.assertTrue(controller.covered()); self.assertTrue(controller.passed())
        chapter['text'] += '改变'
        self.assertFalse(controller.passed())

    def test_resumed_contract_is_not_recreated(self):
        class Session:
            plan = dict(goal='完成记录', constraints=[], chapters=1, closure_enabled=True)
            gateway = ClosureLocal()
            book = dict(chapters=[])
            def _save(self, trace, reason): pass
        session = Session(); StoryClosure(session).initialize()
        StoryClosure(session).initialize()
        self.assertEqual(sum(r.role == 'closure_planner' for r in session.gateway.requests), 1)

    def test_missing_earlier_review_cannot_be_hidden_by_passing_ending(self):
        class Session:
            plan = dict(goal='完成记录', constraints=[], chapters=2, closure_enabled=True)
            gateway = ClosureLocal('outage')
            book = dict(chapters=[])
            def _save(self, trace, reason): pass
        session = Session(); controller = StoryClosure(session); controller.initialize()
        session.book['chapters'].append(dict(number=1, text='甲开始记录。'))
        controller.observe(session.book['chapters'][-1])
        session.gateway.mode = 'resolved'
        session.book['chapters'].append(dict(number=2, text='甲完成记录。'))
        controller.observe(session.book['chapters'][-1])
        self.assertEqual(controller.state['status'], 'UNKNOWN')
        self.assertFalse(controller.passed())

    def controller(self, provider=None):
        obligations = [dict(id=f'O{i}', question=f'问题{i}', acceptance='正文交代',
            status='pending', evidence=[], reason='待完成') for i in (1, 2)]
        session = SimpleNamespace(plan=dict(goal='完成记录', constraints=[], chapters=1),
            gateway=provider, book=dict(chapters=[dict(number=1, text='甲完成记录。乙公开作证。')],
                story_closure=dict(status='UNRESOLVED', obligations=obligations,
                    coverage={}, failures=[], checks=[])), _save=lambda *args: None)
        return StoryClosure(session)

    def test_one_bad_quote_does_not_rollback_other_obligations(self):
        controller = self.controller()
        rows = [dict(id='O1', status='resolved', reason='甲已完成',
                     evidence=[dict(chapter=1, quote='甲完成记录。')]),
                dict(id='O2', status='resolved', reason='乙已完成',
                     evidence=[dict(chapter=1, quote='伪造引文')])]
        issues = []
        updated = controller.validate_rows(dict(obligations=rows), issues=issues)
        self.assertEqual([r['status'] for r in updated], ['resolved', 'uncertain'])
        self.assertEqual(updated[0]['evidence'][0]['quote'], '甲完成记录。')
        self.assertEqual([r['id'] for r in issues], ['O2'])

    def test_choice_binds_program_text_and_rejects_bad_or_boolean_choices(self):
        controller = self.controller()
        sources = evidence_sources({1: '甲完成记录。乙公开作证。'}, 1, 0, 12, [])
        for bad in (True, 0, 999, '1'):
            issues = []
            updated = controller.validate_rows(dict(obligations=[
                dict(id='O1', status='resolved', reason='已完成', evidence=[dict(source_choice=1, quote='模型改写')]),
                dict(id='O2', status='resolved', reason='已完成', evidence=[dict(source_choice=bad)])]), sources, issues)
            self.assertEqual([r['status'] for r in updated], ['resolved', 'uncertain'])
            self.assertEqual(updated[0]['evidence'][0]['quote'], sources[0]['quote'])
            self.assertTrue(issues)

    def test_missing_duplicate_and_bad_rows_are_isolated(self):
        for bad_rows in ([], [None], [{'id': []}], [dict(id='O2'), dict(id='O2')]):
            controller = self.controller(); issues = []
            good = dict(id='O1', status='resolved', reason='已完成', evidence=[dict(chapter=1, quote='甲完成记录。')])
            updated = controller.validate_rows(dict(obligations=[good]+bad_rows), issues=issues)
            self.assertEqual([r['status'] for r in updated], ['resolved', 'uncertain'])
            self.assertTrue(issues)

    def test_old_resolution_is_not_retained_after_invalid_update(self):
        controller = self.controller()
        controller.state['obligations'][1]['status'] = 'resolved'
        updated = controller.validate_rows(dict(obligations=[]))
        self.assertTrue(all(r['status'] == 'uncertain' for r in updated))

    def test_partial_observation_can_recover_without_permanent_coverage_gap(self):
        class Partial:
            broken = True
            def complete(self, request):
                rows = [dict(id=r['id'], status='resolved', reason='正文交代',
                    evidence=[dict(source_choice=999 if self.broken and r['id']=='O2' else 1)])
                    for r in request.payload['obligations']]
                return ModelReply(canonical(dict(obligations=rows, new_obligations=[], ending_closed=True)), 1, 1, 0)
        provider = Partial(); controller = self.controller(provider)
        controller.observe(controller.session.book['chapters'][0])
        self.assertEqual([r['status'] for r in controller.state['obligations']], ['resolved', 'uncertain'])
        self.assertEqual(controller.state['status'], 'UNKNOWN')
        self.assertTrue(controller.covered())
        self.assertFalse(controller.passed())
        self.assertFalse(controller.state['checks'][-1]['update_complete'])
        provider.broken = False
        controller.session.book['chapters'].append(dict(number=2, text='乙完成公开作证。'))
        controller.observe(controller.session.book['chapters'][-1])
        self.assertTrue(controller.passed())
        self.assertTrue(controller.state['update_issues'])

    def test_bad_addition_does_not_rollback_valid_rows_or_pass(self):
        class BadAddition:
            def complete(self, request):
                rows = [dict(id=r['id'], status='resolved', reason='正文交代', evidence=[dict(source_choice=1)])
                    for r in request.payload['obligations']]
                return ModelReply(canonical(dict(obligations=rows, new_obligations=[{'question': None}], ending_closed=True)), 1, 1, 0)
        controller = self.controller(BadAddition())
        controller.observe(controller.session.book['chapters'][0])
        self.assertTrue(all(r['status'] == 'resolved' for r in controller.state['obligations']))
        self.assertFalse(controller.passed())

    def test_source_hash_change_is_rejected(self):
        controller = self.controller()
        sources = evidence_sources({1: controller.session.book['chapters'][0]['text']}, 1, 0, 12, [])
        controller.session.book['chapters'][0]['text'] += '后文推翻'
        issues = []
        updated = controller.validate_rows(dict(obligations=[dict(id=r['id'], status='resolved',
            reason='完成', evidence=[dict(source_choice=1)]) for r in controller.state['obligations']]), sources, issues)
        self.assertTrue(all(r['status'] == 'uncertain' for r in updated))
        self.assertFalse(any(r['evidence'] for r in updated))


if __name__ == '__main__':
    unittest.main()
