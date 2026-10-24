"""Portable opt-in real novel launcher. No credential discovery on import."""
import argparse
from datetime import datetime, timedelta, timezone
import getpass
import hashlib
import math
import os
from pathlib import Path
import platform
import re
import sys
from urllib.parse import urlsplit
from uuid import uuid4

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'memory_runtime/src'
sys.path.insert(0,str(SOURCE))
from inf_writer.chat_provider import ChatCompletionProvider
from inf_writer.domain import ContractError, canonical, digest, strict_json
from inf_writer.trial import save_new
from user_runtime import run_draft_trial

def now():return datetime.now(timezone(timedelta(hours=8))).isoformat()

def validate_config(value):
    required={'title','goal','constraints','chapters','max_chapters','target_han_chars',
              'endpoint','model','input_usd_per_million','output_usd_per_million','thinking_enabled'}
    legacy={'max_calls','max_cost_usd','pricing_confirmed','story_review_enabled','event_first'}
    if not isinstance(value,dict) or not required<=set(value) or set(value)-required-legacy:
        raise ContractError('配置字段缺失或多余；密钥不得放进JSON，请参照novel_config.json')
    for key in ('title','goal','model'):
        if not isinstance(value[key],str) or not value[key].strip():raise ContractError('配置字符串不能为空：'+key)
    if not isinstance(value['constraints'],list) or any(not isinstance(x,str) or not x.strip() for x in value['constraints']):
        raise ContractError('constraints必须是非空字符串组成的列表')
    for key,maximum in [('chapters',30),('max_chapters',30),('target_han_chars',1000000)]:
        if type(value[key]) is not int or not 1<=value[key]<=maximum:raise ContractError('配置整数超出范围：'+key)
    if value['max_chapters']<value['chapters']:raise ContractError('max_chapters不能小于chapters')
    for key in ('input_usd_per_million','output_usd_per_million'):
        x=value[key]
        if type(x) not in (float,int) or not math.isfinite(x) or x<=0:raise ContractError('费用/单价必须为有限正数：'+key)
    if value['thinking_enabled'] is not None and type(value['thinking_enabled']) is not bool:
        raise ContractError('thinking_enabled必须为true、false或null')
    if type(value.get('story_review_enabled',True)) is not bool:
        raise ContractError('story_review_enabled必须为true或false')
    if type(value.get('event_first',True)) is not bool:
        raise ContractError('event_first必须为true或false')
    if not isinstance(value['endpoint'],str):raise ContractError('endpoint必须是HTTPS地址')
    try:
        url=urlsplit(value['endpoint']);port=url.port
        if (url.scheme!='https' or not url.hostname or url.username or url.password or url.query or url.fragment
                or not url.path.endswith('/chat/completions') or port not in (None,443)):
            raise ValueError()
    except ValueError:raise ContractError('仅接受无账号、无查询参数的HTTPS chat/completions地址') from None
    return {k:value[k] for k in ('title','goal','constraints','chapters','max_chapters','target_han_chars','model')} | dict(
        execution_mode='draft_first',review_contract_version=0,review_transport_version=0,
        review_mode='tiered_memory',memory_update_policy='defer_failures_continue_writing',
        story_review_enabled=False if value.get('event_first',True) else value.get('story_review_enabled',True),event_first=value.get('event_first',True))

ENV_FIELDS={'INF_API_KEY','INF_MODEL','INF_BASE_URL','INF_INPUT_USD_PER_MILLION',
            'INF_OUTPUT_USD_PER_MILLION','INF_THINKING_ENABLED'}

def read_settings(path):
    """Read allowlisted connection settings; never execute or expand values."""
    path=Path(path)
    if path.is_symlink():raise ContractError('.env不能是符号链接')
    if not path.exists():return {}
    if not path.is_file() or path.stat().st_size>16384:raise ContractError('.env须为不超过16KB的普通文本文件')
    try:
        with path.open('rb') as stream:raw=stream.read(16385)
        if len(raw)>16384:raise ContractError('.env文件过大')
        lines=raw.decode('utf-8-sig').splitlines()
    except (OSError,UnicodeError):raise ContractError('.env无法读取，请保存为UTF-8文本') from None
    values={}
    for line in lines:
        stripped=line.strip()
        if not stripped or stripped.startswith('#'):continue
        match=re.fullmatch(r'(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)',stripped)
        if not match:
            if any(re.match(r'(?:export\s+)?'+name+r'\b',stripped) for name in ENV_FIELDS):
                raise ContractError('.env中的模型连接配置格式不正确')
            continue
        name,key=match.groups()
        if name not in ENV_FIELDS:continue
        if name in values:raise ContractError('.env中配置项只能出现一次：'+name)
        key=key.strip()
        if key[:1] in ('"',"'"):
            quote=key[0]
            if len(key)<2 or key[-1]!=quote:raise ContractError('.env配置引号未闭合')
            key=key[1:-1]
        else:key=re.split(r'\s+#',key,maxsplit=1)[0].rstrip()
        if '$' in key or '`' in key or any(ord(c)<33 or ord(c)>126 for c in key):
            raise ContractError('.env配置含无效字符；不支持变量替换或命令')
        values[name]=key
    return values

def read_dotenv(path):
    """Compatibility wrapper for key-only callers; never return other settings."""
    return read_settings(path).get('INF_API_KEY','')

def resolve_config(config,settings=None,*,environ=None):
    """Merge only non-secret settings before validation and execution consent."""
    if not isinstance(config,dict):raise ContractError('小说配置必须是JSON对象')
    result=dict(config)
    for key in ('max_calls','max_cost_usd','pricing_confirmed'):result.pop(key,None)
    values=read_settings(ROOT/'.env') if settings is None else settings
    process=os.environ if environ is None else environ
    mapping={'INF_MODEL':'model','INF_BASE_URL':'endpoint',
        'INF_INPUT_USD_PER_MILLION':'input_usd_per_million','INF_OUTPUT_USD_PER_MILLION':'output_usd_per_million',
        'INF_THINKING_ENABLED':'thinking_enabled'}
    for name,field in mapping.items():
        value=process.get(name) or values.get(name)
        if not value:continue
        if name=='INF_BASE_URL':
            value=value.rstrip('/')
            if not value.endswith('/chat/completions'):value+='/chat/completions'
        elif field in ('input_usd_per_million','output_usd_per_million'):
            try:value=float(value)
            except (ValueError,TypeError):raise ContractError('环境单价格式错误：'+name) from None
        elif field in ('pricing_confirmed','thinking_enabled'):
            choices={'true':True,'false':False}
            if field=='thinking_enabled':choices['null']=None
            if value.lower() not in choices:raise ContractError('环境布尔配置错误：'+name)
            value=choices[value.lower()]
        result[field]=value
    validate_config(result)
    return result

def read_secret():
    key=os.environ.get('INF_API_KEY') or read_dotenv(ROOT/'.env') or getpass.getpass('请输入API密钥（输入不显示，不保存）：')
    if not key or any(ord(c)<33 or ord(c)>126 for c in key):raise ContractError('API密钥为空或含无效字符')
    return key

def checked_output(path):
    output=Path(path).resolve()
    base=(ROOT/'runs').resolve()
    if output==base or not output.is_relative_to(base):raise ContractError('输出必须是项目runs目录内的新子目录')
    if output.exists():raise ContractError('输出目录已存在；请换一个新目录，避免覆盖或重复付费')
    return output

def launch(config,output,*,execute=True,confirmed=None,resume=None):
    config={k:v for k,v in config.items() if k not in ('max_calls','max_cost_usd','pricing_confirmed')}
    plan=validate_config(config);output=checked_output(output)
    from memory_runtime.writing import load_resume,runtime_hashes
    book=load_resume(resume,plan) if resume is not None else None
    if not execute:
        print(f'目标{plan["target_han_chars"]}汉字/{plan["chapters"]}章，无调用次数及费用预算上限。')
        print('仅检查配置：可读取.env连接设置，但不使用密钥认证、不调用API、不创建输出目录。')
        return None
    key=read_secret()
    provider=ChatCompletionProvider(config['endpoint'],config['model'],key,
        config['input_usd_per_million'],config['output_usd_per_million'],
        allow_remote=True,timeout_seconds=60,thinking_enabled=config['thinking_enabled'])
    output.mkdir(parents=True,exist_ok=False)
    save_new(output/'config.json',config)
    save_new(output/'launch_manifest.json',dict(started_at=now(),config_sha256=digest(canonical(config)),
        python=sys.version,platform=platform.platform(),source_relative=SOURCE.relative_to(ROOT).as_posix(),
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SOURCE.rglob('*.py'))},
        writing_runtime_sha256=runtime_hashes(),
        resumed_from=str(Path(resume).resolve()) if resume is not None else None,
        resume_checkpoint_sha256=hashlib.sha256(Path(resume).read_bytes()).hexdigest() if resume is not None else None,
        launcher_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        runtime_sha256=hashlib.sha256((ROOT/'user_runtime.py').read_bytes()).hexdigest(),
        authorization='User-operated direct launch; no confirmation prompt',budget_limits=None,network_retries=0,
        format_repairs_per_role=1,scope='Functional draft generation, not comparative quality experiment',
        limitations='Client-side cost estimate, not bill or provider hard cap; no deterministic remote reproduction guarantee'))
    try:
        result=run_draft_trial(output,provider,plan,resume_book=book)
    except BaseException as exc:
        save_new(output/'launcher_failure.json',dict(at=now(),error_type=type(exc).__name__,
            status='INTERRUPTED' if isinstance(exc,KeyboardInterrupt) else 'FAILED',
            warning='Partial files retained. Delivery/billing may be unknown. Never blindly restart this output.'))
        if isinstance(exc,KeyboardInterrupt):raise
        raise ContractError('写作异常退出；已保留部分记录。请检查launcher_failure.json，不要盲目重试。') from None
    print(f'正文：{output / "正文.md"}')
    print(f'问题清单：{output / "问题清单.json"}；字数/章节完成不等于质量通过。')
    return result

def main():
    parser=argparse.ArgumentParser(description='直接调用模型写小说：运行即产生API费用，无费用/调用上限')
    parser.add_argument('--config',type=Path,default=ROOT/'novel_config.json')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--resume',type=Path,help='从新入口的working/checkpoint_XXXX.json恢复到新的输出目录，先补齐未完成记忆')
    parser.add_argument('--execute',action='store_true',help=argparse.SUPPRESS)
    parser.add_argument('--yes',action='store_true',help=argparse.SUPPRESS)
    parser.add_argument('--dry-run',action='store_true',help='可选：只查看配置，不写作、不发API')
    args=parser.parse_args()
    try:
        config=resolve_config(strict_json(args.config.read_text(encoding='utf-8-sig')))
        validate_config(config)
        output=args.output or ROOT/'runs'/('novel_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid4().hex[:8])
        checked_output(output)
        if not args.dry_run:print('开始写作：将产生API费用，无调用次数或费用上限。',flush=True)
        result=launch(config,output,execute=not args.dry_run,resume=args.resume)
        return 0 if result is None or result.get('draft_completed') else 2
    except (ContractError,OSError,EOFError) as exc:
        # Do not echo arbitrary provider/OS messages, request bodies or credentials.
        if isinstance(exc,ContractError):print('未完成：'+str(exc),file=sys.stderr)
        else:print('未启动或未完成：配置文件/终端不可用，请检查路径及权限。',file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('已中断；保留部分文件，不自动续跑。',file=sys.stderr);return 130

if __name__=='__main__':raise SystemExit(main())
