"""A separate, bounded agent that patches only identified failed actions."""
import copy
import re
from inf_writer.domain import ContractError,canonical,strict_json
from inf_writer.models import ModelRequest


def repair(gateway,proposal,choices,details,trace):
    allowed=set()
    def locate(value):
        if isinstance(value,dict):
            path=value.get('path','')
            match=re.search(r'scenes\[(\d+)\]\.beats\[(\d+)\]',path)
            if match:allowed.add(tuple(map(int,match.groups())))
            for child in value.values():locate(child)
        elif isinstance(value,list):
            for child in value:locate(child)
    locate(details)
    if not allowed:raise ContractError('No action locator available for local repair')
    payload=dict(proposal=proposal,reference_choices=choices,errors=details,
        allowed_action_positions=[list(v) for v in sorted(allowed)],
        output_contract=dict(patches=[dict(scene_index=0,beat_index=0,replacement='完整公开动作对象；不含程序编号')]))
    from .reference_choices import formal_operation_catalogue
    payload['operation_schemas']=formal_operation_catalogue()
    if len(canonical(payload).encode('utf-8'))>96000:raise ContractError('Local repair input exceeds its budget')
    # This is an independent role, not another request to the original planner.
    response=gateway.complete(ModelRequest('state_repair',
        '你是结构化状态局部修复员，不构思新剧情。只修allowed_action_positions列出的动作。输出JSON patches数组，每项scene_index、beat_index（均0基）和replacement完整公开动作。保留正确陈述与变更，只修错误字段及必要依赖；引用选给定目录或本章位置；不造编号，不把计划当完成，不改历史事实，不删除无关正确记录。',payload,16384))
    trace.append(dict(role='state_repair',raw_output=response.content,finish_reason=response.finish_reason,
        input_tokens=response.input_tokens,output_tokens=response.output_tokens,cost_usd=response.cost_usd))
    result=strict_json(response.content)
    if not isinstance(result,dict) or set(result)!={'patches'} or not isinstance(result['patches'],list) or not result['patches']:
        raise ContractError('Repair must return nonempty patches')
    updated=copy.deepcopy(proposal);seen=set()
    for row in result['patches']:
        if not isinstance(row,dict) or set(row)!={'scene_index','beat_index','replacement'}:raise ContractError('Invalid repair patch fields')
        pos=(row['scene_index'],row['beat_index'])
        if any(type(i) is not int for i in pos) or pos not in allowed or pos in seen:raise ContractError('Repair cannot change an unlisted or duplicate action')
        if not isinstance(row['replacement'],dict):raise ContractError('Repair replacement must be an action')
        updated['scenes'][pos[0]]['beats'][pos[1]]=copy.deepcopy(row['replacement']);seen.add(pos)
    return updated
