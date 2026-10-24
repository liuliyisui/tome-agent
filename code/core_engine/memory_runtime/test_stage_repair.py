"""Five-output budget, original failures, constrained repair and stage durability."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import write_novel as cli
from inf_writer.domain import ContractError,canonical,digest
from inf_writer.models import ModelReply
from memory_runtime.continuity import empty
from memory_runtime.event_first import prepare,verify
from memory_runtime.event_references import catalogue
from memory_runtime.reference_choices import compile_plan
from memory_runtime.stage_planning import prepare_stages
from memory_runtime.test_event_first import EventLocal,event_config,proposal,beat,fact
from memory_runtime.writing import WritingSession,load_resume


def public_plan():
    return dict(number=1,title='来信',brief='登记来信',future_updates=[],scenes=[dict(purpose='登记',participants=['甲'],beats=[dict(statement='甲在门外。',assertion_scope='performed_action',requires=[],changes=[dict(operation='establish_fact',subject='甲',property_name='location',value='门外',fact_class='current_state')])])])


class Formal(EventLocal):
    def complete(self,request):
        if request.role=='planner':
            self.requests.append(copy.deepcopy(request));return ModelReply(canonical(public_plan()),1,1,0)
        return super().complete(request)


class StageRepairTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=cli.ROOT/'runs');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def session(self,provider,name='session',book=None):return WritingSession(self.root/name,provider,cli.validate_config(event_config(1)),book=book)

    def test_fifth_planner_output_can_succeed_and_budget_is_persisted(self):
        class Fifth(Formal):
            def __init__(self):super().__init__();self.count=0
            def complete(self,request):
                if request.role=='planner':
                    self.count+=1
                    if self.count<5:
                        self.requests.append(copy.deepcopy(request));return ModelReply('{}',1,1,0)
                return super().complete(request)
        gateway=Fifth();session=self.session(gateway);row=session.write_next('继续')
        self.assertIsNone(row['stop_reason']);self.assertEqual(gateway.count,5)
        self.assertEqual(session.book['planning_attempts']['1'],5)
        self.assertEqual(session.book['writing_state']['facts']['n0001r0001']['value'],'门外')

    def test_separate_repair_agent_fixes_only_failed_action_after_five_plans(self):
        class Fix(Formal):
            def complete(self,request):
                if request.role=='planner':
                    self.requests.append(copy.deepcopy(request));raw=public_plan();raw['scenes'][0]['beats'][0]['requires']=[dict(record_choice=999)]
                    return ModelReply(canonical(raw),1,1,0)
                if request.role=='state_repair':
                    self.requests.append(copy.deepcopy(request))
                    return ModelReply(canonical(dict(patches=[dict(scene_index=0,beat_index=0,replacement=public_plan()['scenes'][0]['beats'][0])])),1,1,0)
                return super().complete(request)
        gateway=Fix();session=self.session(gateway);row=session.write_next('继续')
        self.assertIsNone(row['stop_reason']);self.assertEqual(len([r for r in gateway.requests if r.role=='planner']),5)
        self.assertEqual(len([r for r in gateway.requests if r.role=='state_repair']),1)
        self.assertEqual(session.book['writing_state']['facts']['n0001r0001']['value'],'门外')

    def test_repair_cannot_replace_an_unrelated_action(self):
        from memory_runtime.plan_repair import repair
        class Wrong:
            def complete(self,request):return ModelReply(canonical(dict(patches=[dict(scene_index=0,beat_index=0,replacement={})])),1,1,0)
        with self.assertRaises(ContractError):repair(Wrong(),public_plan(),[],dict(path='scenes[0].beats[1].requires[0]'),[])

    def test_original_ar_intention_failure_now_passes_without_manual_scope_change(self):
        folder=cli.ROOT/'runs/event_first_50000_20261022_ar'
        raw=json.loads(json.loads((folder/'call_045.response.json').read_text(encoding='utf-8'))['content'])
        request=json.loads((folder/'call_045.request.json').read_text(encoding='utf-8'))
        book=None
        for path in sorted((folder/'working').glob('checkpoint_*.json')):
            record=json.loads(path.read_text(encoding='utf-8'))
            if record['reason']=='MEMORY_COMMITTED' and len(record['book']['chapters'])==10:book=record['book'];break
        original=copy.deepcopy(raw);compiled=compile_plan(raw,request['payload']['reference_choices'],11)
        packet=prepare(book['writing_state'],compiled,11,references=catalogue(book))
        self.assertEqual(raw,original)
        intentions=[r['proposed_record']['id'] for r in packet['commit']['memory_projection'] if r.get('proposed_record')]
        self.assertIn('n0011r0005',intentions)

    def test_local_selector_for_proposed_effect_binds_intention_not_completed_fact(self):
        raw=public_plan();first=raw['scenes'][0]['beats'][0];first['assertion_scope']='proposed_action'
        next_action=dict(statement='甲记下这项待办，尚未执行。',assertion_scope='performed_action',
            requires=[dict(record_position=[1,1,1])],changes=[])
        raw['scenes'][0]['beats'].append(next_action)
        compiled=compile_plan(raw,[],1)
        self.assertEqual(compiled['scenes'][0]['beats'][1]['requires'][0]['reference_id'],'pending_intention:n0001r0001')
        packet=prepare(empty(),compiled,1)
        self.assertEqual(packet['candidate_state']['facts'],{})
        self.assertEqual(packet['commit']['scenes'][0]['beats'][1]['requires'][0]['type'],'plan')

    def test_bad_middle_stage_defers_dependencies_but_keeps_independent_later_stage(self):
        a=beat('first',changes=[dict(fact(),id='one')]);b=beat('bad',changes=[dict(fact(),id='two',subject='乙')]);b['requires']=[dict(id='missing')]
        dependent=beat('dependent',changes=[]);dependent['requires']=[dict(type='fact',id='two')]
        c=beat('last',changes=[dict(fact(),id='three',subject='丙')])
        raw=proposal([a]);raw['scenes']=[dict(id=f's{i}',purpose='阶段',participants=['甲'],beats=[v]) for i,v in enumerate((a,b,dependent,c),1)]
        packet=prepare_stages(empty(),raw,1,{})
        self.assertEqual(set(packet['candidate_state']['facts']),{'one','three'})
        self.assertEqual([r['status'] for r in packet['stage_reports']],['PREPARED','DEFERRED','DEFERRED','PREPARED'])
        verify(packet['commit'])
        self.assertEqual(packet['commit']['event_plan_status'],'partial')

    def test_completed_stage_prose_survives_interruption_and_is_not_generated_twice(self):
        raw=proposal();raw['scenes'].append(dict(id='second',purpose='后续',participants=['甲'],beats=[beat('later','甲给来信盖了章。',[])]))
        packet=prepare_stages(empty(),raw,1,{})
        class Interrupted(EventLocal):
            def complete(self,request):
                if request.role=='writer' and len([r for r in self.requests if r.role=='writer'])==1:raise KeyboardInterrupt()
                return super().complete(request)
        gateway=Interrupted();session=self.session(gateway);session.book['prepared_events']['1']=copy.deepcopy(packet)
        with self.assertRaises(KeyboardInterrupt):session.write_next('继续')
        self.assertEqual(session.book['chapters'],[])
        self.assertEqual(len(session.book['prepared_events']['1']['stage_realizations']),1)
        book=load_resume(session.latest_checkpoint,session.plan)
        replacement=EventLocal();resumed=self.session(replacement,'resumed',book)
        row=resumed.write_next('继续')
        self.assertIsNone(row['stop_reason'])
        self.assertEqual(len([r for r in replacement.requests if r.role=='writer']),1)
        self.assertEqual(len(resumed.book['chapters'][0]['event_stage_sources']),2)
        load_resume(resumed.latest_checkpoint,resumed.plan)

    def test_tampered_stage_chain_rejected_even_if_outer_hash_is_recomputed(self):
        raw=proposal();packet=prepare_stages(empty(),raw,1,{})
        commit=copy.deepcopy(packet['commit']);commit['stage_transactions'][0]['state_sha256']='wrong'
        commit['sha256']=digest(canonical({k:v for k,v in commit.items() if k!='sha256'}))
        with self.assertRaises(ContractError):verify(commit)

    def test_formal_launcher_keeps_valid_stages_when_one_selector_remains_bad(self):
        class PartlyBad(Formal):
            def complete(self,request):
                if request.role=='planner':
                    self.requests.append(copy.deepcopy(request));raw=public_plan()
                    bad=copy.deepcopy(raw['scenes'][0]);bad['beats'][0]['requires']=[dict(record_choice=999)]
                    bad['beats'][0]['changes'][0]['subject']='乙'
                    last=copy.deepcopy(raw['scenes'][0]);last['beats'][0]['statement']='丙在门外。';last['beats'][0]['changes'][0]['subject']='丙'
                    raw['scenes']+=[bad,last]
                    return ModelReply(canonical(raw),1,1,0)
                return super().complete(request)
        gateway=PartlyBad();session=self.session(gateway);row=session.write_next('继续')
        self.assertIsNone(row['stop_reason']);self.assertEqual(session.book['planning_attempts']['1'],5)
        self.assertEqual(set(session.book['writing_state']['facts']),{'n0001r0001','n0001r0003'})
        chapter=session.book['chapters'][0]
        self.assertEqual(chapter['event_plan_status'],'partial');self.assertEqual(len(chapter['event_stage_sources']),2)
        self.assertEqual([r['stage'] for r in row['deferred_event_stages']],[1])
        self.assertEqual(session.book['state_repair_jobs']['1']['chapter_sha256'],chapter['sha256'])
        load_resume(session.latest_checkpoint,session.plan)


if __name__=='__main__':unittest.main()
