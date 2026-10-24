"""Four responsibility agents; different tasks/contracts, optionally different models."""
import copy
from dataclasses import dataclass
from .domain import ContractError, chapter_plan, fields, strict_json, text
from .models import ModelGateway, ModelRequest

PROMPTS={
 "planner":"你是INF规划智能体。根据总纲、约束和已有状态，只规划下一章；future_updates只能局部修改尚未写作的后续章节。输出JSON：number,title,brief,future_updates（每项number,title,brief）。不要把计划当已发生事实。",
 "writer":"你是INF写作智能体。依照本章计划、总纲约束和当前记忆创作正文。只输出JSON对象，例如{\"text\":\"正文\"}，不要额外添加type、标题字段、解释或代码围栏。人物变化要有事件依据；不能自行修改正式记忆。",
 "memory":"你是INF记忆维护智能体。只根据当前正文和既有记忆提出必要的store/update/retire。只输出JSON对象，顶层只含changes及可选no_change_reason，不添加type、changed、解释或代码围栏。changes是数组，空数组时必须另给no_change_reason说明为何没有新增或变化事实。每项action,subject,attribute,value,expected_revision,reason，以及evidence_id或quote二选一。若输入提供evidence_segments，优先选其中一个evidence_id；程序会取回原文，禁止自己合并或改写引文。attribute必须是稳定英文snake_case，例如eye_color、location、occupation、known_information；不得用中文、属性值或整句当字段名，已有属性沿用原名。以subject + attribute查找active_facts中的已有记录：不存在才store且expected_revision为null；已有同名属性发生变化必须update，expected_revision抄该条的revision，不能store。已有事实未变不重复写。同一主体同一属性每章只提交一个最终变化，不能先store再update。退役用retire且value为null，同样匹配已有revision。程序自动归档旧值，不自行修改旧记录。新属性示例：{\"changes\":[{\"action\":\"store\",\"subject\":\"甲\",\"attribute\":\"location\",\"value\":\"门外\",\"expected_revision\":null,\"evidence_id\":\"e0001\",\"reason\":\"正文明确位置\"}]}。若甲.location已有revision=2，变化示例：{\"changes\":[{\"action\":\"update\",\"subject\":\"甲\",\"attribute\":\"location\",\"value\":\"屋内\",\"expected_revision\":2,\"evidence_id\":\"e0002\",\"reason\":\"正文写明移动\"}]}。示例不是本章事实，必须使用输入真实主体、版本、值与证据编号。不提到不等于丢失；人物猜测、计划或假设不等于世界真值，可记为该人物的suspected_information而不是指控对象的确定属性。不能为了避免格式错误就删除需要保留的全部事实。",
 "reviewer":"你是INF审核智能体。区分硬矛盾与可调整小纲建议。人物说出的猜测不自动等于叙述者确认的事实；小纲未列出的动作、对话、合理反应或信息释放快慢不能单独当硬矛盾。若提供hard_references，输出JSON：approved布尔、issues硬问题数组、suggestions字符串数组、memory_check对象(status为sufficient/missing/uncertain，reason说明复核了哪些事实)。每条硬问题必须给kind(fact_conflict/world_rule/causality/unsupported_memory/memory_omission)、description、draft_quote(逐字正文片段)、basis_ref(输入hard_references里的键)、basis_quote(该参考中的逐字引文)。不得用尚未写作的计划当已经发生的事实。只有具体证据支持的硬问题或记忆遗漏才阻止审核通过，节奏/小纲分歧放suggestions。独立检查记忆提案是否遗漏重要新事实，空changes不代表记忆充分。存在未检查章节时明确其为草稿上下文，不假称已验证。旧接口未提供hard_references时仍可输出approved和字符串issues。"
}

PROMPTS["memory"] += (
    "位置、持有人等当前状态只提交正文支持的章末最终值，数组先后不代表事件先后。"
    "known_information或suspected_information中的不同信息不一定互相替代，不能只保留最后一条；"
    "依据正文合并仍有效信息或使用真正不同且稳定的语义属性，不用编号后缀绕过重复检查。"
    "旧认识被证伪时应依据正文更新，不能盲目取并集。重要中间事件或其后果需用明确语义和证据保留。"
    "合并值包含的每项信息都须有正文证据，不得编造证据、拼接引文。"
    "修复反馈若有details.groups，应逐组处理，保留其他正确候选，不修改正文，不额外增加重试。"
)

# Isolated prototype: old single-quote contracts remain readable, new generation uses support.
PROMPTS['memory'] = PROMPTS['memory'].replace(
    '每项action,subject,attribute,value,expected_revision,reason，以及evidence_id或quote二选一。若输入提供evidence_segments，优先选其中一个evidence_id；程序会取回原文，禁止自己合并或改写引文。',
    '每项action,subject,attribute,value,expected_revision,reason，以及下述support。evidence_segments用于定位原文，禁止自己合并或改写引文。'
).replace('新属性示例：', '旧接口兼容示例（新输出请用下述support）：').replace('变化示例：', '旧接口兼容变化示例（新输出请用下述support）：')
PROMPTS['memory'] += (
    '本副本生成新提案时，用support替代顶层evidence_id/quote，不混用。'
    'support=[{"claim":"一项信息","evidence":[{"evidence_id":"当前章片段ID","quote":"该片段中逐字摘录"}]}]。'
    '每项信息单独列claim；一项可有多段证据，不为不同信息新增编号属性。'
    'value为字符串时必须等于唯一claim；多项信息value为按顺序列出的claim字符串数组，必须完整一一对应。'
    '最多16项claim，每项1到8条证据；不得漏列、重复或将无关证据当支持。'
    'retire仍value=null，support只列一项说明退役依据的claim。不输出start/end，由程序定位。'
    '更新累计认识时保留仍有效的信息，当前原型只引用本章证据；不能为通过校验删除旧知识，'
    '若正文不足以支持完整更新，明确反馈限制，不造证据。人物自述、怀疑、计划不升级为客观已发生事实。'
)
PROMPTS['reviewer'] += (
    '对memory_changes中每条support的每个claim逐项输出support_checks数组。'
    '每项含claim_ref(如memory_1/claim_1，两个索引均从1起)、status(supported/partial/unsupported/uncertain)、reason。'
    '核对该claim的全部断言是否被所绑定引文共同支持，不以编号存在当语义正确；同时核对人物视角和时态。'
    '不得漏查、重复或引用不存在的claim。任一partial/unsupported/uncertain时approved=false且memory_check不能sufficient。'
    '旧单引文项仍需原有整批审核，不能因为没有support就默认正确。'
)

PROMPTS['memory'] = PROMPTS['memory'].replace(
    '更新累计认识时保留仍有效的信息，当前原型只引用本章证据；不能为通过校验删除旧知识，若正文不足以支持完整更新，明确反馈限制，不造证据。',
    '新增/改变信息引用本章证据；既有结构化子项可用下述claim_ops局部更新，由程序沿用未变项及旧章证据。'
)
PROMPTS['memory'] += (
    '当已有属性source含support或claim_sources时，优先action=update并以claim_ops替代value/support/quote/evidence_id。'
    'claim_ops数组只列变化：新增{op:add,claim:新信息,evidence:[{evidence_id:本章ID,quote:逐字引文}]}；'
    '替换{op:replace,index:旧数组0基索引,old_claim:旧项逐字内容,claim:新信息,evidence:[...]}；'
    '移除{op:remove,index:旧数组0基索引,old_claim:旧项逐字内容,reason:已失效理由,evidence:[...]}。'
    'index始终指输入原列表，不能按执行中删除后的列表编号，同一旧项只能改一次。'
    '未提及的旧项及其原章节证据由程序原样保留，不需要在本章重复描写；'
    '但旧认识若已失效必须明确replace/remove，不能把继承当永久正确。'
    '不填写value/support/removals，不伪造旧来源；程序生成完整结果供审核。每批最多32操作、最终1到16项。'
    '旧单quote事实不可自动拆项；不能patch退休属性，全部删除须用显式retire。'
)
PROMPTS['reviewer'] += (
    '对增量结果，support每项含原章节/hash/evidence：按该章节核对，不能因本章没重述旧事实就误判无依据。'
    '同时检查旧认识是否被本章证伪。对removals逐项输出support_checks，引用memory_N/removal_N，'
    '判断删除依据是否成立，不能只审剩下的claim而漏掉删掉的知识。未审/partial/unsupported/uncertain仍不能批准。'
)

PROMPTS['reviewer'] += (
    '必须区分当前值与历史值：旧值曾经正确，不代表它永远有效。正文明确把某状态或安排从A变为B时，'
    '可以把当前值replace为B，旧版本由程序归档；不能仅因A在旧章节有证据就要求A继续作为当前事实。'
    '应判断变化依据是否充分、未变化的其他知识是否保留，不把“发生更新”本身当矛盾。'
    '若输入review_items和review_contract_version=1，只按该目录逐项编号，不自行从claim_ops重编号；'
    'support_checks每项必须含claim_ref、逐字回显的claim、status、reason，覆盖全部最终子项和移除项。'
    '旧单quote提案也按目录逐项查，不假设每段引文支持所有内容。'
    '只输出approved/issues/suggestions/memory_check/support_checks；memory_check仅status/reason，'
    '不输出removals_checks，不把support_checks嵌套进memory_check。'
)
PROMPTS['memory'] += (
    '提交前分别检查新增确认、状态变化、旧认识失效、未变项。撤回旧怀疑与新增澄清事实可能同时发生，'
    '不能只删除怀疑而漏记正文新确认的澄清事实；也不把临时计划当已完成。'
    '最终只输出一个完整JSON对象，闭合一次，不在JSON后再补右括号、解释或第二个对象。'
)
PROMPTS['reviewer'] += (
    '提交前检查决策一致性：approved=true当且仅当issues为空且memory_check.status=sufficient。'
    '拒绝需要可核验硬问题或missing/uncertain；重要知识遗漏包括丢失仍有效旧知识，不能只放suggestions又称充分。'
    '不在memory_changes中的字段保持原状；未提及不等于该字段丢失。不要输出type；仅已知json_object元数据可被兼容。'
)
PROMPTS['memory'] += (
    '如有memory_action_catalog，先按subject+attribute核对动作和版本。新增知识不等于store已有字段；'
    '例如同一人物known_information已存在时，新确认事实应用update+claim_ops.add，保留其他旧知识。'
    '跨字段撤回与澄清分别更新原有字段，不改名绕过检查；修复反馈给出完整原候选时保留仍正确部分，'
    '不能为避免冲突删光候选或简单转换动作后覆盖旧值。'
)

from .memory_output_contract import MEMORY_PROMPT
PROMPTS['memory'] = MEMORY_PROMPT

def validate(role,result,review_policy_version=0):
    if role=="planner":
        fields(result,("number","title","brief","future_updates"),("time_calculations","scenes"))
        chapter_plan({k:result[k] for k in ("number","title","brief")})
        if not isinstance(result["future_updates"],list): raise ContractError("future_updates must be list")
        for item in result["future_updates"]: chapter_plan(item)
    elif role=="writer":
        if isinstance(result,dict) and set(result)=={'event_revision_request'}:
            text(result['event_revision_request'],'Event revision request')
            return copy.deepcopy(result)
        fields(result,("text",),("type","time_calculations","continuity_updates","no_continuity_change_reason"))
        if "type" in result and not isinstance(result['type'],str):
            raise ContractError("Writer wrapper type metadata must be a string")
        # Wrapper metadata never selects an operation. Only the validated text
        # field supplies prose; unknown payload fields still fail above.
        return {"text":text(result["text"],"draft"), **{key:copy.deepcopy(result[key]) for key in ('time_calculations','continuity_updates','no_continuity_change_reason') if key in result}}
    elif role=="memory":
        fields(result,("changes",),("no_change_reason","type"))
        if "type" in result and result["type"]!="json_object":
            raise ContractError("Memory optional type must be exactly json_object")
        if not isinstance(result["changes"],list): raise ContractError("changes must be list")
        # Keep the exact candidates/reason; only strip the observed transport metadata.
        return {key:value for key,value in result.items() if key!="type"}
    elif role=="reviewer":
        from .review_contract import normalize_review_output
        result,_=normalize_review_output(result)
        fields(result,("approved","issues"),("suggestions","memory_check","support_checks")+
            (('review_judgments',) if review_policy_version==5 else ())+
            (('coverage_checks',) if review_policy_version in (3,4,5) else ()))
        if type(result["approved"]) is not bool or not isinstance(result["issues"],list): raise ContractError("Invalid review types")
        for issue in result["issues"]:
            if not isinstance(issue,dict): text(issue,"review issue")
        if result["approved"] and result["issues"]: raise ContractError("Approved review cannot contain unresolved issues")
    else: raise ContractError("Unknown agent role")
    return result

@dataclass
class JsonAgent:
    role: str
    gateway: ModelGateway
    max_format_retries: int = 1
    max_output_tokens: int = 4096
    review_contract_version: int = 0
    review_transport_version: int = 0
    review_policy_version: int = 0
    compact_narrative: bool = False

    def run(self,context,trace,validator=None):
        if type(self.max_format_retries) is not int or not 0<=self.max_format_retries<=1: raise ContractError("Format repairs must be0or1")
        payload=copy.deepcopy(context)
        prompt=PROMPTS[self.role]
        if type(self.compact_narrative) is not bool:raise ContractError('compact_narrative must be boolean')
        lean=self.compact_narrative and self.role in ('planner','writer')
        if lean:
            from .narrative_context import prepare_context
            payload=prepare_context(payload)
            prompt+='当前事实的详细来源保存在本地记忆库，输入保留完整当前值，不把来源省略当作事实缺失。格式修复时仅修输出契约，不重写正文或剧情。'
        if 'event_first_contract' in payload:
            if self.role=='planner':
                prompt+='先输出scenes事件方案并声明前提与状态变化，不写章节正文。遵循event_first_contract；event_plan_state是事件方案状态，retrieved_memory是来源记忆。使用operation目录；引用只用reference_selection_contract选择器，不编写编号。'
            elif self.role=='writer':
                prompt='你负责将已冻结的事件展开成小说。只输出一个JSON对象，例如{"text":"场景描写。\\n\\n[[event:slot_001]]后续描写。"}。所有正文放text字符串，不能用clauses或events列表。确需改变关键事实时只输出{"event_revision_request":"修订理由"}。优先按output_contract.ordered_event_tokens顺序各保留一次占位符；完整逐字、有序且唯一的冻结事件原句也可由程序绑定。不能改写、遗漏或重复事件、事实，不改计算输入或另交状态记录；补充描写和对话须与冻结事件一致。'
        if self.role in ('planner','writer'):
            from .narrative_context import event_role_context
            payload=event_role_context(payload,self.role)
        if self.role=='writer' and payload.get('prose_content_checks')=='disabled':
            prompt='你是小说写作者，按所给章节方案、人物和上下文展开完整场景。只输出JSON text正文，正文不要讨论审核或代码。数值沿用quantity_policy及quantity_sources，保留来源的近似程度；优先使用quantity token让程序原样展开。缺乏精确依据时沿用模糊表述，不自行补成精确数字。event token可用于引用方案原句，不是需要你检查和计数的任务。需要修改方案时可输出event_revision_request。'
        if type(self.review_policy_version) is not int or self.review_policy_version not in (0,1,2,3,4,5):
            raise ContractError('Review policy version must be 0, 1, 2, 3, 4, or 5')
        if payload.get('review_policy_version') in (2,3,4,5) and self.review_policy_version!=payload['review_policy_version']:
            raise ContractError('Review policy requires explicit matching agent configuration')
        if self.review_policy_version and (self.role!='reviewer' or self.review_contract_version!=1):
            raise ContractError('Review policy requires reviewer with logical contract v1')
        if type(self.review_transport_version) is not int or self.review_transport_version not in (0,1):
            raise ContractError('Review transport version must be 0 or 1')
        if self.review_transport_version and (self.role!='reviewer' or self.review_contract_version!=1):
            raise ContractError('Compact review transport requires reviewer with logical contract v1')
        if self.role=='reviewer':
            if type(self.review_contract_version) is not int or self.review_contract_version not in (0,1):
                raise ContractError('Review contract version must be 0 or 1')
            if self.review_contract_version==1:
                from .review_contract import prepare_review_context
                if self.review_policy_version:
                    if 'review_policy_version' in payload and payload['review_policy_version']!=self.review_policy_version:
                        raise ContractError('Configured review policy differs from input')
                    payload['review_policy_version']=self.review_policy_version
                payload=prepare_review_context(payload)
                if self.review_policy_version in (1,2,3,4,5):
                    from .review_policy import prepare_policy_context,REVIEW_POLICY_PROMPT
                    payload=prepare_policy_context(payload)
                    if self.review_policy_version in (2,3,4,5):
                        from .review_state import review_prompt
                        prompt=review_prompt(prompt)
                        if self.review_policy_version in (3,4,5):
                            from .semantic_review import PROMPT
                            if self.review_policy_version==4:
                                from .locator_review import PROMPT
                            prompt=prompt.replace('只输出approved/issues/suggestions/memory_check/support_checks；',
                                '输出approved/issues/suggestions/memory_check/support_checks/coverage_checks；')+PROMPT
                        if self.review_policy_version==5:
                            from .judgment_review import PROMPT
                            prompt=PROMPT
                    else:prompt+=REVIEW_POLICY_PROMPT
        elif self.role=='memory':
            from .memory_action_contract import prepare_memory_context
            payload=prepare_memory_context(payload)
            from .memory_output_contract import prepare_context
            payload=prepare_context(payload)
            payload['memory_extraction_checklist']=[
                '新增确认事实是否都考虑了', '已有状态/认识是否变化或失效',
                '撤回旧怀疑时是否还需增加澄清事实', '未变子项保持原来源，猜测和未实施计划不作已确认事实',
                '一个完整JSON，无多余括号或正文']
        for attempt in range(self.max_format_retries+1):
            entry={"role":self.role,"attempt":attempt+1}; trace.append(entry)
            outgoing=copy.deepcopy(payload)
            if self.review_transport_version==1:
                from .review_transport import compact_review_context
                from .domain import canonical,digest
                outgoing=compact_review_context(payload)
                entry['review_transport']=dict(version=1,logical_sha256=digest(canonical(payload)),
                    wire_sha256=digest(canonical(outgoing)),
                    logical_bytes=len(canonical(dict(system=prompt,payload=payload)).encode('utf-8')),
                    wire_bytes=len(canonical(dict(system=prompt,payload=outgoing)).encode('utf-8')))
            if lean:
                from .narrative_context import transport_info
                try:entry['narrative_transport']=transport_info(prompt,outgoing,attempt or bool(outgoing.get('event_preflight_error')))
                except ContractError as exc:
                    entry.update(status='INPUT_REJECTED',error=str(exc),narrative_transport=exc.repair_details)
                    raise
            reply=self.gateway.complete(ModelRequest(self.role,prompt,outgoing,min(65536,self.max_output_tokens*(2 if attempt and payload.get('output_was_truncated') else 1))))
            entry.update(raw_output=reply.content,input_tokens=reply.input_tokens,output_tokens=reply.output_tokens,cost_usd=reply.cost_usd,finish_reason=reply.finish_reason)
            parsed=None
            try:
                if reply.finish_reason=='length':raise ContractError('Model output reached its token allowance; retain partial reply and repair with a larger allowance')
                parsed=strict_json(reply.content)
                if lean and self.role=='planner':
                    from .narrative_context import normalize_planner_metadata
                    parsed,notes=normalize_planner_metadata(parsed)
                    if notes:entry['normalizations']=notes
                if self.role=='reviewer' and self.review_policy_version==5:
                    from .judgment_review import compile_judgments
                    parsed=compile_judgments(parsed,payload)
                if self.role=='reviewer':
                    from .review_contract import normalize_review_output
                    parsed,notes=normalize_review_output(parsed)
                    if notes:entry['normalizations']=notes
                result=validate(self.role,parsed,review_policy_version=self.review_policy_version)
                if self.role=='writer' and 'frozen_events' in payload:
                    if set(result) not in ({'text'},{'event_revision_request'}):
                        raise ContractError('Event-first writer cannot alter facts, calculations or memory')
                elif self.role=='writer' and 'event_revision_request' in result:
                    raise ContractError('Event revision requests require a frozen event transaction')
                if self.role=='writer' and 'continuity_contract' in payload and 'frozen_events' not in payload:
                    if not isinstance(result.get('continuity_updates'),list):
                        raise ContractError('Writer must return continuity_updates list')
                    if not result['continuity_updates']:
                        text(result.get('no_continuity_change_reason'),'Empty continuity update reason')
                if self.role == 'reviewer':
                    from .domain import validate_support_review
                    validate_support_review(result,payload)
                    if self.review_contract_version==1:
                        from .drafting import validate_review
                        validate_review(result,payload)
                if self.role in ("writer","memory") and "type" in parsed:
                    entry["normalizations"]=[{"rule":self.role+("_json_object_type" if parsed['type']=='json_object' else '_wrapper_metadata'),"field":"type","value":parsed["type"]}]
                if validator is not None: result=validator(result)
                if self.role=='reviewer' and self.review_policy_version in (2,3,4,5):
                    from .review_state import support_summary
                    entry['support_summary']=support_summary(result)
                    if self.review_policy_version==5:
                        entry['resolved_review']=copy.deepcopy(result)
                    if self.review_policy_version==4:
                        from .locator_review import coverage_locations
                        entry['coverage_locations']=coverage_locations(result,payload)
                entry["status"]="ACCEPTED"; return result
            except ContractError as exc:
                entry.update(status="FORMAT_FAILED",error=str(exc))
                details=getattr(exc,"repair_details",None)
                if 'output_contract' in payload and self.role in ('planner','writer'):
                    from .narrative_context import output_error_details
                    details=output_error_details(parsed,payload['output_contract'],details)
                    exc.repair_details=copy.deepcopy(details)
                if isinstance(details,dict): entry["repair_details"]=copy.deepcopy(details)
                if attempt==self.max_format_retries: raise
                if lean:
                    from .narrative_context import prepare_repair
                    payload=prepare_repair(payload,exc,reply.content,details)
                    if reply.finish_reason=='length':payload['output_was_truncated']=True
                    continue
                payload["repair"]={"error":str(exc),"previous_output":reply.content,"instruction":"只修复当前智能体的输出与所列证据/契约问题，保留正文和已正确候选，不编造事实，不用删除全部候选逃避修复。"}
                if self.role=='reviewer' and self.review_policy_version in (4,5):
                    from .review_repair import encode_previous
                    payload['repair']['previous_output']=encode_previous(reply.content,payload)
                if isinstance(details,dict): payload["repair"]["details"]=copy.deepcopy(details)
        raise ContractError("Unreachable agent state")

def build_agents(gateway,review_contract_version=0,review_transport_version=0,review_policy_version=0):
    """The same gateway may serve all roles; callers can supply one per role instead."""
    return {role:JsonAgent(role,gateway,review_contract_version=review_contract_version if role=='reviewer' else 0,
        review_transport_version=review_transport_version if role=='reviewer' else 0,
        review_policy_version=review_policy_version if role=='reviewer' else 0) for role in PROMPTS}
