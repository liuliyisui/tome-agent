"""Real erroneous paragraph replay plus deterministic arithmetic/atomic binding tests."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import write_novel
from inf_writer.domain import ContractError,canonical
from inf_writer.models import ModelReply
from memory_runtime.time_calculation import calculate,render,unbound_claims,write_with_calculations


class Agent:
    def __init__(self,prose,repair=None,requests=()):
        self.prose=prose;self.repair=repair;self.time_requests=list(requests);self.gateway=self;self.calls=[]
    def run(self,context,trace):
        return dict(text=self.prose,time_calculations=self.time_requests)
    def complete(self,request):
        self.calls.append(copy.deepcopy(request))
        if isinstance(self.repair,Exception):raise self.repair
        return ModelReply(canonical(self.repair),1,1,0)


class TimeTests(unittest.TestCase):
    def test_both_real_o_time_requests_report_the_invalid_row_without_mutation(self):
        folder=ROOT/'runs/event_first_50000_20261022_o/working'
        record=json.loads(max(folder.glob('checkpoint_*.json')).read_text(encoding='utf-8'))
        proposals=[json.loads(r['raw_output']) for r in record['trace'] if r.get('role')=='planner' and r.get('status')=='ACCEPTED']
        self.assertEqual(len(proposals),2)
        for proposal in proposals:
            original=copy.deepcopy(proposal)
            with self.assertRaises(ContractError) as caught:calculate(proposal['time_calculations'])
            self.assertEqual(caught.exception.repair_details['issues'][0]['path'],'time_calculations[0]')
            self.assertEqual(proposal,original)

    def test_vague_time_request_has_exact_path_and_no_guessed_result(self):
        requests=[dict(id='good',kind='interval',start='16:41',end='16:45'),
            dict(id='meet',kind='provisional_interval',expression='后天傍晚',result='日落前后')]
        original=copy.deepcopy(requests)
        with self.assertRaises(ContractError) as caught:calculate(requests)
        details=caught.exception.repair_details
        self.assertEqual(details['code'],'TIME_REQUEST_ERRORS')
        self.assertEqual([r['path'] for r in details['issues']],['time_calculations[1]'])
        self.assertEqual(set(details['request_schemas']),{'interval','duration','advance'})
        self.assertEqual(requests,original)

    def test_interval_exact_and_rebinding_changes_result(self):
        for end,expected in [('16:45',4),('16:43',2),('16:41',0)]:
            self.assertEqual(calculate([dict(id='fax',kind='interval',start='16:41',end=end)])[0]['minutes'],expected)

    def test_cross_midnight_requires_explicit_day(self):
        with self.assertRaises(ContractError):calculate([dict(id='a',kind='interval',start='23:58',end='00:02')])
        self.assertEqual(calculate([dict(id='a',kind='interval',start='23:58',end='00:02',day_offset=1)])[0]['minutes'],4)

    def test_dated_leap_day_and_year_boundary(self):
        for start,end in [('2024-02-29T23:58','2024-03-01T00:02'),('2024-12-31T23:58','2025-01-01T00:02')]:
            self.assertEqual(calculate([dict(id='a',kind='interval',start=start,end=end)])[0]['minutes'],4)

    def test_invalid_inputs_do_not_gain_implicit_interpretations(self):
        cases=[dict(start='24:01',end='00:03'),dict(start='16:41',end='2024-01-01T16:45'),
               dict(start='2023-02-29T16:41',end='2023-03-01T16:45'),dict(start='16:41',end='16:45',day_offset=True)]
        for row in cases:
            with self.subTest(row=row),self.assertRaises(ContractError):calculate([dict(id='a',kind='interval',**row)])

    def test_advance_and_duration_require_their_own_endpoints(self):
        advance=calculate([dict(id='gate',kind='advance',actual='21:11',scheduled='21:15')])
        duration=calculate([dict(id='gate',kind='duration',opened='21:11',closed='21:15')])
        self.assertEqual(render('提前[[time:gate]]',advance),'提前四分钟')
        self.assertEqual(render('持续了[[time:gate]]',duration),'持续了四分钟')
        for kind in ('advance','duration'):
            with self.assertRaises(ContractError):calculate([dict(id='gate',kind=kind,start='21:07',end='21:11')])

    def test_interval_cannot_render_as_advance_or_duration(self):
        rows=calculate([dict(id='gate',kind='interval',start='21:07',end='21:11')])
        for text in ('提前[[time:gate]]','持续了[[time:gate]]','共开了[[time:gate]]'):
            with self.assertRaises(ContractError):render(text,rows)

    def test_duplicate_id_cannot_overwrite_locked_input(self):
        row=dict(id='fax',kind='interval',start='16:41',end='16:45')
        with self.assertRaises(ContractError):calculate([dict(row,end='16:43')],calculate([row]))

    def test_wrong_formula_inputs_cannot_override_explicit_prose_endpoints(self):
        rows=calculate([dict(id='fax',kind='interval',start='16:41',end='16:43')])
        with self.assertRaisesRegex(ContractError,'literal start/end'):
            render('16:41到16:45，相隔[[time:fax]]。',rows)
        good=calculate([dict(id='fax',kind='interval',start='16:41',end='16:45')])
        self.assertEqual(render('16:41到16:45，相隔[[time:fax]]。',good),'16:41到16:45，相隔四分钟。')

    def test_unknown_token_or_model_supplied_result_is_not_accepted(self):
        with self.assertRaises(ContractError):render('相隔[[time:unknown]]',[])
        with self.assertRaises(ContractError):render('相隔[[time:bad-id]]',[])
        with self.assertRaises(ContractError):calculate([dict(id='fax',kind='interval',start='16:41',end='16:45',minutes=2)])

    def test_bound_prose_needs_no_extra_call_and_temporary_tokens_never_escape(self):
        rows=calculate([dict(id='fax',kind='interval',start='16:41',end='16:45')])
        agent=Agent('[[time:fax.start]]到[[time:fax.end]]，相隔[[time:fax]]。')
        draft,bindings,_=write_with_calculations(agent,dict(computed_times=rows),[])
        self.assertEqual(draft,'16:41到16:45，相隔四分钟。');self.assertFalse(agent.calls)
        self.assertEqual(bindings,rows)

    def test_real_second_chapter_error_is_detected_and_only_amount_spans_change(self):
        source=json.loads((ROOT/'docs/analysis/novel_review_20261021_c/paragraphs.json').read_text(encoding='utf-8'))
        paragraph=next(p['text'] for c in source['chapters'] for p in c['paragraphs'] if p['id']=='C02P008')
        claims=unbound_claims(paragraph);self.assertEqual(len(claims),3)
        reply=dict(time_calculations=[dict(id='fax',kind='interval',start='16:41',end='16:45')],
                   bindings=[dict(claim_id=c['id'],calculation_id='fax') for c in claims])
        agent=Agent(paragraph,reply);trace=[]
        draft,rows,_=write_with_calculations(agent,{},trace)
        self.assertEqual(draft,paragraph.replace('两分钟','四分钟'))
        self.assertEqual(rows[0]['minutes'],4);self.assertEqual(len(agent.calls),1)
        self.assertEqual(agent.calls[0].role,'writer');self.assertEqual(trace[0]['raw_draft'],paragraph)

    def test_local_binding_cannot_drop_duplicate_or_invent_claims(self):
        prose='16:41到16:45，相隔两分钟。这两分钟很关键。'
        rows=[dict(id='fax',kind='interval',start='16:41',end='16:45')]
        cases=[[],[dict(claim_id='u1',calculation_id='fax')],
               [dict(claim_id='u1',calculation_id='fax')]*2,
               [dict(claim_id='u1',calculation_id='missing'),dict(claim_id='u2',calculation_id='fax')]]
        for bindings in cases:
            with self.subTest(bindings=bindings),self.assertRaises(ContractError):
                write_with_calculations(Agent(prose,dict(time_calculations=rows,bindings=bindings)),{},[])

    def test_unsupported_or_outage_never_approves_unchecked_arithmetic(self):
        for reply in (dict(unresolved='缺少起止时刻'),RuntimeError('offline outage')):
            agent=Agent('中间隔了两分钟。',reply);trace=[]
            with self.assertRaises((ContractError,RuntimeError)):write_with_calculations(agent,{},trace)
            self.assertEqual(len(agent.calls),1)
            self.assertEqual(trace[0]['raw_draft'],'中间隔了两分钟。')

    def test_plain_wait_and_reported_advance_are_not_invented_calculations(self):
        self.assertEqual(unbound_claims('他想等两分钟。报告原话是“提前四分钟开闸”。'),[])
        agent=Agent('雨停了。');self.assertEqual(write_with_calculations(agent,{},[])[0],'雨停了。')
        self.assertFalse(agent.calls)


if __name__=='__main__':unittest.main(verbosity=2)
