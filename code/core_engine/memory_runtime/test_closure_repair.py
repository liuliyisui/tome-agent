"""Failure-isolation, persistence, and formal-runner closure repair tests."""
import copy
import json
from types import SimpleNamespace
import unittest

from memory_runtime import test_story_closure as fixtures
from inf_writer.domain import canonical
from inf_writer.models import ModelReply
from memory_runtime.story_closure import StoryClosure
ClosureLocal = fixtures.ClosureLocal


class RepairProvider:
    def __init__(self):
        self.requests = []
        self.review_bad = True
        self.repair_bad = False
        self.repair_pending = False
        self.extra_peer = False
        self.metadata_bad = False
        self.review_malformed = False
        self.add_question = False

    def complete(self, request):
        self.requests.append(copy.deepcopy(request))
        p = request.payload
        if request.role == 'closure_repair':
            if self.repair_bad:
                raise RuntimeError('simulated outage')
            rows = [dict(id=r['id'], status='pending' if self.repair_pending else 'resolved',
                reason='按已保存正文重新确认', evidence=[] if self.repair_pending else [dict(source_choice=1)])
                for r in p['obligations']]
            if self.extra_peer:
                rows.append(dict(id='O1', status='pending', reason='未经授权覆盖', evidence=[]))
            fields = [dict(job_key=j['key'], new_obligations=[dict(question='新核心问题', acceptance='正文解决')] if self.add_question else [],
                ending_closed=True) for j in p['failed_items'] if j['kind']=='review']
            return ModelReply(canonical(dict(obligations=rows, review_fields=fields)), 1, 1, 0)
        if request.role == 'closure_reviewer':
            if self.review_malformed:
                return ModelReply('{broken', 1, 1, 0)
            rows = [dict(id=r['id'], status='resolved', reason='正文已交代',
                evidence=[dict(source_choice=999 if self.review_bad and r['id']!='O1' else 1)]) for r in p['obligations']]
            value = dict(obligations=rows, ending_closed=True)
            if not self.metadata_bad:
                value['new_obligations'] = []
            return ModelReply(canonical(value), 1, 1, 0)
        raise AssertionError(request.role)


class RepairTests(unittest.TestCase):
    def controller(self, provider):
        obligations = [dict(id=f'O{i}', question=f'问题{i}', acceptance='正文交代',
            status='pending', evidence=[], reason='待完成') for i in (1, 2)]
        self.saved = []
        session = SimpleNamespace(plan=dict(goal='完成记录', constraints=[], chapters=1), gateway=provider,
            book=dict(chapters=[dict(number=1, text='甲完成记录。乙公开作证。')],
                story_closure=dict(status='UNRESOLVED', obligations=obligations, coverage={}, failures=[], checks=[])))
        session._save = lambda *args: self.saved.append(json.loads(canonical(session.book)))
        return StoryClosure(session)

    def observe(self, controller):
        controller.observe(controller.session.book['chapters'][-1])

    def calls(self, provider):
        return [r for r in provider.requests if r.role=='closure_repair']

    def test_immediate_repair_targets_only_failed_item(self):
        provider = RepairProvider(); controller = self.controller(provider)
        self.observe(controller)
        request = self.calls(provider)[0]
        self.assertEqual([r['id'] for r in request.payload['obligations']], ['O2'])
        self.assertFalse(controller.repairs.pending())
        self.assertTrue(controller.passed())
        self.assertEqual(controller.state['obligations'][0]['reason'], '正文已交代')
        before_dispatch = next(b for b in self.saved if b['story_closure']['repair_jobs'].get('obligation:O2', {}).get('attempts')==1)
        self.assertEqual(before_dispatch['story_closure']['repair_jobs']['obligation:O2']['status'], 'PENDING')

    def test_outage_is_persisted_retried_next_chapter_and_bounded(self):
        provider = RepairProvider(); provider.repair_bad = True
        controller = self.controller(provider); self.observe(controller)
        self.assertEqual(len(self.calls(provider)), 1)
        controller.retry_pending(); controller.retry_pending()
        self.assertEqual(len(self.calls(provider)), 1)
        # JSON round-trip simulates a process restart from a durable checkpoint.
        controller.session.book = json.loads(canonical(controller.session.book))
        controller = StoryClosure(controller.session)
        controller.retry_pending()
        self.assertEqual(len(self.calls(provider)), 1)
        controller.session.book['chapters'].append(dict(number=2, text='乙公开作证，记录完成。'))
        provider.repair_bad = False
        self.observe(controller)
        self.assertEqual(len(self.calls(provider)), 2)
        self.assertFalse(controller.repairs.pending())
        self.assertTrue(controller.passed())
        self.assertEqual(self.calls(provider)[-1].payload['latest_completed_chapter'], 2)

    def test_valid_newer_review_supersedes_old_repair(self):
        provider = RepairProvider(); provider.repair_bad = True
        controller = self.controller(provider); self.observe(controller)
        controller.session.book['chapters'].append(dict(number=2, text='乙已公开作证。'))
        provider.review_bad = False
        self.observe(controller)
        self.assertEqual(len(self.calls(provider)), 1)
        self.assertFalse(controller.repairs.pending())
        self.assertEqual(controller.repairs.jobs['obligation:O2']['resolution'], 'FRESH_VALID_REVIEW')
        self.assertTrue(controller.passed())

    def test_extra_peer_update_cannot_overwrite_good_row(self):
        provider = RepairProvider(); provider.extra_peer = True
        controller = self.controller(provider); self.observe(controller)
        self.assertEqual(controller.state['obligations'][0]['reason'], '正文已交代')
        self.assertEqual(controller.state['obligations'][0]['status'], 'resolved')
        self.assertTrue(controller.state['repair_history'][0]['issues'])

    def test_valid_pending_answer_clears_engineering_queue_without_claiming_ending(self):
        provider = RepairProvider(); provider.repair_pending = True
        controller = self.controller(provider); self.observe(controller)
        self.assertFalse(controller.repairs.pending())
        self.assertEqual(controller.state['obligations'][1]['status'], 'pending')
        self.assertFalse(controller.passed())

    def test_bad_metadata_is_repaired_without_overwriting_good_rows(self):
        provider = RepairProvider(); provider.metadata_bad = True; provider.review_bad = False
        controller = self.controller(provider); self.observe(controller)
        request = self.calls(provider)[0]
        self.assertEqual(request.payload['obligations'], [])
        self.assertTrue(request.payload['repair_review_fields'])
        self.assertTrue(controller.passed())
        self.assertTrue(all(r['reason']=='正文已交代' for r in controller.state['obligations']))

    def test_unparseable_reply_can_recover_with_existing_source(self):
        provider = RepairProvider(); provider.review_malformed = True
        controller = self.controller(provider); self.observe(controller)
        self.assertTrue(controller.state['failures'])
        self.assertFalse(controller.repairs.pending())
        self.assertTrue(controller.passed())

    def test_repair_cannot_hide_new_core_question(self):
        provider = RepairProvider(); provider.metadata_bad = True; provider.add_question = True
        controller = self.controller(provider); self.observe(controller)
        self.assertFalse(controller.repairs.pending())
        self.assertEqual(controller.state['obligations'][-1]['status'], 'pending')
        self.assertFalse(controller.passed())

    def test_final_retry_is_bounded_and_remaining_jobs_prevent_pass(self):
        provider = RepairProvider(); provider.repair_bad = True
        controller = self.controller(provider); self.observe(controller)
        controller.retry_pending(final=True); controller.retry_pending(final=True)
        self.assertEqual(len(self.calls(provider)), 2)
        self.assertTrue(controller.repairs.pending())
        controller.state['status'] = 'MODEL_PASSED'
        self.assertFalse(controller.passed())

    def test_modified_source_cannot_be_repaired_using_stale_evidence(self):
        provider = RepairProvider(); provider.repair_bad = True
        controller = self.controller(provider); self.observe(controller)
        controller.session.book['chapters'][0]['text'] += '后文推翻证言。'
        provider.repair_bad = False
        controller.retry_pending(final=True)
        self.assertEqual(len(self.calls(provider)), 1)
        self.assertTrue(controller.repairs.pending())
        self.assertFalse(controller.passed())

    def test_large_queue_is_processed_in_bounded_batches(self):
        provider = RepairProvider(); controller = self.controller(provider)
        for i in range(3, 8):
            controller.state['obligations'].append(dict(id=f'O{i}', question=f'问题{i}',
                acceptance='正文交代', status='pending', reason='待完成', evidence=[]))
        self.observe(controller)
        self.assertEqual(len(self.calls(provider)), 1)
        self.assertEqual(len(controller.repairs.pending()), 2)
        controller.retry_pending(final=True)
        self.assertEqual(len(self.calls(provider)), 2)
        self.assertFalse(controller.repairs.pending())
        self.assertTrue(controller.passed())

    def test_bad_repair_format_and_choices_remain_queued_with_feedback(self):
        for mode in ('json', 'boolean', 'missing', 'unknown'):
            class BadRepair(RepairProvider):
                def complete(self, request):
                    reply = super().complete(request)
                    if request.role != 'closure_repair':
                        return reply
                    if mode == 'json':
                        return ModelReply('{broken', 1, 1, 0)
                    value = json.loads(reply.content)
                    row = value['obligations'][0]
                    if mode == 'missing':
                        value['obligations'] = []
                    else:
                        row['evidence'] = [dict(source_choice=True if mode=='boolean' else 999)]
                    return ModelReply(canonical(value), 1, 1, 0)
            with self.subTest(mode=mode):
                provider = BadRepair(); controller = self.controller(provider); self.observe(controller)
                self.assertTrue(controller.repairs.pending())
                self.assertFalse(controller.passed())
                self.assertTrue(controller.repairs.jobs['obligation:O2']['last_error'])
                self.assertEqual(controller.state['obligations'][0]['reason'], '正文已交代')

    def test_three_valid_sources_are_saved_in_full_but_context_stays_bounded(self):
        from memory_runtime.story_closure import evidence_sources, obligation_view
        controller = self.controller(RepairProvider())
        chapter = controller.session.book['chapters'][0]
        chapter['text'] = '甲完成记录。' * 180
        sources = evidence_sources({1: chapter['text']}, 1, 0, len(chapter['text']), [])
        # Different lengths prevent repetitive text from deduplicating all quotes.
        sources[1]['start'] += 1; sources[1]['quote'] = chapter['text'][sources[1]['start']:sources[1]['end']]
        sources[2]['start'] += 2; sources[2]['quote'] = chapter['text'][sources[2]['start']:sources[2]['end']]
        issues = []
        rows = controller.validate_rows(dict(obligations=[dict(id='O2', status='resolved', reason='正文已交代',
            evidence=[dict(source_choice=i) for i in (1,2,3)])]), sources, issues, target_ids={'O2'})
        self.assertFalse(issues)
        self.assertEqual(len(rows[0]['evidence']), 3)
        view = obligation_view(rows)
        self.assertEqual(len(view[0]['evidence']), 2)
        self.assertEqual(view[0]['omitted_evidence_count'], 1)
        self.assertEqual(len(rows[0]['evidence']), 3)


class RepairRunnerTests(unittest.TestCase):
    setUp = fixtures.ClosureTests.setUp
    run_book = fixtures.ClosureTests.run_book

    def test_repair_outage_never_stops_prose_and_is_reported(self):
        class OfflineRepair(ClosureLocal):
            def complete(self, request):
                if request.role=='closure_repair':
                    self.requests.append(copy.deepcopy(request))
                    raise RuntimeError('repair unavailable')
                return super().complete(request)
        result = self.run_book(OfflineRepair('fabricated'))
        self.assertTrue(result['generation_completed'])
        self.assertEqual(result['chapters'], 2)
        self.assertTrue(result['pending_closure_repair_jobs'])
        self.assertFalse(result['draft_completed'])
        self.assertEqual(result['stop_reason'], 'STORY_CLOSURE_UNVERIFIED')


if __name__ == '__main__':
    unittest.main()
