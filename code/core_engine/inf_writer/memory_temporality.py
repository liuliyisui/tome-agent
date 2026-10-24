"""Evidence-linked expiry of individual portions, independent of storage tier.

Segmentation only supplies literal addressing units, not semantic judgments.
Models/callers must identify expired knowledge; no keyword or age expiry rule.
"""
import copy
import re

from .domain import ContractError, canonical, digest, fields, integer, text


def _recorded_chapter(row):
    sources = row.get('sources', [])
    if sources:
        return max(source['chapter_number'] for source in sources)
    legacy = row.get('legacy', {})
    source = legacy.get('fact', {}).get('source', {})
    claims = source.get('claim_sources', source.get('support', []))
    index = legacy.get('claim_index', 0)
    if index < len(claims) and 'chapter_number' in claims[index]:
        return claims[index]['chapter_number']
    return source.get('chapter_number')


def initialize(row):
    """Attach immutable original-text spans lazily; never rewrite source text."""
    if 'temporality' in row:
        return row
    parts = []
    for match in re.finditer(r'[^，,；;。！？!?\n、]+', row['claim']):
        if not match.group().strip():
            continue
        identifier = 'p_' + digest(canonical([row['id'], row['claim'], match.start(), match.end()]))[:16]
        parts.append(dict(id=identifier, text=match.group(), start=match.start(), end=match.end(),
                          scope='current', recorded_in_chapter=_recorded_chapter(row)))
    if not parts:
        raise ContractError('Memory has no addressable content')
    row['temporality'] = dict(version=1, parts=parts,
        note='Chapter numbers describe knowledge/evidence order, not world-event dates')
    return row


def annotated(row):
    return initialize(copy.deepcopy(row))


def current_parts(row):
    return [p for p in annotated(row)['temporality']['parts'] if p['scope']=='current']


def current_claim(row):
    item = annotated(row)
    parts = item['temporality']['parts']
    if all(p['scope']=='current' for p in parts):
        return row['claim']
    # Fragments remain literal extracts of the source claim. They are never
    # paraphrased into a stronger assertion by this code.
    return '；'.join(p['text'] for p in parts if p['scope']=='current')


def has_current_content(row):
    return bool(current_parts(row)) and row['status'] not in ('superseded', 'cancelled')


def time_view(row, include_historical=False):
    item = annotated(row)
    parts = item['temporality']['parts']
    live = [p for p in parts if p['scope']=='current']
    scope = 'current' if len(live)==len(parts) else 'mixed' if live else 'historical'
    return dict(time_scope=scope, current_parts=[dict(id=p['id'],text=p['text'],
        recorded_in_chapter=p.get('recorded_in_chapter')) for p in live],
        historical_parts=copy.deepcopy([p for p in parts if p['scope']=='historical']) if include_historical else [],
        historical_part_count=len(parts)-len(live),
        scope_note='A historical portion is an earlier belief/state, not a current fact; tier recall does not reactivate it')


def _reaches(memory, start, target, visited=None):
    if start==target:
        return True
    visited=set() if visited is None else visited
    if start in visited:
        return False
    visited.add(start)
    item=memory['items'][start]
    return any(_reaches(memory,next_id,target,visited) for part in annotated(item)['temporality']['parts']
               for next_id in part.get('replacement_ids',[]))


def reconcile(row, operation, memory, chapters):
    """Demote selected outdated portions to history; preserve unrelated parts.

    Literal binding and reference/time-order checks are mechanical. Whether
    new evidence actually supersedes an old belief needs semantic review.
    """
    from .tiered_memory import _sources
    fields(operation, ('op','id','expected_revision','reason','as_of_chapter','resolutions'))
    as_of = integer(operation['as_of_chapter'], 'as_of_chapter', 1)
    if as_of > len(chapters):
        raise ContractError('Future reconciliation chapter')
    resolutions=operation['resolutions']
    if not isinstance(resolutions,list) or not resolutions:
        raise ContractError('reconcile needs explicit resolutions, not silence or age')
    result=annotated(row)
    parts={part['id']:part for part in result['temporality']['parts']}
    touched=set()
    for resolution in resolutions:
        fields(resolution, ('part_ids','replacement_ids','relation','source_refs','reason'))
        if resolution['relation'] not in ('superseded','completed'):
            raise ContractError('Relation must be superseded or completed')
        # Completion describes the explicitly selected task portion, not the
        # container's kind. A report/event may contain an instruction too.
        # Only whole task rows receive task status/progress changes below.
        text(resolution['reason'],'resolution reason')
        ids=resolution['part_ids'];replacement_ids=resolution['replacement_ids']
        if not isinstance(ids,list) or not ids or any(not isinstance(i,str) for i in ids):
            raise ContractError('part_ids must be nonempty IDs')
        if not isinstance(replacement_ids,list) or not replacement_ids or any(not isinstance(i,str) for i in replacement_ids):
            raise ContractError('replacement_ids must be nonempty IDs')
        if len(set(replacement_ids))!=len(replacement_ids):
            raise ContractError('Duplicate replacement ID')
        sources=_sources(resolution['source_refs'],chapters)
        if any(s['chapter_number']!=as_of for s in sources):
            raise ContractError('Reconciliation needs evidence from its as_of chapter')
        for replacement_id in replacement_ids:
            replacement=memory['items'].get(replacement_id)
            if replacement is None or not has_current_content(replacement):
                raise ContractError('Replacement must be an existing current record')
            if _reaches(memory,replacement_id,row['id']):
                raise ContractError('Cyclic/self temporal replacement')
            if not replacement.get('sources'):
                raise ContractError('Replacement must have explicit bound evidence')
            if max(s['chapter_number'] for s in replacement['sources'])>as_of:
                raise ContractError('Cannot use future replacement knowledge')
        for identifier in ids:
            if identifier in touched or identifier not in parts:
                raise ContractError('Unknown or duplicate temporal part ID')
            touched.add(identifier)
            part=parts[identifier]
            if part['scope']!='current':
                raise ContractError('Temporal part is already historical')
            if part.get('recorded_in_chapter') is not None and part['recorded_in_chapter']>as_of:
                raise ContractError('Cannot expire knowledge using an earlier chapter')
            part.update(scope='historical',known_outdated_at_chapter=as_of,
                        replacement_ids=copy.deepcopy(replacement_ids),relation=resolution['relation'],
                        reason=resolution['reason'],change_sources=copy.deepcopy(sources))
    if row['kind']=='task':
        completed=[p for p in parts.values() if p.get('relation')=='completed']
        if completed:
            result['temporality']['task_progress']='partial' if current_parts(result) else 'completed'
            if not current_parts(result):
                result['status']='completed'
    if not current_parts(result) and result['tier']!='long':
        result['tier']={'working':'recent','recent':'long'}[result['tier']]
    return result


def reset_after_update(row):
    """Old annotations stay in archived row; a new value gets new span IDs."""
    row.pop('temporality',None)
    return initialize(row)
