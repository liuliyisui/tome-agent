"""Exact bound reference aliases; never changes an editorial judgment."""
import copy
from inf_writer.domain import ContractError,canonical,strict_json,fields,text,digest
from inf_writer.models import ModelReply,ModelRequest
from inf_writer.light_memory import prepare_review,validate_light_review,REVIEW_PROMPT,NOT_CHECKED

STORY_WIRE_RULES='hard_references中的$story_ref是本输入内的无损引用。field=current_draft取原文，recent_chapters取index对应的text，constraints取index对应字符串，active_facts取index对应对象去掉source后的规范JSON。start/end是Python字符串字符区间；缺省表示全文。basis_ref仍用原参考键，basis_quote从解析后的原文逐字摘录。不得引用指针字符串或凭空补充证据。'


def compact_story_context(context):
    """Share existing evidence text, with a verified reversible wire encoding."""
    if 'story_reference_transport' in context:raise ContractError('Reserved story transport field')
    wire=copy.deepcopy(context);sources=[]
    if isinstance(context.get('current_draft'),str):sources.append((dict(field='current_draft'),context['current_draft']))
    for index,row in enumerate(context.get('recent_chapters',[])):sources.append((dict(field='recent_chapters',index=index),row['text']))
    for index,row in enumerate(context.get('constraints',[])):sources.append((dict(field='constraints',index=index),row))
    for index,row in enumerate(context.get('active_facts',[])):
        sources.append((dict(field='active_facts',index=index),canonical({k:v for k,v in row.items() if k!='source'})))
    for key,value in wire['hard_references'].items():
        if not isinstance(value,str):raise ContractError('Logical story references must be text')
        for target,source in sources:
            start=source.find(value)
            if start<0:continue
            pointer=dict(target)
            if value!=source:pointer.update(start=start,end=start+len(value))
            alias={'$story_ref':pointer}
            if len(canonical(alias).encode('utf-8'))<len(canonical(value).encode('utf-8')):
                wire['hard_references'][key]=alias;break
    wire['story_reference_transport']=dict(version=1,logical_sha256=digest(canonical(context)),rules=STORY_WIRE_RULES)
    if expand_story_context(wire)!=context:raise ContractError('Story reference roundtrip changed evidence')
    return wire


def expand_story_context(wire):
    result=copy.deepcopy(wire);metadata=result.pop('story_reference_transport',{})
    if set(metadata)!={'version','logical_sha256','rules'} or type(metadata['version']) is not int or metadata['version']!=1 or metadata['rules']!=STORY_WIRE_RULES:
        raise ContractError('Invalid story reference transport')
    for key,value in wire['hard_references'].items():
        if isinstance(value,str):continue
        fields(value,('$story_ref',));pointer=value['$story_ref'];fields(pointer,('field',),('index','start','end'))
        field=pointer['field']
        if field=='current_draft':
            if 'index' in pointer:raise ContractError('Invalid story source index')
            source=wire[field]
        elif field in ('recent_chapters','constraints','active_facts'):
            index=pointer.get('index')
            if type(index) is not int or not 0<=index<len(wire.get(field,[])):raise ContractError('Invalid story source index')
            source=wire[field][index]
            if field=='recent_chapters':source=source['text']
            elif field=='active_facts':source=canonical({k:v for k,v in source.items() if k!='source'})
        else:raise ContractError('External or cyclic story reference forbidden')
        start=pointer.get('start',0);end=pointer.get('end',len(source))
        if not isinstance(source,str) or type(start) is not int or type(end) is not int or not 0<=start<=end<=len(source):raise ContractError('Invalid story reference span')
        result['hard_references'][key]=source[start:end]
    if digest(canonical(result))!=metadata['logical_sha256']:raise ContractError('Expanded story evidence hash mismatch')
    return result


class StoryReferenceGateway:
    def __init__(self,gateway):self.gateway=gateway;self.transforms=[]
    def complete(self,request):
        outgoing=request
        if request.payload.get('review_mode')=='light_memory':
            logical_bytes=len(canonical(dict(system=request.system,payload=request.payload)).encode('utf-8'))
            if logical_bytes>120000:
                wire=compact_story_context(request.payload)
                wire_bytes=len(canonical(dict(system=request.system,payload=wire)).encode('utf-8'))
                self.transforms.append(dict(role='story_reference_transport',status='LOSSLESS_WIRE_COMPACTED',logical_bytes=logical_bytes,wire_bytes=wire_bytes,logical_sha256=digest(canonical(request.payload))))
                if wire_bytes>120000:raise ContractError('Story review evidence exceeds input budget after lossless sharing')
                outgoing=ModelRequest(request.role,request.system,wire,request.max_output_tokens)
        reply=self.gateway.complete(outgoing)
        if request.role!='reviewer' or request.payload.get('review_mode')!='light_memory':return reply
        try:parsed=strict_json(reply.content)
        except ContractError:return reply
        if not isinstance(parsed,dict) or not isinstance(parsed.get('issues'),list):return reply
        aliases={};ambiguous=set();refs=request.payload.get('hard_references',{})
        for n,fact in enumerate(request.payload.get('active_facts',[]),1):
            identifier=fact.get('memory_id');alias=f'fact_{n}'
            if not isinstance(identifier,str) or alias not in refs:continue
            if identifier in aliases:ambiguous.add(identifier)
            aliases[identifier]=alias
        changed=[];normalized=copy.deepcopy(parsed)
        for issue in normalized['issues']:
            if not isinstance(issue,dict):continue
            original=issue.get('basis_ref')
            if isinstance(original,str) and original in aliases and original not in ambiguous and original not in refs:
                issue['basis_ref']=aliases[original]
                changed.append(dict(original=original,resolved=aliases[original]))
        if not changed:return reply
        self.transforms.append(dict(role='story_reference_transport',raw_output=reply.content,mappings=changed,
            rule='Exact memory_id from this request mapped to its factual reference; decision and quotes unchanged'))
        return ModelReply(canonical(normalized),reply.input_tokens,reply.output_tokens,reply.cost_usd)


REVIEW_RULES=(
    '先区分真正冲突与新增剧情：旧记忆未写某事，不等于禁止后来发生。'
    '约九点会面、八点四十到达可以是提前到场；只有明确互斥的到场事实才算冲突。'
    '人物后来收到地址、想起线索、改变安排，正文有交代时可成立，不因旧记忆未知就否定。'
    '相似对话不自动是同一次事件；结合日期、场景和新问题判断。'
    '自己判断不构成硬冲突的内容只能放suggestions，不得列入issues。'
)
CONSISTENCY_SYSTEM=(
    '独立复核正文审核提案。提案只是待核意见，不是事实。只用所给正文、此前章节及绑定参考。'
    +REVIEW_RULES+
    '输出JSON decisions，每项ref、classification(confirmed/suggestion/unresolved)、reason、'
    'draft_evidence字符串数组、basis_evidence字符串数组。每个ref恰好一次。'
    'confirmed必须指出无法同时成立的同一主体/事件/时间的断言，且两组证据各至少一段逐字引文；'
    'draft_evidence从current_draft摘，basis_evidence从该项cited_basis摘，不能改写或猜测。'
    'suggestion表示不成立为硬矛盾或仅为写作建议，理由需解释；无法判断用unresolved。'
    '不能为让流程通过而移除真实矛盾；也不能把不确定强行判成错误。'
)


def normalize_proposal(value,payload):
    """Fill optional advice only after the original judgment validates intact."""
    notes=[];value=copy.deepcopy(value)
    if isinstance(value,dict) and set(value)=={'approved','issues'}:
        candidate=dict(value,suggestions=[])
        validate_light_review(candidate,payload)
        value=candidate;notes.append(dict(rule='missing_optional_suggestions',default=[]))
    return value,notes


def adjudicate_issues(proposal,payload,gateway,trace):
    validate_light_review(proposal,payload)
    if not proposal['issues']:
        return dict(proposal,proposed_issues=[],unresolved_issues=[],dismissed_issues=[],adjudication_status='NOT_NEEDED')
    candidates=[dict(ref=f'i{n:03d}',proposed_issue=copy.deepcopy(issue),
        cited_basis=payload['hard_references'][issue['basis_ref']]) for n,issue in enumerate(proposal['issues'],1)]
    body=dict(issue_consistency_review=True,current_draft=payload['current_draft'],
        recent_chapters=payload.get('recent_chapters',[]),candidates=candidates)
    expected={r['ref']:r for r in candidates};decisions=None
    try:
        for attempt in range(2):
            if len(canonical(dict(system=CONSISTENCY_SYSTEM,payload=body)).encode('utf-8'))>120000:
                raise ContractError('Story issue review exceeds explicit input budget')
            reply=gateway.complete(ModelRequest('reviewer',CONSISTENCY_SYSTEM,copy.deepcopy(body),8192))
            entry=dict(role='story_issue_review',attempt=attempt+1,raw_output=reply.content);trace.append(entry)
            try:
                value=strict_json(reply.content);fields(value,('decisions',))
                if not isinstance(value['decisions'],list):raise ContractError('Issue decisions must be a list')
                checked={}
                for row in value['decisions']:
                    fields(row,('ref','classification','reason','draft_evidence','basis_evidence'))
                    ref=row['ref']
                    if not isinstance(ref,str) or ref not in expected or ref in checked:raise ContractError('Invalid or duplicate issue decision')
                    if row['classification'] not in ('confirmed','suggestion','unresolved'):raise ContractError('Invalid issue classification')
                    text(row['reason'],'Issue review reason')
                    for key,source in (('draft_evidence',payload['current_draft']),('basis_evidence',expected[ref]['cited_basis'])):
                        if not isinstance(row[key],list):raise ContractError('Issue evidence must be a list')
                        for quote in row[key]:
                            if text(quote,'Issue evidence quote') not in source:raise ContractError('Issue review quote absent from bound source')
                        if row['classification']!='unresolved' and not row[key]:raise ContractError('Issue classification requires both sides of evidence')
                    checked[ref]=row
                if set(checked)!=set(expected):raise ContractError('Issue decision coverage incomplete')
                decisions=checked;entry['status']='REVIEWED';break
            except ContractError as exc:
                entry.update(status='FORMAT_REJECTED',error=str(exc))
                if attempt:raise
                body['repair']=dict(error=str(exc),previous_output=reply.content,
                    instruction='只修格式、引用和覆盖范围；保留正确判断，不编造引文，不删问题逃避复核。')
    except Exception as exc:
        trace.append(dict(role='story_issue_review',status='UNRESOLVED',error_type=type(exc).__name__))
        return dict(proposal,approved=False,proposed_issues=copy.deepcopy(proposal['issues']),issues=[],
            unresolved_issues=[dict(issue=copy.deepcopy(issue),reason='Independent issue review incomplete') for issue in proposal['issues']],
            dismissed_issues=[],adjudication_status='UNRESOLVED')
    confirmed=[];unresolved=[];dismissed=[]
    for row in candidates:
        decision=decisions[row['ref']];issue=copy.deepcopy(row['proposed_issue'])
        if decision['classification']=='confirmed':confirmed.append(issue)
        else:
            target=dismissed if decision['classification']=='suggestion' else unresolved
            target.append(dict(issue=issue,review=decision))
    return dict(proposal,approved=not confirmed and not unresolved,issues=confirmed,
        proposed_issues=copy.deepcopy(proposal['issues']),unresolved_issues=unresolved,
        dismissed_issues=dismissed,issue_decisions=list(decisions.values()),adjudication_status='REVIEWED')


class StoryReviewAgent:
    """Format handling and issue adjudication have separate, bounded purposes."""
    def __init__(self,gateway):self.gateway=gateway
    def run(self,context,trace):
        payload=prepare_review(context);locked=None
        for attempt in range(2):
            reply=self.gateway.complete(ModelRequest('reviewer',REVIEW_PROMPT+REVIEW_RULES,copy.deepcopy(payload),8192))
            entry=dict(role='reviewer',attempt=attempt+1,raw_output=reply.content);trace.append(entry)
            parsed=None
            try:
                parsed=strict_json(reply.content)
                # A structurally valid original decision is immutable during
                # format-only repair; semantic reconsideration is a separate call.
                if locked is not None and (not isinstance(parsed,dict) or {k:parsed.get(k) for k in ('approved','issues')}!=locked):
                    raise ContractError('Format repair changed protected editorial judgment')
                value,notes=normalize_proposal(parsed,payload);validate_light_review(value,payload)
                entry.update(status='ACCEPTED',normalizations=notes)
                result=adjudicate_issues(value,payload,self.gateway,trace)
                return dict(result,memory_check=copy.deepcopy(NOT_CHECKED))
            except ContractError as exc:
                entry.update(status='FORMAT_FAILED',error=str(exc))
                if attempt:raise
                if isinstance(parsed,dict):
                    core={k:parsed.get(k) for k in ('approved','issues')}
                    try:validate_light_review(dict(core,suggestions=[]),payload)
                    except ContractError:pass
                    else:locked=copy.deepcopy(core)
                payload['repair']=dict(error=str(exc),previous_output=reply.content,
                    protected_judgment=locked,instruction='仅修格式；若protected_judgment非空，approved和issues必须原样保留。不得以批准/删意见代替格式修复。')
