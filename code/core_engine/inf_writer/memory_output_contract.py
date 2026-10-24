"""One source of claim text and lossless, non-mutating batch diagnostics."""
import copy
from .domain import ContractError,canonical,checked_support,evidence_segments,fields

def evidence(identifier='e0001',quote='正文中的逐字引文'):
    return [dict(evidence_id=identifier,quote=quote)]

EXAMPLES={
    'store':dict(changes=[dict(action='store',subject='甲',attribute='location',expected_revision=None,
        reason='正文明确章末位置',support=[dict(claim='甲在门外',evidence=evidence(quote='甲在门外'))])]),
    'update':dict(changes=[dict(action='update',subject='甲',attribute='known_information',expected_revision=2,
        reason='新增已确认信息',claim_ops=[dict(op='add',claim='船明天到港',evidence=evidence(quote='船明天到港'))])]),
    'retire':dict(changes=[dict(action='retire',subject='甲',attribute='permit_status',expected_revision=1,
        reason='该记录已明确失效',support=[dict(claim='原许可已撤销',evidence=evidence(quote='原许可已撤销'))])]),
    'unchanged':dict(changes=[],no_change_reason='没有新增或变化的重要事实')}

MEMORY_PROMPT=(
    '你是INF记忆维护智能体。只输出一个完整JSON对象，顶层changes及可选no_change_reason，不加type、解释或代码围栏。'
    '根据正文选择真正影响后续的重要事实，区分世界事实、人物已知信息、怀疑和未实施计划。'
    '新输出不输出value，不同时生成两份同义内容；只写support里的claim，值由程序逐字生成，证据仍独立审核。'
    '按subject + attribute匹配已有记录，attribute为稳定英文snake_case；沿用旧名，禁止编号后缀绕过冲突。'
    '新属性用store/expected_revision=null；已有属性变化用update且抄当前revision；未变不提交。'
    '模式一：store、需要全量替换的update、retire，字段action/subject/attribute/expected_revision/reason/support。'
    'support数组每项只含claim与evidence；evidence每项只含本章evidence_id和该片段中逐字quote。'
    '最多16项claim、每项1到8证据，不能拼接引文或编造编号；不输出start/end。'
    '模式二：已有source含support/claim_sources的属性优先update+claim_ops局部修改；'
    '只含action/subject/attribute/expected_revision/reason/claim_ops，不混入value/support/removals。'
    'op为add时含claim/evidence；replace含原0基index/逐字old_claim/新claim/evidence；remove含index/old_claim/reason/evidence。'
    'index始终指输入原列表，同一旧项只操作一次；未变项及旧来源由程序保留，不能为通过检查删除旧知识。'
    '旧单quote记录不能自动拆项，不能patch退休属性。全部失效用retire而非删空claim_ops。'
    '每个主体属性本章最多一次最终更新；章末状态以事件为准，数组不是时间线。'
    '累计认识不能只保留最后一条，也不能盲目并集：旧认识证伪须replace/remove。'
    '撤回怀疑与新增澄清事实可同时发生，分别更新原字段，不能只撤回而漏记澄清事实。'
    '空changes必须解释no_change_reason，不能靠删空提案逃避修复。'
    '修复收到candidate_errors时一次处理所有已列错误；保留其他正确候选，不改正文，不加重试。'
    '下面均为合法JSON格式示例，主体、版本、引文和编号只是格式占位，必须替换为当前输入真实资料：'
    +canonical(EXAMPLES))

def prepare_context(context):
    payload=copy.deepcopy(context)
    payload['memory_output_contract']=dict(version=2,examples=copy.deepcopy(EXAMPLES),
        value_policy='New support-only output: copy one claim to a string, multiple claims to an ordered list; retire derives null. Explicit legacy value is never silently overwritten.',
        update_policy='claim_ops stays unchanged; program retains untouched sources and derives the final result',
        forbidden_new_fields=['value','start','end','removals'],
        evidence_policy='Exact quote must belong to the chosen current-chapter segment; IDs are never auto-rebound')
    return payload

def derive_value(candidate,draft):
    if not isinstance(candidate,dict) or 'claim_ops' in candidate or 'value' in candidate or 'support' not in candidate:
        return copy.deepcopy(candidate)
    fields(candidate,('action','subject','attribute','expected_revision','reason','support'))
    support=checked_support(candidate['support'],draft,check_value=False)
    labels=[row['claim'] for row in support]
    value=None if candidate['action']=='retire' else labels[0] if len(labels)==1 else labels
    return dict(copy.deepcopy(candidate),value=value)

def candidate_error(candidate,index,exc,draft):
    details=copy.deepcopy(getattr(exc,'repair_details',{}))
    details.update(candidate_index=index,index_base=0,error=str(exc))
    details.setdefault('code','MEMORY_CANDIDATE_INVALID')
    if not isinstance(candidate,dict):return details
    patch='claim_ops' in candidate
    required={'action','subject','attribute','expected_revision','reason'}
    if patch:required.add('claim_ops');allowed=required
    elif 'support' in candidate:
        required.add('support');allowed=required|{'value'}
    else:
        required.add('value');allowed=required|{'quote','evidence_id'}
    missing=sorted(required-set(candidate));extra=sorted(set(candidate)-allowed)
    if missing:details['missing_fields']=missing
    if extra:details['unexpected_fields']=extra
    support=candidate.get('support')
    if isinstance(support,list) and all(isinstance(row,dict) and isinstance(row.get('claim'),str) for row in support):
        labels=[row['claim'] for row in support]
        if candidate.get('action')!='retire' and 'value' in candidate and candidate['value'] not in (labels,labels[0] if len(labels)==1 else labels):
            details['value_claim_mismatch']=dict(proposed_value=copy.deepcopy(candidate['value']),support_claims=labels,
                guidance='Resolve the intended claims; do not blindly discard either side. New output needs no duplicate value.')
    catalog=evidence_segments(draft);issues=[]
    groups=candidate.get('claim_ops',[]) if patch else candidate.get('support',[])
    if isinstance(groups,list):
        for i,row in enumerate(groups):
            items=row.get('evidence',[]) if isinstance(row,dict) else []
            if not isinstance(items,list):continue
            for j,item in enumerate(items):
                if not isinstance(item,dict):continue
                quote=item.get('quote');identifier=item.get('evidence_id')
                if not isinstance(quote,str) or not quote:continue
                matches=[segment['id'] for segment in catalog if quote in segment['text']]
                if identifier not in matches:
                    issues.append(dict(path=f"{'claim_ops' if patch else 'support'}[{i}].evidence[{j}]",
                        selected_evidence_id=identifier,matching_evidence_ids=matches,
                        guidance='Choose a verified exact-quote segment or repair the quote; code did not rebind it.'))
    if issues:details['evidence_issues']=issues
    return details
