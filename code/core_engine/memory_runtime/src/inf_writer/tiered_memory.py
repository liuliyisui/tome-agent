"""Opt-in, item-based memory. Tier changes never erase a record or its sources.

Storage has no per-attribute claim count limit. Wire contexts remain bounded.
Source matching is mechanical provenance validation, NOT semantic certification.
"""
import copy
import hashlib
import json
import re

from .domain import ContractError, Snapshot, canonical, digest, evidence_segments, fields, integer, text
from .memory_temporality import (initialize, current_claim, has_current_content,
                                time_view, reconcile, reset_after_update)

TIERS = ('working', 'recent', 'long')
KINDS = ('state', 'event', 'knowledge', 'task', 'prose_excerpt', 'legacy')
STATES = ('active', 'superseded', 'planned', 'completed', 'cancelled')


def empty_memory():
    return dict(schema_version='tiered-memory-v2-temporal', revision=0, items={}, receipts={},
                history=[], processed_through=0)


def _sources(source_refs, chapters):
    if not isinstance(source_refs, list) or not source_refs:
        raise ContractError('Changed information requires source_refs')
    result = []
    for ref in source_refs:
        fields(ref, ('chapter_number', 'evidence_id'))
        n = integer(ref['chapter_number'], 'source chapter', 1)
        if n > len(chapters):
            raise ContractError('Future/missing source chapter')
        draft = chapters[n-1]['text']
        catalog = {r['id']: r['text'] for r in evidence_segments(draft)}
        if not isinstance(ref['evidence_id'], str) or ref['evidence_id'] not in catalog:
            raise ContractError('Unknown source evidence_id')
        result.append(dict(ref, chapter_sha256=digest(draft), quote=catalog[ref['evidence_id']]))
    return result


def _identity(subject, attribute):
    text(subject, 'subject')
    if not isinstance(attribute, str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,63}', attribute):
        raise ContractError('attribute must be snake_case')
    return subject, attribute


def _status(kind, status):
    if kind not in KINDS or status not in STATES:
        raise ContractError('Unknown memory kind/status')
    if kind == 'task' and status not in ('planned', 'completed', 'cancelled'):
        raise ContractError('Tasks require planned/completed/cancelled status')
    if kind != 'task' and status not in ('active', 'superseded'):
        raise ContractError('Only tasks use task statuses')


def import_snapshot(snapshot):
    """Lossless import of legacy claims; do not guess their semantic kind.

    Each original fact and its complete provenance remain attached. Old receipts
    are NOT interpreted as extraction coverage of failed chapters.
    """
    snapshot = Snapshot.from_dict(snapshot).to_dict()
    memory = empty_memory()
    facts = snapshot['facts']
    for key, fact in (facts.items() if isinstance(facts, dict) else enumerate(facts)):
        claims = fact['value'] if isinstance(fact['value'], list) else [fact['value']]
        for index, claim in enumerate(claims):
            identifier = 'legacy_' + digest(canonical([key, index]))[:24]
            memory['items'][identifier] = dict(id=identifier, subject=fact['subject'],
                attribute=fact['attribute'], claim=copy.deepcopy(claim), kind='legacy',
                status='active' if fact['status'] == 'active' else 'superseded',
                tier='recent', revision=1, sources=[],
                legacy=dict(fact=copy.deepcopy(fact), claim_index=index))
    memory['legacy_history'] = copy.deepcopy(snapshot.get('history', []))
    memory['legacy_fact_count'] = len(facts)
    return memory


def _add(memory, operation, chapters,transaction_id=None,index=None):
    fields(operation, ('op', 'subject', 'attribute', 'claim', 'kind', 'status', 'source_refs'))
    subject, attribute = _identity(operation['subject'], operation['attribute'])
    claim = text(operation['claim'], 'claim')
    _status(operation['kind'], operation['status'])
    if operation['kind'] == 'legacy':
        raise ContractError('legacy kind is import-only')
    sources = _sources(operation['source_refs'], chapters)
    duplicate=next((r for r in memory['items'].values() if
        (r['subject'],r['attribute'],r['claim'],r['kind'],r['status'])==
        (subject,attribute,claim,operation['kind'],operation['status'])),None)
    if duplicate is not None:
        memory.setdefault('no_change_observations',[]).append(dict(id=duplicate['id'],op='add',
            transaction_id=transaction_id,index=index,sources=sources,disposition='Exact duplicate; original record retained'))
        return duplicate['id']
    if operation['kind'] == 'state' and operation['status'] == 'active' and any(
            r['kind'] == 'state' and r['status'] == 'active' and has_current_content(r) and
            (r['subject'], r['attribute']) == (subject, attribute) for r in memory['items'].values()):
        raise ContractError('Current state already exists; update its ID')
    identifier = 'm_' + digest(canonical([subject, attribute, claim, operation['kind'], sources]))[:24]
    if identifier in memory['items']:
        raise ContractError('Memory ID collision')
    memory['items'][identifier] = dict(id=identifier, subject=subject, attribute=attribute,
        claim=claim, kind=operation['kind'], status=operation['status'], tier='working',
        revision=1, sources=sources)
    return identifier


def apply_delta(memory, result, chapters, transaction_id):
    """Atomic delta against stable item IDs. Omitted old items are unchanged."""
    fields(result, ('changes',), ('no_change_reason',))
    if not isinstance(result['changes'], list):
        raise ContractError('changes must be a list')
    if not result['changes']:
        text(result.get('no_change_reason'), 'Empty delta requires no_change_reason')
    text(transaction_id, 'transaction_id')
    signature = digest(canonical(result))
    previous = memory['receipts'].get(transaction_id)
    if previous:
        if previous['signature'] != signature:
            raise ContractError('Transaction ID reused with different delta')
        return copy.deepcopy(memory)
    candidate = copy.deepcopy(memory)
    candidate['schema_version']='tiered-memory-v2-temporal'
    touched = set()
    for index, operation in enumerate(result['changes']):
        try:
            if not isinstance(operation, dict):
                raise ContractError('Operation must be an object')
            action = operation.get('op')
            if action == 'add':
                _add(candidate, operation, chapters,transaction_id,index)
                continue
            base = ('op', 'id', 'expected_revision', 'reason')
            if action == 'update':
                # Real-model submissions may echo the immutable kind. Accept
                # only an exact identity match after resolving the item below.
                fields(operation, base + ('claim', 'status', 'source_refs'), ('kind',))
            elif action in ('demote', 'recall'):
                fields(operation, base)
            elif action == 'reconcile':
                fields(operation,base+('as_of_chapter','resolutions'))
            else:
                raise ContractError('Use add/update/demote/recall/reconcile; deletion is not supported')
            identifier = text(operation['id'], 'id')
            if identifier in touched:
                raise ContractError('One operation per existing item per transaction')
            touched.add(identifier)
            old = candidate['items'].get(identifier)
            if old is None:
                raise ContractError('Unknown item ID')
            if action == 'update' and 'kind' in operation and operation['kind'] != old['kind']:
                raise ContractError('Update kind must match original item; reclassification is not implicit')
            revision = integer(operation['expected_revision'], 'expected_revision', 1)
            if revision != old['revision']:
                raise ContractError(f'Stale item revision; current={old["revision"]}')
            text(operation['reason'], 'reason')
            row = copy.deepcopy(old)
            if action == 'update':
                row['claim'] = text(operation['claim'], 'claim')
                row['status'] = operation['status']
                _status(row['kind'], row['status'])
                sources = _sources(operation['source_refs'], chapters)
                if (row['claim'], row['status']) == (old['claim'], old['status']):
                    candidate.setdefault('no_change_observations',[]).append(dict(id=identifier,op='update',
                        transaction_id=transaction_id,index=index,sources=sources,
                        disposition='Exact no-op; original record/revision/tier retained'))
                    touched.remove(identifier)
                    continue
                row['sources'] = sources
                row['tier'] = 'working'
                reset_after_update(row)
            elif action == 'reconcile':
                row = reconcile(old,operation,candidate,chapters)
            elif action == 'demote':
                if old['tier'] == 'long':
                    raise ContractError('Already in long-term memory')
                row['tier'] = TIERS[TIERS.index(old['tier']) + 1]
            else:
                if old['tier'] == 'working':
                    raise ContractError('Already in working memory')
                row['tier'] = 'working'
            row['revision'] += 1
            candidate['history'].append(dict(item=copy.deepcopy(old), reason=operation['reason'],
                                             transaction_id=transaction_id))
            candidate['items'][identifier] = row
        except ContractError as exc:
            raise ContractError(f'changes[{index}]: {exc}') from exc
    active_states = set()
    for row in candidate['items'].values():
        if row['kind'] == 'state' and row['status'] == 'active' and has_current_content(row):
            key = (row['subject'], row['attribute'])
            if key in active_states:
                raise ContractError('Multiple active values for the same current-state property')
            active_states.add(key)
    candidate['revision'] += 1
    candidate['receipts'][transaction_id] = dict(signature=signature)
    return candidate


def wire_item(item, include_historical=False):
    result={k: copy.deepcopy(item[k]) for k in
            ('id', 'subject', 'attribute', 'claim', 'kind', 'status', 'tier', 'revision')}
    result['temporality']=time_view(item,include_historical)
    if 'provenance_scope' in item:result['provenance_scope']=item['provenance_scope']
    if not include_historical or result['temporality']['time_scope']!='historical':
        result['claim']=current_claim(item)
    return result


def select_context(memory, *, query='', subjects=(), required_ids=(), max_bytes=48000,
                   include_historical=False):
    """Deterministic lexical baseline, with explicit omissions and forced IDs.

    Working items and explicit IDs must fit or fail. Recent/long items compete
    by query relevance. Stored provenance/history is never truncated/deleted.
    Superseded/completed items remain retrievable for event reconstruction.
    """
    integer(max_bytes, 'max_bytes', 1)
    terms = set(re.findall(r'[a-z0-9_]+|[\u3400-\u9fff]{2}', query.lower()))
    subjects = tuple(subjects)
    required = set(required_ids)
    if required - memory['items'].keys():
        raise ContractError('Unknown required memory ID')
    forced, ranked = [], []
    for identifier, item in memory['items'].items():
        if not has_current_content(item) and not include_historical:
            if identifier in required:
                raise ContractError('Required record is historical; request include_historical explicitly')
            continue
        row = wire_item(item,include_historical)
        hay = canonical(row).lower()
        score = sum(term in hay for term in terms) + 5 * sum(s == item['subject'] for s in subjects)
        if identifier in required or item['tier'] == 'working':
            forced.append(row)
        elif item['tier'] == 'recent' or score:
            ranked.append((score, item['tier'] == 'recent', identifier, row))
    selected = sorted(forced, key=lambda r: r['id'])
    if len(canonical(selected).encode('utf-8')) > max_bytes:
        raise ContractError('Required/working memory exceeds wire budget; demote or increase explicit budget')
    for _, _, _, row in sorted(ranked, key=lambda r: (-r[0], -r[1], r[2])):
        if len(canonical(selected + [row]).encode('utf-8')) <= max_bytes:
            selected.append(row)
    ids = {r['id'] for r in selected}
    return dict(items=selected, selected_ids=sorted(ids),
                omitted_ids=sorted(set(memory['items']) - ids),
                bytes=len(canonical(selected).encode('utf-8')), budget_bytes=max_bytes,
                retrieval='lexical-baseline-not-semantic-completeness',
                storage_revision=memory['revision'])


def legacy_projection(selection):
    """One item per factual reference; no re-aggregation into capped attributes."""
    return [dict(subject=r['subject'], attribute=r['attribute'], value=r['claim'],
                 revision=r['revision'], status='active', memory_id=r['id'],
                 kind=r['kind'], memory_status=r['status'], tier=r['tier'],
                 temporal_scope=r.get('temporality',{}).get('time_scope','current'),
                 **({'provenance_scope':r['provenance_scope']} if 'provenance_scope' in r else {}))
            for r in selection['items'] if r['status'] not in ('superseded', 'cancelled')
            and r.get('temporality',{}).get('time_scope')!='historical']


def select_history_context(memory, *, query='', max_bytes=12000):
    """Retrieve explicitly labelled old portions without restoring authority.

    This is an additional view of the same three-tier store, not a fourth bank.
    It is optional narrative evidence, never projected into active_facts.
    """
    integer(max_bytes,'history max_bytes',1)
    terms=set(re.findall(r'[a-z0-9_]+|[\u3400-\u9fff]{2}',query.lower()))
    ranked=[]
    for identifier,item in memory['items'].items():
        view=time_view(item,include_historical=True)
        old=view['historical_parts']
        if not old:continue
        row=dict(memory_id=identifier,subject=item['subject'],attribute=item['attribute'],
            tier=item['tier'],time_scope='historical_only',original_claim=item['claim'],
            historical_parts=old,
            use_rule='Earlier statements/knowledge only; do not use as current state or negate later valid changes')
        score=sum(term in canonical(row).lower() for term in terms)
        if score or not terms:ranked.append((score,identifier,row))
    snapshots=set()
    for entry in reversed(memory.get('history',[])):
        old=entry['item'];current=memory['items'][old['id']]
        # Tier-only revisions are not new historical states. Keep a distinct
        # prior content/status version, not one copy for every tier move.
        if (old['claim'],old['status'])==(current['claim'],current['status']):continue
        key=(old['id'],old['claim'],old['status'])
        if key in snapshots:continue
        snapshots.add(key)
        row=dict(memory_id=old['id'],memory_revision=old['revision'],subject=old['subject'],
            attribute=old['attribute'],tier=old['tier'],time_scope='historical_snapshot',
            original_claim=old['claim'],old_status=old['status'],archived_reason=entry['reason'],
            source_chapters=sorted({s['chapter_number'] for s in old.get('sources',[])}),
            use_rule='Archived prior version, not current state; consult current record for latest value')
        score=sum(term in canonical(row).lower() for term in terms)
        if score or not terms:ranked.append((score,old['id']+'@'+str(old['revision']),row))
    selected=[];omitted=[]
    for _,identifier,row in sorted(ranked,key=lambda r:(-r[0],r[1])):
        if len(canonical(selected+[row]).encode('utf-8'))<=max_bytes:selected.append(row)
        else:omitted.append(identifier)
    return dict(items=selected,omitted_ids=omitted,bytes=len(canonical(selected).encode('utf-8')),
                budget_bytes=max_bytes,use_rule='Historical context, never current factual authority')


def extraction_payload(memory, chapters, chapter_number, selection):
    integer(chapter_number, 'chapter_number', 1)
    if chapter_number > len(chapters):
        raise ContractError('Missing extraction chapter')
    chapter = chapters[chapter_number-1]
    return dict(chapter_number=chapter_number, current_draft=chapter['text'],
                evidence_segments=evidence_segments(chapter['text']), memory_items=selection['items'],
                memory_coverage=dict(omitted_ids=selection['omitted_ids'],
                                     processed_through=memory['processed_through']),
                memory_contract=dict(operations=['add', 'update', 'demote', 'recall'],
                    tiers=list(TIERS), kinds=list(KINDS[:-1]),
                    add_fields=['op','subject','attribute','claim','kind','status','source_refs'],
                    update_fields=['op','id','expected_revision','reason','claim','status','source_refs'],
                    tier_change_fields=['op','id','expected_revision','reason'],
                    source_ref_fields=['chapter_number','evidence_id']))
