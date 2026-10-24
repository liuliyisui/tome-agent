"""Single field catalogue for planner shape checks and committed state records.

Descriptions are data; only fields used by state operations have closed types.
This module checks structure. Provenance/version/chronology live in continuity.
"""
import copy
from inf_writer.domain import ContractError,canonical
from .event_references import public_type
from .interface_contract import OPERATIONS,OPERATION_BY_KIND,public_field,public_enum

STATE_KINDS=('state','immutable','belief')
BEAT_MODES=('actual','reported','planned')
MAX_PLAN_BYTES=84000
RECORDS={
    'revise_intention':dict(required=('plan_id','value'),optional=(),enums={},id_policy='generated_operation'),
    'fact':dict(required=('subject','attribute','value','kind'),optional=(),enums=dict(kind=STATE_KINDS+('planned',))),
    'transition':dict(required=('fact_id','to_value'),optional=('expected_revision','from_value'),enums={},id_policy='generated_operation',
        reference_contract=dict(fact_id=dict(record_types=['fact'],instruction='Only a mutable fact value can transition. Object IDs identify evidence carriers, not location/custody fact records. Represent descriptive location/custody as a separate fact; do not change object form or provenance to express a move.'))),
    'learn':dict(required=('actor','fact_id','via_event'),optional=('reference_type',),enums={}),
    'event':dict(required=('date','mode','objects','after'),optional=(),enums=dict(mode=('present','historical'))),
    'object':dict(required=('label','form','status'),optional=('origin','origin_event','origin_description','source','event_id'),enums=dict(form=('original','photo','film','index','copy'),status=('missing','available'))),
    'observe':dict(required=('object_id','method','source_id'),optional=(),enums=dict(method=('direct','photo','film','index')),
        reference_contract=dict(source_id=dict(record_types=['object'],instruction='Directly viewing the named object (including a print/photo) uses null. Indirect viewing of another object requires a distinct carrier derived from that object.'))),
    'handoff':dict(required=('signers','non_signers','attendees'),optional=('signer_count',),enums={}),
    'identify':dict(required=('unknown_id','person_id'),optional=(),enums={}),
    'progress':dict(required=('pass_id','completed','total'),optional=('restart_quote',),enums={}),
}


class ShapeError(ContractError):
    def __init__(self,issues):
        super().__init__('Event structure rejected '+str(len(issues))+' field(s): '+issues[0]['error'])
        self.repair_details=dict(code='EVENT_SHAPE_ERRORS',issues=issues,
            instruction='Repair the listed structure before state simulation. Preserve other events, values and descriptions. Do not remove facts to satisfy the schema.')


def _object(value,required,optional,path,issues):
    if not isinstance(value,dict):
        issues.append(dict(path=path,error='Expected an object',expected_fields=list(required)));return False
    missing=set(required)-set(value);extra=set(value)-set(required)-set(optional)
    if missing or extra:issues.append(dict(path=path,error='Missing or unexpected fields',missing_fields=sorted(missing),unexpected_fields=sorted(extra),required_fields=list(required),optional_fields=list(optional)))
    return not missing and not extra


def record_issues(row,path,canonical_record=False):
    issues=[]
    if not isinstance(row,dict):return [dict(path=path,error='Record must be an object')]
    spec=RECORDS.get(row.get('type')) if isinstance(row.get('type'),str) else None
    if spec is None:return [dict(path=path+'.type',error='Unknown state operation',allowed_values=list(RECORDS))]
    generated_id=spec.get('id_policy')=='generated_operation' and not canonical_record
    required=('type',)+(() if generated_id else ('id',))+spec['required'];optional=spec['optional']+(('id',) if generated_id else ())
    if canonical_record:
        required+=('quote',)
        generated={'transition':('expected_revision','from_value'),'handoff':('signer_count',),'object':('origin',)}.get(row['type'],())
        required+=generated;optional=tuple(k for k in optional if k not in generated)
    _object(row,required,optional,path,issues)
    for key,allowed in spec['enums'].items():
        if canonical_record and row['type']=='fact' and key=='kind':allowed=STATE_KINDS
        if key in row and row[key] not in allowed:issues.append(dict(path=path+'.'+key,error='Unknown operational value',submitted_value=row[key],allowed_values=list(allowed)))
    for key in ('id','subject','attribute','actor','fact_id','via_event','label','date','pass_id','unknown_id','person_id','object_id','quote'):
        if key in row and (not isinstance(row[key],str) or not row[key].strip()):issues.append(dict(path=path+'.'+key,error='Expected a nonempty string'))
    for key in ('objects','after','signers','non_signers','attendees'):
        if key in row and (not isinstance(row[key],list) or any(not isinstance(v,str) or not v.strip() for v in row[key])):issues.append(dict(path=path+'.'+key,error='Expected a list of identifiers'))
    for key in ('expected_revision','signer_count','completed','total'):
        if key in row and (type(row[key]) is not int or row[key]<0):issues.append(dict(path=path+'.'+key,error='Expected a nonnegative integer'))
    for key in ('origin','origin_event','source','event_id','source_id'):
        if key in row and row[key] is not None and (not isinstance(row[key],str) or not row[key].strip()):issues.append(dict(path=path+'.'+key,error='Expected an identifier or null'))
    return issues


def validate_record(row,canonical_record=False):
    issues=record_issues(row,'record',canonical_record)
    if issues:raise ShapeError(issues)


def planner_catalogue():
    result={}
    for kind,spec in RECORDS.items():
        generated=spec.get('id_policy')=='generated_operation'
        name=OPERATION_BY_KIND[kind]
        hidden=('origin','reference_type','signer_count','expected_revision','from_value')
        required=['operation']+([] if generated else [public_field(kind,'id')])+[public_field(kind,k) for k in spec['required']]
        optional=[public_field(kind,k) for k in spec['optional'] if k not in hidden]
        result[name]=dict(required=required,optional=optional,result_record_kind=public_type('plan' if kind=='revise_intention' else 'fact' if kind=='transition' else kind),
            operational_values={public_field(kind,k):[public_enum(kind,k,v) for v in values] for k,values in spec['enums'].items()})
        if 'id_policy' in spec:result[name]['id_policy']=spec['id_policy']
        for field in ('optional','operational_values'):
            if not result[name][field]:result[name].pop(field)
        if 'reference_contract' in spec:
            result[name]['reference_contract']={public_field(kind,k):dict(instruction=v['instruction'],record_kinds=[public_type(t) for t in v['record_types']]) for k,v in spec['reference_contract'].items()}
    return result


def validate_plan_size(plan):
    size=len(canonical(plan).encode('utf-8'))
    if size>MAX_PLAN_BYTES:
        error=ContractError(f'Event plan exceeds explicit resource budget: {size}>{MAX_PLAN_BYTES} bytes; no truncation')
        error.repair_details=dict(code='EVENT_PLAN_RESOURCE_LIMIT',actual_bytes=size,limit_bytes=MAX_PLAN_BYTES)
        raise error


def validate_plan_shape(plan):
    validate_plan_size(plan)
    issues=[]
    scenes=plan.get('scenes') if isinstance(plan,dict) else None
    if not isinstance(scenes,list) or not scenes:raise ShapeError([dict(path='scenes',error='Expected a nonempty scene list')])
    for si,scene in enumerate(scenes):
        sp=f'scenes[{si}]'
        if not _object(scene,('id','purpose','participants','beats'),(),sp,issues):continue
        for key in ('id','purpose'):
            if not isinstance(scene[key],str) or not scene[key].strip():issues.append(dict(path=sp+'.'+key,error='Expected a nonempty string'))
        if not isinstance(scene['participants'],list) or any(not isinstance(v,str) or not v.strip() for v in scene['participants']):issues.append(dict(path=sp+'.participants',error='Expected normalized person identifiers'))
        if not isinstance(scene['beats'],list) or not scene['beats']:
            issues.append(dict(path=sp+'.beats',error='Expected a nonempty beat list'));continue
        for bi,beat in enumerate(scene['beats']):
            bp=sp+f'.beats[{bi}]'
            if not _object(beat,('id','statement','mode','requires','changes'),(),bp,issues):continue
            for key in ('id','statement'):
                if not isinstance(beat[key],str) or not beat[key].strip():issues.append(dict(path=bp+'.'+key,error='Expected a nonempty string'))
            if beat['mode'] not in BEAT_MODES:issues.append(dict(path=bp+'.mode',error='Unknown assertion scope',submitted_value=beat['mode'],allowed_values=list(BEAT_MODES)))
            if not isinstance(beat['requires'],list):issues.append(dict(path=bp+'.requires',error='Expected a requirement list'))
            else:
                for ri,req in enumerate(beat['requires']):
                    rp=bp+f'.requires[{ri}]'
                    if not _object(req,('id',),('type','revision','reference_id'),rp,issues):continue
                    if not isinstance(req['id'],str) or not req['id'].strip():issues.append(dict(path=rp+'.id',error='Expected a record identifier'))
                    if 'type' in req and (not isinstance(req['type'],str) or not req['type'].strip()):issues.append(dict(path=rp+'.type',error='Expected a record type string or omit for unique binding'))
                    if 'revision' in req and (type(req['revision']) is not int or req['revision']<0):issues.append(dict(path=rp+'.revision',error='Expected a nonnegative integer'))
            if not isinstance(beat['changes'],list):issues.append(dict(path=bp+'.changes',error='Expected an effect list'))
            else:
                for ci,row in enumerate(beat['changes']):issues.extend(record_issues(row,bp+f'.changes[{ci}]'))
    if issues:raise ShapeError(issues)
    canonical(plan)
    return plan
