"""Replaceable memory/state-transition policy; no role-specific private stores yet."""
import copy
from typing import Protocol
from .domain import ContractError, Snapshot, apply_chapter, integer

class MemoryPolicy(Protocol):
    def current(self,state:Snapshot)->list[dict]: ...
    def stage(self,state,plan,draft,changes,request_id,instruction_hash)->Snapshot: ...

class VersionedMemory:
    def current(self,state): return state.active_facts()
    def stage(self,state,plan,draft,changes,request_id,instruction_hash):
        return apply_chapter(state,plan,draft,changes,request_id,instruction_hash)
    def history(self,state,subject,attribute,limit=5):
        integer(limit,"history limit",1)
        if limit>100: raise ContractError("History query limit is100")
        # Revalidate source hashes/quotes before returning any archived observation.
        checked=Snapshot.from_dict(state.to_dict())
        rows=[copy.deepcopy(row) for row in checked.history if row["fact"]["subject"]==subject and row["fact"]["attribute"]==attribute]
        return rows[-limit:][::-1]
