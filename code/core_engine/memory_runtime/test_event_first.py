"""Event-first source-of-truth integration, using the real launcher offline."""
import copy
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import write_novel as cli
from inf_writer.domain import ContractError,canonical,digest
from inf_writer.models import ModelReply
from memory_runtime.continuity import empty
from memory_runtime.event_first import prepare,realize,project_memory
from memory_runtime.test_writing import Local,config


def fact(value='门外',kind='state'):
    return dict(type='fact',id='location',subject='甲',attribute='location',value=value,kind=kind)
def beat(identifier='arrival',statement='甲在门外登记了来信。',changes=None):
    return dict(id=identifier,statement=statement,mode='actual',requires=[],changes=[fact()] if changes is None else changes)
def proposal(beats=None,number=1):
    return dict(number=number,title='来信',brief='事件接续',future_updates=[],scenes=[dict(id='scene',purpose='调查推进',participants=['甲'],beats=beats or [beat()])])
def event_config(n=3,review=True):return dict(config(n),event_first=True,story_review_enabled=review)


class EventLocal(Local):
    def __init__(self,fail=None,writer=None):super().__init__(fail=fail);self.writer=writer
    def complete(self,request):
        p=request.payload
        if request.role=='planner':
            self.requests.append(copy.deepcopy(request));self.number=p['chapter_number']
            n=self.number
            if n==1:change=fact();statement='甲在门外登记了来信。'
            else:
                prior='门外' if n==2 else '门内';target='门内' if n==2 else '待销库'
                change=dict(type='transition',id='move',fact_id='location',expected_revision=n-1,from_value=prior,to_value=target)
                statement=f'甲从{prior}走到{target}。'
            return ModelReply(canonical(proposal([beat('action',statement,[change])],n)),1,1,0)
        if request.role=='writer':
            self.requests.append(copy.deepcopy(request))
            if p.get('output_mode')=='plain_prose':return ModelReply('甲收好信，沿着走廊继续寻找线索。',1,1,0)
            if self.writer:value=self.writer(p)
            else:value=dict(text='雨落在窗上。\n\n'+''.join('[[event:'+b['id']+']]' for s in p['frozen_events']['scenes'] for b in s['beats']))
            return ModelReply(canonical(value),1,1,0)
        return super().complete(request)


class EventFirstTests(unittest.TestCase):
    def test_real_u_semantic_repair_uses_reserved_headroom_without_truncation(self):
        from memory_runtime.writing import WritingSession
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_u/working').glob('checkpoint_*.json')))
        raw=json.loads(next(r['raw_output'] for r in saved['trace'] if r.get('role')=='planner'))
        conflict=next(r for r in saved['trace'] if r.get('role')=='event_simulation')['repair_details']['issues'][0]
        corrected=copy.deepcopy(raw);effect=corrected['scenes'][0]['beats'][6]['changes'][0]
        corrected['scenes'][0]['beats'][6]['changes'][0]=dict(type='transition',fact_id=conflict['prior']['id'],to_value=effect['value'])
        class Saved:
            def __init__(self):self.requests=[]
            def complete(self,request):
                self.requests.append(copy.deepcopy(request))
                return ModelReply(canonical(raw if len(self.requests)==1 else corrected),1,1,0)
        gateway=Saved();session=WritingSession(self.root/'semantic_budget',gateway,cli.validate_config(self.read(ROOT/'novel_config_50000.json')),book=saved['book'])
        before=copy.deepcopy(session.book['writing_state']);trace=[]
        from tools.testing.archived_plan_fixture import compile_archived_plan
        with patch('memory_runtime.reference_choices.compile_plan',side_effect=compile_archived_plan):packet=session._prepare_events('继续写作',11,trace)
        self.assertEqual(len(gateway.requests),2)
        self.assertEqual(gateway.requests[1].payload['event_preflight_error']['previous_plan'],raw)
        self.assertEqual(session.book['writing_state'],before)
        self.assertEqual(packet['commit']['chapter'],11)
        self.assertEqual([r['narrative_transport']['limit_bytes'] for r in trace if r.get('role')=='planner'],[96000,120000])

    def test_unique_local_event_requirements_bind_but_ambiguous_future_and_stale_do_not(self):
        first=beat('seen','甲看见门开了。',[]);later=beat('enter','甲走进门。',[]);later['requires']=[dict(id='seen')]
        packet=prepare(empty(),proposal([first,later]),1)
        self.assertEqual(packet['commit']['scenes'][0]['beats'][1]['requires'][0]['id'],'c0001.seen')
        with self.assertRaises(ContractError):prepare(empty(),proposal([later,first]),1)
        collision=copy.deepcopy(first);collision['changes']=[dict(fact(),id='seen')]
        with self.assertRaises(ContractError):prepare(empty(),proposal([collision,later]),1)
        stale=copy.deepcopy(later);stale['requires'][0]['revision']=2
        with self.assertRaises(ContractError):prepare(empty(),proposal([first,stale]),1)
        planned=copy.deepcopy(first);planned['mode']='planned'
        with self.assertRaises(ContractError):prepare(empty(),proposal([planned,later]),1)
        from memory_runtime.event_references import catalogue
        record=self.read(max((ROOT/'runs/event_first_50000_20261022_t/working').glob('checkpoint_*.json')))
        raw=[json.loads(r['raw_output']) for r in record['trace'] if r.get('role')=='planner' and r.get('status')=='ACCEPTED']
        self.assertEqual(len(raw),2)
        for value in raw:
            original=copy.deepcopy(value)
            packet=prepare(record['book']['writing_state'],value,4,references=catalogue(record['book']))
            self.assertTrue(packet['candidate_state']['event_log'])
            self.assertEqual(value,original)

    def test_real_r_prepared_chapter_fits_writer_budget_without_losing_events(self):
        from memory_runtime.writing import WritingSession
        from memory_runtime.event_first import writer_view
        from inf_writer.narrative_context import event_role_context
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_r/working').glob('checkpoint_*.json')))
        book=saved['book'];prepared=book['prepared_events']['7'];original=copy.deepcopy(prepared)
        plan=cli.validate_config(self.read(ROOT/'novel_config_50000.json'))
        session=WritingSession(self.root/'writer_budget',EventLocal(),plan,book=book)
        context=session.context('继续写作',prepared['proposal']['title']+' '+prepared['proposal']['brief'])
        context['chapter_plan']={k:prepared['proposal'][k] for k in ('number','title','brief')}
        context['frozen_events']=writer_view(prepared)
        context=event_role_context(context,'writer');session._bound(context)
        expected=[(b['id'],b['statement'],b['mode']) for s in prepared['commit']['scenes'] for b in s['beats']]
        actual=[(b['canonical_id'],b['statement'],b['mode']) for s in context['frozen_events']['scenes'] for b in s['beats']]
        self.assertEqual(actual,expected)
        self.assertEqual([s['participants'] for s in context['frozen_events']['scenes']],
            [s['participants'] for s in prepared['commit']['scenes']])
        self.assertFalse(any('changes' in b or 'requires' in b for s in context['frozen_events']['scenes'] for b in s['beats']))
        template='\n'.join('[[event:'+b['id']+']]' for s in context['frozen_events']['scenes'] for b in s['beats'])
        self.assertTrue(realize(template,prepared['commit']))
        self.assertEqual(prepared,original)

    def test_transition_target_diagnostics_and_sequential_binding(self):
        first=fact();move=dict(type='transition',fact_id='location',to_value='屋内')
        packet=prepare(empty(),proposal([beat(changes=[first,move])]),1)
        self.assertEqual(packet['candidate_state']['facts']['location']['value'],'屋内')
        self.assertEqual(packet['candidate_state']['facts']['location']['revision'],2)
        record=self.read(max((ROOT/'runs/event_first_50000_20261022_q/working').glob('checkpoint_*.json')))
        raw=[json.loads(r['raw_output']) for r in record['trace'] if r.get('role')=='planner' and r.get('status')=='ACCEPTED'][-1]
        original=copy.deepcopy(raw)
        with self.assertRaises(ContractError) as caught:prepare(empty(),raw,1)
        issue=caught.exception.repair_details['issues'][0]
        self.assertEqual(issue['field'],'fact_id')
        self.assertEqual(issue['cause_details']['expected_reference_types'],['fact'])
        self.assertEqual(issue['cause_details']['reference_candidates'][0]['type'],'object')
        self.assertIn('separate fact',issue['cause_details']['instruction'])
        self.assertEqual(raw,original)

    def test_circular_dependency_reports_introduction_and_examples_execute(self):
        from memory_runtime.event_first import CONTRACT
        examples=CONTRACT['dependency_examples']
        packet=prepare(empty(),proposal(examples),1)
        self.assertEqual(packet['candidate_state']['facts']['letter_location']['value'],'屋内')
        bad=proposal();bad['scenes'][0]['beats'][0]['requires']=[dict(id='location',type='fact')]
        with self.assertRaises(ContractError) as caught:prepare(empty(),bad,1)
        issue=caught.exception.repair_details['issues'][0]
        self.assertEqual(issue['same_beat_effects'][0]['id'],'location')
        self.assertIn('cannot also be a prerequisite',issue['instruction'])
        record=self.read(max((ROOT/'runs/event_first_50000_20261022_p/working').glob('checkpoint_*.json')))
        raw=[json.loads(r['raw_output']) for r in record['trace'] if r.get('role')=='planner' and r.get('status')=='ACCEPTED'][-1]
        original=copy.deepcopy(raw)
        with self.assertRaises(ContractError) as caught:prepare(empty(),raw,1)
        self.assertIn('cannot also be a prerequisite',caught.exception.repair_details['issues'][0]['instruction'])
        # A planner-side correction is explicit; normalization never silently drops prerequisites.
        corrected=copy.deepcopy(raw);corrected['scenes'][0]['beats'][0]['requires']=[]
        fixed=prepare(empty(),corrected,1)
        self.assertTrue(fixed['candidate_state']['facts'])
        self.assertEqual(raw,original)

    def test_layer_repairs_only_failed_items_and_keeps_valid_decisions(self):
        from memory_runtime.engine import MemoryEngine
        from memory_runtime.pipeline import LayerAgent
        packet=prepare(empty(),proposal(),1);commit=packet['commit'];template='[[event:arrival]]'
        prose=realize(template,commit)
        chapter=dict(number=1,title='来信',text=prose,sha256=digest(prose),event_commit=commit,realization_template=template)
        memory=project_memory(MemoryEngine.empty(),[chapter],1,[]);original=copy.deepcopy(memory)
        for second in ('valid','invalid','malformed','duplicate'):
            class Partial:
                def __init__(self):self.requests=[]
                def complete(self,request):
                    self.requests.append(copy.deepcopy(request));rows=request.payload['items']
                    if len(self.requests)==1:
                        value=dict(placements=[dict(id=r['id'],tier='recent',priority=3,reason='已完成') for r in rows[:-1]])
                    elif second=='malformed':return ModelReply('not json',1,1,0)
                    else:
                        value=dict(placements=[dict(id=r['id'],tier='recent' if second!='invalid' else 'unknown',priority=3,reason='归档') for r in rows])
                        if second=='duplicate':value['placements']*=3
                    return ModelReply(canonical(value),1,1,0)
            gateway=Partial();trace=[]
            result,report=LayerAgent(gateway).run(memory,[chapter],1,'来信',trace)
            with self.subTest(second=second):
                self.assertEqual(memory,original)
                self.assertEqual(len(gateway.requests),2)
                self.assertEqual(len(gateway.requests[1].payload['items']),1)
                self.assertEqual(set(result['items']),set(memory['items']))
                self.assertEqual(report['status'],'APPLIED' if second=='valid' else 'APPLIED_WITH_DEFERRED')
                self.assertEqual(len(report['deferred_ids']),0 if second=='valid' else 1)
                self.assertEqual(result['layer_deferred_ids'],sorted(report['deferred_ids']))
                self.assertTrue(report['moves'])
                for identifier,row in result['items'].items():
                    self.assertEqual(row['claim'],memory['items'][identifier]['claim'])
                class Recovered:
                    def complete(self,request):
                        return ModelReply(canonical(dict(placements=[dict(id=r['id'],tier=r['tier'],priority=3,reason='重新整理确认') for r in request.payload['items']])),1,1,0)
                recovered,next_report=LayerAgent(Recovered()).run(result,[chapter],2,'来信',[])
                self.assertFalse(recovered['layer_deferred_ids'])
                self.assertEqual(next_report['status'],'APPLIED')

    def test_real_o_layer_replies_retain_correct_rows_without_losing_memory(self):
        from memory_runtime.pipeline import LayerAgent
        folder=ROOT/'runs/event_first_50000_20261022_o/working'
        record=self.read(max(folder.glob('checkpoint_*.json')));book=record['book']
        entries=[r for r in record['trace'] if r.get('role')=='layers' and r.get('chapter_number')==8]
        # The final checkpoint only carries the latest chapter trace; locate its saved predecessor.
        if not entries:
            for path in sorted(folder.glob('checkpoint_*.json'),reverse=True):
                entries=[r for r in self.read(path)['trace'] if r.get('role')=='layers' and r.get('chapter_number')==8]
                if entries:break
        self.assertEqual(len(entries),2)
        memory=project_memory(book['memory'],book['chapters'],8,[]);original=copy.deepcopy(memory)
        class Saved:
            def __init__(self):self.index=0
            def complete(self,request):
                reply=ModelReply(entries[self.index]['raw_output'],1,1,0);self.index+=1;return reply
        result,report=LayerAgent(Saved()).run(memory,book['chapters'],8,book['chapters'][7]['title'],[])
        self.assertEqual(memory,original)
        self.assertEqual(set(result['items']),set(memory['items']))
        self.assertTrue(report['moves'])
        self.assertIn(report['status'],('APPLIED','APPLIED_WITH_DEFERRED'))
        self.assertEqual(result['processed_through'],8)

    def test_vague_time_is_repaired_before_simulation_and_preserved_as_appointment(self):
        class Vague(EventLocal):
            def complete(self,request):
                if request.role!='planner':return super().complete(request)
                self.requests.append(copy.deepcopy(request))
                value=proposal([beat('action','甲约定后天傍晚再来。',[fact('约定后天傍晚再来',kind='planned')])])
                if 'repair' not in request.payload:
                    value['time_calculations']=[dict(id='meet',kind='provisional_interval',expression='后天傍晚',result='日落前后')]
                else:
                    assert request.payload['repair']['details']['code']=='TIME_REQUEST_ERRORS'
                    assert '模糊或相对约定' in request.payload['calculation_contract']['instruction']
                    value['time_calculations']=[]
                return ModelReply(canonical(value),1,1,0)
        provider=Vague();result=self.launch(provider,event_config(1,False))
        self.assertTrue(result['draft_completed'])
        state=self.read(self.root/'run/final_state.json')
        self.assertIn('后天傍晚',state['chapters'][0]['text'])
        self.assertEqual(state['chapters'][0]['time_calculations'],[])
        self.assertFalse(state['writing_state']['facts'])
        self.assertTrue(any('后天傍晚' in r['claim'] for r in state['memory']['items'].values()))
        self.assertEqual(len([r for r in provider.requests if r.role=='planner']),2)

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'runs');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def read(self,p):return json.loads(Path(p).read_text(encoding='utf-8'))
    def launch(self,provider,cfg=None,name='run',resume=None):
        with patch.object(cli,'read_secret',return_value='offline'),patch.object(cli,'ChatCompletionProvider',return_value=provider),contextlib.redirect_stdout(io.StringIO()):
            from tools.testing.archived_plan_fixture import compile_archived_plan
            with patch('memory_runtime.reference_choices.compile_plan',side_effect=compile_archived_plan):return cli.launch(cfg or event_config(),self.root/name,resume=resume)

    def test_default_config_enables_event_first_without_opt_in(self):
        cfg=config(1);cfg.pop('event_first')
        self.assertTrue(cli.validate_config(cfg)['event_first'])
        self.assertTrue(self.launch(EventLocal(),cfg)['draft_completed'])

    def test_simulation_freezes_events_before_writer_and_memory_never_reextracts(self):
        provider=EventLocal();result=self.launch(provider)
        self.assertTrue(result['draft_completed']);self.assertTrue(result['memory_complete'])
        self.assertFalse(any('memory_contract' in r.payload or 'memory_mutation_review' in r.payload or 'candidate_items' in r.payload for r in provider.requests))
        state=self.read(self.root/'run/final_state.json')
        self.assertEqual(state['writing_state']['facts']['location']['value'],'待销库')
        self.assertEqual(state['writing_state']['facts']['location']['revision'],3)
        self.assertTrue(all('event_commit' in c for c in state['chapters']))
        snapshots=[self.read(p) for p in sorted((self.root/'run/working').glob('checkpoint_*.json'))]
        first=next(s for s in snapshots if s['reason']=='EVENTS_PREPARED_NOT_COMMITTED')
        self.assertEqual(first['book']['chapters'],[])
        self.assertEqual(first['book']['writing_state']['facts'],{})
        self.assertEqual(first['book']['prepared_events']['1']['candidate_state']['facts']['location']['value'],'门外')
        sources=[v for v in state['memory']['items'].values() if v['subject']=='甲' and v['attribute']=='location']
        self.assertEqual(len(sources),1);self.assertEqual(sources[0]['claim'],'甲从门内走到待销库。')
        second=next(r for r in provider.requests if r.role=='planner' and r.payload['chapter_number']==2)
        self.assertEqual(set(second.payload['recent_chapters'][0]),{'number','title','text','sha256'})
        self.assertEqual(result['canonical_event_chapters'],3);self.assertEqual(result['writing_mode'],'event_first')

    def test_memory_layer_failure_does_not_revert_world_state_for_next_planner(self):
        provider=EventLocal(fail='layers2');result=self.launch(provider)
        self.assertTrue(result['draft_completed']);self.assertEqual(result['memory_processed_through'],1)
        third=next(r for r in provider.requests if r.role=='planner' and r.payload['chapter_number']==3)
        current=next(r for r in third.payload['event_plan_state']['records'] if r['record_kind']=='fact_record' and r['record_id']=='location')
        self.assertEqual(current['value'],'门内');self.assertEqual(current['record_revision'],2)
        state=self.read(self.root/'run/final_state.json')
        self.assertEqual(state['writing_state']['facts']['location']['value'],'待销库')

    def test_unknown_prose_marker_is_saved_literally_and_resume_verifies_it(self):
        failed=self.launch(EventLocal(writer=lambda p:dict(text='[[event:invented]]')),event_config(1))
        self.assertEqual(failed['chapters'],1)
        state=self.read(self.root/'run/final_state.json')
        self.assertEqual(state['chapters'][0]['text'],'[[event:invented]]')
        self.assertEqual(state['chapters'][0]['prose_encoding'],'literal')
        from memory_runtime.writing import load_resume
        self.assertEqual(load_resume(failed['resume_checkpoint'],cli.validate_config(event_config(1)))['chapters'],state['chapters'])

    def test_writer_cannot_submit_new_facts_even_with_valid_text(self):
        provider=EventLocal(writer=lambda p:dict(text='[[event:action]]',continuity_updates=[]))
        result=self.launch(provider,event_config(1))
        self.assertTrue(result['draft_completed'])
        state=self.read(self.root/'run/final_state.json')
        self.assertEqual(set(state['writing_state']['facts']),{'location'})
        self.assertGreater(result['generation_warning_count'],0)

    def test_precondition_conflict_defers_state_changes_and_continues_prose(self):
        class Bad(EventLocal):
            def complete(self,request):
                if request.role=='planner':
                    self.requests.append(copy.deepcopy(request))
                    b=beat(changes=[dict(type='transition',id='move',fact_id='missing',expected_revision=1,from_value='门外',to_value='屋里')])
                    return ModelReply(canonical(proposal([b])),1,1,0)
                return super().complete(request)
        provider=Bad();result=self.launch(provider,event_config(1))
        self.assertTrue(result['draft_completed']);self.assertTrue(any(r.role=='writer' for r in provider.requests))
        self.assertEqual(result['unprojected_chapters'],[1])
        self.assertEqual(self.read(self.root/'run/final_state.json')['writing_state']['facts'],{})

    def test_time_is_computed_in_frozen_statement_before_prose(self):
        p=proposal([beat(statement='传真[[time:fax.start]]发出，[[time:fax.end]]收到，相隔[[time:fax]]。',changes=[])])
        p['time_calculations']=[dict(id='fax',kind='interval',start='16:41',end='16:45')]
        prepared=prepare(empty(),p,1)
        self.assertEqual(realize('[[event:arrival]]',prepared['commit']),'传真16:41发出，16:45收到，相隔四分钟。')
        with self.assertRaises(ContractError):realize('[[event:arrival]]中间隔了两分钟。',prepared['commit'])

    def test_unknown_or_duplicate_event_tokens_do_not_realize(self):
        c=prepare(empty(),proposal(),1)['commit']
        for raw in ('没有事件','[[event:arrival]][[event:arrival]]','[[event:wrong]]'):
            with self.assertRaises(ContractError):realize(raw,c)

    def test_immutable_facts_cannot_change_and_preconditions_are_versioned(self):
        state=prepare(empty(),proposal([beat(changes=[fact('灰色','immutable')])]),1)['candidate_state']
        change=dict(type='transition',id='change',fact_id='location',expected_revision=1,from_value='灰色',to_value='金色')
        with self.assertRaises(ContractError):prepare(state,proposal([beat(changes=[change])],2),2)
        state=prepare(empty(),proposal(),1)['candidate_state']
        b=beat(changes=[]);b['requires']=[dict(type='fact',id='location',revision=2)]
        with self.assertRaises(ContractError):prepare(state,proposal([b],2),2)

    def test_learning_derives_value_and_requires_participation(self):
        first=beat('light','灯亮了。',[dict(fact('亮'),id='lamp',subject='灯',attribute='status')])
        learn=dict(type='learn',id='noticed',actor='甲',fact_id='lamp',via_event='notice')
        second=beat('notice','甲看见灯亮着。',[learn])
        state=prepare(empty(),proposal([first,second]),1)['candidate_state']
        self.assertEqual(state['knowledge']['noticed']['value'],'亮')
        self.assertEqual(state['knowledge']['noticed']['fact_revision'],1)
        second['changes'][0]['actor']='乙'
        with self.assertRaises(ContractError):prepare(empty(),proposal([first,second]),1)

    def test_reports_and_future_plans_do_not_establish_world_truth(self):
        b=beat();b['mode']='reported'
        with self.assertRaises(ContractError):prepare(empty(),proposal([b]),1)
        b['mode']='planned';packet=prepare(empty(),proposal([b]),1)
        self.assertEqual(packet['candidate_state']['facts'],{})
        self.assertEqual(packet['commit']['scenes'][0]['beats'][0]['proposed_changes'],b['changes'])
        b=beat(statement='甲打算明天进屋。',changes=[]);b['mode']='planned'
        state=prepare(empty(),proposal([b]),1)['candidate_state']
        self.assertEqual(state['facts'],{})

    def test_projection_rejects_modified_commit_or_realized_prose(self):
        p=prepare(empty(),proposal(),1);c=p['commit'];draft=realize('[[event:arrival]]',c)
        chapter=dict(number=1,title='来信',text=draft,sha256=digest(draft),event_commit=c,realization_template='[[event:arrival]]')
        from memory_runtime.engine import MemoryEngine
        before=MemoryEngine.empty();projected=project_memory(before,[chapter],1,[])
        self.assertEqual(project_memory(projected,[chapter],1,[]),projected)
        self.assertEqual(before,MemoryEngine.empty())
        changed=copy.deepcopy(chapter);changed['event_commit']['scenes'][0]['beats'][0]['statement']='篡改'
        with self.assertRaises(ContractError):project_memory(before,[changed],1,[])
        changed=copy.deepcopy(chapter);changed['text']='篡改';changed['sha256']=digest('篡改')
        with self.assertRaises(ContractError):project_memory(before,[changed],1,[])

    def test_world_change_does_not_silently_update_a_characters_old_knowledge(self):
        establish=beat('light','灯亮了。',[dict(fact('亮'),id='lamp',subject='灯',attribute='status')])
        learn=beat('notice','甲看见灯亮着。',[dict(type='learn',id='noticed',actor='甲',fact_id='lamp',via_event='notice')])
        state=prepare(empty(),proposal([establish,learn]),1)['candidate_state']
        later=beat('dark','甲离开后灯熄了。',[dict(type='transition',id='switch',fact_id='lamp',expected_revision=1,from_value='亮',to_value='灭')])
        state=prepare(state,proposal([later],2),2)['candidate_state']
        self.assertEqual(state['facts']['lamp']['value'],'灭')
        self.assertEqual(state['knowledge']['noticed']['value'],'亮')
        self.assertEqual(state['knowledge']['noticed']['fact_revision'],1)

    def test_prose_and_state_roll_back_together_when_draft_checkpoint_cannot_save(self):
        from memory_runtime.writing import WritingSession
        saved=WritingSession._save
        def fail_draft(session,trace,reason):
            if reason=='DRAFT_SAVED_MEMORY_PENDING':raise OSError('simulated disk failure')
            return saved(session,trace,reason)
        with patch.object(WritingSession,'_save',fail_draft):
            result=self.launch(EventLocal(),event_config(1))
        self.assertEqual(result['chapters'],0)
        state=self.read(self.root/'run/final_state.json')
        self.assertEqual(state['writing_state']['facts'],{});self.assertIn('1',state['prepared_events'])
        self.assertEqual(state['pending'],[])

    def test_planned_event_projects_as_plan_instead_of_completed_world_state(self):
        b=beat(statement='甲打算明天进屋。',changes=[]);b['mode']='planned'
        c=prepare(empty(),proposal([b]),1)['commit'];draft=realize('[[event:arrival]]',c)
        chapter=dict(number=1,title='打算',text=draft,sha256=digest(draft),event_commit=c,realization_template='[[event:arrival]]')
        from memory_runtime.engine import MemoryEngine
        memory=project_memory(MemoryEngine.empty(),[chapter],1,[])
        row=next(iter(memory['items'].values()))
        self.assertEqual((row['kind'],row['status']),('task','planned'))

    def test_explicit_revision_returns_to_planning_without_committing_first_candidate(self):
        attempts=[]
        def writer(p):
            attempts.append(p)
            if len(attempts)==1:return dict(event_revision_request='需要先确认来信来源，再展开动作。')
            return dict(text='[[event:action]]')
        provider=EventLocal(writer=writer);result=self.launch(provider,event_config(1))
        self.assertTrue(result['draft_completed'])
        plans=[r for r in provider.requests if r.role=='planner']
        self.assertEqual(len(plans),2);self.assertIn('event_revision_request',plans[1].payload)
        state=self.read(self.root/'run/final_state.json')
        self.assertEqual(state['writing_state']['facts']['location']['revision'],1)
        self.assertEqual(len(state['writing_state']['event_log']),1)

    def test_second_writer_revision_request_continues_prose_without_more_planning(self):
        result=self.launch(EventLocal(writer=lambda p:dict(event_revision_request='再加一个事件。')),event_config(1))
        self.assertTrue(result['draft_completed'])
        self.assertGreater(result['generation_warning_count'],0)

    def test_real_first_run_replies_replay_with_all_facts_and_bound_knowledge(self):
        from memory_runtime.identifiers import attribute_identifier
        saved=self.read(ROOT/'runs/event_first_50000_20261022_a/working/checkpoint_0001.json')
        plans=[r['proposal'] for r in saved['trace'] if r['role']=='event_simulation']
        self.assertEqual(len(plans),2)
        for plan in plans:
            original=copy.deepcopy(plan);before=empty()
            prepared=prepare(before,plan,1);world=prepared['candidate_state']
            inputs={c['id']:c for s in plan['scenes'] for b in s['beats'] for c in b['changes'] if c['type']=='fact'}
            self.assertEqual(set(world['facts']),set(inputs))
            self.assertEqual(plan,original);self.assertEqual(before,empty())
            for fid,row in inputs.items():
                actual=world['facts'][fid]
                self.assertEqual(actual['attribute'],attribute_identifier(row['attribute']))
                self.assertEqual(actual['attribute_label'],row['attribute'])
                self.assertEqual(actual['value'],row['value'])
            self.assertEqual(len(world['knowledge']),5)
            self.assertTrue(all(k['via_event'].startswith('c0001.') for k in world['knowledge'].values()))

    def test_chinese_field_labels_survive_state_transition_and_memory_projection(self):
        from memory_runtime.engine import MemoryEngine
        p=proposal([beat(changes=[dict(fact(),attribute='当前位置')])])
        prepared=prepare(empty(),p,1);world=prepared['candidate_state'];canonical_attr=world['facts']['location']['attribute']
        c=prepared['commit'];draft=realize('[[event:arrival]]',c)
        ch=dict(number=1,title='来信',text=draft,sha256=digest(draft),event_commit=c,realization_template='[[event:arrival]]')
        memory=project_memory(MemoryEngine.empty(),[ch],1,[])
        self.assertEqual(memory['attribute_labels'][canonical_attr],'当前位置')
        change=dict(type='transition',id='move',fact_id='location',expected_revision=1,from_value='门外',to_value='门内')
        next_world=prepare(world,proposal([beat('move','甲进了门。',[change])],2),2)['candidate_state']
        self.assertEqual(next_world['facts']['location']['attribute'],canonical_attr)
        self.assertEqual(next_world['facts']['location']['attribute_label'],'当前位置')

    def test_invalid_labels_produce_all_exact_effect_locations_without_mutating_state(self):
        rows=[dict(fact(),id='bad_one',attribute=''),dict(fact(),id='bad_two',attribute=None)]
        state=empty()
        with self.assertRaises(ContractError) as caught:prepare(state,proposal([beat(changes=rows)]),1)
        issues=caught.exception.repair_details['issues']
        self.assertEqual(len(issues),2)
        self.assertEqual([r['path'] for r in issues],['scenes[0].beats[0].changes[0].attribute','scenes[0].beats[0].changes[1].attribute'])
        self.assertEqual(caught.exception.repair_details['code'],'EVENT_SHAPE_ERRORS')
        self.assertEqual(state,empty())

    def test_non_effect_preflight_error_also_has_a_scene_and_beat_locator(self):
        bad=beat(statement='他引用了[[time:missing]]。',changes=[])
        with self.assertRaises(ContractError) as caught:prepare(empty(),proposal([bad]),1)
        locator=caught.exception.repair_details['locator']
        self.assertEqual(locator['scene_id'],'scene');self.assertEqual(locator['beat_id'],'arrival')

    def test_second_run_real_replies_preserve_identifiers_and_bind_local_initial_revisions(self):
        saved=self.read(ROOT/'runs/event_first_50000_20261022_b/working/checkpoint_0001.json')
        plans=[r['proposal'] for r in saved['trace'] if r['role']=='event_simulation']
        self.assertEqual(len(plans),2)
        for plan in plans:
            original=copy.deepcopy(plan);packet=prepare(empty(),plan,1)
            expected=sum(c['type']=='fact' for s in plan['scenes'] for b in s['beats'] for c in b['changes'])
            self.assertEqual(len(packet['candidate_state']['facts']),expected)
            self.assertEqual(plan,original)
            for s in packet['commit']['scenes']:
                for b in s['beats']:
                    self.assertTrue(all(r['revision']==1 for r in b['requires']))
            template=''.join('[[event:'+b['token_id']+']]' for s in packet['commit']['scenes'] for b in s['beats'])
            prose=realize(template,packet['commit'])
            self.assertNotIn('[[event:',prose)

    def test_zero_version_never_repairs_a_stale_existing_record(self):
        state=prepare(empty(),proposal(),1)['candidate_state']
        later=beat(changes=[]);later['requires']=[dict(type='fact',id='location',revision=0)]
        with self.assertRaises(ContractError):prepare(state,proposal([later],2),2)
        later['requires']=[dict(type='fact',id='location')]
        self.assertEqual(prepare(state,proposal([later],2),2)['commit']['scenes'][0]['beats'][0]['requires'][0]['revision'],1)

    def test_real_clause_replies_get_precise_contract_feedback_not_silent_conversion(self):
        from inf_writer.agents import JsonAgent
        saved=self.read(ROOT/'runs/event_first_50000_20261022_c/working/checkpoint_0018.json')
        replies=[t['raw_output'] for t in saved['trace'] if t.get('role')=='writer']
        request=self.read(ROOT/'runs/event_first_50000_20261022_c/call_024.request.json')
        class Replay:
            def __init__(self):self.requests=[]
            def complete(self,req):
                self.requests.append(copy.deepcopy(req))
                return ModelReply(replies[len(self.requests)-1],1,1,0)
        replay=Replay();trace=[]
        with self.assertRaises(ContractError):JsonAgent('writer',replay,compact_narrative=True).run(request['payload'],trace)
        self.assertEqual(len(replay.requests),2)
        payload=replay.requests[-1].payload;details=payload['repair']['details']
        self.assertEqual(details['missing_fields'],['text'])
        self.assertEqual(details['unexpected_fields'],['clauses'])
        self.assertEqual(payload['repair']['previous_output'],replies[0])
        self.assertEqual(payload['frozen_events'],request['payload']['frozen_events'])
        self.assertNotIn('state_record_contract',payload)
        self.assertNotIn('event_first_contract',payload)
        self.assertNotIn('calculation_contract',payload)
        self.assertEqual(trace[-1]['repair_details']['actual_fields'],['clauses','type'])

    def test_role_contracts_repair_missing_planner_field_and_keep_writer_anchors(self):
        from inf_writer.agents import JsonAgent
        class MissingFuture(EventLocal):
            def complete(self,req):
                if req.role=='planner' and 'repair' not in req.payload:
                    self.requests.append(copy.deepcopy(req))
                    value=proposal();value.pop('future_updates')
                    return ModelReply(canonical(value),1,1,0)
                return super().complete(req)
        provider=MissingFuture();result=self.launch(provider,event_config(1))
        self.assertTrue(result['draft_completed'])
        repair=next(r.payload for r in provider.requests if r.role=='planner' and 'repair' in r.payload)
        self.assertEqual(repair['repair']['details']['missing_fields'],['future_updates'])
        writer=next(r.payload for r in provider.requests if r.role=='writer')
        self.assertNotIn('ordered_event_tokens',writer['output_contract'])
        self.assertEqual(writer['frozen_events']['scenes'][0]['beats'][0]['id'],'slot_001')
        self.assertIn('state_record_contract',repair)
        self.assertNotIn('state_record_contract',writer)

    def test_real_object_origins_bind_to_actual_canonical_beats(self):
        saved=self.read(ROOT/'runs/event_first_50000_20261022_d/working/checkpoint_0001.json')
        plans=[r['proposal'] for r in saved['trace'] if r['role']=='event_simulation']
        self.assertEqual(len(plans),2)
        for plan in plans:
            packet=prepare(empty(),plan,1);world=packet['candidate_state']
            expected=sum(r['type']=='object' for s in plan['scenes'] for b in s['beats'] for r in b['changes'])
            self.assertEqual(len(world['objects']),expected)
            for obj in world['objects'].values():
                if obj['origin'] is not None:self.assertEqual(world['event_log'][obj['origin']]['mode'],'actual')

    def test_object_origins_and_availability_cannot_use_unknown_or_future_beats(self):
        obj=dict(type='object',id='note',label='便笺',form='original',status='missing',origin='arrival')
        packet=prepare(empty(),proposal([beat(changes=[obj])]),1)
        state=packet['candidate_state'];obj=copy.deepcopy(state['objects']['note'])
        update={k:obj[k] for k in ('type','id','label','form','status','origin')}
        update.update(status='available',event_id='retrieve')
        retrieved=prepare(state,proposal([beat('retrieve','甲从抽屉里找回便笺。',[update])],2),2)['candidate_state']
        self.assertEqual(retrieved['objects']['note']['status'],'available')
        for bad in ('unknown_event','later'):
            update['event_id']=bad
            with self.assertRaises(ContractError):prepare(state,proposal([beat('retrieve',changes=[update])],2),2)
        update['event_id']='retrieve';bad=beat('retrieve',changes=[update]);bad['mode']='reported'
        with self.assertRaises(ContractError):prepare(state,proposal([bad],2),2)

    def test_real_namespaced_person_and_all_preflight_errors_are_handled_together(self):
        saved=self.read(ROOT/'runs/event_first_50000_20261022_e/working/checkpoint_0005.json')
        plans=[t['proposal'] for t in saved['trace'] if t['role']=='event_simulation']
        world=saved['book']['writing_state'];original=copy.deepcopy(world)
        with self.assertRaises(ContractError) as caught:prepare(world,plans[0],2)
        issues=caught.exception.repair_details['issues']
        self.assertTrue(any(i['field']=='requires' for i in issues))
        self.assertEqual(world,original)
        packet=prepare(world,plans[1],2);learned=list(packet['candidate_state']['knowledge'].values())
        self.assertTrue(any(k['actor']=='许闻' for k in learned))
        self.assertTrue(any(n['original']=='person:许闻' for n in packet['commit']['identifier_normalizations']))

    def test_multiple_prerequisite_and_effect_failures_reported_without_committing(self):
        first=beat('first',changes=[dict(fact(),attribute='')]);first['requires']=[dict(type='fact',id='missing_one')]
        second=beat('second',changes=[]);second['requires']=[dict(type='fact',id='missing_two')]
        state=empty()
        with self.assertRaises(ContractError) as caught:prepare(state,proposal([first,second]),1)
        issues=caught.exception.repair_details['issues']
        self.assertEqual(len(issues),1)
        self.assertEqual(caught.exception.repair_details['code'],'EVENT_SHAPE_ERRORS')
        first['changes'][0]['attribute']='location'
        with self.assertRaises(ContractError) as caught:prepare(state,proposal([first,second]),1)
        issues=caught.exception.repair_details['issues']
        self.assertEqual(len(issues),2)
        self.assertEqual([i.get('requirement',{}).get('id') for i in issues if i['field']=='requires'],['missing_one','missing_two'])
        self.assertEqual(state,empty())

    def test_real_phone_participant_replies_preserve_learning_and_channel(self):
        saved=self.read(ROOT/'runs/event_first_50000_20261022_f/working/checkpoint_0034.json')
        plans=[t['proposal'] for t in saved['trace'] if t['role']=='event_simulation']
        self.assertEqual(len(plans),2)
        for plan in plans:
            original=copy.deepcopy(plan);packet=prepare(saved['book']['writing_state'],plan,9)
            world=packet['candidate_state']
            for lid in ('l9_liang_hears_outsource','l9_liang_hears_scan_gap'):
                learned=world['knowledge'][lid]
                self.assertEqual(learned['actor'],'梁策')
                self.assertIn('梁策',world['event_log'][learned['via_event']]['participants'])
            self.assertTrue(any(n.get('channel')=='phone' and n['storage_id']=='梁策' for n in packet['commit']['identifier_normalizations']))
            self.assertEqual(plan,original)

    def test_structured_remote_participant_keeps_identity_and_rejects_absent_learner(self):
        p=proposal([beat(changes=[fact(),dict(type='learn',id='heard',actor='甲',fact_id='location',via_event='arrival')])])
        p['scenes'][0]['participants']=[dict(id='甲',channel='phone')]
        packet=prepare(empty(),p,1)
        self.assertEqual(packet['candidate_state']['knowledge']['heard']['actor'],'甲')
        p['scenes'][0]['participants']=[dict(id='乙',channel='phone')]
        with self.assertRaises(ContractError) as caught:prepare(empty(),p,1)
        issue=caught.exception.repair_details['issues'][0]
        self.assertEqual(issue['learner'],'甲');self.assertEqual(issue['expected_participants'],['乙'])
        self.assertEqual(issue['source_event']['id'],'c0001.arrival')

    def test_real_reported_beliefs_can_be_heard_without_becoming_truth(self):
        saved=self.read(ROOT/'runs/event_first_50000_20261022_g/working/checkpoint_0005.json')
        plans=[t['proposal'] for t in saved['trace'] if t['role']=='event_simulation']
        self.assertEqual(len(plans),2)
        # The first proposal also names nonexistent prior fact IDs. Those remain
        # errors; accepting reported knowledge must not weaken prerequisites.
        with self.assertRaises(ContractError) as caught:prepare(saved['book']['writing_state'],plans[0],2)
        self.assertTrue(all(i['field']=='requires' for i in caught.exception.repair_details['issues']))
        for plan in plans[1:]:
            packet=prepare(saved['book']['writing_state'],plan,2);world=packet['candidate_state']
            record=world['facts']['fact_operation_record_trail'];heard=world['knowledge']['lrn_liangce_trail']
            self.assertEqual(record['kind'],'belief')
            self.assertEqual(heard['epistemic_status'],'belief')
            self.assertEqual(heard['value'],record['value'])
            self.assertEqual(world['event_log'][heard['via_event']]['mode'],'reported')

    def test_reported_updates_preserve_belief_and_cannot_upgrade_objective_facts(self):
        established=beat(changes=[fact(kind='belief')]);established['mode']='reported'
        state=prepare(empty(),proposal([established]),1)['candidate_state']
        change=dict(type='transition',id='revise',fact_id='location',expected_revision=1,from_value='门外',to_value='门内')
        heard=dict(type='learn',id='heard',actor='甲',fact_id='location',via_event='report')
        report=beat('report','甲又听说人在门内。',[change,heard]);report['mode']='reported'
        world=prepare(state,proposal([report],2),2)['candidate_state']
        self.assertEqual(world['facts']['location']['kind'],'belief')
        self.assertEqual(world['knowledge']['heard']['epistemic_status'],'belief')
        truth=prepare(empty(),proposal(),1)['candidate_state']
        with self.assertRaises(ContractError):prepare(truth,proposal([report],2),2)
        report['changes']=[dict(type='object',id='paper',label='纸',form='original',status='available',origin=None)]
        with self.assertRaises(ContractError):prepare(state,proposal([report],2),2)

    def test_proposed_future_effects_are_not_knowledge_sources_or_satisfied_preconditions(self):
        planned=beat('later',changes=[fact()]);planned['mode']='planned'
        checked=beat('check',changes=[]);checked['requires']=[dict(type='fact',id='location')]
        with self.assertRaises(ContractError):prepare(empty(),proposal([planned,checked]),1)
        p=prepare(empty(),proposal([planned]),1)
        self.assertEqual(p['candidate_state']['facts'],{})
        actual=beat('now',changes=[fact(),dict(type='learn',id='heard',actor='甲',fact_id='location',via_event='c0001.later')])
        with self.assertRaises(ContractError):prepare(p['candidate_state'],proposal([actual],2),2)
        from memory_runtime.engine import MemoryEngine
        commit=p['commit'];draft=realize('[[event:later]]',commit)
        chapter=dict(number=1,title='打算',text=draft,sha256=digest(draft),event_commit=commit,realization_template='[[event:later]]')
        memory=project_memory(MemoryEngine.empty(),[chapter],1,[])
        self.assertTrue(all(v['kind']=='task' and v['status']=='planned' for v in memory['items'].values()))

    def test_structured_participant_variants_have_one_identity_and_precise_bad_field_feedback(self):
        for value in ('甲',dict(id='甲'),dict(id='甲',channel='phone'),dict(id='甲',label='甲老师'),dict(id='甲',channel='短信/见面'),dict(id='甲',channel=['电话','见面']),dict(id='甲',channel=None),dict(id='甲',channel=[]),dict(id='甲',channel=''),dict(id='甲',costume='雨衣',role='来访者')):
            p=proposal();p['scenes'][0]['participants']=[value]
            packet=prepare(empty(),p,1)
            self.assertEqual(packet['candidate_state']['event_log']['c0001.arrival']['participants'],['甲'])
        for value in ({},dict(id=''),dict(id=[])):
            p=proposal();p['scenes'][0]['participants']=[value]
            with self.assertRaises(ContractError) as caught:prepare(empty(),p,1)
            details=caught.exception.repair_details
            self.assertEqual(details['locator']['path'],'scenes[0].participants[0]')
            self.assertEqual(details['submitted_participant'],value)

    def test_real_id_only_participants_replay_without_inventing_people(self):
        saved=self.read(ROOT/'runs/event_first_50000_20261022_h/working/checkpoint_0009.json')
        plans=[t['proposal'] for t in saved['trace'] if t['role']=='event_simulation']
        self.assertEqual(len(plans),2)
        for plan in plans:
            original=copy.deepcopy(plan)
            packet=prepare(saved['book']['writing_state'],plan,3)
            self.assertEqual(plan,original)
            self.assertTrue(any(n.get('rule')=='program_owned_reference_binding' for n in packet['commit']['identifier_normalizations']))
            for scene in packet['commit']['scenes']:
                self.assertEqual(scene['participants'],['许闻','梁策'])

    def test_requirement_type_binding_is_unique_and_stale_versions_still_reject(self):
        state=prepare(empty(),proposal(),1)['candidate_state']
        b=beat(changes=[]);b['requires']=[dict(id='location')]
        packet=prepare(state,proposal([b],2),2)
        self.assertEqual(packet['commit']['scenes'][0]['beats'][0]['requires'],[dict(type='fact',id='location',revision=1)])
        b['requires'][0]['revision']=0
        with self.assertRaises(ContractError):prepare(state,proposal([b],2),2)
        state['objects']['location']=dict(id='location',revision=1)
        b['requires']=[dict(id='location')]
        with self.assertRaises(ContractError) as caught:prepare(state,proposal([b],2),2)
        self.assertEqual(set(caught.exception.repair_details['issues'][0]['expected_reference_types']),{'evidence_object','fact_record'})

    def test_real_composite_channel_does_not_block_a_correct_state_transition(self):
        saved=self.read(ROOT/'runs/event_first_50000_20261022_i/working/checkpoint_0017.json')
        plans=[t['proposal'] for t in saved['trace'] if t['role']=='event_simulation']
        self.assertEqual(len(plans),2)
        # First proposal really duplicates a known attribute; retain that check.
        with self.assertRaises(ContractError):prepare(saved['book']['writing_state'],plans[0],5)
        packet=prepare(saved['book']['writing_state'],plans[1],5)
        self.assertTrue(any(n.get('channel')=='短信/见面' and n['storage_id']=='梁策' for n in packet['commit']['identifier_normalizations']))
        prior=saved['book']['writing_state']['facts']['id_f177d783ac5f7e15da766f36586c7da8']
        changed=packet['candidate_state']['facts'][prior['id']]
        self.assertEqual(changed['revision'],prior['revision']+1)

    def test_shape_phase_reports_all_bad_fields_before_state_simulation(self):
        from memory_runtime.event_contract import ShapeError
        b=beat(changes=[dict(fact(),kind='unknown')]);b['requires']=[dict(id='location',revision='one',unexpected=True)]
        p=proposal([b]);state=empty()
        with self.assertRaises(ShapeError) as caught:prepare(state,p,1)
        paths=[r['path'] for r in caught.exception.repair_details['issues']]
        self.assertIn('scenes[0].beats[0].requires[0]',paths)
        self.assertIn('scenes[0].beats[0].changes[0].kind',paths)
        self.assertEqual(state,empty())

    def test_real_planned_fact_in_actual_conversation_projects_only_as_task(self):
        from memory_runtime.engine import MemoryEngine
        saved=self.read(ROOT/'runs/event_first_50000_20261022_j/working/checkpoint_0001.json')
        plans=[t['proposal'] for t in saved['trace'] if t['role']=='event_simulation']
        packet=prepare(empty(),plans[-1],1);c=packet['commit']
        planned=[r for r in c['memory_projection'] if r.get('proposed_record',{}).get('kind')=='planned']
        self.assertEqual(len(planned),1);row=planned[0]
        self.assertNotIn(row['proposed_record']['id'],packet['candidate_state']['facts'])
        template='\n\n'.join('[[event:'+b['token_id']+']]' for s in c['scenes'] for b in s['beats'])
        draft=realize(template,c);ch=dict(number=1,title='开始',text=draft,sha256=digest(draft),event_commit=c,realization_template=template)
        memory=project_memory(MemoryEngine.empty(),[ch],1,[])
        tasks=[r for r in memory['items'].values() if r['kind']=='task']
        self.assertEqual(len(tasks),1);self.assertEqual(tasks[0]['status'],'planned')
        self.assertEqual(memory['attribute_labels'][row['attribute']],'下一步行动')
        # Full first response still has a real identity mismatch, not a plan-format error.
        with self.assertRaises(ContractError) as caught:prepare(empty(),plans[0],1)
        self.assertTrue(any(i.get('learner')=='周敏' for i in caught.exception.repair_details['issues']))

    def test_derived_transition_and_handoff_fields_keep_explicit_conflict_checks(self):
        state=prepare(empty(),proposal(),1)['candidate_state']
        change=dict(type='transition',id='move',fact_id='location',to_value='门内')
        p=proposal([beat('move','甲进屋。',[change])],2)
        self.assertEqual(prepare(state,p,2)['candidate_state']['facts']['location']['value'],'门内')
        change['from_value']='别处'
        with self.assertRaises(ContractError):prepare(state,proposal([beat('move',changes=[change])],2),2)
        receipt=dict(type='handoff',id='receipt',signers=['甲'],non_signers=['乙'],attendees=['甲','乙'])
        world=prepare(empty(),proposal([beat(changes=[receipt])]),1)['candidate_state']
        self.assertEqual(world['handoffs']['receipt']['signer_count'],1)
        receipt['signer_count']=2
        with self.assertRaises(ContractError):prepare(empty(),proposal([beat(changes=[receipt])]),1)

    def test_statement_layout_and_scene_count_do_not_change_fact_admissibility(self):
        p=proposal();p['scenes']=[]
        for s in range(9):
            p['scenes'].append(dict(id=f's{s}',purpose='推进',participants=['甲'],beats=[beat(f'b{s}_{b}',f'甲记录第{s}组第{b}项。',[]) for b in range(6)]))
        p['scenes'][0]['beats'][0]['statement']='甲写下说明。\n\n'+'纸上的字迹很清楚。'*100
        packet=prepare(empty(),p,1);commit=packet['commit']
        template=''.join('[[event:'+b['token_id']+']]' for s in commit['scenes'] for b in s['beats'])
        self.assertIn(p['scenes'][0]['beats'][0]['statement'],realize(template,commit))
        self.assertEqual(len(packet['candidate_state']['event_log']),54)

    def test_repeat_pass_uses_explicit_explanation_instead_of_keyword_allowlist(self):
        prior=dict(type='progress',id='pages',pass_id='first',completed=17,total=17)
        state=prepare(empty(),proposal([beat(changes=[prior])]),1)['candidate_state']
        why='为排除透光造成的重影，逐页改用侧光比对。'
        next_pass=dict(type='progress',id='pages',pass_id='side_light',completed=1,total=17,restart_quote=why)
        packet=prepare(state,proposal([beat('check',why,[next_pass])],2),2)
        self.assertEqual(packet['candidate_state']['progress']['pages']['completed'],1)
        next_pass.pop('restart_quote')
        with self.assertRaises(ContractError):prepare(state,proposal([beat('check',why,[next_pass])],2),2)

    def test_total_resource_budget_is_reported_without_silent_truncation(self):
        from memory_runtime.event_contract import MAX_PLAN_BYTES
        p=proposal([beat(statement='说明。'*(MAX_PLAN_BYTES//3),changes=[])]);before=copy.deepcopy(p);state=empty()
        with self.assertRaises(ContractError) as caught:prepare(state,p,1)
        details=caught.exception.repair_details
        self.assertEqual(details['code'],'EVENT_PLAN_RESOURCE_LIMIT')
        self.assertGreater(details['actual_bytes'],details['limit_bytes'])
        self.assertEqual(p,before);self.assertEqual(state,empty())

    def test_shape_repair_and_state_replanning_have_separate_bounded_budgets(self):
        class RepairPhases(EventLocal):
            def __init__(self):super().__init__();self.plans=0
            def complete(self,req):
                if req.role!='planner':return super().complete(req)
                self.requests.append(copy.deepcopy(req));self.plans+=1
                if self.plans==1:
                    b=beat(changes=[dict(fact(),kind='unknown')]);b['requires']=[dict(id='missing',unexpected=True)]
                elif self.plans==2:
                    b=beat();b['requires']=[dict(id='missing')]
                else:b=beat()
                return ModelReply(canonical(proposal([b])),1,1,0)
        provider=RepairPhases();result=self.launch(provider,event_config(1))
        self.assertTrue(result['draft_completed'])
        planners=[r for r in provider.requests if r.role=='planner']
        self.assertEqual(len(planners),3)
        self.assertEqual(planners[1].payload['repair']['details']['code'],'EVENT_SHAPE_ERRORS')
        self.assertEqual(len(planners[1].payload['repair']['details']['issues']),2)
        self.assertIn('event_preflight_error',planners[2].payload)
        self.assertNotIn('repair',planners[2].payload)
        self.assertEqual(len([r for r in provider.requests if r.role=='writer' and 'current_draft' not in r.payload]),1)

    def test_real_memory_ids_bind_to_plan_and_fact_without_promoting_the_plan(self):
        from memory_runtime.event_references import catalogue
        saved=self.read(ROOT/'runs/event_first_50000_20261022_k/working/checkpoint_0005.json')
        refs=catalogue(saved['book']);plans=[t['proposal'] for t in saved['trace'] if t['role']=='event_simulation']
        mid='m_89bc0cee02565032483d9468';binding=refs['memory'][mid]
        self.assertEqual(binding['type'],'plan')
        packet=prepare(saved['book']['writing_state'],plans[-1],2,references=refs)
        self.assertNotIn(binding['id'],packet['candidate_state']['facts'])
        requirements=[r for s in packet['commit']['scenes'] for b in s['beats'] for r in b['requires']]
        self.assertTrue(any(r['type']=='plan' and r['id']==binding['id'] for r in requirements))
        # Legacy type hints do not own identity; the actual record stays an intention.
        first=prepare(saved['book']['writing_state'],plans[0],2,references=refs)
        self.assertNotIn(binding['id'],first['candidate_state']['facts'])
        self.assertTrue(any(r['type']=='plan' and r['id']==binding['id'] for s in first['commit']['scenes'] for b in s['beats'] for r in b['requires']))

    def test_memory_view_revision_is_not_the_canonical_fact_revision(self):
        from memory_runtime.engine import MemoryEngine
        from memory_runtime.event_references import catalogue
        packet=prepare(empty(),proposal(),1);commit=packet['commit'];draft=realize('[[event:arrival]]',commit)
        chapter=dict(number=1,title='登记',text=draft,sha256=digest(draft),event_commit=commit,realization_template='[[event:arrival]]')
        memory=project_memory(MemoryEngine.empty(),[chapter],1,[])
        item=next(r for r in memory['items'].values() if r['kind']=='state');item['revision']+=3
        book=dict(chapters=[chapter],memory=memory);refs=catalogue(book)
        req=dict(id=item['id'],revision=item['revision']);b=beat('next',changes=[]);b['requires']=[req]
        result=prepare(packet['candidate_state'],proposal([b],2),2,references=refs)
        self.assertEqual(result['commit']['scenes'][0]['beats'][0]['requires'],[dict(id='location',type='fact',revision=1)])
        current=copy.deepcopy(packet['candidate_state']);current['facts']['location']['revision']=2
        with self.assertRaises(ContractError):prepare(current,proposal([b],2),2,references=refs)
        req.pop('revision')
        result=prepare(current,proposal([b],2),2,references=refs)
        self.assertEqual(result['commit']['scenes'][0]['beats'][0]['requires'][0]['revision'],2)

    def test_planner_sees_canonical_references_and_future_occurrence_stays_invalid(self):
        provider=EventLocal();result=self.launch(provider,event_config(2))
        self.assertTrue(result['draft_completed'])
        context=next(r.payload for r in provider.requests if r.role=='planner' and r.payload['chapter_number']==2)
        fact_view=next(f for f in context['retrieved_memory'] if f['memory_kind']=='state_summary')
        self.assertEqual(fact_view['state_record_reference'],dict(record_kind='fact_record',record_id='location',record_revision=1))
        planned=beat('later',changes=[]);planned['mode']='planned'
        state=prepare(empty(),proposal([planned]),1)['candidate_state']
        now=beat('now',changes=[]);now['requires']=[dict(type='occurrence',id='c0001.later')]
        with self.assertRaises(ContractError):prepare(state,proposal([now],2),2)

    def test_real_object_provenance_and_knowledge_replay_without_inventing_history(self):
        from memory_runtime.event_references import catalogue
        saved=self.read(ROOT/'runs/event_first_50000_20261022_l/working/checkpoint_0025.json')
        plans=[t['proposal'] for t in saved['trace'] if t['role']=='event_simulation']
        packet=prepare(saved['book']['writing_state'],plans[-1],7,references=catalogue(saved['book']))
        world=packet['candidate_state']
        self.assertEqual(world['objects']['obj_song_package']['origin_description'],'宋常青九八年底寄存于赵姓妇人家中，未拆动')
        self.assertIsNone(world['objects']['obj_song_package']['origin'])
        self.assertEqual(world['events'],saved['book']['writing_state']['events'])
        for kid,oid in (('learn_xu_package_receive','obj_song_package'),('learn_xu_third_copy','obj_third_copy'),('learn_xu_note_found','obj_song_note')):
            learned=world['knowledge'][kid]
            self.assertEqual(learned['reference_type'],'object')
            self.assertEqual(learned['value']['id'],oid)
            self.assertEqual(learned['fact_revision'],world['objects'][oid]['revision'])
        with self.assertRaises(ContractError):prepare(saved['book']['writing_state'],plans[0],7,references=catalogue(saved['book']))

    def test_explicit_origin_is_checked_and_same_chapter_full_event_id_is_bound(self):
        obj=dict(type='object',id='paper',label='纸',form='original',status='available',origin_event='c0001.arrival')
        state=prepare(empty(),proposal([beat(changes=[obj])]),1)['candidate_state']
        self.assertEqual(state['objects']['paper']['origin'],'c0001.arrival')
        for origin in ('unknown_event','不存在的历史事件','c0001.future'):
            obj['origin_event']=origin
            with self.assertRaises(ContractError):prepare(empty(),proposal([beat(changes=[obj])]),1)
        obj.pop('origin_event');obj['origin_description']='据说从旧巷搬来，尚待查证'
        state=prepare(empty(),proposal([beat(changes=[obj])]),1)['candidate_state']
        self.assertIsNone(state['objects']['paper']['origin'])
        self.assertEqual(state['objects']['paper']['origin_description'],obj['origin_description'])

    def test_old_source_event_cannot_convey_a_later_fact_revision(self):
        first=prepare(empty(),proposal([beat('old','甲看见灯亮。',[dict(fact('亮'),id='lamp',subject='灯',attribute='status')])]),1)['candidate_state']
        change=dict(type='transition',id='switch',fact_id='lamp',to_value='灭')
        state=prepare(first,proposal([beat('dark','灯灭了。',[change])],2),2)['candidate_state']
        heard=dict(type='learn',id='heard',actor='甲',fact_id='lamp',via_event='c0001.old')
        with self.assertRaises(ContractError):prepare(state,proposal([beat('now','甲看向灯。',[heard])],3),3)
        heard['via_event']='now'
        result=prepare(state,proposal([beat('now','甲看见灯灭了。',[heard])],3),3)['candidate_state']
        self.assertEqual(result['knowledge']['heard']['value'],'灭')
        self.assertEqual(result['knowledge']['heard']['fact_revision'],2)

    def test_generic_knowledge_references_require_unique_ids_and_preserve_belief(self):
        obj=dict(type='object',id='record',label='纸',form='original',status='available',origin=None)
        state=prepare(empty(),proposal([beat('create',changes=[obj,dict(fact(kind='belief'),id='record')])]),1)['candidate_state']
        heard=dict(type='learn',id='heard',actor='甲',fact_id='record',via_event='hear')
        with self.assertRaises(ContractError):prepare(state,proposal([beat('hear',changes=[heard])],2),2)
        heard['reference_type']='fact'
        world=prepare(state,proposal([beat('hear',changes=[heard])],2),2)['candidate_state']
        self.assertEqual(world['knowledge']['heard']['epistemic_status'],'belief')

    def test_real_literal_event_prose_is_preserved_and_missing_event_stays_rejected(self):
        from memory_runtime.event_first import compile_realization
        saved=self.read(ROOT/'runs/event_first_50000_20261022_m/working/checkpoint_0006.json')
        commit=saved['book']['prepared_events']['2']['commit']
        replies=[json.loads(t['raw_output'])['text'] for t in saved['trace'] if t.get('role')=='writer']
        self.assertEqual(len(replies),2)
        compiled=compile_realization(replies[0],commit)
        self.assertEqual(realize(compiled,commit),replies[0])
        self.assertEqual(realize(replies[0],commit),replies[0])
        with self.assertRaises(ContractError) as caught:realize(replies[1],commit)
        self.assertIn('slot_002',caught.exception.repair_details['missing_events'])

    def test_literal_and_token_anchors_require_unique_complete_ordered_coverage(self):
        from memory_runtime.event_first import compile_realization
        c=prepare(empty(),proposal([beat('one','甲走到门前。',[]),beat('two','甲打开门。',[])]),1)['commit']
        self.assertEqual(realize('雨停了。甲走到门前。\n\n[[event:slot_002]]',c),'雨停了。甲走到门前。\n\n甲打开门。')
        for text in ('甲打开门。甲走到门前。','甲走到门前。甲走到门前。甲打开门。',
            '[[event:slot_001]]雨停了。甲走到门前。[[event:slot_002]]','甲走到了门前。甲打开门。'):
            with self.assertRaises(ContractError):compile_realization(text,c)

    def test_unique_adjacent_marker_annotations_compile_without_dropping_prose(self):
        c=prepare(empty(),proposal([beat('one','甲走到门前。',[]),beat('two','甲打开门。',[])]),1)['commit']
        for annotated in ('[[event:slot_001]]甲走到门前。','甲走到门前。\n\n[[event:slot_001]]'):
            raw='雨停了。'+annotated+'\n风吹过。[[event:slot_002]]'
            self.assertEqual(realize(raw,c),'雨停了。甲走到门前。\n风吹过。甲打开门。')
        for bad in ('[[event:slot_001]][[event:slot_001]]甲走到门前。[[event:slot_002]]',
            '[[event:slot_001]]甲走到门前。甲走到门前。[[event:slot_002]]',
            '[[event:slot_001]]甲走到了门前。[[event:slot_002]]甲走到门前。'):
            with self.assertRaises(ContractError):realize(bad,c)
        record=self.read(max((ROOT/'runs/event_first_50000_20261022_s/working').glob('checkpoint_*.json')))
        commit=record['book']['prepared_events']['2']['commit']
        replies=[json.loads(r['raw_output'])['text'] for r in record['trace'] if r.get('role')=='writer']
        self.assertEqual(len(replies),2)
        for raw in replies:
            prose=realize(raw,commit)
            for scene in commit['scenes']:
                for b in scene['beats']:self.assertEqual(prose.count(b['statement']),1)
            self.assertNotIn('[[event:',prose)
        def paired_writer(payload):
            return dict(text='雨停了。\n'+''.join('[[event:'+b['id']+']]\n\n'+b['statement'] for s in payload['frozen_events']['scenes'] for b in s['beats']))
        result=self.launch(EventLocal(writer=paired_writer),event_config(2,False))
        self.assertTrue(result['draft_completed']);self.assertTrue(result['memory_complete'])
        book=self.read(self.root/'run/final_state.json')
        for chapter in book['chapters']:
            self.assertEqual(realize(chapter['realization_template'],chapter['event_commit']),chapter['text'])

    def test_literal_calculated_anchor_does_not_hide_invented_free_prose_math(self):
        p=proposal([beat(statement='传真[[time:fax.start]]发出，[[time:fax.end]]收到，相隔[[time:fax]]。',changes=[])])
        p['time_calculations']=[dict(id='fax',kind='interval',start='16:41',end='16:45')]
        c=prepare(empty(),p,1)['commit'];literal='传真16:41发出，16:45收到，相隔四分钟。'
        self.assertEqual(realize(literal,c),literal)
        with self.assertRaises(ContractError):realize(literal+'中间隔了两分钟。',c)

    def test_literal_prose_is_preserved_before_atomic_save_and_memory_projection(self):
        def literal_writer(p):
            return dict(text='雨停了。\n\n'+''.join(b['statement'] for s in p['frozen_events']['scenes'] for b in s['beats']))
        result=self.launch(EventLocal(writer=literal_writer),event_config(2))
        self.assertTrue(result['draft_completed']);self.assertTrue(result['memory_complete'])
        book=self.read(self.root/'run/final_state.json')
        for c in book['chapters']:
            self.assertEqual(c['prose_policy'],'unchecked')
            self.assertEqual(c['realization_template'],c['text'])

    def test_real_transition_operation_ids_are_generated_without_changing_record_ids(self):
        from memory_runtime.event_references import catalogue
        saved=self.read(ROOT/'runs/event_first_50000_20261022_n/working/checkpoint_0005.json')
        plans=[json.loads(t['raw_output']) for t in saved['trace'] if t.get('role')=='planner' and t.get('status')=='FORMAT_FAILED']
        self.assertEqual(len(plans),2)
        for p in plans:
            before=copy.deepcopy(p)
            packet=prepare(saved['book']['writing_state'],p,2,references=catalogue(saved['book']))
            self.assertTrue(any(n.get('rule')=='generated_operation_id' for n in packet['commit']['identifier_normalizations']))
            self.assertEqual(p,before)
            for scene in packet['commit']['scenes']:
                for b in scene['beats']:
                    for c in b['changes']:
                        if c['type']=='transition':self.assertIn(c['fact_id'],saved['book']['writing_state']['facts'])
            self.assertEqual(packet['commit'],prepare(saved['book']['writing_state'],p,2,references=catalogue(saved['book']))['commit'])


if __name__=='__main__':unittest.main(verbosity=2)
