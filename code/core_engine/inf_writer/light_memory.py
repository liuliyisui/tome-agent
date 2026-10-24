"""Opt-in lightweight memory maintenance, not semantic memory certification.

The model selects chapter-local source IDs. Existing storage resolves them to
literal segments for compatibility; source presence does NOT prove entailment.
Legacy strict agents and stored sources are left unchanged.
"""
import copy
from dataclasses import dataclass
from .domain import ContractError,canonical,evidence_segments,fields,strict_json,text
from .models import ModelRequest

MEMORY_PROMPT=(
    '你是INF记忆维护智能体。根据当前正文与已有记忆，选择影响后续的重要信息。'
    '只输出JSON对象changes及可选no_change_reason。新增确认、已有状态变化、旧认识失效分别处理，未变不提交。'
    '严格按memory_submission_contract的动作专属格式提交，不能把新增与更新两类格式混用。'
    'store新增：action/subject/attribute/expected_revision=null/reason/support，禁止claim_ops。'
    'update已有记录：action/subject/attribute/expected_revision=当前revision/reason，结构化记录优先claim_ops增量；'
    '也兼容support全量替换，但必须保留所有仍有效知识；support与claim_ops不能同时输出。'
    'retire整条失效：action/subject/attribute/expected_revision=当前revision/reason/support，禁止claim_ops。'
    'attribute沿用稳定英文snake_case名。新字段store且expected_revision=null；已有字段update或retire且匹配revision。'
    'support=[{"claim":"一项信息","evidence":[{"evidence_id":"e0001"}]}]，不输出value、quote、start或end。'
    '编号只标明信息来源，程序取回原文，不要重复抄写正文；必须选择本章实际存在的编号。'
    '已有结构化字段优先update+claim_ops局部修改：add含op/claim/evidence；'
    'replace含op/index/old_claim/claim/evidence；remove含op/index/old_claim/reason/evidence。'
    'index是输入value列表的0基原索引，old_claim逐字匹配；未变项与来源由程序保留。'
    '一个主体属性每章只提交一次最终更新，不能把新增信息误当新建已有字段。'
    '最多16项信息，每项1到8个来源；retire用一项support说明失效依据，不删除全部知识逃避错误。'
    '区分客观事实、人物知道的内容、怀疑、计划及短期情绪；计划不当已发生事实。'
    '累计认识不可只留最后一项，旧认识证伪要替换或删除。撤回怀疑时还需考虑新增澄清信息。'
    '空changes必须给no_change_reason。仅一次格式修复，返回完整提案，不修改正文。'
)
REVIEW_PROMPT=(
    '你是INF正文审核智能体。本模式不审核候选记忆的证据充分性，也不清点记忆遗漏。'
    '只检查正文与已知事实、世界规则的明确冲突及明确因果矛盾；合理变化、猜测、悬念和节奏偏好不是硬错误。'
    '只输出JSON：approved布尔、issues数组、suggestions字符串数组。'
    '每个issue只含kind(fact_conflict/world_rule/causality)、description、draft_quote、basis_ref、basis_quote。'
    '引用hard_references中存在的参考，quote均为对应原文逐字摘录。规则用constraint_，其他用fact_/past_/draft_。'
    'approved当且仅当issues为空。不要输出memory_check、support_checks、coverage_checks或记忆遗漏问题。'
)

def lean_facts(facts):
    result=[]
    for fact in facts:
        row={k:copy.deepcopy(v) for k,v in fact.items() if k!='source'}
        source=fact.get('source',{})
        # Only a capability marker is needed for patch selection. Old evidence is
        # inherited from the actual state, never reconstructed from this projection.
        if any(k in source for k in ('support','claim_sources')):
            row['source']={'claim_sources':[], 'details_omitted':True}
        result.append(row)
    return result

def prepare_memory(context,reconcile_updates=False):
    payload={k:copy.deepcopy(context[k]) for k in (
        'goal','constraints','chapter_plan','current_draft','memory_extraction_checklist') if k in context}
    payload['active_facts']=lean_facts(context.get('active_facts',[]))
    payload['evidence_segments']=evidence_segments(payload['current_draft'])
    if reconcile_updates:payload['require_explicit_retention']=True
    from .memory_action_contract import prepare_memory_context
    from .memory_submission import add_contract
    return add_contract(prepare_memory_context(payload))

def prepare_review(context):
    payload={k:copy.deepcopy(context[k]) for k in (
        'goal','constraints','chapter_plan','current_draft','recent_chapters',
        'unresolved_chapters','fact_bank_status') if k in context}
    payload['active_facts']=lean_facts(context.get('active_facts',[]))
    refs={}
    for ref,value in context.get('hard_references',{}).items():
        if ref.startswith(('constraint_','past_','draft_')):refs[ref]=value
    for i,fact in enumerate(payload['active_facts'],1):
        refs[f'fact_{i}']=canonical({k:v for k,v in fact.items() if k!='source'})
    # Strict coordinator may not have built references yet.
    for i,rule in enumerate(payload.get('constraints',[]),1):refs.setdefault(f'constraint_{i}',rule)
    payload['hard_references']=refs
    payload['review_mode']='light_memory'
    return payload

def resolve_sources(result,draft):
    fields(result,('changes',),('no_change_reason',))
    value=copy.deepcopy(result)
    if not isinstance(value['changes'],list):raise ContractError('changes must be list')
    catalog={r['id']:r['text'] for r in evidence_segments(draft)}
    for candidate in value['changes']:
        if not isinstance(candidate,dict):raise ContractError('Memory candidate must be object')
        groups=candidate.get('claim_ops',candidate.get('support'))
        if not isinstance(groups,list):raise ContractError('Light memory requires support or claim_ops')
        for group in groups:
            if 'claim_ops' in candidate and isinstance(group,dict) and group.get('op')=='retain':
                fields(group,('op','index','old_claim','reason'))
                continue
            if not isinstance(group,dict) or not isinstance(group.get('evidence'),list):
                raise ContractError('Memory information requires evidence IDs')
            for item in group['evidence']:
                fields(item,('evidence_id',))
                identifier=item['evidence_id']
                if not isinstance(identifier,str) or identifier not in catalog:
                    raise ContractError('Unknown evidence_id; select a current-chapter ID')
                item['quote']=catalog[identifier]
    return value

def validate_light_review(result,context,*,resolved=False):
    fields(result,('approved','issues','suggestions'),('memory_check',) if resolved else ())
    if type(result['approved']) is not bool or not isinstance(result['issues'],list):
        raise ContractError('Invalid light review decision')
    if not isinstance(result['suggestions'],list):raise ContractError('suggestions must be list')
    for suggestion in result['suggestions']:text(suggestion,'suggestion')
    kinds={'fact_conflict':('fact_','past_','draft_'),'world_rule':('constraint_',),'causality':('fact_','past_','draft_')}
    refs=context.get('hard_references',{})
    for issue in result['issues']:
        fields(issue,('kind','description','draft_quote','basis_ref','basis_quote'))
        kind,ref=issue['kind'],issue['basis_ref']
        if not isinstance(kind,str) or kind not in kinds or not isinstance(ref,str) or not ref.startswith(kinds[kind]) or ref not in refs:
            raise ContractError('Light review needs a factual reference; memory audit is disabled')
        if text(issue['draft_quote'],'draft quote') not in context['current_draft']:
            raise ContractError('Review quote not in current draft')
        if text(issue['basis_quote'],'basis quote') not in refs[ref]:raise ContractError('Review basis absent')
        text(issue['description'],'issue description')
    if result['approved'] != (not result['issues']):raise ContractError('Light decision inconsistent with issues')
    if resolved:
        if result.get('memory_check')!=NOT_CHECKED:raise ContractError('Light memory must remain explicitly not_checked')
    return result

NOT_CHECKED=dict(status='not_checked',reason='Light mode: semantic support and memory coverage audit disabled; source IDs and update contracts only.')

@dataclass
class LightAgent:
    role:str
    gateway:object
    max_format_retries:int=1
    max_output_tokens:int=4096
    review_contract_version:int=0
    review_policy_version:int=0
    review_mode:str='light_memory'
    reconcile_updates:bool=False
    def run(self,context,trace,validator=None):
        if type(self.max_format_retries) is not int or not 0<=self.max_format_retries<=1:
            raise ContractError('Format repairs must be 0 or 1')
        payload=prepare_memory(context,reconcile_updates=self.reconcile_updates) if self.role=='memory' else prepare_review(context)
        prompt=MEMORY_PROMPT if self.role=='memory' else REVIEW_PROMPT
        if self.role=='memory' and self.reconcile_updates:
            prompt+=(
                '本模式更新claim_ops时，必须逐个处理该属性每一个旧index：仍有效用retain，'
                '变化用replace，已失效用remove；每个旧index恰好出现一次，add不算处理旧项。'
                'retain只含op/index/old_claim/reason，不带evidence，程序沿用原来源；理由说明为何仍有效。'
                '物品持有人、眼色、位置等当前状态变化时，旧现状应replace/remove，不能retain旧持有人再add新持有人。'
                '保留历史靠自动归档，不靠把过期现状继续留在当前列表；累计知识中未变化且仍有效的子项才retain。'
                '只retain而没有变化则不要提交该属性。support全量替换只列最终仍有效的信息，不能丢无关知识。'
            )
        for attempt in range(self.max_format_retries+1):
            entry=dict(role=self.role,attempt=attempt+1,memory_semantic_review='disabled',review_mode='light_memory')
            trace.append(entry)
            reply=self.gateway.complete(ModelRequest(self.role,prompt,copy.deepcopy(payload),self.max_output_tokens))
            entry.update(raw_output=reply.content,input_tokens=reply.input_tokens,output_tokens=reply.output_tokens,cost_usd=reply.cost_usd)
            try:
                result=strict_json(reply.content)
                if self.role=='memory':
                    # Reuse the legacy narrow metadata contract. Do not silently
                    # drop arbitrary keys or rewrite a candidate to make it pass.
                    from .agents import validate
                    parsed=result
                    result=validate('memory',parsed)
                    if 'type' in parsed:
                        entry['normalizations']=[dict(rule='memory_json_object_type',field='type',value=parsed['type'])]
                    from .memory_submission import check_submission
                    check_submission(result,payload)
                    result=resolve_sources(result,context['current_draft'])
                else:
                    validate_light_review(result,payload)
                    result=dict(result,memory_check=copy.deepcopy(NOT_CHECKED))
                if validator is not None:result=validator(result)
                entry['status']='ACCEPTED'
                return result
            except ContractError as exc:
                entry.update(status='FORMAT_FAILED',error=str(exc))
                details=getattr(exc,'repair_details',None)
                if isinstance(details,dict):entry['repair_details']=copy.deepcopy(details)
                if attempt==self.max_format_retries:raise
                payload['repair']=dict(error=str(exc),previous_output=reply.content,
                    instruction='只修格式或所列更新契约错误；保留正确候选，不改正文；来源只输出evidence_id，不抄quote。')
                if isinstance(details,dict):
                    from .memory_submission import compact_feedback
                    payload['repair']['details']=compact_feedback(details)
        raise ContractError('Unreachable light agent state')

def build_light_agents(gateway,reconcile_updates=False,compact_narrative=False):
    if type(reconcile_updates) is not bool:raise ContractError('reconcile_updates must be boolean')
    if type(compact_narrative) is not bool:raise ContractError('compact_narrative must be boolean')
    from .agents import build_agents
    agents=build_agents(gateway)
    for role in ('planner','writer'):agents[role].compact_narrative=compact_narrative
    agents['memory']=LightAgent('memory',gateway,reconcile_updates=reconcile_updates)
    agents['reviewer']=LightAgent('reviewer',gateway)
    return agents
