"""Four responsibility agents; different tasks/contracts, optionally different models."""
import copy
from dataclasses import dataclass
from .domain import ContractError, chapter_plan, fields, strict_json, text
from .models import ModelGateway, ModelRequest

PROMPTS={
 "planner":"你是INF规划智能体。根据总纲、约束和已有状态，只规划下一章；future_updates只能局部修改尚未写作的后续章节。输出JSON：number,title,brief,future_updates（每项number,title,brief）。不要把计划当已发生事实。",
 "writer":"你是INF写作智能体。依照本章计划、总纲约束和当前记忆创作正文。只输出JSON对象，例如{\"text\":\"正文\"}，不要额外添加type、标题字段、解释或代码围栏。人物变化要有事件依据；不能自行修改正式记忆。",
 "memory":"你是INF记忆维护智能体。只根据当前正文和既有记忆提出必要的store/update/retire。输出JSON：changes数组，空数组时必须另给no_change_reason说明为何没有新增或变化事实。每项action,subject,attribute,value,expected_revision,reason，以及evidence_id或quote二选一。若输入提供evidence_segments，优先选其中一个evidence_id；程序会取回原文，禁止自己合并或改写引文。attribute必须是稳定英文snake_case，例如eye_color、location、occupation、known_information；不得用中文、属性值或整句当字段名，已有属性沿用原名。store的expected_revision为null；update/retire用已有revision；retire的value为null。不提到不等于丢失；人物猜测、计划或假设不等于世界真值，可记为该人物的suspected_information而不是指控对象的确定属性。程序归档旧值。不能为了避免格式错误就删除需要保留的全部事实。",
 "reviewer":"你是INF审核智能体。区分硬矛盾与可调整小纲建议。人物说出的猜测不自动等于叙述者确认的事实；小纲未列出的动作、对话、合理反应或信息释放快慢不能单独当硬矛盾。若提供hard_references，输出JSON：approved布尔、issues硬问题数组、suggestions字符串数组、memory_check对象(status为sufficient/missing/uncertain，reason说明复核了哪些事实)。每条硬问题必须给kind(fact_conflict/world_rule/causality/unsupported_memory/memory_omission)、description、draft_quote(逐字正文片段)、basis_ref(输入hard_references里的键)、basis_quote(该参考中的逐字引文)。不得用尚未写作的计划当已经发生的事实。只有具体证据支持的硬问题或记忆遗漏才阻止审核通过，节奏/小纲分歧放suggestions。独立检查记忆提案是否遗漏重要新事实，空changes不代表记忆充分。存在未检查章节时明确其为草稿上下文，不假称已验证。旧接口未提供hard_references时仍可输出approved和字符串issues。"
}

def validate(role,result):
    if role=="planner":
        fields(result,("number","title","brief","future_updates"))
        chapter_plan({k:result[k] for k in ("number","title","brief")})
        if not isinstance(result["future_updates"],list): raise ContractError("future_updates must be list")
        for item in result["future_updates"]: chapter_plan(item)
    elif role=="writer":
        fields(result,("text",),("type",))
        if "type" in result and result["type"]!="json_object":
            raise ContractError("Writer optional type must be exactly json_object")
        # Narrow compatibility for the observed response; do not drop arbitrary keys.
        return {"text":text(result["text"],"draft")}
    elif role=="memory":
        fields(result,("changes",),("no_change_reason",))
        if not isinstance(result["changes"],list): raise ContractError("changes must be list")
    elif role=="reviewer":
        fields(result,("approved","issues"),("suggestions","memory_check"))
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

    def run(self,context,trace,validator=None):
        if type(self.max_format_retries) is not int or not 0<=self.max_format_retries<=1: raise ContractError("Format repairs must be0or1")
        payload=copy.deepcopy(context)
        for attempt in range(self.max_format_retries+1):
            entry={"role":self.role,"attempt":attempt+1}; trace.append(entry)
            reply=self.gateway.complete(ModelRequest(self.role,PROMPTS[self.role],copy.deepcopy(payload),self.max_output_tokens))
            entry.update(raw_output=reply.content,input_tokens=reply.input_tokens,output_tokens=reply.output_tokens,cost_usd=reply.cost_usd)
            try:
                parsed=strict_json(reply.content)
                result=validate(self.role,parsed)
                if self.role=="writer" and "type" in parsed:
                    entry["normalizations"]=[{"rule":"writer_json_object_type","field":"type","value":parsed["type"]}]
                if validator is not None: result=validator(result)
                entry["status"]="ACCEPTED"; return result
            except ContractError as exc:
                entry.update(status="FORMAT_FAILED",error=str(exc))
                if attempt==self.max_format_retries: raise
                payload["repair"]={"error":str(exc),"previous_output":reply.content,"instruction":"只修复当前智能体的输出与所列证据/契约问题，保留正文和已正确候选，不编造事实，不用删除全部候选逃避修复。"}
        raise ContractError("Unreachable agent state")

def build_agents(gateway):
    """The same gateway may serve all roles; callers can supply one per role instead."""
    return {role:JsonAgent(role,gateway) for role in PROMPTS}
