"""Generation inputs and exact quantity slots; no prose inspection or verdicts."""
import re
from inf_writer.domain import ContractError,canonical,digest

AMOUNT=re.compile(r'(?:大约|大概|将近|接近|超过|不足|至少|至多|约|近|仅)?[零〇一二两三四五六七八九十百千万亿\d]+(?:\.[\d]+)?(?:到|至|—|-)?[零〇一二两三四五六七八九十百千万亿\d]*(?:多|余|来)?(?:分钟|小时|秒钟|秒|天|日|个月|月|年|米|公里|厘米|毫米|页|份|人|次|元|万元)(?:左右|上下|以上|以下|以内|以外)?')
SLOT=re.compile(r'\[\[quantity:(q_[a-f0-9]{20})\]\]')
POLICY=('数值以quantity_sources为来源目录。复述同一数值时优先使用目录token，程序按原表述展开。'
    '目录保留来源、单位、近似和范围；“约四十分钟”只能仍作“约四十分钟”，不能自行细化成“三十八分钟”。'
    '不同来源的量不能合并成一次测量，不把传闻或计划的量写成已证实结果。'
    '目录没有所需精确数值时保持来源的模糊表述，或不写该数值；新计算应回到规划阶段提供精确输入。'
    '自由描写不补造关键日期、时长、金额、页数和人数。此目录用于生成，不是对已有资料真实性的认证。')


def sources(commit):
    """Every slot quotes one declared event, never inferred or rounded."""
    rows=[]
    for scene in commit['scenes']:
        for beat in scene['beats']:
            for match in AMOUNT.finditer(beat['statement']):
                expression=match[0]
                modifiers=re.findall(r'大约|大概|将近|接近|超过|不足|至少|至多|约|近|多|余|来|左右|上下|以上|以下|以内|以外',expression)
                identifier='q_'+digest(canonical([commit['sha256'],beat['id'],match.start(),expression]))[:20]
                rows.append(dict(id=identifier,token='[[quantity:'+identifier+']]',expression=expression,
                    source_event=beat['event_id'],source_span=[match.start(),match.end()],mode=beat['mode'],
                    precision='qualified' if modifiers else 'range' if re.search(r'到|至|—|-',expression) else 'source_stated',
                    modifiers=modifiers,instruction='原样沿用修饰词、范围和单位，不增加精度'))
    return rows


def render(prose,rows):
    catalogue={r['id']:r['expression'] for r in rows}
    def replace(match):
        if match[1] not in catalogue:raise ContractError('Unknown quantity source slot')
        return catalogue[match[1]]
    result=SLOT.sub(replace,prose)
    if '[[quantity:' in result:raise ContractError('Malformed quantity source slot')
    return result
