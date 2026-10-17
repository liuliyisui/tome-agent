import argparse
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from .agents import build_agents
from .demo import DemoModel
from .domain import Snapshot
from .models import Budget, ModelGateway
from .runtime import Coordinator
from .storage import FileStore

PROJECT_ROOT = Path(__file__).resolve().parents[3]

def main():
    parser=argparse.ArgumentParser(description="INF independent offline multi-agent foundation")
    sub=parser.add_subparsers(dest="command",required=True)
    demo=sub.add_parser("demo",help="Run two deterministic fixture chapters; no API")
    demo.add_argument("--output",type=Path,default=None)
    args=parser.parse_args()
    output=args.output or PROJECT_ROOT/"code"/"backend"/"data"/"runs"/("offline_"+datetime.now().strftime("%Y%m%d_%H%M%S")+"_"+uuid4().hex[:8])
    store=FileStore(output); store.initialize(Snapshot("demo","守灯人的身份核验故事",["真实身体变化必须有事件依据"]))
    budget=Budget(max_calls=8,max_cost_usd=0)
    coordinator=Coordinator(store,build_agents(ModelGateway(DemoModel(),budget)))
    results=[coordinator.write_next("demo",f"chapter{n}") for n in (1,2)]
    state=store.load("demo")
    print(json.dumps({"mode":"OFFLINE_FIXTURES_NOT_LLM_GENERATION","output":str(output.resolve()),"outcomes":[asdict(r) for r in results],
        "roles":["planner","writer","memory","reviewer"],"model_calls":budget.calls,"api_calls":0,
        "chapter_count":len(state.chapters),"active_facts":state.active_facts(),"archive_versions":len(state.history)},ensure_ascii=False,indent=2))
    if any(r.status!="COMMITTED" for r in results): raise SystemExit(1)
