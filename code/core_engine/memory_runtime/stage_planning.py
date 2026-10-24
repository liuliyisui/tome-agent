"""Independent event-scene transactions with explicit dependency failures."""
import copy
import re
from inf_writer.domain import ContractError,canonical,digest
from .event_first import prepare,normalize_plan,verify
from .event_references import plan_record
from .identifiers import record_identifier


def prepare_stages(state,proposal,chapter,references,deferred=None):
    normalized,_=normalize_plan(proposal,state,chapter,references=references)
    current=copy.deepcopy(state);refs=copy.deepcopy(references);packets=[];reports=copy.deepcopy(deferred or [])
    for index,scene in enumerate(normalized['scenes']):
        if re.fullmatch(r's\d{4}',scene['id']):index=int(scene['id'][1:])-1
        part=dict(number=chapter,title=proposal['title'],brief=proposal['brief'],future_updates=[],
            time_calculations=copy.deepcopy(proposal.get('time_calculations',[])),scenes=[copy.deepcopy(scene)])
        try:packet=prepare(current,part,chapter,references=refs)
        except ContractError as exc:
            reports.append(dict(stage=index,status='DEFERRED',scene_id=scene['id'],
                error=str(exc),details=copy.deepcopy(getattr(exc,'repair_details',{})),
                proposed_scene=copy.deepcopy(scene)))
            continue
        current=packet['candidate_state'];packet['stage']=index;packets.append(packet)
        reports.append(dict(stage=index,status='PREPARED',scene_id=scene['id'],commit_sha256=packet['commit']['sha256']))
        events={b['id']:b['event_id'] for s in packet['commit']['scenes'] for b in s['beats']}
        for row in packet['commit']['memory_projection']:
            if row['kind']=='task' and row.get('status')=='planned':
                eid=events[row['beat_id']];identifier=row.get('proposed_record',{}).get('id') or record_identifier('plan:'+eid)
                refs.setdefault('plans',{})[identifier]=plan_record(row,eid,None,refs.get('plans',{}).get(identifier))
    scenes=[];projection=[]
    for packet in packets:
        scenes.extend(copy.deepcopy(packet['commit']['scenes']));projection.extend(copy.deepcopy(packet['commit']['memory_projection']))
    for i,beat in enumerate([b for s in scenes for b in s['beats']],1):beat['token_id']=f'slot_{i:03d}'
    from .time_calculation import calculate
    reports.sort(key=lambda r:r['stage'])
    body=dict(version=1,chapter=chapter,base_state_sha256=digest(canonical(state)),state_sha256=digest(canonical(current)),
        proposal_sha256=digest(canonical(proposal)),scenes=scenes,computed_times=calculate(proposal.get('time_calculations',[])),
        memory_projection=projection,identifier_normalizations=[],stage_transactions=[p['commit'] for p in packets],stage_reports=reports,
        event_plan_status='partial' if any(r['status']=='DEFERRED' for r in reports) else 'prepared')
    if not packets:body['event_plan_status']='unavailable'
    return dict(proposal=copy.deepcopy(proposal),candidate_state=current,commit=dict(body,sha256=digest(canonical(body))),
        stage_packets=packets,stage_reports=reports,stage_realizations=[])


def verify_stage_chain(commit):
    expected=commit['base_state_sha256'];scenes=[];projection=[]
    for part in commit.get('stage_transactions',[]):
        verify(part)
        if part['chapter']!=commit['chapter'] or part['base_state_sha256']!=expected:raise ContractError('Stage transaction chain gap')
        expected=part['state_sha256'];scenes.extend(copy.deepcopy(part['scenes']));projection.extend(part['memory_projection'])
    if expected!=commit['state_sha256']:raise ContractError('Stage transaction final state mismatch')
    for scene in scenes:
        for beat in scene['beats']:beat.pop('token_id',None)
    outer=copy.deepcopy(commit['scenes'])
    for scene in outer:
        for beat in scene['beats']:beat.pop('token_id',None)
    if scenes!=outer or projection!=commit['memory_projection']:raise ContractError('Stage transaction projection mismatch')
