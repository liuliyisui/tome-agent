import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from inf_writer.domain import Snapshot, ContractError, ConflictError, apply_chapter
from inf_writer.models import Budget, ModelReply, ModelGateway
from inf_writer.agents import build_agents
from inf_writer.runtime import Coordinator, ContextBuilder
from inf_writer.storage import FileStore

TEXT = "艾岚的眼睛是灰色。"
GOLD = "艾岚喝下药剂，眼睛变为金色。"
def change(value="灰色", action="store", revision=None, quote=TEXT):
    return dict(action=action, subject="艾岚", attribute="eye_color", value=value,
                expected_revision=revision, quote=quote, reason="正文明确给出当前眼色")
def plan(number=1, future=None):
    return dict(number=number, title="守灯人", brief="写出当前事件", future_updates=future or [])
class FixtureModel:
    """Role-specific fixture responses, NOT an actual language model."""
    def __init__(self, text=TEXT, changes=None, approved=True):
        self.text=text; self.changes=[change()] if changes is None else changes
        self.approved=approved; self.requests=[]; self.bad_first=False
    def complete(self, request):
        self.requests.append(copy.deepcopy(request))
        if self.bad_first and len(self.requests)==1: return ModelReply("{", 0, 0, 0)
        number=request.payload["chapter_number"]
        values={"planner":plan(number), "writer":{"text":self.text},
                "memory":{"changes":self.changes}, "reviewer":{"approved":self.approved,"issues":[] if self.approved else ["人物行为缺依据"]}}
        return ModelReply(json.dumps(values[request.role],ensure_ascii=False),0,0,0)

class DomainTests(unittest.TestCase):
    def test_current_update_archives_old_value(self):
        first=apply_chapter(Snapshot("demo","写故事"),plan(),TEXT,[change()],"r1","h1")
        second=apply_chapter(first,plan(2),GOLD,[change("金色","update",1,GOLD)],"r2","h2")
        self.assertEqual(second.active_facts()[0]["value"],"金色")
        self.assertEqual(second.history[0]["fact"]["value"],"灰色")
        self.assertEqual(second.history[0]["replaced_by"]["quote"],GOLD)
        self.assertEqual(first.active_facts()[0]["value"],"灰色")
    def test_bad_quote_does_not_mutate_snapshot(self):
        state=Snapshot("demo","写故事"); before=state.to_dict()
        with self.assertRaises(ContractError): apply_chapter(state,plan(),TEXT,[change(quote="不存在")],"r1","h")
        self.assertEqual(state.to_dict(),before)
    def test_stale_revision_rejected(self):
        state=apply_chapter(Snapshot("demo","写故事"),plan(),TEXT,[change()],"r1","h")
        state=apply_chapter(state,plan(2),GOLD,[change("金色","update",1,GOLD)],"r2","h")
        with self.assertRaises(ConflictError): apply_chapter(state,plan(3),TEXT,[change("灰色","update",1,TEXT)],"r3","h")
    def test_partial_memory_batch_rolls_back(self):
        state=Snapshot("demo","写故事")
        with self.assertRaises(ContractError): apply_chapter(state,plan(),TEXT,[change(),dict(change(),subject="别人",quote="无此句")],"r1","h")
        self.assertEqual(state.facts,{})
    def test_future_patch_cannot_rewrite_current_or_past(self):
        with self.assertRaises(ContractError): apply_chapter(Snapshot("demo","写故事"),plan(future=[dict(number=1,title="改写",brief="不许")]),TEXT,[],"r1","h")
    def test_duplicate_attribute_in_one_batch_rejected(self):
        with self.assertRaises(ContractError): apply_chapter(Snapshot("demo","写故事"),plan(),TEXT,[change(),change()],"r1","h")
    def test_fact_values_must_be_finite_json(self):
        with self.assertRaises(ContractError): apply_chapter(Snapshot("demo","写故事"),plan(),TEXT,[change(float("nan"))],"r1","h")
    def test_snapshot_roundtrip(self):
        state=apply_chapter(Snapshot("demo","写故事"),plan(),TEXT,[change()],"r1","h")
        self.assertEqual(Snapshot.from_dict(json.loads(json.dumps(state.to_dict()))).to_dict(),state.to_dict())
    def test_retire_excludes_current_and_preserves_history(self):
        state=apply_chapter(Snapshot("demo","写故事"),plan(),TEXT,[change()],"r1","h")
        state=apply_chapter(state,plan(2),TEXT,[change(None,"retire",1,TEXT)],"r2","h")
        self.assertEqual(state.active_facts(),[]); self.assertEqual(len(state.history),1)
    def test_future_plan_can_be_revised_without_rewriting_past(self):
        state=apply_chapter(Snapshot("demo","写故事"),plan(future=[dict(number=2,title="后章",brief="未写计划")]),TEXT,[],"r1","h")
        state=apply_chapter(state,plan(2,future=[dict(number=3,title="再后章",brief="局部计划")]),GOLD,[],"r2","h")
        self.assertEqual(state.plan["1"]["title"],"守灯人"); self.assertEqual(state.plan["3"]["title"],"再后章")

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        sandbox=Path(__file__).resolve().parents[1]/"runs"/"test-tmp"
        sandbox.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=sandbox); self.addCleanup(self.temp.cleanup)
        self.store=FileStore(Path(self.temp.name)); self.store.initialize(Snapshot("demo","写故事"))
    def coordinator(self,model=None,max_calls=10):
        model=model or FixtureModel(); gateway=ModelGateway(model,Budget(max_calls=max_calls,max_cost_usd=0),reserve_per_call=0)
        return Coordinator(self.store,build_agents(gateway)),model
    def test_four_roles_complete_one_atomic_chapter(self):
        runner,model=self.coordinator(); result=runner.write_next("demo","request1")
        self.assertEqual(result.status,"COMMITTED")
        self.assertEqual([r.role for r in model.requests],["planner","writer","memory","reviewer"])
        state=self.store.load("demo"); self.assertEqual(len(state.chapters),1); self.assertEqual(len(state.active_facts()),1)
        self.assertEqual(state.revision,1)
    def test_reviewer_rejection_keeps_previous_state(self):
        runner,_=self.coordinator(FixtureModel(approved=False)); result=runner.write_next("demo","r1")
        self.assertEqual(result.status,"REJECTED"); self.assertEqual(self.store.load("demo").revision,0)
        self.assertTrue(list((Path(self.temp.name)/"demo"/"audit").glob("*.json")))
    def test_bad_memory_cannot_commit_chapter(self):
        runner,_=self.coordinator(FixtureModel(changes=[change(quote="不存在")]))
        self.assertEqual(runner.write_next("demo","r1").status,"FAILED")
        self.assertEqual(self.store.load("demo").chapters,[])
    def test_idempotent_request_does_not_call_model_twice(self):
        runner,model=self.coordinator(); one=runner.write_next("demo","r1"); two=runner.write_next("demo","r1")
        self.assertEqual(two.status,"ALREADY_COMMITTED"); self.assertEqual(one.chapter_number,two.chapter_number); self.assertEqual(len(model.requests),4)
    def test_idempotency_key_cannot_change_instruction(self):
        runner,_=self.coordinator(); runner.write_next("demo","r1",instruction="一")
        self.assertEqual(runner.write_next("demo","r1",instruction="二").status,"FAILED")
    def test_single_format_retry_and_budget_accounting(self):
        model=FixtureModel(); model.bad_first=True; runner,_=self.coordinator(model)
        self.assertEqual(runner.write_next("demo","r1").status,"COMMITTED")
        self.assertEqual(len(model.requests),5); self.assertIn("repair",model.requests[1].payload)
    def test_budget_failure_does_not_commit(self):
        runner,model=self.coordinator(max_calls=2)
        self.assertEqual(runner.write_next("demo","r1").status,"FAILED"); self.assertEqual(len(model.requests),2)
        self.assertEqual(self.store.load("demo").revision,0)
    def test_context_does_not_include_archive(self):
        state=apply_chapter(Snapshot("demo","写故事"),plan(),TEXT,[change()],"r1","h")
        state=apply_chapter(state,plan(2),GOLD,[change("金色","update",1,GOLD)],"r2","h")
        context=ContextBuilder().build(state)
        self.assertNotIn("history",context); self.assertEqual(context["active_facts"][0]["value"],"金色")
    def test_context_overflow_is_explicit_not_silent_fact_loss(self):
        with self.assertRaises(ContractError): ContextBuilder(max_chars=5).build(Snapshot("demo","写故事"))
    def test_store_compare_and_swap(self):
        state=apply_chapter(self.store.load("demo"),plan(),TEXT,[change()],"r1","h")
        self.store.commit(state,expected_revision=0)
        with self.assertRaises(ConflictError): self.store.commit(state,expected_revision=0)
    def test_storage_replace_failure_preserves_checkpoint(self):
        state=apply_chapter(self.store.load("demo"),plan(),TEXT,[change()],"r1","h")
        with patch("inf_writer.storage.os.replace",side_effect=OSError("simulated write failure")):
            with self.assertRaises(OSError): self.store.commit(state,expected_revision=0)
        self.assertEqual(self.store.load("demo").revision,0)
    def test_storage_path_escape_rejected(self):
        with self.assertRaises(ContractError): self.store.load("../escape")
    def test_snapshot_unknown_schema_rejected(self):
        data=Snapshot("demo","写故事").to_dict(); data["schema_version"]=999
        with self.assertRaises(ContractError): Snapshot.from_dict(data)
    def test_model_budget_reserves_unknown_failures(self):
        class Broken:
            def complete(self,request): raise OSError("fixture")
        budget=Budget(max_calls=2,max_cost_usd=.1)
        gateway=ModelGateway(Broken(),budget,reserve_per_call=.1)
        from inf_writer.models import ModelRequest
        with self.assertRaises(OSError): gateway.complete(ModelRequest("writer","test",{},100))
        self.assertEqual(budget.calls,1); self.assertAlmostEqual(budget.cost_upper_usd,.1)
    def test_failure_in_one_story_does_not_stop_another(self):
        self.store.initialize(Snapshot("other","另一本故事"))
        runner,_=self.coordinator(FixtureModel(approved=False)); self.assertEqual(runner.write_next("demo","r1").status,"REJECTED")
        runner,_=self.coordinator(); self.assertEqual(runner.write_next("other","r1").status,"COMMITTED")
    def test_duplicate_json_key_is_not_silently_accepted(self):
        from inf_writer.domain import strict_json
        with self.assertRaises(ContractError): strict_json('{"approved":true,"approved":false}')
    def test_lock_conflict_is_explicit(self):
        state=apply_chapter(self.store.load("demo"),plan(),TEXT,[change()],"r1","h")
        lock=Path(self.temp.name)/"demo"/"checkpoint.lock"
        lock.write_text("another writer",encoding="utf-8")
        with self.assertRaises(ConflictError): self.store.commit(state,expected_revision=0)
        self.assertTrue(lock.exists()); self.assertEqual(self.store.load("demo").revision,0)
    def test_no_nst_code_dependency(self):
        import ast
        source=Path(__file__).resolve().parents[1]/"src"/"inf_writer"
        for path in source.rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                names=[n.name for n in node.names] if isinstance(node,ast.Import) else [node.module or ""] if isinstance(node,ast.ImportFrom) else []
                self.assertFalse(any("nstagent" in name.lower() for name in names),path.name)
    def test_audit_failure_does_not_disguise_committed_state(self):
        runner,_=self.coordinator()
        with patch.object(self.store,"save_audit",side_effect=OSError("fixture audit failure")):
            result=runner.write_next("demo","r1")
        self.assertEqual(result.status,"COMMITTED"); self.assertIsNotNone(result.audit_warning)
        self.assertEqual(self.store.load("demo").revision,1)
    def test_archived_history_is_source_checked(self):
        from inf_writer.memory import VersionedMemory
        state=apply_chapter(self.store.load("demo"),plan(),TEXT,[change()],"r1","h")
        state=apply_chapter(state,plan(2),GOLD,[change("金色","update",1,GOLD)],"r2","h")
        self.assertEqual(VersionedMemory().history(state,"艾岚","eye_color")[0]["fact"]["value"],"灰色")
        state.history[0]["fact"]["source"]["quote"]="不存在"
        with self.assertRaises(ContractError): VersionedMemory().history(state,"艾岚","eye_color")
    def test_quote_presence_alone_does_not_prove_semantic_truth(self):
        # Deliberately demonstrate this check's boundary instead of claiming a truth oracle.
        state=apply_chapter(self.store.load("demo"),plan(),TEXT,[change(value="金色")],"r1","h")
        self.assertEqual(state.active_facts()[0]["value"],"金色")

if __name__=="__main__": unittest.main()
