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


def unplanned_packet(state,number,instruction):
    proposal=dict(number=number,title=f'续写{number}',brief=instruction,future_updates=[])
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
        value=value.get('text')
        return value if isinstance(value,str) and value.strip() else None
    return None


def continue_prose(gateway,book,instruction,number,trace,prior_outputs=()):
    for raw in reversed(list(prior_outputs)):
        prose=prose_from_reply(raw)
        if prose:return prose
    # Bypass planner schemas and memory/context assembly. Saved prose is always
    # available even when structured projection or context selection failed.
    payload=dict(goal=book['goal'],constraints=book['constraints'],chapter_number=number,
        instruction=instruction,recent_chapters=[dict(number=c['number'],text=c['text'][-12000:]) for c in book['chapters'][-2:]],
        output_mode='plain_prose',context_policy='last_two_chapters_each_last_12000_characters')
    from .input_budget import fit
    payload=fit(payload,84000)
    for attempt in range(2):
        reply=gateway.complete(ModelRequest('writer',
            '继续创作本章完整小说正文。只返回正文，不要JSON、字段、解释或修订请求。依据总纲及已有正文续写，保留数值的近似程度，不猜测精确数值。',payload,16384))
        trace.append(dict(role='writer',mode='plain_prose',attempt=attempt+1,raw_output=reply.content,
            input_tokens=reply.input_tokens,output_tokens=reply.output_tokens,cost_usd=reply.cost_usd,finish_reason=reply.finish_reason))
        prose=prose_from_reply(reply.content)
        if prose:return prose
    raise ContractError('Writer returned no usable prose in plain-text continuation')
