"""Durable writing adapter for the verified three-tier memory pipeline."""
import copy
from pathlib import Path

from .engine import MemoryEngine
from .pipeline import source_evidence_view
from .story_review import StoryReferenceGateway,StoryReviewAgent
from .time_calculation import CONTRACT as TIME_CONTRACT,calculate,write_with_calculations
from .continuity import CONTRACT as CONTINUITY_CONTRACT,empty as empty_writing_state,context_view as writing_state_view,guard as guard_continuity
from .event_first import CONTRACT as EVENT_CONTRACT,STATE_CONTRACT as EVENT_STATE_CONTRACT,prepare as prepare_events,writer_view,realize,verify as verify_events
from .event_first import normalize_plan,compile_realization
from .event_contract import validate_plan_shape
from .event_references import catalogue as reference_catalogue,public_state_view,reference_id,public_type
from .numeric_grounding import sources as quantity_sources,POLICY as QUANTITY_POLICY
from .prose_rendering import render as render_prose
from .interface_contract import public_memory_rows
from .completion import ContextCapacityError,PlanningOutputFailure,unplanned_packet,continue_prose
from inf_writer.domain import ContractError,canonical,digest,evidence_segments,text
from inf_writer.agents import JsonAgent
from inf_writer.tiered_memory import legacy_projection,select_context,select_history_context


def runtime_hashes():
    from check_memory import source_hashes,sha,ROOT
    from importlib.metadata import version
    return dict(memory_runtime=source_hashes(),entrypoints={name:sha(ROOT/name)
        for name in ('write_novel.py','user_runtime.py','check_memory.py')},
        orchestration=dict(framework='langgraph',version=version('langgraph')))


def load_resume(path,plan):
    from check_memory import read
    record=read(path)
    if record.get('schema')!='inf-writing-checkpoint-v1':raise ContractError('仅可恢复新写作入口的完整检查点；旧小说需显式迁移')
    if record.get('runtime_sha256')!=runtime_hashes():raise ContractError('写作运行时版本不一致，不能直接恢复旧检查点')
    if record.get('writing_plan_sha256')!=digest(canonical(plan)):raise ContractError('恢复时小说配置必须与原运行一致')
    book=record['book']
    if record.get('book_sha256')!=digest(canonical(book)):raise ContractError('写作检查点内容校验失败')
    done=book['memory']['processed_through'];chapters=book['chapters']
    if type(done) is not int or not 0<=done<=len(chapters):raise ContractError('Invalid memory coverage')
    if [c['number'] for c in chapters]!=list(range(1,len(chapters)+1)):raise ContractError('Invalid chapter sequence')
    if book['pending']!=list(range(done+1,len(chapters)+1)):raise ContractError('Memory pending coverage gap')
    if [r['chapter_number'] for r in book['outcomes']]!=list(range(1,len(chapters)+1)):
        raise ContractError('Invalid writing outcome sequence')
    if any(int(n)<1 or int(n)>len(chapters) for n in book['review_jobs']):raise ContractError('Invalid pending prose review')
    if plan.get('event_first',True):
        expected=digest(canonical(empty_writing_state()))
        for chapter in chapters:
            commit=verify_events(chapter.get('event_commit'))
            from .prose_rendering import saved_text
            if digest(chapter['text'])!=chapter['sha256'] or saved_text(chapter)!=chapter['text']:
                raise ContractError('Saved prose data integrity failure')
            if 'event_stage_sources' in chapter:
                chunks=chapter['event_stage_sources'];parts=commit.get('stage_transactions',[])
                if len(chunks)!=len(parts) or '\n\n'.join(c['text'] for c in chunks)!=chapter['text']:
                    raise ContractError('Saved event stages differ from chapter prose')
                for chunk,part in zip(chunks,parts):
                    if digest(chunk['text'])!=chunk['sha256'] or chunk['commit_sha256']!=part['sha256']:
                        raise ContractError('Saved event-stage source hash mismatch')
            if commit['chapter']!=chapter['number'] or commit['base_state_sha256']!=expected:
                raise ContractError('Canonical event history has a state-chain gap')
            expected=commit['state_sha256']
            if chapter['number']<=done and book['memory'].get('canonical_commits',{}).get(str(chapter['number']))!=commit['sha256']:
                raise ContractError('Memory projection does not match committed event source')
            if chapter['number']<=done and chapter.get('prose_policy')=='unchecked':
                from .prose_memory import verify_prose_coverage
                if not verify_prose_coverage(book['memory'],chapter):raise ContractError('Saved prose memory coverage is missing or damaged')
        if digest(canonical(book['writing_state']))!=expected:
            raise ContractError('Current world state differs from committed event outcomes')
        for key,prepared in book.get('prepared_events',{}).items():
            commit=verify_events(prepared['commit'])
            if key!=str(len(chapters)+1) or commit['chapter']!=len(chapters)+1 or commit['base_state_sha256']!=expected:
                raise ContractError('Prepared event transaction has an invalid chapter or base state')
            if digest(canonical(prepared['candidate_state']))!=commit['state_sha256'] or digest(canonical(prepared['proposal']))!=commit['proposal_sha256']:
                raise ContractError('Prepared event proposal/state integrity failure')
            verify_stage_realizations(prepared)
    return copy.deepcopy(book)


def verify_stage_realizations(prepared):
    packets=prepared.get('stage_packets',[]);chunks=prepared.get('stage_realizations',[])
    if len(chunks)>len(packets):raise ContractError('Too many saved event stages')
    for chunk,packet in zip(chunks,packets):
        verify_events(packet['commit'])
        if (chunk['stage']!=packet['stage'] or chunk['commit_sha256']!=packet['commit']['sha256']
                or digest(chunk['text'])!=chunk['sha256']
                or digest(canonical(packet['candidate_state']))!=packet['commit']['state_sha256']):
            raise ContractError('Saved event-stage prose/state integrity failure')


class WritingSession:
    def __init__(self,output,gateway,plan,book=None):
        self.output=Path(output);self.output.mkdir(parents=True,exist_ok=False)
        self.plan=copy.deepcopy(plan);self.gateway=gateway;self.engine=MemoryEngine(gateway)
        if self.plan.get('event_first',True):self.plan['story_review_enabled']=False
        self.story_gateway=StoryReferenceGateway(gateway)
        self.agents=dict(planner=JsonAgent('planner',gateway,compact_narrative=True,max_format_retries=0,max_output_tokens=16384),
            writer=JsonAgent('writer',gateway,compact_narrative=True,max_output_tokens=16384),
            reviewer=StoryReviewAgent(self.story_gateway))
        self.book=copy.deepcopy(book) if book is not None else dict(
            schema_version='inf-writing-book-v1',goal=plan['goal'],constraints=copy.deepcopy(plan['constraints']),
            chapters=[],plan={},memory=MemoryEngine.empty(),pending=[],outcomes=[],review_jobs={})
        self.book.setdefault('writing_state',empty_writing_state())
        self.book.setdefault('prepared_events',{})
        from .graph_runtime import build_writing_graph
        self.graph=build_writing_graph(self)
        self.serial=0;self.latest_checkpoint=None;self.hashes=runtime_hashes()
        self._save([],'RESUMED' if book is not None else 'EMPTY_START')

    def _save(self,trace,reason):
        from check_memory import save_new
        path=self.output/f'checkpoint_{self.serial:04d}.json'
        save_new(path,dict(schema='inf-writing-checkpoint-v1',runtime_sha256=self.hashes,
            writing_plan_sha256=digest(canonical(self.plan)),book_sha256=digest(canonical(self.book)),
            book=self.book,trace=trace,reason=reason,orchestration='langgraph'))
        self.latest_checkpoint=path;self.serial+=1

    def context(self,instruction,query):
        book=self.book;memory=book['memory'];number=len(book['chapters'])+1
        event_first=self.plan.get('event_first',True)
        selection=select_context(memory,query=query,max_bytes=22000 if event_first else 32000)
        bindings={i:dict(memory_id=i,view='current') for i in selection['selected_ids']}
        evidence=source_evidence_view(memory,selection['selected_ids'],bindings,query,max_bytes=8000 if event_first else 12000)
        history=select_history_context(memory,query=query,max_bytes=4000 if event_first else 6000)
        context=dict(goal=book['goal'],constraints=book['constraints'],chapter_number=number,instruction=instruction,
            checkpoint_revision=memory['revision'],recent_chapters=[{k:c[k] for k in ('number','title','text','sha256')} for c in book['chapters'][-2:]],
            planned_next_chapters=[v for k,v in sorted(book['plan'].items(),key=lambda r:int(r[0])) if int(k)>=number],
            active_facts=legacy_projection(selection),historical_memory=history,source_evidence=evidence['items'],
            memory_coverage=dict(processed_through=memory['processed_through'],selected_ids=selection['selected_ids'],
                omitted_ids=selection['omitted_ids'],source_evidence_omitted=evidence['omitted'],
                pending_chapters=copy.deepcopy(book['pending']),complete=not book['pending']),
            unresolved_chapters=[r['chapter_number'] for r in book['outcomes'] if r['status']!='DRAFT_CHECKED'],
            fact_bank_status=f"Memory committed through chapter {memory['processed_through']}; pending chapters {book['pending']}. "
                'Pending chapter changes may be absent from memory. Read recent prose for newer events; do not treat older memory or historical quotes as unconditionally current authority.')
        context['calculation_contract']=copy.deepcopy(TIME_CONTRACT)
        context['quantity_policy']=QUANTITY_POLICY
        context['unprojected_chapters']=[c['number'] for c in book['chapters'] if c.get('event_plan_status') in ('partial','unavailable')]
        if context['unprojected_chapters']:
            context['fact_bank_status']+=' Some chapters have prose only; event state omits their changes. Prefer saved prose for these chapters.'
        context['continuity_contract']=copy.deepcopy(CONTINUITY_CONTRACT)
        references=reference_catalogue(book) if event_first else None
        context['writing_state']=public_state_view(writing_state_view(book['writing_state'],query,plans=references['plans'])) if event_first else writing_state_view(book['writing_state'],query)
        if event_first:
            context['event_first_contract']=copy.deepcopy(EVENT_CONTRACT)
            for item in context['active_facts']:
                binding=references['memory'].get(item['memory_id'])
                if binding:
                    item['canonical_reference']=dict(record_kind=public_type(binding['type']),record_id=binding['id'],record_revision=binding['revision'])
                    item['reference_id']=reference_id(binding['type'],binding['id'])
                    item['reference_scope']=binding['scope']
            context.pop('continuity_contract')
            context['state_record_contract']=copy.deepcopy(EVENT_STATE_CONTRACT)
            context['fact_bank_status']+=' event_plan_state is simulated plan state. prose_excerpt quotes saved text, not current-world fact declarations. Memory IDs are never state preconditions; select references via reference_selection_contract.'
            context['calculation_contract']['instruction']+=' Only planner declares time_calculations before event freeze. Writer can use frozen tokens but cannot add or change calculation inputs.'
            context['interface_contract_version']=2
            context['memory_bank_revision']=context.pop('checkpoint_revision')
            context['event_plan_state']=context.pop('writing_state')
            from .reference_choices import CONTRACT as CHOICE_CONTRACT,formal_operation_catalogue
            context['reference_choices']=list(dict.fromkeys(r['reference_id'] for r in context['event_plan_state']['records']))
            context['reference_selection_contract']=CHOICE_CONTRACT
            context['reference_choices_by_kind']={kind:[i for i,v in enumerate(context['reference_choices'],1) if v.startswith(kind+':')] for kind in sorted(set(v.split(':',1)[0] for v in context['reference_choices']))}
            context['state_record_contract']['instruction']='operation选操作，record_kind是只读类别；按目录字段填值。新编号由程序生成，引用仅用reference_selection_contract选择器，属性显示名自由。'
            context['state_record_contract'].pop('reference_contract',None)
            for index,row in enumerate(context['event_plan_state']['records'],1):row['record_choice']=index
            context['event_first_contract']['instruction']='scenes每项必须purpose/participants/beats；beats每项必须statement/assertion_scope/requires/changes。requires和changes无内容填[]。不填id。引用遵循reference_selection_contract，changes用state_record_contract的operation及字段。'
            context['event_first_contract'].pop('dependency_examples',None)
            context['state_record_contract']['schemas']=formal_operation_catalogue()
            context['reference_protocol']='choices_v1'
            context['retrieved_memory']=public_memory_rows(context.pop('active_facts'))
            context['memory_context_status']=context.pop('fact_bank_status')
            context['content_unchecked_chapters']=context.pop('unresolved_chapters')
            from .prose_memory import verify_prose_coverage
            context['memory_coverage'].update(processing_complete=not book['pending'],
                prose_storage_complete=all(verify_prose_coverage(memory,c) for c in book['chapters'] if c.get('prose_policy')=='unchecked'),
                event_alignment_complete=not memory.get('projection_omissions',{}) and not context['unprojected_chapters'])
            context['memory_coverage'].pop('complete',None)
        if self.plan.get('closure_enabled',True):
            from .story_closure import context as closure_context
            context['story_closure']=closure_context(book,self.plan)
        self._bound(context)
        return context

    @staticmethod
    def _bound(context):
        size=len(canonical(context).encode('utf-8'))
        from inf_writer.narrative_context import REPAIR_HEADROOM_BYTES
        limit=84000+(REPAIR_HEADROOM_BYTES if context.get('event_preflight_error') else 0)
        if size>limit:
            from .input_budget import fit
            bounded=fit(context,limit);context.clear();context.update(bounded)
            size=len(canonical(context).encode('utf-8'))
        if size>limit:raise ContextCapacityError(f'Writing context exceeds explicit budget: {size}>{limit}; no silent truncation')

    def catch_up(self,trace):
        while self.book['pending']:
            number=self.book['pending'][0];row=self.book['outcomes'][number-1]
            try:
                candidate,report=self.engine.advance(self.book['memory'],self.book['chapters'],number,trace)
            except BaseException:
                row.update(memory_update_status='PENDING',status='DRAFT_UNCHECKED')
                self._save(trace,'MEMORY_PENDING');raise
            self.book['memory']=candidate;self.book['pending'].pop(0)
            row.update(memory_update_status='APPLIED',memory_promoted=True,memory_report=report,
                withheld_mutations=report['withheld_mutations'],memory_semantic_review='canonical_event_projection' if report.get('canonical_projection') else 'independent_model_review_not_certified',stop_reason=None)
            if row.get('review',{}).get('approved') and not row['withheld_mutations']:
                row['status']='DRAFT_CHECKED'
            self._save(trace,'MEMORY_COMMITTED')

    def attempt_memory(self,trace):
        """One ordered queue pass per chapter; failure never blocks prose."""
        try:self.catch_up(trace)
        except Exception as exc:
            failure=dict(chapter=self.book['pending'][0],after_written_chapter=len(self.book['chapters']),
                error_type=type(exc).__name__,error=str(exc) if isinstance(exc,ContractError) else 'Memory processing failed',
                policy='DEFERRED_CONTINUE_WRITING')
            self.book.setdefault('memory_failures',[]).append(failure)
            self.book['outcomes'][failure['chapter']-1].setdefault('memory_errors',[]).append(failure)
            self._save(trace,'MEMORY_DEFERRED_CONTINUE_WRITING')
            return False
        return True

    def _review_pending(self,trace):
        if not self.plan.get('story_review_enabled',True):return
        for key in sorted(list(self.book['review_jobs']),key=int):
            row=self.book['outcomes'][int(key)-1];context=self.book['review_jobs'][key]
            start=len(self.story_gateway.transforms)
            try:review=self.agents['reviewer'].run(context,trace)
            except Exception as exc:
                row.update(status='DRAFT_UNCHECKED',stop_reason=None)
                failure=dict(chapter=int(key),after_written_chapter=len(self.book['chapters']),
                    error_type=type(exc).__name__,error=str(exc) if isinstance(exc,ContractError) else 'Review service failed',policy='DEFERRED_CONTINUE_WRITING')
                row.setdefault('review_errors',[]).append(failure)
                self.book.setdefault('review_failures',[]).append(failure)
                self._save(trace,'REVIEW_DEFERRED_CONTINUE_WRITING')
                # End this queue pass: do not retry the same failing service for
                # every pending chapter before allowing another prose chapter.
                break
            finally:trace.extend(copy.deepcopy(self.story_gateway.transforms[start:]))
            row.update(review=review,issues=review['issues'],suggestions=review['suggestions'],stop_reason=None,story_review_status='REPORTED',
                unresolved_review_issues=review.get('unresolved_issues',[]),
                dismissed_review_issues=review.get('dismissed_issues',[]),
                status='DRAFT_CHECKED' if review['approved'] and row['memory_update_status']=='APPLIED' and not row.get('withheld_mutations') else 'DRAFT_UNCHECKED')
            del self.book['review_jobs'][key]
            self._save(trace,'CHAPTER_REVIEWED')

    def finish_pending(self):
        from .graph_runtime import new_run
        run=new_run(self,'')
        run['recovery_only']=True
        self.last_graph_trace=run['trace']
        self.graph.invoke({'run':run},config={'recursion_limit':32})

    def write_next(self,instruction):
        from .graph_runtime import new_run
        run=new_run(self,instruction)
        row=run['row'];trace=run['trace'];number=run['number']
        self.last_graph_trace=trace
        try:
            self.graph.invoke({'run':run},config={'recursion_limit':32})
        except Exception as exc:
            row['errors'].append(str(exc) if isinstance(exc,ContractError) else type(exc).__name__)
            if self.plan.get('event_first',True):
                row['stop_reason']='EVENT_FIRST_WRITING_UNRESOLVED'
                trace.append(dict(role='event_first_attempt',chapter=number,status='UNRESOLVED',error_type=type(exc).__name__,
                    error=str(exc) if isinstance(exc,ContractError) else 'Writing step failed; prepared events retained'))
            else:
                row['stop_reason']=row['stop_reason'] or 'NO_USABLE_DRAFT'
            self._save(trace,row['stop_reason'])
        return copy.deepcopy(row)

    def _prepare_events(self,instruction,number,trace):
        key=str(number);saved=self.book['prepared_events'].get(key)
        if saved and not saved.get('revision_request'):
            verify_events(saved['commit'])
            verify_stage_realizations(saved)
            if saved['commit']['base_state_sha256']!=digest(canonical(self.book['writing_state'])):
                raise ContractError('Prepared events no longer match committed canonical state')
            return copy.deepcopy(saved)
        try:context=self.context(instruction,instruction)
        except ContextCapacityError as exc:raise PlanningOutputFailure(str(exc)) from exc
        if saved:
            context['event_revision_request']=saved['revision_request']
            if 'public_proposal' not in saved:raise ContractError('Prepared revision lacks the original public proposal')
            context['previous_event_plan']=copy.deepcopy(saved['public_proposal'])
        public_proposal=None
        last_public=None;last_compiled=None;last_error=None
        def validate(value):
            nonlocal public_proposal,last_public,last_compiled
            incoming=copy.deepcopy(value)
            last_public=copy.deepcopy(value)
            from .reference_choices import compile_plan
            value=compile_plan(value,context['reference_choices'],number)
            if type(value['number']) is not int or value['number']!=number:raise ContractError('Planner must address next chapter')
            numbers=[r['number'] for r in value['future_updates']]
            if len(numbers)!=len(set(numbers)) or any(n<=number or n>self.plan['max_chapters'] for n in numbers):
                raise ContractError('Future updates must address distinct unwritten chapters')
            if not isinstance(value.get('scenes'),list):raise ContractError('Event-first planner must declare scenes')
            normalized=value
            try:
                normalized,_=normalize_plan(value,self.book['writing_state'],number,references=reference_catalogue(self.book))
                validate_plan_shape(normalized)
            except ContractError as exc:
                from .interface_contract import public_repair_details
                exc.repair_details=public_repair_details(getattr(exc,'repair_details',{}),normalized)
                raise
            calculate(value.get('time_calculations',[]))
            public_proposal=incoming
            last_compiled=copy.deepcopy(value)
            return value
        def accept(prepared,source):
            prepared['public_proposal']=copy.deepcopy(source)
            prepared['revision_count']=(saved or {}).get('revision_count',0)
            self.book['prepared_events'][key]=copy.deepcopy(prepared)
            trace.append(dict(role='event_simulation',status='PREPARED',commit_sha256=prepared['commit']['sha256'],
                before_state_sha256=prepared['commit']['base_state_sha256'],after_state_sha256=prepared['commit']['state_sha256']))
            self._save(trace,'EVENTS_PREPARED_NOT_COMMITTED')
            return prepared
        def recover(error):
            from .plan_repair import repair
            from .stage_planning import prepare_stages
            from .interface_contract import public_repair_details
            if last_public is not None:
                try:
                    fixed=repair(self.gateway,last_public,context['reference_choices'],
                        public_repair_details(getattr(error,'repair_details',{}),last_compiled or {}),trace)
                    compiled=validate(fixed)
                    prepare_events(self.book['writing_state'],compiled,number,references=reference_catalogue(self.book))
                    return accept(prepare_stages(self.book['writing_state'],compiled,number,reference_catalogue(self.book)),fixed)
                except Exception as repair_error:
                    trace.append(dict(role='state_repair',status='DEFERRED',error_type=type(repair_error).__name__,
                        error=str(repair_error) if isinstance(repair_error,ContractError) else 'Local repair unavailable'))
            if last_compiled is not None:
                packet=prepare_stages(self.book['writing_state'],last_compiled,number,reference_catalogue(self.book))
                return accept(packet,public_proposal)
            if last_public is not None:
                try:
                    from .reference_choices import compile_independent_stages
                    compiled,deferred=compile_independent_stages(last_public,context['reference_choices'],number)
                    packet=prepare_stages(self.book['writing_state'],compiled,number,reference_catalogue(self.book),deferred)
                except ContractError:
                    raise PlanningOutputFailure(str(error)) from error
                return accept(packet,last_public)
            raise PlanningOutputFailure(str(error)) from error
        attempts=self.book.setdefault('planning_attempts',{})
        remaining=max(0,5-attempts.get(key,0))
        for attempt in range(remaining):
            try:self._bound(context)
            except ContextCapacityError as exc:raise PlanningOutputFailure(str(exc)) from exc
            start=len(trace)
            attempts[key]=attempts.get(key,0)+1
            agent=copy.copy(self.agents['planner'])
            if context.get('output_was_truncated'):agent.max_output_tokens=min(65536,agent.max_output_tokens*2)
            try:proposal=agent.run(context,trace,validator=validate)
            except ContractError as exc:
                if any(r.get('role')=='planner' and r.get('status') in ('FORMAT_FAILED','INPUT_REJECTED') for r in trace[start:]):
                    if attempts[key]>=5:return recover(exc)
                    from .interface_contract import public_repair_details
                    previous=next((r.get('raw_output') for r in reversed(trace[start:]) if r.get('role')=='planner'),None)
                    details=public_repair_details(getattr(exc,'repair_details',{}),{})
                    from inf_writer.narrative_context import prepare_repair
                    context=prepare_repair(context,exc,previous,details)
                    context['event_preflight_error']=dict(error=str(exc),instruction='Repair listed output errors; do not invent references or treat intentions as completed actions.')
                    if any(r.get('finish_reason')=='length' for r in trace[start:]):context['output_was_truncated']=True
                    self._save(trace,'PLANNING_OUTPUT_REJECTED_RETRY')
                    continue
                raise
            try:
                prepared=prepare_events(self.book['writing_state'],proposal,number,references=reference_catalogue(self.book))
                from .stage_planning import prepare_stages
                prepared=prepare_stages(self.book['writing_state'],proposal,number,reference_catalogue(self.book))
                return accept(prepared,public_proposal)
            except ContractError as exc:
                trace.append(dict(role='event_simulation',status='REJECTED',proposal=proposal,error=str(exc),repair_details=getattr(exc,'repair_details',None)))
                if attempts[key]>=5:return recover(exc)
                from .interface_contract import public_repair_details
                context.pop('repair',None)
                context['event_preflight_error']=dict(error=str(exc),details=public_repair_details(getattr(exc,'repair_details',{}),proposal),
                    previous_plan=copy.deepcopy(public_proposal),instruction='Replan only unwritten events; resolve preconditions before any prose, preserve committed history. Keep the public fields; IDs are program-owned.')
        raise PlanningOutputFailure('Five planner outputs exhausted for this chapter')

    def _realize_stages(self,prepared,instruction,number,trace,row):
        """Persist each successful stage before requesting the next one."""
        from inf_writer.narrative_context import event_role_context
        packets=prepared['stage_packets'];key=str(number)
        verify_stage_realizations(prepared)
        for packet in packets[len(prepared['stage_realizations']):]:
            ordinal=len(prepared['stage_realizations'])+1
            earlier='\n\n'.join(c['text'] for c in prepared['stage_realizations'])
            stage_instruction=instruction+f' 本次只展开第{ordinal}/{len(packets)}个事件阶段，不重复此前阶段，不输出章节标题。'
            try:
                context=self.context(stage_instruction,prepared['proposal']['brief'])
                context['chapter_plan']={k:prepared['proposal'][k] for k in ('number','title','brief')}
                context['frozen_events']=writer_view(packet)
                context['quantity_sources']=quantity_sources(packet['commit'])
                context['quantity_policy']=QUANTITY_POLICY;context['prose_content_checks']='disabled'
                context['earlier_stage_prose']=earlier
                context=event_role_context(context,'writer');self._bound(context)
                start=len(trace)
                try:output=self.agents['writer'].run(context,trace)
                except ContractError:
                    if not any(t.get('role')=='writer' and t.get('status') in ('FORMAT_FAILED','INPUT_REJECTED') for t in trace[start:]):raise
                    raw=[t.get('raw_output') for t in trace[start:] if t.get('role')=='writer']
                    output=dict(text=continue_prose(self.gateway,self.book,stage_instruction+' 已写阶段：'+earlier,number,trace,raw))
                if 'event_revision_request' in output:
                    output=dict(text=continue_prose(self.gateway,self.book,stage_instruction+' 已写阶段：'+earlier,number,trace))
                    row.setdefault('generation_warnings',[]).append(dict(stage='stage_revision',event_stage=packet['stage'],policy='CONTINUE_STAGE_PROSE'))
                try:prose=render_prose(output['text'],packet['commit'],context['quantity_sources'])
                except ContractError as exc:
                    prose=output['text'];row.setdefault('generation_warnings',[]).append(dict(stage='stage_prose_reference',event_stage=packet['stage'],error=str(exc),policy='PRESERVE_LITERAL_PROSE'))
            except ContextCapacityError:
                prose=continue_prose(self.gateway,self.book,stage_instruction+' 已写阶段：'+earlier,number,trace)
            report=None
            if getattr(self,'chapter_length_target',None) is not None:
                from .length_control import adjust,han_count
                target=max(1,(self.chapter_length_target-han_count(earlier)+len(packets)-ordinal)//(len(packets)-ordinal+1))
                prose,report=adjust(prose,target,self.book,number,self.gateway,trace)
            prepared['stage_realizations'].append(dict(stage=packet['stage'],text=prose,sha256=digest(prose),
                commit_sha256=packet['commit']['sha256'],length_report=report))
            self.book['prepared_events'][key]=copy.deepcopy(prepared)
            self._save(trace,'EVENT_STAGE_PROSE_SAVED_NOT_CHAPTER_COMMITTED')
        return '\n\n'.join(c['text'] for c in prepared['stage_realizations'])

    def _graph_event_plan(self,run):
        instruction=run['instruction'];number=run['number'];key=str(number);trace=run['trace'];row=run['row']
        try:prepared=self._prepare_events(instruction,number,trace)
        except PlanningOutputFailure as exc:
            prepared=unplanned_packet(self.book['writing_state'],number,instruction,
                title=self.book['plan'].get(key,{}).get('title'))
            self.book['prepared_events'][key]=copy.deepcopy(prepared)
            row.setdefault('generation_warnings',[]).append(dict(stage='planning',error=str(exc),policy='CONTINUE_PROSE_WITHOUT_STATE_CHANGES'))
            self._save(trace,'PLANNING_DEFERRED_CONTINUE_PROSE')

        run.update(prepared=prepared,revision_requested=False)

    def _graph_event_writer(self,run):
        instruction=run['instruction'];number=run['number'];key=str(number);trace=run['trace'];row=run['row'];prepared=run['prepared']
        while True:
            deferred=[r for r in prepared.get('stage_reports',[]) if r['status']=='DEFERRED']
            if deferred:
                row['deferred_event_stages']=copy.deepcopy(deferred)
                row.setdefault('generation_warnings',[]).append(dict(stage='event_stages',policy='COMMIT_INDEPENDENT_VALID_STAGES',deferred_stages=[r['stage'] for r in deferred]))
            if prepared.get('stage_packets') and (len(prepared['stage_packets'])>1 or deferred):
                context=dict(recent_chapters=self.book['chapters'][-2:],historical_memory=dict(items=[]),quantity_sources=quantity_sources(prepared['commit']))
                output=dict(text=self._realize_stages(prepared,instruction,number,trace,row))
                break
            if prepared['commit'].get('event_plan_status')=='unavailable':
                context=dict(recent_chapters=self.book['chapters'][-2:],historical_memory=dict(items=[]),quantity_sources=[])
                output=dict(text=continue_prose(self.gateway,self.book,instruction,number,trace))
                break
            try:context=self.context(instruction,prepared['proposal']['title']+' '+prepared['proposal']['brief'])
            except ContextCapacityError as exc:
                context=dict(recent_chapters=self.book['chapters'][-2:],historical_memory=dict(items=[]),quantity_sources=quantity_sources(prepared['commit']))
                output=dict(text=continue_prose(self.gateway,self.book,instruction,number,trace))
                row.setdefault('generation_warnings',[]).append(dict(stage='writer_context',error=str(exc),policy='CONTINUE_WITH_BOUNDED_PROSE_CONTEXT'))
                break
            context['chapter_plan']={k:prepared['proposal'][k] for k in ('number','title','brief')}
            context['frozen_events']=writer_view(prepared)
            context['quantity_sources']=quantity_sources(prepared['commit'])
            context['quantity_policy']=QUANTITY_POLICY
            context['prose_content_checks']='disabled'
            from inf_writer.narrative_context import event_role_context
            context=event_role_context(context,'writer')
            try:self._bound(context)
            except ContextCapacityError as exc:
                output=dict(text=continue_prose(self.gateway,self.book,instruction,number,trace))
                row.setdefault('generation_warnings',[]).append(dict(stage='writer_context',error=str(exc),policy='CONTINUE_WITH_BOUNDED_PROSE_CONTEXT'))
                break
            start=len(trace)
            try:output=self.agents['writer'].run(context,trace)
            except ContractError as exc:
                rejected=[r.get('raw_output') for r in trace[start:] if r.get('role')=='writer' and r.get('status')=='FORMAT_FAILED']
                if not rejected and not any(r.get('role')=='writer' and r.get('status')=='INPUT_REJECTED' for r in trace[start:]):raise
                output=dict(text=continue_prose(self.gateway,self.book,instruction,number,trace,rejected))
                row.setdefault('generation_warnings',[]).append(dict(stage='writer_format',error=str(exc),policy='PRESERVE_PROSE_CONTINUE'))
            if 'event_revision_request' not in output:break
            if prepared['revision_count']>=1:
                output=dict(text=continue_prose(self.gateway,self.book,instruction,number,trace))
                row.setdefault('generation_warnings',[]).append(dict(stage='revision',policy='CONTINUE_PROSE_AFTER_REVISION_LIMIT'))
                break
            prepared['revision_count']+=1;prepared['revision_request']=output['event_revision_request']
            self.book['prepared_events'][key]=copy.deepcopy(prepared)
            self._save(trace,'EVENT_REVISION_REQUESTED_NOT_COMMITTED')
            run['revision_requested']=True
            return
        run.update(prepared=prepared,context=context,output=output,revision_requested=False)

    def _graph_event_commit(self,run):
        number=run['number'];key=str(number);trace=run['trace'];row=run['row'];prepared=run['prepared'];context=run['context'];output=run['output']
        template=output['text']
        verify_events(prepared['commit'])
        if canonical(context['quantity_sources'])!=canonical(quantity_sources(prepared['commit'])):
            raise ContractError('Quantity source table differs from its event data')
        encoding='references'
        try:draft=render_prose(template,prepared['commit'],context['quantity_sources'])
        except ContractError as exc:
            draft=template;encoding='literal'
            row.setdefault('generation_warnings',[]).append(dict(stage='prose_reference',error=str(exc),policy='PRESERVE_LITERAL_PROSE'))
        if draft!=template:
            trace.append(dict(role='event_realization',status='REFERENCES_RENDERED',input_sha256=digest(template),output_sha256=digest(draft)))
        length_report=None
        if getattr(self,'chapter_length_target',None) is not None and not prepared.get('stage_realizations'):
            from .length_control import adjust
            revised,length_report=adjust(draft,self.chapter_length_target,self.book,number,self.gateway,trace)
            if revised!=draft:draft=revised;template=revised;encoding='literal'
        if digest(canonical(prepared['candidate_state']))!=prepared['commit']['state_sha256']:
            raise ContractError('Prepared candidate state integrity failure')
        proposal=prepared['proposal']
        from .chapter_titles import resolve_title
        title=resolve_title(proposal['title'],draft,number,self.book['plan'].get(key,{}).get('title'),gateway=self.gateway,trace=trace)
        chapter=dict(number=number,title=title,text=draft,sha256=digest(draft),
            event_commit=copy.deepcopy(prepared['commit']),realization_template=template,
            prose_policy='unchecked',quantity_sources=copy.deepcopy(context['quantity_sources']),
            prose_encoding=encoding,event_plan_status=prepared['commit'].get('event_plan_status','prepared'),
            time_calculations=copy.deepcopy(prepared['commit']['computed_times']))
        if length_report is not None:chapter['length_report']=length_report
        if prepared.get('stage_realizations'):
            chapter['event_stage_sources']=copy.deepcopy(prepared['stage_realizations'])
        if prepared.get('stage_reports'):chapter['event_stage_reports']=copy.deepcopy(prepared['stage_reports'])
        refs={f'constraint_{i}':rule for i,rule in enumerate(self.book['constraints'],1)}
        refs.update({f'draft_{s["id"]}':s['text'] for s in evidence_segments(draft)})
        refs.update({f'past_{c["number"]}':c['text'] for c in context['recent_chapters']})
        refs.update({f'past_memory_{i}':canonical(h) for i,h in enumerate(context['historical_memory']['items'],1)})
        review_context=dict(context,current_draft=draft,hard_references=refs)
        # Event outcome and prose enter the same durable checkpoint. The
        # candidate was never treated as already happened before this point.
        previous_book=copy.deepcopy(self.book)
        self.book['chapters'].append(chapter);self.book['pending'].append(number)
        self.book['writing_state']=copy.deepcopy(prepared['candidate_state'])
        del self.book['prepared_events'][key]
        self.book['plan'][key]={k:proposal[k] for k in ('number','title','brief')}
        self.book['plan'][key]['title']=title
        for future in proposal['future_updates']:self.book['plan'][str(future['number'])]=copy.deepcopy(future)
        row.update(status='DRAFT_UNCHECKED',memory_update_status='PENDING',writing_invariants='EVENT_DATA_COMMITTED_PROSE_UNCHECKED',
            event_commit_sha256=prepared['commit']['sha256'],
            story_review_status='PENDING' if self.plan.get('story_review_enabled',True) else 'DISABLED')
        self.book['outcomes'].append(row)
        if chapter['event_plan_status'] in ('partial','unavailable'):
            self.book.setdefault('state_repair_jobs',{})[key]=dict(status='PENDING',chapter_sha256=chapter['sha256'],
                deferred_stages=copy.deepcopy(row.get('deferred_event_stages',[])),
                instruction='Rebuild only from saved prose with source evidence; rejected proposals are not facts.')
        if self.plan.get('story_review_enabled',True):self.book['review_jobs'][key]=review_context
        try:self._save(trace,'DRAFT_SAVED_MEMORY_PENDING')
        except BaseException:
            self.book=previous_book
            row.update(status='NO_DRAFT',memory_update_status='NOT_RUN',memory_promoted=False)
            raise

    def _graph_legacy_plan(self,run):
        instruction=run['instruction'];number=run['number'];trace=run['trace']
        context=self.context(instruction,instruction+' '+(self.book['chapters'][-1]['title'] if self.book['chapters'] else ''))
        def validate_plan(value):
            if type(value['number']) is not int or value['number']!=number:raise ContractError('Planner must address next chapter')
            numbers=[r['number'] for r in value['future_updates']]
            if any(n<=number or n>self.plan['max_chapters'] for n in numbers) or len(numbers)!=len(set(numbers)):
                raise ContractError('Future updates must address distinct unwritten chapters within the configured cap')
            calculate(value.get('time_calculations',[]))
            return value
        proposal=self.agents['planner'].run(context,trace,validator=validate_plan)

        run['proposal']=proposal

    def _graph_legacy_writer(self,run):
        instruction=run['instruction'];number=run['number'];trace=run['trace'];row=run['row'];proposal=run['proposal']
        context=self.context(instruction,proposal['title']+' '+proposal['brief']+' '+instruction)
        context['chapter_plan']=proposal
        context['computed_times']=calculate(proposal.get('time_calculations',[]))
        self._bound(context)
        try:draft,calculations,metadata=write_with_calculations(self.agents['writer'],context,trace)
        except Exception:
            row['stop_reason']='WRITING_TIME_CALCULATION_UNRESOLVED' if any(t['role']=='writer_time_calculation' for t in trace) else 'WRITING_OUTPUT_UNRESOLVED'
            raise
        try:
            draft,writing_state=guard_continuity(self.book['writing_state'],metadata['updates'],metadata['no_change_reason'],
                draft,number,calculations,self.gateway,trace)
        except Exception:
            row['stop_reason']='WRITING_CONTINUITY_UNRESOLVED'
            raise

        run.update(context=context,draft=draft,calculations=calculations,writing_state=writing_state)

    def _graph_legacy_commit(self,run):
        number=run['number'];trace=run['trace'];row=run['row'];proposal=run['proposal'];context=run['context'];draft=run['draft'];calculations=run['calculations'];writing_state=run['writing_state']
        from .chapter_titles import resolve_title
        title=resolve_title(proposal['title'],draft,number,self.book['plan'].get(str(number),{}).get('title'),gateway=self.gateway,trace=trace)
        chapter=dict(number=number,title=title,text=draft,sha256=digest(draft),time_calculations=calculations)
        review_context=dict(context,current_draft=draft)
        refs={f'constraint_{i}':rule for i,rule in enumerate(self.book['constraints'],1)}
        refs.update({f'draft_{s["id"]}':s['text'] for s in evidence_segments(draft)})
        refs.update({f'past_{c["number"]}':c['text'] for c in context['recent_chapters']})
        refs.update({f'past_memory_{i}':canonical(h) for i,h in enumerate(context['historical_memory']['items'],1)})
        review_context['hard_references']=refs
        self.book['chapters'].append(chapter);self.book['pending'].append(number)
        self.book['writing_state']=writing_state
        self.book['plan'][str(number)]={k:proposal[k] for k in ('number','title','brief')}
        self.book['plan'][str(number)]['title']=title
        for future in proposal['future_updates']:self.book['plan'][str(future['number'])]=copy.deepcopy(future)
        row.update(status='DRAFT_UNCHECKED',memory_update_status='PENDING',stop_reason=None,
            writing_invariants='VALIDATED_DECLARATIONS',story_review_status='PENDING' if self.plan.get('story_review_enabled',True) else 'DISABLED')
        self.book['outcomes'].append(row)
        if self.plan.get('story_review_enabled',True):self.book['review_jobs'][str(number)]=review_context
        self._save(trace,'DRAFT_SAVED_MEMORY_PENDING')

