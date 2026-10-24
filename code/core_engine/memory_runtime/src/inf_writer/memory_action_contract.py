"""Action/identity feedback only: no choice of facts, conversion, or state mutation."""
import copy
from .domain import ContractError,identity


def prepare_memory_context(context):
    payload=copy.deepcopy(context)
    payload['memory_action_catalog']=[dict(subject=row['subject'],attribute=row['attribute'],
        expected_revision=row['revision'],status=row['status'],
        allowed_actions=['update','retire'] if row['status']=='active' else ['update'],
        claim_ops_available=row['status']=='active' and any(key in row.get('source',{}) for key in ('support','claim_sources')))
        for row in context.get('active_facts',[])]
    payload['memory_action_rules']=[
        '新增一条知识不等于新建一个已有属性；同subject+attribute已存在时禁止store。',
        '已有结构化知识字段新增信息，用update及claim_ops.add并抄当前revision；不变项与旧来源自动保留。',
        'catalog只说明输入中已有条目的动作，不是完整数据库的不存在证明；最终按原状态再次校验。',
        '没有变化则不提交；新属性才store且expected_revision=null；不改属性名绕过冲突。',
        '如果同章撤回怀疑并新增确认，分别对两个已有字段提出变化，每字段一次，返回完整批次。']
    return payload


def check_memory_action(candidate,state,index,changes):
    if not isinstance(candidate,dict) or not all(key in candidate for key in ('action','subject','attribute','expected_revision')):
        return  # The ordinary schema validator owns missing/unknown fields.
    old=state.facts.get(identity(candidate['subject'],candidate['attribute']))
    action=candidate['action'];revision=candidate['expected_revision']
    conflict=(action=='store' and (old is not None or revision is not None)) or (
        action in ('update','retire') and (old is None or type(revision) is not int or revision!=old['revision']))
    if not conflict:return
    current={key:copy.deepcopy(old[key]) for key in ('value','revision','status')} if old else None
    message=(f"{candidate['subject']}.{candidate['attribute']} already exists with revision={old['revision']}; use update for a changed value and match that revision, or omit an unchanged fact"
        if action=='store' and old else
        f"{candidate['subject']}.{candidate['attribute']}: current revision={old['revision'] if old else 'absent'}, proposed revision={revision}; update/retire must match an existing attribute revision; do not invent one"
        if action in ('update','retire') else
        f"New attribute {candidate['subject']}.{candidate['attribute']} requires store with expected_revision=null")
    error=ContractError(message)
    error.repair_details=dict(code='MEMORY_ACTION_CONFLICT',candidate_index=index,index_base=0,
        subject=candidate['subject'],attribute=candidate['attribute'],proposed_action=action,
        proposed_revision=revision,current=current,candidates=copy.deepcopy(changes),
        guidance=[
            '程序拒绝整批，未提交、未改动作、未删除任何候选。返回完整changes，保留其他仍正确的提案与证据。',
            '以subject+attribute匹配原状态：已有字段变化用update并抄current.revision；未变省略，新字段才store/null。',
            '新增已确认信息不是新建已有known_information；已有结构化字段可update+claim_ops.add，保留仍有效旧项。',
            '不要简单把store改为update后全量覆盖旧知识；依据正文重新判断该新增、替换或删除哪些项。',
            'claim_ops不附value/support/removals；操作索引针对输入原列表，不能发明证据或改名绕过冲突。'])
    raise error
