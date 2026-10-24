"""Runtime adapters for continuous memory extraction, tiers and recall.

All transformations are logged. Raw HTTP requests/replies remain in the
RecordedProvider output. No fuzzy matching or semantic correction occurs.
"""
import copy
import hashlib

from inf_writer.domain import ContractError, canonical, fields, strict_json
from inf_writer.models import ModelReply,ModelRequest
from inf_writer.tiered_memory import apply_delta,select_context,select_history_context,wire_item
from inf_writer.memory_temporality import has_current_content
from inf_writer.tiered_runtime import MEMORY_SYSTEM
from inf_writer.memory_temporality import current_claim,time_view,annotated
from inf_writer.temporal_agent import TemporalReconciler,TemporalUnresolved,SYSTEM as TEMPORAL_SYSTEM
from inf_writer.temporal_transport import decode
import re
from .identifiers import attribute_identifier


def normalize(value):
    notes=[]
    if isinstance(value,dict) and 'type' in value:
        if value['type']!='json_object':raise ContractError('Optional type must be exactly json_object')
        value={k:v for k,v in value.items() if k!='type'}
        notes.append(dict(rule='exact_json_metadata',field='type',value='json_object'))
    return value,notes


def container_status(operation,kind,notes):
    requested=operation.get('status');actual=requested
    if kind=='task' and requested in ('active','pending','ongoing','in_progress'):actual='planned'
    elif kind in ('state','event','knowledge','legacy') and requested in ('planned','completed','cancelled'):actual='active'
    if actual!=requested:
        operation['status']=actual
        notes.append(dict(rule='container_status_domain',kind=kind,requested=requested,actual=actual))


class ExtractionAdapter:
    """Request-local short IDs, with exact reverse binding to selected records."""
    def __init__(self,gateway):self.gateway=gateway;self.transforms=[];self.full_memory=None
    def complete(self,request):
        if request.system==TEMPORAL_SYSTEM:
            return self._temporal(request)
        return self._extract(request)

    def _temporal(self,request):
        original=copy.deepcopy(request.payload);candidate_ids=[r['id'] for r in original['candidate_items']]
        batch={k:v for k,v in original.items() if k!='repair'}
        token='batch_'+hashlib.sha256(canonical(batch).encode('utf-8')).hexdigest()[:24]
        payload=copy.deepcopy(original)
        payload['batch_acknowledgement']=dict(token=token,candidate_count=len(candidate_ids),
            instruction='返回checked_batch_token精确等于token；不要枚举checked_ids，不把changed_items当旧候选。')
        prompt=request.system+('本次传输只需checked_batch_token确认本次candidate_items批次；checked_ids由程序根据候选清单生成，不要自行抄写。'
            '返回checked_batch_token、changes，可附no_change_reason/unresolved。批次确认不表示语义已获认证。')
        if 'repair' in payload:payload=self._feedback(payload)
        reply=self.gateway.complete(ModelRequest(request.role,prompt,payload,request.max_output_tokens))
        try:
            value,notes=normalize(strict_json(reply.content))
            if not isinstance(value,dict) or 'checked_batch_token' not in value:return reply
            if value['checked_batch_token']!=token:raise ContractError('Temporal batch acknowledgement differs')
            if 'checked_ids' in value and value['checked_ids']!=candidate_ids:
                raise ContractError('Conflicting temporal batch and candidate list')
            value.pop('checked_batch_token');value['checked_ids']=candidate_ids
            self.transforms.append(dict(role='temporal_batch_scope',token=token,candidate_ids=candidate_ids,
                raw_content=reply.content,normalizations=notes,
                semantic_certification=False,scope='Program-bound candidate batch; not per-item semantic proof'))
            return ModelReply(canonical(value),reply.input_tokens,reply.output_tokens,reply.cost_usd)
        except ContractError:
            return reply

    def _feedback(self,payload):
        try:return self._collect_feedback(payload)
        except (ContractError,TypeError,KeyError,AttributeError):
            # Feedback is additive. An unreadable previous reply must never
            # prevent the validator's existing repair request from being sent.
            return copy.deepcopy(payload)

    def _collect_feedback(self,payload):
        payload=copy.deepcopy(payload)
        prior,_=normalize(strict_json(payload['repair']['previous_output']))
        candidates={r['id']:r for r in payload['candidate_items']}
        changed={r['id'] for r in payload['changed_items']};errors=[]
        for op in prior.get('changes',[]):
            if op.get('id') not in candidates:
                errors.append(str(op.get('id'))+': 不在candidate_items，禁止reconcile；changed_items已经包含本章新增或更新，旧版本已归档，不是本步骤可修改的旧候选。')
            for index,res in enumerate(op.get('resolutions',[])):
                prefix=f"{op.get('id')} resolutions[{index}]"
                if not res.get('replacement_ids'):errors.append(prefix+': replacement_ids必须非空')
                if res.get('relation')!='completed' and not set(res.get('replacement_ids',[]))<=changed:
                    errors.append(prefix+': superseded只能引用changed_items')
        payload['repair']['all_detected_contract_errors']=errors
        payload['repair']['instruction']+=' 同时修复all_detected_contract_errors中全部问题，不仅首个；不通过删除已证实变化来规避校验。'
        return payload

    def _extract(self,request):
        if request.system!=MEMORY_SYSTEM:return self.gateway.complete(request)
        payload=copy.deepcopy(request.payload);bindings={}
        for number,row in enumerate(payload['memory_items'],1):
            alias=f'm{number:03d}';bindings[alias]=row['id'];row['id']=alias
            row['temporality']={k:v for k,v in row.get('temporality',{}).items()
                                  if k in ('time_scope','historical_part_count')}
        payload['memory_contract']['operations']=['add','update']
        payload['memory_contract']['update_optional_fields']=['kind (must match original)']
        # Repairs contain previous canonical IDs; those remain accepted only
        # when exactly present in this request's mapping.
        prompt=request.system+('本次id是请求局部短编号，更新时逐字选择所给mNNN。'
            '本步骤只提取add/update，分层交给后续步骤，不输出demote/recall。'
            '单个任务尽量只含一个可独立完成的行动。不要添加type字段。')
        reply=self.gateway.complete(ModelRequest(request.role,prompt,payload,request.max_output_tokens))
        transform=dict(bindings=bindings,raw_content=reply.content,normalizations=[])
        self.transforms.append(transform)
        try:
            value,notes=normalize(strict_json(reply.content));transform['normalizations']=notes
            if not isinstance(value,dict) or not isinstance(value.get('changes'),list):
                return reply
            stored=(self.full_memory['items'] if self.full_memory is not None else
                    {row['id']:row for row in request.payload['memory_items']})
            for operation in value['changes']:
                if not isinstance(operation,dict):continue
                attribute=operation.get('attribute') if isinstance(operation,dict) else None
                if operation.get('op')=='add' and attribute_identifier(attribute)!=attribute:
                    operation['attribute']=attribute_identifier(attribute)
                    transform['normalizations'].append(dict(rule='attribute_storage_identifier',old=attribute,new=operation['attribute']))
                if operation.get('op')=='add':container_status(operation,operation.get('kind'),transform['normalizations'])
                if operation.get('op')=='add' and operation.get('kind')=='state' and operation.get('status')=='active':
                    existing=[r for r in stored.values() if r['kind']=='state' and r['status']=='active' and has_current_content(r)
                        and (r['subject'],r['attribute'])==(operation.get('subject'),operation.get('attribute'))]
                    if len(existing)==1:
                        target=existing[0]
                        operation.update(op='update',id=target['id'],expected_revision=target['revision'],
                            reason='Program resolved the exact existing current-state property')
                        operation.pop('subject');operation.pop('attribute')
                        transform['normalizations'].append(dict(rule='exact_state_identity_upsert',id=target['id']))
                if 'id' not in operation:continue
                identifier=operation['id']
                if identifier in bindings:operation['id']=bindings[identifier]
                elif identifier not in bindings.values():
                    # Let the existing validator report an unknown ID and use
                    # its single repair. Never guess which item was intended.
                    transform['unknown_id']=identifier
                old=stored.get(operation['id'])
                if operation.get('op')=='update' and old is not None and 'kind' in old:
                    if 'kind' in operation and operation['kind']!=old['kind']:
                        transform['normalizations'].append(dict(rule='program_owned_kind',id=old['id'],requested=operation['kind'],actual=old['kind']))
                        operation['kind']=old['kind']
                    container_status(operation,old['kind'],transform['normalizations'])
            transform['normalized_content']=canonical(value)
            return ModelReply(transform['normalized_content'],reply.input_tokens,reply.output_tokens,reply.cost_usd)
        except ContractError:
            return reply


LAYER_SYSTEM=(
    '你负责三层记忆调度。输出JSON placements数组，每项仅id、tier、priority、reason。'
    '必须为提供的每个条目恰好返回一次决定，id选所给短编号，tier选该条allowed_tiers。'
    'working是接下来需持续携带的工作记忆：当前调查、证据所在、未完成行动及相关身份关系。'
    'recent是近期剧情可能用、但不必持续携带的信息；long是更远历史、已结束支线、可检索的旧线索。'
    '保持原层也可以。降级一次只下一层；recent/long可按需要调回working。'
    '不能为凑三层而强行归档，也不要把全部旧条目永久留在working。'
    'priority是1到5的整数，5最重要；程序根据优先级精确分配working_budget_bytes，不要求你做字节加法。'
    '明确未完成任务和核心当前状态优先，背景与已完成事件可以检索。超预算的工作候选只退到近期或保留原层，不删除。'
    '降级不删除内容、不改变有效期，历史信息调回也不变成当前事实。'
    '只能决定层级，不改事实、状态或类别。给出简短具体理由，不输出其它字段。'
)


class LayerAgent:
    def __init__(self,gateway):self.gateway=gateway
    def run(self,memory,chapters,number,focus,trace):
        # Intake must fit before selecting a bounded model request. A long new
        # chapter can otherwise make mandatory working records impossible to
        # select, so the very scheduler that could demote them never runs.
        working=[];overflow=[]
        rows=[r for r in memory['items'].values() if r['tier']=='working' and has_current_content(r)]
        for row in sorted(rows,key=lambda r:(r['kind']=='prose_excerpt',-max(s['chapter_number'] for s in r['sources']),r['id'])):
            wire=wire_item(row)
            if len(canonical(working+[wire]).encode('utf-8'))<=16000:working.append(wire)
            else:overflow.append(dict(op='demote',id=row['id'],expected_revision=row['revision'],reason='工作输入超预算，暂存近期，保留完整内容与来源供剧情调度'))
        staged=apply_delta(memory,dict(changes=overflow),chapters,f'layer-intake-{number}') if overflow else memory
        result,report=self._schedule(staged,chapters,number,focus,trace)
        report['intake_moves']=overflow
        report['moves']=overflow+report['moves']
        return result,report

    def _schedule(self,memory,chapters,number,focus,trace):
        pending=[i for i in memory.get('layer_deferred_ids',[]) if i in memory['items'] and has_current_content(memory['items'][i])]
        forced=[wire_item(r) for r in memory['items'].values() if r['tier']=='working' and has_current_content(r)]
        forced_ids={r['id'] for r in forced};required=[]
        for identifier in pending:
            row=wire_item(memory['items'][identifier])
            if identifier in forced_ids:required.append(identifier)
            elif len(canonical(forced+[row]).encode('utf-8'))<=96000:
                forced.append(row);forced_ids.add(identifier);required.append(identifier)
        selection=select_context(memory,query=focus,required_ids=required,max_bytes=96000)
        bindings={};items=[]
        for index,row in enumerate(selection['items'],1):
            alias=f't{index:03d}';bindings[alias]=row['id']
            allowed={'working':['working','recent'],'recent':['recent','long','working'],'long':['long','working']}[row['tier']]
            items.append(dict(id=alias,subject=row['subject'],attribute=row['attribute'],claim=row['claim'],
                kind=row['kind'],status=row['status'],tier=row['tier'],allowed_tiers=allowed,
                time_scope=row['temporality']['time_scope'],wire_bytes=len(canonical(row).encode('utf-8'))))
        if not items:return copy.deepcopy(memory),dict(status='EMPTY',moves=[],decisions=[],omitted_ids=selection['omitted_ids'])
        payload=dict(completed_chapter=number,current_focus=focus,items=items,
                     working_budget_bytes=16000,
                     instruction='仅根据已完成章节及当前未完成事项判断，不知道未来正文。')
        by_alias={row['id']:row for row in items};accepted={};deferred=[]
        for attempt in range(2):
            if len(canonical(dict(system=LAYER_SYSTEM,payload=payload)).encode('utf-8'))>120000:
                raise ContractError('Layer request exceeds bound')
            entry=dict(role='layers',chapter_number=number,attempt=attempt+1,bindings=bindings)
            trace.append(entry)
            reply=self.gateway.complete(ModelRequest('memory',LAYER_SYSTEM,copy.deepcopy(payload),8192))
            entry['raw_output']=reply.content
            try:
                parse_error=None
                try:
                    parsed,notes=normalize(strict_json(reply.content));fields(parsed,('placements',))
                    placements=parsed['placements']
                    if not isinstance(placements,list):raise ContractError('placements must be list')
                except (ContractError,TypeError,KeyError) as exc:
                    if not attempt or not accepted:raise
                    placements=[];notes=[];parse_error=str(exc)
                seen=set();operations=[];decisions=[];errors=[];duplicates=set();locked=set(accepted)
                if parse_error:errors.append(dict(id=None,error=parse_error))
                for placement in placements:
                    alias=placement.get('id') if isinstance(placement,dict) else None
                    try:
                        fields(placement,('id','tier','priority','reason'))
                        if not isinstance(alias,str) or alias not in bindings:
                            raise ContractError('Unknown tier ID')
                        if alias in duplicates:raise ContractError('Duplicate tier ID')
                        if alias in seen:raise ContractError('Duplicate tier ID')
                        seen.add(alias);row=by_alias[alias]
                        if alias in accepted:
                            if placement!=accepted[alias]:raise ContractError('Cannot overwrite an already accepted decision')
                            continue
                        if placement['tier'] not in row['allowed_tiers']:
                            raise ContractError(f'{alias}: tier must be one of {row["allowed_tiers"]}')
                        if type(placement['priority']) is not int or not 1<=placement['priority']<=5:
                            raise ContractError('priority must be an integer from 1 to 5')
                        if not isinstance(placement['reason'],str) or not placement['reason'].strip():raise ContractError('Tier reason required')
                        accepted[alias]=copy.deepcopy(placement)
                    except (ContractError,TypeError,KeyError) as exc:
                        errors.append(dict(id=alias,error=str(exc)))
                        # Ambiguous repeated decisions in this reply cannot be applied.
                        if isinstance(alias,str) and alias in seen and str(exc)=='Duplicate tier ID':
                            duplicates.add(alias)
                            if alias not in locked:accepted.pop(alias,None)
                missing=[alias for alias in bindings if alias not in accepted]
                if missing or errors:
                    entry.update(status='PARTIAL',errors=errors,accepted_ids=list(accepted),deferred_ids=missing)
                    if not attempt:
                        payload['items']=[by_alias[alias] for alias in missing]
                        payload['repair']=dict(errors=errors,missing_ids=missing,
                            instruction='只返回这些未完成条目的placements；之前正确决定已保留，不重写。每项tier只能从自身allowed_tiers选择。')
                        continue
                    if not accepted:raise ContractError('No valid tier decisions after repair')
                    deferred=missing
                    for alias in missing:
                        accepted[alias]=dict(id=alias,tier=by_alias[alias]['tier'],priority=5,
                            reason='本条调度未通过，保留原层等待后续重新整理')
                for alias in bindings:
                    placement=accepted[alias];identifier=bindings[alias];old=memory['items'][identifier]
                    decisions.append(dict(id=identifier,from_tier=old['tier'],requested_tier=placement['tier'],
                        to_tier=placement['tier'],priority=placement['priority'],reason=placement['reason']))
                working=[];budget_deferred=[]
                for decision in sorted((d for d in decisions if d['requested_tier']=='working'),
                                       key=lambda d:(-d['priority'],d['id'])):
                    row=wire_item(memory['items'][decision['id']])
                    row['tier']='working'
                    if decision['from_tier']!='working':row['revision']+=1
                    if len(canonical(working+[row]).encode('utf-8'))<=16000:working.append(row)
                    else:
                        # Do not perform two moves on a recalled long record;
                        # defer the recall and leave it in its original bank.
                        decision['to_tier']='recent' if decision['from_tier']=='working' else decision['from_tier']
                        decision['budget_deferred']=True;budget_deferred.append(decision['id'])
                for decision in decisions:
                    if decision['to_tier']==decision['from_tier']:continue
                    old=memory['items'][decision['id']]
                    operation='recall' if decision['to_tier']=='working' else 'demote'
                    reason=decision['reason']+('；按优先级暂存原层或近期以满足工作字节预算' if decision.get('budget_deferred') else '')
                    operations.append(dict(op=operation,id=decision['id'],expected_revision=old['revision'],reason=reason))
                delta=dict(changes=operations)
                if not operations:delta['no_change_reason']='Model explicitly kept every selected item in its current tier'
                result=apply_delta(memory,delta,chapters,f'chapter-layers-{number}')
                deferred_ids={bindings[alias] for alias in deferred}
                result['layer_deferred_ids']=sorted((set(pending)|deferred_ids)-(set(bindings.values())-deferred_ids))
                working=[wire_item(row) for row in result['items'].values()
                         if row['tier']=='working' and has_current_content(row)]
                if len(canonical(working).encode('utf-8'))>16000:
                    raise ContractError('Internal working allocation exceeds budget')
                entry.update(status='ACCEPTED_WITH_DEFERRED' if deferred else 'ACCEPTED',normalizations=notes)
                return result,dict(status='APPLIED_WITH_DEFERRED' if deferred else 'APPLIED',moves=operations,decisions=decisions,
                    deferred_ids=[bindings[alias] for alias in deferred],
                    budget_deferred=budget_deferred,working_bytes=len(canonical(working).encode('utf-8')),
                    omitted_ids=selection['omitted_ids'],selection_ids=selection['selected_ids'])
            except (ContractError,TypeError,KeyError) as exc:
                entry.update(status='REJECTED',error=str(exc))
                if attempt:raise ContractError('Layer decision failed: '+str(exc)) from exc
                payload['repair']=dict(error=str(exc),previous_output=reply.content,
                    instruction='修复所列格式/层级错误，完整返回placements，不删除正确决定。')


RECALL_SYSTEM=(
    '只根据提供的记忆回答问题，不依据常识猜测小说事实。输出JSON且只允许answer字符串、memory_ids数组这两个顶层字段。'
    'memory_ids只能选本次qNNN或hNNN引用，给出实际支持回答的记录。'
    'current_memory表示当前可用信息，historical_memory明确表示历史说法或旧版本。'
    '历史未找到而后来找到时应说明变化，不把旧判断复活。身份归属和人物已故状态要准确。'
    'source_evidence是已入库记录附带的原始证据，可以补充摘要遗漏的动作；证据是当时的记录，不自动代表现在。'
    '允许把明确指向同一具名人物或同一亲属关系的事实关联起来；没有相反证据，不凭空拆成不同人物。'
    '没有足够依据时写未知；有冲突则明确冲突。不要编造正文、来源或字段。'
)

RECALL_REVIEW_SYSTEM=RECALL_SYSTEM+(
    '现在复核draft_answer并给出最终answer和memory_ids。草案本身不是事实依据。'
    '逐项核对当前记忆、历史标签和已存证据，纠正自相矛盾、无依据的不确定、过度推断和漏读证据。'
    '如果已经认定某对象属于一个明确的人，就不能无依据否认同一人的其它明确属性适用于该对象主人。'
    '确实没有证据的问题仍写未知，不能为让测试通过而猜答案。')


def source_evidence_view(memory,selected_ids,bindings,query,max_bytes=24000):
    """Read stored bound quotes, never reopen the original chapter files."""
    terms=set(re.findall(r'[a-z0-9_]+',query.lower()))
    for match in re.finditer(r'[\u3400-\u9fff]+',query):
        value=match.group();terms.update(value[i:i+2] for i in range(len(value)-1))
    characters={c for c in query if '\u3400'<=c<='\u9fff' and c not in '的了在是谁是否与和及目前这那其中'}
    alias_by_id={b['memory_id']:alias for alias,b in bindings.items() if b['view']=='current'}
    clauses=[part for part in re.split(r'[？?；;。]',query) if part.strip()]
    ranked=[]
    for item_rank,identifier in enumerate(selected_ids):
        item=memory['items'][identifier];rows=[];seen=set()
        for source in item.get('sources',[]):
            key=(source['chapter_number'],source['evidence_id'])
            if key in seen:continue
            seen.add(key)
            score=sum(term in source['quote'].lower() for term in terms)+0.2*sum(c in source['quote'] for c in characters)
            rows.append((score,dict(memory_id=alias_by_id[identifier],chapter_number=key[0],evidence_id=key[1],quote=source['quote'],
                scope='Stored source quote; not a declaration that its earlier state is still current')))
        clause_winners=set()
        for clause in clauses:
            chars={c for c in clause if c in characters}
            pairs={clause[i:i+2] for i in range(len(clause)-1)}
            if rows:
                winner=max(rows,key=lambda r:(sum(p in r[1]['quote'] for p in pairs)+0.2*sum(c in r[1]['quote'] for c in chars),r[0]))
                clause_winners.add((winner[1]['chapter_number'],winner[1]['evidence_id']))
        for rank,(score,row) in enumerate(sorted(rows,key=lambda r:(-r[0],r[1]['chapter_number'],r[1]['evidence_id']))):
            # Reserve multiple subquestion witnesses for the most relevant records.
            # Remaining records still compete for the same explicit byte budget.
            priority=0 if item_rank<12 and (row['chapter_number'],row['evidence_id']) in clause_winners else 1+rank
            ranked.append((priority,score,identifier,row))
    selected=[];omitted=[]
    # Compound questions need distinct witnesses, not only one quote per record.
    for _,_,identifier,row in sorted(ranked,key=lambda r:(r[0],-r[1],r[2])):
        if len(canonical(selected+[row]).encode('utf-8'))<=max_bytes:selected.append(row)
        else:omitted.append(dict(memory_id=identifier,chapter_number=row['chapter_number'],evidence_id=row['evidence_id']))
    return dict(items=selected,omitted=omitted,bytes=len(canonical(selected).encode('utf-8')))


def parse_recall_answer(content,bindings):
    parsed,notes=normalize(strict_json(content))
    if isinstance(parsed,dict) and 'historical_memory_ids' in parsed:
        historical=parsed.pop('historical_memory_ids')
        if not isinstance(historical,list) or any(not isinstance(i,str) or i not in bindings or bindings[i]['view']!='historical' for i in historical):
            raise ContractError('Invalid separate historical recall references')
        if not isinstance(parsed.get('memory_ids'),list):raise ContractError('Invalid recall references')
        parsed['memory_ids']=list(dict.fromkeys(parsed['memory_ids']+historical))
        notes.append('Merged validated historical_memory_ids into memory_ids')
    fields(parsed,('answer','memory_ids'))
    if not isinstance(parsed['answer'],str) or not isinstance(parsed['memory_ids'],list):raise ContractError('Invalid recall answer')
    if any(not isinstance(i,str) or i not in bindings for i in parsed['memory_ids']):raise ContractError('Recall cites unknown memory')
    return parsed,notes


def recall_probe(memory,query,gateway,trace,label):
    current=recall_selection(memory,query,max_bytes=36000)
    history=select_history_context(memory,query=query,max_bytes=12000)
    bindings={};current_rows=[];old_rows=[]
    for n,row in enumerate(current['items'],1):
        alias=f'q{n:03d}';bindings[alias]=dict(memory_id=row['id'],view='current',tier=row['tier'])
        current_rows.append(dict(id=alias,subject=row['subject'],attribute=row['attribute'],claim=row['claim'],
                                 kind=row['kind'],status=row['status'],tier=row['tier'],
                                 **({'provenance_scope':row['provenance_scope']} if 'provenance_scope' in row else {})))
    for n,row in enumerate(history['items'],1):
        alias=f'h{n:03d}';bindings[alias]=dict(memory_id=row['memory_id'],view='historical',tier=memory['items'][row['memory_id']]['tier'])
        old_rows.append(dict(row,id=alias))
    evidence=source_evidence_view(memory,current['selected_ids'],bindings,query)
    payload=dict(question=query,current_memory=current_rows,historical_memory=old_rows,source_evidence=evidence['items'],
                 scope='Memory and its stored bound quotes only; no original chapter loaded, expected answer or future chapter supplied')
    repair_budget=[1]
    def request_answer(system,body,role):
        reply=gateway.complete(ModelRequest('reviewer',system,body,4096))
        try:parsed,notes=parse_recall_answer(reply.content,bindings)
        except ContractError as exc:
            trace.append(dict(role=role,label=label,status='FORMAT_REJECTED',raw_output=reply.content,error=str(exc)))
            if not repair_budget[0]:raise
            repair_budget[0]-=1
            repaired=dict(body,repair=dict(error=str(exc),previous_output=reply.content,
                instruction='仅修复JSON格式与字段。只返回answer和memory_ids；不得增加证据字段或发明引用。保持有依据的回答。'))
            reply=gateway.complete(ModelRequest('reviewer',system,repaired,4096))
            parsed,notes=parse_recall_answer(reply.content,bindings)
            notes.append('Used shared single recall format repair')
        return reply,parsed,notes
    reply,parsed,notes=request_answer(RECALL_SYSTEM,payload,'recall_draft')
    entry=dict(role='recall_draft',label=label,bindings=bindings,raw_output=reply.content)
    trace.append(entry)
    entry.update(status='DRAFT_RETURNED',normalizations=notes)
    review_payload=dict(payload,draft_answer=parsed)
    reply,parsed,notes=request_answer(RECALL_REVIEW_SYSTEM,review_payload,'recall')
    entry=dict(role='recall',label=label,bindings=bindings,raw_output=reply.content,consistency_review=True)
    trace.append(entry)
    cited=[bindings[i] for i in parsed['memory_ids']]
    entry.update(status='RETURNED',normalizations=notes)
    return dict(question=query,answer=parsed['answer'],references=cited,
        cited_long_term=sum(r['tier']=='long' for r in cited),
        cited_historical=sum(r['view']=='historical' for r in cited),
        retrieved_long_term=sum(r['tier']=='long' for r in current_rows),
        current_selection_ids=current['selected_ids'],current_omitted_ids=current['omitted_ids'],
        evidence_omitted=evidence['omitted'],evidence_bytes=evidence['bytes'],consistency_reviewed=True,
        historical_omitted_ids=history['omitted_ids'],semantic_correctness='PENDING_MANUAL_REVIEW')


def recall_selection(memory,query,max_bytes=36000):
    """Query-specific thin view, with one-hop subject expansion across tiers.

    Unlike the generation context, a recall query need not force every working
    item into its answer context. Only literal current information is ranked.
    """
    terms=set(re.findall(r'[a-z0-9_]+',query.lower()))
    for match in re.finditer(r'[\u3400-\u9fff]+',query):
        value=match.group();terms.update(value[i:i+2] for i in range(len(value)-1))
    rows=[]
    for identifier,item in memory['items'].items():
        if not has_current_content(item):continue
        row={k:item[k] for k in ('id','subject','attribute','kind','status','tier','revision')}
        row['claim']=current_claim(item);row['time_scope']=time_view(item)['time_scope']
        if 'provenance_scope' in item:row['provenance_scope']=item['provenance_scope']
        hay=canonical(row).lower();score=sum(term in hay for term in terms)
        rows.append((score,identifier,row))
    related={row['subject'] for _,_,row in rows if row['subject'] in query}
    related.update(row['subject'] for score,_,row in sorted(rows,key=lambda r:(-r[0],r[1]))[:5] if score>0)
    ranked=sorted(rows,key=lambda r:(-(r[0]+8*(r[2]['subject'] in related)),r[1]))
    selected=[];omitted=[]
    for score,identifier,row in ranked:
        if score==0 and row['subject'] not in related:
            omitted.append(identifier);continue
        if len(canonical(selected+[row]).encode('utf-8'))<=max_bytes:selected.append(row)
        else:omitted.append(identifier)
    return dict(items=selected,selected_ids=[r['id'] for r in selected],omitted_ids=omitted,
                bytes=len(canonical(selected).encode('utf-8')),retrieval='thin lexical with one-hop subject expansion')


class ReviewedTemporal:
    """Adjudicate uncertainty conservatively; never remove an actual conflict.

    A second model may only conclude keep-unconfirmed or remain-blocked. It
    cannot invent a replacement fact, delete evidence or alter old information.
    """
    def __init__(self,gateway):self.gateway=gateway
    def run(self,before,after,chapters,number,selection,trace,cached_request=None,cached_reply=None,
            _depth=0,_budget=None):
        budget={'repairs':1} if _budget is None else _budget
        def use_repair():
            if budget['repairs']<=0:raise ContractError('Temporal format repair budget exhausted; chapter remains pending')
            budget['repairs']-=1
        requests=[];replies=[];owner=self
        class Capture:
            used=False
            def complete(self,request):
                requests.append(copy.deepcopy(request))
                if cached_request is not None and not self.used:
                    if request.system!=cached_request['system'] or request.payload!=cached_request['payload']:
                        raise ContractError('Cached temporal reply request differs')
                    self.used=True;reply=ModelReply(**cached_reply)
                else:
                    if 'repair' in request.payload:use_repair()
                    reply=owner.gateway.complete(request)
                replies.append(reply);return reply
        try:
            return TemporalReconciler(Capture()).run(before,after,chapters,number,selection,trace)
        except TemporalUnresolved:
            if _depth>=3:raise TemporalUnresolved('Uncertainty review round limit reached; chapter remains pending')
            issue_entry=trace[-1];issues=issue_entry['issues']
            payload=dict(chapter_number=number,issues=[dict(ref=f'u{i:03d}',old_record=wire_item(after['items'][issue['id']]),
                questioned_parts=issue['part_ids'],uncertainty_reason=issue['reason']) for i,issue in enumerate(issues,1)],
                new_records=[wire_item(row) for identifier,row in after['items'].items() if identifier not in before['items'] or row!=before['items'][identifier]],
                evidence_segments=requests[-1].payload['evidence_segments'])
            prompt=('复核时效整理中的未解决问题。只输出JSON decisions数组，每项ref、decision、reason。'
                'decision只能keep_unconfirmed或block。未证明旧安排完成/取消、只因未提及或时间锚点不明时，keep_unconfirmed，保留原内容和不确定说明。'
                '本章明确推翻旧现状却缺少新记忆、明确冲突、无法安全拆分时block。不能为了继续测试而放行。'
                '逐个判断所给问题，不改事实，不添加替代记忆，不把不确定当已完成。')
            reply=self.gateway.complete(ModelRequest('reviewer',prompt,payload,4096))
            parsed,notes=normalize(strict_json(reply.content));fields(parsed,('decisions',))
            decisions=parsed['decisions'];wanted={f'u{i:03d}' for i in range(1,len(issues)+1)}
            if not isinstance(decisions,list):raise ContractError('Uncertainty decisions must be list')
            seen=set()
            for decision in decisions:
                fields(decision,('ref','decision','reason'))
                if decision['ref'] not in wanted or decision['ref'] in seen:raise ContractError('Invalid uncertainty review coverage')
                seen.add(decision['ref'])
                if decision['decision'] not in ('keep_unconfirmed','block') or not isinstance(decision['reason'],str):raise ContractError('Invalid uncertainty disposition')
            if seen!=wanted:raise ContractError('Uncertainty review incomplete')
            trace.append(dict(role='uncertainty_review',chapter_number=number,raw_output=reply.content,decisions=decisions,
                              normalizations=notes,status='RETURNED'))
            if any(d['decision']=='block' for d in decisions):raise TemporalUnresolved('Uncertainty review retained blocking issue')
            # Replay the unchanged first-stage decisions, removing only the
            # separately reviewed keep-unconfirmed requests. Full checks still run.
            raw,_=normalize(strict_json(replies[-1].content))
            bindings=issue_entry['wire_bindings'];expanded=decode(raw,bindings)
            kept={issue['id'] for issue in issues}
            protected={identifier:{pid for issue in issues if issue['id']==identifier for pid in issue['part_ids']}
                       for identifier in kept}
            placeholders={op['id'] for op in expanded['changes'] if op['id'] in kept
                and op.get('resolutions') and all(not r.get('part_ids') and not r.get('replacement_ids')
                    and not r.get('source_refs') for r in op['resolutions'])}
            if any(op['id'] in kept-placeholders and any(set(r['part_ids'])&protected[op['id']]
                   for r in op['resolutions']) for op in expanded['changes']):
                raise ContractError('Cannot both retain and reconcile the same uncertain portion')
            # Empty unresolved placeholders carry no actionable parts/evidence.
            # A keep-unconfirmed verdict leaves these targets wholly unchanged.
            raw['changes']=[op for op,decoded in zip(raw['changes'],expanded['changes']) if decoded['id'] not in placeholders]
            raw['unresolved']=[]
            if not raw['changes']:raw['no_change_reason']='Reviewed uncertain arrangements retained unchanged and unconfirmed'
            class Replay:
                def complete(self,request):
                    if 'repair' in request.payload:
                        use_repair()
                        # Remaining proposals still obey the original format
                        # checks and its single paid repair, with review intact.
                        request.payload['repair']['instruction']+=' 已独立复核的未证实旧安排须保持不变，不能重新将其判为完成或替代。所有replacement_ids必须非空且只能选changed_items编号（即使relation=completed也一样），不能引用candidate_items旧记录；缺少本章新替代记录时不得提交该项完成操作。逐项核对全部引用后完整返回。'
                        return owner.gateway.complete(request)
                    expected={k:v for k,v in requests[-1].payload.items() if k!='repair'}
                    if request.system!=requests[-1].system or request.payload!=expected:
                        raise ContractError('Temporal control replay changed inputs')
                    return ModelReply(canonical(raw),0,0,0)
            try:
                result=TemporalReconciler(Replay()).run(before,after,chapters,number,selection,trace)
            except TemporalUnresolved:
                # A repair may discover a different semantic issue. Re-enter
                # the review state with that exact recorded reply; never send
                # another paid initial request or reset the repair budget.
                pending=trace[-1]['raw_output']
                base={k:v for k,v in requests[0].payload.items() if k!='repair'}
                result=self.run(before,after,chapters,number,selection,trace,
                    cached_request=dict(system=requests[0].system,payload=base),
                    cached_reply=dict(content=pending,input_tokens=0,output_tokens=0,cost_usd=0),
                    _depth=_depth+1,_budget=budget)
            for identifier,part_ids in protected.items():
                old_parts={p['id']:p for p in annotated(after['items'][identifier])['temporality']['parts']}
                new_parts={p['id']:p for p in annotated(result['items'][identifier])['temporality']['parts']}
                if any(new_parts.get(pid)!=old_parts[pid] for pid in part_ids):
                    raise ContractError('Repair changed a reviewed keep-unconfirmed portion')
            result.setdefault('uncertain_prior_arrangements',[]).append(dict(chapter_number=number,issues=issues,review=decisions,
                disposition='Kept unchanged and unconfirmed; no semantic replacement asserted'))
            trace[-1]['program_replay_after_uncertainty_review']=True
            return result


class ReviewedMemoryAgent:
    def __init__(self,gateway):
        from inf_writer.tiered_runtime import TieredMemoryAgent
        self.extractor=TieredMemoryAgent(gateway);self.reconciler=ReviewedTemporal(gateway)
    def extract(self,memory,chapters,number,selection,trace):
        after=self.extractor.extract(memory,chapters,number,selection,trace)
        return self.reconciler.run(memory,after,chapters,number,selection,trace)
