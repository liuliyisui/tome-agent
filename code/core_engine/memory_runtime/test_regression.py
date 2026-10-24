"""Local, credential-free regression suite, including archived real failures."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'memory_runtime/src'))
from memory_runtime import pipeline
sys.modules['components']=pipeline
spec=importlib.util.spec_from_file_location('archived_regression',ROOT/'tools/continuous_memory_20261021_i/test_run.py')
fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)
class ContinuousTests(fixtures.ContinuousTests):
    def test_empty_start_full_prefix_chain_and_real_interface_shapes(self):
        import tempfile,contextlib,io,json
        gateway=fixtures.FixtureGateway()
        with tempfile.TemporaryDirectory() as directory,contextlib.redirect_stdout(io.StringIO()):
            output=Path(directory);result=fixtures.module.execute(output,gateway,fixtures.chapters())
            self.assertEqual(result['completed_through'],12)
            self.assertEqual(len(result['probes']),4)
            self.assertEqual(len(gateway.requests),43)
            self.assertEqual(json.loads((output/'initial_memory.json').read_text(encoding='utf-8'))['items'],{})
            self.assertTrue(result['recent_to_long_observed'])
            self.assertGreater(result['cited_long_term_in_recall'],0)
            for number in range(1,13):
                scope=json.loads((output/f'chapter_{number:03d}/input_scope.json').read_text(encoding='utf-8'))
                self.assertEqual(scope['source_chapter_numbers'],list(range(1,number+1)))
                self.assertFalse(scope['future_chapters_supplied'])

    def test_recall_gets_memory_only_and_cites_long_term(self):
        import tempfile,contextlib,io
        gateway=fixtures.FixtureGateway()
        with tempfile.TemporaryDirectory() as directory,contextlib.redirect_stdout(io.StringIO()):
            result=fixtures.module.execute(Path(directory),gateway,fixtures.chapters())
        payload=gateway.last_probe
        self.assertEqual(set(payload),{'question','current_memory','historical_memory','source_evidence','scope','draft_answer'})
        self.assertNotIn('current_draft',payload);self.assertNotIn('expected_answer',payload)
        self.assertTrue(any(p['cited_long_term']>0 for p in result['probes']))
    def test_completed_task_can_reference_prior_current_evidence_but_supersession_cannot(self):
        from inf_writer.temporal_agent import TemporalReconciler
        from inf_writer.tiered_memory import apply_delta,select_context
        before=fixtures.module.read(fixtures.BASELINE/'checkpoint_005.json')['memory']
        prose=fixtures.module.read(fixtures.module.PARENT/'final_state.json')['chapters'][:6]
        old_trace=fixtures.module.read(fixtures.BASELINE/'chapter_006/trace.json')
        candidate=apply_delta(before,__import__('json').loads(old_trace[0]['raw_output']),prose,'chapter-memory-6')
        selection=select_context(before,query=prose[-1]['text'],max_bytes=48000)
        value=__import__('json').loads(fixtures.module.read(ROOT/'runs/continuous_memory_real_20261021_d/call_001.response.json')['content'])
        target=old_trace[-1]['wire_bindings']['items'][value['changes'][1]['id']]
        class Saved:
            def complete(self,request):return ModelReply(canonical(value),0,0,0)
        for kind in ('task','knowledge','event','state','legacy'):
            before['items'][target]['kind']=candidate['items'][target]['kind']=kind
            result=TemporalReconciler(Saved()).run(before,candidate,prose,6,selection,[])
            self.assertEqual(result['items'][target]['kind'],kind)
            self.assertEqual(result['items'][target]['claim'],candidate['items'][target]['claim'])
            if kind!='task':self.assertEqual(result['items'][target]['status'],candidate['items'][target]['status'])
        value['changes'][1]['resolutions'][0]['relation']='superseded'
        with self.assertRaises(ContractError):TemporalReconciler(Saved()).run(before,candidate,prose,6,selection,[])

    def test_repair_then_unresolved_review_replays_without_transport_repair_metadata(self):
        from inf_writer.tiered_memory import apply_delta,select_context
        parent=ROOT/'runs/continuous_memory_real_20261021_h'
        before=fixtures.module.read(parent/'checkpoint_010.json')['memory']
        prose=fixtures.module.read(fixtures.module.PARENT/'final_state.json')['chapters'][:11]
        raw=fixtures.module.read(parent/'chapter_011/trace.json')[0]['raw_output']
        candidate=apply_delta(before,__import__('json').loads(raw),prose,'chapter-memory-11')
        class Saved:
            def complete(self,request):
                index=11 if 'issues' in request.payload else 10 if 'repair' in request.payload else 9
                return ModelReply(**fixtures.module.read(parent/f'call_{index:03d}.response.json'))
        result=pipeline.ReviewedTemporal(Saved()).run(before,candidate,prose,11,
            select_context(before,query=prose[-1]['text'],max_bytes=48000),[])
        self.assertEqual(result['temporal_processed_through'],11)
from inf_writer.domain import canonical,ContractError
from inf_writer.models import ModelReply,ModelRequest
from inf_writer.temporal_agent import SYSTEM
from inf_writer.tiered_runtime import MEMORY_SYSTEM
from memory_runtime.engine import MemoryEngine

_fixture_complete=fixtures.FixtureGateway.complete
def fixture_complete_with_evidence_gate(self,request):
    if 'memory_mutation_review' in request.payload:
        import copy
        self.requests.append(copy.deepcopy(request))
        return ModelReply(canonical(dict(decisions=[dict(ref=p['ref'],decision='accept',reason='离线夹具明确定义的事实')
            for p in request.payload['proposals']])),0,0,0)
    return _fixture_complete(self,request)
fixtures.FixtureGateway.complete=fixture_complete_with_evidence_gate


class StructuralRegression(unittest.TestCase):
    def test_recall_format_repair_is_shared_and_bounded(self):
        import json
        memory=fixtures.module.read(ROOT/'runs/continuous_memory_stable_20261021_h/checkpoint_012.json')['memory']
        malformed=fixtures.module.read(ROOT/'runs/recall_verified_real_20261021_b/call_007.response.json')['content']
        valid=json.loads(malformed);valid.pop('source_evidence');requests=[]
        class Gateway:
            def complete(self,request):
                requests.append(request)
                return ModelReply(malformed if len(requests) in (1,3) else canonical(valid),0,0,0)
        trace=[]
        with self.assertRaises(ContractError):pipeline.recall_probe(memory,fixtures.module.PROBES[12],Gateway(),trace,'bounded-format')
        self.assertEqual(len(requests),3)
        self.assertIn('repair',requests[1].payload)
        self.assertNotIn('repair',requests[2].payload)

    def test_recall_actual_extra_evidence_field_repairs_without_accepting_it_as_fact(self):
        import json
        memory=fixtures.module.read(ROOT/'runs/continuous_memory_stable_20261021_h/checkpoint_012.json')['memory']
        malformed=fixtures.module.read(ROOT/'runs/recall_verified_real_20261021_b/call_007.response.json')['content']
        valid=json.loads(malformed);valid.pop('source_evidence');requests=[]
        class Gateway:
            def complete(self,request):
                requests.append(request)
                return ModelReply(malformed if len(requests)==1 else canonical(valid),0,0,0)
        trace=[];result=pipeline.recall_probe(memory,fixtures.module.PROBES[12],Gateway(),trace,'repair-actual-extra')
        self.assertEqual(len(requests),3);self.assertEqual(result['answer'],valid['answer'])
        self.assertEqual(trace[0]['status'],'FORMAT_REJECTED')
        self.assertNotIn('repair',requests[-1].payload)

    def test_separate_historical_references_merge_only_valid_history_aliases(self):
        bindings={'q001':dict(view='current'),'h001':dict(view='historical')}
        body=dict(answer='有证据的回答',memory_ids=['q001'],historical_memory_ids=['h001'])
        parsed,notes=pipeline.parse_recall_answer(canonical(body),bindings)
        self.assertEqual(parsed['memory_ids'],['q001','h001']);self.assertTrue(notes)
        for bad in (['q001'],['h999'],'h001'):
            body['historical_memory_ids']=bad
            with self.assertRaises(ContractError):pipeline.parse_recall_answer(canonical(body),bindings)

    def test_recall_surfaces_stored_source_action_omitted_by_summary(self):
        parent=ROOT/'runs/continuous_memory_stable_20261021_h'
        checkpoint=fixtures.module.read(parent/'checkpoint_012.json')
        query=fixtures.module.PROBES[12];memory=checkpoint['memory']
        selection=pipeline.recall_selection(memory,query)
        bindings={f'q{n:03d}':dict(memory_id=r['id'],view='current',tier=r['tier']) for n,r in enumerate(selection['items'],1)}
        evidence=pipeline.source_evidence_view(memory,selection['selected_ids'],bindings,query)
        self.assertTrue(any('梁策低头看完' in row['quote'] for row in evidence['items']))
        self.assertLessEqual(evidence['bytes'],24000)
        self.assertTrue(all(row['chapter_number']<=12 for row in evidence['items']))
        self.assertTrue(all(row['memory_id'] in bindings for row in evidence['items']))

    def test_recall_returns_reviewed_answer_and_preserves_actual_failed_draft(self):
        import json
        parent=ROOT/'runs/continuous_memory_stable_20261021_h'
        memory=fixtures.module.read(parent/'checkpoint_003.json')['memory']
        old=next(t for t in fixtures.module.read(parent/'chapter_003/trace.json') if t['role']=='recall')
        draft,_=pipeline.normalize(json.loads(old['raw_output']))
        requests=[]
        class Gateway:
            def complete(self,request):
                requests.append(request)
                if 'draft_answer' not in request.payload:return ModelReply(old['raw_output'],0,0,0)
                return ModelReply(canonical(dict(answer='笔记主人是梁策父亲，已去世。',memory_ids=draft['memory_ids'])),0,0,0)
        trace=[];result=pipeline.recall_probe(memory,fixtures.module.PROBES[3],Gateway(),trace,'saved-failed-answer')
        self.assertEqual(len(requests),2)
        self.assertEqual(requests[1].payload['draft_answer'],draft)
        self.assertEqual(trace[0]['raw_output'],old['raw_output'])
        self.assertNotEqual(result['answer'],draft['answer'])
        self.assertTrue(result['consistency_reviewed'])
    def test_status_domain_matrix_and_incomplete_task_aliases(self):
        for kind in ('state','event','knowledge','legacy','task'):
            for status in ('active','superseded','planned','completed','cancelled','pending','ongoing','in_progress','unknown'):
                op=dict(status=status);notes=[];pipeline.container_status(op,kind,notes)
                expected=('planned' if kind=='task' and status in ('active','pending','ongoing','in_progress')
                    else 'active' if kind!='task' and status in ('planned','completed','cancelled') else status)
                self.assertEqual(op['status'],expected)
                if status in ('completed','cancelled') and kind=='task':self.assertEqual(op['status'],status)
        self.assertEqual(pipeline.container_status(dict(status='active'),'unknown',[]),None)

    def test_saved_chapter_two_active_task_has_a_valid_unfinished_status(self):
        import json
        from inf_writer.tiered_memory import apply_delta,extraction_payload,select_context
        parent=ROOT/'runs/continuous_memory_stable_20261021_g'
        before=fixtures.module.read(parent/'checkpoint_001.json')['memory']
        prose=fixtures.module.read(fixtures.module.PARENT/'final_state.json')['chapters'][:2]
        payload=extraction_payload(before,prose,2,select_context(before,query=prose[-1]['text'],max_bytes=48000))
        class Gateway:
            def complete(self,request):return ModelReply(**fixtures.module.read(parent/'call_004.response.json'))
        adapter=pipeline.ExtractionAdapter(Gateway());adapter.full_memory=before
        delta=json.loads(adapter.complete(ModelRequest('memory',MEMORY_SYSTEM,payload,8192)).content)
        result=apply_delta(before,delta,prose,'chapter-memory-2')
        self.assertGreater(len(result['items']),len(before['items']))
        self.assertTrue(any(n['rule']=='container_status_domain' for n in adapter.transforms[-1]['normalizations']))
    def test_kind_is_program_owned_and_task_status_does_not_reclassify_container(self):
        import json
        from inf_writer.tiered_memory import empty_memory,apply_delta,wire_item
        prose=[dict(number=1,title='问题',text='许闻已写出三个待问问题。')]
        before=apply_delta(empty_memory(),dict(changes=[dict(op='add',subject='许闻',attribute='questions',claim='拟写待问问题',kind='knowledge',status='active',source_refs=[dict(chapter_number=1,evidence_id='e0001')])]),prose,'seed')
        old=next(iter(before['items'].values()))
        class Gateway:
            def complete(self,request):return ModelReply(canonical(dict(changes=[dict(op='update',id='m001',expected_revision=1,kind='task',status='completed',claim='许闻已写出三个待问问题',reason='写问题完成',source_refs=[dict(chapter_number=1,evidence_id='e0001')])])),0,0,0)
        adapter=pipeline.ExtractionAdapter(Gateway());adapter.full_memory=before
        payload=dict(memory_items=[wire_item(old)],memory_contract={})
        parsed=json.loads(adapter.complete(ModelRequest('memory',MEMORY_SYSTEM,payload,200)).content)
        after=apply_delta(before,parsed,prose,'update')
        self.assertEqual(after['items'][old['id']]['kind'],'knowledge')
        self.assertEqual(after['items'][old['id']]['status'],'active')
        self.assertEqual(after['items'][old['id']]['claim'],'许闻已写出三个待问问题')
        self.assertTrue(any(n['rule']=='program_owned_kind' for n in adapter.transforms[0]['normalizations']))

    def test_existing_current_state_is_resolved_from_exact_full_store_identity(self):
        import json
        from inf_writer.tiered_memory import empty_memory,apply_delta
        prose=[dict(number=1,title='位置',text='卷宗从柜中移到桌面。')]
        add=dict(op='add',subject='卷宗',attribute='location',claim='卷宗在柜中',kind='state',status='active',source_refs=[dict(chapter_number=1,evidence_id='e0001')])
        before=apply_delta(empty_memory(),dict(changes=[add]),prose,'seed');old=next(iter(before['items'].values()))
        class Gateway:
            def complete(self,request):return ModelReply(canonical(dict(changes=[dict(add,claim='卷宗在桌面')])),0,0,0)
        adapter=pipeline.ExtractionAdapter(Gateway());adapter.full_memory=before
        reply=adapter.complete(ModelRequest('memory',MEMORY_SYSTEM,dict(memory_items=[],memory_contract={}),200))
        delta=json.loads(reply.content)
        self.assertEqual(delta['changes'][0]['op'],'update')
        self.assertEqual(delta['changes'][0]['id'],old['id'])
        after=apply_delta(before,delta,prose,'next')
        self.assertEqual(len(after['items']),1)
        self.assertEqual(after['items'][old['id']]['claim'],'卷宗在桌面')

    def test_saved_chapter_eight_readonly_kind_cannot_reject_valid_content(self):
        import json
        from inf_writer.tiered_memory import apply_delta,extraction_payload,select_context
        parent=ROOT/'runs/continuous_memory_stable_20261021_f'
        before=fixtures.module.read(parent/'checkpoint_007.json')['memory']
        prose=fixtures.module.read(fixtures.module.PARENT/'final_state.json')['chapters'][:8]
        payload=extraction_payload(before,prose,8,select_context(before,query=prose[-1]['text'],max_bytes=48000))
        class Gateway:
            def complete(self,request):return ModelReply(**fixtures.module.read(parent/'call_030.response.json'))
        adapter=pipeline.ExtractionAdapter(Gateway());adapter.full_memory=before
        result=json.loads(adapter.complete(ModelRequest('memory',MEMORY_SYSTEM,payload,8192)).content)
        after=apply_delta(before,result,prose,'chapter-memory-8')
        for identifier,row in before['items'].items():self.assertEqual(after['items'][identifier]['kind'],row['kind'])
        self.assertGreater(len(after['items']),len(before['items']))

    def test_exact_noops_and_duplicate_adds_are_idempotent_with_other_changes(self):
        from inf_writer.tiered_memory import empty_memory,apply_delta
        prose=[dict(number=1,title='记录',text='甲守着旧卷。乙拿来新卷。')]
        add=dict(op='add',subject='甲',attribute='role',claim='甲守着旧卷',kind='knowledge',status='active',source_refs=[dict(chapter_number=1,evidence_id='e0001')])
        before=apply_delta(empty_memory(),dict(changes=[add]),prose,'seed');identifier=next(iter(before['items']))
        noop=dict(op='update',id=identifier,expected_revision=1,reason='再次确认',claim=add['claim'],kind='knowledge',status='active',source_refs=add['source_refs'])
        other=dict(add,subject='乙',claim='乙拿来新卷')
        delta=dict(changes=[noop,dict(add),other])
        after=apply_delta(before,delta,prose,'next')
        self.assertEqual(after['items'][identifier],before['items'][identifier])
        self.assertEqual(len(after['items']),2)
        self.assertEqual(len(after['no_change_observations']),2)
        self.assertEqual(apply_delta(after,delta,prose,'next'),after)

    def test_noop_still_rejects_invalid_source_stale_revision_and_reclassification(self):
        import copy
        from inf_writer.tiered_memory import empty_memory,apply_delta
        prose=[dict(number=1,title='记录',text='旧卷在柜中。')]
        before=apply_delta(empty_memory(),dict(changes=[dict(op='add',subject='旧卷',attribute='location',claim='旧卷在柜中',kind='state',status='active',source_refs=[dict(chapter_number=1,evidence_id='e0001')])]),prose,'seed')
        identifier=next(iter(before['items']));original=canonical(before)
        op=dict(op='update',id=identifier,expected_revision=1,reason='重复',claim='旧卷在柜中',status='active',source_refs=[dict(chapter_number=1,evidence_id='e0001')])
        for replacement in [dict(source_refs=[dict(chapter_number=1,evidence_id='missing')]),dict(expected_revision=9),dict(kind='event'),dict(unexpected=True)]:
            with self.assertRaises(ContractError):apply_delta(before,dict(changes=[dict(op,**replacement)]),prose,'bad')
        self.assertEqual(canonical(before),original)

    def test_saved_chapter_five_noop_does_not_reject_valid_batch(self):
        import json
        from inf_writer.tiered_memory import apply_delta
        parent=ROOT/'runs/continuous_memory_stable_20261021_e'
        before=fixtures.module.read(parent/'checkpoint_004.json')['memory']
        prose=fixtures.module.read(fixtures.module.PARENT/'final_state.json')['chapters'][:5]
        trace=fixtures.module.read(parent/'chapter_005/trace.json')
        self.assertIn('NO_MEMORY_CHANGE',trace[-1]['error'])
        candidate=apply_delta(before,json.loads(trace[-1]['raw_output']),prose,'chapter-memory-5')
        self.assertTrue(candidate['no_change_observations'])
        self.assertGreater(len(candidate['items']),len(before['items']))

    def test_unproven_cancellation_is_withheld_and_prior_task_preserved(self):
        import json
        from inf_writer.tiered_memory import apply_delta
        from memory_runtime.semantics import guard_extraction
        parent=ROOT/'runs/continuous_memory_stable_20261021_d'
        before=fixtures.module.read(parent/'checkpoint_002.json')['memory']
        prose=fixtures.module.read(fixtures.module.PARENT/'final_state.json')['chapters'][:3]
        entry=next(t for t in fixtures.module.read(parent/'chapter_003/trace.json') if t['role']=='memory' and t.get('status')=='ACCEPTED')
        candidate=apply_delta(before,json.loads(entry['raw_output']),prose,'chapter-memory-3');candidate['processed_through']=3
        cancelled=[op for op in json.loads(entry['raw_output'])['changes'] if op.get('status')=='cancelled']
        self.assertTrue(cancelled)
        class Keep:
            def complete(self,request):
                return ModelReply(canonical(dict(decisions=[dict(ref=p['ref'],decision='keep_current' if p['proposed_change'].get('status')=='cancelled' else 'accept',reason='取消无依据，其它夹具变更明确')
                    for p in request.payload['proposals']])),0,0,0)
        trace=[dict(entry)]
        result=guard_extraction(before,candidate,prose,3,Keep(),trace)
        for op in cancelled:self.assertEqual(result['items'][op['id']],before['items'][op['id']])
        self.assertTrue(set(candidate['items'])-set(before['items']))
        self.assertTrue((set(candidate['items'])-set(before['items']))<=set(result['items']))
        self.assertTrue(result['withheld_memory_mutations'])
        self.assertEqual(trace[-1]['status'],'ACCEPTED')
        self.assertIn('withheld',trace[-1])

    def test_unproven_expiry_preserves_old_portions_while_other_changes_survive(self):
        from inf_writer.tiered_memory import empty_memory,apply_delta
        from inf_writer.memory_temporality import annotated
        from memory_runtime.semantics import guard_temporal
        import copy
        prose=[dict(number=1,title='计划',text='计划查甲，计划查乙。'),dict(number=2,title='新焦点',text='先查丙，已经查过乙。')]
        before=apply_delta(empty_memory(),dict(changes=[dict(op='add',subject='甲',attribute='plan',claim='计划查甲，计划查乙',
            kind='knowledge',status='active',source_refs=[dict(chapter_number=1,evidence_id='e0001')]),
            dict(op='add',subject='丙',attribute='new_focus',claim='先查丙，已经查过乙',kind='knowledge',status='active',source_refs=[dict(chapter_number=2,evidence_id='e0001')])]),prose,'seed')
        old=next(r for r in before['items'].values() if r['subject']=='甲');new=next(r for r in before['items'].values() if r['subject']=='丙')
        part=annotated(old)['temporality']['parts'][0]
        op=dict(op='reconcile',id=old['id'],expected_revision=old['revision'],reason='误将新焦点当旧计划失效',as_of_chapter=2,
            resolutions=[dict(part_ids=[part['id']],replacement_ids=[new['id']],relation='superseded',source_refs=[dict(chapter_number=2,evidence_id='e0001')],reason='错误提案')])
        second=annotated(old)['temporality']['parts'][1]
        op['resolutions'].append(dict(part_ids=[second['id']],replacement_ids=[new['id']],relation='completed',source_refs=[dict(chapter_number=2,evidence_id='e0001')],reason='乙确实已查'))
        candidate=apply_delta(before,dict(changes=[op]),prose,'chapter-time-2')
        trace=[dict(role='temporal',status='ACCEPTED',raw_output=canonical(dict(checked_ids=[old['id']],changes=[op])),
            wire_bindings=dict(items={'r001':old['id'],'r002':new['id']},parts={'s001':part['id'],'s002':second['id']}))]
        class Keep:
            def complete(self,request):return ModelReply(canonical(dict(decisions=[dict(ref='t001',decision='keep_current',reason='先查丙未取消查甲'),dict(ref='t002',decision='accept',reason='明确已查乙')])),0,0,0)
        result=guard_temporal(before,candidate,prose,2,Keep(),trace)
        actual={p['id']:p for p in annotated(result['items'][old['id']])['temporality']['parts']}
        self.assertEqual(actual[part['id']],part)
        self.assertEqual(actual[second['id']]['scope'],'historical')
        self.assertEqual(result['items'][new['id']],before['items'][new['id']])
        self.assertTrue(result['withheld_memory_mutations'])

    def test_malformed_previous_json_does_not_break_the_repair_path(self):
        import json
        payload=fixtures.module.read(ROOT/'runs/continuous_memory_stable_20261021_c/call_042.request.json')['payload']
        payload['repair']=dict(previous_output='{broken json',error='Invalid JSON',instruction='修复')
        called=[]
        class Gateway:
            def complete(self,request):
                called.append(request)
                return ModelReply(canonical(dict(checked_batch_token=request.payload['batch_acknowledgement']['token'],
                    changes=[],no_change_reason='夹具不变')),0,0,0)
        reply=pipeline.ExtractionAdapter(Gateway()).complete(ModelRequest('memory',SYSTEM,payload,200))
        self.assertEqual(len(called),1)
        self.assertEqual(json.loads(reply.content)['checked_ids'],[r['id'] for r in payload['candidate_items']])

    def test_batch_scope_maps_only_candidates_and_rejects_wrong_or_conflicting_ack(self):
        import copy,json
        parent=ROOT/'runs/continuous_memory_stable_20261021_c'
        payload=fixtures.module.read(parent/'call_042.request.json')['payload']
        expected=[r['id'] for r in payload['candidate_items']]
        self.assertTrue(payload['changed_items'])
        class Gateway:
            mode='valid'
            def complete(self,request):
                token=request.payload['batch_acknowledgement']['token']
                value=dict(checked_batch_token=token if self.mode!='wrong' else 'wrong',changes=[],no_change_reason='夹具不变')
                if self.mode=='conflict':value['checked_ids']=[r['id'] for r in payload['changed_items']]
                return ModelReply(canonical(value),0,0,0)
        gateway=Gateway();adapter=pipeline.ExtractionAdapter(gateway)
        request=ModelRequest('memory',SYSTEM,payload,200)
        result=json.loads(adapter.complete(request).content)
        self.assertEqual(result['checked_ids'],expected)
        self.assertNotIn('checked_batch_token',result)
        self.assertFalse(adapter.transforms[-1]['semantic_certification'])
        for mode in ('wrong','conflict'):
            gateway.mode=mode;invalid=json.loads(adapter.complete(request).content)
            self.assertIn('checked_batch_token',invalid)  # No valid core reply is manufactured.

    def test_disjoint_parts_of_same_record_can_be_reconciled_and_retained(self):
        import json,copy
        from inf_writer.tiered_memory import apply_delta,select_context
        from inf_writer.memory_temporality import annotated
        parent=ROOT/'runs/continuous_memory_stable_20261021_b'
        before=fixtures.module.read(parent/'checkpoint_002.json')['memory']
        prose=fixtures.module.read(fixtures.module.PARENT/'final_state.json')['chapters'][:3]
        trace_old=fixtures.module.read(parent/'chapter_003/trace.json')
        candidate=apply_delta(before,json.loads(trace_old[0]['raw_output']),prose,'chapter-memory-3');candidate['processed_through']=3
        temporal=json.loads(fixtures.module.read(parent/'call_008.response.json')['content'])
        review=fixtures.module.read(parent/'call_009.response.json')
        class Saved:
            def complete(self,request):
                return ModelReply(**review) if 'issues' in request.payload else ModelReply(canonical(temporal),0,0,0)
        selected=select_context(before,query=prose[-1]['text'],max_bytes=48000)
        result=pipeline.ReviewedTemporal(Saved()).run(before,candidate,prose,3,selected,[])
        self.assertEqual(result['temporal_processed_through'],3)
        issue=next(t for t in trace_old if t.get('issues'))['issues'][0]
        old={p['id']:p for p in annotated(candidate['items'][issue['id']])['temporality']['parts']}
        new={p['id']:p for p in annotated(result['items'][issue['id']])['temporality']['parts']}
        for pid in issue['part_ids']:self.assertEqual(new[pid],old[pid])
        # Protecting one portion must not permit an overlapping change.
        unresolved=temporal['unresolved'][0]
        operation=next(op for op in temporal['changes'] if op['id']==unresolved['id'])
        operation['resolutions'][0]['part_ids'].append(unresolved['part_ids'][0])
        original=canonical(candidate)
        with self.assertRaises(ContractError):pipeline.ReviewedTemporal(Saved()).run(before,candidate,prose,3,selected,[])
        self.assertEqual(canonical(candidate),original)

    def test_checkpoint_is_atomic_and_never_overwrites_previous_commit(self):
        import tempfile
        import check_memory
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'checkpoint.json'
            check_memory.save_new(target,dict(committed=7))
            with self.assertRaises(FileExistsError):check_memory.save_new(target,dict(committed=8))
            self.assertEqual(check_memory.read(target),dict(committed=7))
            self.assertFalse(list(Path(directory).glob('.memory-pending-*')))
    def test_new_uncertainty_discovered_by_repair_is_reviewed_without_resetting_budget(self):
        from inf_writer.tiered_memory import empty_memory,apply_delta,select_context
        import copy
        prose=[dict(number=1,title='计划',text='计划看盘，计划见人。'),dict(number=2,title='未定',text='今天没有新结论。')]
        before=apply_delta(empty_memory(),dict(changes=[dict(op='add',subject='甲',attribute='plans',claim='计划看盘，计划见人',
            kind='knowledge',status='active',source_refs=[dict(chapter_number=1,evidence_id='e0001')]),
            dict(op='add',subject='乙',attribute='plans',claim='计划取档，计划核对',kind='knowledge',status='active',source_refs=[dict(chapter_number=1,evidence_id='e0001')])]),prose,'seed')
        after=copy.deepcopy(before)
        class Gateway:
            def __init__(self,broken_second=False):self.repairs=0;self.reviews=0;self.broken_second=broken_second
            def complete(self,request):
                p=request.payload
                if 'issues' in p:
                    self.reviews+=1
                    return ModelReply(canonical(dict(decisions=[dict(ref=i['ref'],decision='keep_unconfirmed',reason='没有完成依据') for i in p['issues']])),0,0,0)
                item=p['candidate_items'][int('repair' in p)];parts=item['temporality']['current_parts']
                target=p['candidate_items'][int('repair' not in p)]
                broken=dict(op='reconcile',id=target['id'],expected_revision='bad',reason='夹具格式错误',as_of_chapter=2,resolutions=[])
                if 'repair' in p:self.repairs+=1
                repaired='repair' in p
                return ModelReply(canonical(dict(checked_ids=[r['id'] for r in p['candidate_items']],changes=[broken] if not repaired or self.broken_second else [],
                    no_change_reason='保留',unresolved=[dict(id=item['id'],part_ids=[parts[int(repaired)]['id']],reason='旧计划未证实完成') ])),0,0,0)
        selected=select_context(before,query='计划')
        good=Gateway();result=pipeline.ReviewedTemporal(good).run(before,after,prose,2,selected,[])
        self.assertEqual(good.repairs,1);self.assertEqual(good.reviews,2)
        self.assertEqual(result['items'],after['items'])
        bad=Gateway(True)
        with self.assertRaises(ContractError):pipeline.ReviewedTemporal(bad).run(before,after,prose,2,selected,[])
        self.assertEqual(bad.repairs,1)
    def test_arbitrary_attribute_labels_have_stable_distinct_valid_identifiers(self):
        import re
        labels=['1998_incoming_entry','中文属性','A field with spaces','x'*200]
        result=[pipeline.attribute_identifier(label) for label in labels]
        self.assertEqual(len(set(result)),len(labels))
        for label,identifier in zip(labels,result):
            self.assertRegex(identifier,r'^[a-z][a-z0-9_]{0,63}$')
            self.assertEqual(identifier,pipeline.attribute_identifier(label))
        self.assertEqual(pipeline.attribute_identifier('valid_field'),'valid_field')
        self.assertIsNone(pipeline.attribute_identifier(None))

    def test_public_engine_runs_empty_start_twelve_chapters_with_no_future_input(self):
        gateway=fixtures.FixtureGateway();engine=MemoryEngine(gateway);memory=engine.empty()
        for number in range(1,13):
            memory,report=engine.advance(memory,fixtures.chapters(),number,[])
            self.assertEqual(memory['processed_through'],number)
            self.assertEqual(memory['temporal_processed_through'],number)
        self.assertTrue(any(row['tier']=='long' for row in memory['items'].values()))
        for request in gateway.requests:
            if 'chapter_number' in request.payload:
                self.assertNotIn('expected_answer',request.payload)

    def test_numeric_attribute_is_normalized_without_changing_claim_or_source(self):
        class Gateway:
            def complete(self,request):
                return ModelReply(canonical(dict(changes=[dict(op='add',attribute='1998_incoming_entry',claim='原句',source_refs=[])])),0,0,0)
        adapter=pipeline.ExtractionAdapter(Gateway())
        reply=adapter.complete(ModelRequest('memory',MEMORY_SYSTEM,dict(memory_items=[],memory_contract={}),200))
        import json
        op=json.loads(reply.content)['changes'][0]
        self.assertEqual(op['attribute'],'field_1998_incoming_entry')
        self.assertEqual(op['claim'],'原句');self.assertEqual(op['source_refs'],[])
        self.assertTrue(adapter.transforms[0]['normalizations'])

    def test_repair_reports_all_invalid_targets_and_relations_together(self):
        captured=[]
        class Gateway:
            def complete(self,request):captured.append(request);return ModelReply('{}',0,0,0)
        bad=dict(changes=[dict(id='r999',resolutions=[]),dict(id='r001',resolutions=[dict(relation='completed',replacement_ids=[])])])
        payload=dict(candidate_items=[dict(id='r001',kind='event')],changed_items=[dict(id='r999')],
            repair=dict(previous_output=canonical(bad),instruction='修复'))
        pipeline.ExtractionAdapter(Gateway()).complete(ModelRequest('memory',SYSTEM,payload,200))
        errors=captured[0].payload['repair']['all_detected_contract_errors']
        self.assertEqual(len(errors),2)
        self.assertTrue(any('r999' in e and 'candidate_items' in e for e in errors))
        self.assertTrue(any('replacement_ids' in e for e in errors))

    def test_advance_rejects_skipped_chapter_before_any_call(self):
        class NoCalls:
            def complete(self,request):raise AssertionError('No request expected')
        with self.assertRaises(ContractError):MemoryEngine(NoCalls()).advance(MemoryEngine.empty(),[],2,[])

    def test_engine_failure_keeps_input_byte_for_byte(self):
        class Bad(fixtures.FixtureGateway):
            def complete(self,request):
                if 'completed_chapter' in request.payload:return ModelReply('{"placements":[]}',0,0,0)
                return super().complete(request)
        memory=MemoryEngine.empty();original=canonical(memory)
        with self.assertRaises(ContractError):MemoryEngine(Bad()).advance(memory,fixtures.chapters(),1,[])
        self.assertEqual(canonical(memory),original)


if __name__=='__main__':unittest.main(verbosity=2)
