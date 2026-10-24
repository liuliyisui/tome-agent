"""Model-facing names and one compatibility compiler; storage names stay stable."""
import copy
import re
from inf_writer.domain import ContractError,canonical

RECORD_NAMES=dict(fact='fact_record',learn='character_knowledge',
    event='dated_event_record',object='evidence_object',observe='observation_record',
    handoff='receipt_record',identify='person_identity_record',progress='check_progress_record',
    occurrence='chapter_action',plan='pending_intention')

OPERATIONS={
    'revise_intention':('revise_intention',dict(intention_ref='plan_id',new_value='value')),
    'establish_fact':('fact',dict(record_id='id',property_name='attribute',fact_class='kind')),
    'change_fact_value':('transition',dict(operation_id='id',fact_ref='fact_id',new_value='to_value',previous_value='from_value')),
    'record_character_knowledge':('learn',dict(record_id='id',character_id='actor',learned_record_ref='fact_id',source_action_ref='via_event')),
    'record_dated_event':('event',dict(record_id='id',story_date='date',timeline_relation='mode',involved_object_refs='objects',follows_dated_event_refs='after')),
    'register_evidence_object':('object',dict(record_id='id',carrier_form='form',availability='status',created_by_action_ref='origin_event',provenance_description='origin_description',derived_from_object_ref='source',dated_event_ref='event_id')),
    'record_observation':('observe',dict(record_id='id',observed_object_ref='object_id',observation_method='method',evidence_carrier_ref='source_id')),
    'record_receipt':('handoff',dict(record_id='id',signer_ids='signers',attendee_without_signature_ids='non_signers',attendee_ids='attendees')),
    'resolve_person_identity':('identify',dict(record_id='id',unidentified_person_id='unknown_id',identified_person_id='person_id')),
    'record_check_progress':('progress',dict(record_id='id',check_pass_id='pass_id',completed_count='completed',total_count='total',new_pass_reason_quote='restart_quote')),
}
OPERATION_BY_KIND={kind:name for name,(kind,_) in OPERATIONS.items()}
ENUM_NAMES={
    ('fact','kind'):dict(state='current_state',immutable='fixed_fact',belief='character_belief',planned='planned_intention'),
    ('event','mode'):dict(present='current_timeline',historical='historical_timeline'),
}
ACTION_SCOPES=dict(actual='performed_action',reported='reported_claim',planned='proposed_action')
MEMORY_KINDS=dict(state='state_summary',event='event_summary',knowledge='knowledge_summary',task='task_summary',legacy='legacy_memory',prose_excerpt='prose_excerpt')


def public_memory_rows(rows):
    result=copy.deepcopy(rows)
    for row in result:
        row['memory_kind']=MEMORY_KINDS.get(row.pop('kind'), 'legacy_memory')
        row['memory_revision']=row.pop('revision')
        row.pop('status',None)
        if 'canonical_reference' in row:row['state_record_reference']=row.pop('canonical_reference')
    return result


def public_kind(kind):return RECORD_NAMES.get(kind,kind) if isinstance(kind,str) else kind
def stored_kind(kind):return {v:k for k,v in RECORD_NAMES.items()}.get(kind,kind) if isinstance(kind,str) else kind


def public_field(kind,field):
    if field=='revision':return 'record_revision'
    if kind=='occurrence' and field=='mode':return 'assertion_scope'
    if field=='source_event':return 'recorded_by_action_ref'
    if kind=='object' and field=='origin':return 'creation_source_ref'
    name=OPERATION_BY_KIND.get(kind)
    fields=OPERATIONS[name][1] if name else {}
    return next((new for new,old in fields.items() if old==field),field)


def public_enum(kind,field,value):
    if kind=='occurrence' and field=='mode':return ACTION_SCOPES.get(value,value)
    return ENUM_NAMES.get((kind,field),{}).get(value,value)


def _move(row,new,old,path,notes):
    if new not in row:return
    value=row.pop(new)
    if old in row and canonical(row[old])!=canonical(value):
        error=ContractError(f'Conflicting interface aliases at {path}: {new} / {old}')
        error.repair_details=dict(path=path,conflicting_fields=[new,old]);raise error
    row[old]=value;notes.append(dict(path=path+'.'+new,storage_field=old,rule='public_field_name'))


def normalize_public_plan(plan):
    result=copy.deepcopy(plan);notes=[]
    for si,scene in enumerate(result.get('scenes',[]) if isinstance(result.get('scenes'),list) else []):
        if not isinstance(scene,dict):continue
        for bi,beat in enumerate(scene.get('beats',[]) if isinstance(scene.get('beats'),list) else []):
            if not isinstance(beat,dict):continue
            path=f'scenes[{si}].beats[{bi}]'
            _move(beat,'assertion_scope','mode',path,notes)
            if isinstance(beat.get('mode'),str):beat['mode']={v:k for k,v in ACTION_SCOPES.items()}.get(beat['mode'],beat['mode'])
            for ri,req in enumerate(beat.get('requires',[]) if isinstance(beat.get('requires'),list) else []):
                if isinstance(req,dict):_move(req,'record_revision','revision',path+f'.requires[{ri}]',notes)
            for ci,row in enumerate(beat.get('changes',[]) if isinstance(beat.get('changes'),list) else []):
                if not isinstance(row,dict):continue
                rp=path+f'.changes[{ci}]';name=row.pop('operation',None)
                if name is not None:
                    if not isinstance(name,str) or name not in OPERATIONS:
                        error=ContractError('Unknown operation; use the operation catalogue')
                        error.repair_details=dict(path=rp+'.operation',allowed_values=list(OPERATIONS));raise error
                    kind,_=OPERATIONS[name]
                    if 'type' in row and stored_kind(row['type'])!=kind:raise ContractError('Operation and legacy type disagree')
                    row['type']=kind
                    notes.append(dict(path=rp+'.operation',original=name,storage_id=kind,rule='operation_name'))
                kind=stored_kind(row.get('type'));name=OPERATION_BY_KIND.get(kind) if isinstance(kind,str) else None
                if name:
                    for new,old in OPERATIONS[name][1].items():_move(row,new,old,rp,notes)
                    row['type']=kind
                    for (record_type,field),values in ENUM_NAMES.items():
                        if kind==record_type and isinstance(row.get(field),str):row[field]={v:k for k,v in values.items()}.get(row[field],row[field])
    return result,notes


def validate_catalogue_names():
    if len(set(RECORD_NAMES.values()))!=len(RECORD_NAMES):raise ContractError('Duplicate record-kind name')
    if set(OPERATIONS)&set(RECORD_NAMES.values()):raise ContractError('Operation and record-kind names overlap')
    if len(OPERATION_BY_KIND)!=len(OPERATIONS):raise ContractError('Duplicate operation kind')
    for _,(_,fields) in OPERATIONS.items():
        if len(set(fields.values()))!=len(fields):raise ContractError('Ambiguous field alias')

validate_catalogue_names()


def public_repair_details(details,plan):
    """Translate diagnostics at the model boundary, using the same field catalogue.

    Invalid submitted values stay invalid: this never guesses the intended action.
    """
    def location(path):
        current=plan;kind=None;scope='plan'
        for key,index in re.findall(r'([A-Za-z_]+)|\[(\d+)\]',path):
            try:current=current[int(index)] if index else current[key]
            except (KeyError,IndexError,TypeError):break
            if key=='beats':scope='beat'
            if key=='requires':scope='requirement'
            if key=='changes':scope='change'
            if isinstance(current,dict) and scope=='change':
                kind=current.get('type')
                if not kind and current.get('operation') in OPERATIONS:kind=OPERATIONS[current['operation']][0]
        return scope,kind
    def field_name(field,scope,kind):
        if scope=='beat':return 'assertion_scope' if field=='mode' else field
        if scope=='requirement':return dict(id='reference_id',type='record_kind',revision='record_revision').get(field,field)
        if scope=='change':return 'operation' if field=='type' else public_field(kind,field)
        return field
    def path_name(path):
        if not isinstance(path,str):return path
        prefix,sep,field=path.rpartition('.')
        scope,kind=location(prefix if sep else path)
        return prefix+sep+field_name(field,scope,kind) if sep else path
    def convert(row,inherited_path='',role=''):
        if isinstance(row,list):return [convert(v,inherited_path,role) for v in row]
        if not isinstance(row,dict):return copy.deepcopy(row)
        path=row.get('path',inherited_path);scope,kind=location(path)
        record_kind=stored_kind(row.get('type'))
        if record_kind not in RECORD_NAMES:record_kind=None
        if record_kind is None and {'id','statement','participants','mode'}<=set(row):record_kind='occurrence'
        leaf=path.rsplit('.',1)[-1] if isinstance(path,str) else ''
        result={}
        for key,value in row.items():
            if record_kind:
                target=public_field(record_kind,key)
                if key=='type':
                    target='operation' if role=='proposed' and record_kind in OPERATION_BY_KIND else 'record_kind'
                    value=OPERATION_BY_KIND[record_kind] if target=='operation' else public_kind(record_kind)
                elif key=='id':target='record_id'
                elif isinstance(value,str):value=public_enum(record_kind,key,value)
                result[target]=convert(value,path,key)
            elif key=='path':result[key]=path_name(value)
            elif key=='field' and isinstance(value,str):result[key]=field_name(value,scope,kind)
            elif key in ('required_fields','optional_fields','missing_fields','unexpected_fields','expected_fields') and isinstance(value,list):
                result[key]=list(dict.fromkeys(field_name(v,scope,kind) for v in value if not (v=='id' and scope in ('plan','beat') and key!='unexpected_fields')))
            elif key=='allowed_values' and isinstance(value,list):
                if scope=='beat' and leaf=='mode':result[key]=[ACTION_SCOPES.get(v,v) for v in value]
                elif scope=='change' and leaf=='type':result[key]=[OPERATION_BY_KIND.get(v,v) for v in value]
                elif scope=='change':result[key]=[public_enum(kind,leaf,v) for v in value]
                else:result[key]=copy.deepcopy(value)
            else:result[key]=convert(value,path,key)
        error=row.get('error','')
        if error=='Event precondition does not match canonical state' and not row.get('candidate_records'):
            result['repair_guidance']='所填编号未解析到现有记录，不能只换命名空间或用revise_intention修订它。若确是本动作首次达成新安排，不把该新安排列为requires，改用establish_fact及fact_class=planned_intention建立；若依赖过去安排，只选给出的existing_intention_ids或其它真实目录编号，不伪造过去。'
        if 'unverified report cannot establish' in error:
            result['repair_guidance']='本条reported_claim只能写character_belief。若陈述实际描述当下说话、听到或展示，可将动作范围修正为performed_action，但未证实的说话内容仍不能写成客观事实；须保留人物、内容和来源。'
        if 'proposed future event is not an actual occurrence' in error:
            result['repair_guidance']='引用未来执行动作不能证明其已发生。若前面的statement描述当下达成约定，应修正那个动作的assertion_scope为performed_action，安排的fact_class仍是planned_intention；若确为未来动作，改用已有pending_intention引用，不伪造已完成事件。'
        if 'Indirect observation requires' in error:
            result['repair_guidance']='若直接查看的是照片/打印件本身，observed_object_ref选该载体、observation_method=direct、evidence_carrier_ref=null；若经照片观察另一个原物，observed_object_ref选原物、evidence_carrier_ref选独立照片且该照片derived_from_object_ref须指向原物。不要虚构原件可用。'
        if 'Fact identity already exists' in error:
            prior=row.get('prior') or {};proposed=row.get('proposed') or {}
            if prior.get('id') and 'value' in proposed and prior.get('kind') in ('state','belief'):
                result['replacement_operation_example']=dict(operation='change_fact_value',fact_ref='fact_record:'+prior['id'],new_value=copy.deepcopy(proposed['value']))
                result['repair_guidance']='同一主体同一属性已有稳定编号，替换本条新增操作为示例的change_fact_value。new_value须由你确认完整当前值；累计材料须保留仍持有的旧材料，不能把新增材料误当旧材料已丢失。更新后后续引用沿用fact_ref，不沿用被拒的新编号。程序不自动猜测累计或替换。'
        return result
    result=convert(details or {})
    result['interface_contract_version']=2
    result['instruction']='按公开字段路径及其allowed_values修复；不同字段的枚举不可互换。保留其它正确事件、值和描述，不删除事实绕过检查。'
    return result
