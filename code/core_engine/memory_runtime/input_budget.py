"""Bound request views without editing stored prose or canonical facts."""
import copy
from inf_writer.domain import canonical,digest


def size(value):return len(canonical(value).encode('utf-8'))


def fit(context,limit):
    if size(context)<=limit:return context
    result=copy.deepcopy(context);changes=[];before=size(result)
    for chapter in result.get('recent_chapters',[]):
        raw=chapter['text'].encode('utf-8')
        if len(raw)>12000:
            chapter['source_sha256']=chapter.get('sha256',digest(chapter['text']));chapter['excerpt']=True
            chapter['text']=raw[-12000:].decode('utf-8',errors='ignore')
            chapter['sha256']=digest(chapter['text'])
            changes.append(dict(field='recent_chapters',chapter=chapter['number'],view='last_12000_utf8_bytes'))
    result['input_selection']=dict(original_bytes=before,limit_bytes=limit,stored_sources_unchanged=True,changes=changes)
    # Remove whole optional retrieval rows, never typed state or choice entries.
    lists=[('historical_memory.items',result.get('historical_memory',{}).get('items',[])),
        ('source_evidence',result.get('source_evidence',[])),
        ('retrieved_memory',result.get('retrieved_memory',[])),
        ('recent_chapters',result.get('recent_chapters',[]))]
    for label,rows in lists:
        if not isinstance(rows,list):continue
        removed=0
        while rows and size(result)>limit:
            rows.pop(0 if label=='recent_chapters' else -1);removed+=1
        if removed:
            changes.append(dict(field=label,omitted_rows=removed,scope='request_view_only'))
            if label=='retrieved_memory' and 'memory_coverage' in result:
                coverage=result['memory_coverage'];kept=[r['memory_id'] for r in rows if 'memory_id' in r]
                coverage['omitted_ids']=list(dict.fromkeys(coverage.get('omitted_ids',[])+[i for i in coverage.get('selected_ids',[]) if i not in kept]))
                coverage['selected_ids']=kept
        if size(result)<=limit:return result
    return result
