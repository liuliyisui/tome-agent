"""Coordinator owns the transaction; agents only return proposals."""
import copy
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from .domain import ContractError, canonical, digest, text, evidence_segments
from .memory import VersionedMemory
from .ports import Agent, CheckpointStore

@dataclass
class ContextBuilder:
    recent_chapters: int = 2
    max_chars: int = 100_000
    max_facts: int = 128
    memory_reader: object = None
    include_fact_sources: bool = True
    def build(self,state):
        if type(self.recent_chapters) is not int or self.recent_chapters<0: raise ContractError("Invalid recent chapter limit")
        facts=(self.memory_reader or VersionedMemory()).current(state)
        if len(facts)>self.max_facts: raise ContractError("Active fact limit exceeded; configure an explicit retrieval policy")
        if type(self.include_fact_sources) is not bool:raise ContractError('include_fact_sources must be boolean')
        if not self.include_fact_sources:
            from .narrative_context import project_facts
            facts=project_facts(facts)
        chapters=state.chapters[-self.recent_chapters:] if self.recent_chapters else []
        result={"goal":state.goal,"constraints":copy.deepcopy(state.constraints),"checkpoint_revision":state.revision,
                "chapter_number":len(state.chapters)+1,"recent_chapters":copy.deepcopy(chapters),"active_facts":facts,
                "planned_next_chapters":[copy.deepcopy(v) for k,v in sorted(state.plan.items(),key=lambda p:int(p[0])) if int(k)>len(state.chapters)],
                "context_policy":{"recent_chapters":self.recent_chapters,"older_prose_omitted":max(0,len(state.chapters)-len(chapters)),"history_included":False}}
        if not self.include_fact_sources:result['context_policy']['fact_sources_included']=False
        if len(canonical(result))>self.max_chars: raise ContractError("Context size exceeded; no silent truncation of facts")
        return result

@dataclass
class Outcome:
    status: str
    chapter_number: int | None = None
    issues: list[str] = field(default_factory=list)
    error: str | None = None
    audit_warning: str | None = None
    attempt_id: str | None = None

class Coordinator:
    def __init__(self,store:CheckpointStore,agents:dict[str,Agent],context_builder=None,memory_policy=None):
        if set(agents)!={"planner","writer","memory","reviewer"}: raise ContractError("Four role agents required")
        if any(agent.role!=role for role,agent in agents.items()): raise ContractError("Agent role binding mismatch")
        self.memory_policy=memory_policy or VersionedMemory()
        self.store=store; self.agents=agents; self.context_builder=context_builder or ContextBuilder(memory_reader=self.memory_policy,include_fact_sources=not getattr(agents['planner'],'compact_narrative',False))
    def write_next(self,identifier,request_id,instruction=""):
        attempt_id="attempt_"+uuid.uuid4().hex; trace=[]; started=datetime.now().astimezone().isoformat(); begin=time.monotonic()
        result=Outcome("FAILED",attempt_id=attempt_id); revision=None
        try:
            text(request_id,"request id")
            if len(request_id)>128 or not isinstance(instruction,str): raise ContractError("Invalid request identity/instruction")
            instruction_hash=digest(instruction); state=self.store.load(identifier); revision=state.revision
            receipt=state.receipts.get(request_id)
            if receipt:
                if receipt["instruction_hash"]!=instruction_hash: raise ContractError("Idempotency key reused with a different instruction")
                result=Outcome("ALREADY_COMMITTED",receipt["chapter_number"],attempt_id=attempt_id)
            else:
                context=self.context_builder.build(state); context["instruction"]=instruction
                proposed_plan=self.agents["planner"].run(context,trace)
                if proposed_plan["number"]!=len(state.chapters)+1: raise ContractError("Planner returned a non-next chapter")
                writing_context={**context,"chapter_plan":proposed_plan}
                draft=self.agents["writer"].run(writing_context,trace)["text"]
                memory_context={**writing_context,"current_draft":draft,"evidence_segments":evidence_segments(draft)}
                from .drafting import normalize_memory
                changes=self.agents["memory"].run(memory_context,trace,
                    validator=lambda value:normalize_memory(value,state,proposed_plan,draft)
                    if getattr(self.agents['reviewer'],'review_mode',None)=='light_memory' or
                        getattr(self.agents['reviewer'],'review_contract_version',0)==1 or
                        any(isinstance(row,dict) and 'claim_ops' in row for row in value['changes']) else value)["changes"]
                # Validate mechanical constraints before reviewer; no partial promotion.
                candidate=self.memory_policy.stage(state,proposed_plan,draft,changes,request_id,instruction_hash)
                review_context={**memory_context,"memory_changes":changes}
                if getattr(self.agents['reviewer'],'review_contract_version',0)==1:
                    from .review_contract import prepare_review_context
                    review_context=prepare_review_context(review_context)
                    if getattr(self.agents['reviewer'],'review_policy_version',0) in (1,2,3,4,5):
                        from .review_policy import prepare_policy_context
                        review_context['review_policy_version']=self.agents['reviewer'].review_policy_version
                        review_context=prepare_policy_context(review_context)
                review=self.agents["reviewer"].run(review_context,trace)
                if not review["approved"]: result=Outcome("REJECTED",issues=review["issues"],attempt_id=attempt_id)
                else:
                    self.store.commit(candidate,expected_revision=state.revision)
                    result=Outcome("COMMITTED",len(candidate.chapters),attempt_id=attempt_id)
        except Exception as exc:
            # Local chapter failure does not stop another story. Caller decides retry policy.
            result.error=type(exc).__name__+": "+str(exc)
        record={"schema_version":1,"project_id":identifier,"request_id":request_id,"attempt_id":attempt_id,
                "started_at":started,"ended_at":datetime.now().astimezone().isoformat(),"elapsed_seconds":time.monotonic()-begin,
                "starting_revision":revision,"status":result.status,"chapter_number":result.chapter_number,
                "issues":result.issues,"error":result.error,"model_calls":trace}
        try: self.store.save_audit(identifier,attempt_id,record)
        except Exception as exc:
            # A failed audit write must never disguise a successfully committed receipt as a failed chapter.
            result.audit_warning="Audit persistence failed: "+type(exc).__name__
        return result
