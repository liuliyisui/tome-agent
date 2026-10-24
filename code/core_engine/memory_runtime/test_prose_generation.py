"""Unchecked development generation, source-preserving quantities and storage integrity."""
import copy
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from memory_runtime.test_event_first import ROOT,EventLocal,event_config,proposal,beat,fact
import write_novel as cli
from inf_writer.domain import ContractError,canonical,digest
from inf_writer.models import ModelReply
from memory_runtime.continuity import empty
from memory_runtime.event_first import prepare,project_memory
from memory_runtime.numeric_grounding import sources
from memory_runtime.prose_rendering import render,saved_text
from memory_runtime.writing import WritingSession,load_resume


class ProseGenerationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'runs');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def launch(self,provider,cfg=None):
        from tools.testing.archived_plan_fixture import compile_archived_plan
        with patch.object(cli,'read_secret',return_value='offline'),patch.object(cli,'ChatCompletionProvider',return_value=provider),patch('memory_runtime.reference_choices.compile_plan',side_effect=compile_archived_plan),contextlib.redirect_stdout(io.StringIO()):
            return cli.launch(cfg or event_config(1,True),self.root/'run')
    def read(self,path):return json.loads(path.read_text(encoding='utf-8'))

    def test_generation_preserves_approximate_source_through_quantity_slot(self):
        class Quantities(EventLocal):
            def complete(self,request):
                if request.role=='planner':
                    self.requests.append(copy.deepcopy(request))
                    value=proposal([beat('action','记录写着相差约四十分钟。',[fact('约四十分钟')])])
                    return ModelReply(canonical(value),1,1,0)
                if request.role=='writer':
                    self.requests.append(copy.deepcopy(request));p=request.payload
                    assert '不能自行细化' in p['quantity_policy']
                    source=next(r for r in p['quantity_sources'] if r['expression']=='约四十分钟')
                    return ModelReply(canonical(dict(text='[[event:slot_001]]\n他仍按原记录描述为'+source['token']+'。')),1,1,0)
                return super().complete(request)
        provider=Quantities();result=self.launch(provider)
        self.assertTrue(result['draft_completed']);self.assertFalse(result['story_review_enabled'])
        book=self.read(self.root/'run/final_state.json');chapter=book['chapters'][0]
        self.assertEqual(chapter['text'],'记录写着相差约四十分钟。\n他仍按原记录描述为约四十分钟。')
        self.assertNotIn('三十八',chapter['text']);self.assertEqual(saved_text(chapter),chapter['text'])
        row=next(r for r in chapter['quantity_sources'] if r['expression']=='约四十分钟')
        self.assertEqual(row['precision'],'qualified');self.assertEqual(row['modifiers'],['约'])
        self.assertTrue(result['mechanical_checks_passed']);self.assertIsNone(result['story_and_mechanical_checks_passed'])
        self.assertFalse(result['quality_checked'])
        self.assertFalse(any(r.role=='reviewer' for r in provider.requests))

    def test_content_omission_and_wrong_arithmetic_do_not_trigger_retry_or_review(self):
        prose='16:41到16:45，相隔两分钟。找不出来，这三十八分钟只是照片里的三十八分钟。'
        from memory_runtime.length_control import han_count
        provider=EventLocal(writer=lambda p:dict(text=prose));result=self.launch(provider,dict(event_config(1,True),target_han_chars=han_count(prose)))
        self.assertTrue(result['draft_completed']);self.assertEqual(result['prose_content_checks'],'disabled')
        self.assertFalse(result['memory_projection_complete'])
        self.assertEqual(result['pending_story_review_chapters'],[])
        self.assertEqual(len([r for r in provider.requests if r.role=='writer' and 'current_draft' not in r.payload]),1)
        self.assertFalse(any(r.role=='reviewer' for r in provider.requests))
        book=self.read(self.root/'run/final_state.json')
        self.assertEqual(book['chapters'][0]['text'],prose)
        self.assertTrue(book['memory']['items'])
        self.assertTrue(all(r['kind']=='prose_excerpt' for r in book['memory']['items'].values()))
        self.assertTrue(result['prose_memory_complete']);self.assertTrue(result['memory_complete'])
        self.assertTrue(result['memory_processing_complete'])
        self.assertFalse(result['event_alignment_complete'])
        self.assertTrue(book['memory']['projection_omissions'])
        self.assertEqual(book['memory']['processed_through'],1)

    def test_real_v_fifth_chapter_saves_without_content_gate(self):
        folder=ROOT/'runs/event_first_50000_20261022_v/working'
        saved=self.read(max(folder.glob('checkpoint_*.json')));book=saved['book'];original=copy.deepcopy(book)
        prose=json.loads([r['raw_output'] for r in saved['trace'] if r.get('role')=='writer'][-1])['text']
        provider=EventLocal(writer=lambda p:dict(text=prose))
        plan=cli.validate_config(self.read(ROOT/'novel_config_50000.json'))
        session=WritingSession(self.root/'replay',provider,plan,book=book)
        outcome=session.write_next('继续写作')
        self.assertIsNone(outcome['stop_reason']);self.assertEqual(len(session.book['chapters']),5)
        self.assertIn('三十八分钟',session.book['chapters'][-1]['text'])
        self.assertEqual(len([r for r in provider.requests if r.role=='writer']),1)
        self.assertFalse(any(r.role=='reviewer' for r in provider.requests))
        self.assertEqual(book,original)

    def test_unknown_reference_and_tampered_quantity_table_are_still_rejected(self):
        commit=prepare(empty(),proposal([beat(statement='相差近四十分钟。')]),1)['commit'];rows=sources(commit)
        for prose in ('[[event:missing]]','[[time:missing]]','[[quantity:q_00000000000000000000]]'):
            with self.subTest(prose=prose),self.assertRaises(ContractError):render(prose,commit,rows)
        damaged=copy.deepcopy(rows);damaged[0]['expression']='三十八分钟'
        with self.assertRaises(ContractError):render(rows[0]['token'],commit,damaged)
        self.assertEqual(render(rows[0]['token'],commit,rows),'近四十分钟')

    def test_plain_prose_remains_hash_checked_on_resume_and_projection(self):
        result=self.launch(EventLocal(writer=lambda p:dict(text='一段没有引用事件原句的正文。')))
        path=Path(result['resume_checkpoint']);record=self.read(path);chapter=record['book']['chapters'][0]
        chapter['text']='文件发生了变化。';record['book_sha256']=digest(canonical(record['book']))
        corrupted=self.root/'corrupted.json';corrupted.write_text(canonical(record),encoding='utf-8')
        with self.assertRaises(ContractError):load_resume(corrupted,cli.validate_config(event_config(1,True)))
        with self.assertRaises(ContractError):project_memory(record['book']['memory'],record['book']['chapters'],1,[])


if __name__=='__main__':unittest.main()
