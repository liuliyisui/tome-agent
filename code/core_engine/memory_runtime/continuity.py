"""Typed writing-state invariants, separate from editorial review and memory tiers.

The writer declares relevant facts with literal prose evidence. This validates
declared relationships; it cannot certify completeness or infer arbitrary prose.
"""
import calendar
import copy
from datetime import date
import re

from inf_writer.domain import ContractError, canonical, digest, fields, text, strict_json
from inf_writer.models import ModelRequest
from .identifiers import attribute_identifier
from .event_contract import RECORDS,STATE_KINDS,validate_record
from .event_references import record_matches


CONTRACT = dict(version=1, instruction=(
    '随正文输出continuity_updates数组；没有相关新增或变化时给空数组和no_continuity_change_reason。'
    '这不是另一篇摘要，只记录本章出现的关键日期、物证状态、签收角色、核对进度。'
    '已有对象沿用writing_state中的稳定id；每项quote必须逐字来自本章正文（可含时间工具占位符）。'
    '每项type/id/quote，按依赖顺序提交。event另含date(YYYY、YYYY-MM或YYYY-MM-DD)、'
    'mode(present/historical)、objects(涉及的已登记物证id数组)、after(明确晚于的事件id数组)。'
    '当前行动用present，追述或引述历史事件用historical，不能把历史文字当当前日期。'
    'object另含label/form(original/photo/film/index/copy)/status(missing/available)、'
    'origin(形成事件id或null)，可选source(照片等对应的原件id)、event_id(找回/归还事件)。'
    '目录号、附件原件、胶片和照片分开id；照片可留存于原件失踪后，但须单独登记来源，不能直接观察缺失原件。'
    'observe另含object_id/method(direct/photo/film/index)/source_id(直接观察为null，否则对应的载体id)。'
    'handoff另含signers、non_signers、attendees三个人物标识数组和signer_count；'
    '未知签字者用稳定unknown_标识保留，不把未签字的跟车人补成签字者。'
    '后来查明未知者姓名时，用identify记录(unknown_id/person_id/quote)绑定同一人，再更新签收记录，不把新获知当改写历史。'
    'progress另含pass_id/completed/total，同一任务同一轮次进度只能前进；'
    '第二轮或初筛转细核需新pass_id及restart_quote逐字说明这次复查。'
    '只记录正文支持的事实，不把计划写成完成，不用换id、漏字段或删除正确内容绕过检查。'
))
FORMS = set(RECORDS['object']['enums']['form'])


class ContinuityError(ContractError):
    def __init__(self, message, row, prior=None):
        super().__init__(message)
        self.repair_details = dict(code='WRITING_CONTINUITY_CONFLICT', proposed=row,
                                   prior=prior, instruction='只修本章相关段落及结构化记录；不改既有事实，不删除无关正确内容。')


def empty():
    return dict(version=1, events={}, objects={}, observations={}, handoffs={}, identities={}, progress={},
                facts={},knowledge={},event_log={},present_cursor=None)


def _range(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}(?:-\d{2}(?:-\d{2})?)?', value):
        raise ContractError('Story date must be YYYY, YYYY-MM or YYYY-MM-DD')
    parts = [int(s) for s in value.split('-')]
    try:
        y = parts[0]
        if len(parts) == 1:return date(y,1,1),date(y,12,31)
        m = parts[1]
        if len(parts) == 2:return date(y,m,1),date(y,m,calendar.monthrange(y,m)[1])
        return date(y,m,parts[2]),date(y,m,parts[2])
    except (ValueError,calendar.IllegalMonthError):
        raise ContractError('Invalid story calendar date') from None


def _date_in_quote(value, quote):
    # No guessing exact days from a month-only source or guessing the century.
    parts=value.split('-')
    if value in quote:return True
    pattern=parts[0]+'年'
    if len(parts)>1:pattern+=str(int(parts[1]))+'月'
    if len(parts)>2:pattern+=str(int(parts[2]))+'日'
    return pattern in quote


def _people(values):
    if not isinstance(values,list) or any(not isinstance(v,str) or not v.strip() for v in values) or len(set(values))!=len(values):
        raise ContractError('People must be distinct nonempty stable identifiers')
    return set(values)


def apply(state, updates, prose, chapter, no_change_reason=None):
    if not isinstance(updates,list) or len(updates)>24:
        raise ContractError('continuity_updates must be a list of at most 24 records per chapter')
    if not updates:
        text(no_change_reason,'Empty continuity update needs an explicit reason')
    result=copy.deepcopy(state)
    seen=set()
    for row in updates:
        validate_record(row,canonical_record=True)
        fields(row,('type','id','quote'),tuple(k for k in row if k not in ('type','id','quote')))
        identifier=text(row['id'],'Continuity id')
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,63}',identifier):
            raise ContractError('Use stable English identifiers for writing state')
        if (row['type'],identifier) in seen:raise ContractError('Only one final update per writing-state identity in a chapter')
        seen.add((row['type'],identifier))
        if text(row['quote'],'Continuity quote') not in prose:
            raise ContinuityError('Continuity evidence is absent from the final prose',row)
        kind=row['type'];record=copy.deepcopy(row)
        record.update(chapter=chapter,source_sha256=digest(prose))
        groups=dict(event='events',object='objects',observe='observations',handoff='handoffs',identify='identities',progress='progress',fact='facts',learn='knowledge')
        if kind in groups:
            previous=result[groups[kind]].get(identifier)
            record['revision']=(previous or {}).get('revision',0)+1
        def fail(message,prior=None):raise ContinuityError(message,row,prior)
        if kind=='fact':
            from inf_writer.domain import identity
            label=row['attribute']
            row=copy.deepcopy(row);row['attribute']=attribute_identifier(label)
            try:identity(row['subject'],row['attribute'])
            except ContractError as exc:
                error=ContinuityError(str(exc),row)
                error.repair_details.update(field='attribute',submitted_label=label)
                raise error from exc
            record['attribute']=row['attribute']
            prior=result['facts'].get(identifier)
            record['attribute_label']=(prior or {}).get('attribute_label',label)
            canonical(row['value'])
            if row['kind'] not in STATE_KINDS:fail('Fact kind must distinguish mutable state, immutable fact and belief')
            for fid,prior in result['facts'].items():
                if (prior['subject'],prior['attribute'])==(row['subject'],row['attribute']) and fid!=identifier:
                    fail('Fact identity already exists; reuse its ID and an explicit transition',prior)
            previous=result['facts'].get(identifier)
            if previous:
                if any(previous[k]!=row[k] for k in ('subject','attribute','value','kind')):
                    fail('Established facts require explicit transitions, not re-establishment',previous)
            else:result['facts'][identifier]=record
        elif kind=='transition':
            prior=result['facts'].get(row['fact_id'])
            if not prior:fail('Transition requires an established fact')
            if prior['kind']=='immutable':fail('An immutable fact cannot be changed by a state transition',prior)
            if type(row['expected_revision']) is not int or row['expected_revision']!=prior['revision'] or canonical(row['from_value'])!=canonical(prior['value']):
                fail('Transition precondition does not match the current state',prior)
            canonical(row['to_value'])
            changed=copy.deepcopy(prior)
            changed.update(value=copy.deepcopy(row['to_value']),revision=prior['revision']+1,
                quote=row['quote'],chapter=chapter,source_sha256=digest(prose))
            result['facts'][row['fact_id']]=changed
        elif kind=='learn':
            matches=record_matches(result,row['fact_id'],row.get('reference_type'))
            reference_type,prior=matches[0] if len(matches)==1 else (None,None)
            source=result['event_log'].get(row['via_event'])
            if not prior or not source or row['actor'] not in source['participants']:
                error=ContinuityError('Learning requires a unique existing record and an event in which the learner participates',row,prior)
                error.repair_details.update(field='via_event',source_event=copy.deepcopy(source),learner=row['actor'],
                    expected_participants=copy.deepcopy((source or {}).get('participants',[])),
                    reference_candidates=[dict(type=k,id=v['id'],revision=v.get('revision',1)) for k,v in record_matches(result,row['fact_id'])])
                raise error
            epistemic=prior.get('epistemic_status',prior.get('kind','record:'+reference_type))
            if source['mode']=='planned' or prior.get('mode')=='planned' or (source['mode']=='reported' and epistemic!='belief'):
                fail('A future plan or unverified report cannot establish knowledge of objective truth',source)
            formation=prior.get('source_event')
            order={eid:index for index,eid in enumerate(result['event_log'])}
            if formation in order and order[row['via_event']]<order[formation]:
                fail('A source event cannot convey a record revision created after it',prior)
            if prior.get('chapter',0)>source.get('chapter',0):fail('A source event predates the referenced record revision',prior)
            value=prior.get('value') if 'value' in prior else {k:copy.deepcopy(v) for k,v in prior.items() if k not in ('quote','source_sha256','source_event','source_stage','chapter','revision')}
            record.update(fact_revision=prior.get('revision',1),value=copy.deepcopy(value),reference_type=reference_type,
                epistemic_status=epistemic)
            result['knowledge'][identifier]=record
        elif kind=='event':
            lower,upper=_range(row['date'])
            if row['mode'] not in ('present','historical'):fail('Event mode must distinguish current action from history')
            if not _date_in_quote(row['date'],row['quote']):fail('Date precision/value must occur in the bound source quote')
            if not isinstance(row['objects'],list) or not isinstance(row['after'],list):fail('Event objects and after must be lists')
            previous=result['events'].get(identifier)
            if previous and any(previous[k]!=row[k] for k in ('date','objects','after')):
                fail('An established event date or identity cannot be silently rewritten',previous)
            for eid in row['after']:
                prior=result['events'].get(eid)
                if prior is None or eid==identifier:fail('Unknown or self-referential earlier event')
                if upper<_range(prior['date'])[0]:fail('Event occurs before its required preceding event',prior)
            for oid in row['objects']:
                obj=result['objects'].get(oid)
                if obj is None:fail('Referenced object must be registered before the event')
                origin=result['events'].get(obj['origin']) if obj['origin'] else None
                if origin and upper<_range(origin['date'])[0]:fail('Evidence event predates the origin of this object',origin)
            cursor=result['present_cursor']
            if row['mode']=='present':
                if cursor and upper<_range(cursor['date'])[0]:fail('Current investigation date moved backwards without a historical frame',cursor)
                if not cursor or lower>_range(cursor['date'])[0]:result['present_cursor']=dict(id=identifier,date=row['date'])
            result['events'][identifier]=record
        elif kind=='object':
            if row['form'] not in FORMS or row['status'] not in ('missing','available'):fail('Invalid object form or existence state')
            label=text(row['label'],'Object label')
            for oid,other in result['objects'].items():
                if oid!=identifier and other['label'].casefold()==label.casefold() and other['form']==row['form']:
                    fail('Same object label/form already has a stable identity',other)
            def real_event(reference):
                if reference in result['events']:return True
                return result['event_log'].get(reference,{}).get('mode')=='actual'
            if row['origin'] is not None and not real_event(row['origin']):fail('Unknown object origin event')
            source=row.get('source')
            if source is not None and source not in result['objects']:fail('Unknown source object')
            if source==identifier:fail('An object cannot be its own source')
            previous=result['objects'].get(identifier)
            if previous:
                if any(previous[k]!=row[k] for k in ('label','form','origin')) or previous.get('source')!=source:
                    fail('An object identity/form/origin cannot silently change',previous)
                if previous['status']!=row['status'] and not real_event(row.get('event_id')):
                    fail('Object availability change requires a separately evidenced event',previous)
            result['objects'][identifier]=record
        elif kind=='observe':
            obj=result['objects'].get(row['object_id'])
            if obj is None:fail('Cannot observe an unregistered object')
            method=row['method']
            if method=='direct':
                if row['source_id'] is not None or obj['status']!='available':fail('A missing original cannot be directly observed',obj)
            elif method in ('photo','film','index'):
                carrier=result['objects'].get(row['source_id'])
                if not carrier or carrier['status']!='available' or carrier['form']!=method or carrier.get('source')!=row['object_id']:
                    fail('Indirect observation requires a distinct available carrier with bound provenance',carrier)
            else:fail('Unknown observation method')
            result['observations'][identifier]=record
        elif kind=='handoff':
            signers=_people(row['signers']);non=_people(row['non_signers']);_people(row['attendees'])
            aliases={r['unknown_id']:r['person_id'] for r in result['identities'].values()}
            resolve=lambda values:{aliases.get(p,p) for p in values}
            if resolve(signers)&resolve(non) or len(resolve(signers))!=len(signers):fail('One person cannot both sign and not sign the same handoff record')
            if type(row['signer_count']) is not int or row['signer_count']!=len(signers):fail('Signing count must include the actual signers, with explicit unknown identities if needed')
            previous=result['handoffs'].get(identifier)
            if previous and (resolve(previous['signers'])!=resolve(signers) or resolve(previous['non_signers'])!=resolve(non)):
                fail('Signing roles in the same record cannot silently change; record identity clarification separately',previous)
            result['handoffs'][identifier]=record
        elif kind=='identify':
            unknown=text(row['unknown_id'],'Unknown signer identity');person=text(row['person_id'],'Resolved person identity')
            if not unknown.startswith('unknown_') or person.startswith('unknown_'):fail('Identity resolution must map one explicit unknown to a known person')
            for prior in result['identities'].values():
                if prior['unknown_id']==unknown and prior['person_id']!=person:fail('Established identity resolution cannot silently change',prior)
            for handoff in result['handoffs'].values():
                signed={person if p==unknown else p for p in handoff['signers']}
                non={person if p==unknown else p for p in handoff['non_signers']}
                if signed&non or len(signed)!=len(handoff['signers']):fail('Identity resolution contradicts existing signing roles',handoff)
            result['identities'][identifier]=record
        elif kind=='progress':
            text(row['pass_id'],'Comparison pass id')
            if type(row['completed']) is not int or type(row['total']) is not int or not 0<=row['completed']<=row['total']:
                fail('Invalid comparison progress')
            previous=result['progress'].get(identifier)
            if previous:
                if row['pass_id']==previous['pass_id']:
                    if row['total']!=previous['total'] or row['completed']<previous['completed']:
                        fail('Same-pass comparison progress cannot silently go backwards',previous)
                else:
                    why=row.get('restart_quote','')
                    if not isinstance(why,str) or not why.strip() or why not in prose:
                        fail('A new pass requires an explicit prose explanation of the repeat/checking stage',previous)
            result['progress'][identifier]=record
        else:fail('Unknown writing-state record type')
    return result


def context_view(state,query,max_bytes=14000,plans=None):
    """Compact relevant state; full persistent state still validates every update."""
    result=dict(version=1,present_cursor=copy.deepcopy(state['present_cursor']),records=[],omitted_count=0,
                scope='Selected typed writing constraints; not a fourth memory bank or complete semantic certification')
    candidates=[]
    for row in (plans or {}).values():
        compact={k:copy.deepcopy(v) for k,v in row.items() if k not in ('quote','source_sha256')}
        compact['type']='plan'
        candidates.append((len(row['id']) if row['id'] in query else 0,row.get('chapter',0),compact))
    for group in ('objects','handoffs','identities','progress','events','facts','knowledge'):
        for row in state[group].values():
            compact={k:copy.deepcopy(v) for k,v in row.items() if k not in ('quote','source_sha256')}
            labels=[row['id'],row.get('label','')]
            score=sum(len(v) for v in labels if v and v in query)
            candidates.append((score,row['chapter'],compact))
    for _,_,row in sorted(candidates,key=lambda x:(x[0],x[1]),reverse=True):
        result['records'].append(row)
        if len(canonical(result).encode('utf-8'))>max_bytes:
            result['records'].pop();result['omitted_count']+=1
    return result


def guard(state,updates,reason,prose,chapter,calculations,gateway,trace):
    """One writer patch on a detected invariant violation, never editorial review."""
    from collections import Counter
    from .time_calculation import render,unbound_claims,validate_literal_intervals
    entry=dict(role='writer_continuity',proposed_updates=copy.deepcopy(updates),status='CHECKING')
    trace.append(entry)
    try:
        candidate=apply(state,updates,prose,chapter,reason)
        entry.update(status='VALIDATED_DECLARATIONS',patch_count=0)
        return prose,candidate
    except ContractError as exc:
        entry['initial_error']=str(exc)
        details=getattr(exc,'repair_details',{})
    quote=details.get('proposed',{}).get('quote','')
    allowed=[]
    for index,match in enumerate(re.finditer(r'[^\n]+',prose),1):
        if quote and quote in match[0]:
            allowed.append(dict(id=f'p{index}',start=match.start(),end=match.end(),text=match[0]))
    payload=dict(writing_continuity_repair=True,current_draft=prose,continuity_updates=updates,
        conflict=details,allowed_paragraphs=allowed,computed_times=calculations,
        continuity_contract=CONTRACT)
    request_trace=dict(role='writer_continuity_patch',status='REQUESTED')
    trace.append(request_trace)
    try:
        if len(canonical(payload).encode('utf-8'))>100000:raise ContractError('Continuity patch input exceeds explicit budget')
        response=gateway.complete(ModelRequest('writer',
            '只修写作阶段检出的事实约束冲突。输出JSON：replacements数组(每项paragraph_id/replacement)、'
            'continuity_updates完整数组、可选no_continuity_change_reason。只能替换allowed_paragraphs中的段落，'
            '其他正文由程序逐字保留。已有记录的type/id必须全部保留，可补充有正文依据的新记录。'
            '不能修改旧章或编造已查明结论，不能靠删掉记录、换id或伪造引文通过；'
            '若只是结构化标记错误，可不改正文。新的计算仍须用computed_times中已有占位符。'
            '无法修正时输出unresolved原因，不猜关键前提。',payload,8192))
        request_trace['raw_output']=response.content
        result=strict_json(response.content)
        fields(result,('replacements','continuity_updates'),('no_continuity_change_reason',))
        if not isinstance(result['continuity_updates'],list):raise ContractError('Replacement continuity records must be a list')
        original_ids={(r['type'],r['id']) for r in updates}
        new_ids={(r['type'],r['id']) for r in result['continuity_updates']}
        if not original_ids<=new_ids:raise ContractError('Continuity repair deleted or renamed protected records')
        proposed_by_id={(r['type'],r['id']):r for r in updates}
        for row in result['continuity_updates']:
            old=proposed_by_id.get((row['type'],row['id']))
            if old and row['type']=='event' and row.get('mode')!=old.get('mode'):
                if not re.search(r'回忆|当年|此前|曾经|旧记录|追述|回看|那年',row.get('quote','')):
                    raise ContractError('Changing current action into history requires an explicit historical frame in prose')
        if not isinstance(result['replacements'],list):raise ContractError('Prose replacements must be a list')
        known={p['id']:p for p in allowed};patches=[];seen=set()
        for patch in result['replacements']:
            fields(patch,('paragraph_id','replacement'))
            pid=patch['paragraph_id']
            if not isinstance(pid,str) or pid not in known or pid in seen:raise ContractError('Unknown, duplicate or protected prose paragraph')
            replacement=text(patch['replacement'],'Replacement paragraph')
            if '\n' in replacement or '\r' in replacement:raise ContractError('Local repair must remain one paragraph')
            # Existing rendered arithmetic may remain; newly invented literal
            # computed amounts must instead use a bound program token.
            old=Counter(r['quote'] for r in unbound_claims(known[pid]['text']))
            new=Counter(r['quote'] for r in unbound_claims(replacement))
            if any(n>old[q] for q,n in new.items()):raise ContractError('Local prose repair introduced unbound time arithmetic')
            patches.append((known[pid],replacement));seen.add(pid)
        revised=prose
        for original,replacement in sorted(patches,key=lambda x:x[0]['start'],reverse=True):
            revised=revised[:original['start']]+replacement+revised[original['end']:]
        revised=render(revised,calculations)
        validate_literal_intervals(revised,calculations)
        records=copy.deepcopy(result['continuity_updates'])
        for row in records:
            for key in ('quote','restart_quote'):
                if key in row:row[key]=render(row[key],calculations)
        candidate=apply(state,records,revised,chapter,result.get('no_continuity_change_reason',reason))
        request_trace.update(status='APPLIED',patch_count=len(patches))
        entry.update(status='VALIDATED_DECLARATIONS',patch_count=len(patches),final_updates=records,final_draft=revised)
        return revised,candidate
    except Exception as exc:
        entry['status']='UNRESOLVED'
        request_trace.update(status='UNRESOLVED',error=str(exc) if isinstance(exc,ContractError) else type(exc).__name__)
        raise
