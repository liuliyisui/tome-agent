"""Prepare -> simulate -> freeze -> realize -> commit -> project, never prose-led truth."""
import copy
import re

from inf_writer.domain import ContractError,canonical,digest,evidence_segments,fields,text
from inf_writer.tiered_memory import apply_delta
from .continuity import apply
from .time_calculation import calculate,render as render_time,unbound_claims,validate_literal_intervals
from .identifiers import record_identifier,attribute_identifier
from .event_contract import BEAT_MODES,RECORDS,planner_catalogue,validate_plan_shape,validate_plan_size
from .event_references import plan_record,REFERENCE_GROUPS,internal_type,public_type,parse_reference,reference_id,action_aliases
from .interface_contract import normalize_public_plan,ACTION_SCOPES


TOKEN=re.compile(r'\[\[event:([A-Za-z][A-Za-z0-9_]{0,63})\]\]')
GROUPS=('events','objects','observations','handoffs','identities','progress','facts','knowledge')
TYPE_GROUP={k:v for k,v in REFERENCE_GROUPS.items() if k!='occurrence'}
REFERENCE_GROUP=REFERENCE_GROUPS
STATE_CONTRACT=dict(version=2,
    instruction='operation是要执行的动作，record_kind是程序给出的记录类别，二者不混用。按schemas选择operation及其字段。引用已有记录使用完整reference_id，不重复抄写类别、旧值或版本；程序在执行位置确定这些机械信息。property_name是自由显示名称，允许中文。不要填写quote，来源由程序绑定。',
    schemas=planner_catalogue())
STATE_CONTRACT['reference_contract']=dict(
    instruction='Choose an existing reference_id. The program owns record kinds, local/full ID resolution and omitted versions; do not classify the reference yourself.',
    examples=['fact_record:letter_location','chapter_action:c0001.arrival','dated_event_record:accident_date','pending_intention:visit_station'],
    definitions=dict(chapter_action='已登记章节动作或对话，断言范围单独标记',dated_event_record='带明确日期的时间线记录',pending_intention='待办或意图，不代表已经完成',prose_excerpt='实际正文摘录，不是世界状态前提'))
CONTRACT=dict(version=2,instruction=(
    '先确定本章发生什么，再写正文。planner必须额外输出scenes数组，每场id/purpose/participants/beats。'
    '每个beat含id/statement/assertion_scope/requires/changes；id在本章唯一。assertion_scope按assertion_scopes区分实际动作、传闻和提议。'
    'participants使用稳定人物id；通信方式是自由描述，与人物身份分开。'
    'statement是关键情节陈述；changes使用state_record_contract中各operation的字段，不把操作名当记录类别。'
    'requires优先只填reference_id，例如{"reference_id":"chapter_action:前面动作的id"}，或直接选已给出的引用字符串；不要重复填写类型。程序确定类型、完整编号及缺省版本。显式旧版本仍须精确匹配。changes不写quote，程序以statement绑定来源。'
    '从retrieved_memory选用已给出的reference_id；记录类别含义见reference_contract.definitions。版本区分record_revision（状态记录）、memory_revision（记忆条目）及memory_bank_revision（整库）。'
    '物证的created_by_action_ref是来源动作引用，provenance_description只是来历描述，derived_from_object_ref是另一个载体。不得混用。'
    '传闻仅产生人物信念，不升级为客观事实；提议只产生意图，不改变现实状态。'
    '没有状态变化的对话/动作也需要beat，changes可为空；不需要虚构属性变化来凑记录。'
    '精确计算可选time_calculations；模糊约定直接保留描述。writer展开场景，不执行正文内容校验，记忆来源从实际保存的正文建立。'
    '准备方案不是已经发生；只有正文保存时才提交候选状态。'
    'requires只列本事件发生之前已登记的依赖，不是本事件涉及的道具清单，也不是本事件准备建立的结果。'
    '空状态的首次介绍、发现或登记可用requires=[]；其结果写changes，后续事件才可引用。'
),assertion_scopes={value:dict(performed_action='实际动作',reported_claim='人物转述或传闻',proposed_action='提议或计划')[value] for value in ACTION_SCOPES.values()})
CONTRACT['dependency_examples']=[
    dict(id='introduce',statement='甲在门口登记来信。',assertion_scope='performed_action',requires=[],
        changes=[dict(operation='establish_fact',record_id='letter_location',subject='来信',property_name='位置',value='门口',fact_class='current_state')]),
    dict(id='move',statement='甲把来信从门口带进屋内。',assertion_scope='performed_action',requires=[dict(reference_id='fact_record:letter_location')],
        changes=[dict(operation='change_fact_value',fact_ref='fact_record:letter_location',new_value='屋内')])]
CONTRACT['scope_examples']=[
    '当场约定明天取件：动作performed_action，安排planned_intention；设想尚未执行的明天取件才是proposed_action。',
    '说话/听到/展示实际发生用performed_action；内容未核实仍须character_belief。reported_claim不可建立客观事实。']


def _id(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,63}',value):
        raise ContractError('Scene and beat IDs must be stable English identifiers')
    return value


def normalize_plan(proposal,state,chapter=None,references=None):
    validate_plan_size(proposal)
    result,notes=normalize_public_plan(proposal)
    for si,scene in enumerate(result.get('scenes',[]) if isinstance(result.get('scenes'),list) else []):
        if not isinstance(scene,dict):continue
        for bi,beat in enumerate(scene.get('beats',[]) if isinstance(scene.get('beats'),list) else []):
            if not isinstance(beat,dict):continue
            for ci,row in enumerate(beat.get('changes',[]) if isinstance(beat.get('changes'),list) else []):
                if not isinstance(row,dict):continue
                target=parse_reference(row.get('plan_id',row.get('fact_id')))
                explicit=row.get('type')=='revise_intention'
                if not explicit and not (row.get('type')=='transition' and target and target[0]=='plan'):continue
                identifier=target[1] if target else row.get('plan_id')
                prior=(references or {}).get('plans',{}).get(identifier) if isinstance(identifier,str) else None
                if (target and target[0]!='plan') or not prior:
                    error=ContractError('Intention revision requires an existing pending_intention')
                    error.repair_details=dict(path=f'scenes[{si}].beats[{bi}].changes[{ci}]',available_reference_ids=['pending_intention:'+i for i in (references or {}).get('plans',{})],
                        repair_guidance='revise_intention只修已有意图。若本动作首次达成新安排，用establish_fact及fact_class=planned_intention建立，不可引用尚不存在的意图作为前提。');raise error
                allowed={'type','plan_id','value','id'} if explicit else {'type','fact_id','to_value','id'}
                if set(row)-allowed:raise ContractError('Intention revision contains unsupported fields')
                if ('value' if explicit else 'to_value') not in row:raise ContractError('Intention revision requires new_value')
                row_value=copy.deepcopy(row['value'] if explicit else row['to_value'])
                row.clear();row.update(type='fact',id=identifier,subject=prior['subject'],attribute=prior['attribute'],value=row_value,kind='planned')
                notes.append(dict(path=f'scenes[{si}].beats[{bi}].changes[{ci}]',rule='program_owned_intention_revision',reference_id='pending_intention:'+identifier))
    event_aliases=action_aliases(state,result,chapter)
    typed_events={key:key for key in state.get('events',{})}
    for s in result.get('scenes',[]) if isinstance(result.get('scenes'),list) else []:
        if not isinstance(s,dict):continue
        for b in s.get('beats',[]) if isinstance(s.get('beats'),list) else []:
            if not isinstance(b,dict):continue
            for row in b.get('changes',[]) if isinstance(b.get('changes'),list) else []:
                if isinstance(row,dict) and internal_type(row.get('type'))=='event' and isinstance(row.get('id'),str) and row['id'].strip():
                    typed_events[row['id']]=record_identifier(row['id'])
    def person(value,path):
        # An explicit person namespace is a wire spelling, not a second person.
        original=copy.deepcopy(value);channel=None
        if isinstance(value,dict):
            # Only id participates in identity. Every other JSON field is
            # retained descriptive metadata, including empty/unknown channels.
            valid=('id' in value and isinstance(value['id'],str) and bool(value['id'].strip()))
            if not valid:
                error=ContractError('Participant object requires a nonempty id and optional channel/label')
                error.repair_details=dict(locator=dict(path=path),submitted_participant=original,
                    expected_schema=dict(required=['id'],descriptions='Other fields are preserved JSON metadata; they do not determine identity or factual validity'))
                raise error
            channel=value.get('channel','in_person');value=value['id']
        if isinstance(value,str):
            marked=re.fullmatch(r'(.+?)[（(](电话(?:中)?|视频(?:中)?|远程)[）)]',value)
            if marked:
                value=marked[1];channel='phone' if marked[2].startswith('电话') else 'video' if marked[2].startswith('视频') else 'remote'
        if isinstance(value,str) and value.startswith('person:') and value[7:]:
            value=value[7:]
        if value!=original or channel is not None:
            note=dict(path=path,original=original,storage_id=value)
            if channel is not None:note['channel']=channel
            notes.append(note)
        return value
    def convert(owner,key,path,nullable=False,event_ref=False):
        if key not in owner or (nullable and owner[key] is None):return
        old=owner[key]
        if key!='id':
            qualified=parse_reference(old)
            if qualified:
                expected={'via_event':('occurrence',),'origin':('occurrence','event'),'event_id':('event',),
                    'object_id':('object',),'source_id':('object',),'source':('object',)}.get(key)
                if key=='fact_id' and owner.get('type')=='transition':expected=('fact',)
                if expected and qualified[0] not in expected:
                    exc=ContractError('Reference namespace does not match this field')
                    exc.repair_details=dict(path=path,submitted_value=old,allowed_record_kinds=[public_type(k) for k in expected]);raise exc
                old=qualified[1];owner[key]=old
        if event_ref and isinstance(old,str) and old in event_aliases:
            candidates=event_aliases[old]
            if len(candidates)!=1:raise ContractError('Ambiguous chapter action reference')
            owner[key]=next(iter(candidates))
            if owner[key]!=old:notes.append(dict(path=path,original=old,storage_id=owner[key],rule='event_reference'))
            return
        if event_ref and isinstance(old,str) and '.' in old:
            # Keep unresolved action paths visible for missing/future checks;
            # never turn an unknown path into an unrelated ordinary record ID.
            owner[key]=old
            return
        try:new=record_identifier(old)
        except ContractError as exc:
            exc.repair_details=dict(locator=dict(path=path),submitted_id=old)
            raise
        owner[key]=new
        if new!=old:notes.append(dict(path=path,original=old,storage_id=new))
    scenes=result.get('scenes',[])
    if not isinstance(scenes,list):return result,notes
    for si,scene in enumerate(scenes):
        if not isinstance(scene,dict):continue
        convert(scene,'id',f'scenes[{si}].id')
        if isinstance(scene.get('participants'),list):
            scene['participants']=[person(v,f'scenes[{si}].participants[{i}]') for i,v in enumerate(scene['participants'])]
        for bi,beat in enumerate(scene.get('beats',[]) if isinstance(scene.get('beats'),list) else []):
            if not isinstance(beat,dict):continue
            path=f'scenes[{si}].beats[{bi}]';convert(beat,'id',path+'.id')
            if isinstance(beat.get('requires'),list):
                for ri,req in enumerate(beat['requires']):
                    if isinstance(req,str):
                        beat['requires'][ri]=dict(id=req)
                        notes.append(dict(path=path+f'.requires[{ri}]',original=req,storage_id=req,rule='identifier_requirement'))
            for ri,req in enumerate(beat.get('requires',[]) if isinstance(beat.get('requires'),list) else []):
                if isinstance(req,dict):
                    raw=req.get('reference_id',req.get('id'));parsed=parse_reference(raw)
                    if 'reference_id' in req and not parsed:
                        if not isinstance(raw,str) or not raw.strip() or ':' in raw:
                            error=ContractError('Reference requires a nonempty bare ID or a known record namespace')
                            error.repair_details=dict(path=path+f'.requires[{ri}].reference_id',submitted_value=raw,
                                instruction='选择目录中的reference_id；裸编号仅在候选唯一时可绑定。');raise error
                        if 'id' in req and req['id']!=raw:raise ContractError('Conflicting id and reference_id')
                        req['id']=req.pop('reference_id')
                    if parsed:
                        kind,identifier=parsed
                        if 'id' in req and req['id'] not in (raw,identifier):raise ContractError('Conflicting id and reference_id')
                        req.update(id=identifier,type=kind,reference_id=raw)
                    elif 'type' in req:req['type']=internal_type(req['type'])
                    convert(req,'id',path+f'.requires[{ri}].id',event_ref=req.get('type')=='occurrence' or req.get('id') in state.get('event_log',{}) or (isinstance(req.get('id'),str) and '.' in req['id'] and req['id'] in event_aliases))
                    if 'reference_id' in req:req['reference_id']=reference_id(req['type'],req['id'])
            for ci,row in enumerate(beat.get('changes',[]) if isinstance(beat.get('changes'),list) else []):
                if not isinstance(row,dict):continue
                prefix=path+f'.changes[{ci}]'
                operation=internal_type(row.get('type'))
                if operation!=row.get('type'):
                    notes.append(dict(path=prefix+'.type',original=row['type'],storage_id=operation,rule='public_record_name'))
                    row['type']=operation
                if 'reference_type' in row:row['reference_type']=internal_type(row['reference_type'])
                if row.get('type')=='learn':
                    target=parse_reference(row.get('fact_id'))
                    if target:
                        if 'reference_type' in row and row['reference_type']!=target[0]:raise ContractError('Conflicting learned-record reference kind')
                        row['reference_type']=target[0]
                spec=RECORDS.get(row.get('type'),{}) if isinstance(row.get('type'),str) else {}
                if spec.get('id_policy')=='generated_operation' and 'id' not in row:
                    row['id']='op_'+digest(canonical([chapter,scene.get('id'),beat.get('id'),ci,row['type'],row.get('fact_id')]))[:32]
                    notes.append(dict(path=prefix+'.id',original=None,storage_id=row['id'],rule='generated_operation_id'))
                if row.get('type')=='object':
                    explicit_origin='origin_event' in row
                    if 'origin_event' in row:
                        if 'origin' in row and row['origin']!=row['origin_event']:
                            raise ContractError('Specify a single origin event; put descriptive provenance in origin_description')
                        row['origin']=row.pop('origin_event')
                    origin=row.setdefault('origin',None)
                    if isinstance(origin,str) and origin in typed_events:row['origin']=typed_events[origin]
                    elif not explicit_origin and isinstance(origin,str) and origin not in event_aliases and not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,63}',origin) and not re.match(r'^c\d{4}\.',origin):
                        description=row.get('origin_description')
                        row['origin_description']=copy.deepcopy(origin) if description is None or description==origin else dict(description=description,legacy_description=origin)
                        row['origin']=None
                        notes.append(dict(path=prefix+'.origin',original=origin,storage_id=None,rule='unverified_origin_description'))
                for key in ('actor','subject','person_id','unknown_id'):
                    if key in row:row[key]=person(row[key],prefix+'.'+key)
                for key in ('signers','non_signers','attendees'):
                    if isinstance(row.get(key),list):row[key]=[person(v,prefix+f'.{key}[{i}]') for i,v in enumerate(row[key])]
                for key in ('id','fact_id','object_id','origin','source','event_id','source_id'):
                    convert(row,key,prefix+'.'+key,nullable=True,event_ref=key in ('origin','event_id'))
                convert(row,'via_event',prefix+'.via_event',event_ref=True)
                if row.get('type')=='observe' and row.get('method')=='direct' and row.get('source_id')==row.get('object_id'):
                    row['source_id']=None
                    notes.append(dict(path=prefix+'.source_id',rule='direct_observation_redundant_self_carrier',storage_value=None))
                for key in ('objects','after'):
                    if isinstance(row.get(key),list):
                        values=[]
                        for value in row[key]:
                            parsed=parse_reference(value)
                            expected='object' if key=='objects' else 'event'
                            if parsed and parsed[0]!=expected:raise ContractError('Reference list namespace does not match '+key)
                            values.append(record_identifier((parsed or (None,value))[1]))
                        row[key]=values
    return result,notes


class EventPreflightError(ContractError):
    def __init__(self,issues):
        super().__init__('Event preflight rejected '+str(len(issues))+' item(s): '+issues[0]['error'])
        self.repair_details=dict(code='EVENT_PREFLIGHT_ERRORS',issues=issues,
            instruction='Use scene_id, beat_id and change_index to fix the listed effects. Preserve other correct facts and statements. Attribute labels are normalized by the program; do not translate or delete facts to bypass checks.')


def _prepare(state,proposal,chapter,cursor,references):
    original_proposal=copy.deepcopy(proposal)
    proposal,normalizations=normalize_plan(proposal,state,chapter,references=references)
    validate_plan_shape(proposal)
    scenes=proposal.get('scenes')
    cursor.update(path='time_calculations',field='time_calculations')
    computed=calculate(proposal.get('time_calculations',[]))
    candidate=copy.deepcopy(state);seen=set();scene_ids=set();frozen=[];projection=[];issues=[]
    plans=copy.deepcopy(references.get('plans',{}))
    for scene in scenes:
        cursor.clear();cursor.update(chapter=chapter,path=f'scenes[{len(frozen)}]')
        fields(scene,('id','purpose','participants','beats'))
        sid=_id(scene['id']);text(scene['purpose'],'Scene purpose')
        if sid in scene_ids:raise ContractError('Duplicate scene identity')
        scene_ids.add(sid)
        people=scene['participants']
        if not isinstance(people,list) or any(not isinstance(p,str) or not p.strip() for p in people) or len(set(people))!=len(people):
            raise ContractError('Scene participants must be distinct identities')
        output=dict(id=sid,purpose=scene['purpose'],participants=copy.deepcopy(people),beats=[])
        for beat in scene['beats']:
            cursor.clear();cursor.update(chapter=chapter,scene_id=sid,
                path=f'scenes[{len(frozen)}].beats[{len(output["beats"])}]')
            fields(beat,('id','statement','mode','requires','changes'))
            bid=_id(beat['id'])
            cursor['beat_id']=bid
            if bid in seen:raise ContractError('Beat identities must be unique')
            seen.add(bid)
            if beat['mode'] not in BEAT_MODES:raise ContractError('Beat mode must separate events, reports and plans')
            raw=text(beat['statement'],'Canonical event statement')
            if '[[event:' in raw:raise ContractError('A canonical statement cannot recursively reference an event placeholder')
            statement=render_time(raw,computed,check_semantics=False)
            if not isinstance(beat['requires'],list) or not isinstance(beat['changes'],list):raise ContractError('Event preconditions and changes must be lists')
            for req_index,req in enumerate(beat['requires']):
                cursor.update(field='requires',requirement_index=req_index)
                fields(req,('id',),('type','revision','reference_id'))
                if req.get('type')=='occurrence' and req['id'] in seen:req['id']=f'c{chapter:04d}.'+req['id']
                binding=references.get('memory',{}).get(req['id'])
                if binding:
                    if ('reference_id' in req and req['type']!=binding['type']) or ('revision' in req and req['revision']!=binding['memory_revision']):
                        issues.append(dict(scene_id=sid,beat_id=bid,field='requires',path=cursor['path']+f'.requires[{req_index}]',
                            error='Memory reference type/version does not match its canonical binding',requirement=copy.deepcopy(req),canonical_reference=copy.deepcopy(binding)))
                        continue
                    original=copy.deepcopy(req)
                    req['id']=binding['id'];req['type']=binding['type']
                    if 'revision' in req:req['revision']=binding['revision']
                    normalizations.append(dict(path=cursor['path']+f'.requires[{req_index}]',original=original,canonical_reference=copy.deepcopy(req),rule='memory_canonical_reference'))
                matches=[dict(type=kind,record=copy.deepcopy(candidate[group][req['id']]))
                    for kind,group in REFERENCE_GROUP.items() if req['id'] in candidate[group]]
                if req['id'] in plans:matches.append(dict(type='plan',record=copy.deepcopy(plans[req['id']])))
                local=f'c{chapter:04d}.'+req['id']
                if local in candidate['event_log']:
                    matches.append(dict(type='occurrence',record=copy.deepcopy(candidate['event_log'][local])))
                available_reference_ids=[reference_id(m['type'],m['record']['id']) for m in matches]
                if 'reference_id' in req or req.get('type')=='plan':
                    matches=[m for m in matches if m['type']==req['type']]
                elif req.get('type'):
                    # Internal ID-only bindings may derive their actual kind,
                    # but a future intention must never satisfy a fact/action.
                    matches=[m for m in matches if m['type']!='plan']
                if len(matches)==1:
                    original=copy.deepcopy(req);match=matches[0]
                    req['type']=match['type'];req['id']=match['record']['id']
                    if 'reference_id' in req:req['reference_id']=reference_id(req['type'],req['id'])
                    if req!=original:
                        normalizations.append(dict(path=cursor['path']+f'.requires[{req_index}]',original=original,
                            canonical_reference=copy.deepcopy(req),rule='program_owned_reference_binding'))
                group=REFERENCE_GROUP.get(req.get('type'))
                prior=matches[0]['record'] if len(matches)==1 else None
                if prior and 'revision' not in req:
                    req['revision']=prior.get('revision',1)
                elif prior and req.get('revision')==0 and type(req.get('revision')) is int and req['id'] not in (references.get('plans',{}) if req.get('type')=='plan' else state.get(group,{})):
                    req['revision']=1
                if prior and req.get('type')=='occurrence' and prior.get('mode')=='planned':
                    issues.append(dict(scene_id=sid,beat_id=bid,field='requires',path=cursor['path']+f'.requires[{req_index}]',
                        error='A proposed future event is not an actual occurrence',requirement=copy.deepcopy(req),prior=copy.deepcopy(prior)))
                    continue
                if not prior or type(req.get('revision')) is not int or prior.get('revision',1)!=req['revision']:
                    own_effects=[copy.deepcopy(c) for c in beat['changes'] if c.get('id')==req['id']]
                    issues.append(dict(scene_id=sid,beat_id=bid,requirement_index=req_index,
                        path=cursor['path']+f'.requires[{req_index}]',field='requires',
                        error='Event precondition does not match canonical state',requirement=copy.deepcopy(req),prior=copy.deepcopy(prior),
                        candidate_records=matches,expected_reference_types=[public_type(m['type']) for m in matches],
                        available_reference_ids=available_reference_ids,
                        existing_intention_ids=['pending_intention:'+i for i in list(references.get('plans',{}))[:20]],
                        same_beat_effects=own_effects,
                        instruction=('This record is first introduced by this very beat, so it cannot also be a prerequisite. For a legitimate introduction preserve its statement and changes, use requires: [] or other genuinely existing prerequisites. Later beats can reference the newly established record. Do not fabricate earlier events to satisfy a circular dependency.' if not matches and own_effects else
                            'Select the provided reference_id. The program resolves its kind. Missing or ambiguous references and explicitly stale versions remain errors; do not invent earlier facts.')))
            planned_effects=[copy.deepcopy(c) for c in beat['changes'] if beat['mode']=='planned' or (c.get('type')=='fact' and c.get('kind')=='planned')]
            for effect in planned_effects:
                if not isinstance(effect,dict) or 'quote' in effect or effect.get('type') not in (*TYPE_GROUP,'transition'):
                    raise ContractError('Future effect proposals must be typed records without source quotes')
                _id(effect.get('id'))
            eid=f'c{chapter:04d}.{bid}'
            if eid in candidate['event_log']:raise ContractError('Canonical event already committed')
            candidate['event_log'][eid]=dict(id=eid,chapter=chapter,statement=statement,participants=copy.deepcopy(people),mode=beat['mode'])
            before=copy.deepcopy(candidate);updates=[]
            for change_index,change in enumerate(beat['changes']):
                if beat['mode']=='planned' or (change.get('type')=='fact' and change.get('kind')=='planned'):continue
                cursor.update(field='changes',change_index=change_index)
                if not isinstance(change,dict) or 'quote' in change:raise ContractError('Event effects cannot invent source quotes')
                update=copy.deepcopy(change);update['quote']=statement
                if update.get('type')=='learn':
                    # A learn effect can cite an earlier canonical event or the
                    # current beat. It cannot manufacture a fact/value.
                    if update.get('via_event') in seen:update['via_event']=f'c{chapter:04d}.'+update['via_event']
                if update.get('type')=='object':
                    for field in ('origin','event_id'):
                        reference=update.get(field)
                        if reference in seen and reference not in candidate['events']:
                            update[field]=f'c{chapter:04d}.'+reference
                if update.get('type')=='handoff' and 'signer_count' not in update:
                    update['signer_count']=len(update['signers'])
                updates.append(update)
            touched=set()
            for change_index,update in enumerate(updates):
                try:
                    if update.get('type')=='transition':
                        prior=candidate['facts'].get(update.get('fact_id'))
                        if not prior:
                            error=ContractError('transition.fact_id must identify an existing fact, not an object or missing record')
                            error.repair_details=dict(field='fact_id',expected_reference_types=['fact'],
                                reference_candidates=[dict(type=k,record=copy.deepcopy(candidate[g][update['fact_id']])) for k,g in REFERENCE_GROUP.items() if update['fact_id'] in candidate[g]],
                                instruction=RECORDS['transition']['reference_contract']['fact_id']['instruction'])
                            raise error
                        if 'expected_revision' not in update:update['expected_revision']=prior['revision']
                        elif type(update['expected_revision']) is int and update['expected_revision']==0 and update['fact_id'] not in state['facts']:update['expected_revision']=1
                        if 'from_value' not in update:update['from_value']=copy.deepcopy(prior['value'])
                    if beat['mode']=='reported':
                        belief=(update.get('type')=='fact' and update.get('kind')=='belief')
                        if update.get('type') in ('transition','learn'):
                            belief=candidate['facts'].get(update.get('fact_id'),{}).get('kind')=='belief'
                        if not belief:raise ContractError('An unverified report cannot establish objective world facts')
                    key=(update.get('type'),update.get('id'))
                    if key in touched:raise ContractError('Only one final effect per record in a beat')
                    touched.add(key)
                    prior_candidate=candidate
                    candidate=apply(candidate,[update],statement,chapter)
                    # Bind each effect before later effects (e.g. learning) read
                    # it, so they cannot cite an older event for a newer value.
                    for group in GROUPS:
                        for identifier,row in candidate[group].items():
                            if prior_candidate[group].get(identifier)!=row:
                                row['source_event']=eid;row['source_stage']='canonical_event'
                except ContractError as exc:
                    details=getattr(exc,'repair_details',{})
                    issues.append(dict(scene_id=sid,beat_id=bid,change_index=change_index,
                        path=f'scenes[{len(frozen)}].beats[{len(output["beats"])}].changes[{change_index}]',
                        record_id=update.get('id'),field=details.get('field'),error=str(exc),
                        proposed=update,prior=details.get('prior'),
                        cause_details=copy.deepcopy(details),
                        source_event=copy.deepcopy(details.get('source_event')),
                        learner=details.get('learner'),expected_participants=details.get('expected_participants'),reference_candidates=details.get('reference_candidates')))
            event_kind='task' if beat['mode']=='planned' else 'knowledge' if beat['mode']=='reported' else 'event'
            projection.append(dict(ref='event:'+eid,subject='event:'+eid,attribute='occurrence',kind=event_kind,
                status='planned' if event_kind=='task' else 'active',claim=statement,beat_id=bid))
            # A proposed action still declares an intention with its allocated
            # record ID. Its existence never means the action was performed.
            for planned in planned_effects:
                projection.append(dict(ref='plan:'+planned['id'],subject=planned.get('subject','event:'+eid),
                    attribute=attribute_identifier(planned.get('attribute','intention')),
                    kind='task',status='planned',claim=statement,beat_id=bid,proposed_record=copy.deepcopy(planned)))
            for row in projection:
                if row['beat_id']==bid and row['kind']=='task':
                    identifier=row.get('proposed_record',{}).get('id') or record_identifier('plan:'+eid)
                    plans[identifier]=plan_record(row,eid,None,plans.get(identifier))
            for group in GROUPS:
                for identifier,row in candidate[group].items():
                    if before[group].get(identifier)==row:continue
                    row['source_event']=eid
                    row['source_stage']='canonical_event'
                    if group=='facts':
                        subject=row['subject'];attribute=row['attribute'];kind='knowledge' if row['kind']=='belief' else 'state'
                    elif group=='knowledge':
                        subject=row['actor'];attribute='knows_'+digest(row['fact_id'])[:20];kind='knowledge'
                    else:
                        subject=group+':'+identifier;attribute='canonical_record'
                        kind='state' if group in ('objects','progress') else 'knowledge' if group=='identities' else 'event'
                    projection.append(dict(ref=group+':'+identifier,subject=subject,attribute=attribute,kind=kind,
                        claim=statement,beat_id=bid,canonical_record=copy.deepcopy(row)))
            output['beats'].append(dict(id=bid,event_id=eid,statement=statement,mode=beat['mode'],requires=copy.deepcopy(beat['requires']),changes=updates))
            if planned_effects:output['beats'][-1]['proposed_changes']=planned_effects
        frozen.append(output)
    if issues:raise EventPreflightError(issues)
    canonical_ids={b['id'] for s in frozen for b in s['beats']}
    for index,b in enumerate([b for s in frozen for b in s['beats']],1):
        token_id=f'slot_{index:03d}'
        while token_id in canonical_ids:token_id+='_' 
        b['token_id']=token_id
    body=dict(version=1,chapter=chapter,base_state_sha256=digest(canonical(state)),
        state_sha256=digest(canonical(candidate)),proposal_sha256=digest(canonical(original_proposal)),
        scenes=frozen,computed_times=computed,memory_projection=projection,identifier_normalizations=normalizations)
    if references:body['reference_catalogue_sha256']=digest(canonical(references))
    commit=dict(body,sha256=digest(canonical(body)))
    return dict(proposal=original_proposal,commit=commit,candidate_state=candidate)


def prepare(state,proposal,chapter,references=None):
    cursor=dict(chapter=chapter,path='scenes',field='scenes')
    try:return _prepare(state,proposal,chapter,cursor,references or {})
    except ContractError as exc:
        details=copy.deepcopy(getattr(exc,'repair_details',{}))
        details.setdefault('locator',copy.deepcopy(cursor))
        exc.repair_details=details
        raise


def verify(commit):
    if not isinstance(commit,dict) or commit.get('version')!=1 or commit.get('sha256')!=digest(canonical({k:v for k,v in commit.items() if k!='sha256'})):
        raise ContractError('Frozen event transaction integrity failure')
    if 'stage_transactions' in commit:
        from .stage_planning import verify_stage_chain
        verify_stage_chain(commit)
    return commit


def writer_view(prepared):
    c=verify(prepared['commit'])
    # The writer realizes statements, not the transaction executor's typed effects.
    # Keep every event/participant in order; the full hashed commit remains stored.
    scenes=[dict(id=s['id'],purpose=s['purpose'],participants=copy.deepcopy(s['participants']),
        beats=[dict(id=b.get('token_id',b['id']),canonical_id=b['id'],event_id=b['event_id'],
            statement=b['statement'],mode=b['mode']) for b in s['beats']]) for s in c['scenes']]
    return dict(sha256=c['sha256'],scenes=scenes,computed_times=copy.deepcopy(c['computed_times']),
                authority='Read-only event transaction; writer may request revision, never mutate it')


def compile_realization(raw,commit):
    """Bind exact literal anchors or token anchors, never infer paraphrases."""
    verify(commit)
    beats=[b for s in commit['scenes'] for b in s['beats']]
    aliases={b.get('token_id',b['id']):b['id'] for b in beats}
    tokens={b['id']:[] for b in beats};unknown=[]
    for match in TOKEN.finditer(raw):
        identifier=aliases.get(match[1],match[1])
        if identifier in tokens:tokens[identifier].append(match.span())
        else:unknown.append(match[1])
    spans=[];missing=[];duplicates=[];ambiguous=[]
    for b in beats:
        literal=[m.span() for m in re.finditer(re.escape(b['statement']),raw)]
        marked=tokens[b['id']]
        if marked:
            # A unique marker immediately annotating its unique exact statement
            # is one anchor representation, not two executed events. Consume
            # only the marker/statement pair and its intervening whitespace.
            pair=sorted(marked+literal)
            adjacent=(len(marked)==len(literal)==1 and pair[0][1]<=pair[1][0]
                and not raw[pair[0][1]:pair[1][0]].strip())
            if adjacent:spans.append((pair[0][0],pair[1][1],b))
            elif len(marked)!=1 or literal:duplicates.append(b.get('token_id',b['id']))
            else:spans.append((*marked[0],b))
        elif len(literal)==1:spans.append((*literal[0],b))
        elif not literal:missing.append(b.get('token_id',b['id']))
        else:ambiguous.append(b.get('token_id',b['id']))
    spans.sort(key=lambda r:r[0])
    wrong_order=[r[2]['id'] for r in spans]!=[b['id'] for b in beats]
    overlap=any(a[1]>b[0] for a,b in zip(spans,spans[1:]))
    if unknown or missing or duplicates or ambiguous or wrong_order or overlap:
        error=ContractError('Every frozen event must appear once, in planned order, as a token or exact complete statement')
        error.repair_details=dict(code='EVENT_REALIZATION_COVERAGE',missing_events=missing,duplicated_events=duplicates,
            ambiguous_literal_events=ambiguous,unknown_tokens=unknown,order_mismatch=wrong_order,overlapping_anchors=overlap,
            expected_order=[b.get('token_id',b['id']) for b in beats],
            instruction='Keep each frozen statement exactly once and in order, preferably using its event token. Exact complete statements may be compiled by the program; paraphrases are not matched. Fix only the listed coverage errors, preserving other prose.')
        raise error
    template=raw
    for start,end,b in reversed(spans):template=template[:start]+'[[event:'+b.get('token_id',b['id'])+']]'+template[end:]
    return template


def realize(raw,commit):
    template=compile_realization(raw,commit)
    beats=[b for s in commit['scenes'] for b in s['beats']]
    aliases={b.get('token_id',b['id']):b['id'] for b in beats}
    if unbound_claims(template):raise ContractError('Writer cannot invent calculated time amounts; use a frozen time token or request event revision')
    template=render_time(template,commit['computed_times'])
    catalog={b['id']:b['statement'] for b in beats}
    result=TOKEN.sub(lambda m:catalog[aliases.get(m[1],m[1])],template)
    if '[[event:' in result or '[[time:' in result:raise ContractError('Unknown or malformed event/time token')
    validate_literal_intervals(result,commit['computed_times'])
    return result


def project_memory(memory,chapters,number,trace):
    """Deterministic materialized view of committed events; no prose extraction."""
    chapter=chapters[number-1];commit=verify(chapter['event_commit'])
    if commit['chapter']!=number or digest(chapter['text'])!=chapter['sha256']:raise ContractError('Canonical chapter identity mismatch')
    from .prose_rendering import saved_text
    if chapter.get('realization_template') is None or saved_text(chapter)!=chapter['text']:
        raise ContractError('Prose no longer matches its frozen event realization')
    existing=memory.get('canonical_commits',{}).get(str(number))
    if existing:
        if existing!=commit['sha256']:raise ContractError('Canonical chapter already projected with another transaction')
        if chapter.get('prose_policy')=='unchecked':
            from .prose_memory import store_prose_excerpts
            return store_prose_excerpts(memory,chapters,number)
        return copy.deepcopy(memory)
    candidate=copy.deepcopy(memory);omitted=[]
    for index,row in enumerate(commit['memory_projection']):
        claim=row['claim'];start=chapter['text'].find(claim)
        if start<0:
            if chapter.get('prose_policy')!='unchecked':raise ContractError('Canonical memory source missing from saved prose')
            omitted.append(row['ref']);continue
        refs=[dict(chapter_number=number,evidence_id=s['id']) for s in evidence_segments(chapter['text'])
              if s['start']<start+len(claim) and s['end']>start]
        status=row.get('status','active')
        current=next((v for v in candidate['items'].values() if v['subject']==row['subject'] and v['attribute']==row['attribute'] and v['kind']==row['kind'] and v['status']==status),None)
        if current:
            op=dict(op='update',id=current['id'],expected_revision=current['revision'],reason='Projection of committed event '+row['beat_id'],claim=claim,status=status,source_refs=refs)
        else:
            op=dict(op='add',subject=row['subject'],attribute=row['attribute'],kind=row['kind'],claim=claim,status=status,source_refs=refs)
        candidate=apply_delta(candidate,dict(changes=[op]),chapters,f'canonical:{commit["sha256"]}:{index}')
        label=row.get('canonical_record',{}).get('attribute_label')
        if label is None:label=row.get('proposed_record',{}).get('attribute')
        if label is not None:candidate.setdefault('attribute_labels',{})[row['attribute']]=label
    if chapter.get('prose_policy')=='unchecked':
        from .prose_memory import store_prose_excerpts
        candidate=store_prose_excerpts(candidate,chapters,number)
    candidate['processed_through']=number
    candidate.setdefault('canonical_commits',{})[str(number)]=commit['sha256']
    if omitted:candidate.setdefault('projection_omissions',{})[str(number)]=omitted
    trace.append(dict(role='canonical_memory_projection',chapter=number,commit_sha256=commit['sha256'],
        records=len(commit['memory_projection'])-len(omitted),omitted_without_prose_source=omitted,status='PROJECTED',prose_inference=False))
    return candidate
