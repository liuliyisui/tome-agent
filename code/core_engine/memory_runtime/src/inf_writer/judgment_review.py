"""v5 separates semantic judgments from deterministic source resolution.

Resolution attests identity/provenance, NOT entailment or completeness.
"""
import copy
from .domain import ContractError,canonical,digest,evidence_segments,fields,text
from .semantic_review import bindings

OUTPUT_CONTRACT=dict(
    top_level=['approved','issues','suggestions','memory_check','support_checks','coverage_checks'],
    memory_check_fields=['coverage_status','reason'],support_check_fields=['claim_ref','status','reason'],
    check_status_values=['supported','partial','unsupported','uncertain'],
    semantic_fields=dict(coverage_check=['reviewed_units','facts'],reviewed_unit=['unit_ref','reason'],
        coverage_fact=['fact','source_refs','status','memory_refs','reason'],
        missing_fact_extra=['omission'],omission=['scope','target_subject','consequence'],
        issue=['kind','description','source_refs','basis_ref']),
    rule='Return judgments only. Program retrieves original claim, evidence, source locations and memory values; never infer semantic truth from resolved IDs.')

PROMPT=(
    '你是审核Agent，显式审核政策v5。通读正文、世界约束、候选记忆及已有记忆。只输出一个JSON对象，严格按review_output_contract。'
    '输出approved/issues/suggestions/memory_check/support_checks/coverage_checks。不要重抄claim、原文quote、语境引文、字符位置或连续片段列表。'
    'support_checks按review_items的claim_ref恰好一次，只含claim_ref/status/reason。status为supported/partial/unsupported/uncertain。'
    '判断完整claim是否由它的原绑定source支持；绑定全部由程序原样保留，不需要你再选择或复制。'
    'semantic_contexts仅帮助理解谁说话及指代，不能把缺失的数量、物件、位置、结果从别处补进绑定。'
    '推测不当确认、计划不当完成；但不能因计划尚未实施就否认这是计划。跨章继承按原章节证据核查，不因本章未重复就否认旧知识。'
    'partial/unsupported的理由将由程序连同原绑定编成unsupported_memory问题，不再在issues重复输出；uncertain同样不能批准。'
    'coverage_checks={reviewed_units:[{unit_ref,reason}],facts:[...]}。独立核查全部coverage_units，每单元说明检查情况，不重复/漏项。'
    'facts列影响后续的重要事实，含fact（简短事实描述，非逐字引文）/source_refs/status/memory_refs/reason。'
    'source_refs选择现有draft_eNNNN参考，程序逐条取回完整原文与位置。可以选择多个不同段落，不假称连续引文；无须复制文字。'
    'status为covered/missing/uncertain/not_needed。covered的memory_refs至少一个coverage_targets键，表示真实记忆覆盖；其他状态的memory_refs表示已核查但未确认覆盖的相关候选，可为空。'
    '不要把正文出现当记忆已有；检查拒绝、承诺、重要限制、物品变动和新线索。facts只在确无重要新约束时可空，并在各单元reason解释。'
    'missing事实另含omission={scope:story_fact或character_knowledge,target_subject:人物名或null,consequence:对后续的具体约束}。'
    'story_fact的target_subject为null；人物独立知识缺口须明确人物，其他主体已有同一事实不自动意味着必须重复存储。'
    '程序从fact/reason/memory_refs生成missing_fact/why_uncovered/coverage_refs，不需你重复填写。'
    'issues只列其他正文硬问题{kind:fact_conflict或world_rule或causality,description,source_refs,basis_ref}。'
    'source_refs必须是当前章draft参考；basis_ref按kind选择已有fact_/past_/draft_或constraint_，程序取回原文，不填写basis_quote/draft_quote。'
    'memory_check只含coverage_status/reason，有missing事实时为missing，无missing但有uncertain时为uncertain，其余sufficient。'
    'approved=true仅当逐项全supported、覆盖sufficient、无其他硬问题；否则false。程序检查一致性，不替你改判。'
    '编号合法不代表语义正确，必须判断来源实际是否支持事实和映射，不虚构问题或后果。suggestions放非硬性建议。'
    '一次格式修复可能附previous_output的可逆JSON引用表示；按review_transport规则及start包含/end不含还原，不丢原判断或正确内容。')

def fail(path,message,options=()):
    exc=ContractError(path+': '+message)
    exc.repair_details=dict(code='REVIEW_JUDGMENT_INVALID',path=path,
        eligible_refs=list(options)[:16],guidance='核对该字段及原输入；不删除真实问题、不自动批准、不编造来源。')
    raise exc

def refs(value,allowed,path,required=False):
    if not isinstance(value,list) or len(value)>8 or any(not isinstance(v,str) for v in value):
        fail(path,'expected at most 8 reference strings',allowed)
    if len(set(value))!=len(value) or any(v not in allowed for v in value) or (required and not value):
        fail(path,'unknown, duplicate or missing required reference',allowed)
    return value

def source_table(context):
    segments=evidence_segments(context['current_draft'])
    if context.get('evidence_segments',segments)!=segments:fail('evidence_segments','differs from original body')
    return {'draft_'+s['id']:dict(ref='draft_'+s['id'],chapter_number=context['chapter_number'],
        chapter_sha256=digest(context['current_draft']),**s) for s in segments}

def compile_judgments(value,context):
    """Materialize only fields recoverable from original input and model decisions."""
    if context.get('review_policy_version')!=5:fail('review_policy_version','explicit v5 required')
    fields(value,('approved','issues','suggestions','memory_check','support_checks','coverage_checks'))
    if type(value['approved']) is not bool:fail('approved','must be bool')
    fields(value['memory_check'],('coverage_status','reason'));text(value['memory_check']['reason'],'Coverage reason')
    if not isinstance(value['suggestions'],list):fail('suggestions','must be list')
    for suggestion in value['suggestions']:text(suggestion,'Suggestion')
    items={r['claim_ref']:r for r in context['review_items']};seen=set();support=[];issues=[]
    if not isinstance(value['support_checks'],list):fail('support_checks','must be list')
    for i,row in enumerate(value['support_checks']):
        fields(row,('claim_ref','status','reason'));ref=row['claim_ref'];path=f'support_checks[{i}]'
        if not isinstance(ref,str) or ref not in items or ref in seen:fail(path+'.claim_ref','unknown or duplicate',items)
        seen.add(ref);status=row['status'];reason=text(row['reason'],'Support reason')
        if status not in ('supported','partial','unsupported','uncertain'):fail(path+'.status','unknown judgment')
        item=items[ref];original=bindings(item)
        support.append(dict(claim_ref=ref,claim=item['claim'],status=status,reason=reason,
            evidence=dict(bindings=[dict(index=j,quote=b['quote']) for j,b in enumerate(original)],context=[])))
        if status in ('partial','unsupported'):
            source=item['source']
            issues.append(dict(kind='unsupported_memory',description=reason,claim_ref=ref,
                basis_ref=ref.replace('/','_'),basis_quote=item['claim'],
                source_records=[dict(chapter_number=source['chapter_number'],chapter_sha256=source['chapter_sha256'],**copy.deepcopy(b)) for b in original]))
    if seen!=set(items):fail('support_checks','missing judgments',set(items)-seen)
    body_sources=source_table(context);targets=context['coverage_targets'];ledger=value['coverage_checks']
    fields(ledger,('reviewed_units','facts'));units={u['unit_ref']:u for u in context['coverage_units']};scanned=set()
    if not isinstance(ledger['reviewed_units'],list):fail('coverage_checks.reviewed_units','must be list')
    for row in ledger['reviewed_units']:
        fields(row,('unit_ref','reason'));ref=row['unit_ref'];text(row['reason'],'Unit scan reason')
        if not isinstance(ref,str) or ref not in units or ref in scanned:fail('coverage_checks.reviewed_units','unknown or duplicate unit',units)
        scanned.add(ref)
    if scanned!=set(units):fail('coverage_checks.reviewed_units','missing units',set(units)-scanned)
    if not isinstance(ledger['facts'],list) or len(ledger['facts'])>8*len(units):fail('coverage_checks.facts','unbounded facts')
    facts=[];statuses=[];per_unit={u:0 for u in units}
    for i,row in enumerate(ledger['facts']):
        path=f'coverage_checks.facts[{i}]';fields(row,('fact','source_refs','status','memory_refs','reason'),('omission',))
        text(row['fact'],'Observed fact');text(row['reason'],'Mapping reason');status=row['status']
        if status not in ('covered','missing','uncertain','not_needed'):fail(path+'.status','unknown coverage judgment')
        source_refs=refs(row['source_refs'],body_sources,path+'.source_refs',True)
        memory_refs=refs(row['memory_refs'],targets,path+'.memory_refs',status=='covered')
        resolved=copy.deepcopy(row);resolved['source_records']=[copy.deepcopy(body_sources[r]) for r in source_refs]
        resolved['memory_records']=[dict(ref=r,text=targets[r]) for r in memory_refs]
        resolved['unit_refs']=[u for u,scope in units.items() if any(body_sources[r]['id'] in scope['segment_ids'] for r in source_refs)]
        for u in resolved['unit_refs']:
            per_unit[u]+=1
            if per_unit[u]>8:fail(path,'too many observations in unit')
        facts.append(resolved);statuses.append(status)
        if status=='missing':
            omission=row.get('omission');fields(omission,('scope','target_subject','consequence'))
            if omission['scope'] not in ('story_fact','character_knowledge'):fail(path+'.omission.scope','unknown scope')
            if omission['scope']=='story_fact' and omission['target_subject'] is not None:fail(path+'.omission.target_subject','story scope requires null')
            if omission['scope']=='character_knowledge':text(omission['target_subject'],'Knowledge target')
            text(omission['consequence'],'Omission consequence')
            issues.append(dict(kind='memory_omission',description=row['reason'],source_records=copy.deepcopy(resolved['source_records']),
                omission=dict(**copy.deepcopy(omission),missing_fact=row['fact'],coverage_refs=memory_refs.copy(),why_uncovered=row['reason'])))
        elif 'omission' in row:fail(path+'.omission','only missing facts carry omission')
    if not isinstance(value['issues'],list) or len(value['issues'])>128:fail('issues','must be bounded list')
    for i,row in enumerate(value['issues']):
        fields(row,('kind','description','source_refs','basis_ref'));path=f'issues[{i}]'
        kind=row['kind'];prefixes={'fact_conflict':('fact_','past_','draft_'),'world_rule':('constraint_',),'causality':('fact_','past_','draft_')}
        if not isinstance(kind,str) or kind not in prefixes:fail(path+'.kind','memory problems belong to judgments')
        text(row['description'],'Issue description');basis=row['basis_ref'];hard=context['hard_references']
        if not isinstance(basis,str) or basis not in hard or not basis.startswith(prefixes[kind]):fail(path+'.basis_ref','unknown/ineligible basis',hard)
        chosen=refs(row['source_refs'],body_sources,path+'.source_refs',True)
        issues.append(dict(kind=kind,description=row['description'],source_records=[copy.deepcopy(body_sources[r]) for r in chosen],
            basis_ref=basis,basis_quote=hard[basis]))
    expected='missing' if 'missing' in statuses else 'uncertain' if 'uncertain' in statuses else 'sufficient'
    if value['memory_check']['coverage_status']!=expected:fail('memory_check.coverage_status','inconsistent with observations')
    can_approve=all(r['status']=='supported' for r in support) and expected=='sufficient' and not issues
    if value['approved']!=can_approve:fail('approved','inconsistent with support/coverage/issues; program will not change it')
    return dict(approved=value['approved'],issues=issues,suggestions=copy.deepcopy(value['suggestions']),
        memory_check=copy.deepcopy(value['memory_check']),support_checks=support,
        coverage_checks=dict(reviewed_units=copy.deepcopy(ledger['reviewed_units']),facts=facts),review_judgments=copy.deepcopy(value))

def validate_resolved(result,context):
    """Do not accept forged or altered derived evidence on a later boundary."""
    if not isinstance(result,dict) or 'review_judgments' not in result:fail('review_judgments','missing original judgments')
    expected=compile_judgments(result['review_judgments'],context)
    if canonical(expected)!=canonical(result):fail('resolved_review','differs from program reconstruction')
    return result
