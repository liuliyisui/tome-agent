"""Isolated four-role session with durable, ordered memory catch-up.

Uses the existing planner/writer/reviewer interfaces; opt-in only. Each chapter
is a new complete checkpoint. No legacy store/schema/launcher is changed.
"""
import copy
from pathlib import Path

from .domain import ContractError, canonical, digest, evidence_segments, strict_json, fields, text
from .models import ModelRequest
from .tiered_memory import (empty_memory, import_snapshot, apply_delta, select_context,
                           extraction_payload, legacy_projection,select_history_context)

MEMORY_SYSTEM = (
    '你是三层记忆维护智能体。只输出JSON changes数组，可附no_change_reason。'
    '只提交变化；未提及的旧条目由程序保留，不重抄旧信息，不输出retain。'
    '按memory_contract格式新增add、更新update、降级demote或调回recall。'
    'state当前状态、event历史事件、knowledge人物所知、task任务分开。'
    'state/event/knowledge使用active或superseded；task用planned/completed/cancelled。'
    '完成任务update为completed，保留事件；不删除历史。'
    'demote逐级working→recent→long，仅改变层级，不改事实；recall调回working。'
    '更新引用稳定id和expected_revision，不回显旧句。新/改信息必须给本章source_refs，'
    '每项chapter_number和evidence_id由输入选取。不存在于当前选择不代表全库不存在；'
    '需要未提供旧记录时返回明确限制，不编造ID。'
    '语义上相同的新旧信息不得重复存；空changes需说明原因。'
)


def new_book(goal, constraints):
    return dict(schema_version='tiered-book-v2-temporal', goal=goal, constraints=copy.deepcopy(constraints),
                chapters=[], plan={}, memory=empty_memory(), pending=[], outcomes=[])


def resume_book(snapshot):
    book = new_book(snapshot['goal'], snapshot['constraints'])
    book.update(chapters=copy.deepcopy(snapshot['chapters']), plan=copy.deepcopy(snapshot['plan']),
                memory=import_snapshot(snapshot))
    # Import alone proves no semantic coverage; caller must establish the
    # starting checkpoint, otherwise all old prose is queued for extraction.
    book['pending'] = list(range(1, len(book['chapters'])+1))
    return book


class TieredMemoryAgent:
    role = 'memory'
    def __init__(self, gateway, max_input_bytes=120000, max_output_tokens=8192):
        self.gateway = gateway
        self.max_input_bytes = max_input_bytes
        self.max_output_tokens = max_output_tokens

    def extract(self, memory, chapters, number, selection, trace):
        payload = extraction_payload(memory, chapters, number, selection)
        for attempt in range(2):
            size = len(canonical(dict(system=MEMORY_SYSTEM, payload=payload)).encode('utf-8'))
            if size > self.max_input_bytes:
                raise ContractError(f'Memory input exceeds bound: {size}>{self.max_input_bytes}')
            entry = dict(role='memory', attempt=attempt+1, chapter_number=number, input_bytes=size)
            trace.append(entry)
            # Transport errors propagate; no automatic network retry.
            reply = self.gateway.complete(ModelRequest('memory', MEMORY_SYSTEM, copy.deepcopy(payload), self.max_output_tokens))
            entry['raw_output'] = reply.content
            try:
                result = strict_json(reply.content)
                # Current-chapter source restriction is deliberate; catch-up
                # processes old chapters in order rather than inventing sources.
                for operation in result.get('changes', []):
                    for ref in operation.get('source_refs', []):
                        if ref.get('chapter_number') != number:
                            raise ContractError('Use only this extraction chapter as source')
                candidate = apply_delta(memory, result, chapters, f'chapter-memory-{number}')
                entry['status'] = 'ACCEPTED'
                candidate['processed_through'] = number
                return candidate
            except (ContractError, AttributeError, TypeError) as exc:
                entry.update(status='REJECTED', error=str(exc))
                if attempt:
                    raise ContractError(str(exc)) from exc
                payload['repair'] = dict(error=str(exc), previous_output=reply.content,
                    instruction='只修提案；完整返回changes。不改正文，不用省略全部变化逃避错误。')


class TieredDraftSession:
    def __init__(self, output, book, agents, *, memory_bytes=48000, context_bytes=96000,history_bytes=12000):
        self.output = Path(output)
        self.book = copy.deepcopy(book)
        self.agents = agents
        if set(agents) != {'planner', 'writer', 'memory', 'reviewer'}:
            raise ContractError('Four role agents required')
        self.memory_bytes, self.context_bytes = memory_bytes, context_bytes
        self.history_bytes=history_bytes
        self.serial = 0
        if self.output.exists():
            raise ContractError('Use a new isolated output directory')
        self.output.mkdir(parents=True)

    def _save(self, trace, reason):
        self.serial += 1
        record = dict(book=self.book, trace=trace, reason=reason,
                      memory_semantic_review='NOT_CERTIFIED')
        path = self.output / f'checkpoint_{self.serial:04d}.json'
        # Exclusive checkpoint creation: failures never overwrite prior state.
        with path.open('x', encoding='utf-8') as stream:
            stream.write(canonical(record))

    def _selection(self, query, required_ids=(), subjects=()):
        return select_context(self.book['memory'], query=query, subjects=subjects,
                              required_ids=required_ids, max_bytes=self.memory_bytes)

    def catch_up(self, trace):
        while self.book['pending']:
            number = self.book['pending'][0]
            if number != self.book['memory']['processed_through'] + 1:
                raise ContractError('Memory coverage gap; replay pending chapters in order')
            chapter = self.book['chapters'][number-1]
            selection = self._selection(chapter['text'])
            memory = self.agents['memory'].extract(self.book['memory'], self.book['chapters'], number, selection, trace)
            self.book['memory'] = memory
            self.book['pending'].pop(0)

    def maintain(self, operations, transaction_id):
        """Explicit, journaled tier changes at scene/arc boundaries; never erase."""
        if any(op.get('op') not in ('demote', 'recall') for op in operations):
            raise ContractError('Maintenance accepts tier changes only')
        self.book['memory'] = apply_delta(self.book['memory'], dict(changes=operations),
                                          self.book['chapters'], transaction_id)
        self._save([], 'TIER_MAINTENANCE')

    def finish_segment(self, segment_id):
        """Explicit scene/arc boundary. Recent -> long, current working stays.

        Boundary detection is caller-controlled; age alone is not proof that a
        plot thread is complete. Repeating the same boundary is idempotent.
        """
        transaction_id = 'segment-' + text(segment_id, 'segment_id')
        if transaction_id in self.book['memory']['receipts']:
            return
        operations = [dict(op='demote', id=r['id'], expected_revision=r['revision'],
                           reason='Scene/arc boundary: '+segment_id)
                      for r in self.book['memory']['items'].values() if r['tier']=='recent']
        if operations:
            self.maintain(operations, transaction_id)

    def _advance_working(self, number, required_ids):
        operations = [dict(op='demote', id=r['id'], expected_revision=r['revision'],
                           reason=f'Chapter {number} working-set rotation')
                      for r in self.book['memory']['items'].values()
                      if r['tier']=='working' and r['id'] not in required_ids]
        if operations:
            self.maintain(operations, f'working-rotation-{number}-'+digest(canonical(operations))[:12])

    def write_next(self, instruction, *, required_ids=(), subjects=()):
        trace = []
        try:
            self.catch_up(trace)
        except Exception as exc:
            self._save(trace, 'MEMORY_BLOCKED')
            return dict(status='MEMORY_BLOCKED', error=str(exc), pending=copy.deepcopy(self.book['pending']))
        number = len(self.book['chapters']) + 1
        row = dict(chapter_number=number, status='NO_DRAFT', errors=[])
        try:
            self._advance_working(number, required_ids)
            selection = self._selection(instruction, required_ids, subjects)
            context = dict(goal=self.book['goal'], constraints=self.book['constraints'],
                chapter_number=number, instruction=instruction, checkpoint_revision=number-1,
                recent_chapters=self.book['chapters'][-2:],
                planned_next_chapters=[v for k,v in self.book['plan'].items() if int(k)>=number],
                active_facts=legacy_projection(selection), tiered_memory=selection,
                historical_memory=select_history_context(self.book['memory'],query=instruction,max_bytes=self.history_bytes),
                unresolved_chapters=[r['chapter_number'] for r in self.book['outcomes'] if r['status']!='DRAFT_CHECKED'],
                fact_bank_status='Mechanically extracted; semantic correctness not certified',
                context_policy=dict(older_prose_omitted=max(0,number-3), history_included=False))
            self._bound(context)
            plan = self.agents['planner'].run(context, trace)
            fields(plan, ('number','title','brief','future_updates'))
            if plan['number'] != number:
                raise ContractError('Planner must address next chapter')
            seen = set()
            for future in plan['future_updates']:
                fields(future, ('number','title','brief'))
                if type(future['number']) is not int or future['number'] <= number or future['number'] in seen:
                    raise ContractError('Future plan may only update distinct unwritten chapters')
                seen.add(future['number'])
            context['chapter_plan'] = plan
            self._bound(context)
            draft = self.agents['writer'].run(context, trace)['text']
            text(draft, 'draft')
            chapter = dict(number=number, title=plan['title'], text=draft, sha256=digest(draft))
            self.book['chapters'].append(chapter)
            self.book['pending'].append(number)
            for future in plan['future_updates']:
                self.book['plan'][str(future['number'])] = copy.deepcopy(future)
            # Persist raw prose and pending work BEFORE extraction/review.
            self._save(trace, 'DRAFT_SAVED_MEMORY_PENDING')
            try:
                self.catch_up(trace)
            except Exception as exc:
                row.update(status='DRAFT_UNCHECKED', memory_update_status='PENDING')
                row['errors'].append('memory: '+str(exc))
                self.book['outcomes'].append(row)
                self._save(trace, 'MEMORY_PENDING')
                return row
            # Audit against updated memory, not the pre-chapter snapshot.
            review_selection = self._selection(instruction+' '+draft, required_ids, subjects)
            review_context = dict(context, active_facts=legacy_projection(review_selection),
                current_draft=draft, evidence_segments=evidence_segments(draft), memory_changes=[],
                historical_memory=select_history_context(self.book['memory'],query=instruction+' '+draft,max_bytes=self.history_bytes),
                memory_no_change_reason='Incremental memory already committed; not semantic certification')
            refs = {f'constraint_{i}': rule for i,rule in enumerate(self.book['constraints'],1)}
            refs.update({f'fact_{i}':canonical(f) for i,f in enumerate(review_context['active_facts'],1)})
            refs.update({f'draft_{s["id"]}':s['text'] for s in evidence_segments(draft)})
            refs.update({f'past_{c["number"]}':c['text'] for c in context['recent_chapters']})
            # Existing reviewer transport permits past_ references. The value
            # retains explicit historical-only labels and the replacement link.
            refs.update({f'past_memory_{i}':canonical(item) for i,item in enumerate(review_context['historical_memory']['items'],1)})
            review_context['hard_references'] = refs
            self._bound(review_context)
            review = self.agents['reviewer'].run(review_context, trace)
            row.update(status='DRAFT_CHECKED' if review['approved'] else 'DRAFT_UNCHECKED',
                       memory_update_status='APPLIED', review=review)
        except Exception as exc:
            row['errors'].append(str(exc))
            if len(self.book['chapters']) >= number:
                row.update(status='DRAFT_UNCHECKED', memory_update_status='PENDING' if number in self.book['pending'] else 'APPLIED')
        self.book['outcomes'].append(row)
        self._save(trace, row['status'])
        return row

    def _bound(self, context):
        size = len(canonical(context).encode('utf-8'))
        if size > self.context_bytes:
            raise ContractError(f'Context exceeds bound: {size}>{self.context_bytes}; no silent truncation')


def build_tiered_agents(gateway, temporal_reconciliation=True):
    from .light_memory import build_light_agents
    agents = build_light_agents(gateway, compact_narrative=True)
    if type(temporal_reconciliation) is not bool:
        raise ContractError('temporal_reconciliation must be boolean')
    if temporal_reconciliation:
        from .temporal_agent import TemporalMemoryAgent
        agents['memory']=TemporalMemoryAgent(gateway)
    else:
        agents['memory'] = TieredMemoryAgent(gateway)
    return agents
