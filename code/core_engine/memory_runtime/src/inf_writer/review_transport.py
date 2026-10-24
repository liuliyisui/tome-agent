"""Lossless, explicit reviewer wire aliases. No summarizing, pruning or semantic edits."""
import copy
import re
from .domain import ContractError,canonical,digest

MARKER='$inf_review_ref'
RULES=[
    '这是审核输入的无损引用表示，不是省略内容。hard_references的键名与basis_ref规则不变。',
    '遇到$inf_review_ref，按本输入根对象的/字段/0基索引定位；render=text读取目标字符串，canonical_json读取目标对象的JSON文本，value读取目标对象。',
    'fact和memory参考正文在active_facts与memory_changes中；draft参考在evidence_segments.text，past参考在recent_chapters.text。独有参考仍以完整文本给出。',
    'review_items.transition指向review_transitions共享表；这只复用相同的变化说明，claim_ref、claim、source和删除项仍须逐一检查。',
    '输出仍是原approved/issues/suggestions/memory_check/support_checks合同，basis_quote必须是解析后参考文本中的逐字引文，不能引用指针字符串。',
    '不要将未修改字段当删除，目录未列出的新事实仍需结合完整正文检查；不能把去重当证据已充分。']


def _alias(path,render):return {MARKER:path,'render':render}


def _rules(context):
    rules=RULES.copy()
    if context.get('review_policy_version') in (3,4,5):
        rules[4]=rules[4].replace('support_checks合同','support_checks/coverage_checks合同')
    if context.get('review_policy_version') in (4,5):
        rules.append('v4的semantic_contexts.text和coverage_targets也可用同一$inf_review_ref引用已有原文/claim；先解析这些无损引用，再按repair的字符范围还原先前答复。')
    return rules


def compact_review_context(context):
    if type(context.get('review_contract_version')) is not int or context['review_contract_version']!=1:
        raise ContractError('Review transport requires explicit logical contract v1')
    if any(key in context for key in ('review_transport','review_transitions')):
        raise ContractError('Reserved review transport fields cannot be overwritten')
    wire=copy.deepcopy(context)
    targets={}
    for field,prefix,render in (('active_facts','fact','canonical_json'),('memory_changes','memory','canonical_json'),('constraints','constraint','text')):
        for i,item in enumerate(context.get(field,[])):
            rendered=canonical(item) if render=='canonical_json' else item
            targets[f'{prefix}_{i+1}']=(rendered,_alias(f'/{field}/{i}',render))
    for i,item in enumerate(context.get('evidence_segments',[])):
        targets['draft_'+item['id']]=(item['text'],_alias(f'/evidence_segments/{i}/text','text'))
    for i,item in enumerate(context.get('recent_chapters',[])):
        targets[f'past_{item["number"]}']=(item['text'],_alias(f'/recent_chapters/{i}/text','text'))
    for i,item in enumerate(context.get('review_items',[])):
        targets[item['claim_ref'].replace('/','_')]=(item['claim'],_alias(f'/review_items/{i}/claim','text'))
    for name,value in wire['hard_references'].items():
        if not isinstance(value,str):raise ContractError('Logical hard references must be complete text')
        if name in targets and value==targets[name][0]:wire['hard_references'][name]=targets[name][1]
    transitions=[];indices={}
    for item in wire['review_items']:
        key=canonical(item['transition'])
        if key not in indices:
            indices[key]=len(transitions);transitions.append(copy.deepcopy(item['transition']))
        item['transition']=_alias(f'/review_transitions/{indices[key]}','value')
    wire['review_transitions']=transitions
    if context.get('review_policy_version') in (4,5):
        originals={row['text']:i for i,row in enumerate(context.get('evidence_segments',[]))}
        for row in wire.get('semantic_contexts',[]):
            if row['chapter_number']==context['chapter_number'] and row['text'] in originals:
                alias=_alias(f'/evidence_segments/{originals[row["text"]]}/text','text')
                if len(canonical(alias).encode('utf-8'))<len(canonical(row['text']).encode('utf-8')):row['text']=alias
        claims={row['claim_ref']:i for i,row in enumerate(context.get('review_items',[]))}
        for ref,value in wire.get('coverage_targets',{}).items():
            if ref in claims and value==context['review_items'][claims[ref]]['claim']:
                wire['coverage_targets'][ref]=_alias(f'/review_items/{claims[ref]}/claim','text')
    wire['review_transport']=dict(version=1,logical_sha256=digest(canonical(context)),rules=_rules(context))
    # Reversibility is enforced before a request can reach a provider.
    if expand_review_context(wire)!=context:raise ContractError('Review transport roundtrip changed input')
    return wire


def _resolve(wire,alias,*,transition=False):
    if not isinstance(alias,dict) or set(alias)!={MARKER,'render'}:
        raise ContractError('Invalid review alias shape')
    path=alias[MARKER];render=alias['render']
    if not isinstance(path,str):raise ContractError('Alias path must be local text')
    match=re.fullmatch(r'/(active_facts|memory_changes|constraints|evidence_segments|recent_chapters|review_transitions|review_items)/(0|[1-9][0-9]*)(/(?:text|claim))?',path)
    if not match:raise ContractError('Unknown/external/cyclic review alias path')
    field,index,suffix=match.groups()
    allowed=(field=='review_transitions' and suffix is None and render=='value') if transition else (
        (field in ('active_facts','memory_changes') and suffix is None and render=='canonical_json') or
        (field=='constraints' and suffix is None and render=='text') or
        (field=='review_items' and suffix=='/claim' and render=='text') or
        (field in ('evidence_segments','recent_chapters') and suffix=='/text' and render=='text'))
    if not allowed:raise ContractError('Review alias target/render not allowed here')
    try:
        values=wire[field]
        if not isinstance(values,list):raise ContractError('Alias target must be list')
        value=values[int(index)]
        if suffix:value=value[suffix[1:]]
    except (KeyError,IndexError,TypeError,ValueError):raise ContractError('Missing review alias target') from None
    if render=='canonical_json':return canonical(value)
    if render=='text' and not isinstance(value,str):raise ContractError('Text alias must resolve to text')
    return copy.deepcopy(value)


def expand_review_context(wire):
    metadata=wire.get('review_transport')
    if not isinstance(metadata,dict) or set(metadata)!={'version','logical_sha256','rules'} or type(metadata['version']) is not int or metadata['version']!=1:
        raise ContractError('Unknown review transport contract')
    if metadata['rules']!=_rules(wire):raise ContractError('Review transport interpretation rules changed')
    if not isinstance(wire.get('review_transitions'),list):raise ContractError('Missing transition table')
    restored=copy.deepcopy(wire)
    for name,value in wire['hard_references'].items():
        if isinstance(value,dict):restored['hard_references'][name]=_resolve(wire,value)
        elif not isinstance(value,str):raise ContractError('Invalid reference text')
    for index,item in enumerate(wire['review_items']):
        restored['review_items'][index]['transition']=_resolve(wire,item['transition'],transition=True)
    if wire.get('review_policy_version') in (4,5):
        for index,row in enumerate(wire.get('semantic_contexts',[])):
            if isinstance(row['text'],dict):restored['semantic_contexts'][index]['text']=_resolve(wire,row['text'])
        for ref,value in wire.get('coverage_targets',{}).items():
            if isinstance(value,dict):restored['coverage_targets'][ref]=_resolve(wire,value)
    del restored['review_transport'];del restored['review_transitions']
    if digest(canonical(restored))!=metadata['logical_sha256']:
        raise ContractError('Expanded review input hash differs from original')
    return restored
