"""Lossless JSON-value reference encoding for v4's one format repair.

The exact raw response remains in the trace. No list or decision is pruned.
"""
import copy
from .domain import ContractError,canonical,digest,strict_json

MARKER='$inf_repair_ref'

def _strings(context):
    values={}
    for i,row in enumerate(context.get('review_items',[])):
        values[f'/review_items/{i}/claim']=row['claim']
        source=row.get('source',{})
        if isinstance(source.get('quote'),str):values[f'/review_items/{i}/source/quote']=source['quote']
        for j,ev in enumerate(source.get('evidence',[])):
            values[f'/review_items/{i}/source/evidence/{j}/quote']=ev['quote']
    for field in ('evidence_segments','semantic_contexts'):
        for i,row in enumerate(context.get(field,[])):values[f'/{field}/{i}/text']=row['text']
    for key,value in context.get('coverage_targets',{}).items():values[f'/coverage_targets/{key.replace("~","~0").replace("/","~1")}']=value
    return {key:value for key,value in values.items() if isinstance(value,str)}

def encode_previous(raw,context):
    try:parsed=strict_json(raw)
    except ContractError:return dict(encoding='raw-text-v1',text=raw,raw_sha256=digest(raw))
    def reserved(value):
        if isinstance(value,dict):return MARKER in value or any(reserved(v) for v in value.values())
        if isinstance(value,list):return any(reserved(v) for v in value)
        return False
    if reserved(parsed):return dict(encoding='raw-text-v1',text=raw,raw_sha256=digest(raw))
    sources=_strings(context)
    def encode(value):
        if isinstance(value,str) and len(value)>=16:
            for path,source in sources.items():
                start=source.find(value)
                if start>=0:
                    alias={MARKER:path,'start':start,'end':start+len(value)}
                    if len(canonical(alias).encode('utf-8'))<len(canonical(value).encode('utf-8')):return alias
        if isinstance(value,dict):return {key:encode(v) for key,v in value.items()}
        if isinstance(value,list):return [encode(v) for v in value]
        return copy.deepcopy(value)
    encoded=dict(encoding='review-json-refs-v1',value=encode(parsed),raw_sha256=digest(raw),value_sha256=digest(canonical(parsed)))
    if decode_previous(encoded,context)!=parsed:raise ContractError('Repair encoding changed previous JSON value')
    return encoded

def decode_previous(encoded,context):
    if encoded.get('encoding')=='raw-text-v1':
        if digest(encoded['text'])!=encoded['raw_sha256']:raise ContractError('Previous raw response hash differs')
        return encoded['text']
    if encoded.get('encoding')!='review-json-refs-v1':raise ContractError('Unknown repair encoding')
    sources=_strings(context)
    def decode(value):
        if isinstance(value,dict) and MARKER in value:
            if set(value)!={MARKER,'start','end'} or value[MARKER] not in sources:raise ContractError('Invalid repair reference')
            source=sources[value[MARKER]];start=value['start'];end=value['end']
            if type(start) is not int or type(end) is not int or not 0<=start<end<=len(source):raise ContractError('Invalid repair reference range')
            return source[start:end]
        if isinstance(value,dict):return {key:decode(v) for key,v in value.items()}
        if isinstance(value,list):return [decode(v) for v in value]
        return copy.deepcopy(value)
    restored=decode(encoded['value'])
    if digest(canonical(restored))!=encoded['value_sha256']:raise ContractError('Previous JSON response hash differs')
    return restored
