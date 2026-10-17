"""JSON contracts and pure, copy-on-write chapter transactions.

Evidence checks prove quote presence, not semantic entailment or story quality.
"""
import copy
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any

class ContractError(ValueError): pass
class ConflictError(ContractError): pass

def canonical(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise ContractError("Expected finite JSON data") from exc

def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def text(value, label):
    if not isinstance(value,str) or not value.strip(): raise ContractError(f"{label} must be nonempty text")
    return value

def integer(value, label, minimum=0):
    if type(value) is not int or value<minimum: raise ContractError(f"{label} must be integer >= {minimum}")
    return value

def fields(value, required, optional=()):
    if not isinstance(value,dict) or not set(required)<=set(value) or set(value)-set(required)-set(optional):
        raise ContractError("Unexpected or missing fields; required="+str(tuple(required)))
    return value

def project_id(value):
    if not isinstance(value,str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}",value):
        raise ContractError("Unsafe project identifier")
    return value

def strict_json(raw):
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result: raise ContractError("Duplicate JSON field: "+key)
            result[key]=value
        return result
    def reject(value): raise ContractError("Nonfinite JSON: "+value)
    try: return json.loads(raw,object_pairs_hook=unique,parse_constant=reject)
    except (ValueError,TypeError) as exc: raise ContractError("Invalid complete JSON: "+str(exc)) from exc

def identity(subject, attribute):
    text(subject,"subject")
    if not isinstance(attribute,str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}",attribute):
        raise ContractError("Use a stable snake_case attribute; values do not belong in the name")
    return canonical([subject,attribute])

def chapter_plan(value):
    fields(value,("number","title","brief")); integer(value["number"],"chapter number",1)
    text(value["title"],"title"); text(value["brief"],"brief")
    return copy.deepcopy(value)

@dataclass
class Snapshot:
    project_id: str
    goal: str
    constraints: list[str] = field(default_factory=list)
    revision: int = 0
    chapters: list[dict] = field(default_factory=list)
    plan: dict[str,dict] = field(default_factory=dict)
    facts: dict[str,dict] = field(default_factory=dict)
    history: list[dict] = field(default_factory=list)
    receipts: dict[str,dict] = field(default_factory=dict)
    schema_version: int = 1

    def to_dict(self): return copy.deepcopy(asdict(self))
    def active_facts(self):
        return [copy.deepcopy(self.facts[k]) for k in sorted(self.facts) if self.facts[k]["status"]=="active"]

    @classmethod
    def from_dict(cls,data):
        fields(data,cls.__dataclass_fields__)
        if data["schema_version"]!=1 or type(data["schema_version"]) is not int: raise ContractError("Unsupported snapshot schema")
        project_id(data["project_id"]); text(data["goal"],"goal"); integer(data["revision"],"revision")
        for name in ("constraints","chapters","history"):
            if not isinstance(data[name],list): raise ContractError(name+" must be list")
        for name in ("facts","plan","receipts"):
            if not isinstance(data[name],dict): raise ContractError(name+" must be object")
        for constraint in data["constraints"]: text(constraint,"constraint")
        if len(data["chapters"])!=data["revision"]: raise ContractError("Chapter/revision mismatch")
        for n,ch in enumerate(data["chapters"],1):
            fields(ch,("number","title","text","sha256")); integer(ch["number"],"chapter number",1)
            if ch["number"]!=n or ch["sha256"]!=digest(text(ch["text"],"chapter text")): raise ContractError("Chapter hash/order mismatch")
            text(ch["title"],"title")
        def source_check(source):
            fields(source,("chapter_number","chapter_sha256","quote"))
            n=integer(source["chapter_number"],"source chapter",1)
            if n>len(data["chapters"]): raise ContractError("Future/missing evidence source")
            ch=data["chapters"][n-1]
            if source["chapter_sha256"]!=ch["sha256"] or text(source["quote"],"quote") not in ch["text"]:
                raise ContractError("Evidence source changed or quote absent")
        def fact_check(fact):
            fields(fact,("subject","attribute","value","revision","status","source","reason"))
            identity(fact["subject"],fact["attribute"]); integer(fact["revision"],"fact revision",1)
            if fact["status"] not in ("active","retired"): raise ContractError("Invalid fact status")
            if (fact["value"] is None)!=(fact["status"]=="retired"): raise ContractError("Invalid retired/current value")
            text(fact["reason"],"reason"); source_check(fact["source"])
        for key,fact in data["facts"].items():
            fact_check(fact)
            if key!=identity(fact["subject"],fact["attribute"]): raise ContractError("Fact identity mismatch")
        for old in data["history"]:
            fields(old,("fact","replaced_by","action","reason")); fact_check(old["fact"]); source_check(old["replaced_by"])
            if old["action"] not in ("update","retire"): raise ContractError("Invalid archive action")
            text(old["reason"],"archive reason")
        for key,entry in data["plan"].items():
            chapter_plan(entry)
            if key!=str(entry["number"]): raise ContractError("Plan identity mismatch")
        for key,receipt in data["receipts"].items():
            text(key,"request id"); fields(receipt,("instruction_hash","chapter_number")); text(receipt["instruction_hash"],"instruction hash")
            if integer(receipt["chapter_number"],"receipt chapter",1)>len(data["chapters"]): raise ContractError("Receipt points to missing chapter")
        canonical(data)
        return cls(**copy.deepcopy(data))

def apply_chapter(state, proposal, draft, changes, request_id, instruction_hash):
    """Produce a new snapshot; never mutate the input or persist a partial group."""
    trial=Snapshot.from_dict(state.to_dict()); text(request_id,"request id"); text(instruction_hash,"instruction hash")
    if request_id in trial.receipts: raise ConflictError("Request already committed")
    fields(proposal,("number","title","brief","future_updates"))
    current=chapter_plan({k:proposal[k] for k in ("number","title","brief")})
    number=len(trial.chapters)+1
    if current["number"]!=number: raise ContractError("Planner must produce the next unwritten chapter")
    text(draft,"draft")
    if not isinstance(proposal["future_updates"],list) or not isinstance(changes,list): raise ContractError("Expected list proposals")
    if len(changes)>128: raise ContractError("Memory candidate cap exceeded")
    trial.plan[str(number)]=current; seen_plans=set()
    for future in proposal["future_updates"]:
        future=chapter_plan(future)
        if future["number"]<=number or future["number"] in seen_plans: raise ContractError("Only unique future chapter plans can change")
        seen_plans.add(future["number"]); trial.plan[str(future["number"])]=future
    trial.chapters.append(dict(number=number,title=current["title"],text=draft,sha256=digest(draft)))
    seen=set()
    for entry in changes:
        fields(entry,("action","subject","attribute","value","expected_revision","quote","reason"))
        key=identity(entry["subject"],entry["attribute"])
        if key in seen: raise ContractError("At most one final change per attribute per chapter")
        seen.add(key); action=entry["action"]; old=trial.facts.get(key)
        if action not in ("store","update","retire"): raise ContractError("Unknown memory action")
        quote=text(entry["quote"],"quote"); reason=text(entry["reason"],"reason")
        if quote not in draft: raise ContractError("Memory evidence must quote this accepted draft")
        canonical(entry["value"])
        if (entry["value"] is None)!=(action=="retire"): raise ContractError("Only retire uses null value")
        if action=="store":
            if old is not None or entry["expected_revision"] is not None: raise ConflictError("Store requires a new attribute and null revision")
            revision=1
        else:
            integer(entry["expected_revision"],"expected_revision",1)
            if old is None or old["revision"]!=entry["expected_revision"]: raise ConflictError("Stale or missing fact revision")
            if action=="retire" and old["status"]=="retired": raise ConflictError("Attribute already retired")
            revision=old["revision"]+1
        source=dict(chapter_number=number,chapter_sha256=digest(draft),quote=quote)
        if old is not None: trial.history.append(dict(fact=copy.deepcopy(old),replaced_by=copy.deepcopy(source),action=action,reason=reason))
        trial.facts[key]=dict(subject=entry["subject"],attribute=entry["attribute"],value=copy.deepcopy(entry["value"]),
            revision=revision,status="retired" if action=="retire" else "active",source=source,reason=reason)
    trial.revision+=1; trial.receipts[request_id]=dict(instruction_hash=instruction_hash,chapter_number=number)
    return Snapshot.from_dict(trial.to_dict())
