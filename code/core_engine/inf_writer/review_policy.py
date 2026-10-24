"""Opt-in review evidence/omission protocol, never an automatic approval oracle."""
import copy
import re
from .domain import ContractError,fields,text

OMISSION_FIELDS=['scope','target_subject','missing_fact','consequence','coverage_refs','why_uncovered']
REVIEW_POLICY_PROMPT=(
    '审核政策v1：不自动批准，也不因格式修复而删除真实问题。'
    'unsupported_memory优先引用hard_references中的memory_N_claim_M或memory_N_removal_M原文，'
    '这些参考的本地指针指向review_items对应项的claim文本，读取原文而非引用指针本身。'
    'basis_quote从该参考逐字复制，不加句号、不引用程序指针；draft_quote仍逐字来自当前正文。'
    '不同kind仍使用原有允许的参考类型，不把正文引文冒充记忆参考。'
    '判断遗漏前检查active_facts、完整最终review_items及memory_coverage_index。'
    '同一故事事实已在其他主体或共享记录中保留，不因没有逐人物重复存储就自动认定遗漏。'
    '若确有某人物独立知识边界或后续决策需要，必须说明为何该人物的记录不足，以及具体后果。'
    'memory_omission硬问题额外含omission对象：scope为story_fact或character_knowledge，'
    'target_subject在story_fact时为null，character_knowledge时为人物名；'
    'missing_fact写缺少的具体事实，consequence写影响后续的约束，'
    'coverage_refs列已核查的claim_ref或fact_N（全新事实可为空数组），why_uncovered说明现有记录为何未覆盖。'
    '这些字段只是审查理由，写齐不等于语义正确；不能编造后果或仅换个说法重复缺失指控。'
    'memory_check为missing时必须有上述可核验遗漏issue；不能靠改uncertain回避说明。'
    '非重要细节、记忆写法偏好或可选重复建议放suggestions，不当硬问题；'
    '猜测与客观事实、未实施计划与已完成事件仍须区分，真正缺少重要新事实仍需拒绝。'
    '当前请求只规划/审核一章，总字数目标不是单章长度要求。'
    '若repair.details存在，核对所给精确参考候选与原文，保留原有语义判断，程序未改你的引用或决策。')

def prepare_policy_context(context):
    if type(context.get('review_contract_version')) is not int or context['review_contract_version']!=1:
        raise ContractError('Review policy requires logical contract v1')
    version=context.get('review_policy_version',1)
    if type(version) is not int or version not in (1,2,3,4,5):
        raise ContractError('Unknown review policy version')
    payload=copy.deepcopy(context);refs=payload['hard_references'];coverage=[]
    for row in payload['review_items']:
        key=row['claim_ref'].replace('/','_')
        if key in refs and refs[key]!=row['claim']:raise ContractError('Policy reference collision: '+key)
        refs[key]=row['claim']
        change=payload['memory_changes'][int(row['claim_ref'].split('/')[0].split('_')[1])-1]
        coverage.append(dict(claim_ref=row['claim_ref'],subject=change['subject'],attribute=change['attribute'],change_kind=row['change_kind']))
    policy=dict(version=version,omission_fields=OMISSION_FIELDS.copy(),scopes=['story_fact','character_knowledge'],
        rule='Explicit reasons and evidence only; never automatic semantic acceptance or duplicate-per-character requirement')
    if version==5:policy['omission_fields']=['scope','target_subject','consequence']
    index=dict(existing_fact_refs=[name for name in refs if re.fullmatch(r'fact_\d+',name)],candidate_claims=coverage)
    for name,value in [('review_policy',policy),('memory_coverage_index',index)]:
        if name in payload and payload[name]!=value:raise ContractError('Provided '+name+' differs from derived policy')
        payload[name]=value
    payload['review_policy_version']=version
    if version in (3,4,5):
        from .semantic_review import prepare
        payload=prepare(payload)
    if version==5:
        from .judgment_review import source_table
        source_table(payload)
    return payload

def omission_error(message):
    exc=ContractError(message)
    exc.repair_details=dict(code='REVIEW_OMISSION_JUSTIFICATION_REQUIRED',required_fields=OMISSION_FIELDS.copy(),
        guidance=['核查现有全部记忆和最终候选，说明具体缺少什么、哪些现有记录不足及未来后果。',
            '其他主体已有同一故事事实不自动等于该人物必须重复存储；人物知识缺口须明确目标和必要性。',
            '不自动批准，不删真实遗漏，不仅为了通过检查填编造理由。'])
    return exc

def validate_omission(issue,context):
    try:
        value=issue.get('omission');fields(value,OMISSION_FIELDS)
        if value['scope'] not in ('story_fact','character_knowledge'):raise ContractError('Unknown omission scope')
        if value['scope']=='character_knowledge':text(value['target_subject'],'Omission target_subject')
        elif value['target_subject'] is not None:raise ContractError('Story omission target_subject must be null')
        for name in ('missing_fact','consequence','why_uncovered'):text(value[name],'Omission '+name)
        refs=value['coverage_refs']
        if not isinstance(refs,list) or len(refs)>128 or any(not isinstance(ref,str) for ref in refs):
            raise ContractError('Omission coverage_refs must be a bounded list of reference strings')
        allowed={row['claim_ref'] for row in context['review_items']}
        allowed.update(name for name in context['hard_references'] if re.fullmatch(r'fact_\d+',name))
        if len(set(refs))!=len(refs) or any(ref not in allowed for ref in refs):
            raise ContractError('Unknown or duplicate omission coverage reference')
    except ContractError as exc:raise omission_error(str(exc)) from None

def issue_error(exc,issue,index,context):
    if isinstance(getattr(exc,'repair_details',None),dict):return exc
    error=ContractError(str(exc));issue=issue if isinstance(issue,dict) else {}
    kind=issue.get('kind');selected=issue.get('basis_ref');quote=issue.get('basis_quote')
    prefixes={'fact_conflict':('fact_','past_','draft_'),'world_rule':('constraint_',),
        'causality':('fact_','past_','draft_'),'unsupported_memory':('memory_',),'memory_omission':('draft_','fact_')}.get(kind if isinstance(kind,str) else None,())
    refs=context['hard_references'];match=re.fullmatch(r'memory_(\d+)(?:_.*)?',selected) if isinstance(selected,str) else None
    prefix='memory_'+match[1]+'_' if match else None;options=[]
    if kind=='unsupported_memory':
        for name,value in refs.items():
            if (re.fullmatch(r'memory_\d+_(claim|removal)_\d+',name) and (prefix is None or name.startswith(prefix))
                    and isinstance(value,str) and len(value)<=768):
                options.append(dict(basis_ref=name,quote=value))
                if len(options)==8:break
    error.repair_details=dict(code='REVIEW_CITATION_INVALID',issue_index=index,index_base=0,
        selected_basis_ref=selected,provided_basis_quote=quote,
        matching_eligible_refs=[name for name,value in refs.items() if name.startswith(prefixes)
            and isinstance(quote,str) and quote and quote in value][:16],reference_quote_options=options,
        guidance=['basis_quote必须是所选hard_references值的逐字子串，不能自行增减标点或更换来源。',
            '候选只提供可核对原文；重新选择能支持原问题的引用，不自动批准、不删除真实问题。',
            'draft_quote和basis_quote属于不同通道；有正文原句不代表它也在所选memory参考中。'])
    return error

def validate_missing_status(result):
    if result['memory_check']['status']=='missing' and not any(issue.get('kind')=='memory_omission' for issue in result['issues']):
        raise omission_error('Missing memory assessment requires an explicit evidence-backed memory_omission issue')
