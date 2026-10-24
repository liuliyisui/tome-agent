"""Request-local short references. Exact mappings only, never fuzzy ID repair."""
import copy

from .domain import ContractError


def encode(payload):
    wire=copy.deepcopy(payload);items={};parts={}
    for field in ('candidate_items','changed_items'):
        for row in wire[field]:
            stable=row['id']
            alias=next((a for a,s in items.items() if s==stable),None)
            if alias is None:
                alias=f'r{len(items)+1:03d}';items[alias]=stable
            row['id']=alias
            for part in row['temporality']['current_parts']:
                stable_part=part['id']
                alias_part=next((a for a,s in parts.items() if s==stable_part),None)
                if alias_part is None:
                    alias_part=f's{len(parts)+1:03d}';parts[alias_part]=stable_part
                part['id']=alias_part
    wire['reference_policy']=dict(item_ids='request-local rNNN',part_ids='request-local sNNN',
        instruction='Use the supplied short IDs exactly; do not invent stable hashes or infer missing IDs')
    return wire,dict(items=items,parts=parts)


def decode(result,bindings):
    normalized=copy.deepcopy(result)
    def resolve(identifier,group):
        if not isinstance(identifier,str):raise ContractError('Reference must be a string')
        mapping=bindings[group]
        if identifier in mapping:return mapping[identifier]
        # Exact canonical IDs are allowed for old recorded/local fixtures, only
        # if that very ID belonged to this request. No typo correction.
        if identifier in mapping.values():return identifier
        raise ContractError(f'Unknown {group} reference {identifier!r}; select an ID supplied in this request')
    def ids(values,group):
        if not isinstance(values,list):raise ContractError('References must be a list')
        return [resolve(i,group) for i in values]
    normalized['checked_ids']=ids(normalized.get('checked_ids'),'items')
    if not isinstance(normalized.get('changes'),list):raise ContractError('changes must be list')
    for operation in normalized['changes']:
        if not isinstance(operation,dict):raise ContractError('Operation must be an object')
        operation['id']=resolve(operation.get('id'),'items')
        if not isinstance(operation.get('resolutions'),list):raise ContractError('resolutions must be list')
        for resolution in operation['resolutions']:
            resolution['part_ids']=ids(resolution.get('part_ids'),'parts')
            resolution['replacement_ids']=ids(resolution.get('replacement_ids'),'items')
    for issue in normalized.get('unresolved',[]):
        issue['id']=resolve(issue.get('id'),'items')
        issue['part_ids']=ids(issue.get('part_ids'),'parts')
    return normalized
