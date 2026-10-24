"""v4: exact segment citations, with program-derived unit membership."""
from .domain import ContractError,fields,text,evidence_segments
from .semantic_review import PROMPT as BASE_PROMPT

PROMPT=BASE_PROMPT.split('顶层另有coverage_checks数组')[0]+(
    '当前显式启用v4，coverage_checks不是旧数组，而是对象{reviewed_units:[{unit_ref:unit_1,reason:核查说明},...],facts:[...]}。'
    '必须独立通读全部正文单元，reviewed_units逐一列出所有coverage_units.unit_ref且不重复，reason说明该单元核查内容；无重要新约束也要解释。'
    'facts平铺列出影响后续的重要事实，不按unit分组、不输出unit_ref。每事实含evidence_ids/draft_quote/status/memory_refs/reason。'
    'evidence_ids是evidence_segments中当前章真实ID列表，如[e0001]；跨片段引用最多4个按原顺序连续ID，且只列引文确实跨越的片段。'
    'draft_quote逐字复制所列片段覆盖的正文，程序核对位置并计算所属unit，不凭情节猜unit编号。'
    'status为covered/missing/uncertain/not_needed；covered的memory_refs至少一项{ref:coverage_targets键,quote:目标记忆值逐字子串}并说明语义对应；其余memory_refs为空。'
    '全部无重要新约束时facts才可为空，不靠空数组/not_needed跳过重要事件。正文写过不等于已记住；需独立检查拒绝、承诺、取得或失去、限制、新线索。'
    'coverage_targets只含最终候选与未被替换现有值，正文和source不算记忆值。'
    '有missing时coverage_status=missing并给完整memory_omission问题与理由；无missing有uncertain则uncertain，其余sufficient。'
    '不自动批准或删除真实问题，合法引用不代表语义支持。顶层只输出approved/issues/suggestions/memory_check/support_checks/coverage_checks，无备注字段。'
    '格式修复时previous_output可能采用review-json-refs-v1无损表示：value里$inf_repair_ref按本请求输入根对象的path读取字符串，取start含到end不含的字符子串，递归还原原JSON值。'
    '这不是删减过的答复；不要把指针当引文，保留原判定和正确内容，只修复已指出的契约/证据问题。')

def _location(fact,context,index):
    ids=fact.get('evidence_ids');segments=evidence_segments(context['current_draft'])
    positions={s['id']:i for i,s in enumerate(segments)}
    if (not isinstance(ids,list) or not 1<=len(ids)<=4 or
            any(not isinstance(k,str) or k not in positions for k in ids)):
        raise ContractError('Unknown or invalid coverage evidence_ids')
    order=[positions[k] for k in ids]
    if order!=list(range(order[0],order[0]+len(order))):
        raise ContractError('Coverage evidence_ids must be unique, ordered and contiguous')
    selected=[segments[i] for i in order];quote=text(fact.get('draft_quote'),'Coverage draft quote')
    start,end=selected[0]['start'],selected[-1]['end'];body=context['current_draft']
    # All declared segments must intersect this exact occurrence; no extra broad spans.
    position=body.find(quote,start,end)
    if position<0 or position>=selected[0]['end'] or position+len(quote)<=selected[-1]['start']:
        error=ContractError('Coverage quote absent from declared segment span')
        error.repair_details=dict(code='REVIEW_COVERAGE_LOCATION_INVALID',fact_index=index,index_base=0,
            provided_evidence_ids=ids,provided_draft_quote=quote,
            matching_segment_ids=[s['id'] for s in segments if quote in s['text']][:8],
            guidance='核对evidence_segments原文及ID；只改错误定位，不搬运无关引用、不改判定或删真实问题。')
        raise error
    units=[u['unit_ref'] for u in context['coverage_units'] if any(k in u['segment_ids'] for k in ids)]
    return dict(fact_index=index,evidence_ids=ids.copy(),unit_refs=units)

def coverage_locations(result,context):
    return [_location(fact,context,i) for i,fact in enumerate(result['coverage_checks']['facts'])]

def validate_coverage(result,context):
    value=result.get('coverage_checks');fields(value,('reviewed_units','facts'))
    expected=[u['unit_ref'] for u in context['coverage_units']];reviewed=value['reviewed_units']
    if not isinstance(reviewed,list):raise ContractError('reviewed_units must be list')
    refs=[]
    for row in reviewed:
        fields(row,('unit_ref','reason'));text(row['reason'],'Unit scan reason')
        refs.append(text(row['unit_ref'],'Reviewed unit ref'))
    if len(refs)!=len(expected) or set(refs)!=set(expected):
        raise ContractError('All coverage units must be explicitly reviewed exactly once')
    facts=value['facts']
    if not isinstance(facts,list) or len(facts)>8*len(expected):raise ContractError('Coverage facts must be bounded list')
    statuses=[];missing=[];per_unit={ref:0 for ref in expected}
    for i,fact in enumerate(facts):
        fields(fact,('evidence_ids','draft_quote','status','memory_refs','reason'))
        location=_location(fact,context,i)
        for ref in location['unit_refs']:
            per_unit[ref]+=1
            if per_unit[ref]>8:raise ContractError('Too many facts in coverage unit')
        text(fact['reason'],'Mapping reason');status=fact['status']
        if status not in ('covered','missing','uncertain','not_needed'):raise ContractError('Invalid coverage fact status')
        refs=fact['memory_refs']
        if not isinstance(refs,list) or len(refs)>8:raise ContractError('Invalid memory mappings')
        if status=='covered' and not refs:raise ContractError('Covered needs actual memory value reference')
        if status!='covered' and refs:raise ContractError('Uncovered/not-needed fact cannot claim memory mapping')
        seen=set()
        for cite in refs:
            fields(cite,('ref','quote'));key=cite['ref']
            if not isinstance(key,str) or key not in context['coverage_targets'] or key in seen:
                raise ContractError('Invalid/duplicate memory target')
            seen.add(key)
            if text(cite['quote'],'Memory value quote') not in context['coverage_targets'][key]:
                raise ContractError('Body/source is not a memory value')
        statuses.append(status)
        if status=='missing':missing.append(fact['draft_quote'])
    expected_status='missing' if 'missing' in statuses else 'uncertain' if 'uncertain' in statuses else 'sufficient'
    if result['memory_check']['coverage_status']!=expected_status:raise ContractError('Coverage ledger and global coverage disagree')
    issues=[r for r in result['issues'] if r['kind']=='memory_omission']
    for quote in missing:
        if not any(r['draft_quote'] in quote or quote in r['draft_quote'] for r in issues):
            raise ContractError('Missing fact needs an evidence-linked omission issue')
    if issues and not missing:raise ContractError('Omission issue needs a corresponding missing coverage observation')
    return result
