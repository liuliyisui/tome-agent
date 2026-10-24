"""Fault injection through the formal launcher, without replacing its compiler."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import write_novel as cli
from inf_writer.domain import ContractError,canonical
from inf_writer.models import ModelReply
from memory_runtime.completion import prose_from_reply
from memory_runtime.test_event_first import EventLocal,event_config
from memory_runtime.writing import WritingSession,load_resume


class Faults(EventLocal):
    def complete(self,request):
        p=request.payload;n=p.get('chapter_number',self.number)
        if request.role=='planner':
            self.requests.append(copy.deepcopy(request));self.number=n
            if n%3==1:return ModelReply('{"title":"只有标题"}',1,1,0)
            if n%3==2:return ModelReply('这不是JSON。',1,1,0)
            # Valid public fields, nonexistent existing-record selection.
            change=dict(operation='change_fact_value',fact_ref=dict(record_choice=999999),new_value='门内')
            value=dict(number=n,title='追索',brief='继续调查',future_updates=[],scenes=[dict(purpose='查找',participants=['甲'],beats=[dict(statement='甲推开门。',assertion_scope='performed_action',requires=[],changes=[change])])])
            return ModelReply(canonical(value),1,1,0)
        if request.role=='writer':
            self.requests.append(copy.deepcopy(request))
            # Deliberately return prose instead of JSON.
            return ModelReply(('甲沿走廊追索来信的来源。雨声里传来脚步，他停下辨认，随后继续向前。'*70),1,1,0)
        return super().complete(request)


class CompletionTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory(dir=cli.ROOT/'runs');self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()

    def launch(self,provider,cfg,name='run',resume=None):
        with patch.object(cli,'read_secret',return_value='offline'),patch.object(cli,'ChatCompletionProvider',return_value=provider),contextlib.redirect_stdout(io.StringIO()):
            return cli.launch(cfg,self.root/name,resume=resume)

    def test_twenty_five_chapters_finish_despite_missing_fields_bad_json_and_unknown_choices(self):
        cfg=dict(event_config(25),target_han_chars=50000)
        result=self.launch(Faults(),cfg)
        self.assertTrue(result['draft_completed']);self.assertGreaterEqual(result['han_chars'],50000)
        self.assertEqual(result['chapters'],25);self.assertEqual(result['canonical_event_chapters'],0)
        self.assertEqual(result['unprojected_chapters'],list(range(1,26)))
        self.assertFalse(result['event_alignment_complete']);self.assertTrue(result['memory_complete'])
        state=json.loads((self.root/'run/final_state.json').read_text(encoding='utf-8'))
        self.assertEqual(state['writing_state']['facts'],{})
        self.assertTrue(all(r['stop_reason'] is None for r in state['outcomes']))
        self.assertEqual(load_resume(result['resume_checkpoint'],cli.validate_config(cfg))['chapters'],state['chapters'])

    def test_writer_missing_text_requests_plain_prose_and_preserves_normal_state(self):
        class BadWriter(Faults):
            def complete(self,request):
                if request.role=='planner':
                    self.requests.append(copy.deepcopy(request));self.number=request.payload['chapter_number']
                    raw=dict(number=self.number,title='来信',brief='读信',future_updates=[],scenes=[dict(purpose='调查',participants=['甲'],beats=[dict(statement='甲读了来信。',assertion_scope='performed_action',requires=[],changes=[])])])
                    return ModelReply(canonical(raw),1,1,0)
                if request.role=='writer' and request.payload.get('output_mode')!='plain_prose':
                    self.requests.append(copy.deepcopy(request));return ModelReply('{"title":"缺少正文"}',1,1,0)
                return super().complete(request)
        provider=BadWriter();result=self.launch(provider,event_config(3))
        self.assertTrue(result['draft_completed']);self.assertEqual(result['unprojected_chapters'],[])
        self.assertEqual(sum(r.payload.get('output_mode')=='plain_prose' and 'current_draft' not in r.payload for r in provider.requests),3)
        self.assertGreaterEqual(result['generation_warning_count'],3)

    def test_text_salvage_never_treats_control_objects_as_prose(self):
        for raw in ('{}','{"event_revision_request":"修改"}','{"text":null}','{"text":','[]',''):
            self.assertIsNone(prose_from_reply(raw))
        for raw in ('正文','```json\n{"text":"正文","extra":1}\n```','{"text":"正文",BROKEN'):
            self.assertEqual(prose_from_reply(raw),'正文')

    def test_normal_planning_recovers_after_one_unprojected_chapter(self):
        class Mixed(Faults):
            def complete(self,request):
                if request.role=='planner':
                    p=request.payload;n=p['chapter_number'];self.number=n;self.requests.append(copy.deepcopy(request))
                    if n==2:return ModelReply('{"title":"不完整规划"}',1,1,0)
                    value='门外' if n==1 else '门内'
                    change=dict(operation='establish_fact',subject='甲',property_name='location',value=value,fact_class='current_state') if n==1 else dict(operation='change_fact_value',fact_ref=dict(record_choice=p['reference_choices'].index('fact_record:n0001r0001')+1),new_value=value)
                    raw=dict(number=n,title='来信',brief='调查',future_updates=[],scenes=[dict(purpose='调查',participants=['甲'],beats=[dict(statement='甲在'+value+'。',assertion_scope='performed_action',requires=[],changes=[change])])])
                    return ModelReply(canonical(raw),1,1,0)
                if request.role=='writer' and 'frozen_events' in request.payload:
                    self.requests.append(copy.deepcopy(request))
                    return ModelReply(canonical(dict(text=request.payload['frozen_events']['scenes'][0]['beats'][0]['statement'])),1,1,0)
                return super().complete(request)
        result=self.launch(Mixed(),event_config(3))
        self.assertTrue(result['draft_completed']);self.assertEqual(result['unprojected_chapters'],[2])
        state=json.loads((self.root/'run/final_state.json').read_text(encoding='utf-8'))
        current=state['writing_state']['facts']['n0001r0001']
        self.assertEqual(current['revision'],2);self.assertEqual(current['value'],'门内')
        self.assertTrue(result['memory_complete'])
        self.assertEqual(load_resume(result['resume_checkpoint'],cli.validate_config(event_config(3)))['chapters'],state['chapters'])

    def test_memory_outage_still_finishes_with_real_prose_and_pending_queue(self):
        provider=Faults(fail='layers2');result=self.launch(provider,event_config(4))
        self.assertTrue(result['draft_completed']);self.assertFalse(result['memory_complete'])
        self.assertEqual(result['chapters'],4)

    def test_actual_ap_chapter_fifteen_input_overflow_continues_without_mutating_old_run(self):
        from memory_runtime.completion import ContextCapacityError
        path=cli.ROOT/'runs/event_first_50000_20261022_ap/working/checkpoint_0043.json'
        source=path.read_bytes();book=json.loads(source)['book']
        cfg=json.loads((cli.ROOT/'novel_config_50000.json').read_text(encoding='utf-8'))
        session=WritingSession(self.root/'capacity',Faults(),cli.validate_config(cfg),book=book)
        instruction=('连续草稿目标50000汉字，名义25章，现在第15章。'
            '本章约1364汉字，用完整场景、对话推进，不用梗概，不重复凑字数。'
            '根据已写事实局部调整后续计划，保持人物和世界因果一致；待修章节不假称已通过。'
            '名义最后一章解决主要冲突；如需补章，补与结局相容的场景，不推翻前文。')
        bounded=session.context(instruction,instruction)
        from memory_runtime.input_budget import size
        self.assertLessEqual(size(bounded),84000)
        self.assertTrue(bounded['input_selection']['stored_sources_unchanged'])
        self.assertEqual(session.book['chapters'],book['chapters'])
        prior=copy.deepcopy(session.book['writing_state']);row=session.write_next(instruction)
        self.assertIsNone(row['stop_reason']);self.assertEqual(len(session.book['chapters']),15)
        self.assertEqual(session.book['writing_state'],prior)
        self.assertEqual(session.book['memory']['processed_through'],15)
        self.assertEqual(session.book['chapters'][-1]['event_plan_status'],'unavailable')
        self.assertTrue(any(r.role=='planner' for r in session.gateway.requests))
        self.assertEqual(path.read_bytes(),source)

    def test_writer_context_overflow_keeps_prepared_transaction_and_writes_prose(self):
        from memory_runtime.completion import ContextCapacityError
        from memory_runtime.event_first import prepare
        from memory_runtime.test_event_first import proposal
        session=WritingSession(self.root/'writer_capacity',Faults(),cli.validate_config(event_config(1)))
        packet=prepare(session.book['writing_state'],proposal(),1)
        session.book['prepared_events']['1']=packet
        with patch.object(session,'context',side_effect=ContextCapacityError('oversize writer context')):
            row=session.write_next('继续写作')
        self.assertIsNone(row['stop_reason']);self.assertEqual(len(session.book['chapters']),1)
        self.assertEqual(session.book['writing_state'],packet['candidate_state'])
        self.assertEqual(row['generation_warnings'][0]['stage'],'writer_context')

    def test_corrupted_prepared_state_is_not_silently_bypassed(self):
        from memory_runtime.completion import unplanned_packet
        session=WritingSession(self.root/'session',Faults(),cli.validate_config(event_config(1)))
        packet=unplanned_packet(session.book['writing_state'],1,'续写')
        packet['commit']['state_sha256']='tampered'
        session.book['prepared_events']['1']=packet
        row=session.write_next('续写')
        self.assertEqual(row['status'],'NO_DRAFT');self.assertEqual(session.book['chapters'],[])
        self.assertFalse(any(r.role=='writer' for r in session.gateway.requests))

    def test_failed_checkpoint_save_does_not_claim_a_saved_chapter(self):
        session=WritingSession(self.root/'session',Faults(),cli.validate_config(event_config(1)))
        real_save=session._save
        def fail_prose(trace,reason):
            if reason=='DRAFT_SAVED_MEMORY_PENDING':raise OSError('disk unavailable')
            return real_save(trace,reason)
        with patch.object(session,'_save',side_effect=fail_prose):row=session.write_next('续写')
        self.assertEqual(session.book['chapters'],[]);self.assertIsNotNone(row['stop_reason'])


if __name__=='__main__':unittest.main()
