"""Public contract compilation and actual prose storage across all three tiers."""
import copy
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from memory_runtime.test_event_first import ROOT,proposal,beat
import write_novel as cli
from inf_writer.domain import ContractError,canonical,digest
from inf_writer.models import ModelReply
from memory_runtime.continuity import empty
from memory_runtime.engine import MemoryEngine
from memory_runtime.event_contract import planner_catalogue,validate_plan_shape,RECORDS
from memory_runtime.event_first import normalize_plan,prepare,project_memory
from memory_runtime.event_references import catalogue,public_state_view
from memory_runtime.interface_contract import OPERATIONS,validate_catalogue_names,public_repair_details
from memory_runtime.prose_memory import excerpts,verify_prose_coverage
from memory_runtime.pipeline import LayerAgent


class InterfaceAndMemoryRepair(unittest.TestCase):
    def read(self,path):return json.loads(path.read_text(encoding='utf-8'))

    def test_formal_ingress_cannot_select_legacy_by_adding_fields(self):
        from memory_runtime.reference_choices import compile_plan
        from memory_runtime.test_event_first import event_config
        raw=dict(number=1,title='记录',brief='记录',future_updates=[],scenes=[dict(purpose='登记',participants=['甲'],beats=[dict(statement='甲记录。',assertion_scope='performed_action',requires=[],changes=[])])])
        for scope,key,value in (('plan','reference_protocol','legacy_v2'),('scene','id','invented'),('action','id','invented')):
            bad=copy.deepcopy(raw);owner=bad if scope=='plan' else bad['scenes'][0] if scope=='scene' else bad['scenes'][0]['beats'][0]
            owner[key]=value
            with self.assertRaises(ContractError):compile_plan(bad,[],1)
        import inspect
        self.assertNotIn('strict',inspect.signature(compile_plan).parameters)
        with self.assertRaises(ContractError):cli.validate_config(dict(event_config(1),reference_protocol='legacy_v2'))
        self.assertFalse((ROOT/'memory_runtime/legacy_protocol.py').exists())

    def test_formal_semantic_retry_receives_public_source_not_compiled_ids(self):
        from memory_runtime.test_event_first import EventLocal,event_config
        class FormalRepair(EventLocal):
            def __init__(self):super().__init__();self.attempts=0;self.first=None
            def complete(self,request):
                if request.role!='planner':return super().complete(request)
                self.requests.append(copy.deepcopy(request));self.number=1;self.attempts+=1
                if self.attempts==2:
                    assert request.payload['event_preflight_error']['previous_plan']==self.first
                    assert 'id' not in request.payload['event_preflight_error']['previous_plan']['scenes'][0]
                value=dict(number=1,title='记录',brief='记录',future_updates=[],scenes=[dict(purpose='登记',participants=['甲'],beats=[dict(statement='甲看到信在门口。',assertion_scope='reported_claim' if self.attempts==1 else 'performed_action',requires=[],changes=[dict(operation='establish_fact',subject='信',property_name='位置',value='门口',fact_class='current_state')])])])
                if self.first is None:self.first=copy.deepcopy(value)
                return ModelReply(canonical(value),1,1,0)
        provider=FormalRepair()
        with tempfile.TemporaryDirectory(dir=ROOT/'runs') as directory:
            with patch.object(cli,'read_secret',return_value='offline'),patch.object(cli,'ChatCompletionProvider',return_value=provider),contextlib.redirect_stdout(io.StringIO()):result=cli.launch(event_config(1,False),Path(directory)/'run')
            self.assertTrue(result['draft_completed']);self.assertTrue(result['memory_complete']);self.assertEqual(provider.attempts,2)

    def test_runtime_has_no_import_of_archive_test_adapter(self):
        import ast
        for path in (ROOT/'memory_runtime').rglob('*.py'):
            if path.name.startswith('test_'):continue
            tree=ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom):self.assertFalse((node.module or '').startswith('tools.testing'),str(path))

    def test_an_reference_wrappers_select_only_supplied_records(self):
        from memory_runtime.reference_choices import compile_plan
        from memory_runtime.continuity import context_view
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_an/working').glob('checkpoint_*.json')))
        book=saved['book'];refs=catalogue(book)
        choices=list(dict.fromkeys(r['reference_id'] for r in public_state_view(context_view(book['writing_state'],'',plans=refs['plans']))['records']))
        replies=[json.loads(t['raw_output']) for t in saved['trace'] if t.get('role')=='planner' and 'raw_output' in t]
        self.assertEqual(len(replies),2)
        for raw in replies:
            original=copy.deepcopy(raw)
            self.assertTrue(prepare(book['writing_state'],compile_plan(raw,choices,5),5,references=refs)['candidate_state'])
            self.assertEqual(raw,original)

    def test_unknown_reference_wrappers_have_a_precise_location_and_never_guess(self):
        from memory_runtime.reference_choices import compile_plan
        for value in (dict(ref='fact_record:fake'),dict(ref='fact_record:real',record_choice=1),dict(unexpected='fact_record:real')):
            raw=dict(number=1,title='测试',brief='测试',future_updates=[],scenes=[dict(purpose='测试',participants=['甲'],beats=[dict(statement='甲登记。',assertion_scope='performed_action',requires=[value],changes=[])])])
            with self.assertRaises(ContractError) as caught:compile_plan(raw,['fact_record:real'],1)
            self.assertEqual(caught.exception.repair_details['path'],'scenes[0].beats[0].requires[0]')

    def test_observation_choices_only_bind_real_object_records(self):
        from memory_runtime.reference_choices import compile_plan
        base=prepare(empty(),proposal([beat(changes=[dict(type='fact',id='f',subject='照片',attribute='用途',value='核对',kind='state'),dict(type='object',id='photo',label='照片',form='photo',status='available',origin=None)])]),1)['candidate_state']
        choices=['fact_record:f','evidence_object:photo']
        row=dict(operation='record_observation',observed_object_ref=dict(record_choice=1),observation_method='direct',evidence_carrier_ref=None)
        raw=dict(number=2,title='查看',brief='查看',future_updates=[],scenes=[dict(purpose='查看',participants=['甲'],beats=[dict(statement='甲直接查看照片。',assertion_scope='performed_action',requires=[],changes=[row])])])
        with self.assertRaises(ContractError) as caught:compile_plan(raw,choices,2)
        self.assertEqual(caught.exception.repair_details['allowed_choice_indices'],[2])
        row['observed_object_ref']=dict(record_choice=2)
        packet=prepare(base,compile_plan(raw,choices,2),2)
        self.assertEqual(packet['candidate_state']['observations']['n0002r0001']['object_id'],'photo')

    def test_al_exact_directory_values_are_valid_choices_not_free_identifiers(self):
        from memory_runtime.reference_choices import compile_plan
        from memory_runtime.continuity import context_view
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_al/working').glob('checkpoint_*.json')))
        book=saved['book'];refs=catalogue(book)
        choices=list(dict.fromkeys(r['reference_id'] for r in public_state_view(context_view(book['writing_state'],'',plans=refs['plans']))['records']))
        replies=[json.loads(t['raw_output']) for t in saved['trace'] if t.get('role')=='planner' and 'raw_output' in t]
        self.assertEqual(len(replies),2)
        for raw in replies:
            original=copy.deepcopy(raw)
            self.assertTrue(prepare(book['writing_state'],compile_plan(raw,choices,6),6,references=refs)['candidate_state'])
            self.assertEqual(raw,original)

    def test_ak_stringified_choices_are_parsed_before_any_identifier_conversion(self):
        from tools.testing.archived_plan_fixture import compile_archived_plan as compile_plan
        from memory_runtime.continuity import context_view
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_ak/working').glob('checkpoint_*.json')))
        book=saved['book'];refs=catalogue(book)
        choices=list(dict.fromkeys(r['reference_id'] for r in public_state_view(context_view(book['writing_state'],'',plans=refs['plans']))['records']))
        count=0
        for t in saved['trace']:
            if t.get('role')!='planner' or 'raw_output' not in t:continue
            raw=json.loads(t['raw_output'])
            if 'scenes' not in raw:continue
            original=copy.deepcopy(raw);compiled=compile_plan(raw,choices,6)
            self.assertTrue(prepare(book['writing_state'],compiled,6,references=refs)['candidate_state'])
            self.assertEqual(raw,original);count+=1
        self.assertEqual(count,2)

    def test_new_requires_cannot_bypass_selector_validation_as_a_string(self):
        from memory_runtime.reference_choices import compile_plan
        for value in ('made_up','{record_choice:999}','{record_choice:1,record_choice:2}','{record_choice:true}',dict(reference_id='made_up')):
            raw=dict(number=1,title='测试',brief='测试',future_updates=[],scenes=[dict(purpose='测试',participants=['甲'],beats=[dict(statement='甲登记。',assertion_scope='performed_action',requires=[value],changes=[])])])
            with self.subTest(value=value),self.assertRaises(ContractError):compile_plan(raw,['fact_record:real'],1)

    def test_full_launcher_uses_choices_and_program_ids_without_model_record_ids(self):
        from memory_runtime.test_event_first import EventLocal,event_config
        class ChoiceProvider(EventLocal):
            def complete(self,request):
                if request.role!='planner':return super().complete(request)
                self.requests.append(copy.deepcopy(request));self.number=request.payload['chapter_number']
                p=request.payload;n=self.number
                self.assert_contract(p)
                changes=[dict(operation='establish_fact',subject='信',property_name='位置',value='门口',fact_class='current_state')] if n==1 else [dict(operation='change_fact_value',fact_ref=dict(record_choice=p['reference_choices'].index('fact_record:n0001r0001')+1),new_value='屋内')]
                return ModelReply(canonical(dict(number=n,title='来信',brief='移动',future_updates=[],scenes=[dict(purpose='记事',participants=['甲'],beats=[dict(statement='甲把信放好。',assertion_scope='performed_action',requires=[],changes=changes)])])),1,1,0)
            def assert_contract(self,p):
                assert 'reference_selection_contract' in p
                assert 'record_id' not in p['state_record_contract']['schemas']['establish_fact']['required']
        provider=ChoiceProvider()
        with tempfile.TemporaryDirectory(dir=ROOT/'runs') as directory:
            output=Path(directory)/'run'
            with patch.object(cli,'read_secret',return_value='offline'),patch.object(cli,'ChatCompletionProvider',return_value=provider),contextlib.redirect_stdout(io.StringIO()):result=cli.launch(event_config(2,False),output)
            book=self.read(output/'final_state.json')
            self.assertTrue(result['draft_completed']);self.assertTrue(result['memory_complete'])
            self.assertEqual(book['writing_state']['facts']['n0001r0001']['value'],'屋内')

    def test_choice_compiler_owns_ids_and_rejects_made_up_choices(self):
        from memory_runtime.reference_choices import compile_plan
        raw=dict(number=1,title='来信',brief='记事',future_updates=[],scenes=[dict(purpose='登记',participants=['甲'],beats=[dict(statement='甲收到信并确认。',assertion_scope='performed_action',requires=[],changes=[dict(operation='establish_fact',subject='信',property_name='位置',value='门口',fact_class='current_state'),dict(operation='record_character_knowledge',character_id='甲',learned_record_ref=dict(record_position=[1,1,1]),source_action_ref=dict(current_action=True))])])])
        original=copy.deepcopy(raw);compiled=compile_plan(raw,[],1)
        self.assertEqual(raw,original)
        packet=prepare(empty(),compiled,1)
        self.assertEqual(packet['candidate_state']['knowledge']['n0001r0002']['value'],'门口')
        for bad in (dict(record_choice=1),dict(record_choice=True),dict(action_position=99),dict(record_position=[1,1,99]),'fact_record:made_up'):
            invalid=copy.deepcopy(raw);invalid['scenes'][0]['beats'][0]['changes'][1]['learned_record_ref']=bad
            with self.assertRaises(ContractError):compile_plan(invalid,[],1)
        future=copy.deepcopy(raw)
        future['scenes'][0]['beats'][0]['requires']=[dict(record_position=[1,1,1])]
        with self.assertRaises(ContractError):prepare(empty(),compile_plan(future,[],1),1)

    def test_choice_directory_binds_existing_records_without_guessing_kind(self):
        from memory_runtime.reference_choices import compile_plan
        base=prepare(empty(),proposal(),1)['candidate_state']
        action=dict(statement='甲把信移到屋里。',assertion_scope='performed_action',requires=[dict(record_choice=1)],changes=[dict(operation='change_fact_value',fact_ref=dict(record_choice=1),new_value='屋里')])
        raw=dict(number=2,title='移动',brief='移动',future_updates=[],scenes=[dict(purpose='移动',participants=['甲'],beats=[action])])
        packet=prepare(base,compile_plan(raw,['fact_record:location'],2),2)
        self.assertEqual(packet['candidate_state']['facts']['location']['value'],'屋里')

    def test_ah_nonexistent_intention_is_not_invented_and_reports_creation_route(self):
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_ah/working').glob('checkpoint_*.json')))
        refs=catalogue(saved['book']);original=copy.deepcopy(saved['book']['writing_state'])
        replies=[json.loads(t['raw_output']) for t in saved['trace'] if t.get('role')=='planner' and 'raw_output' in t]
        for raw in replies:
            with self.assertRaises(ContractError) as caught:prepare(original,raw,5,references=refs)
            feedback=public_repair_details(caught.exception.repair_details,raw)
            self.assertIn('establish_fact',canonical(feedback))
        self.assertNotIn('intention_find_foreman_1',refs['plans'])
        self.assertEqual(original,saved['book']['writing_state'])

    def test_ag_duplicate_identity_feedback_supplies_real_target_without_applying_it(self):
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_ag/working').glob('checkpoint_*.json')))
        raw=json.loads([t['raw_output'] for t in saved['trace'] if t.get('role')=='planner' and 'raw_output' in t][-1])
        original=copy.deepcopy(saved['book']['writing_state'])
        with self.assertRaises(ContractError) as caught:prepare(original,raw,3,references=catalogue(saved['book']))
        feedback=public_repair_details(caught.exception.repair_details,raw)
        example=feedback['issues'][0]['replacement_operation_example']
        self.assertEqual(example['fact_ref'],'fact_record:liang_brings_dispatch_copy')
        self.assertEqual(example['operation'],'change_fact_value')
        self.assertEqual(saved['book']['writing_state'],original)

    def test_af_intention_revision_never_changes_objective_facts(self):
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_af/working').glob('checkpoint_*.json')))
        book=saved['book'];refs=catalogue(book)
        replies=[json.loads(t['raw_output']) for t in saved['trace'] if t.get('role')=='planner' and 'raw_output' in t]
        for raw in replies:
            original=copy.deepcopy(raw);packet=prepare(book['writing_state'],raw,2,references=refs)
            self.assertNotIn('intent_liangce_sign',packet['candidate_state']['facts']);self.assertEqual(raw,original)
        action=dict(id='revise',statement='梁策决定暂不签字，等核对原件。',assertion_scope='performed_action',requires=[],changes=[dict(operation='revise_intention',intention_ref='pending_intention:intent_liangce_sign',new_value='等待原件核对')])
        raw=proposal([action],2);packet=prepare(book['writing_state'],raw,2,references=refs)
        self.assertEqual(packet['candidate_state']['facts'],book['writing_state']['facts'])
        chapter=dict(number=2,event_commit=packet['commit'])
        updated=catalogue(dict(chapters=book['chapters']+[chapter],memory=book['memory']))['plans']['intent_liangce_sign']
        self.assertEqual(updated['value'],'等待原件核对');self.assertEqual(updated['revision'],refs['plans']['intent_liangce_sign']['revision']+1)
        bad=copy.deepcopy(raw);bad['scenes'][0]['beats'][0]['changes'][0]['intention_ref']='fact_record:missing'
        with self.assertRaises(ContractError):prepare(book['writing_state'],bad,2,references=refs)

    def test_ae_bare_reference_id_replays_without_manual_classification(self):
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_ae/working').glob('checkpoint_*.json')))
        replies=[json.loads(t['raw_output']) for t in saved['trace'] if t.get('role')=='planner' and 'raw_output' in t]
        self.assertEqual(len(replies),2)
        for raw in replies:
            original=copy.deepcopy(raw)
            self.assertTrue(prepare(saved['book']['writing_state'],raw,7,references=catalogue(saved['book']))['candidate_state'])
            self.assertEqual(raw,original)
        a=beat('same','甲把信登记。',[dict(type='fact',id='same',subject='信',attribute='位置',value='门口',kind='state')])
        for value in ('same','missing','unknown:thing'):
            b=beat('later','甲翻开记录。',[]);b['requires']=[dict(reference_id=value)]
            with self.assertRaises(ContractError):prepare(empty(),proposal([a,b]),1)

    def test_ad_direct_photo_view_binds_same_object_without_inventing_original(self):
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_ad/working').glob('checkpoint_*.json')))
        replies=[json.loads(t['raw_output']) for t in saved['trace'] if t.get('role')=='planner' and 'raw_output' in t]
        self.assertEqual(len(replies),2)
        raw=replies[0];original=copy.deepcopy(raw)
        packet=prepare(saved['book']['writing_state'],raw,5,references=catalogue(saved['book']))
        observed=packet['candidate_state']['observations']['lao_zhou_sees_signature']
        self.assertEqual(observed['method'],'direct');self.assertIsNone(observed['source_id'])
        self.assertEqual(packet['candidate_state']['objects'][observed['object_id']]['form'],'photo')
        self.assertEqual(raw,original)
        with self.assertRaises(ContractError) as caught:prepare(saved['book']['writing_state'],replies[1],5,references=catalogue(saved['book']))
        feedback=public_repair_details(caught.exception.repair_details,replies[1])
        self.assertIn('evidence_carrier_ref=null',feedback['issues'][0]['repair_guidance'])

    def test_ac_long_chapter_memory_intake_fits_before_model_scheduling(self):
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_ac/working').glob('checkpoint_*.json')))
        book=saved['book'];self.assertEqual(book['pending'],[2])
        class Keep:
            def complete(self,request):
                value=dict(placements=[dict(id=r['id'],tier=r['tier'],priority=3,reason='离线保持来源') for r in request.payload['items']])
                return ModelReply(canonical(value),1,1,0)
        original=copy.deepcopy(book['memory'])
        memory,report=MemoryEngine(Keep()).advance(book['memory'],book['chapters'],2,[])
        self.assertTrue(verify_prose_coverage(memory,book['chapters'][1]))
        self.assertTrue(report['layers']['intake_moves'])
        self.assertLessEqual(report['layers']['working_bytes'],16000)
        self.assertTrue(set(original['items'])<=set(memory['items']))
        self.assertEqual(book['memory'],original)

    def test_ac_writer_wrapper_metadata_preserves_actual_prose(self):
        from inf_writer.agents import validate
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_ac/working').glob('checkpoint_*.json')))
        replies=[json.loads(t['raw_output']) for t in saved['trace'] if t.get('role')=='writer' and 'raw_output' in t]
        self.assertEqual(len(replies),2)
        for raw in replies:
            original=copy.deepcopy(raw)
            self.assertEqual(validate('writer',raw),{'text':raw['text']})
            self.assertEqual(raw,original)
            bad=dict(raw,memory_changes=[])
            with self.assertRaises(ContractError):validate('writer',bad)

    def test_ab_semantic_failures_remain_rejected_with_actionable_public_feedback(self):
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_ab/working').glob('checkpoint_*.json')))
        raw=json.loads([t['raw_output'] for t in saved['trace'] if t.get('role')=='planner' and 'raw_output' in t][-1])
        with self.assertRaises(ContractError) as caught:prepare(saved['book']['writing_state'],raw,2,references=catalogue(saved['book']))
        feedback=public_repair_details(caught.exception.repair_details,raw)
        self.assertEqual(len(feedback['issues']),2)
        self.assertTrue(all(i.get('repair_guidance') for i in feedback['issues']))
        self.assertIn('character_belief',canonical(feedback));self.assertIn('planned_intention',canonical(feedback))

    def test_agreement_is_actual_but_arranged_execution_remains_an_intention(self):
        a=dict(id='agree',statement='甲当场约定明天送信。',assertion_scope='performed_action',requires=[],changes=[dict(operation='establish_fact',record_id='arrangement',subject='甲',property_name='安排',value='明天送信',fact_class='planned_intention')])
        b=dict(id='note',statement='甲把约定写下。',assertion_scope='performed_action',requires=[dict(reference_id='chapter_action:agree')],changes=[])
        packet=prepare(empty(),proposal([a,b]),1)
        self.assertNotIn('arrangement',packet['candidate_state']['facts'])
        self.assertEqual(packet['candidate_state']['event_log']['c0001.agree']['mode'],'actual')
        a['assertion_scope']='proposed_action'
        with self.assertRaises(ContractError):prepare(empty(),proposal([a,b]),1)

    def test_aa_wrong_plan_namespace_reports_available_intention_and_context_includes_it(self):
        from memory_runtime.continuity import context_view
        saved=self.read(max((ROOT/'runs/event_first_50000_20261022_aa/working').glob('checkpoint_*.json')))
        book=saved['book'];refs=catalogue(book)
        view=public_state_view(context_view(book['writing_state'],'meeting_plan',plans=refs['plans']))
        self.assertTrue(any(r['reference_id']=='pending_intention:meeting_plan' for r in view['records']))
        raw=json.loads([t['raw_output'] for t in saved['trace'] if t.get('role')=='planner' and 'raw_output' in t][-1])
        with self.assertRaises(ContractError) as caught:prepare(book['writing_state'],raw,2,references=refs)
        issue=caught.exception.repair_details['issues'][0]
        self.assertIn('pending_intention:xu_plan_meet_liang',issue['available_reference_ids'])
        corrected=copy.deepcopy(raw)
        for scene in corrected['scenes']:
            for action in scene['beats']:
                for req in action['requires']:
                    if req.get('reference_id')=='fact_record:xu_plan_meet_liang':req['reference_id']='pending_intention:xu_plan_meet_liang'
        self.assertTrue(prepare(book['writing_state'],corrected,2,references=refs)['candidate_state'])
        wrong_kind=copy.deepcopy(corrected)
        for scene in wrong_kind['scenes']:
            for action in scene['beats']:
                for req in action['requires']:
                    if req.get('reference_id')=='pending_intention:xu_plan_meet_liang':req['reference_id']='fact_record:xu_plan_meet_liang'
        with self.assertRaises(ContractError) as caught:prepare(book['writing_state'],wrong_kind,2,references=refs)
        self.assertIn('pending_intention:xu_plan_meet_liang',caught.exception.repair_details['issues'][0]['available_reference_ids'])

    def test_real_z_replies_bind_scene_action_paths_without_manual_changes(self):
        saved=self.read(ROOT/'runs/event_first_50000_20261022_z/working/checkpoint_0001.json')
        replies=[json.loads(t['raw_output']) for t in saved['trace'] if t.get('role')=='planner' and 'raw_output' in t]
        self.assertEqual(len(replies),2)
        for raw in replies:
            original=copy.deepcopy(raw);packet=prepare(empty(),raw,1)
            self.assertEqual(len(packet['candidate_state']['knowledge']),4)
            self.assertEqual(raw,original)

    def test_action_reference_spellings_are_idempotent_and_namespaces_are_checked(self):
        for spelling in ('a','s.a','c0001.a','c0001.s.a'):
            action=dict(id='a',statement='甲确认信在门口。',assertion_scope='performed_action',requires=[],changes=[dict(operation='establish_fact',record_id='f',subject='信',property_name='位置',value='门口',fact_class='current_state'),dict(operation='record_character_knowledge',record_id='k',character_id='甲',learned_record_ref='fact_record:f',source_action_ref='chapter_action:'+spelling)])
            raw=proposal([action]);raw['scenes'][0]['id']='s'
            normalized,_=normalize_plan(raw,empty(),1)
            again,_=normalize_plan(normalized,empty(),1)
            self.assertEqual(normalized,again)
            self.assertEqual(prepare(empty(),raw,1)['candidate_state']['knowledge']['k']['value'],'门口')
            bad=copy.deepcopy(raw);bad['scenes'][0]['beats'][0]['changes'][1]['source_action_ref']='fact_record:a'
            with self.assertRaises(ContractError):prepare(empty(),bad,1)
        for spelling in ('s.missing','c0002.a'):
            bad=copy.deepcopy(raw);bad['scenes'][0]['beats'][0]['changes'][1]['source_action_ref']='chapter_action:'+spelling
            normalized,_=normalize_plan(bad,empty(),1)
            self.assertEqual(normalized['scenes'][0]['beats'][0]['changes'][1]['via_event'],spelling)
            with self.assertRaises(ContractError):prepare(empty(),bad,1)

    def test_nested_semantic_diagnostics_use_public_record_fields(self):
        plan,_=normalize_plan(proposal([beat(changes=[dict(type='learn',id='k',actor='甲',fact_id='f',via_event='missing')])]),empty(),1)
        details=dict(issues=[dict(path='scenes[0].beats[0].changes[0]',field='via_event',proposed=dict(type='learn',id='k',actor='甲',fact_id='f',via_event='missing'),prior=dict(type='fact',id='f',revision=1,kind='state'),reference_candidates=[dict(type='fact',id='f',revision=1)])])
        original=copy.deepcopy(details);public=public_repair_details(details,plan);issue=public['issues'][0]
        self.assertEqual(issue['field'],'source_action_ref')
        self.assertEqual(issue['proposed']['operation'],'record_character_knowledge')
        self.assertEqual(issue['proposed']['source_action_ref'],'missing')
        self.assertEqual(issue['prior']['record_kind'],'fact_record')
        self.assertEqual(issue['prior']['record_revision'],1)
        self.assertNotIn('type',issue['reference_candidates'][0]);self.assertEqual(details,original)

    def test_real_y_invalid_scope_returns_public_path_and_values_without_guessing(self):
        saved=self.read(ROOT/'runs/event_first_50000_20261022_y/working/checkpoint_0001.json')
        replies=[json.loads(t['raw_output']) for t in saved['trace'] if t.get('role')=='planner' and 'raw_output' in t]
        self.assertEqual(len(replies),2)
        for raw in replies:
            original=copy.deepcopy(raw);normalized,_=normalize_plan(raw,empty(),1)
            with self.assertRaises(ContractError) as caught:validate_plan_shape(normalized)
            feedback=public_repair_details(caught.exception.repair_details,normalized)
            issue=next(i for i in feedback['issues'] if i['path'].endswith('.assertion_scope'))
            self.assertEqual(issue['submitted_value'],'planned_intention')
            self.assertEqual(issue['allowed_values'],['performed_action','reported_claim','proposed_action'])
            self.assertEqual(raw,original)

    def test_all_operation_errors_use_public_fields_and_enums(self):
        from memory_runtime.event_contract import record_issues
        for name,(kind,aliases) in OPERATIONS.items():
            effect=dict(type=kind,id='sample')
            plan=proposal([beat(changes=[effect])])
            diagnostics=dict(issues=record_issues(effect,'scenes[0].beats[0].changes[0]'))
            translated=public_repair_details(diagnostics,plan)
            missing=translated['issues'][0]['missing_fields']
            self.assertTrue(set(missing)<=set(planner_catalogue()[name]['required']))
            self.assertNotIn('type',translated['issues'][0]['required_fields'])
        plan=proposal([beat(changes=[dict(type='fact',id='f',subject='信',attribute='状态',value='在',kind='wrong')])])
        feedback=public_repair_details(dict(issues=record_issues(plan['scenes'][0]['beats'][0]['changes'][0],'scenes[0].beats[0].changes[0]')),plan)
        issue=next(i for i in feedback['issues'] if 'allowed_values' in i)
        self.assertTrue(issue['path'].endswith('.fact_class'))
        self.assertEqual(issue['allowed_values'],['current_state','fixed_fact','character_belief','planned_intention'])

    def test_real_launcher_repairs_using_public_scope_feedback(self):
        from memory_runtime.test_event_first import EventLocal,event_config
        class RepairProvider(EventLocal):
            def __init__(self):super().__init__();self.attempt=0;self.feedback=None
            def complete(self,request):
                if request.role!='planner':return super().complete(request)
                self.attempt+=1;self.requests.append(copy.deepcopy(request))
                if self.attempt==2:
                    self.feedback=request.payload
                    encoded=canonical(request.payload)
                    assert 'proposed_action' in encoded
                    assert 'scenes[0].beats[0].assertion_scope' in encoded
                    assert 'scenes[0].beats[0].mode' not in encoded
                action=dict(statement='甲打算明天送信。',assertion_scope='planned_intention' if self.attempt==1 else 'proposed_action',requires=[],changes=[])
                value=proposal([action]);value['scenes'][0].pop('id')
                return ModelReply(canonical(value),1,1,0)
        provider=RepairProvider()
        with tempfile.TemporaryDirectory(dir=ROOT/'runs') as directory:
            with patch.object(cli,'read_secret',return_value='offline'),patch.object(cli,'ChatCompletionProvider',return_value=provider),contextlib.redirect_stdout(io.StringIO()):
                result=cli.launch(event_config(1,False),Path(directory)/'run')
            self.assertTrue(result['draft_completed']);self.assertEqual(provider.attempt,2)

    def test_all_operations_share_a_distinct_public_catalogue(self):
        validate_catalogue_names();catalog=planner_catalogue()
        self.assertEqual(set(catalog),set(OPERATIONS));self.assertEqual(len(catalog),len(RECORDS))
        self.assertNotIn('event',catalog);self.assertNotIn('occurrence',catalog)
        self.assertIn('learned_record_ref',catalog['record_character_knowledge']['required'])
        self.assertNotIn('fact_id',catalog['record_character_knowledge']['required'])
        self.assertIn('timeline_relation',catalog['record_dated_event']['required'])
        self.assertIn('availability',catalog['register_evidence_object']['required'])
        self.assertNotIn('expected_revision',catalog['change_fact_value']['required'])
        self.assertNotIn('type',set().union(*(set(v['required']) for v in catalog.values())))

    def test_three_chapters_use_new_contract_store_rephrased_prose_and_recall_first_chapter(self):
        from memory_runtime.test_event_first import event_config
        class PublicProvider:
            def __init__(self):self.requests=[]
            def complete(self,request):
                self.requests.append(copy.deepcopy(request));p=request.payload
                if request.role=='planner':
                    n=p['chapter_number'];target={1:'门外',2:'门内',3:'院子里'}[n]
                    assert 'event_plan_state' in p and 'writing_state' not in p
                    assert 'retrieved_memory' in p and 'active_facts' not in p
                    assert 'content_unchecked_chapters' in p and 'unresolved_chapters' not in p
                    assert 'memory_bank_revision' in p and 'checkpoint_revision' not in p
                    for row in p['retrieved_memory']:assert 'memory_kind' in row and 'memory_revision' in row and 'revision' not in row
                    choice=p['reference_choices'].index('fact_record:n0001r0001')+1 if n>1 else None
                    change=dict(operation='establish_fact',subject='信',property_name='位置',value=target,fact_class='current_state') if n==1 else dict(operation='change_fact_value',fact_ref=dict(record_choice=choice),new_value=target)
                    action=dict(statement='甲将信放在'+target+'。',assertion_scope='performed_action',requires=[] if n==1 else [dict(record_choice=choice)],changes=[change])
                    value=proposal([action],n)
                    value['scenes'][0].pop('id')
                    if n==3:value['title']='门外'
                elif request.role=='writer':
                    n=p['chapter_plan']['number'];place={1:'门外',2:'门内',3:'院子里'}[n]
                    value=dict(text=f'第{n}次记事，信的位置是{place}。甲把这一点写进自己的小本。')
                elif 'completed_chapter' in p:
                    n=p['completed_chapter'];rows=[]
                    for row in p['items']:
                        target='working' if n==3 and '门外' in row['claim'] else 'recent' if row['tier']=='working' else 'long'
                        rows.append(dict(id=row['id'],tier=target if target in row['allowed_tiers'] else row['tier'],priority=5 if '门外' in row['claim'] else 2,reason='离线剧情范围整理'))
                    value=dict(placements=rows)
                elif 'question' in p:
                    row=next(r for r in p['current_memory'] if '门外' in r['claim'])
                    value=dict(answer=row['claim'],memory_ids=[row['id']])
                else:raise AssertionError('Unexpected provider operation')
                return ModelReply(canonical(value),1,1,0)
        provider=PublicProvider()
        with tempfile.TemporaryDirectory(dir=ROOT/'runs') as directory:
            output=Path(directory)/'run'
            with patch.object(cli,'read_secret',return_value='offline'),patch.object(cli,'ChatCompletionProvider',return_value=provider),contextlib.redirect_stdout(io.StringIO()):
                result=cli.launch(event_config(3,True),output)
            book=self.read(output/'final_state.json')
            self.assertTrue(result['draft_completed']);self.assertTrue(result['memory_complete']);self.assertTrue(result['prose_memory_complete'])
            self.assertFalse(result['event_alignment_complete']);self.assertEqual(result['prose_excerpt_count'],3)
            self.assertTrue(all(verify_prose_coverage(book['memory'],c) for c in book['chapters']))
            moves=[m for o in book['outcomes'] for m in o['memory_report']['layers']['moves']]
            self.assertTrue(any(m['op']=='demote' for m in moves));self.assertTrue(any(m['op']=='recall' for m in moves))
            self.assertFalse(any(r.role=='reviewer' for r in provider.requests))
            answer=MemoryEngine(provider).recall(book['memory'],'第一次记事中信放在哪里',[])
            self.assertIn('门外',answer['answer'])
            self.assertEqual(book['writing_state']['facts']['n0001r0001']['value'],'院子里')

    def test_every_public_operation_compiles_with_its_own_fields_and_enums(self):
        rows=[
            dict(operation='establish_fact',record_id='lamp',subject='灯',property_name='状态',value='亮',fact_class='current_state'),
            dict(operation='change_fact_value',fact_ref='fact_record:lamp',new_value='灭'),
            dict(operation='record_character_knowledge',record_id='knows',character_id='甲',learned_record_ref='evidence_object:photo',source_action_ref='chapter_action:arrival'),
            dict(operation='record_dated_event',record_id='day',story_date='2026-10-22',timeline_relation='historical_timeline',involved_object_refs=['evidence_object:photo'],follows_dated_event_refs=[]),
            dict(operation='register_evidence_object',record_id='photo',label='照片',carrier_form='photo',availability='available',created_by_action_ref='chapter_action:arrival',provenance_description='由甲翻拍'),
            dict(operation='record_observation',record_id='look',observed_object_ref='evidence_object:paper',observation_method='photo',evidence_carrier_ref='evidence_object:photo'),
            dict(operation='record_receipt',record_id='signed',signer_ids=['甲'],attendee_without_signature_ids=['乙'],attendee_ids=['甲','乙']),
            dict(operation='resolve_person_identity',record_id='name',unidentified_person_id='来客',identified_person_id='甲'),
            dict(operation='record_check_progress',record_id='check',check_pass_id='round1',completed_count=1,total_count=3),
        ]
        original=copy.deepcopy(rows);normalized,_=normalize_plan(proposal([beat(changes=rows)]),empty(),1)
        validate_plan_shape(normalized);effects=normalized['scenes'][0]['beats'][0]['changes']
        self.assertEqual([r['type'] for r in effects],[kind for kind,_ in OPERATIONS.values() if kind!='revise_intention'])
        self.assertEqual(effects[0]['kind'],'state');self.assertEqual(effects[1]['fact_id'],'lamp')
        self.assertEqual(effects[2]['reference_type'],'object');self.assertEqual(effects[2]['via_event'],'c0001.arrival')
        self.assertEqual(effects[3]['mode'],'historical');self.assertEqual(effects[3]['objects'],['photo'])
        self.assertEqual(effects[4]['origin'],'c0001.arrival');self.assertEqual(rows,original)

    def test_new_fact_change_and_knowledge_execute_without_model_types_or_versions(self):
        a=dict(id='a',statement='甲把信放在门外。',assertion_scope='performed_action',requires=[],changes=[dict(operation='establish_fact',record_id='location',subject='信',property_name='位置',value='门外',fact_class='current_state')])
        b=dict(id='b',statement='甲把信拿进门内。',assertion_scope='performed_action',requires=[dict(reference_id='fact_record:location')],changes=[dict(operation='change_fact_value',fact_ref='fact_record:location',new_value='门内')])
        c=dict(id='c',statement='甲确认信已经在门内。',assertion_scope='performed_action',requires=['chapter_action:b'],changes=[dict(operation='record_character_knowledge',record_id='known',character_id='甲',learned_record_ref='fact_record:location',source_action_ref='chapter_action:c')])
        packet=prepare(empty(),proposal([a,b,c]),1);state=packet['candidate_state']
        self.assertEqual(state['facts']['location']['value'],'门内');self.assertEqual(state['facts']['location']['revision'],2)
        self.assertEqual(state['knowledge']['known']['value'],'门内')
        from memory_runtime.continuity import context_view
        view=public_state_view(context_view(state,'信'))
        self.assertTrue(all('record_kind' in r and 'reference_id' in r and 'type' not in r for r in view['records']))
        self.assertTrue(all('record_revision' in r and 'revision' not in r for r in view['records']))

    def test_named_references_resolve_collisions_but_not_missing_future_or_stale(self):
        first=beat('same','甲在门外登记。',[dict(type='fact',id='same',subject='信',attribute='位置',value='门外',kind='state')])
        for reference in ('fact_record:same','chapter_action:same'):
            later=beat('next','甲翻开本子。',[]);later['requires']=[dict(reference_id=reference)]
            self.assertTrue(prepare(empty(),proposal([first,later]),1)['candidate_state'])
        for req in (dict(id='same'),dict(reference_id='dated_event_record:same'),dict(reference_id='fact_record:missing'),dict(reference_id='fact_record:same',record_revision=9)):
            later=beat('next','甲翻开本子。',[]);later['requires']=[req]
            with self.subTest(req=req),self.assertRaises(ContractError):prepare(empty(),proposal([first,later]),1)
        future=beat('next','甲翻开本子。',[]);future['requires']=[dict(reference_id='chapter_action:same')]
        with self.assertRaises(ContractError):prepare(empty(),proposal([future,first]),1)

    def test_alias_conflicts_are_rejected_and_normalization_is_idempotent(self):
        value=proposal();value['scenes'][0]['beats'][0]['requires']=[dict(reference_id='chapter_action:arrival')]
        first,_=normalize_plan(value,empty(),1);second,_=normalize_plan(first,empty(),1)
        self.assertEqual(first,second)
        bad=proposal([beat(changes=[dict(operation='establish_fact',record_id='a',id='b',subject='信',property_name='位置',value='门外',fact_class='current_state')])])
        with self.assertRaises(ContractError):normalize_plan(bad,empty(),1)

    def test_real_w_plan_replays_without_manual_type_edits(self):
        folder=ROOT/'runs/event_first_50000_20261022_w/working';saved=self.read(max(folder.glob('checkpoint_*.json')))
        plans=[json.loads(t['raw_output']) for t in saved['trace'] if t.get('role')=='planner' and t.get('status')=='ACCEPTED']
        self.assertEqual(len(plans),2);original=copy.deepcopy(plans[-1])
        packet=prepare(saved['book']['writing_state'],plans[-1],2,references=catalogue(saved['book']))
        self.assertEqual(plans[-1],original)
        self.assertTrue(any(n.get('rule')=='program_owned_reference_binding' for n in packet['commit']['identifier_normalizations']))
        with self.assertRaises(ContractError):prepare(saved['book']['writing_state'],plans[0],2,references=catalogue(saved['book']))

    def test_real_w_prose_enters_memory_idempotently_with_all_actual_sources(self):
        saved=self.read(ROOT/'runs/event_first_50000_20261022_w/final_state.json');chapter=saved['chapters'][0]
        original=copy.deepcopy(chapter);before=MemoryEngine.empty()
        result=project_memory(before,[chapter],1,[])
        self.assertTrue(verify_prose_coverage(result,chapter))
        self.assertEqual(len([r for r in result['items'].values() if r['kind']=='prose_excerpt']),len(excerpts(chapter)))
        self.assertEqual(project_memory(result,[chapter],1,[]),result)
        self.assertEqual(chapter,original);self.assertEqual(before,MemoryEngine.empty())
        self.assertTrue(result['projection_omissions']['1'])
        for row in result['items'].values():
            self.assertEqual(row['kind'],'prose_excerpt');self.assertIn(row['claim'],chapter['text'])
            self.assertEqual(row['sources'][0]['chapter_sha256'],chapter['sha256'])
        damaged=copy.deepcopy(result);next(iter(damaged['items'].values()))['claim']='篡改的记忆'
        self.assertFalse(verify_prose_coverage(damaged,chapter))
        with self.assertRaises(ContractError):project_memory(damaged,[chapter],1,[])

    def test_real_w_excerpts_demote_twice_recall_and_promote_without_losing_sources(self):
        saved=self.read(ROOT/'runs/event_first_50000_20261022_w/final_state.json');chapters=saved['chapters']
        memory=project_memory(MemoryEngine.empty(),chapters,1,[])
        class Demote:
            def complete(self,request):
                return ModelReply(canonical(dict(placements=[dict(id=r['id'],tier='recent' if r['tier']=='working' else 'long',priority=2,reason='离线整理轮次') for r in request.payload['items']])),1,1,0)
        recent,report1=LayerAgent(Demote()).run(memory,chapters,1,'缺页记录',[])
        long,report2=LayerAgent(Demote()).run(recent,chapters,2,'缺页记录',[])
        self.assertTrue(report1['moves']);self.assertTrue(report2['moves'])
        self.assertTrue(all(r['tier']=='long' for r in long['items'].values()))
        class Recall:
            def complete(self,request):
                rows=request.payload['current_memory'];row=next(r for r in rows if '十七至二十一' in r['claim'])
                return ModelReply(canonical(dict(answer=row['claim'],memory_ids=[row['id']])),1,1,0)
        answer=MemoryEngine(Recall()).recall(long,'许闻记录的卷宗缺页情况是什么',[])
        self.assertIn('四页',answer['answer']);self.assertGreater(answer['cited_long_term'],0)
        class Promote:
            def complete(self,request):
                return ModelReply(canonical(dict(placements=[dict(id=r['id'],tier='working' if '十七至二十一' in r['claim'] else r['tier'],priority=5,reason='当前需要引用') for r in request.payload['items']])),1,1,0)
        promoted,report3=LayerAgent(Promote()).run(long,chapters,3,'十七至二十一',[])
        self.assertTrue(any(m['op']=='recall' for m in report3['moves']))
        self.assertTrue(verify_prose_coverage(promoted,chapters[0]))
        self.assertEqual(set(memory['items']),set(promoted['items']))


if __name__=='__main__':unittest.main()
