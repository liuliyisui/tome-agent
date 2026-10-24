"""Explicit opt-in review catalog. Checks identity/coverage, never semantic truth."""
import copy
from .domain import ContractError, canonical, digest, fields, text, evidence_segments


def normalize_review_output(value):
    if not isinstance(value,dict):raise ContractError('Reviewer result must be object')
    result=copy.deepcopy(value);notes=[]
    if 'type' in result:
        if result['type']!='json_object':raise ContractError('Reviewer optional type must be exactly json_object')
        del result['type']
        notes.append(dict(rule='reviewer_json_object_type',field='type',value='json_object'))
    if 'removals_checks' in result:
        if result['removals_checks']!=[]:raise ContractError('Nonempty removals_checks cannot be discarded; use support_checks')
        del result['removals_checks'];notes.append(dict(rule='empty_removals_checks',field='removals_checks',value=[]))
    assessment=result.get('memory_check')
    if isinstance(assessment,dict) and 'support_checks' in assessment:
        if 'support_checks' in result:raise ContractError('Both nested and top-level support_checks supplied')
        result['support_checks']=assessment.pop('support_checks')
        notes.append(dict(rule='nested_support_checks',source='memory_check.support_checks',target='support_checks'))
    return result,notes


def review_decision_error(result):
    error=ContractError('Review decision inconsistent with hard issues or memory_check')
    error.repair_details=dict(code='REVIEW_DECISION_INCONSISTENT',
        observed=dict(approved=result['approved'],hard_issue_count=len(result['issues']),
                      memory_status=result['memory_check']['status']),
        guidance=[
            '只有issues为空且memory_check.status=sufficient时才能approved=true。',
            '拒绝必须有可核验硬问题或missing/uncertain；不得只在suggestions写关键知识遗漏又称记忆充分。',
            '逐项重新判断并给出依据，不为通过格式检查简单改为批准，不删真实问题；程序未替你改变结论。'])
    return error


def _catalog(context):
    items=[]
    old_facts={(row['subject'],row['attribute']):row for row in context.get('active_facts',[])}
    for i,row in enumerate(context.get('memory_changes',[]),1):
        old=old_facts.get((row['subject'],row['attribute']))
        transition=dict(action=row['action'],previous_value=copy.deepcopy(old['value']) if old else None,
            proposed_value=copy.deepcopy(row['value']),expected_revision=row['expected_revision'],
            archive_policy='更新当前值时程序归档旧版本；不是让新旧值同时作为当前事实')
        if 'support' in row:
            for j,claim in enumerate(row['support'],1):
                kind='add' if row['action']=='store' else 'full_update'
                previous=None
                if 'claim_ops' in row:
                    matches=[op for op in row['claim_ops'] if op.get('claim')==claim['claim'] and op['op'] in ('replace','add')]
                    if matches:
                        kind=matches[0]['op'];previous=matches[0].get('old_claim')
                    else:kind='retained'
                source={k:copy.deepcopy(v) for k,v in claim.items() if k!='claim'}
                source.setdefault('chapter_number',context.get('chapter_number'))
                source.setdefault('chapter_sha256',digest(context['current_draft']))
                items.append(dict(claim_ref=f'memory_{i}/claim_{j}',claim=claim['claim'],change_kind=kind,
                    previous_claim=previous,source=source,transition=copy.deepcopy(transition)))
        else:
            value=row['value']
            claims=value if isinstance(value,list) and value and all(isinstance(v,str) for v in value) else [value]
            for j,claim in enumerate(claims,1):
                label=claim if isinstance(claim,str) else canonical(claim)
                if row['action']=='retire':label=f"退役{row['attribute']}：{canonical(old['value']) if old else '原值未知'}"
                items.append(dict(claim_ref=f'memory_{i}/claim_{j}',claim=label,
                    change_kind='retire' if row['action']=='retire' else 'legacy_full_update',previous_claim=None,
                    source=dict(chapter_number=context.get('chapter_number'),chapter_sha256=digest(context['current_draft']),
                        quote=row.get('quote'),limitation='旧单引文，必须逐项判断，不能以引文存在代替支持充分'),
                    transition=copy.deepcopy(transition)))
        for j,removed in enumerate(row.get('removals',[]),1):
            items.append(dict(claim_ref=f'memory_{i}/removal_{j}',claim=removed['claim'],change_kind='remove',
                previous_claim=removed['claim'],source={k:copy.deepcopy(v) for k,v in removed.items() if k not in ('claim','reason')},
                removal_reason=removed['reason'],transition=copy.deepcopy(transition)))
    return items


def prepare_review_context(context):
    payload=copy.deepcopy(context)
    version=payload.get('review_contract_version',1)
    if type(version) is not int or version!=1:raise ContractError('Explicit review contract version must be 1')
    items=_catalog(payload)
    if 'review_items' in payload and payload['review_items']!=items:
        raise ContractError('Provided review_items differs from program-derived catalog')
    payload['review_contract_version']=1;payload['review_items']=items
    payload['review_output_contract']=dict(top_level=['approved','issues','suggestions','memory_check','support_checks'],
        memory_check_fields=['status','reason'],support_check_fields=['claim_ref','claim','status','reason'],
        check_status_values=['supported','partial','unsupported','uncertain'],
        decision_rules=[
            'approved=true当且仅当issues为空且memory_check.status=sufficient。',
            'approved=false需有可核验硬问题或memory_check为missing/uncertain。',
            '遗失仍有效旧知识也属于记忆不充分，不能只放suggestions并称sufficient。',
            '只更新的字段才替换当前记录；未出现在memory_changes中的字段保持原状，不据此报告丢失。'],
        rule='逐项按review_items编号回显claim原文，全部覆盖且不添加不存在的项；status由审核者判断，不预填正确答案')
    if payload.get('review_policy_version') in (2,3,4,5):
        from .review_state import DECISION_RULES
        payload['review_output_contract'].update(memory_check_fields=['coverage_status','reason'],
            decision_rules=DECISION_RULES.copy())
    if payload.get('review_policy_version') in (3,4,5):
        payload['review_output_contract']['top_level'].append('coverage_checks')
        payload['review_output_contract']['support_check_fields'].append('evidence')
        payload['review_output_contract']['semantic_fields']={
            'evidence':['bindings','context'],'binding':['index','quote'],
            'context':['ref','quote','purpose'],'coverage_check':['unit_ref','reason','facts'],
            'coverage_fact':['draft_quote','status','memory_refs','reason'],'memory_ref':['ref','quote']}
        if payload.get('review_policy_version')==4:
            payload['review_output_contract']['semantic_fields'].update(
                coverage_check=['reviewed_units','facts'],reviewed_unit=['unit_ref','reason'],
                coverage_fact=['evidence_ids','draft_quote','status','memory_refs','reason'])
        if payload.get('review_policy_version')==5:
            from .judgment_review import OUTPUT_CONTRACT
            payload['review_output_contract']=copy.deepcopy(OUTPUT_CONTRACT)
    payload['review_required_checks']=[
        '核对完整最终列表，而不只核对claim_ops本次改动项；移除项也逐项检查。',
        'retained引用原章节，新增/替换引用本章；区分当前值与历史值，旧值曾经正确不等于永远有效。',
        '有正文依据的状态变化可替换当前值，程序归档旧值；不因替换本身就认定知识丢失。',
        '同时逐段核对正文是否遗漏重要新事实，审核清单不包含未提取的信息，不能仅查清单。',
        '撤回旧怀疑时，核查是否还需要记录新确认的澄清事实；猜测/计划不升级为客观已发生事实。']
    references=copy.deepcopy(payload.get('hard_references',{}))
    references.update({f'fact_{i}':canonical(row) for i,row in enumerate(payload.get('active_facts',[]),1)})
    references.update({f'constraint_{i}':row for i,row in enumerate(payload.get('constraints',[]),1)})
    references.update({f'draft_{row["id"]}':row['text'] for row in evidence_segments(payload['current_draft'])})
    references.update({f'memory_{i}':canonical(row) for i,row in enumerate(payload.get('memory_changes',[]),1)})
    payload['hard_references']=references
    return payload


def validate_catalog_checks(result,context):
    catalog=prepare_review_context(context)['review_items']
    expected={row['claim_ref']:row['claim'] for row in catalog}
    checks=result.get('support_checks',[])
    if not isinstance(checks,list):raise ContractError('support_checks must be list')
    seen=set();all_supported=True
    for row in checks:
        try:fields(row,('claim_ref','claim','status','reason')+(('evidence',) if context.get('review_policy_version') in (3,4,5) else ()))
        except ContractError as exc:
            if context.get('review_policy_version') not in (3,4,5):raise
            from .semantic_review import error
            raise error(exc) from None
        ref=text(row['claim_ref'],'claim_ref')
        if ref not in expected or ref in seen:raise ContractError('Unknown or duplicate catalog ref: '+ref)
        if row['claim']!=expected[ref]:raise ContractError('Claim echo differs from catalog for '+ref)
        text(row['reason'],'support reason');seen.add(ref)
        if row['status'] not in ('supported','partial','unsupported','uncertain'):raise ContractError('Invalid support status')
        all_supported=all_supported and row['status']=='supported'
    if seen!=set(expected):raise ContractError('Missing catalog checks: '+canonical(sorted(set(expected)-seen)))
    if context.get('review_policy_version') not in (2,3,4,5) and not all_supported and (result.get('approved') or result.get('memory_check',{}).get('status')=='sufficient'):
        raise ContractError('Non-supported catalog items cannot be approved or called sufficient')
    return result
