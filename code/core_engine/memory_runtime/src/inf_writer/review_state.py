"""Policy v2: independent coverage judgment and program-derived support summary.

These are contract checks, not an oracle for the model's semantic judgments.
Never rewrite a reviewer decision, quote, or omission to make it pass.
"""
from .domain import ContractError, fields, text


DECISION_RULES=[
    'memory_check只含coverage_status和reason；coverage_status只判断重要知识覆盖，不评价已列候选的证据充分性。',
    '逐项support_checks全部supported、coverage_status=sufficient、issues为空时，且仅此时，approved=true。',
    'partial/unsupported需有引用有效的unsupported_memory硬问题；不因此编造memory_omission。',
    'coverage_status=missing当且仅当存在有证据和omission说明的memory_omission硬问题。',
    '任一uncertain仍不能批准；程序从逐项判断计算支持汇总，不填写额外支持总状态。',
    '只更新的字段才替换当前记录；未出现在memory_changes中的字段保持原状，不据此报告丢失。']


def review_prompt(base):
    # Remove old coupling rather than append mutually incompatible instructions.
    replacements=[
        ('只有具体证据支持的硬问题或记忆遗漏才阻止审核通过',
         '具体证据支持的硬问题、重要记忆遗漏或尚不确定的支持／覆盖判断都会阻止审核通过'),
        ('memory_check对象(status为sufficient/missing/uncertain，reason说明复核了哪些事实)',
         'memory_check对象(coverage_status为sufficient/missing/uncertain，reason说明重要知识是否覆盖)'),
        ('任一partial/unsupported/uncertain时approved=false且memory_check不能sufficient。',
         '任一partial/unsupported/uncertain时approved=false，但coverage_status可为sufficient；证据不足不等于遗漏。'),
        ('memory_check仅status/reason，','memory_check仅coverage_status/reason，'),
        ('approved=true当且仅当issues为空且memory_check.status=sufficient。',
         'approved=true当且仅当逐项全supported、issues为空且memory_check.coverage_status=sufficient。'),
        ('拒绝需要可核验硬问题或missing/uncertain；重要知识遗漏包括丢失仍有效旧知识，不能只放suggestions又称充分。',
         '拒绝需要可核验硬问题、支持不确定或覆盖missing/uncertain；重要知识遗漏包括丢失仍有效旧知识，不能只放suggestions又称覆盖充分。')]
    for old,new in replacements:
        if base.count(old)!=1:
            raise ContractError('Split review prompt base changed; inspect contract before use')
        base=base.replace(old,new)
    from .review_policy import REVIEW_POLICY_PROMPT
    policy=REVIEW_POLICY_PROMPT.replace('审核政策v1','审核政策v2').replace(
        'memory_check为missing时','memory_check.coverage_status为missing时')
    return base+policy+'支持／覆盖分开判断：'+''.join(DECISION_RULES)+(
        '每项只能根据所绑定全部证据判断支持度；正文别处存在相似事实不自动补足该项绑定。'
        '候选已保留的事实不报遗漏；核查coverage_refs不能跳过直接相关候选。'
        '有证据缺口但没有事实遗漏时：approved=false，coverage_status=sufficient，'
        '指出unsupported_memory并给对应partial/unsupported；不必为满足状态规则新增遗漏。')


def support_summary(result):
    checks=result.get('support_checks')
    if not isinstance(checks,list):raise ContractError('support_checks must be list')
    counts={name:0 for name in ('supported','partial','unsupported','uncertain')}
    for row in checks:
        status=row.get('status') if isinstance(row,dict) else None
        if not isinstance(status,str) or status not in counts:raise ContractError('Invalid support status')
        counts[status]+=1
    status='insufficient' if counts['partial'] or counts['unsupported'] else 'uncertain' if counts['uncertain'] else 'sufficient'
    return dict(status=status,total=len(checks),**counts)


def state_error(message,result):
    error=ContractError(message)
    assessment=result.get('memory_check')
    error.repair_details=dict(code='REVIEW_STATE_INCONSISTENT',
        observed=dict(approved=result.get('approved'),
            coverage_status=assessment.get('coverage_status') if isinstance(assessment,dict) else None,
            support_summary=support_summary(result)),
        required_memory_check_fields=['coverage_status','reason'],
        guidance=DECISION_RULES+['根据原证据重新判断；不自动批准、不改引文、不删真实问题、不编造遗漏。'])
    return error


def validate_coverage(result):
    try:
        assessment=result['memory_check']
        fields(assessment,('coverage_status','reason'))
        if assessment['coverage_status'] not in ('sufficient','missing','uncertain'):
            raise ContractError('Invalid coverage_status')
        text(assessment['reason'],'Coverage review reason')
    except ContractError as exc:
        raise state_error(str(exc),result) from None


def validate_state(result):
    coverage=result['memory_check']['coverage_status']
    summary=support_summary(result)
    kinds=[issue['kind'] for issue in result['issues']]
    if (coverage=='missing') != ('memory_omission' in kinds):
        raise state_error('Missing coverage and evidence-backed omission issues must agree',result)
    if summary['status']=='insufficient' and 'unsupported_memory' not in kinds:
        raise state_error('Partial/unsupported candidates require an evidence-backed unsupported_memory issue',result)
    can_approve=summary['status']=='sufficient' and coverage=='sufficient' and not kinds
    if result['approved']!=can_approve:
        raise state_error('Review decision inconsistent with support, coverage, or hard issues',result)
    return result
