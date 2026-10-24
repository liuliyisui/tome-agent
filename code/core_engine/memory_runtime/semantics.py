"""Evidence review before critical memory mutations become authoritative.

Review is model judgment, not a proof. Unsupported mutations are explicitly
withheld; the prior record and the raw proposal remain available for audit.
"""
import copy
from inf_writer.domain import ContractError,canonical,strict_json,fields,evidence_segments
from inf_writer.models import ModelRequest
from inf_writer.tiered_memory import apply_delta,wire_item
from inf_writer.memory_temporality import annotated
from inf_writer.temporal_transport import decode
from .pipeline import normalize

SYSTEM=(
    '独立复核记忆变更是否由所给本章证据明确支持。只输出JSON decisions数组，每项ref、decision、reason。'
    'decision只能accept或keep_current，每个ref恰好一次。不能为让流程继续而通过。'
    '任务取消必须有明确放弃/取消/被取代依据，任务完成必须证明该行动已执行。'
    '先查另一条线索、当前关注点变化、暂时未提及、又增加新计划，都不等于取消或完成旧任务。'
    '旧认识失效也必须有直接新依据；历史事件曾发生过，不因后续进展而失效。'
    '复合记录只判断所给变更片段，不牵连其它内容，不能安全判断就keep_current。'
    'keep_current表示不应用这项提案、保留之前状态，不编造替代事实。'
    '根据引用证据判断，不把提案的reason本身当作事实依据。'
    '对新增与更新的事实陈述逐点核查引用是否直接支持；容器类别由程序固定，不靠改类别解决证据不足。'
)


def evidence(proposal,chapters,number):
    catalog={r['id']:r['text'] for r in evidence_segments(chapters[number-1]['text'])}
    return [dict(ref,quote=catalog[ref['evidence_id']]) for ref in proposal['source_refs']]


def review(gateway,proposals,number,phase,trace):
    if not proposals:return {}
    payload=dict(chapter_number=number,memory_mutation_review=phase,proposals=proposals)
    expected={p['ref'] for p in proposals}
    for attempt in range(2):
        if len(canonical(dict(system=SYSTEM,payload=payload)).encode('utf-8'))>120000:
            raise ContractError('Semantic mutation review exceeds context bound')
        reply=gateway.complete(ModelRequest('reviewer',SYSTEM,copy.deepcopy(payload),8192))
        entry=dict(role='memory_mutation_review',phase=phase,attempt=attempt+1,raw_output=reply.content)
        trace.append(entry)
        try:
            parsed,notes=normalize(strict_json(reply.content));fields(parsed,('decisions',))
            if not isinstance(parsed['decisions'],list):raise ContractError('Decisions must be a list')
            decisions={}
            for row in parsed['decisions']:
                fields(row,('ref','decision','reason'))
                if row['ref'] not in expected or row['ref'] in decisions:raise ContractError('Invalid or duplicate review reference')
                if row['decision'] not in ('accept','keep_current') or not isinstance(row['reason'],str) or not row['reason'].strip():
                    raise ContractError('Invalid semantic disposition')
                decisions[row['ref']]=row
            if set(decisions)!=expected:raise ContractError('Semantic review coverage incomplete')
            entry.update(status='REVIEWED',decisions=parsed['decisions'],normalizations=notes,semantic_certification=False)
            return decisions
        except (ContractError,TypeError,KeyError) as exc:
            entry.update(status='REJECTED',error=str(exc))
            if attempt:raise ContractError('Semantic review interface failed: '+str(exc)) from exc
            payload['repair']=dict(error=str(exc),required_refs=sorted(expected),previous_output=reply.content,
                instruction='修复格式和覆盖范围，不改变证据标准。')


def keep_notes(candidate,notes):
    if notes:candidate.setdefault('withheld_memory_mutations',[]).extend(notes)
    return candidate


def guard_extraction(before,candidate,chapters,number,gateway,trace):
    entry=next(t for t in reversed(trace) if t['role']=='memory' and t.get('status')=='ACCEPTED')
    delta=strict_json(entry['raw_output']);proposals=[];indices={}
    for index,op in enumerate(delta['changes']):
        if op.get('op') not in ('add','update'):continue
        ref=f'c{len(proposals)+1:03d}';indices[index]=ref
        old=before['items'].get(op.get('id'))
        if old and (op['claim'],op['status'])==(old['claim'],old['status']):
            indices.pop(index)
            continue
        proposals.append(dict(ref=ref,proposed_change=op,previous_record=wire_item(old) if old else None,
            cited_evidence=evidence(op,chapters,number)))
    decisions=review(gateway,proposals,number,'record_updates',trace)
    withheld=[dict(chapter=number,phase='record_updates',proposal=op,review=decisions[indices[index]],
        disposition='Not applied; previous record retained') for index,op in enumerate(delta['changes'])
        if index in indices and decisions[indices[index]]['decision']=='keep_current']
    if not withheld:return candidate
    filtered=copy.deepcopy(delta)
    filtered['changes']=[op for index,op in enumerate(delta['changes']) if index not in indices or decisions[indices[index]]['decision']=='accept']
    if not filtered['changes']:filtered['no_change_reason']='Independent evidence review withheld unsupported task status proposals'
    result=apply_delta(before,filtered,chapters,f'chapter-memory-{number}');result['processed_through']=number
    entry['status']='STRUCTURE_ACCEPTED_PENDING_SEMANTIC'
    trace.append(dict(role='memory',status='ACCEPTED',chapter_number=number,raw_output=canonical(filtered),
        independent_evidence_gate=True,withheld=len(withheld),semantic_certification=False))
    return keep_notes(result,withheld)


def guard_temporal(before,candidate,chapters,number,gateway,trace):
    entries=[t for t in trace if t['role']=='temporal' and t.get('status')=='ACCEPTED']
    if not entries:return candidate
    entry=entries[-1];raw,_=normalize(strict_json(entry['raw_output']));decoded=decode(raw,entry['wire_bindings'])
    proposals=[];indices={}
    for oi,op in enumerate(decoded['changes']):
        old=before['items'][op['id']];parts={p['id']:p for p in annotated(old)['temporality']['parts']}
        for ri,resolution in enumerate(op['resolutions']):
            ref=f't{len(proposals)+1:03d}';indices[oi,ri]=ref
            proposals.append(dict(ref=ref,previous_record=wire_item(old),
                proposed_resolution=resolution,selected_parts=[parts[pid] for pid in resolution['part_ids']],
                replacement_records=[wire_item(before['items'][identifier]) for identifier in resolution['replacement_ids']],
                cited_evidence=evidence(resolution,chapters,number)))
    decisions=review(gateway,proposals,number,'temporal_parts',trace)
    withheld=[];operations=[]
    for oi,op in enumerate(decoded['changes']):
        approved=[]
        for ri,resolution in enumerate(op['resolutions']):
            decision=decisions[indices[oi,ri]]
            if decision['decision']=='accept':approved.append(resolution)
            else:withheld.append(dict(chapter=number,phase='temporal_parts',id=op['id'],proposal=resolution,
                review=decision,disposition='Not applied; previous portions retained'))
        if approved:operations.append(dict(op,resolutions=approved))
    if not withheld:return candidate
    delta={k:v for k,v in decoded.items() if k not in ('checked_ids','unresolved')};delta['changes']=operations
    if not operations:delta['no_change_reason']='Independent evidence review retained unsupported prior portions'
    result=apply_delta(before,delta,chapters,f'chapter-time-{number}');result['temporal_processed_through']=number
    if 'uncertain_prior_arrangements' in candidate:
        result['uncertain_prior_arrangements']=copy.deepcopy(candidate['uncertain_prior_arrangements'])
    entry['status']='STRUCTURE_ACCEPTED_PENDING_SEMANTIC'
    trace.append(dict(role='temporal',status='ACCEPTED',chapter_number=number,
        raw_output=canonical(dict(delta,checked_ids=decoded['checked_ids'])),wire_bindings=entry['wire_bindings'],
        independent_evidence_gate=True,withheld=len(withheld),semantic_certification=False))
    return keep_notes(result,withheld)
