"""Permanent provider refusal preserves prose and suspends further remote work."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from memory_runtime.test_event_first import ROOT
import write_novel as cli
from inf_writer.chat_provider import ChatCompletionProvider,ProviderError
from inf_writer.domain import canonical
from inf_writer.models import ModelReply,ModelRequest
from inf_writer.trial import RecordedProvider
from memory_runtime.writing import WritingSession,load_resume
from user_runtime import MeteredGateway,run_draft_trial


class ProviderStopTests(unittest.TestCase):
    def test_http_status_recorded_without_response_body_or_secret(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'runs')as folder:
            provider=ChatCompletionProvider(endpoint='https://api.deepseek.com/chat/completions',model='offline',
                api_key='offline-secret-not-for-logs',input_usd_per_million=0,output_usd_per_million=0,allow_remote=True)
            with patch('inf_writer.chat_provider.http.client.HTTPSConnection')as factory:
                response=factory.return_value.getresponse.return_value;response.status=402
                response.read.return_value=b'sensitive server response'
                recorder=RecordedProvider(provider,folder)
                with contextlib.redirect_stdout(io.StringIO()),self.assertRaises(ProviderError)as caught:
                    recorder.complete(ModelRequest('writer','test',{},10))
                self.assertEqual(caught.exception.http_status,402)
                response.read.assert_not_called()
            error=json.loads((Path(folder)/'call_001.error.json').read_text(encoding='utf-8'))
            self.assertEqual(error['http_status'],402)
            self.assertEqual(error['failure_category'],'insufficient_balance')
            self.assertNotIn('offline-secret',canonical(error));self.assertNotIn('sensitive',canonical(error))

    def test_permanent_refusal_latches_across_writer_and_memory_without_new_calls(self):
        for status in (401,402,403):
            with self.subTest(status=status):
                class Provider:
                    calls=0
                    def complete(self,r):
                        self.calls+=1;raise ProviderError('sanitized',http_status=status)
                provider=Provider();gateway=MeteredGateway(provider)
                for role in ('writer','memory','planner'):
                    with self.assertRaises(ProviderError):gateway.complete(ModelRequest(role,'test',{},10))
                self.assertEqual(provider.calls,1);self.assertEqual(gateway.calls,1)
                self.assertEqual(gateway.provider_blocked['http_status'],status)

    def test_transient_or_payload_error_does_not_globally_latch(self):
        for status in (400,429,500,503):
            with self.subTest(status=status):
                class Provider:
                    calls=0
                    def complete(self,r):
                        self.calls+=1
                        if self.calls==1:raise ProviderError('sanitized',http_status=status)
                        return ModelReply('正文',1,1,0)
                provider=Provider();gateway=MeteredGateway(provider)
                with self.assertRaises(ProviderError):gateway.complete(ModelRequest('writer','test',{},10))
                self.assertEqual(gateway.complete(ModelRequest('memory','test',{},10)).content,'正文')
                self.assertEqual(provider.calls,2);self.assertIsNone(gateway.provider_blocked)

    def test_actual_partial_chapter_quota_stop_exports_then_resumes_without_rewriting_first_unit(self):
        source=ROOT/'runs/event_first_30000_20261028_full_after_transfer_a'
        record=json.loads((source/'working/checkpoint_0109.json').read_text(encoding='utf-8'));book=record['book']
        cfg=json.loads((source/'config.json').read_text(encoding='utf-8'));plan=cli.validate_config(cfg)
        reply=json.loads((source/'call_137.response.json').read_text(encoding='utf-8'))
        class Exhausted:
            def __init__(self):self.requests=[]
            def complete(self,r):
                self.requests.append(copy.deepcopy(r))
                if len(self.requests)==1:return ModelReply(**reply)
                raise ProviderError('Provider HTTP 402; no retry or redirect',http_status=402)
        with tempfile.TemporaryDirectory(dir=ROOT/'runs')as folder:
            output=Path(folder)/'stopped';provider=Exhausted()
            # Isolate the actual writer/length-edit boundary. Closure replay is
            # already covered independently and may issue unrelated requests.
            with patch('user_runtime.StoryClosure.initialize'),contextlib.redirect_stdout(io.StringIO()):
                result=run_draft_trial(output,provider,plan,resume_book=book)
            self.assertEqual(result['stop_reason'],'PROVIDER_BALANCE_EXHAUSTED')
            self.assertFalse(result['generation_completed']);self.assertEqual(len(provider.requests),2)
            self.assertEqual(result['provider_failure']['http_status'],402)
            state=load_resume(result['resume_checkpoint'],plan)
            self.assertEqual(state['chapters'],book['chapters'])
            partial=state['prepared_events']['15']['stage_realizations'];self.assertEqual(len(partial),1)
            self.assertEqual(partial[0]['text'],json.loads(reply['content'])['new_stage_text'])
            original=copy.deepcopy(partial[0])
            class Restored:
                def __init__(self):self.requests=[]
                def complete(self,r):
                    self.requests.append(copy.deepcopy(r))
                    if 'current_draft'in r.payload:return ModelReply(r.payload['current_draft'],1,1,0)
                    text=''.join(b['statement']for s in r.payload['frozen_events']['scenes']for b in s['beats'])
                    return ModelReply(canonical(dict(new_stage_text=text)),1,1,0)
            recovered=Restored();session=WritingSession(Path(folder)/'resumed',recovered,plan,book=state)
            session.chapter_length_target=3195;packet=copy.deepcopy(session.book['prepared_events']['15'])
            session._realize_stages(packet,'继续第15章',15,[],{})
            self.assertEqual(packet['stage_realizations'][0],original)
            units=[r.payload['stage_task']['unit_number']for r in recovered.requests if 'current_draft'not in r.payload]
            self.assertEqual(units,[2,3])
            self.assertEqual(load_resume(session.latest_checkpoint,plan),session.book)


if __name__=='__main__':unittest.main()
