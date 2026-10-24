"""Exact links from derived memory views back to committed event records.

This is a disposable index, reconstructed from committed chapters. It is not
another truth store, and an intention reference never means future completion.
"""
import copy
from inf_writer.domain import ContractError
from .identifiers import record_identifier
from .interface_contract import RECORD_NAMES,public_kind,stored_kind,public_field,public_enum,ACTION_SCOPES

REFERENCE_GROUPS=dict(fact='facts',object='objects',observe='observations',handoff='handoffs',identify='identities',progress='progress',event='events',learn='knowledge',occurrence='event_log')
PUBLIC_REFERENCE_NAMES=RECORD_NAMES
INTERNAL_REFERENCE_NAMES={v:k for k,v in PUBLIC_REFERENCE_NAMES.items()}


def public_type(kind):return public_kind(kind)
def internal_type(kind):return stored_kind(kind)
def reference_id(kind,identifier):return public_type(kind)+':'+identifier


def parse_reference(value):
    if not isinstance(value,str) or ':' not in value:return None
    name,identifier=value.split(':',1)
    if name not in (*REFERENCE_GROUPS,'plan',*INTERNAL_REFERENCE_NAMES):return None
    if not identifier:raise ContractError('Reference identifier is empty')
    return internal_type(name),identifier


def action_aliases(state,plan,chapter):
    """Only directory-backed spellings can resolve to a chapter action."""
    aliases={key:{key} for key in state.get('event_log',{})}
    if chapter is None:return aliases
    for scene in plan.get('scenes',[]) if isinstance(plan.get('scenes'),list) else []:
        if not isinstance(scene,dict):continue
        sid=scene.get('id')
        for beat in scene.get('beats',[]) if isinstance(scene.get('beats'),list) else []:
            if not isinstance(beat,dict):continue
            bid=beat.get('id')
            if not isinstance(bid,str) or not bid.strip():continue
            stored=record_identifier(bid);full=f'c{chapter:04d}.{stored}'
            names={bid,stored,full}
            if isinstance(sid,str) and sid.strip():
                for scene_name in (sid,record_identifier(sid)):
                    for beat_name in (bid,stored):
                        names.update((scene_name+'.'+beat_name,f'c{chapter:04d}.'+scene_name+'.'+beat_name))
            for name in names:aliases.setdefault(name,set()).add(full)
    return aliases


def public_state_view(view):
    result=copy.deepcopy(view)
    for row in result.get('records',[]):
        kind=row.pop('type');identifier=row.pop('id')
        for field in list(row):
            target=public_field(kind,field)
            value=row.pop(field);row[target]=public_enum(kind,field,value) if isinstance(value,str) else value
        row.update(record_kind=public_type(kind),record_id=identifier,reference_id=reference_id(kind,identifier))
    return result


def record_matches(state,identifier,reference_type=None):
    return [(kind,state[group][identifier]) for kind,group in REFERENCE_GROUPS.items()
        if (reference_type is None or reference_type==kind) and identifier in state[group]]


def plan_record(row,event_id,source_commit,previous=None):
    proposed=row.get('proposed_record',{})
    identifier=proposed.get('id') or record_identifier('plan:'+event_id)
    return dict(id=identifier,revision=(previous or {}).get('revision',0)+1,
        subject=row['subject'],attribute=row['attribute'],value=copy.deepcopy(proposed.get('value',row['claim'])),
        kind='planned',status='planned',scope='intention_only',source_event=event_id,source_commit=source_commit)


def catalogue(book):
    result=dict(memory={},plans={});rows=[]
    for chapter in book['chapters']:
        commit=chapter.get('event_commit')
        if not commit:continue
        events={b['id']:b['event_id'] for s in commit['scenes'] for b in s['beats']}
        for row in commit['memory_projection']:
            if row['kind']=='task' and row.get('status')=='planned':
                event_id=events[row['beat_id']]
                identifier=row.get('proposed_record',{}).get('id') or record_identifier('plan:'+event_id)
                record=plan_record(row,event_id,commit['sha256'],result['plans'].get(identifier))
                result['plans'][record['id']]=record
                ref=dict(type='plan',id=record['id'],revision=record['revision'],scope='intention_only')
            elif 'canonical_record' in row:
                record=row['canonical_record'];ref=dict(type=record['type'],id=record['id'],revision=record['revision'],scope=record.get('kind','record'))
            else:
                ref=dict(type='occurrence',id=events[row['beat_id']],revision=1,scope='event_occurrence')
            rows.append((chapter['number'],row,dict(ref,source_commit=commit['sha256'])))
    for mid,item in book['memory']['items'].items():
        source_chapters={s['chapter_number'] for s in item['sources']}
        for number,row,ref in reversed(rows):
            if (number in source_chapters and item['claim']==row['claim'] and
                (item['subject'],item['attribute'],item['kind'],item['status'])==
                (row['subject'],row['attribute'],row['kind'],row.get('status','active'))):
                result['memory'][mid]=dict(ref,memory_revision=item['revision'])
                break
    return result
