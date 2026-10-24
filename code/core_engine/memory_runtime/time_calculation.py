"""Writer-owned time calculations. No editorial decisions or free prose rewriting."""
import copy
from datetime import datetime, timedelta
import re

from inf_writer.domain import ContractError, canonical, fields, strict_json, text
from inf_writer.models import ModelRequest


CONTRACT = {
    'version': 1,
    'instruction': (
        '时间运算由程序完成，不心算。调用方可输出可选time_calculations数组，具体角色权限由写作流程规定。'
        '每项id(英文标识)、kind(interval/duration/advance)，interval用start/end，'
        'duration用opened/closed，advance用actual/scheduled；时间为HH:MM或YYYY-MM-DDTHH:MM。'
        '纯钟点跨日必须显式day_offset=1，否则不猜次日；同日可省略。不要输出计算结果。'
        '正文计算所得分钟数使用[[time:标识]]，程序替换成准确的“几分钟”。'
        '可用[[time:标识.start]]和[[time:标识.end]]引用程序绑定的起止时刻。'
        '已提供computed_times的输入不得改动；修改时间需用新id重新计算。'
        '明确的相隔、间隔、耗时、合计分钟数及“这几分钟”等回指须使用绑定，'
        '不要把接电间隔当提前量，提前量必须另给scheduled，持续时间必须有closed。'
        '独立的计划等待时长、文书引述中的数字不是自动推算出的结果；不宣称本工具验证其真实性。'
        '模糊或相对约定（如后天傍晚、天黑前）直接保留在事件statement及计划value中，不是计算请求。'
        '没有精确起止输入时time_calculations留空，不猜钟点，不造新kind，不提交expression/result。'
    ),
}
KINDS = {'interval': ('start', 'end'), 'duration': ('opened', 'closed'), 'advance': ('actual', 'scheduled')}
CONTRACT['request_schemas']={kind:dict(required=['id','kind',*endpoints],optional=['day_offset'],
    kind=kind,input_format='HH:MM or YYYY-MM-DDTHH:MM',
    example=dict(id='example_time',kind=kind,**dict(zip(endpoints,('16:41','16:45')))))
    for kind,endpoints in KINDS.items()}
TOKEN = re.compile(r'\[\[time:([A-Za-z][A-Za-z0-9_]{0,31})(?:\.(start|end))?\]\]')
CLOCK_PAIR = re.compile(
    r'(?P<start>(?:[01]\d|2[0-3]):[0-5]\d)\s*(?:到|至|—|→)\s*'
    r'(?P<end>(?:[01]\d|2[0-3]):[0-5]\d)[^。！？\n]{0,40}?'
    r'(?:中间隔了?|相隔(?:了)?|间隔(?:了|为|是)?)\s*$')
NUM = r'(?:[0-9]+|[零〇一二两三四五六七八九十百千万]+)'
# Intentionally narrow: these phrases assert a computed amount. A bare "等两分钟"
# or a report saying "提前四分钟" does not prove there is a calculation to check.
ASSERTION = re.compile(
    rf'(?:中间隔了?|相隔(?:了)?|间隔(?:了|为|是)?|合计(?:为)?|加起来(?:是)?|'
    rf'一共(?:用|花)了?|共(?:用|花)了?|耗时(?:为|是)?|持续了|共开了|这)\s*'
    rf'(?P<amount>{NUM}\s*分钟)')


def _clock(value):
    if not isinstance(value, str):
        raise ContractError('Time input must be a clock or dated minute string')
    try:
        if re.fullmatch(r'\d{2}:\d{2}', value):
            return datetime.strptime('2000-01-01T' + value, '%Y-%m-%dT%H:%M'), False
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', value):
            return datetime.strptime(value, '%Y-%m-%dT%H:%M'), True
    except ValueError:
        pass
    raise ContractError('Invalid time; use HH:MM or YYYY-MM-DDTHH:MM')


def _amount(minutes):
    # Fixed rendering avoids a second model arithmetic step.
    digits = '零一二三四五六七八九'
    if minutes < 10:
        return digits[minutes] + '分钟'
    if minutes < 100:
        tens, ones = divmod(minutes, 10)
        return (digits[tens] if tens > 1 else '') + '十' + (digits[ones] if ones else '') + '分钟'
    return str(minutes) + '分钟'


def calculate(requests, existing=()):
    """Validate tool input before state simulation, with an actionable request path."""
    try:
        return _calculate(requests,existing)
    except ContractError as exc:
        # Locate each invalid row independently; never drop it or invent endpoints.
        issues=[]
        if isinstance(requests,list):
            prior=list(existing)
            for index,row in enumerate(requests):
                try:prior=_calculate([row],prior)
                except ContractError as error:
                    issues.append(dict(path=f'time_calculations[{index}]',request=copy.deepcopy(row),error=str(error)))
        exc.repair_details=dict(code='TIME_REQUEST_ERRORS',issues=issues,error=str(exc),
            request_schemas=copy.deepcopy(CONTRACT['request_schemas']),
            instruction='Only exact endpoint arithmetic belongs here. Preserve vague/relative appointments in event statements and planned values, with no invented clock time or numeric result. If no calculation is needed return time_calculations: []. Preserve all other correct events. Never remove a request referenced by [[time:id]] without replanning its dependent statement.')
        raise


def _calculate(requests, existing=()):
    if not isinstance(requests, list) or len(requests) > 32:
        raise ContractError('time_calculations must be a list of at most 32 requests')
    output = copy.deepcopy(list(existing))
    ids = {r['id'] for r in output}
    if len(output) + len(requests) > 32:
        raise ContractError('At most 32 bound calculations per chapter')
    for row in requests:
        if not isinstance(row, dict) or row.get('kind') not in KINDS:
            raise ContractError('Time calculation kind must be interval, duration or advance')
        first, second = KINDS[row['kind']]
        fields(row, ('id', 'kind', first, second), ('day_offset',))
        identifier = row['id']
        if not isinstance(identifier, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,31}', identifier) or identifier in ids:
            raise ContractError('Time calculation id must be valid and unique; do not overwrite a binding')
        start, dated_start = _clock(row[first])
        end, dated_end = _clock(row[second])
        if dated_start != dated_end:
            raise ContractError('Both time inputs must either have dates or both be clocks')
        offset = row.get('day_offset', 0)
        if type(offset) is not int or offset not in (0, 1) or (dated_start and 'day_offset' in row):
            raise ContractError('day_offset must be 0/1 for clock-only inputs; dated inputs already specify days')
        end += timedelta(days=offset)
        minutes = int((end - start).total_seconds() // 60)
        if minutes < 0:
            raise ContractError('Negative time interval; specify actual dates or explicit next day, do not guess rollover')
        output.append(dict(id=identifier, kind=row['kind'], inputs=copy.deepcopy(row),
            start=row[first], end=row[second], minutes=minutes, rendered=_amount(minutes), token=f'[[time:{identifier}]]'))
        ids.add(identifier)
    return output


def unbound_claims(draft):
    claims = []
    for match in ASSERTION.finditer(draft):
        start, end = match.span('amount')
        claims.append(dict(id=f'u{len(claims)+1}', start=start, end=end, quote=draft[start:end],
                           context=draft[max(0, match.start()-100):min(len(draft), end+100)]))
    return claims


def render(draft, calculations, *, check_semantics=True):
    catalog = {row['id']: row for row in calculations}
    def replace(match):
        if match[1] not in catalog:
            raise ContractError('Unknown time result token: ' + match[1])
        row = catalog[match[1]]
        if check_semantics and not match[2]:
            prefix = draft[max(0, match.start()-12):match.start()]
            if re.search(r'提前(?:了|约|整)?\s*$', prefix) and row['kind'] != 'advance':
                raise ContractError('An advance amount requires actual/scheduled, not response interval')
            if re.search(r'(?:持续了?|共开了|开着|开了)\s*$', prefix) and row['kind'] != 'duration':
                raise ContractError('A duration requires opened/closed, not response interval')
            literal_prefix = draft[max(0, match.start()-100):match.start()]
            # Resolve endpoint tokens locally before comparing an explicit
            # "HH:MM to HH:MM, interval ..." with the chosen formula.
            def endpoint(m):
                if m[1] in catalog and m[2]:return catalog[m[1]][m[2]]
                return m[0]
            pair = CLOCK_PAIR.search(TOKEN.sub(endpoint, literal_prefix))
            if pair and (row['start'][-5:] != pair['start'] or row['end'][-5:] != pair['end']):
                raise ContractError('Bound time inputs disagree with the literal start/end in this sentence')
        return row[match[2]] if match[2] else row['rendered']
    result = TOKEN.sub(replace, draft)
    if '[[time:' in result:
        raise ContractError('Malformed time result token')
    return result


def validate_literal_intervals(prose,calculations=()):
    for claim in unbound_claims(prose):
        pair=CLOCK_PAIR.search(prose[max(0,claim['start']-100):claim['start']])
        if not pair:continue
        start,_=_clock(pair['start']);end,_=_clock(pair['end'])
        if end<start:
            matching=[c for c in calculations if c['start'][-5:]==pair['start'] and c['end'][-5:]==pair['end']]
            if len(matching)!=1:raise ContractError('Clock rollover lacks one explicit bound calculation')
            minutes=matching[0]['minutes']
        else:minutes=int((end-start).total_seconds()//60)
        if re.sub(r'\s','',claim['quote']) not in (_amount(minutes),str(minutes)+'分钟'):
            raise ContractError('Literal clock interval disagrees with its stated amount')


def write_with_calculations(agent, context, trace):
    """One initial prose call; only numeric-span bindings may be repaired once."""
    value = agent.run(context, trace)
    raw = text(value['text'], 'draft')
    original = raw
    changes = []
    calculations = calculate(value.get('time_calculations', []), context.get('computed_times', []))
    entry = dict(role='writer_time_calculation', raw_draft=raw,
                 calculated_inputs=copy.deepcopy(calculations), status='CHECKING')
    trace.append(entry)
    # Verify token spelling even when there is no unbound expression.
    render(raw, calculations)
    claims = unbound_claims(raw)
    if claims:
        # The repair cannot change times, characters, plot or other wording.
        # It only binds already located amount spans to computed results.
        payload = dict(time_binding_repair=True, current_draft=raw, unbound_claims=claims,
                       computed_times=calculations, calculation_contract=CONTRACT)
        prompt = (
            '你是写作阶段的计算工具调用者，不是审核。只输出JSON：time_calculations数组、bindings数组。'
            '如需新计算，只提交输入，不填写结果；已有计算直接引用。bindings每项仅claim_id、calculation_id，'
            '覆盖所有unbound_claims各一次；程序只替换这些分钟数，其他文字不能修改。'
            '没有足够时间条件、不能确定属于同一计算时，不猜输入，输出unresolved说明原因。'
        )
        repair = dict(role='writer_time_binding', status='REQUESTED')
        trace.append(repair)
        try:
            reply = agent.gateway.complete(ModelRequest('writer', prompt, payload, 4096))
            repair['raw_output']=reply.content
            result = strict_json(reply.content)
            fields(result, ('time_calculations', 'bindings'))
            calculations = calculate(result['time_calculations'], calculations)
            if not isinstance(result['bindings'], list):
                raise ContractError('Time bindings must be a list')
            wanted = {r['id']: r for r in claims}
            known = {r['id'] for r in calculations}
            bindings = {}
            for binding in result['bindings']:
                fields(binding, ('claim_id', 'calculation_id'))
                cid, tid = binding['claim_id'], binding['calculation_id']
                if not isinstance(cid, str) or not isinstance(tid, str) or cid not in wanted or cid in bindings or tid not in known:
                    raise ContractError('Invalid, duplicate or unknown time claim binding')
                bindings[cid] = tid
            if set(bindings) != set(wanted):
                raise ContractError('Time binding coverage incomplete; do not leave unchecked arithmetic')
            for claim in reversed(claims):
                token=f'[[time:{bindings[claim["id"]]}]]'
                changes.append((claim['start'],claim['end'],token))
                raw = raw[:claim['start']] + token + raw[claim['end']:]
            repair.update(status='BOUND', bindings=result['bindings'])
        except Exception as exc:
            repair.update(status='UNRESOLVED', error=str(exc) if isinstance(exc,ContractError) else type(exc).__name__)
            entry['status'] = 'UNRESOLVED'
            raise
    draft = render(raw, calculations)
    validate_literal_intervals(draft,calculations)
    entry.update(status='CALCULATED', final_draft=draft, calculations=calculations,
                 bound_claim_count=len(claims), scope='Declared formulas and recognized computed-minute phrases only')
    updates=copy.deepcopy(value.get('continuity_updates',[]))
    # Carry source quotes through the exact same numeric-span edits and token
    # rendering as the prose. Do not invent or paraphrase evidence.
    for update in updates:
        for key in ('quote','restart_quote'):
            if key not in update:continue
            quote=update[key]
            if not isinstance(quote,str) or quote not in original:
                raise ContractError('Continuity quote must come from the original writer reply')
            start=original.index(quote);end=start+len(quote)
            for left,right,replacement in changes:
                if start<=left and right<=end:
                    quote=quote[:left-start]+replacement+quote[right-start:]
                elif left<end and right>start:
                    raise ContractError('Continuity quote splits a computed amount')
            update[key]=render(quote,calculations)
    metadata=dict(updates=updates,no_change_reason=value.get('no_continuity_change_reason'))
    return draft, calculations, metadata
