"""Meaning/lifecycle contracts, independent of model quality and storage tier."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import write_novel
from inf_writer.domain import ContractError,canonical,digest,evidence_segments
from inf_writer.models import ModelReply
from inf_writer.memory_meaning import content_key,meaning_view,pending_ids,valid_annotation,verify_meanings
from inf_writer.memory_temporality import annotated
from inf_writer.tiered_memory import empty_memory,apply_delta
from memory_runtime.meaning_organizer import _annotate,_relation,organize


def unit(parts=(1,),kind='current_state',certainty='narration_confirmed',owner=None):
    return dict(part_choices=list(parts),claim_type=kind,epistemic_status=certainty,perspective_owner=owner)


def fixture(old='许闻计划公布材料',new='许闻已经公布材料',kind='task',old_units=None,new_units=None):
    chapters=[dict(number=n,text=t)for n,t in enumerate((old+'。',new+'。'),1)]
    memory=empty_memory();ids=[]
    for n,(claim,storage)in enumerate(((old,kind),(new,'event')),1):
        memory=apply_delta(memory,dict(changes=[dict(op='add',subject='许闻',attribute='record_'+str(n),
            claim=claim,kind=storage,status='planned'if storage=='task'else 'active',
            source_refs=[dict(chapter_number=n,evidence_id=evidence_segments(chapters[n-1]['text'])[0]['id'])])]),chapters,'add'+str(n))
        ids.append(next(i for i in memory['items']if i not in ids))
    for mid,units in zip(ids,(old_units or [unit(kind='task'if kind=='task'else 'current_state')],new_units or [unit(kind='historical_event')])):
        row=memory['items'][mid];row['meaning_annotation']=_annotate(row,units,'原文含义')
    return memory,chapters,ids


def relate(memory,chapters,ids,kind='completes',old_parts=(1,),new_parts=(1,)):
    proof=memory['items'][ids[1]]['sources'][0]
    return _relation(memory,dict(earlier_memory_choice=1,later_memory_choice=2,relation_type=kind,
        earlier_part_choices=list(old_parts),later_part_choices=list(new_parts),evidence_choices=[1],reason='实际后续原文'),
        {1:ids[0],2:ids[1]},[proof],chapters)


class MeaningTests(unittest.TestCase):
    def test_completion_keeps_quote_history_and_is_idempotent(self):
        m,c,ids=fixture();original=copy.deepcopy(m);r=relate(m,c,ids)
        self.assertEqual(m,original)
        self.assertEqual(meaning_view(r['items'][ids[0]])['task_state'],'completed')
        self.assertEqual(r['items'][ids[0]]['claim'],m['items'][ids[0]]['claim'])
        self.assertTrue(r['history']);self.assertEqual(relate(r,c,ids),r)
        self.assertTrue(verify_meanings(r,c))

    def test_partial_completion_preserves_unrelated_current_state(self):
        m,c,ids=fixture(old='许闻仍在岗；许闻计划公布材料',kind='state',
            old_units=[unit(),unit((2,),kind='intention')])
        r=relate(m,c,ids,old_parts=(2,));view=meaning_view(r['items'][ids[0]])
        self.assertTrue(view['units'][0]['usable_as_current_fact'])
        self.assertEqual(view['units'][1]['validity'],'historical')
        self.assertEqual(view['task_state'],'completed');self.assertTrue(verify_meanings(r,c))

    def test_unverified_report_and_guess_cannot_complete_or_replace(self):
        for certainty,kind,owner in [('reported_unverified','character_statement','许闻'),('hypothesis','character_belief','许闻')]:
            m,c,ids=fixture(new='许闻猜想材料可能已经公布',new_units=[unit(kind=kind,certainty=certainty,owner=owner)])
            with self.assertRaises(ContractError):relate(m,c,ids)
            self.assertEqual(meaning_view(m['items'][ids[0]])['task_state'],'planned')

    def test_new_plan_cannot_prove_completion(self):
        m,c,ids=fixture(new='许闻打算明天公布材料',new_units=[unit(kind='intention')])
        with self.assertRaises(ContractError):relate(m,c,ids)

    def test_explicit_cancellation_is_distinct_from_completion(self):
        m,c,ids=fixture(new='许闻决定取消公布材料');r=relate(m,c,ids,'cancels')
        self.assertEqual(meaning_view(r['items'][ids[0]])['task_state'],'cancelled')
        self.assertNotEqual(r['items'][ids[0]]['claim'],r['items'][ids[1]]['claim'])

    def test_topic_link_does_not_cancel_task(self):
        m,c,ids=fixture(new='许闻先去查看闸门');r=relate(m,c,ids,'same_topic')
        self.assertEqual(meaning_view(r['items'][ids[0]])['task_state'],'planned')

    def test_refutation_preserves_old_perspective(self):
        m,c,ids=fixture(old='许闻怀疑材料被梁策取走',new='核查确认材料一直在许闻桌上',kind='knowledge',
            old_units=[unit(kind='character_belief',certainty='hypothesis',owner='许闻')])
        r=relate(m,c,ids,'refutes');u=meaning_view(r['items'][ids[0]])['units'][0]
        self.assertEqual((u['perspective_owner'],u['epistemic_status'],u['validity']),('许闻','hypothesis','historical'))

    def test_historical_event_cannot_be_erased(self):
        m,c,ids=fixture(kind='event',old_units=[unit(kind='historical_event')])
        with self.assertRaises(ContractError):relate(m,c,ids,'supersedes')

    def test_whole_units_preserve_negation_context(self):
        m,c,ids=fixture(old='许闻不知道；材料是否已经公布',kind='knowledge',
            old_units=[unit((1,2),kind='character_belief',certainty='uncertain',owner='许闻')])
        with self.assertRaises(ContractError):relate(m,c,ids,'refutes',old_parts=(2,))

    def test_conflict_retains_both_and_later_proof_resolves_it(self):
        m,c,ids=fixture(old='许闻目前在岗',new='许闻已被停职',kind='knowledge',new_units=[unit()])
        r=relate(m,c,ids,'conflicts')
        self.assertTrue(all(not meaning_view(r['items'][i])['usable_as_current_fact']for i in ids))
        r=relate(r,c,ids,'supersedes')
        self.assertTrue(meaning_view(r['items'][ids[1]])['usable_as_current_fact'])
        self.assertTrue(any(v.get('resolved_by')for v in r['meaning_relations'].values()))
        self.assertTrue(verify_meanings(r,c))

    def test_historical_information_cannot_create_new_current_conflict(self):
        m,c,ids=fixture();r=relate(m,c,ids)
        with self.assertRaises(ContractError):relate(r,c,ids,'conflicts')

    def test_demotion_and_recall_preserve_completed_status(self):
        m,c,ids=fixture();r=relate(m,c,ids);mid=ids[0];before=meaning_view(r['items'][mid])
        for n,op in enumerate(('demote','recall')):
            r=apply_delta(r,dict(changes=[dict(op=op,id=mid,expected_revision=r['items'][mid]['revision'],reason='测试存储移动')]),c,'move'+str(n))
        self.assertEqual(meaning_view(r['items'][mid]),before);self.assertTrue(valid_annotation(r['items'][mid]))

    def test_value_update_invalidates_annotation_preserves_lineage(self):
        m,c,ids=fixture(kind='state');mid=ids[0];oldkey=content_key(m['items'][mid])
        r=apply_delta(m,dict(changes=[dict(op='update',id=mid,expected_revision=1,reason='后续变化',claim='许闻已经公开材料',status='active',
            source_refs=[dict(chapter_number=2,evidence_id=m['items'][ids[1]]['sources'][0]['evidence_id'])])]),c,'update')
        self.assertIn(mid,pending_ids(r));self.assertFalse(meaning_view(r['items'][mid])['assessed'])
        self.assertEqual(meaning_view(r['items'][mid])['previous_content_sha256'],oldkey)
        self.assertTrue(valid_annotation(r['history'][-1]['item']));self.assertTrue(verify_meanings(r,c))

    def test_unknown_missing_duplicate_parts_are_rejected(self):
        m,c,ids=fixture(old='许闻仍在岗；许闻计划公布材料',kind='state',old_units=[unit((1,2))]);row=m['items'][ids[0]]
        for units in ([unit((9,))],[unit()],[unit((1,2)),unit((2,))]):
            with self.assertRaises(ContractError):_annotate(row,units,'测试')

    def test_partially_valid_response_retains_good_peer_during_retry(self):
        m,c,ids=fixture();[r.pop('meaning_annotation')for r in m['items'].values()];calls=[]
        class Provider:
            def complete(self,request):
                calls.append(copy.deepcopy(request.payload));rows=[]
                for choice in request.payload['annotation_required_choices']:
                    row=next(r for r in request.payload['memory_records']if r['memory_choice']==choice)
                    positions=[p['part_choice']for p in row['parts']]
                    if len(calls)==1 and choice==1:positions=[999]
                    rows.append(dict(memory_choice=choice,units=[unit(positions,kind='unclassified',certainty='not_assessed')],reason='保守标注'))
                return ModelReply(canonical(dict(annotations=rows,relations=[])),1,1,0)
        trace=[];r=organize(m,c,2,Provider(),trace,max_batches=1)
        self.assertEqual(len(calls),2);self.assertEqual(calls[1]['annotation_required_choices'],[1])
        self.assertTrue(all(row['source_evidence_choices']for row in calls[0]['memory_records']))
        self.assertTrue(any(row['accepted_units']for row in calls[1]['memory_records']))
        self.assertEqual(pending_ids(r),[]);self.assertTrue(verify_meanings(r,c))

    def test_service_and_internal_failures_are_nonblocking_and_explicit(self):
        m,c,ids=fixture();m['items'][ids[0]].pop('meaning_annotation')
        class Offline:
            def complete(self,request):raise RuntimeError('offline')
        trace=[];r=organize(m,c,2,Offline(),trace)
        self.assertEqual(r['items'],m['items']);self.assertIn(ids[0],r['meaning_pending_ids'])
        with patch('memory_runtime.meaning_organizer._organize',side_effect=RuntimeError('unexpected')):
            r=organize(m,c,2,Offline(),trace)
        self.assertEqual(r['items'],m['items']);self.assertEqual(trace[-1]['status'],'DEFERRED')

    def test_tampered_annotation_relation_and_prose_are_rejected(self):
        m,c,ids=fixture();r=relate(m,c,ids)
        for change in ('annotation','relation','prose'):
            bad=copy.deepcopy(r);chapters=copy.deepcopy(c)
            if change=='annotation':bad['items'][ids[0]]['meaning_annotation']['units'][0]['epistemic_status']='hypothesis'
            elif change=='relation':next(iter(bad['meaning_relations'].values()))['later']['memory_id']='invented'
            else:chapters[1]['text']='已更改'
            with self.assertRaises(ContractError):verify_meanings(bad,chapters)

    def test_raw_excerpt_and_unassessed_rows_are_never_current_fact(self):
        m,c,ids=fixture();row=copy.deepcopy(m['items'][ids[0]])
        row['kind']='prose_excerpt';self.assertFalse(meaning_view(row)['usable_as_current_fact'])
        row['kind']='state';row.pop('meaning_annotation');self.assertFalse(meaning_view(row)['usable_as_current_fact'])

    def test_unknown_speaker_stays_unknown_without_becoming_fact(self):
        m,c,ids=fixture(kind='knowledge',old_units=[unit(kind='character_statement',certainty='reported_unverified')])
        u=meaning_view(m['items'][ids[0]])['units'][0]
        self.assertEqual(u['perspective_resolution'],'unknown');self.assertFalse(u['usable_as_current_fact'])

    def test_unbound_speaker_name_downgrades_to_unknown_without_inventing_fact(self):
        m,c,ids=fixture(kind='knowledge',old_units=[unit(owner='原文没有的人')])
        row=m['items'][ids[0]];u=meaning_view(row)['units'][0]
        self.assertIsNone(u['perspective_owner']);self.assertEqual(u['epistemic_status'],'uncertain')
        self.assertFalse(u['usable_as_current_fact']);self.assertTrue(row['meaning_annotation']['normalizations'])

    def test_root_extra_field_does_not_discard_valid_annotations(self):
        m,c,ids=fixture();[r.pop('meaning_annotation')for r in m['items'].values()]
        class Provider:
            def complete(self,request):
                rows=[dict(memory_choice=i,units=[unit(kind='unclassified',certainty='not_assessed')],reason='原文')for i in request.payload['annotation_required_choices']]
                return ModelReply(canonical(dict(annotations=rows,relations=[],extra='不进入记忆')),1,1,0)
        r=organize(m,c,2,Provider(),[],max_batches=1)
        self.assertEqual(pending_ids(r),[]);self.assertNotIn('extra',r)

    def test_failed_relation_is_queued_then_reconsidered_without_expiring_task(self):
        m,c,ids=fixture();m['items'][ids[0]].pop('meaning_annotation')
        class Bad:
            def complete(self,request):
                rows=request.payload['memory_records'];old=next(r['memory_choice']for r in rows if r['storage_kind']=='task')
                new=next(r['memory_choice']for r in rows if r['storage_kind']=='event')
                value=dict(annotations=[dict(memory_choice=old,units=[unit(kind='task')],reason='原文计划')],relations=[dict(
                    earlier_memory_choice=old,later_memory_choice=new,relation_type='completes',earlier_part_choices=[999],
                    later_part_choices=[1],evidence_choices=[1],reason='错误片段')])
                return ModelReply(canonical(value),1,1,0)
        trace=[];r=organize(m,c,2,Bad(),trace,max_batches=1)
        self.assertTrue(r['meaning_review_jobs']);self.assertTrue(pending_ids(r))
        class Reconsider:
            def complete(self,request):
                self.assert_review=request.payload['relationship_review']
                return ModelReply(canonical(dict(annotations=[],relations=[])),1,1,0)
        p=Reconsider();r=organize(r,c,2,p,[],max_batches=1)
        self.assertTrue(p.assert_review);self.assertFalse(r['meaning_review_jobs'])
        self.assertFalse(pending_ids(r));self.assertEqual(meaning_view(r['items'][ids[0]])['task_state'],'planned')

    def test_organized_actual_book_fits_writer_context_and_restores(self):
        from memory_runtime.writing import WritingSession,load_resume
        from memory_runtime.meaning_organizer import reference_meanings
        root=Path(write_novel.ROOT);source=root/'runs/state_recovery_real_20261025_a'
        book=json.loads((source/'final_state.json').read_text(encoding='utf-8'))
        plan=write_novel.validate_config(json.loads((source/'config.json').read_text(encoding='utf-8')))
        class Provider:
            def complete(self,request):
                rows=[dict(memory_choice=i,units=[unit([p['part_choice']for p in next(r for r in request.payload['memory_records']if r['memory_choice']==i)['parts']],
                    kind='mixed',certainty='mixed')],reason='仅测试输入容量，保守保留混合性质')for i in request.payload['annotation_required_choices']]
                return ModelReply(canonical(dict(annotations=rows,relations=[])),1,1,0)
        before=copy.deepcopy(book);trace=[];book['memory']=organize(book['memory'],book['chapters'],3,Provider(),trace,max_batches=8)
        with tempfile.TemporaryDirectory(dir=root/'runs')as tmp:
            s=WritingSession(Path(tmp)/'session',Provider(),plan,book=book)
            context=s.context('测试输入','许闻 梁策 材料 便条')
            self.assertTrue(all(r['memory_kind']!='prose_excerpt'for r in context['retrieved_memory']))
            self.assertTrue(all('meaning'in r for r in context['retrieved_memory']))
            self.assertLessEqual(len(canonical(context).encode('utf-8')),84000)
            self.assertEqual(load_resume(s.latest_checkpoint,plan),s.book)
        self.assertEqual(book['chapters'],before['chapters']);self.assertEqual(book['writing_state'],before['writing_state'])
        self.assertTrue(reference_meanings(book))


if __name__=='__main__':unittest.main()
