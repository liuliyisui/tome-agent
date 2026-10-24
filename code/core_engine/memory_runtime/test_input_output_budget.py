"""Request-view sizing and output truncation at the real protocol boundary."""
import copy
import io
import json
import unittest
from unittest.mock import patch
import write_novel
from inf_writer.agents import JsonAgent
from inf_writer.chat_provider import ChatCompletionProvider
from inf_writer.domain import canonical,digest
from inf_writer.models import ModelReply,ModelRequest
from memory_runtime.input_budget import fit,size


class InputOutputBudgetTests(unittest.TestCase):
    def test_length_adjustment_uses_actual_han_count_and_never_blocks_on_failure(self):
        from memory_runtime.length_control import adjust
        class Better:
            def complete(self,request):return ModelReply('甲'*100,1,1,0)
        class Broken:
            def complete(self,request):raise RuntimeError('offline')
        book=dict(goal='小说',constraints=[])
        original='甲'*200
        result,report=adjust(original,100,book,1,Better(),[])
        self.assertEqual(len(result),100);self.assertEqual(report['adjustment'],'accepted')
        result,report=adjust(original,100,book,1,Broken(),[])
        self.assertEqual(result,original);self.assertEqual(report['adjustment'],'kept_original_failure')

    def test_large_unicode_chapters_fit_without_editing_sources_or_reference_indices(self):
        prose='风雨中的档案。'*7000
        payload=dict(recent_chapters=[dict(number=i,title='旧卷',text=prose,sha256=digest(prose)) for i in (1,2)],
            event_plan_state=dict(records=[dict(record_id='known',value='甲仍在门外')]),
            reference_choices=['fact_record:known'],reference_choices_by_kind=dict(fact_record=[1]))
        original=copy.deepcopy(payload);bounded=fit(payload,24000)
        self.assertLessEqual(size(bounded),24000);self.assertEqual(payload,original)
        self.assertEqual(bounded['event_plan_state'],original['event_plan_state'])
        self.assertEqual(bounded['reference_choices'],original['reference_choices'])
        self.assertTrue(bounded['input_selection']['stored_sources_unchanged'])
        for chapter in bounded['recent_chapters']:
            self.assertEqual(chapter['source_sha256'],digest(prose))
            self.assertEqual(chapter['sha256'],digest(chapter['text']))
            self.assertLessEqual(len(chapter['text'].encode('utf-8')),12000)

    def test_small_request_is_unchanged(self):
        payload=dict(goal='调查',recent_chapters=[])
        self.assertEqual(fit(payload,84000),payload)

    def test_truncated_agent_reply_is_retained_and_repair_has_double_allowance(self):
        requests=[]
        class Provider:
            def complete(self,request):
                requests.append(request)
                return ModelReply('{"text":',1,1,0,'length') if len(requests)==1 else ModelReply('{"text":"正文"}',1,1,0)
        trace=[];result=JsonAgent('writer',Provider(),compact_narrative=True,max_output_tokens=16384).run({},trace)
        self.assertEqual(result['text'],'正文')
        self.assertEqual([r.max_output_tokens for r in requests],[16384,32768])
        self.assertEqual(trace[0]['raw_output'],'{"text":');self.assertEqual(trace[0]['finish_reason'],'length')

    def test_http_length_reply_keeps_prose_usage_and_plain_mode_does_not_force_json(self):
        sent=[]
        raw=canonical(dict(choices=[dict(finish_reason='length',message=dict(content='尚未写完的正文'))],
            usage=dict(prompt_tokens=5,completion_tokens=10,total_tokens=15))).encode('utf-8')
        class Connection:
            def __init__(self,*args,**kwargs):pass
            def request(self,*args):sent.append(json.loads(args[2]))
            def getresponse(self):
                response=io.BytesIO(raw);response.status=200;return response
            def close(self):pass
        provider=ChatCompletionProvider('https://api.deepseek.com/chat/completions','deepseek-flash','placeholder',0.3,1.2,allow_remote=True)
        with patch('inf_writer.chat_provider.http.client.HTTPSConnection',Connection):
            reply=provider.complete(ModelRequest('writer','只写正文',dict(output_mode='plain_prose'),16384))
            provider.complete(ModelRequest('planner','方案',{},16384))
        self.assertEqual(reply.content,'尚未写完的正文');self.assertEqual(reply.finish_reason,'length')
        self.assertEqual(reply.output_tokens,10);self.assertGreater(reply.cost_usd,0)
        self.assertNotIn('response_format',sent[0]);self.assertIn('response_format',sent[1])


if __name__=='__main__':unittest.main()
