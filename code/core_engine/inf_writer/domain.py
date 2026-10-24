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


def evidence_segments(draft):
    """Unchanged line/300-character policy; IDs are chapter-local."""
    text(draft, "draft")
    rows = []
    for match in re.finditer(r"[^\r\n]+", draft):
        for offset in range(match.start(), match.end(), 300):
            end = min(offset + 300, match.end())
            rows.append(dict(id=f"e{len(rows)+1:04d}", start=offset, end=end, text=draft[offset:end]))
    return rows


def checked_support(support, draft, value=None, check_value=True, retire=False, resolved=False):
    """Check literal binding and explicit value coverage, NOT semantic entailment."""
    if not isinstance(support, list) or not 1 <= len(support) <= 16:
        raise ContractError("support requires 1..16 claims")
    catalog = {row['id']: row for row in evidence_segments(draft)}
    result, claims = [], []
    for claim in support:
        fields(claim, ('claim', 'evidence'))
        label = text(claim['claim'], 'claim')
        if label in claims: raise ContractError('Duplicate claim')
        claims.append(label)
        items = claim['evidence']
        if not isinstance(items, list) or not 1 <= len(items) <= 8:
            raise ContractError('Each claim requires 1..8 evidence records')
        evidence, seen = [], set()
        for item in items:
            fields(item, ('evidence_id', 'quote', 'start', 'end') if resolved else ('evidence_id', 'quote'),
                   () if resolved else ('start', 'end'))
            identifier = item['evidence_id']
            if not isinstance(identifier, str) or identifier not in catalog:
                raise ContractError('Unknown evidence_id')
            segment = catalog[identifier]; quote = text(item['quote'], 'quote')
            offset = segment['text'].find(quote)
            if offset < 0: raise ContractError('Quote absent from selected evidence segment')
            start = item.get('start', segment['start'] + offset)
            end = item.get('end', start + len(quote)) if type(start) is int else None
            integer(start, 'evidence start'); integer(end, 'evidence end', 1)
            if not segment['start'] <= start < end <= segment['end'] or draft[start:end] != quote:
                raise ContractError('Evidence offset or segment mismatch')
            if ('start' in item) != ('end' in item): raise ContractError('Supply both evidence offsets or neither')
            key = (identifier, start, end)
            if key in seen: raise ContractError('Duplicate evidence within claim')
            seen.add(key); evidence.append(dict(evidence_id=identifier, quote=quote, start=start, end=end))
        result.append(dict(claim=label, evidence=evidence))
    if check_value:
        if retire:
            if value is not None or len(claims) != 1: raise ContractError('Retire requires null value and one retirement claim')
        elif isinstance(value, str):
            if claims != [value]: raise ContractError('String value must exactly equal its single claim')
        elif not isinstance(value, list) or value != claims:
            raise ContractError('List value must exactly match the ordered claims; no unbound content')
    return result


def validate_support_review(result, context):
    """Require explicit per-claim judgements without pretending to verify their truth."""
    if context.get('review_contract_version')==1:
        from .review_contract import validate_catalog_checks
        return validate_catalog_checks(result,context)
    expected = {f'memory_{i}/claim_{j}' for i, row in enumerate(context.get('memory_changes', []), 1)
                for j, claim in enumerate(row.get('support', []), 1)}
    expected.update(f'memory_{i}/removal_{j}' for i,row in enumerate(context.get('memory_changes',[]),1)
                    for j,item in enumerate(row.get('removals',[]),1))
    checks = result.get('support_checks', [])
    if not isinstance(checks, list): raise ContractError('support_checks must be a list')
    seen, all_supported = set(), True
    for check in checks:
        fields(check, ('claim_ref', 'status', 'reason'))
        ref = text(check['claim_ref'], 'claim_ref')
        if ref not in expected or ref in seen: raise ContractError('Unknown or duplicate support check')
        seen.add(ref); text(check['reason'], 'support check reason')
        if check['status'] not in ('supported', 'partial', 'unsupported', 'uncertain'):
            raise ContractError('Invalid support check status')
        all_supported = all_supported and check['status'] == 'supported'
    if seen != expected: raise ContractError('support_checks must cover every new-format claim')
    if not all_supported and (result.get('approved') or result.get('memory_check', {}).get('status') == 'sufficient'):
        raise ContractError('Partial/unsupported/uncertain claims cannot be approved or called sufficient')
    return result

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
        if data["schema_version"] not in (1,2,3) or type(data["schema_version"]) is not int: raise ContractError("Unsupported snapshot schema")
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
            fields(source,("chapter_number","chapter_sha256"),("quote","support","claim_sources","removed"))
            if sum(k in source for k in ('quote','support','claim_sources')) != 1:
                raise ContractError('Source requires one explicit evidence format')
            if 'removed' in source and 'claim_sources' not in source: raise ContractError('Removal log requires claim_sources')
            n=integer(source["chapter_number"],"source chapter",1)
            if n>len(data["chapters"]): raise ContractError("Future/missing evidence source")
            ch=data["chapters"][n-1]
            if source["chapter_sha256"]!=ch["sha256"]:
                raise ContractError("Evidence source changed or quote absent")
            if 'claim_sources' in source:
                from .claim_updates import validate_claim_sources
                if data['schema_version'] != 3: raise ContractError('Cross-chapter sources require schema 3')
                validate_claim_sources(source['claim_sources'],data['chapters'],n)
                removed = source.get('removed',[])
                if not isinstance(removed,list) or len(removed)>16: raise ContractError('Invalid removed claims')
                labels = set()
                for item in removed:
                    fields(item,('claim','evidence','chapter_number','chapter_sha256','reason'))
                    text(item['reason'],'removal reason')
                    if item['claim'] in labels: raise ContractError('Duplicate removed claim')
                    labels.add(item['claim'])
                    if item['chapter_number'] != n: raise ContractError('Removal needs evidence from update chapter')
                    validate_claim_sources([{k:v for k,v in item.items() if k!='reason'}],data['chapters'],n)
            elif 'support' in source:
                if data['schema_version'] not in (2,3): raise ContractError('New support requires schema 2 or 3')
                checked_support(source['support'], ch['text'], check_value=False, resolved=True)
            elif text(source['quote'], 'quote') not in ch['text']:
                raise ContractError('Evidence source changed or quote absent')
        def fact_check(fact):
            fields(fact,("subject","attribute","value","revision","status","source","reason"))
            identity(fact["subject"],fact["attribute"]); integer(fact["revision"],"fact revision",1)
            if fact["status"] not in ("active","retired"): raise ContractError("Invalid fact status")
            if (fact["value"] is None)!=(fact["status"]=="retired"): raise ContractError("Invalid retired/current value")
            text(fact["reason"],"reason"); source_check(fact["source"])
            if 'claim_sources' in fact['source']:
                if fact['status']!='active' or fact['value'] != [row['claim'] for row in fact['source']['claim_sources']]:
                    raise ContractError('Claim source/value mismatch')
            if 'support' in fact['source']:
                checked_support(fact['source']['support'], data['chapters'][fact['source']['chapter_number']-1]['text'],
                                fact['value'], retire=fact['status']=='retired', resolved=True)
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
        is_patch = isinstance(entry,dict) and 'claim_ops' in entry
        if is_patch:
            from .claim_updates import resolve_patch
            entry = resolve_patch(entry,state,draft,prepared='value' in entry)
        else:
            fields(entry,("action","subject","attribute","value","expected_revision","reason"),("quote","support"))
        key=identity(entry["subject"],entry["attribute"])
        if key in seen: raise ContractError("At most one final change per attribute per chapter")
        seen.add(key); action=entry["action"]; old=trial.facts.get(key)
        if action not in ("store","update","retire"): raise ContractError("Unknown memory action")
        reason=text(entry["reason"],"reason")
        if is_patch:
            trial.schema_version = 3
            source=dict(chapter_number=number,chapter_sha256=digest(draft),claim_sources=copy.deepcopy(entry['support']),
                        removed=copy.deepcopy(entry['removals']))
        elif ('quote' in entry) == ('support' in entry): raise ContractError('Supply quote or support exclusively')
        elif 'support' in entry:
            support = checked_support(entry['support'], draft, entry['value'], retire=action=='retire')
            trial.schema_version = max(trial.schema_version,2)
            source=dict(chapter_number=number,chapter_sha256=digest(draft),support=support)
        else:
            quote=text(entry['quote'], 'quote')
            if quote not in draft: raise ContractError('Memory evidence must quote this accepted draft')
            source=dict(chapter_number=number,chapter_sha256=digest(draft),quote=quote)
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
        if old is not None: trial.history.append(dict(fact=copy.deepcopy(old),replaced_by=copy.deepcopy(source),action=action,reason=reason))
        trial.facts[key]=dict(subject=entry["subject"],attribute=entry["attribute"],value=copy.deepcopy(entry["value"]),
            revision=revision,status="retired" if action=="retire" else "active",source=source,reason=reason)
    trial.revision+=1; trial.receipts[request_id]=dict(instruction_hash=instruction_hash,chapter_number=number)
    return Snapshot.from_dict(trial.to_dict())
