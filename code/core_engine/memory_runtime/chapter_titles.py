"""Resolve display titles without modifying prose or frozen event proposals."""
import re

from inf_writer.domain import ContractError, strict_json
from inf_writer.models import ModelRequest


NUMBER = r'[0-9零〇一二三四五六七八九十百千两]+'
CHAPTER_PREFIX = re.compile(r'^第\s*' + NUMBER + r'\s*章\s*[·:：、.\-—]*\s*')
PLACEHOLDER = re.compile(r'^(?:续写|继续写作|继续创作|续章)\s*(?:第?\s*' + NUMBER + r'\s*章?)?$')


def clean_title(value):
    if not isinstance(value, str):
        return None
    title = value.strip()
    title = re.sub(r'^#{1,6}\s+', '', title)
    title = CHAPTER_PREFIX.sub('', title).strip()
    if not title or len(title) > 40 or '\n' in title or '\r' in title:
        return None
    if PLACEHOLDER.fullmatch(title) or re.fullmatch(r'第\s*' + NUMBER + r'\s*章', title):
        return None
    if any(token in title for token in ('[[', ']]', '{', '}', '<', '>')):
        return None
    return title


def prose_heading(prose):
    """Only an explicit heading can supply a title; never consume body text."""
    first = next((line.strip() for line in prose.splitlines() if line.strip()), '')
    if re.match(r'^#{1,6}\s+', first) or CHAPTER_PREFIX.match(first):
        return clean_title(first)
    return None


def excerpt_title(prose, number):
    # A literal short excerpt is the last resort when title generation fails.
    # It creates no story facts and incurs no additional retry/model calls.
    for line in prose.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or CHAPTER_PREFIX.match(line):
            continue
        line = re.sub(r'^[\s“”"‘’\'、—]+', '', line)
        phrase = re.split(r'[，。！？!?；;：:]', line, maxsplit=1)[0].strip()
        if not phrase:
            continue
        candidate = phrase if len(phrase) <= 18 else phrase[:18] + '…'
        title = clean_title(candidate)
        if title:
            return title
    # Handles unusual punctuation-only prose without exposing workflow labels.
    return f'篇章{number}'


def resolve_title(proposed, prose, number, planned=None, *, gateway=None, trace=None):
    trace = trace if trace is not None else []
    for source, value in (('proposal', proposed), ('existing_plan', planned)):
        title = clean_title(value)
        if title:
            return title
    title = prose_heading(prose)
    if title:
        trace.append(dict(role='chapter_title', status='RESOLVED', source='prose_heading'))
        return title
    if gateway is not None:
        try:
            # Only invalid/missing titles trigger this bounded, title-only call.
            reply = gateway.complete(ModelRequest('chapter_title',
                '根据提供的本章正文拟一个简短、具体的中文章节标题。只返回JSON对象{"title":"标题"}。'
                '不要章号，不要使用“续写”“续章”等工作流占位词，不添加正文未出现的情节。',
                dict(chapter_number=number, prose_excerpt=prose[:4000]), 128))
            trace.append(dict(role='chapter_title', status='REPLIED', raw_output=reply.content,
                input_tokens=reply.input_tokens, output_tokens=reply.output_tokens,
                cost_usd=reply.cost_usd, finish_reason=reply.finish_reason))
            value = strict_json(reply.content)
            if not isinstance(value, dict) or set(value) != {'title'} or reply.finish_reason != 'stop':
                raise ContractError('Invalid chapter title response')
            title = clean_title(value['title'])
            if title:
                return title
            raise ContractError('Placeholder or invalid chapter title')
        except Exception as exc:
            trace.append(dict(role='chapter_title', status='FALLBACK', error_type=type(exc).__name__))
    title = excerpt_title(prose, number)
    trace.append(dict(role='chapter_title', status='RESOLVED', source='prose_excerpt'))
    return title
