"""Post-extraction time reconciliation; never commits partial chapter memory."""
import copy

from .domain import ContractError, canonical, fields, strict_json, evidence_segments
from .models import ModelRequest
from .tiered_memory import apply_delta, wire_item
from .temporal_transport import encode,decode

SYSTEM=(
    '你是记忆时效整理智能体。只输出JSON checked_ids、changes，可附no_change_reason。'
    '先比较旧认识与本章变化，不因未提及、年久或暂时不用而判失效。'
    '章节编号表示获知/证据顺序，不直接证明故事时间先后，回忆和倒叙不可误当当前变化。'
    'checked_ids必须逐一列出本次candidate_items的全部id，表示你已检查；不要填写未提供的id。'
    '同一旧认识可能存在于多个条目；每份仍作为当前依据的副本都要判断，不能因已整理其中一份而略过其它副本。'
    '只有被本章明确取代的片段才用reconcile。不能因复合条目中一部分过时就使整条失效。'
    '片段只提供原文定位，不保证语义独立；不能切断条件、否定或指代依赖。无法安全保留其余语义则报告unresolved。'
    '每项操作字段op=reconcile/id/expected_revision/reason/as_of_chapter/resolutions。'
    'resolutions每项part_ids/replacement_ids/relation/source_refs/reason。'
    'part_ids选旧条目temporality.current_parts的编号；replacement_ids选本章已有变化记录的稳定id；'
    'relation为superseded，明确任务片段的已完成部分用completed，与容器的kind无关。不得因此改变整条kind或使报告/历史事件本身失效，未完成及非任务片段必须保留。'
    'source_refs每项chapter_number/evidence_id，选本章证据。'
    '新旧认识之间须有明确依据，历史事件的确发生过不因后续变化而被判没发生；'
    '只移出旧的当前判断，例如未找到变为已找到，尚未行动变为行动完成。'
    '未变化片段由程序原样保留，正文、原句和旧来源都不删除；无需重抄旧句。'
    '本章证明旧认识有变，但changed_items没有对应新记录时，不可默认无变化；'
    '返回unresolved数组，每项id、part_ids、reason，说明缺哪条新记录或哪项语义未定。'
    '无变化返回changes=[]并说明原因；不负责降级层级，不允许借此改类别、改事实。'
)


class TemporalUnresolved(ContractError):
    """Semantic/extraction gap; a format-only retry cannot resolve it."""


class TemporalReconciler:
    def __init__(self,gateway,max_input_bytes=120000,max_output_tokens=8192):
        self.gateway=gateway;self.max_input_bytes=max_input_bytes;self.max_output_tokens=max_output_tokens

    def run(self,before,after,chapters,number,selection,trace):
        changed=[row for identifier,row in after['items'].items()
                 if identifier not in before['items'] or row!=before['items'][identifier]]
        # Explicit updates already archive the old version. Inspect untouched
        # selected old items, including mixed legacy records, for cross-item expiry.
        candidate_ids=[identifier for identifier in selection['selected_ids']
                       if identifier in before['items'] and before['items'][identifier]==after['items'][identifier]]
        if not candidate_ids:
            result=copy.deepcopy(after)
            result['temporal_processed_through']=number
            trace.append(dict(role='temporal',status='NOT_NEEDED',chapter_number=number,
                              semantic_certification=False))
            return result
        payload=dict(chapter_number=number,
            candidate_items=[wire_item(after['items'][identifier]) for identifier in candidate_ids],
            changed_items=[wire_item(row) for row in changed],
            evidence_segments=evidence_segments(chapters[number-1]['text']),
            coverage=dict(omitted_ids=selection['omitted_ids'],scope='selected-items-only',
                          semantic_verification='model judgment, not certified'))
        payload,bindings=encode(payload)
        for attempt in range(2):
            size=len(canonical(dict(system=SYSTEM,payload=payload)).encode('utf-8'))
            if size>self.max_input_bytes:
                raise ContractError('Temporal request exceeds bound; no silent dropping of required checks')
            entry=dict(role='temporal',attempt=attempt+1,chapter_number=number,input_bytes=size,
                       wire_bindings=copy.deepcopy(bindings))
            trace.append(entry)
            reply=self.gateway.complete(ModelRequest('memory',SYSTEM,copy.deepcopy(payload),self.max_output_tokens))
            entry['raw_output']=reply.content
            try:
                result=strict_json(reply.content)
                # Match the existing project's narrow JSON metadata policy.
                # This field changes no memory content; other values/keys are
                # still rejected. Preserve the raw reply and normalization log.
                if isinstance(result,dict) and 'type' in result:
                    if result['type']!='json_object':
                        raise ContractError('Optional type must be exactly json_object')
                    result={k:v for k,v in result.items() if k!='type'}
                    entry['normalizations']=[dict(field='type',value='json_object',rule='exact_json_metadata')]
                fields(result,('checked_ids','changes'),('no_change_reason','unresolved'))
                result=decode(result,bindings)
                checked=result['checked_ids']
                if (not isinstance(checked,list) or any(not isinstance(i,str) for i in checked)
                    or len(set(checked))!=len(checked) or set(checked)!=set(candidate_ids)):
                    raise ContractError('checked_ids must cover each candidate exactly once')
                if not isinstance(result['changes'],list):raise ContractError('changes must be list')
                unresolved=result.get('unresolved',[])
                if not isinstance(unresolved,list):raise ContractError('unresolved must be list')
                for issue in unresolved:
                    fields(issue,('id','part_ids','reason'))
                    if issue['id'] not in candidate_ids or not isinstance(issue['part_ids'],list) or not issue['part_ids']:
                        raise ContractError('Unresolved issue must identify a supplied candidate and its parts')
                    valid={p['id'] for p in wire_item(after['items'][issue['id']])['temporality']['current_parts']}
                    if not set(issue['part_ids'])<=valid or not isinstance(issue['reason'],str) or not issue['reason'].strip():
                        raise ContractError('Unresolved issue has unknown parts or empty reason')
                if unresolved:
                    entry.update(status='UNRESOLVED',issues=copy.deepcopy(unresolved),semantic_certification=False)
                    raise TemporalUnresolved('TEMPORAL_UNRESOLVED: '+canonical(unresolved))
                for operation in result['changes']:
                    if (operation.get('op')!='reconcile' or operation.get('id') not in candidate_ids
                        or operation.get('as_of_chapter')!=number):
                        raise ContractError('Only reconcile supplied candidates using this chapter')
                    for resolution in operation.get('resolutions',[]):
                        allowed=(set(after['items']) if resolution.get('relation')=='completed'
                                 else set(row['id'] for row in changed))
                        if not set(resolution['replacement_ids'])<=allowed:
                            raise ContractError('Replacement must be among this chapter changes')
                delta={k:v for k,v in result.items() if k not in ('checked_ids','unresolved')}
                reconciled=apply_delta(after,delta,chapters,f'chapter-time-{number}')
                reconciled['temporal_processed_through']=number
                entry.update(status='ACCEPTED',checked_ids=checked,changes=len(result['changes']),
                             coverage_scope='selected-items-only',semantic_certification=False)
                return reconciled
            except TemporalUnresolved:
                raise
            except (ContractError,KeyError,TypeError,AttributeError) as exc:
                entry.update(status='REJECTED',error=str(exc))
                if attempt:raise ContractError('Temporal reconciliation failed: '+str(exc)) from exc
                payload['repair']=dict(error=str(exc),previous_output=reply.content,
                    instruction='只修格式或所列引用错误；不要使未变化事实失效，不删正文。')


class TemporalMemoryAgent:
    role='memory'
    def __init__(self,gateway):
        from .tiered_runtime import TieredMemoryAgent
        self.extractor=TieredMemoryAgent(gateway)
        self.reconciler=TemporalReconciler(gateway)

    def extract(self,memory,chapters,number,selection,trace):
        after=self.extractor.extract(memory,chapters,number,selection,trace)
        # The caller only gets a candidate once BOTH phases pass. A failure
        # leaves the chapter pending rather than publishing stale mixed states.
        return self.reconciler.run(memory,after,chapters,number,selection,trace)
