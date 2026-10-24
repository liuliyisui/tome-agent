"""Writing-state regressions drawn from the completed 35k content review."""
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import write_novel
from inf_writer.domain import ContractError,canonical
from inf_writer.models import ModelReply
from memory_runtime.continuity import apply,empty,guard,context_view


def event(identifier,when,quote,mode='historical',objects=None):
    return dict(type='event',id=identifier,date=when,quote=quote,mode=mode,objects=objects or [],after=[])
def obj(identifier='attachment',status='missing',**extra):
    return dict(type='object',id=identifier,label='7-B',form='original',status=status,origin='accident',quote='7-B原件未见。',**extra)


class ContinuityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d=json.loads((ROOT/'docs/analysis/novel_review_20261021_c/paragraphs.json').read_text(encoding='utf-8'))
        cls.paragraphs={p['id']:p['text'] for c in d['chapters'] for p in c['paragraphs']}
    def base(self):
        q=self.paragraphs['C01P002']
        return apply(empty(),[event('accident','1998',q),obj()],q+'\n7-B原件未见。',1)

    def test_real_april_to_march_seal_is_rejected_but_historical_march_is_valid(self):
        april=self.paragraphs['C04P004'];march=self.paragraphs['C12P048']
        state=apply(empty(),[event('sample','2024-04',april,'present')],april,4)
        with self.assertRaisesRegex(ContractError,'backwards'):
            apply(state,[event('seal','2024-03',march,'present')],march,12)
        historic=apply(state,[event('seal','2024-03',march)],march,12)
        self.assertEqual(historic['present_cursor']['date'],'2024-04')

    def test_real_1988_inventory_cannot_be_evidence_for_1998_attachment(self):
        quote=self.paragraphs['C13P021']
        with self.assertRaisesRegex(ContractError,'predates'):
            apply(self.base(),[event('inventory','1988-12',quote,objects=['attachment'])],quote,13)

    def test_missing_original_cannot_be_directly_inspected(self):
        quote=self.paragraphs['C04P008']
        row=dict(type='observe',id='holes',quote=quote,object_id='attachment',method='direct',source_id=None)
        with self.assertRaisesRegex(ContractError,'missing original'):
            apply(self.base(),[row],quote,4)

    def test_photo_is_distinct_from_original_and_requires_its_own_source(self):
        quote='旧照片仍在，来源注明7-B。'
        photo=dict(type='object',id='old_photo',label='7-B页缘照片',form='photo',status='available',origin=None,source='attachment',quote=quote)
        observation=dict(type='observe',id='photo_check',quote=quote,object_id='attachment',method='photo',source_id='old_photo')
        with self.assertRaisesRegex(ContractError,'carrier'):
            apply(self.base(),[observation],quote,4)
        state=apply(self.base(),[photo,observation],quote,4)
        self.assertEqual(state['objects']['attachment']['status'],'missing')

    def test_object_cannot_be_renamed_into_availability_or_reappear_without_event(self):
        row=obj(status='available')
        with self.assertRaisesRegex(ContractError,'availability'):
            apply(self.base(),[row],row['quote'],4)
        row=obj(identifier='new_attachment')
        with self.assertRaisesRegex(ContractError,'stable identity'):
            apply(self.base(),[row],row['quote'],4)

    def test_explicit_find_event_allows_missing_original_to_return(self):
        q='2024年4月发现7-B，原件收回。'
        rows=[event('found','2024-04',q,'present',objects=['attachment']),dict(obj(status='available',event_id='found'),quote=q)]
        self.assertEqual(apply(self.base(),rows,q,4)['objects']['attachment']['status'],'available')

    def test_real_unsigned_youth_cannot_be_one_of_signers(self):
        quote=self.paragraphs['C08P009']
        row=dict(type='handoff',id='box_handoff',quote=quote,signers=['刘广志','跟车青年'],
                 non_signers=['跟车青年'],attendees=['刘广志','跟车青年'],signer_count=2)
        with self.assertRaisesRegex(ContractError,'both sign'):
            apply(empty(),[row],quote,8)
        row['signers']=['刘广志','unknown_sender_signer']
        self.assertEqual(len(apply(empty(),[row],quote,8)['handoffs']['box_handoff']['signers']),2)

    def test_real_seventeen_pages_then_eight_cannot_reset_same_pass(self):
        first=self.paragraphs['C12P063'];second=self.paragraphs['C13P002']
        row=dict(type='progress',id='pages',pass_id='first',completed=17,total=17,quote=first)
        state=apply(empty(),[row],first,12)
        with self.assertRaisesRegex(ContractError,'backwards'):
            apply(state,[dict(row,completed=8,quote=second)],second,13)
        with self.assertRaisesRegex(ContractError,'explicit prose'):
            apply(state,[dict(row,pass_id='new',completed=8,quote=second)],second,13)
        explanation='这是第二轮逐字细核。'
        updated=apply(state,[dict(row,pass_id='detail',completed=8,quote=second,restart_quote=explanation)],second+'\n'+explanation,13)
        self.assertEqual(updated['progress']['pages']['completed'],8)

    def test_later_identity_discovery_is_allowed_without_rewriting_who_signed(self):
        q='库方刘签字，另一签字者不明，青年没签。'
        row=dict(type='handoff',id='handoff',quote=q,signers=['刘','unknown_sender'],non_signers=['青年'],attendees=['青年'],signer_count=2)
        state=apply(empty(),[row],q,1)
        new='查明另一签字者是周。'
        identify=dict(type='identify',id='resolve_sender',quote=new,unknown_id='unknown_sender',person_id='周')
        updated=apply(state,[identify,dict(row,quote=new,signers=['刘','周'])],new,2)
        self.assertEqual(updated['handoffs']['handoff']['signers'],['刘','周'])
        with self.assertRaises(ContractError):apply(state,[dict(identify,person_id='青年')],new,2)

    def test_month_precision_does_not_invent_a_day_and_bad_date_is_rejected(self):
        with self.assertRaises(ContractError):apply(empty(),[event('a','2024-04-01','2024年4月')],'2024年4月',1)
        with self.assertRaises(ContractError):apply(empty(),[event('a','2023-02-29','2023-02-29')],'2023-02-29',1)

    def test_retelling_an_established_event_does_not_make_a_second_event_or_reset_current_date(self):
        q='2024年4月取样。';first=event('sample','2024-04',q,'present')
        state=apply(empty(),[first],q,1)
        retelling='回忆2024年4月取样的经过。'
        state=apply(state,[dict(first,mode='historical',quote=retelling)],retelling,2)
        self.assertEqual(state['present_cursor']['date'],'2024-04');self.assertEqual(len(state['events']),1)

    def test_failed_transaction_does_not_modify_prior_state(self):
        state=self.base();before=canonical(state)
        with self.assertRaises(ContractError):apply(state,[obj(status='available')],'7-B原件未见。',4)
        self.assertEqual(canonical(state),before)
        view=context_view(state,'7-B',max_bytes=1000)
        self.assertLessEqual(len(canonical(view).encode('utf-8')),1000)

    def test_local_writer_patch_preserves_unrelated_paragraph_and_is_not_review(self):
        april='2024年4月完成取样。';bad='2024年3月封存新袋。'
        state=apply(empty(),[event('sample','2024-04',april,'present')],april,4)
        proposed=[event('seal','2024-03',bad,'present')]
        fix='2024年4月封存新袋。';calls=[]
        class Gateway:
            def complete(self,request):
                calls.append(request)
                return ModelReply(canonical(dict(replacements=[dict(paragraph_id='p2',replacement=fix)],
                    continuity_updates=[event('seal','2024-04',fix,'present')])),0,0,0)
        prose='窗外仍在下雨。\n\n'+bad+'\n\n他收好了钥匙。'
        final,new=guard(state,proposed,None,prose,12,[],Gateway(),[])
        self.assertEqual(final,prose.replace(bad,fix));self.assertEqual(new['present_cursor']['date'],'2024-04')
        self.assertEqual(len(calls),1);self.assertEqual(calls[0].role,'writer')

    def test_patch_cannot_clear_conflict_or_change_other_paragraph(self):
        q='2024年4月取样。';bad='2024年3月封存。'
        state=apply(empty(),[event('a','2024-04',q,'present')],q,1)
        row=event('b','2024-03',bad,'present')
        bad_replies=[dict(replacements=[],continuity_updates=[]),
                     dict(replacements=[dict(paragraph_id='p1',replacement='删除其他段落')],continuity_updates=[row])]
        for reply in bad_replies:
            class Gateway:
                def complete(self,request):return ModelReply(canonical(reply),0,0,0)
            with self.assertRaises(ContractError):guard(state,[row],None,'无关内容\n\n'+bad,2,[],Gateway(),[])


if __name__=='__main__':unittest.main(verbosity=2)
