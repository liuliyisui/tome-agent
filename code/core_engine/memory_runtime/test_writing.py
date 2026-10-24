"""Actual launcher, real memory pipeline, deterministic offline model replies."""
import copy
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import write_novel as cli
from inf_writer.domain import ContractError,canonical
from inf_writer.models import ModelReply
from memory_runtime.writing import load_resume,WritingSession
from memory_runtime.story_review import StoryReferenceGateway
from inf_writer.light_memory import LightAgent,validate_light_review
from inf_writer.models import ModelRequest


def config(chapters=4):
    return dict(title='接入测试',goal='甲的记录逐章增长',constraints=[],chapters=chapters,max_chapters=chapters,
        target_han_chars=1,endpoint='https://fixture.invalid/chat/completions',model='offline',
        input_usd_per_million=0.3,output_usd_per_million=1.2,thinking_enabled=False,event_first=False,closure_enabled=False)


class Local:
    def __init__(self,fail=None,reject=False,withhold=False):
        self.requests=[];self.number=0;self.fail=fail;self.reject=reject;self.withhold=withhold
    def complete(self,request):
        self.requests.append(copy.deepcopy(request));p=request.payload
        if self.fail=='memory_once' and 'memory_contract' in p:
            self.fail=None;raise RuntimeError('offline one-time memory outage')
        if self.fail=='memory' and 'memory_contract' in p:raise RuntimeError('offline memory outage')
        if self.fail=='review' and p.get('review_mode')=='light_memory':raise RuntimeError('offline review outage')
        if self.fail=='adjudication' and p.get('issue_consistency_review'):raise RuntimeError('offline consistency outage')
        if self.fail=='layers2' and p.get('completed_chapter')==2:raise RuntimeError('offline layer outage')
        if self.fail=='interrupt' and 'memory_contract' in p:raise KeyboardInterrupt()
        if request.role=='planner':
            self.number=p['chapter_number'];value=dict(number=self.number,title='甲的记录',brief='甲的记录接续',future_updates=[])
        elif request.role=='writer':value=dict(text=f'甲的第{self.number}次记录已经完成。',continuity_updates=[],no_continuity_change_reason='仅一般记录动作，无日期、物证、签收或逐页核对变化')
        elif 'memory_contract' in p:
            n=p['chapter_number'];value=dict(changes=[dict(op='add',subject='甲',attribute='anchor' if n==1 else 'notes',
                claim=f'甲的第{n}次记录已经完成。',kind='event',status='active',source_refs=[dict(chapter_number=n,evidence_id='e0001')])])
        elif 'memory_mutation_review' in p:
            value=dict(decisions=[dict(ref=r['ref'],decision='keep_current' if self.withhold else 'accept',reason='离线明确设定') for r in p['proposals']])
        elif 'candidate_items' in p:
            value=dict(checked_ids=[r['id'] for r in p['candidate_items']],changes=[],no_change_reason='旧事件仍成立')
        elif 'completed_chapter' in p:
            rows=[]
            for r in p['items']:
                desired='working' if r['attribute']=='anchor' else 'recent' if r['tier']=='working' else 'long'
                rows.append(dict(id=r['id'],tier=desired if desired in r['allowed_tiers'] else r['tier'],priority=3,reason='离线分层'))
            value=dict(placements=rows)
        elif p.get('issue_consistency_review'):
            value=dict(decisions=[dict(ref=r['ref'],classification='confirmed',reason='离线夹具明确设定为矛盾',
                draft_evidence=[r['proposed_issue']['draft_quote']],basis_evidence=[r['proposed_issue']['basis_quote']]) for r in p['candidates']])
        elif p.get('review_mode')=='light_memory':
            issues=[]
            if self.reject:
                refs=p['hard_references'];ref=next(k for k in refs if k.startswith('draft_'))
                issues=[dict(kind='causality',description='离线模拟拒绝',draft_quote=p['current_draft'],basis_ref=ref,basis_quote=refs[ref])]
            value=dict(approved=not issues,issues=issues,suggestions=[])
        else:raise AssertionError('Unexpected request schema')
        return ModelReply(canonical(value),1,1,0)


class WritingIntegration(unittest.TestCase):
    def test_actual_chapter_eleven_review_reference_replays_without_changing_rejection(self):
        folder=ROOT/'runs/writing_tiered_30000_20261021_a'
        ctx=self.read(folder/'final_state.json')['review_jobs']['11']
        raw=self.read(folder/'call_087.response.json')['content'];requests=[]
        class Saved:
            def complete(self,request):requests.append(request);return ModelReply(raw,1,1,0)
        transport=StoryReferenceGateway(Saved());trace=[]
        value=LightAgent('reviewer',transport).run(ctx,trace)
        self.assertFalse(value['approved']);self.assertEqual(len(value['issues']),1)
        self.assertEqual(len(requests),1);self.assertTrue(value['issues'][0]['basis_ref'].startswith('fact_'))
        original=json.loads(raw)['issues'][0]
        self.assertEqual(value['issues'][0]['description'],original['description'])
        self.assertEqual(value['issues'][0]['basis_quote'],original['basis_quote'])
        self.assertEqual(transport.transforms[0]['raw_output'],raw)

    def test_story_reference_alias_never_guesses_unknown_id_or_fabricates_quote(self):
        payload=dict(review_mode='light_memory',current_draft='甲到了。',
            active_facts=[dict(memory_id='m_known',value='旧事实')],hard_references={'fact_1':'旧事实'})
        for identifier,quote in (('m_unknown','旧事实'),('m_known','不存在的证据')):
            body=dict(approved=False,issues=[dict(kind='fact_conflict',description='模拟',draft_quote='甲到了。',
                basis_ref=identifier,basis_quote=quote)],suggestions=[])
            class Saved:
                def complete(self,request):return ModelReply(canonical(body),1,1,0)
            transport=StoryReferenceGateway(Saved());request=ModelRequest('reviewer','',payload,8192)
            parsed=json.loads(transport.complete(request).content)
            with self.assertRaises(ContractError):validate_light_review(parsed,payload)

    def setUp(self):
        self.directory=tempfile.TemporaryDirectory(dir=ROOT/'runs');self.addCleanup(self.directory.cleanup)
        self.root=Path(self.directory.name)
    def launch(self,provider,name='output',cfg=None,resume=None):
        with patch.object(cli,'read_secret',return_value='offline-not-secret'),patch.object(cli,'ChatCompletionProvider',return_value=provider),contextlib.redirect_stdout(io.StringIO()):
            return cli.launch(cfg or config(),self.root/name,resume=resume)
    def read(self,path):return json.loads(path.read_text(encoding='utf-8'))

    def test_default_launcher_uses_live_runtime_and_runs_all_memory_phases(self):
        provider=Local();result=self.launch(provider)
        self.assertEqual(cli.SOURCE,ROOT/'memory_runtime/src')
        self.assertTrue(result['draft_completed']);self.assertTrue(result['memory_complete'])
        self.assertEqual(result['memory_processed_through'],4);self.assertEqual(result['review_mode'],'tiered_memory')
        self.assertGreater(result['memory_counts']['long'],0)
        phases={r.payload.get('memory_mutation_review') for r in provider.requests}
        self.assertIn('record_updates',phases)
        self.assertTrue(any('candidate_items' in r.payload for r in provider.requests))
        state=self.read(self.root/'output/final_state.json');self.assertEqual(len(state['memory']['items']),4)
        manifest=self.read(self.root/'output/launch_manifest.json')
        self.assertEqual(manifest['source_relative'],'memory_runtime/src')
        self.assertIn('writing.py',manifest['writing_runtime_sha256']['memory_runtime'])

    def test_planner_writer_receive_committed_memory_and_stored_quotes_across_tiers(self):
        provider=Local();self.launch(provider)
        for role in ('planner','writer'):
            requests=[r for r in provider.requests if r.role==role]
            self.assertEqual(requests[1].payload['memory_coverage']['processed_through'],1)
            self.assertTrue(requests[1].payload['active_facts']);self.assertTrue(requests[1].payload['source_evidence'])
            self.assertTrue(any(r['tier']=='long' for r in requests[3].payload['active_facts']))
            self.assertTrue(all(s['chapter_number']<=3 for s in requests[3].payload['source_evidence']))

    def test_persistent_memory_failure_keeps_writing_and_reports_full_pending_queue(self):
        provider=Local(fail='memory');result=self.launch(provider)
        self.assertEqual(result['chapters'],4);self.assertTrue(result['draft_completed'])
        self.assertIsNone(result['stop_reason']);self.assertFalse(result['memory_complete'])
        self.assertEqual(result['pending_memory_chapters'],[1,2,3,4]);self.assertEqual(result['memory_processed_through'],0)
        self.assertEqual(sum(r.role=='writer' for r in provider.requests),4)
        self.assertEqual(result['memory_failure_count'],4)
        self.assertFalse(result['story_and_mechanical_checks_passed']);self.assertEqual(result['checked_draft_chapters'],0)
        second=next(r for r in provider.requests if r.role=='planner' and r.payload['chapter_number']==2)
        self.assertEqual(second.payload['memory_coverage']['pending_chapters'],[1])
        self.assertIn('Pending chapter changes',second.payload['fact_bank_status'])
        records=[self.read(p) for p in sorted((self.root/'output/working').glob('checkpoint_*.json'))]
        saved=next(r for r in records if r['reason']=='DRAFT_SAVED_MEMORY_PENDING')
        self.assertEqual(saved['book']['pending'],[1]);self.assertEqual(len(saved['book']['chapters']),1)
        self.assertEqual(saved['book']['memory']['items'],{})

    def test_resume_extracts_saved_chapter_before_next_planner_and_does_not_rewrite_it(self):
        failed=self.launch(Local(fail='memory'))
        provider=Local();result=self.launch(provider,'resumed',resume=failed['resume_checkpoint'])
        self.assertTrue(result['draft_completed']);self.assertEqual(result['chapters'],4)
        self.assertIn('memory_contract',provider.requests[0].payload)
        self.assertEqual([r for r in provider.requests if r.role=='planner'],[])
        old=self.read(self.root/'output/final_state.json')['chapters']
        self.assertEqual(self.read(self.root/'resumed/final_state.json')['chapters'],old)
        self.assertTrue(result['memory_complete'])

    def test_review_outage_resumes_review_without_reextracting_or_rewriting(self):
        failed=self.launch(Local(fail='review'),cfg=config(1));self.assertIsNone(failed['stop_reason'])
        self.assertTrue(failed['draft_completed']);self.assertEqual(failed['pending_story_review_chapters'],[1])
        self.assertTrue(failed['memory_complete'])
        provider=Local();result=self.launch(provider,'resumed',cfg=config(1),resume=failed['resume_checkpoint'])
        self.assertTrue(result['draft_completed']);self.assertEqual(len(provider.requests),1)
        self.assertEqual(provider.requests[0].payload['review_mode'],'light_memory')

    def test_persistent_review_outage_does_not_block_or_retry_before_next_prose(self):
        provider=Local(fail='review');result=self.launch(provider,cfg=config(3))
        self.assertTrue(result['draft_completed']);self.assertTrue(result['memory_complete'])
        self.assertIsNone(result['stop_reason']);self.assertEqual(result['pending_story_review_chapters'],[1,2,3])
        self.assertEqual(result['story_review_failure_count'],3)
        self.assertEqual(result['checked_draft_chapters'],0)
        self.assertFalse(result['story_and_mechanical_checks_passed'])
        requests=provider.requests
        failures=[i for i,r in enumerate(requests) if r.payload.get('review_mode')=='light_memory']
        self.assertEqual(len(failures),3)
        for first,second in zip(failures,failures[1:]):
            self.assertIn('writer',[r.role for r in requests[first+1:second]])
        state=self.read(self.root/'output/final_state.json')
        self.assertEqual(len(state['review_jobs']),3)
        self.assertTrue(all(r['stop_reason'] is None for r in state['outcomes']))

    def test_review_format_failure_preserves_jobs_and_keeps_writing(self):
        class BrokenReview(Local):
            def complete(self,request):
                if request.payload.get('review_mode')=='light_memory':
                    self.requests.append(copy.deepcopy(request));return ModelReply('{broken',1,1,0)
                return super().complete(request)
        result=self.launch(BrokenReview(),cfg=config(2))
        self.assertTrue(result['draft_completed']);self.assertEqual(result['pending_story_review_chapters'],[1,2])
        self.assertEqual(result['story_review_failure_count'],2)
        self.assertEqual(result['checked_draft_chapters'],0)

    def test_review_keyboard_interrupt_still_interrupts_and_preserves_pending_job(self):
        class InterruptReview(Local):
            def complete(self,request):
                if request.payload.get('review_mode')=='light_memory':raise KeyboardInterrupt()
                return super().complete(request)
        with self.assertRaises(KeyboardInterrupt):self.launch(InterruptReview(),cfg=config(1))
        result=self.read(self.root/'output/result.json')
        self.assertEqual(result['stop_reason'],'INTERRUPTED')
        self.assertEqual(result['pending_story_review_chapters'],[1])

    def test_unbound_time_failure_never_enters_memory_or_review(self):
        class BrokenTime(Local):
            def complete(self,request):
                if request.payload.get('time_binding_repair'):
                    self.requests.append(copy.deepcopy(request));return ModelReply(canonical(dict(unresolved='缺少起止时刻')),1,1,0)
                if request.role=='writer':
                    self.requests.append(copy.deepcopy(request));return ModelReply(canonical(dict(text='中间隔了两分钟。',continuity_updates=[],no_continuity_change_reason='无上述状态变化')),1,1,0)
                return super().complete(request)
        provider=BrokenTime();result=self.launch(provider,cfg=config(1))
        self.assertFalse(result['draft_completed']);self.assertEqual(result['chapters'],0)
        self.assertEqual(result['stop_reason'],'WRITING_TIME_CALCULATION_UNRESOLVED')
        self.assertFalse(any('memory_contract' in r.payload or r.payload.get('review_mode') for r in provider.requests))
        saved=self.read(Path(result['resume_checkpoint']))
        raw=[r for r in saved['trace'] if r['role']=='writer_time_calculation']
        self.assertEqual(raw[0]['raw_draft'],'中间隔了两分钟。')

    def test_calculator_supplies_writer_values_before_memory_and_review(self):
        class WithTime(Local):
            def complete(self,request):
                if request.role=='planner':
                    self.number=request.payload['chapter_number']
                    self.requests.append(copy.deepcopy(request))
                    return ModelReply(canonical(dict(number=self.number,title='传真',brief='核对发送和接收间隔',future_updates=[],
                        time_calculations=[dict(id='fax',kind='interval',start='16:41',end='16:45')])),1,1,0)
                if request.role=='writer':
                    self.requests.append(copy.deepcopy(request))
                    assert request.payload['computed_times'][0]['minutes']==4
                    return ModelReply(canonical(dict(text='传真[[time:fax.start]]发出，[[time:fax.end]]收到，相隔[[time:fax]]。',continuity_updates=[],no_continuity_change_reason='只计算本章发送接收间隔')),1,1,0)
                return super().complete(request)
        provider=WithTime();result=self.launch(provider,cfg=config(1))
        self.assertTrue(result['draft_completed']);self.assertEqual(result['time_calculation_count'],1)
        state=self.read(self.root/'output/final_state.json')
        self.assertEqual(state['chapters'][0]['text'],'传真16:41发出，16:45收到，相隔四分钟。')
        memory_request=next(r for r in provider.requests if 'memory_contract' in r.payload)
        self.assertIn('四分钟',canonical(memory_request.payload))
        self.assertNotIn('[[time:',canonical(memory_request.payload))

    def test_missing_advance_reference_is_rejected_before_writer(self):
        class BadPlan(Local):
            def complete(self,request):
                if request.role=='planner':
                    self.requests.append(copy.deepcopy(request))
                    return ModelReply(canonical(dict(number=1,title='开闸',brief='查时间',future_updates=[],
                        time_calculations=[dict(id='gate',kind='advance',start='21:07',end='21:11')])),1,1,0)
                return super().complete(request)
        provider=BadPlan();result=self.launch(provider,cfg=config(1))
        self.assertFalse(result['draft_completed']);self.assertEqual(result['chapters'],0)
        self.assertFalse(any(r.role=='writer' for r in provider.requests))

    def test_disabling_story_review_removes_its_calls_but_not_memory_or_writer_guards(self):
        cfg=dict(config(2),story_review_enabled=False);provider=Local(fail='review')
        result=self.launch(provider,cfg=cfg)
        self.assertTrue(result['draft_completed']);self.assertTrue(result['memory_complete'])
        self.assertFalse(result['story_review_enabled']);self.assertEqual(result['story_review_usage']['attempted_calls'],0)
        self.assertFalse(any(r.payload.get('review_mode')=='light_memory' for r in provider.requests))
        self.assertEqual(result['pending_story_review_chapters'],[])
        self.assertFalse(result['story_and_mechanical_checks_passed'])
        self.assertTrue(all(r['story_review_status']=='DISABLED' for r in result['outcomes']))

    def test_review_effectiveness_does_not_label_model_confirmation_as_true_finding(self):
        result=self.launch(Local(reject=True),cfg=config(1))
        usage=result['story_review_usage']
        self.assertEqual(usage['attempted_calls'],2)
        self.assertEqual(usage['successful_calls'],2)
        assessment=self.read(self.root/'output/审核效用评估.json')
        self.assertEqual(assessment['proposals'][0]['human_verdict'],'UNASSESSED')
        self.assertIsNone(assessment['validated_true_findings'])
        self.assertFalse(assessment['full_text_review_completed'])
        self.assertEqual(result['story_review_counts']['confirmed'],1)

    def test_writing_state_is_committed_with_prose_and_used_by_next_writer(self):
        class WithLedger(Local):
            def complete(self,request):
                if request.role=='writer':
                    self.requests.append(copy.deepcopy(request))
                    q='2024年4月1日，甲登记了来信。'
                    updates=[dict(type='event',id='first_letter',quote=q,date='2024-04-01',mode='present',objects=[],after=[])] if self.number==1 else []
                    return ModelReply(canonical(dict(text=q if self.number==1 else '甲接着整理来信。',
                        continuity_updates=updates,no_continuity_change_reason='同日接续一般动作，无关键状态变化')),1,1,0)
                return super().complete(request)
        provider=WithLedger();result=self.launch(provider,cfg=config(2))
        self.assertTrue(result['draft_completed'])
        second=[r for r in provider.requests if r.role=='writer'][1]
        self.assertEqual(second.payload['writing_state']['present_cursor']['date'],'2024-04-01')
        state=self.read(self.root/'output/final_state.json')
        self.assertEqual(state['writing_state']['events']['first_letter']['chapter'],1)

    def test_late_memory_phase_failure_keeps_prior_commit_and_resumes_pending_chapter(self):
        failed=self.launch(Local(fail='layers2'),cfg=config(3))
        self.assertEqual(failed['chapters'],3);self.assertEqual(failed['memory_processed_through'],1)
        self.assertEqual(failed['pending_memory_chapters'],[2,3]);self.assertTrue(failed['draft_completed'])
        state=self.read(self.root/'output/final_state.json')
        self.assertEqual(len(state['memory']['items']),1)
        self.assertEqual(state['memory']['items'][next(iter(state['memory']['items']))]['claim'],'甲的第1次记录已经完成。')
        provider=Local();result=self.launch(provider,'resumed',cfg=config(3),resume=failed['resume_checkpoint'])
        self.assertTrue(result['draft_completed']);self.assertEqual(result['memory_processed_through'],3)
        self.assertIn('memory_contract',provider.requests[0].payload)
        self.assertEqual([r for r in provider.requests if r.role=='planner'],[])

    def test_transient_memory_failure_catches_up_in_order_after_next_chapter(self):
        provider=Local(fail='memory_once');result=self.launch(provider,cfg=config(3))
        self.assertTrue(result['draft_completed']);self.assertTrue(result['memory_complete'])
        extraction=[r.payload['chapter_number'] for r in provider.requests if 'memory_contract' in r.payload]
        self.assertEqual(extraction,[1,1,2,3])
        roles=[r.role for r in provider.requests]
        # No immediate network retry: next planner/writer runs before catch-up.
        first=next(i for i,r in enumerate(provider.requests) if 'memory_contract' in r.payload)
        second=next(i for i,r in enumerate(provider.requests) if i>first and 'memory_contract' in r.payload)
        self.assertIn('writer',roles[first+1:second])
        self.assertEqual(result['checked_draft_chapters'],3)

    def test_editorial_rejection_keeps_committed_memory_for_next_chapter(self):
        provider=Local(reject=True);result=self.launch(provider,cfg=config(2))
        self.assertTrue(result['memory_complete']);self.assertEqual(result['pending_draft_chapters'],2)
        self.assertFalse(result['quality_gate_passed'])
        self.assertTrue([r for r in provider.requests if r.role=='planner'][1].payload['active_facts'])

    def test_failed_secondary_issue_review_keeps_uncertainty_visible_and_continues_prose(self):
        result=self.launch(Local(reject=True,fail='adjudication'),cfg=config(2))
        self.assertTrue(result['draft_completed']);self.assertTrue(result['memory_complete'])
        self.assertEqual(result['checked_draft_chapters'],0)
        self.assertEqual(result['story_review_counts'],dict(proposed=2,confirmed=0,unresolved=2,suggestions=0))
        self.assertTrue(all(r['unresolved_review_issues'] for r in result['outcomes']))
        self.assertIsNone(result['stop_reason'])

    def test_withheld_mutations_remain_explicit_without_false_quality_pass(self):
        result=self.launch(Local(withhold=True),cfg=config(1))
        self.assertTrue(result['memory_complete']);self.assertEqual(result['withheld_mutations'],1)
        self.assertEqual(result['checked_draft_chapters'],0);self.assertEqual(result['active_facts'],0)

    def test_resume_mismatch_rejected_before_credentials_or_network(self):
        result=self.launch(Local(),cfg=config(1));path=Path(result['resume_checkpoint'])
        altered=config(1);altered['goal']='另一部小说'
        with patch.object(cli,'read_secret',side_effect=AssertionError('Must not read key')),self.assertRaises(ContractError):
            cli.launch(altered,self.root/'bad',resume=path)
        self.assertFalse((self.root/'bad').exists())
        record=self.read(path);record['runtime_sha256']['entrypoints']['write_novel.py']='wrong'
        corrupt=self.root/'changed-runtime.json';corrupt.write_text(json.dumps(record),encoding='utf-8')
        with self.assertRaises(ContractError):load_resume(corrupt,cli.validate_config(config(1)))

    def test_interrupt_keeps_resumable_prose_and_pending_memory(self):
        with self.assertRaises(KeyboardInterrupt):self.launch(Local(fail='interrupt'),cfg=config(1))
        result=self.read(self.root/'output/result.json')
        self.assertEqual(result['stop_reason'],'INTERRUPTED');self.assertEqual(result['pending_memory_chapters'],[1])
        restored=self.launch(Local(),'resumed',cfg=config(1),resume=result['resume_checkpoint'])
        self.assertTrue(restored['draft_completed'])

    def test_dry_run_has_no_key_or_network_and_creates_no_output(self):
        with patch.object(cli,'read_secret',side_effect=AssertionError('No key')),contextlib.redirect_stdout(io.StringIO()):
            self.assertIsNone(cli.launch(config(),self.root/'dry',execute=False))
        self.assertFalse((self.root/'dry').exists())


if __name__=='__main__':unittest.main(verbosity=2)
