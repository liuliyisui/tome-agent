"""Lossless chapter excerpts in the existing three tiers, independent of plans."""
import copy
from inf_writer.domain import ContractError,digest,evidence_segments
from inf_writer.tiered_memory import apply_delta


def excerpts(chapter):
    return [row for row in evidence_segments(chapter['text']) if row['text'].strip()]


def verify_prose_coverage(memory,chapter):
    coverage=memory.get('prose_memory_coverage',{}).get(str(chapter['number']))
    rows=excerpts(chapter)
    if not coverage or coverage.get('chapter_sha256')!=digest(chapter['text']):return False
    bindings=coverage.get('excerpts',[])
    if [b.get('evidence_id') for b in bindings]!=[r['id'] for r in rows]:return False
    for binding,source in zip(bindings,rows):
        item=memory['items'].get(binding.get('memory_id'),{})
        if item.get('kind')!='prose_excerpt' or item.get('claim')!=source['text']:return False
        if not any(ref.get('chapter_number')==chapter['number'] and ref.get('evidence_id')==source['id']
            and ref.get('chapter_sha256')==coverage['chapter_sha256'] and ref.get('quote')==source['text'] for ref in item.get('sources',[])):return False
    return bool(rows)


def store_prose_excerpts(memory,chapters,number):
    chapter=chapters[number-1]
    if digest(chapter['text'])!=chapter['sha256']:raise ContractError('Saved prose hash mismatch')
    if verify_prose_coverage(memory,chapter):return copy.deepcopy(memory)
    if str(number) in memory.get('prose_memory_coverage',{}):raise ContractError('Stored prose excerpt coverage is damaged')
    rows=excerpts(chapter);operations=[]
    for row in rows:
        operations.append(dict(op='add',subject=f'prose:c{number:04d}.{row["id"]}',attribute='excerpt',
            claim=row['text'],kind='prose_excerpt',status='active',
            source_refs=[dict(chapter_number=number,evidence_id=row['id'])]))
    if not operations:raise ContractError('Saved prose has no storable text')
    result=apply_delta(memory,dict(changes=operations),chapters,f'prose-excerpts:{number}:{chapter["sha256"]}')
    by_subject={r['subject']:r for r in result['items'].values() if r['kind']=='prose_excerpt'}
    bindings=[]
    for source in rows:
        item=by_subject[f'prose:c{number:04d}.{source["id"]}']
        item['provenance_scope']='source_chapter_text_only'
        bindings.append(dict(evidence_id=source['id'],memory_id=item['id']))
    result.setdefault('prose_memory_coverage',{})[str(number)]=dict(
        chapter_sha256=chapter['sha256'],excerpts=bindings,excerpt_count=len(bindings),status='STORED')
    if not verify_prose_coverage(result,chapter):raise ContractError('Prose excerpt transaction lost source coverage')
    return result
