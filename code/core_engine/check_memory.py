"""Opt-in continuous memory check on existing prose; never generates prose."""
import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'memory_runtime/src'))
from memory_runtime.engine import MemoryEngine
from inf_writer.domain import ContractError,canonical
from inf_writer.trial import RecordedProvider,load_authorized_nst_secret
from inf_writer.chat_provider import ChatCompletionProvider


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save_new(path,value):
    """Atomic create, no overwrite: a checkpoint is complete or absent."""
    path=Path(path);body=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
    descriptor,temporary=tempfile.mkstemp(prefix='.memory-pending-',dir=path.parent)
    try:
        with os.fdopen(descriptor,'w',encoding='utf-8') as stream:
            stream.write(body);stream.flush();os.fsync(stream.fileno())
        if os.name=='nt':os.rename(temporary,path)  # Windows rename refuses existing targets.
        else:os.link(temporary,path)
    finally:
        Path(temporary).unlink(missing_ok=True)
def source_hashes():
    folder=ROOT/'memory_runtime'
    return {p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*.py')) if '__pycache__' not in p.parts}


def execute(output,gateway,chapters,through,questions=None,resume=None,input_hash=None):
    output=Path(output)
    memory=MemoryEngine.empty() if resume is None else resume['memory']
    done=0 if resume is None else resume['done_through']
    if resume is not None and (resume.get('input_sha256')!=input_hash or resume.get('runtime_sha256')!=source_hashes()):
        raise ContractError('Resume input/runtime differs; require an explicit migration rather than silent reuse')
    engine=MemoryEngine(gateway);rows=[];probes=[]
    save_new(output/'initial_memory.json',memory)
    for number in range(done+1,through+1):
        folder=output/f'chapter_{number:03d}';folder.mkdir()
        trace=[]
        save_new(folder/'memory_before.json',memory)
        print(canonical(dict(chapter=number,phase='memory',items=len(memory['items']))),flush=True)
        try:
            candidate,report=engine.advance(memory,chapters,number,trace)
        except Exception as exc:
            save_new(folder/'trace.json',trace)
            save_new(output/'pending.json',dict(pending_chapter=number,done_through=done,memory=memory,
                input_sha256=input_hash,runtime_sha256=source_hashes(),
                error_type=type(exc).__name__,error=str(exc) if isinstance(exc,ContractError) else 'Sanitized runtime failure'))
            raise
        save_new(folder/'memory_after.json',candidate)
        save_new(folder/'report.json',report)
        memory=candidate;done=number;rows.append(report)
        save_new(output/f'checkpoint_{number:03d}.json',dict(done_through=done,memory=memory,
            input_sha256=input_hash,runtime_sha256=source_hashes()))
        # Diagnostic answers do not roll back a valid memory transaction.
        if questions and str(number) in questions:
            try:probe=engine.recall(memory,questions[str(number)],trace,f'after-{number}')
            except ContractError as exc:probe=dict(status='INVALID_REPLY',error=str(exc))
            probe['after_chapter']=number;probes.append(probe);save_new(folder/'recall.json',probe)
        save_new(folder/'trace.json',trace)
    save_new(output/'final_memory.json',memory)
    return dict(completed_through=done,chapters=rows,probes=probes,
        initial_items=0 if resume is None else len(resume['memory']['items']),
        final_counts={t:sum(row['tier']==t for row in memory['items'].values()) for t in ('working','recent','long')},
        final_items=len(memory['items']),withheld_mutations=len(memory.get('withheld_memory_mutations',[])),
        novel_rewritten=False,semantic_certification=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--through',type=int,default=12)
    parser.add_argument('--questions',type=Path)
    parser.add_argument('--resume',type=Path)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preflight',action='store_true');mode.add_argument('--allow-remote',action='store_true')
    args=parser.parse_args();data=read(args.input)
    chapters=data['chapters'] if isinstance(data,dict) else data
    if not 1<=args.through<=len(chapters):raise ContractError('Invalid chapter range')
    if any(c['number']!=i or not isinstance(c.get('title'),str) or not isinstance(c.get('text'),str)
           for i,c in enumerate(chapters[:args.through],1)):raise ContractError('Invalid chapter prefix')
    questions=read(args.questions) if args.questions else {}
    if not isinstance(questions,dict) or any(not isinstance(v,str) for v in questions.values()):
        raise ContractError('Questions must map chapter numbers to text; no expected answers')
    hashes=source_hashes();original=sha(args.input)
    if args.preflight:
        print(canonical(dict(status='PREFLIGHT_PASS',input_sha256=original,runtime_sha256=hashes,
            through=args.through,no_remote_calls=True,novel_rewritten=False)))
        return
    args.output.mkdir(parents=True,exist_ok=False)
    save_new(args.output/'manifest.json',dict(input=str(args.input.resolve()),input_sha256=original,runtime_sha256=hashes,
        runner_sha256=sha(__file__),through=args.through,resume=str(args.resume) if args.resume else None,
        questions=questions,network_retries=0,format_repairs_per_phase=1,
        temporal_coverage='selected_old_records_only',scope='MEMORY_ONLY_NO_PROSE_GENERATION'))
    result={};recorder=None;started=time.monotonic()
    try:
        key,endpoint,model=load_authorized_nst_secret(ROOT/'NstAgent/.env')
        provider=ChatCompletionProvider(endpoint,model,key,0.3,1.2,allow_remote=True,timeout_seconds=60,thinking_enabled=False)
        recorder=RecordedProvider(provider,args.output)
        result=execute(args.output,recorder,chapters,args.through,questions,
            read(args.resume) if args.resume else None,original)
        result['status']='COMPLETE'
    except Exception as exc:
        result=dict(status='FAILED_OR_PENDING',error_type=type(exc).__name__)
        if (args.output/'pending.json').exists():result['done_through']=read(args.output/'pending.json')['done_through']
    replies=[read(p) for p in args.output.glob('call_*.response.json')]
    result.update(calls=recorder.calls if recorder else 0,
        input_tokens=sum(r['input_tokens'] for r in replies),output_tokens=sum(r['output_tokens'] for r in replies),
        cost_usd_historical_estimate_not_bill=sum(r['cost_usd'] for r in replies),
        elapsed_seconds=time.monotonic()-started,novel_unchanged=sha(args.input)==original,
        runtime_unchanged=source_hashes()==hashes)
    save_new(args.output/'result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('chapters','probes')},ensure_ascii=False,indent=2))
    if result['status']!='COMPLETE':raise SystemExit(1)


if __name__=='__main__':main()
