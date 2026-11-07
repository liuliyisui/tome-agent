"""Real failed-plan replay, wrong-target rejection and append-only recovery."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import write_novel as cli
from inf_writer.domain import ContractError,canonical,digest
from inf_writer.models import ModelReply
from memory_runtime.writing import WritingSession,load_resume
from memory_runtime.state_recovery import verify_recoveries,directory,_packet
from memory_runtime.reference_choices import compile_plan
from memory_runtime.plan_repair import protect_targets
from memory_runtime.test_stage_repair import Formal,public_plan

ROOT=cli.ROOT
RUN=ROOT/'runs/narrative_3000_20261025_b'


class Recovery(Formal):
    def __init__(self,invalid=False):super().__init__();self.invalid=invalid
    def complete(self,r):
        if r.role=='state_repair' and 'evidence' in r.payload:
            self.requests.append(copy.deepcopy(r));evidence=r.payload['evidence']
            source=next(s for s in evidence if '便条是我写的' in s['text'])
            row=dict(evidence_position=source['evidence_position'],quote=source['text'],changes=[dict(
                operation='establish_fact',subject='组长',property_name='对便条来源的承认',
                value='承认便条出自其手，并想让卷随待销毁批次出库',fact_class='character_belief')])
            if self.invalid:row['quote']='正文从未出现的句子'
            return ModelReply(canonical(dict(participants=['许闻','梁策','组长','副站长'],actions=[row])),1,1,0)
        if r.role=='planner':
            self.requests.append(copy.deepcopy(r));value=public_plan();value['number']=r.payload['chapter_number']
            return ModelReply(canonical(value),1,1,0)
        return super().complete(r)


class StateRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'runs');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.book=json.loads((RUN/'final_state.json').read_text(encoding='utf-8'))
        self.plan=cli.validate_config(json.loads((RUN/'config.json').read_text(encoding='utf-8')))
    def session(self,gateway):return WritingSession(self.root/'session',gateway,self.plan,book=self.book)

    def test_original_repair_cannot_move_batch_update_to_person_attitude(self):
        request=json.loads((RUN/'call_023.request.json').read_text(encoding='utf-8'))['payload']
        patch=json.loads(json.loads((RUN/'call_023.response.json').read_text(encoding='utf-8'))['content'])['patches'][0]
        original=request['proposal']['scenes'][0]['beats'][6]
        records=json.loads((RUN/'call_022.request.json').read_text(encoding='utf-8'))['payload']['event_plan_state']['records']
        with self.assertRaises(ContractError):protect_targets(original,patch['replacement'],request['reference_choices'],records)

    def test_reference_metadata_is_checked_without_changing_selector_identity(self):
        plan=public_plan();plan['scenes'][0]['beats'][0]['changes']=[dict(operation='change_fact_value',
            fact_ref=dict(record_choice=1,record_kind='fact_record',record_subject='甲'),new_value='门内')]
        choices=['fact_record:location'];records=[dict(reference_id=choices[0],subject='甲')]
        result=compile_plan(plan,choices,1,reference_records=records)
        self.assertEqual(result['scenes'][0]['beats'][0]['changes'][0]['fact_ref'],choices[0])
        for key,value in (('record_kind','pending_intention'),('record_subject','乙')):
            bad=copy.deepcopy(plan);bad['scenes'][0]['beats'][0]['changes'][0]['fact_ref'][key]=value
            with self.assertRaises(ContractError):compile_plan(bad,choices,1,reference_records=records)

    def test_original_local_repair_retries_wrong_subject_and_accepts_correct_intention_operation(self):
        from memory_runtime.plan_repair import repair
        from memory_runtime.event_first import prepare
        from memory_runtime.event_references import catalogue
        request=json.loads((RUN/'call_023.request.json').read_text(encoding='utf-8'))['payload']
        bad=json.loads(json.loads((RUN/'call_023.response.json').read_text(encoding='utf-8'))['content'])
        records=json.loads((RUN/'call_022.request.json').read_text(encoding='utf-8'))['payload']['event_plan_state']['records']
        original=request['proposal'];correct=copy.deepcopy(original['scenes'][0]['beats'][6])
        correct['changes'][0]=dict(operation='revise_intention',intention_ref=dict(record_choice=14),new_value='原出库计划暂停，转入重新登记复核')
        correct['changes'].append(dict(operation='establish_fact',subject='待销毁旧档批次',property_name='当前出库处置',
            value='暂停出库销毁，转入重新登记复核',fact_class='current_state'))
        good=dict(patches=[dict(scene_index=0,beat_index=6,replacement=correct)])
        class Replies:
            def __init__(self):self.requests=[]
            def complete(self,r):
                self.requests.append(copy.deepcopy(r));return ModelReply(canonical(bad if len(self.requests)==1 else good),1,1,0)
        gateway=Replies();trace=[]
        def validate(value):
            compiled=compile_plan(value,request['reference_choices'],3,reference_records=records)
            return prepare(self.book['writing_state'],compiled,3,references=catalogue(self.book))
        fixed=repair(gateway,original,request['reference_choices'],request['errors'],trace,reference_records=records,validator=validate)
        self.assertEqual(len(gateway.requests),2)
        self.assertIn('another subject',gateway.requests[1].payload['repair_feedback']['error'])
        self.assertEqual(fixed['scenes'][0]['beats'][6]['changes'][0]['operation'],'revise_intention')
        packet=validate(fixed)
        self.assertEqual(self.book['writing_state']['facts']['n0002r0008']['value'],
            packet['candidate_state']['facts']['n0002r0008']['value'])
        self.assertTrue(any(r.get('subject')=='待销毁旧档批次'for r in packet['candidate_state']['facts'].values()))

    def test_recovery_preserves_prose_and_original_commit_projects_memory_and_restores(self):
        gateway=Recovery();session=self.session(gateway);old=copy.deepcopy(session.book)
        self.assertTrue(session.attempt_state_repair(force=True))
        book=session.book;self.assertFalse(book['state_repair_jobs'])
        self.assertEqual([c['text']for c in book['chapters']],[c['text']for c in old['chapters']])
        self.assertEqual(book['chapters'][2]['event_commit'],old['chapters'][2]['event_commit'])
        self.assertEqual(book['chapters'][2]['state_recovery_status'],'reconciled')
        self.assertEqual(len(book['state_recovery_commits']),1)
        self.assertTrue(verify_recoveries(book) is None)
        self.assertTrue(any(r['subject']=='组长' and '便条是我写的' in r['claim']for r in book['memory']['items'].values()))
        self.assertEqual(load_resume(session.latest_checkpoint,self.plan),book)
        recovery_request=next(r for r in gateway.requests if r.role=='state_repair')
        self.assertNotIn('proposal',recovery_request.payload)
        self.assertNotIn('deferred_stages',recovery_request.payload)
        self.assertEqual(session.context('继续','便条')['unprojected_chapters'],[])

    def test_next_chapter_extends_recovered_chain_without_rewriting_original_chapters(self):
        gateway=Recovery();session=self.session(gateway);self.assertTrue(session.attempt_state_repair(force=True))
        prefix=[c['text']for c in session.book['chapters']]
        row=session.write_next('补写一次交接')
        self.assertIsNone(row['stop_reason'])
        self.assertEqual([c['text']for c in session.book['chapters'][:3]],prefix)
        self.assertEqual(load_resume(session.latest_checkpoint,self.plan),session.book)

    def test_invalid_recovery_keeps_pending_job_and_does_not_publish_partial_state(self):
        gateway=Recovery(invalid=True);session=self.session(gateway)
        before=copy.deepcopy(session.book)
        self.assertFalse(session.attempt_state_repair())
        self.assertEqual(session.book['writing_state'],before['writing_state'])
        self.assertEqual(session.book['memory'],before['memory'])
        self.assertTrue(session.book['state_repair_jobs']);calls=len(gateway.requests)
        self.assertFalse(session.attempt_state_repair());self.assertEqual(len(gateway.requests),calls)
        load_resume(session.latest_checkpoint,self.plan)

    def test_tampered_recovered_prose_binding_rejected_on_resume(self):
        session=self.session(Recovery());self.assertTrue(session.attempt_state_repair(force=True))
        record=json.loads(session.latest_checkpoint.read_text(encoding='utf-8'))
        record['book']['state_recovery_commits'][0]['bindings'][0]['quote']='伪造引文'
        record['book_sha256']=digest(canonical(record['book']))
        path=self.root/'corrupt.json';path.write_text(canonical(record),encoding='utf-8')
        with self.assertRaises(ContractError):load_resume(path,self.plan)

    def test_nested_selector_cannot_bypass_newer_state_protection(self):
        records,choices=directory(self.book,'许闻')
        fact=next(r for r in records if r['record_kind']=='fact_record')
        fact['chapter']=4;choice=choices.index(fact['reference_id'])+1
        from inf_writer.domain import evidence_segments
        source=evidence_segments(self.book['chapters'][2]['text'])[0]
        value=dict(participants=['许闻'],actions=[dict(evidence_position=1,quote=source['text'],changes=[dict(
            operation='change_fact_value',fact_ref=dict(record_subject=fact['subject'],record_property_name=fact['property_name'],ref=dict(record_choice=choice)),new_value='旧章值')])])
        with self.assertRaises(ContractError):_packet(self.book,3,value,records,choices,1)


if __name__=='__main__':unittest.main()
