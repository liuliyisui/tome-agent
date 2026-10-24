"""User-operated draft writing. Usage is recorded, not budget-gated.

The frozen research trial and its caps are deliberately left unchanged.
Imports require the source path selected by write_novel.py.
"""
import copy
import math
from pathlib import Path
import re
import time
from memory_runtime.writing import WritingSession
from inf_writer.domain import ContractError, digest, integer, text
from inf_writer.memory_temporality import has_current_content
from inf_writer.models import ModelReply
from inf_writer.trial import RecordedProvider, save_new

class MeteredGateway:
    def __init__(self,provider):
        self.provider=provider
        self.calls=self.input_tokens=self.output_tokens=0
        self.cost_usd=0.0
        self.story_review_usage=dict(attempted_calls=0,successful_calls=0,failed_calls=0,
            input_tokens=0,output_tokens=0,cost_usd_estimate_not_bill=0.0,elapsed_seconds=0.0)
    def complete(self,request):
        integer(request.max_output_tokens,'max_output_tokens',1)
        self.calls+=1
        is_story_review=request.role=='reviewer' and (request.payload.get('review_mode')=='light_memory' or request.payload.get('issue_consistency_review') is True)
        started=time.monotonic()
        if is_story_review:self.story_review_usage['attempted_calls']+=1
        try:reply=self.provider.complete(copy.deepcopy(request))
        except BaseException:
            if is_story_review:self.story_review_usage['failed_calls']+=1
            raise
        finally:
            if is_story_review:self.story_review_usage['elapsed_seconds']+=time.monotonic()-started
        if not isinstance(reply,ModelReply):raise ContractError('Provider must return ModelReply with usage')
        integer(reply.input_tokens,'input_tokens');integer(reply.output_tokens,'output_tokens')
        if type(reply.cost_usd) not in (int,float) or not math.isfinite(reply.cost_usd) or reply.cost_usd<0:
            raise ContractError('Missing/invalid provider cost estimate')
        self.input_tokens+=reply.input_tokens;self.output_tokens+=reply.output_tokens;self.cost_usd+=reply.cost_usd
        if reply.output_tokens>request.max_output_tokens:raise ContractError('Provider exceeded output limit')
        text(reply.content,'model content')
        if is_story_review:
            self.story_review_usage['successful_calls']+=1
            self.story_review_usage['input_tokens']+=reply.input_tokens
            self.story_review_usage['output_tokens']+=reply.output_tokens
            self.story_review_usage['cost_usd_estimate_not_bill']+=reply.cost_usd
        return reply

def run_draft_trial(output,provider,plan,*,resume_book=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    save_new(output/'execution.json',dict(execution_mode='draft_first',budget_limits=None,
        authorization='User-operated direct command',network_retries=0,
        review_mode='tiered_memory',memory_update_policy='defer_failures_continue_writing',
        writing_mode='event_first' if plan.get('event_first',True) else 'legacy_prose_first',
        story_review_failure_policy='defer_failures_continue_writing',
        resumed=resume_book is not None))
    recorder=RecordedProvider(provider,output);meter=MeteredGateway(recorder)
    session=WritingSession(output/'working',meter,plan,book=resume_book)
    started=time.monotonic();stop=None;interrupted=False
    try:
        session.finish_pending()
        for number in range(len(session.book['chapters'])+1,plan['max_chapters']+1):
            written=sum(len(re.findall(r'[\u3400-\u9fff]',ch['text'])) for ch in session.book['chapters'])
            if number>plan['chapters'] and written>=plan['target_han_chars']:break
            remaining=max(1,plan['chapters']-number+1)
            target=max(1,(plan['target_han_chars']-written+remaining-1)//remaining)
            instruction=(f"连续草稿目标{plan['target_han_chars']}汉字，名义{plan['chapters']}章，现在第{number}章。"
                f'已写{written}汉字，剩余篇幅{max(0,plan["target_han_chars"]-written)}汉字，须分配给剩余{remaining}章。'
                f'本章约{target}汉字，用完整场景、对话推进，不用梗概，不重复凑字数。'
                '根据已写事实局部调整后续计划，保持人物和世界因果一致；待修章节不假称已通过。'
                '名义最后一章解决主要冲突；如需补章，补与结局相容的场景，不推翻前文。')
            session.chapter_length_target=target
            row=session.write_next(instruction)
            saved_label='未保存' if row['status']=='NO_DRAFT' else '已保存'
            print(f"第{number}章{saved_label}：{row['status']}；累计请求{recorder.calls}次。",flush=True)
            if row['stop_reason'] or row['status']=='NO_DRAFT':
                stop=row['stop_reason'] or 'NO_USABLE_DRAFT';break
    except KeyboardInterrupt:
        stop='INTERRUPTED';interrupted=True
    except Exception as exc:
        stop='MEMORY_PENDING' if session.book['pending'] else 'REVIEW_PENDING' if session.book['review_jobs'] else 'RUNTIME_FAILURE'
        save_new(output/'runtime_failure.json',dict(error_type=type(exc).__name__,stop_reason=stop))
    state=session.book;memory=state['memory']
    prose='# '+plan['title']+'\n\n> 待修草稿，不表示质量通过。\n\n'
    prose+='\n\n'.join(f"## 第{ch['number']}章 {ch['title']}\n\n{ch['text']}" for ch in state['chapters'])
    with (output/'正文.md').open('x',encoding='utf-8') as stream:stream.write(prose+'\n')
    pending=[row for row in state['outcomes'] if row['status']!='DRAFT_CHECKED']
    review_counts=dict(proposed=sum(len(r.get('review',{}).get('proposed_issues',[])) for r in state['outcomes']),
        confirmed=sum(len(r.get('issues',[])) for r in state['outcomes']),
        unresolved=sum(len(r.get('unresolved_review_issues',[])) for r in state['outcomes']),
        suggestions=sum(len(r.get('dismissed_review_issues',[])) for r in state['outcomes']))
    save_new(output/'问题清单.json',dict(scope='Model-reviewed reports, not independently certified error counts',
        chapters=pending,story_review_counts=review_counts,
        pending_story_review_chapters=sorted(int(n) for n in state['review_jobs']),
        story_review_failures=state.get('review_failures',[]),
        nonblocking_review_suggestions=[dict(chapter=r['chapter_number'],items=r['dismissed_review_issues'])
            for r in state['outcomes'] if r.get('dismissed_review_issues')]))
    save_new(output/'final_state.json',state)
    if plan.get('event_first',True):
        save_new(output/'事件链.json',dict(scope='Canonical events simulated before prose; not a semantic correctness certificate',
            commits=[c['event_commit'] for c in state['chapters']],current_state=state['writing_state'],
            prepared_not_committed=[dict(chapter=int(n),commit_sha256=p['commit']['sha256']) for n,p in state['prepared_events'].items()]))
    assessment=[]
    for row in state['outcomes']:
        review=row.get('review',{})
        for index,issue in enumerate(review.get('proposed_issues',review.get('issues',[])),1):
            assessment.append(dict(id=f'chapter_{row["chapter_number"]}_issue_{index}',chapter=row['chapter_number'],
                proposal=issue,human_verdict='UNASSESSED',human_evidence=[],reason=''))
    save_new(output/'审核效用评估.json',dict(story_review_enabled=plan.get('story_review_enabled',True),
        story_review_usage=meter.story_review_usage,novel_sha256=digest(prose+'\n'),
        policy='Manually verify proposals against prose and separately record missed errors. Model confirmation is not a true-positive label.',
        proposals=assessment,missed_errors=[],full_text_review_completed=False,
        effectiveness='NOT_YET_MEASURED',validated_true_findings=None))
    han=sum(len(re.findall(r'[\u3400-\u9fff]',ch['text'])) for ch in state['chapters'])
    length_met=han>=plan['target_han_chars']
    if stop is None and not length_met:stop='CHAPTER_CAP_BEFORE_LENGTH_TARGET'
    memory_processing_complete=memory['processed_through']==len(state['chapters']) and not state['pending']
    from memory_runtime.prose_memory import verify_prose_coverage
    prose_memory_complete=all(verify_prose_coverage(memory,c) for c in state['chapters'] if c.get('prose_policy')=='unchecked')
    memory_complete=memory_processing_complete and prose_memory_complete
    memory_layers_complete=not memory.get('layer_deferred_ids',[])
    unprojected=[c['number'] for c in state['chapters'] if c.get('event_plan_status')=='unavailable']
    result=dict(scope='USER_WRITING_NOT_COMPARATIVE_EXPERIMENT',chapters=len(state['chapters']),han_chars=han,
        target_chapters=plan['chapters'],target_han_chars=plan['target_han_chars'],length_target_met=length_met,
        draft_completed=not stop and length_met and len(state['chapters'])>=plan['chapters'],stop_reason=stop,
        checked_draft_chapters=sum(r['status']=='DRAFT_CHECKED' for r in state['outcomes']),pending_draft_chapters=len(pending),
        quality_gate_passed=False,story_and_mechanical_checks_passed=not stop and memory_complete and memory_layers_complete and not pending and length_met and len(state['chapters'])>=plan['chapters'],
        prose_content_checks='disabled' if plan.get('event_first',True) else 'legacy',
        memory_projection_complete=not memory.get('projection_omissions',{}) and not unprojected,
        memory_projection_omissions=memory.get('projection_omissions',{}),
        event_alignment_complete=not memory.get('projection_omissions',{}) and not unprojected,
        unprojected_chapters=unprojected,
        generation_warning_count=sum(len(r.get('generation_warnings',[])) for r in state['outcomes']),
        memory_processing_complete=memory_processing_complete,prose_memory_complete=prose_memory_complete,
        prose_excerpt_count=sum(i['kind']=='prose_excerpt' for i in memory['items'].values()),
        review_mode='tiered_memory',memory_semantic_review='canonical_event_projection' if plan.get('event_first',True) else 'independent_model_review_not_certified',
        writing_mode='event_first' if plan.get('event_first',True) else 'legacy_prose_first',
        canonical_event_chapters=sum('event_commit' in c and c.get('event_plan_status')!='unavailable' for c in state['chapters']),
        prepared_event_chapters=sorted(int(n) for n in state['prepared_events']),
        story_review_failure_policy='DEFERRED_CONTINUE_WRITING',
        story_review_enabled=plan.get('story_review_enabled',True),story_review_usage=meter.story_review_usage,
        story_review_effectiveness='NOT_YET_MEASURED',
        story_review_failure_count=len(state.get('review_failures',[])),
        pending_story_review_chapters=sorted(int(n) for n in state['review_jobs']),
        time_calculation_count=sum(len(c.get('time_calculations',[])) for c in state['chapters']),
        time_calculation_scope='Optional declared formulas only; no prose arithmetic inspection' if plan.get('event_first',True) else 'Legacy time binding',
        writing_state_scope='Simulated event plan state; prose alignment is unchecked; memory only projects sources present in saved prose' if plan.get('event_first',True) else 'Typed writer-declared constraints; not semantic completeness certification',
        memory_processed_through=memory['processed_through'],memory_complete=memory_complete,pending_memory_chapters=state['pending'],
        memory_layers_complete=memory_layers_complete,pending_layer_ids=memory.get('layer_deferred_ids',[]),
        memory_failure_count=len(state.get('memory_failures',[])),memory_failure_policy='DEFERRED_CONTINUE_WRITING',
        story_review_counts=review_counts,
        memory_counts={tier:sum(i['tier']==tier for i in memory['items'].values()) for tier in ('working','recent','long')},
        withheld_mutations=len(memory.get('withheld_memory_mutations',[])),
        active_facts=sum(has_current_content(i) for i in memory['items'].values()),archived_versions=len(memory['history']),
        budget_limits=None,calls=recorder.calls,gateway_attempts=meter.calls,input_tokens=meter.input_tokens,
        output_tokens=meter.output_tokens,cost_usd_estimate_not_bill=meter.cost_usd,
        cost_scope='This invocation successful metered replies only; excludes parent runs; failed delivery may incur unknown charges',
        resume_checkpoint=str(session.latest_checkpoint.resolve()),
        elapsed_seconds=time.monotonic()-started,outcomes=state['outcomes'],story_sha256=digest(prose+'\n'))
    if plan.get('event_first',True):
        result.update(story_and_mechanical_checks_passed=None,quality_checked=False,
            mechanical_checks_passed=not stop and memory_complete and memory_layers_complete and length_met and len(state['chapters'])>=plan['chapters'],
            story_review_effectiveness='DISABLED')
    save_new(output/'result.json',result)
    if interrupted:raise KeyboardInterrupt()
    return result
