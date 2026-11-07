"""Nonblocking model-output failures; never manufacture story text or facts."""
import copy
import json
import re

from inf_writer.domain import ContractError,canonical,digest
from inf_writer.models import ModelRequest


class PlanningOutputFailure(ContractError):
    pass


class ContextCapacityError(ContractError):
    pass


def unplanned_packet(state,number,instruction,title=None):
    from .chapter_titles import clean_title
    proposal=dict(number=number,title=clean_title(title) or f'第{number}章',brief=instruction,future_updates=[])
    body=dict(version=1,chapter=number,base_state_sha256=digest(canonical(state)),
        state_sha256=digest(canonical(state)),proposal_sha256=digest(canonical(proposal)),
        scenes=[],computed_times=[],memory_projection=[],identifier_normalizations=[],
        event_plan_status='unavailable')
    return dict(proposal=proposal,commit=dict(body,sha256=digest(canonical(body))),
        candidate_state=copy.deepcopy(state),revision_count=0,public_proposal=None)


def prose_from_reply(raw):
    if not isinstance(raw,str) or not raw.strip():return None
    raw=raw.strip()
    if raw.startswith('```'):
        raw=re.sub(r'^```[^\n]*\n','',raw)
        raw=re.sub(r'\n```\s*$','',raw).strip()
    try:value=json.loads(raw)
    except ValueError:
        # Recover an intact text value even if the outer object is malformed.
        match=re.search(r'"text"\s*:\s*',raw)
        if match:
            try:value,_=json.JSONDecoder().raw_decode(raw[match.end():])
            except ValueError:return None
            return value if isinstance(value,str) and value.strip() else None
        # Structured control/metadata is not chapter prose.
        return None if raw.startswith(('{','[')) else raw
    if isinstance(value,str):return value if value.strip() else None
    if isinstance(value,dict):
        value=value.get('new_stage_text',value.get('text'))
        return value if isinstance(value,str) and value.strip() else None
    return None


def continue_prose(gateway,book,instruction,number,trace,prior_outputs=(),*,stage_task=None,previous_tail='',save_progress=None):
    # These are complete replies for the same unit, not saved earlier units.
    # A format-only retry may incorrectly continue the first draft; never let
    # that later text silently replace an already recoverable complete unit.
    for raw in prior_outputs:
        prose=prose_from_reply(raw)
        if prose:return prose
    # Bypass planner schemas and memory/context assembly. Saved prose is always
    # available even when structured projection or context selection failed.
    payload=dict(goal=book['goal'],constraints=book['constraints'],chapter_number=number,
        instruction=instruction,recent_chapters=[dict(number=c['number'],text=c['text'][-12000:]) for c in book['chapters'][-2:]],
        output_mode='plain_prose',context_policy='last_two_chapters_each_last_12000_characters')
    from .narrative_planning import context as narrative_context
    payload['narrative_continuity']=narrative_context(book,number)
    from .narrative_planning import handoff as chapter_handoff,advance_writer_context
    payload['chapter_handoff']=chapter_handoff(book)
    payload['narrative_plan']=copy.deepcopy(book.get('prepared_events',{}).get(str(number),{}).get('narrative_plan',{}))
    if book.get('memory',{}).get('items'):
        try:
            from inf_writer.tiered_memory import select_context
            selection=select_context(book['memory'],query=instruction,max_bytes=22000)
            payload['organized_memory']=[r for r in selection['items']if r['kind']!='prose_excerpt']
            payload['memory_meaning_policy']='按meaning的视角、证实程度、有效状态和任务进度读取；recent_chapters是原文证据，不整体当成当前事实。'
        except ContractError:
            payload['memory_meaning_policy']='组织化记忆视图暂不可用；近期正文为未整理证据，谨慎区分人物说法、计划和已发生事实。'
    if stage_task is not None:
        payload['stage_task']=copy.deepcopy(stage_task)
        payload['previous_prose_tail']=dict(text=previous_tail,read_only=True)
    prepared=book.get('prepared_events',{}).get(str(number),{})
    earlier='\n\n'.join(r['text'] for r in prepared.get('stage_realizations',[])) or previous_tail
    advance_writer_context(payload,book,number,earlier)
    from .input_budget import fit
    payload=fit(payload,84000)
    unit=stage_task.get('unit_number') if stage_task else 'chapter'
    fragment_key=f'{number}:{unit}'
    fragments=book.setdefault('prose_fragments',{})
    saved=fragments.get(fragment_key,{})
    prefix=saved.get('text','')
    if prefix and digest(prefix)!=saved.get('sha256'):
        raise ContractError('Saved prose fragment integrity failure')
    for attempt in range(2):
        if prefix:
            advance_writer_context(payload,book,number,(earlier+'\n\n' if earlier else '')+prefix)
            payload['incomplete_prose_tail']=prefix[-12000:]
            payload['continuation_instruction']='只补完已有文本的未完成末段，然后结束当前写作单元。不要重复已有文字，不重开场景，不扩展新情节。'
            payload=fit(payload,84000)
        system=('仅写stage_task当前单元的新增正文，不复制previous_prose_tail，不重开整章。只返回正文，不要JSON或解释。'
                if stage_task is not None else
                '继续创作本章完整小说正文。只返回正文，不要JSON、字段、解释或修订请求。依据总纲及已有正文续写，保留数值的近似程度，不猜测精确数值。')
        system+='遵守场景连续性和叙事规划，不能重置已经进行的会谈、动作和时间口径，不靠重复动作填字。'
        reply=gateway.complete(ModelRequest('writer',system,payload,32768 if prefix else 16384))
        trace.append(dict(role='writer',mode='plain_prose',attempt=attempt+1,raw_output=reply.content,
            input_tokens=reply.input_tokens,output_tokens=reply.output_tokens,cost_usd=reply.cost_usd,finish_reason=reply.finish_reason))
        prose=prose_from_reply(reply.content)
        if prose and reply.finish_reason in ('stop',None):
            fragments.pop(fragment_key,None)
            return prefix+prose
        if prose and reply.finish_reason=='length':
            prefix+=prose
            fragments[fragment_key]=dict(text=prefix,sha256=digest(prefix),status='PENDING',chapter=number,unit=unit)
            if save_progress is not None:save_progress()
            continue
    if prefix:
        boundary=max(prefix.rfind(mark)+len(mark) for mark in ('。','！','？','\n\n') if mark in prefix) if any(mark in prefix for mark in ('。','！','？','\n\n')) else len(prefix)
        fragments[fragment_key]['status']='DEFERRED'
        book.setdefault('prose_output_warnings',[]).append(dict(chapter=number,unit=unit,
            reason='OUTPUT_LIMIT_AFTER_BOUNDED_CONTINUATION',raw_fragment_sha256=digest(prefix)))
        return prefix[:boundary]
    raise ContractError('Writer returned no usable prose in plain-text continuation')
