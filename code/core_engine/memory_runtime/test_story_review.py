"""Evidence-bound editorial review regression, with actual archived failures."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import write_novel
from inf_writer.domain import canonical,ContractError
from inf_writer.models import ModelReply
from memory_runtime.story_review import StoryReviewAgent,adjudicate_issues


def issue():return dict(kind='fact_conflict',description='两条互斥眼色',draft_quote='甲的眼睛是金色。',basis_ref='fact_1',basis_quote='甲的眼睛是灰色。')
def payload():return dict(current_draft='甲的眼睛是金色。',hard_references={'fact_1':'甲的眼睛是灰色。'},
    active_facts=[dict(subject='甲',attribute='eye_color',value='甲的眼睛是灰色。',revision=1,status='active')])
def proposal():return dict(approved=False,issues=[issue()],suggestions=[])
def decision(classification='confirmed'):
    return dict(ref='i001',classification=classification,reason='离线独立判断',draft_evidence=['甲的眼睛是金色。'],basis_evidence=['甲的眼睛是灰色。'])


class Replies:
    def __init__(self,values):self.values=list(values);self.requests=[]
    def complete(self,request):
        self.requests.append(copy.deepcopy(request));value=self.values.pop(0)
        if isinstance(value,Exception):raise value
        return ModelReply(value if isinstance(value,str) else canonical(value),0,0,0)


class EditorialTests(unittest.TestCase):
    def test_real_u_pending_review_shares_evidence_losslessly_under_same_budget(self):
        from memory_runtime.story_review import compact_story_context,expand_story_context,StoryReferenceGateway,REVIEW_PROMPT,REVIEW_RULES
        from inf_writer.light_memory import prepare_review
        saved=json.loads(max((ROOT/'runs/event_first_50000_20261022_u/working').glob('checkpoint_*.json')).read_text(encoding='utf-8'))
        original=prepare_review(saved['book']['review_jobs']['4']);before=copy.deepcopy(original)
        wire=compact_story_context(original)
        self.assertEqual(expand_story_context(wire),original)
        self.assertEqual(original,before)
        self.assertGreater(len(canonical(dict(system=REVIEW_PROMPT+REVIEW_RULES,payload=original)).encode('utf-8')),120000)
        self.assertLess(len(canonical(dict(system=REVIEW_PROMPT+REVIEW_RULES,payload=wire)).encode('utf-8')),120000)
        gateway=Replies([dict(approved=True,issues=[],suggestions=[])]);transport=StoryReferenceGateway(gateway)
        result=StoryReviewAgent(transport).run(saved['book']['review_jobs']['4'],[])
        self.assertTrue(result['approved'])
        self.assertEqual(expand_story_context(gateway.requests[0].payload),original)
        for change in ('source','span','external'):
            damaged=copy.deepcopy(wire)
            key=next(k for k,v in damaged['hard_references'].items() if isinstance(v,dict))
            if change=='source':damaged['current_draft']+='改动'
            elif change=='span':damaged['hard_references'][key]['$story_ref'].update(start=-1,end=2)
            else:damaged['hard_references'][key]['$story_ref']['field']='external_url'
            with self.subTest(change=change),self.assertRaises(ContractError):expand_story_context(damaged)

    def test_actual_missing_suggestions_preserves_original_judgment_without_format_retry(self):
        folder=ROOT/'runs/writing_tiered_30000_20261021_c'
        read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
        original=json.loads(read('call_006.response.json')['content'])
        ctx=read('call_006.request.json')['payload']
        decisions=[dict(ref=f'i{n:03d}',classification='unresolved',reason='离线仅保留待核判断',draft_evidence=[],basis_evidence=[])
            for n in range(1,len(original['issues'])+1)]
        gateway=Replies([original,dict(decisions=decisions)]);trace=[]
        result=StoryReviewAgent(gateway).run(ctx,trace)
        self.assertEqual(result['proposed_issues'],original['issues']);self.assertFalse(result['approved'])
        self.assertEqual(len(gateway.requests),2);self.assertTrue(gateway.requests[1].payload['issue_consistency_review'])
        self.assertTrue(all('repair' not in r.payload for r in gateway.requests))
        self.assertEqual(trace[0]['raw_output'],canonical(original));self.assertTrue(trace[0]['normalizations'])

    def test_approved_proposal_without_advice_needs_no_extra_call(self):
        gateway=Replies([dict(approved=True,issues=[])])
        result=StoryReviewAgent(gateway).run(payload(),[])
        self.assertTrue(result['approved']);self.assertEqual(result['suggestions'],[])
        self.assertEqual(len(gateway.requests),1)

    def test_missing_advice_does_not_bypass_invalid_decision(self):
        gateway=Replies([dict(approved=True,issues=[issue()])]*2)
        with self.assertRaises(ContractError):StoryReviewAgent(gateway).run(payload(),[])
        self.assertEqual(len(gateway.requests),2)

    def test_format_repair_cannot_flip_original_valid_judgment(self):
        original=dict(proposal(),unexpected_metadata=True)
        gateway=Replies([original,dict(approved=True,issues=[],suggestions=[])])
        with self.assertRaisesRegex(ContractError,'protected editorial judgment'):
            StoryReviewAgent(gateway).run(payload(),[])
        self.assertEqual(gateway.requests[1].payload['repair']['protected_judgment'],
            {k:original[k] for k in ('approved','issues')})

    def test_format_repair_can_remove_extra_metadata_with_same_judgment(self):
        gateway=Replies([dict(proposal(),metadata=True),proposal(),dict(decisions=[decision()])])
        result=StoryReviewAgent(gateway).run(payload(),[])
        self.assertFalse(result['approved']);self.assertEqual(result['issues'],proposal()['issues'])

    def test_confirmed_conflict_keeps_original_issue_and_two_sided_evidence(self):
        result=adjudicate_issues(proposal(),payload(),Replies([dict(decisions=[decision()])]),[])
        self.assertFalse(result['approved']);self.assertEqual(result['issues'],[issue()])
        self.assertEqual(result['issue_decisions'][0]['draft_evidence'],['甲的眼睛是金色。'])

    def test_false_alarm_becomes_recorded_suggestion_not_silently_deleted(self):
        result=adjudicate_issues(proposal(),payload(),Replies([dict(decisions=[decision('suggestion')])]),[])
        self.assertTrue(result['approved']);self.assertEqual(result['issues'],[])
        self.assertEqual(result['dismissed_issues'][0]['issue'],issue())
        self.assertEqual(result['proposed_issues'],[issue()])

    def test_unresolved_judgment_does_not_approve(self):
        result=adjudicate_issues(proposal(),payload(),Replies([dict(decisions=[decision('unresolved')])]),[])
        self.assertFalse(result['approved']);self.assertTrue(result['unresolved_issues'])

    def test_bad_reference_missing_coverage_or_fabricated_quotes_stay_unresolved(self):
        bad=[dict(decisions=[]),dict(decisions=[dict(decision(),ref='i999')]),
            dict(decisions=[dict(decision(),basis_evidence=['并不存在'])]),
            dict(decisions=[dict(decision(),draft_evidence=[])]),dict(decisions=[decision(),decision()])]
        for value in bad:
            with self.subTest(value=value):
                gateway=Replies([value,value]);trace=[]
                result=adjudicate_issues(proposal(),payload(),gateway,trace)
                self.assertFalse(result['approved']);self.assertTrue(result['unresolved_issues'])
                self.assertEqual(len(gateway.requests),2)
                self.assertEqual(result['proposed_issues'],[issue()])

    def test_transport_failure_has_no_network_retry_and_preserves_unresolved_issue(self):
        gateway=Replies([RuntimeError('offline outage')])
        result=adjudicate_issues(proposal(),payload(),gateway,[])
        self.assertFalse(result['approved']);self.assertEqual(len(gateway.requests),1)
        self.assertEqual(result['unresolved_issues'][0]['issue'],issue())


if __name__=='__main__':unittest.main(verbosity=2)
