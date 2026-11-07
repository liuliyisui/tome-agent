"""Nonblocking titles for saved fallback chapters; never rewrite prose."""
import re
from inf_writer.domain import canonical,fields,strict_json
from inf_writer.models import ModelRequest


def placeholder(value):return isinstance(value,str)and bool(re.fullmatch(r'续写\s*\d+',value.strip()))


def valid(value):
    return isinstance(value,str)and 1<=len(value.strip())<=40 and '\n'not in value and not placeholder(value)and not re.fullmatch(r'第[0-9一二三四五六七八九十百]+章',value.strip())


def assign(book,chapter,gateway,trace):
    """Called only after the prose checkpoint exists; failures stay pending."""
    if not placeholder(chapter['title'])and chapter.get('title_status')!='pending':return False
    number=chapter['number'];key=str(number);jobs=book.setdefault('chapter_title_jobs',{})
    chapter['title']='';chapter['title_status']='pending'
    job=jobs.setdefault(key,dict(chapter_sha256=chapter['sha256'],attempts=0));job['attempts']+=1
    entry=dict(role='chapter_title',chapter=number);trace.append(entry)
    try:
        title=None
        # Failed references do not invalidate an otherwise usable chapter name.
        for item in reversed(trace[:-1]):
            if item.get('role')!='planner' or not isinstance(item.get('raw_output'),str):continue
            try:proposal=strict_json(item['raw_output'])
            except Exception:continue
            if not isinstance(proposal,dict):continue
            if proposal.get('number')==number and valid(proposal.get('title')):
                title=proposal['title'].strip();entry['source']='same_chapter_planning_reply';break
        if title is None:
            reply=gateway.complete(ModelRequest('chapter_title','仅根据已保存的本章正文拟一个简短、自然的中文章名。'
                '输出JSON且只含title字符串，不用章号、续写字样，不改写正文。',dict(chapter_number=number,
                    opening=chapter['text'][:1500],ending=chapter['text'][-1500:]),256))
            entry.update(raw_output=reply.content,source='saved_chapter_text')
            if reply.finish_reason not in ('stop',None):raise ValueError('Incomplete chapter title')
            value=strict_json(reply.content);fields(value,('title',));title=value['title']
        if not valid(title):raise ValueError('Invalid chapter title')
        chapter['title']=title.strip();chapter['title_status']='assigned'
        chapter['title_source']=dict(chapter_sha256=chapter['sha256'],scope='Metadata only, no prose change')
        if key in book.get('plan',{}):book['plan'][key]['title']=chapter['title']
        jobs.pop(key,None);entry['status']='ASSIGNED';return True
    except Exception as exc:
        entry.update(status='DEFERRED',error_type=type(exc).__name__);return False
