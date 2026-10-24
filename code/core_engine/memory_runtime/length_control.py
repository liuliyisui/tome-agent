"""One nonblocking length adjustment, independent of transport token ceilings."""
import math
import re
from inf_writer.domain import ContractError
from inf_writer.models import ModelRequest
from .completion import prose_from_reply
from .input_budget import size


def han_count(value):return len(re.findall(r'[\u3400-\u9fff]',value))


def adjust(draft,target,book,number,gateway,trace):
    actual=han_count(draft);report=dict(target=target,before=actual,after=actual,adjustment='not_needed')
    if max(1,math.floor(target*.9))<=actual<=math.ceil(target*1.1):return draft,report
    payload=dict(output_mode='plain_prose',chapter_number=number,goal=book['goal'],constraints=book['constraints'],
        current_draft=draft,target_han_chars=target,current_han_chars=actual,
        instruction=f'将本章调整到约{target}汉字（不含标点，允许上下10%）。保留剧情推进、结局、人物关系、证据来源和数值的近似程度；压缩冗余描写或扩展已有场景，不增加支线，不输出解释。')
    if size(payload)>84000:
        report['adjustment']='kept_original_context_limit';return draft,report
    try:
        reply=gateway.complete(ModelRequest('writer','只返回调整后的完整小说正文，不要JSON或说明。',payload,min(16384,max(1024,target*3))))
        trace.append(dict(role='writer',mode='length_adjustment',raw_output=reply.content,finish_reason=reply.finish_reason,
            input_tokens=reply.input_tokens,output_tokens=reply.output_tokens,cost_usd=reply.cost_usd))
        candidate=prose_from_reply(reply.content)
        count=han_count(candidate) if candidate else 0
        if count and abs(count-target)<abs(actual-target):
            report.update(after=count,adjustment='accepted');return candidate,report
        report['adjustment']='kept_original_no_improvement'
    except Exception as exc:
        report.update(adjustment='kept_original_failure',error_type=type(exc).__name__)
    return draft,report
