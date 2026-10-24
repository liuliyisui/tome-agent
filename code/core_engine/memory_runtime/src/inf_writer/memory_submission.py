"""Explicit wire forms and bounded feedback; no candidate conversion or writes."""
import copy
from .domain import ContractError,evidence_segments,fields

BASE=('action','subject','attribute','expected_revision','reason')
FORMS={'store':['support'],'update':['claim_ops','support'],'retire':['support']}
EXAMPLES={
    'store':dict(action='store',subject='甲',attribute='location',expected_revision=None,reason='新增属性',
        support=[dict(claim='甲在门外',evidence=[dict(evidence_id='e0001')])]),
    'update':dict(action='update',subject='甲',attribute='location',expected_revision=1,reason='状态变化',
        claim_ops=[dict(op='replace',index=0,old_claim='甲在门外',claim='甲在门内',evidence=[dict(evidence_id='e0001')])]),
    'retire':dict(action='retire',subject='甲',attribute='location',expected_revision=1,reason='整条记录失效',
        support=[dict(claim='旧位置记录已失效',evidence=[dict(evidence_id='e0001')])])}

def add_contract(payload):
    result=copy.deepcopy(payload)
    result['memory_submission_contract']=dict(version=1,forms=copy.deepcopy(FORMS),
        examples=copy.deepcopy(EXAMPLES),index_base=0,
        operation_fields=dict(add=['op','claim','evidence'],replace=['op','index','old_claim','claim','evidence'],
                              remove=['op','index','old_claim','reason','evidence']),
        rules=['store只能support，绝不能claim_ops；不存在的属性不能update。',
               'update时support全量替换与claim_ops增量二选一；已有结构化字段优先增量，未变项由程序保留。',
               'retire只能support；无value/quote/start/end，来源编号照抄本章evidence_segments。',
               '例子不是正文事实，不可照抄主体、值、版本或证据；错误不由程序自动改动作。'])
    for row in result.get('memory_action_catalog',[]):
        row['allowed_forms']={'update':['claim_ops','support'] if row.get('claim_ops_available') else ['support']}
        if 'retire' in row['allowed_actions']:row['allowed_forms']['retire']=['support']
    if result.get('require_explicit_retention'):
        contract=result['memory_submission_contract']
        contract['version']=2
        contract['operation_fields']['retain']=['op','index','old_claim','reason']
        contract['rules']+=[
            'claim_ops更新必须逐个处理旧index：retain/replace/remove恰好一次，add不覆盖旧项；未变属性不提交。',
            '当前状态变化不能保留过期现状再追加新值；旧完整版本自动归档。retain明确说明该项为何仍有效。']
        contract['retain_example']=dict(op='retain',index=1,old_claim='仍有效的另一项知识',reason='本章没有改变该项且它仍有效')
        facts={(f['subject'],f['attribute']):f for f in result.get('active_facts',[])}
        for row in result.get('memory_action_catalog',[]):
            fact=facts[(row['subject'],row['attribute'])]
            labels=fact['value'] if isinstance(fact['value'],list) else [fact['value']]
            if row.get('claim_ops_available'):row['required_old_indices']=list(range(len(labels)))
    return result

def check_submission(value,context):
    fields(value,('changes',),('no_change_reason',))
    candidates=value['changes']
    if not isinstance(candidates,list) or len(candidates)>128:raise ContractError('changes must have at most 128 candidates')
    valid_ids=[r['id'] for r in evidence_segments(context['current_draft'])]
    errors=[]
    def error(index,path,code,**detail):
        errors.append(dict(candidate_index=index,index_base=0,path=path,code=code,**detail))
    def shape(item,required,index,path,code='INVALID_FIELDS'):
        required=set(required)
        missing=sorted(required-set(item)) if isinstance(item,dict) else sorted(required)
        extra=sorted(set(item)-required) if isinstance(item,dict) else []
        if missing or extra or not isinstance(item,dict):
            error(index,path,code,missing_fields=missing,unexpected_fields=extra,required_fields=sorted(required))
            return False
        return True
    for index,candidate in enumerate(candidates):
        path=f'changes[{index}]'
        action=candidate.get('action') if isinstance(candidate,dict) else None
        if not isinstance(action,str) or action not in FORMS:
            error(index,path,'INVALID_ACTION',allowed_actions=list(FORMS));continue
        groups=[key for key in ('support','claim_ops') if key in candidate]
        if len(groups)!=1 or groups[0] not in FORMS[action]:
            code='STORE_REQUIRES_SUPPORT' if action=='store' else 'RETIRE_REQUIRES_SUPPORT' if action=='retire' else 'UPDATE_REQUIRES_EXCLUSIVE_FORM'
            expected=set(BASE)|{'support' if action!='update' else 'claim_ops'}
            error(index,path,code,missing_fields=sorted(expected-set(candidate)),
                unexpected_fields=sorted(set(candidate)-expected),allowed_forms=FORMS[action],
                instruction='store/retire用support；仅已有结构化记录的update可用claim_ops。按example重新提交完整changes，不改正文或删除正确条目。',
                example=copy.deepcopy(EXAMPLES[action]));continue
        form=groups[0]
        if not shape(candidate,BASE+(form,),index,path):continue
        rows=candidate[form]
        maximum=32 if form=='claim_ops' else 16
        if not isinstance(rows,list) or not 1<=len(rows)<=maximum:
            error(index,path+'.'+form,'INVALID_GROUP_COUNT',minimum=1,maximum=maximum);continue
        for j,row in enumerate(rows):
            rowpath=f'{path}.{form}[{j}]'
            required=('claim','evidence')
            if form=='claim_ops':
                kind=row.get('op') if isinstance(row,dict) else None
                if kind=='add':required=('op','claim','evidence')
                elif kind=='replace':required=('op','index','old_claim','claim','evidence')
                elif kind=='remove':required=('op','index','old_claim','reason','evidence')
                elif kind=='retain':required=('op','index','old_claim','reason')
                else:error(index,rowpath,'INVALID_CLAIM_OPERATION',allowed_operations=['add','replace','remove','retain']);continue
            if not shape(row,required,index,rowpath):continue
            if form=='claim_ops' and row.get('op')=='retain':continue
            evidence=row['evidence']
            if not isinstance(evidence,list) or not 1<=len(evidence)<=8:
                error(index,rowpath+'.evidence','INVALID_SOURCE_COUNT',minimum=1,maximum=8);continue
            for k,item in enumerate(evidence):
                itempath=f'{rowpath}.evidence[{k}]'
                if not shape(item,('evidence_id',),index,itempath):continue
                if not isinstance(item['evidence_id'],str) or item['evidence_id'] not in valid_ids:
                    error(index,itempath+'.evidence_id','UNKNOWN_SOURCE_ID',selected_evidence_id=copy.deepcopy(item['evidence_id']),
                        valid_evidence_ids=valid_ids,instruction='逐字选择本章已有编号，保留e前缀；程序不会自动补前缀或重定位。')
        if form=='claim_ops' and context.get('require_explicit_retention'):
            if all(isinstance(row,dict) and row.get('op')=='retain' for row in rows):
                error(index,path+'.claim_ops','NO_MEMORY_CHANGE',instruction='所有旧项都未变时省略该属性；整批无变化则返回changes=[]及no_change_reason，不创建无意义新版本。')
            old=next((f for f in context.get('active_facts',[]) if f['subject']==candidate['subject'] and f['attribute']==candidate['attribute']),None)
            if old is not None:
                labels=old['value'] if isinstance(old['value'],list) else [old['value']]
                handled=set()
                for j,row in enumerate(rows):
                    if not isinstance(row,dict) or row.get('op') not in ('retain','replace','remove'):continue
                    slot=row.get('index')
                    if type(slot) is not int or not 0<=slot<len(labels):
                        error(index,f'{path}.claim_ops[{j}].index','INVALID_OLD_INDEX',allowed_indices=list(range(len(labels))));continue
                    if slot in handled:error(index,f'{path}.claim_ops[{j}].index','DUPLICATE_OLD_INDEX',selected_index=slot)
                    handled.add(slot)
                    if row.get('old_claim')!=labels[slot]:
                        error(index,f'{path}.claim_ops[{j}].old_claim','OLD_CLAIM_MISMATCH',selected_index=slot,expected_old_claim=labels[slot])
                unresolved=sorted(set(range(len(labels)))-handled)
                if unresolved:
                    error(index,path+'.claim_ops','OLD_CLAIMS_NOT_RECONCILED',subject=candidate['subject'],attribute=candidate['attribute'],
                        unresolved_indices=unresolved,unresolved_claims=[dict(index=i,old_claim=labels[i]) for i in unresolved],
                        instruction='每个旧index明确retain/replace/remove一次，add不覆盖旧项。仍有效才retain；过期现状应replace/remove；不要为通过而删光仍有效知识。',
                        retain_fields=['op','index','old_claim','reason'])
    if errors:
        first=errors[0]
        exc=ContractError(f"Memory submission {first['path']}: {first['code']}; 修复details列出的条目并返回完整changes")
        exc.repair_details=dict(code='MEMORY_SUBMISSION_ERRORS',index_base=0,candidate_errors=errors[:64],
            total_errors=len(errors),remaining_errors=max(0,len(errors)-64))
        raise exc
    return value

def compact_feedback(detail):
    """Keep actionable diagnostics but not duplicated candidates/full quotes."""
    if not isinstance(detail,dict):return {}
    def clean(value):
        if isinstance(value,dict):return {k:clean(v) for k,v in value.items() if k not in ('candidates','candidate','quote','source','previous_output')}
        if isinstance(value,list):return [clean(v) for v in value]
        return copy.deepcopy(value)
    return clean(detail)
