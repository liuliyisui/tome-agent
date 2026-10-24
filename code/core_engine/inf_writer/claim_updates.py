"""Copy-only incremental claims. Old sources are carried by code, never invented by a model."""
import copy
from .domain import ContractError, ConflictError, Snapshot, checked_support, fields, identity, integer, text, digest


def validate_claim_sources(sources, chapters, anchor_number):
    if not isinstance(sources, list) or not 1 <= len(sources) <= 16:
        raise ContractError('claim_sources requires 1..16 claims')
    labels = set()
    for row in sources:
        fields(row, ('claim','evidence','chapter_number','chapter_sha256'))
        label = text(row['claim'], 'claim')
        if label in labels: raise ContractError('Duplicate inherited claim')
        labels.add(label)
        n = integer(row['chapter_number'], 'claim source chapter', 1)
        if n > anchor_number or n > len(chapters): raise ContractError('Future/missing claim source')
        chapter = chapters[n-1]
        if row['chapter_sha256'] != chapter['sha256']: raise ContractError('Claim chapter hash mismatch')
        checked_support([dict(claim=label,evidence=row['evidence'])], chapter['text'], label, resolved=True)


def resolve_patch(entry, state, draft, prepared=False):
    """All indices refer to the same input fact; no partial mutation or implicit deletes."""
    required = ('action','subject','attribute','expected_revision','reason','claim_ops')
    fields(entry, required, ('value','support','removals') if prepared else ())
    if prepared and not all(k in entry for k in ('value','support','removals')):
        raise ContractError('Prepared patch requires complete derived fields')
    checked = Snapshot.from_dict(state.to_dict())
    old = checked.facts.get(identity(entry['subject'],entry['attribute']))
    if entry['action'] != 'update' or old is None or old['status'] != 'active':
        raise ContractError('claim_ops requires update of an existing active fact')
    integer(entry['expected_revision'], 'expected_revision', 1)
    if old['revision'] != entry['expected_revision']: raise ConflictError('Stale fact revision for claim_ops')
    text(entry['reason'], 'reason')
    source = old['source']
    if 'claim_sources' in source:
        original = copy.deepcopy(source['claim_sources'])
    elif 'support' in source:
        original = [dict(copy.deepcopy(row), chapter_number=source['chapter_number'], chapter_sha256=source['chapter_sha256'])
                    for row in source['support']]
    else:
        raise ContractError('Legacy quote-only fact has no explicit subclaims; do not silently split it')
    operations = entry['claim_ops']
    if not isinstance(operations,list) or not 1 <= len(operations) <= 32:
        raise ContractError('claim_ops requires 1..32 operations')
    edits, additions, removals = {}, [], []
    number, sha = len(checked.chapters)+1, digest(text(draft,'draft'))
    for operation in operations:
        if not isinstance(operation,dict): raise ContractError('Claim operation must be an object')
        kind = operation.get('op')
        if kind == 'add':
            fields(operation, ('op','claim','evidence'))
        elif kind in ('replace','remove','retain'):
            fields(operation, ('op','index','old_claim','evidence','claim') if kind=='replace'
                   else ('op','index','old_claim','reason') if kind=='retain'
                   else ('op','index','old_claim','evidence','reason'))
            index = integer(operation['index'], 'claim index', 0)
            if index >= len(original) or index in edits: raise ContractError('Claim index missing or targeted more than once')
            if operation['old_claim'] != original[index]['claim']: raise ConflictError('old_claim differs from original indexed claim')
        else: raise ContractError('Unknown claim op')
        if kind=='retain':
            text(operation['reason'],'retention reason')
            edits[index]=copy.deepcopy(original[index])
            continue  # Keep exact original evidence/chapter; no invented new source.
        label = text(operation['old_claim'] if kind=='remove' else operation['claim'], 'claim')
        evidence = checked_support([dict(claim=label,evidence=operation['evidence'])],draft,label)[0]['evidence']
        item = dict(claim=label,evidence=evidence,chapter_number=number,chapter_sha256=sha)
        if kind=='add': additions.append(item)
        elif kind=='replace':
            if label == original[index]['claim']: raise ContractError('Unchanged claim does not need replace')
            edits[index] = item
        else:
            edits[index] = None
            removals.append(dict(item,reason=text(operation['reason'],'removal reason')))
    # Iterate original slots, not operation order; untouched sources are exact deep copies.
    support = [copy.deepcopy(edits.get(i,row)) for i,row in enumerate(original) if edits.get(i,row) is not None] + additions
    labels = [row['claim'] for row in support]
    if not 1 <= len(labels) <= 16: raise ContractError('Keep 1..16 final claims; use explicit retire to remove the entire fact')
    if len(set(labels)) != len(labels): raise ContractError('Duplicate final claims')
    result = {key:copy.deepcopy(entry[key]) for key in required}
    result.update(value=labels,support=support,removals=removals)
    if prepared and any(entry[key] != result[key] for key in ('value','support','removals')):
        raise ContractError('Derived patch fields differ from trusted recomputation')
    return result
