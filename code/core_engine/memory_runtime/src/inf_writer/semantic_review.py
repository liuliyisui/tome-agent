"""Explicit evidence channels and coverage mappings; NOT semantic truth checking."""
import copy
from .domain import ContractError,canonical,digest,evidence_segments,fields,text

PROMPT=(
    '语义审核政策v3：分两步完成同一审核。先检查候选claim与其绑定证据，再独立扫coverage_units的全部正文。'
    'semantic_packets的bindings.index指review_items相应source.evidence的0基位置，旧source.quote使用index=0。'
    'context_refs对应semantic_contexts的真实邻近片段，只供speaker或coreference消解。'
    '对话的“我”可通过同段或相邻说话者标签识别，不因引文没重复姓名就拒绝；自述仍与叙述者客观确认区分。'
    '上下文可以确定谁在说话，但不能补充候选缺失的实体、数量、位置、行为结果等新事实。'
    '对象、数量、位置或因果关系不同，不因主题相似就视作相互支持；引文不完整应partial，不可因正文别处出现就supported。'
    '每个support_checks项在原claim_ref/claim/status/reason外必须含evidence对象：'
    'bindings=[{index:0,quote:绑定引文的逐字子串}]，context=[{ref:context_ref,quote:该邻近片段的逐字子串,purpose:speaker或coreference}]。'
    'supported/partial必须有绑定引文；context可为空，不能把context的独有内容放入bindings。'
    '顶层另有coverage_checks数组，每个coverage_units.unit_ref恰好一次，含unit_ref/reason/facts。'
    'facts列该单元中影响后续的所有重要事实，不只列候选已有事实；含draft_quote/status/memory_refs/reason。'
    'draft_quote逐字来自该单元；status为covered/missing/uncertain/not_needed；'
    'covered时memory_refs=[{ref:coverage_targets中的键,quote:该目标记忆值中的逐字子串}]，并说明语义对应。'
    '其余status的memory_refs为空。只有无重要新约束时facts可为空，reason要解释，不用空数组跳过重要事件。'
    '正文写过不等于记忆记过。拒绝、承诺、取得/失去物品、限制与新线索均按后续影响判断，不预先判本章真假。'
    'coverage_targets只含最终候选及未被替换的现有记忆值；正文和source证据不算记忆值，不虚构映射。'
    '有missing事实时coverage_status=missing并给完整引用和omission说明的memory_omission问题；'
    '无missing但有uncertain时coverage_status=uncertain；其余为sufficient。'
    '所有supported与covered仍须实际语义支持，编号/引文合法不代表判断正确；不自动批准，不编造证据或遗漏。'
    '输出保持approved/issues/suggestions/memory_check/support_checks，另加coverage_checks，不增加模型调用。')


def bindings(item):
    source=item['source']
    return source.get('evidence') or ([dict(quote=source['quote'])] if source.get('quote') else [])


def prepare(context):
    """Derive windows from the recorded source chapter, never relocate evidence."""
    payload=copy.deepcopy(context)
    chapters={row['number']:row['text'] for row in payload.get('recent_chapters',[])}
    chapters[payload['chapter_number']]=payload['current_draft']
    pool={};packets=[]
    for item in payload['review_items']:
        source=item['source'];number=source['chapter_number'];body=chapters.get(number)
        if body is not None and source.get('chapter_sha256') and digest(body)!=source['chapter_sha256']:
            raise ContractError('Semantic context source chapter hash mismatch')
        segments=evidence_segments(body) if body is not None else []
        entries=[]
        for index,ev in enumerate(bindings(item)):
            quote=text(ev.get('quote'),'Binding quote');found=[]
            if body is not None:
                for j,segment in enumerate(segments):
                    if ev.get('evidence_id') and segment['id']!=ev['evidence_id']:continue
                    if quote in segment['text']:found.append(j)
                if not found and not ev.get('evidence_id'):
                    start=body.find(quote)
                    while start!=-1:
                        found.extend(j for j,s in enumerate(segments) if s['start']<start+len(quote) and s['end']>start)
                        start=body.find(quote,start+1)
                    found=sorted(set(found))
                if not found:raise ContractError('Recorded binding absent from source chapter/segment')
            refs=[]
            for j in found:
                for k in range(max(0,j-1),min(len(segments),j+2)):
                    segment=segments[k];ref=f'ch{number}_{segment["id"]}'
                    pool.setdefault(ref,dict(ref=ref,chapter_number=number,chapter_sha256=digest(body),**segment))
                    if ref not in refs:refs.append(ref)
            entries.append(dict(index=index,context_refs=refs))
        packets.append(dict(claim_ref=item['claim_ref'],bindings=entries,
            context_status='available' if body is not None else 'source_chapter_outside_current_context'))
    segments=evidence_segments(payload['current_draft'])
    units=[dict(unit_ref=f'unit_{i//4+1}',segment_ids=[s['id'] for s in segments[i:i+4]],
                start=segments[i]['start'],end=segments[min(i+3,len(segments)-1)]['end'])
        for i in range(0,len(segments),4)]
    changed={(r['subject'],r['attribute']) for r in payload['memory_changes']}
    targets={f'fact_{i}':canonical(r['value']) for i,r in enumerate(payload.get('active_facts',[]),1)
        if (r['subject'],r['attribute']) not in changed}
    targets.update({r['claim_ref']:r['claim'] for r in payload['review_items']
        if r['change_kind'] not in ('remove','retire') and
        payload['memory_changes'][int(r['claim_ref'].split('/')[0].split('_')[1])-1]['action']!='retire'})
    derived=dict(semantic_packets=packets,semantic_contexts=list(pool.values()),coverage_units=units,coverage_targets=targets)
    for name,value in derived.items():
        if name in payload and payload[name]!=value:raise ContractError('Program-derived semantic field changed: '+name)
        payload[name]=value
    return payload


def error(exc):
    if isinstance(getattr(exc,'repair_details',None),dict):return exc
    result=ContractError(str(exc))
    result.repair_details=dict(code='REVIEW_SEMANTIC_MAPPING_INVALID',
        guidance=['binding只引当前claim原绑定quote；context只引该claim的邻近语境，不能替代事实证据。',
            'covered必须引用coverage_targets的记忆值；不引用正文或source冒充已存事实。',
            '逐单元核查重要约束；missing/uncertain与整体coverage_status一致，不自动批准或删真实问题。'])
    return result


def validate(result,context):
    """Check provenance, mappings and state agreement, not entailment or completeness."""
    try:
        packets={r['claim_ref']:r for r in context['semantic_packets']}
        items={r['claim_ref']:r for r in context['review_items']}
        pool={r['ref']:r['text'] for r in context['semantic_contexts']}
        for row in result['support_checks']:
            value=row['evidence'];fields(value,('bindings','context'))
            if not isinstance(value['bindings'],list) or len(value['bindings'])>8:raise ContractError('Invalid binding citations')
            if row['status'] in ('supported','partial') and not value['bindings']:raise ContractError('Supported/partial needs bound evidence citation')
            source=bindings(items[row['claim_ref']]);seen=set()
            for cite in value['bindings']:
                fields(cite,('index','quote'));i=cite['index']
                if type(i) is not int or not 0<=i<len(source) or i in seen:raise ContractError('Unknown/duplicate bound evidence index')
                seen.add(i)
                if text(cite['quote'],'Bound quote') not in source[i]['quote']:raise ContractError('Context/unbound text cannot substitute bound evidence')
            allowed={ref for b in packets[row['claim_ref']]['bindings'] for ref in b['context_refs']}
            if not isinstance(value['context'],list) or len(value['context'])>8:raise ContractError('Invalid context citations')
            for cite in value['context']:
                fields(cite,('ref','quote','purpose'))
                if not isinstance(cite['ref'],str) or cite['ref'] not in allowed:raise ContractError('Context outside claim source neighborhood')
                if cite['purpose'] not in ('speaker','coreference'):raise ContractError('Context may only disambiguate speaker/coreference')
                if text(cite['quote'],'Context quote') not in pool[cite['ref']]:raise ContractError('Context quote absent')
        if context.get('review_policy_version')==4:
            from .locator_review import validate_coverage
            return validate_coverage(result,context)
        units={r['unit_ref']:r for r in context['coverage_units']};seen=set();statuses=[];missing=[]
        checks=result.get('coverage_checks')
        if not isinstance(checks,list):raise ContractError('coverage_checks must cover all units')
        for unit in checks:
            fields(unit,('unit_ref','reason','facts'));ref=unit['unit_ref']
            if not isinstance(ref,str) or ref not in units or ref in seen:raise ContractError('Unknown/duplicate coverage unit')
            seen.add(ref);text(unit['reason'],'Unit coverage reason');scope=units[ref]
            body=context['current_draft'][scope['start']:scope['end']]
            if not isinstance(unit['facts'],list) or len(unit['facts'])>8:raise ContractError('Unit facts must be bounded list')
            for fact in unit['facts']:
                fields(fact,('draft_quote','status','memory_refs','reason'))
                quote=text(fact['draft_quote'],'Coverage draft quote');text(fact['reason'],'Mapping reason')
                if quote not in body:raise ContractError('Coverage evidence outside unit')
                status=fact['status']
                if status not in ('covered','missing','uncertain','not_needed'):raise ContractError('Invalid coverage fact status')
                refs=fact['memory_refs']
                if not isinstance(refs,list) or len(refs)>8:raise ContractError('Invalid memory mappings')
                if status=='covered' and not refs:raise ContractError('Covered needs actual memory value reference')
                if status!='covered' and refs:raise ContractError('Uncovered/not-needed fact cannot claim memory mapping')
                mapped=set()
                for cite in refs:
                    fields(cite,('ref','quote'));key=cite['ref']
                    if not isinstance(key,str) or key not in context['coverage_targets'] or key in mapped:raise ContractError('Invalid/duplicate memory target')
                    mapped.add(key)
                    if text(cite['quote'],'Memory value quote') not in context['coverage_targets'][key]:raise ContractError('Body/source is not a memory value')
                statuses.append(status)
                if status=='missing':missing.append(quote)
        if seen!=set(units):raise ContractError('Missing coverage units')
        expected='missing' if 'missing' in statuses else 'uncertain' if 'uncertain' in statuses else 'sufficient'
        if result['memory_check']['coverage_status']!=expected:raise ContractError('Coverage ledger and global coverage disagree')
        issues=[r for r in result['issues'] if r['kind']=='memory_omission']
        for quote in missing:
            if not any(r['draft_quote'] in quote or quote in r['draft_quote'] for r in issues):
                raise ContractError('Missing fact needs an evidence-linked omission issue')
        if issues and not missing:raise ContractError('Omission issue needs a corresponding missing coverage observation')
    except (ContractError,KeyError,TypeError) as exc:
        raise error(exc) from None
    return result
