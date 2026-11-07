"""All Python-side fixes for the VS Code code-quality remediation.

Bundle 1 of 4. Siblings: ``fixes.yaml`` (CI workflow + pre-commit config),
``fixes.toml`` (Ruff config), ``fixes.md`` (README index + review documents).

Every change is a plain unified diff against baseline ``e4d23ce``.
``apply_patch`` applies it in place, hunk by hunk, and is idempotent: a second
run reports the hunks as already applied instead of duplicating them. Per-file
line endings are preserved, so LF and CRLF checkouts both work.

Usage::

    python fixes/fixes.py --check             # report only, change nothing
    python fixes/fixes.py                     # apply the Python fixes (44 files)
    python fixes/fixes.py --only yaml         # CI workflow + pre-commit config
    python fixes/fixes.py --only toml         # Ruff configuration
    python fixes/fixes.py --only md           # README index + review documents
    python fixes/fixes.py --all               # all four bundles
    python fixes/fixes.py --root /other/repo  # apply to another checkout

The human-readable list of the 79 fixes (what/where/before/after) is in
``docs/software/CODE_QUALITY_FIXES.md``.
"""

# The embedded unified diff keeps its verbatim " " context markers, so lines
# that stand for an empty source line carry a single space (W293 would fire).
# ruff: noqa: W293

import argparse
import pathlib
import re
import sys
import tomllib

PY_PATCH = r'''
diff --git a/code/backend/inf_backend/migrate.py b/code/backend/inf_backend/migrate.py
index 5fe6da0..9360c32 100644
--- a/code/backend/inf_backend/migrate.py
+++ b/code/backend/inf_backend/migrate.py
@@ -229,7 +229,7 @@ def main():
     except (db.DatabaseUnavailable, ValueError, OSError, KeyError):
         raise SystemExit(
             "数据库操作未完成。请检查数据库、源存档格式、冲突作品及命令参数。"
-        )
+        ) from None
 
 
 if __name__ == "__main__":
diff --git a/code/backend/inf_backend/service.py b/code/backend/inf_backend/service.py
index f843927..7d412d7 100644
--- a/code/backend/inf_backend/service.py
+++ b/code/backend/inf_backend/service.py
@@ -467,20 +467,24 @@ def load_longform(book_id):
     except ContractError as exc:
         if str(exc) != "写作运行时版本不一致，不能直接恢复旧检查点":
             raise
-        pointer = strict_json(_longform_pointer(book_id).read_text(encoding="utf-8-sig"))
+        pointer = strict_json(
+            _longform_pointer(book_id).read_text(encoding="utf-8-sig")
+        )
         if not isinstance(pointer, dict) or set(pointer) != {"checkpoint"}:
-            raise ValueError("长文本检查点索引格式不正确")
+            raise ValueError("长文本检查点索引格式不正确") from exc
         root = book_path(book_id).resolve()
         checkpoint = (root / pointer["checkpoint"]).resolve()
         if checkpoint == root or not checkpoint.is_relative_to(root):
-            raise ValueError("长文本检查点路径不安全")
+            raise ValueError("长文本检查点路径不安全") from exc
         record = strict_json(checkpoint.read_text(encoding="utf-8-sig"))
         state = record.get("book")
-        if (record.get("schema") != "inf-writing-checkpoint-v1"
-                or record.get("writing_plan_sha256") != digest(canonical(plan))
-                or not isinstance(state, dict)
-                or record.get("book_sha256") != digest(canonical(state))
-                or not isinstance(state.get("chapters"), list)):
+        if (
+            record.get("schema") != "inf-writing-checkpoint-v1"
+            or record.get("writing_plan_sha256") != digest(canonical(plan))
+            or not isinstance(state, dict)
+            or record.get("book_sha256") != digest(canonical(state))
+            or not isinstance(state.get("chapters"), list)
+        ):
             raise ValueError("旧版存档完整性校验失败") from exc
         return {"metadata": meta, "state": state, "read_only": True}
     return {"metadata": meta, "state": state}
diff --git a/code/core_engine/inf_writer/agents.py b/code/core_engine/inf_writer/agents.py
index b5fc154..62d53e3 100644
--- a/code/core_engine/inf_writer/agents.py
+++ b/code/core_engine/inf_writer/agents.py
@@ -4,6 +4,7 @@ import copy
 from dataclasses import dataclass
 
 from .domain import ContractError, chapter_plan, fields, strict_json, text
+from .memory_output_contract import MEMORY_PROMPT
 from .models import ModelGateway, ModelRequest
 
 PROMPTS = {
@@ -98,8 +99,6 @@ PROMPTS["memory"] += (
     "不能为避免冲突删光候选或简单转换动作后覆盖旧值。"
 )
 
-from .memory_output_contract import MEMORY_PROMPT
-
 PROMPTS["memory"] = MEMORY_PROMPT
 
 
diff --git a/code/core_engine/inf_writer/narrative_context.py b/code/core_engine/inf_writer/narrative_context.py
index 29e72e9..376eb7a 100644
--- a/code/core_engine/inf_writer/narrative_context.py
+++ b/code/core_engine/inf_writer/narrative_context.py
@@ -32,12 +32,12 @@ def parse_planner_json(raw):
         try:
             _, end = json.JSONDecoder().raw_decode(stripped)
         except (ValueError, TypeError):
-            raise original
+            raise original from None
         if stripped[end:].strip() != "}":
-            raise original
+            raise original from None
         parsed = strict_json(stripped[:end])
         if not isinstance(parsed, dict):
-            raise original
+            raise original from None
         return parsed, [
             {
                 "rule": "planner_surplus_closing_brace",
diff --git a/code/core_engine/memory_runtime/__init__.py b/code/core_engine/memory_runtime/__init__.py
index 74502be..630a82e 100644
--- a/code/core_engine/memory_runtime/__init__.py
+++ b/code/core_engine/memory_runtime/__init__.py
@@ -1 +1,14 @@
 """Opt-in three-tier memory runtime; importing does not read credentials."""
+
+import sys
+from pathlib import Path
+
+# ``inf_writer`` is a top-level package that lives both in
+# ``code/core_engine/inf_writer`` and in ``memory_runtime/src/inf_writer``, and it
+# is never installed as a distribution. Submodules of this package (and the
+# ``python memory_runtime/test_*.py`` suites) import it by name, so the bundled
+# copy must be importable as soon as this package is imported. Bootstrapping it
+# here keeps every import block in the submodules at the top of its file (E402).
+_SOURCE = Path(__file__).resolve().parent / "src"
+if str(_SOURCE) not in sys.path:
+    sys.path.insert(0, str(_SOURCE))
diff --git a/code/core_engine/memory_runtime/continuity.py b/code/core_engine/memory_runtime/continuity.py
index 8d5fd30..454f812 100644
--- a/code/core_engine/memory_runtime/continuity.py
+++ b/code/core_engine/memory_runtime/continuity.py
@@ -160,8 +160,11 @@ def apply(state, updates, prose, chapter, no_change_reason=None):
             previous = result[groups[kind]].get(identifier)
             record["revision"] = (previous or {}).get("revision", 0) + 1
 
+        # Late binding of `row` is intentional: the binding is refreshed later in
+        # this same iteration (attribute normalisation) and the error payload must
+        # carry that value. Default-argument binding would freeze the stale one.
         def fail(message, prior=None):
-            raise ContinuityError(message, row, prior)
+            raise ContinuityError(message, row, prior)  # noqa: B023
 
         if kind == "fact":
             from inf_writer.domain import identity
diff --git a/code/core_engine/memory_runtime/engine.py b/code/core_engine/memory_runtime/engine.py
index f8a6915..193a237 100644
--- a/code/core_engine/memory_runtime/engine.py
+++ b/code/core_engine/memory_runtime/engine.py
@@ -1,11 +1,7 @@
 """Reusable atomic memory pipeline, independent of any test novel/run path."""
 
 import copy
-import sys
-from pathlib import Path
 
-SOURCE = Path(__file__).resolve().parent / "src"
-sys.path.insert(0, str(SOURCE))
 from inf_writer.domain import ContractError
 from inf_writer.tiered_memory import empty_memory, select_context
 from inf_writer.tiered_runtime import TieredMemoryAgent
diff --git a/code/core_engine/memory_runtime/pipeline.py b/code/core_engine/memory_runtime/pipeline.py
index 247a35e..a9c329b 100644
--- a/code/core_engine/memory_runtime/pipeline.py
+++ b/code/core_engine/memory_runtime/pipeline.py
@@ -1018,7 +1018,7 @@ def recall_selection(memory, query, max_bytes=36000, *, focus="balanced"):
                         value[1],
                     )
 
-                for score, identifier, row in sorted(group, key=first_source):
+                for _score, identifier, row in sorted(group, key=first_source):
                     if (
                         len(canonical(row).encode("utf-8")) <= witness_budget
                         and len(canonical(selected + [row]).encode("utf-8"))
@@ -1081,7 +1081,7 @@ def recall_selection(memory, query, max_bytes=36000, *, focus="balanced"):
         ),
     )
     reserved_subjects = set()
-    for score, identifier, row in reserved:
+    for _score, _identifier, row in reserved:
         if len(selected) >= 4:
             break
         if row["subject"] in reserved_subjects:
@@ -1169,11 +1169,11 @@ class ReviewedTemporal:
             return TemporalReconciler(Capture()).run(
                 before, after, chapters, number, selection, trace
             )
-        except TemporalUnresolved:
+        except TemporalUnresolved as unresolved:
             if _depth >= 3:
                 raise TemporalUnresolved(
                     "Uncertainty review round limit reached; chapter remains pending"
-                )
+                ) from unresolved
             issue_entry = trace[-1]
             issues = issue_entry["issues"]
             payload = {
@@ -1209,20 +1209,26 @@ class ReviewedTemporal:
             decisions = parsed["decisions"]
             wanted = {f"u{i:03d}" for i in range(1, len(issues) + 1)}
             if not isinstance(decisions, list):
-                raise ContractError("Uncertainty decisions must be list")
+                raise ContractError(
+                    "Uncertainty decisions must be list"
+                ) from unresolved
             seen = set()
             for decision in decisions:
                 fields(decision, ("ref", "decision", "reason"))
                 if decision["ref"] not in wanted or decision["ref"] in seen:
-                    raise ContractError("Invalid uncertainty review coverage")
+                    raise ContractError(
+                        "Invalid uncertainty review coverage"
+                    ) from unresolved
                 seen.add(decision["ref"])
                 if decision["decision"] not in (
                     "keep_unconfirmed",
                     "block",
                 ) or not isinstance(decision["reason"], str):
-                    raise ContractError("Invalid uncertainty disposition")
+                    raise ContractError(
+                        "Invalid uncertainty disposition"
+                    ) from unresolved
             if seen != wanted:
-                raise ContractError("Uncertainty review incomplete")
+                raise ContractError("Uncertainty review incomplete") from unresolved
             trace.append(
                 {
                     "role": "uncertainty_review",
@@ -1234,7 +1240,9 @@ class ReviewedTemporal:
                 }
             )
             if any(d["decision"] == "block" for d in decisions):
-                raise TemporalUnresolved("Uncertainty review retained blocking issue")
+                raise TemporalUnresolved(
+                    "Uncertainty review retained blocking issue"
+                ) from unresolved
             # Replay the unchanged first-stage decisions, removing only the
             # separately reviewed keep-unconfirmed requests. Full checks still run.
             raw, _ = normalize(strict_json(replies[-1].content))
@@ -1271,7 +1279,7 @@ class ReviewedTemporal:
             ):
                 raise ContractError(
                     "Cannot both retain and reconcile the same uncertain portion"
-                )
+                ) from unresolved
             # Empty unresolved placeholders carry no actionable parts/evidence.
             # A keep-unconfirmed verdict leaves these targets wholly unchanged.
             raw["changes"] = [
@@ -1350,7 +1358,7 @@ class ReviewedTemporal:
                 if any(new_parts.get(pid) != old_parts[pid] for pid in part_ids):
                     raise ContractError(
                         "Repair changed a reviewed keep-unconfirmed portion"
-                    )
+                    ) from unresolved
             result.setdefault("uncertain_prior_arrangements", []).append(
                 {
                     "chapter_number": number,
diff --git a/code/core_engine/memory_runtime/reference_choices.py b/code/core_engine/memory_runtime/reference_choices.py
index abe614c..a6be53d 100644
--- a/code/core_engine/memory_runtime/reference_choices.py
+++ b/code/core_engine/memory_runtime/reference_choices.py
@@ -290,10 +290,10 @@ def _compile_plan(
             )
             try:
                 parsed = strict_json(normalized)
-            except ContractError:
+            except ContractError as invalid:
                 raise ContractError(
                     "Malformed reference selector; use a selector object"
-                )
+                ) from invalid
             if not isinstance(parsed, dict):
                 raise ContractError("Reference selector must be an object")
             return resolve(parsed, current, depth + 1)
diff --git a/code/core_engine/memory_runtime/src/inf_writer/agents.py b/code/core_engine/memory_runtime/src/inf_writer/agents.py
index b5fc154..62d53e3 100644
--- a/code/core_engine/memory_runtime/src/inf_writer/agents.py
+++ b/code/core_engine/memory_runtime/src/inf_writer/agents.py
@@ -4,6 +4,7 @@ import copy
 from dataclasses import dataclass
 
 from .domain import ContractError, chapter_plan, fields, strict_json, text
+from .memory_output_contract import MEMORY_PROMPT
 from .models import ModelGateway, ModelRequest
 
 PROMPTS = {
@@ -98,8 +99,6 @@ PROMPTS["memory"] += (
     "不能为避免冲突删光候选或简单转换动作后覆盖旧值。"
 )
 
-from .memory_output_contract import MEMORY_PROMPT
-
 PROMPTS["memory"] = MEMORY_PROMPT
 
 
diff --git a/code/core_engine/memory_runtime/src/inf_writer/narrative_context.py b/code/core_engine/memory_runtime/src/inf_writer/narrative_context.py
index 29e72e9..376eb7a 100644
--- a/code/core_engine/memory_runtime/src/inf_writer/narrative_context.py
+++ b/code/core_engine/memory_runtime/src/inf_writer/narrative_context.py
@@ -32,12 +32,12 @@ def parse_planner_json(raw):
         try:
             _, end = json.JSONDecoder().raw_decode(stripped)
         except (ValueError, TypeError):
-            raise original
+            raise original from None
         if stripped[end:].strip() != "}":
-            raise original
+            raise original from None
         parsed = strict_json(stripped[:end])
         if not isinstance(parsed, dict):
-            raise original
+            raise original from None
         return parsed, [
             {
                 "rule": "planner_surplus_closing_brace",
diff --git a/code/core_engine/memory_runtime/story_closure.py b/code/core_engine/memory_runtime/story_closure.py
index 73b2484..9a1dd81 100644
--- a/code/core_engine/memory_runtime/story_closure.py
+++ b/code/core_engine/memory_runtime/story_closure.py
@@ -578,9 +578,6 @@ class StoryClosure:
                 rows_committed = False
                 end = min(start + CHUNK_CHARS, len(prose))
                 final = n >= self.plan["chapters"] and end == len(prose)
-                chapters = {
-                    c["number"]: c["text"] for c in self.session.book["chapters"]
-                }
                 sources = closing_sources(
                     self.session.book, n, max(0, start - 600), end
                 )
diff --git a/code/core_engine/memory_runtime/test_closure_repair.py b/code/core_engine/memory_runtime/test_closure_repair.py
index b80d8d5..ba5ff1a 100644
--- a/code/core_engine/memory_runtime/test_closure_repair.py
+++ b/code/core_engine/memory_runtime/test_closure_repair.py
@@ -7,7 +7,6 @@ from types import SimpleNamespace
 
 from inf_writer.domain import canonical
 from inf_writer.models import ModelReply
-
 from memory_runtime import test_story_closure as fixtures
 from memory_runtime.story_closure import StoryClosure
 
@@ -295,27 +294,31 @@ class RepairTests(unittest.TestCase):
         self.assertTrue(controller.passed())
 
     def test_bad_repair_format_and_choices_remain_queued_with_feedback(self):
-        for mode in ("json", "boolean", "missing", "unknown"):
+        class BadRepair(RepairProvider):
+            def __init__(self, mode):
+                super().__init__()
+                self.mode = mode
 
-            class BadRepair(RepairProvider):
-                def complete(self, request):
-                    reply = super().complete(request)
-                    if request.role != "closure_repair":
-                        return reply
-                    if mode == "json":
-                        return ModelReply("{broken", 1, 1, 0)
-                    value = json.loads(reply.content)
-                    row = value["obligations"][0]
-                    if mode == "missing":
-                        value["obligations"] = []
-                    else:
-                        row["evidence"] = [
-                            {"source_choice": True if mode == "boolean" else 999}
-                        ]
-                    return ModelReply(canonical(value), 1, 1, 0)
+            def complete(self, request):
+                mode = self.mode
+                reply = super().complete(request)
+                if request.role != "closure_repair":
+                    return reply
+                if mode == "json":
+                    return ModelReply("{broken", 1, 1, 0)
+                value = json.loads(reply.content)
+                row = value["obligations"][0]
+                if mode == "missing":
+                    value["obligations"] = []
+                else:
+                    row["evidence"] = [
+                        {"source_choice": True if mode == "boolean" else 999}
+                    ]
+                return ModelReply(canonical(value), 1, 1, 0)
 
+        for mode in ("json", "boolean", "missing", "unknown"):
             with self.subTest(mode=mode):
-                provider = BadRepair()
+                provider = BadRepair(mode)
                 controller = self.controller(provider)
                 self.observe(controller)
                 self.assertTrue(controller.repairs.pending())
diff --git a/code/core_engine/memory_runtime/test_completion.py b/code/core_engine/memory_runtime/test_completion.py
index 5afb767..40e2234 100644
--- a/code/core_engine/memory_runtime/test_completion.py
+++ b/code/core_engine/memory_runtime/test_completion.py
@@ -12,7 +12,6 @@ from unittest.mock import patch
 import write_novel as cli
 from inf_writer.domain import canonical
 from inf_writer.models import ModelReply
-
 from memory_runtime.completion import prose_from_reply
 from memory_runtime.test_event_first import EventLocal, event_config
 from memory_runtime.writing import WritingSession, load_resume
diff --git a/code/core_engine/memory_runtime/test_continuity.py b/code/core_engine/memory_runtime/test_continuity.py
index 27c193f..43803e9 100644
--- a/code/core_engine/memory_runtime/test_continuity.py
+++ b/code/core_engine/memory_runtime/test_continuity.py
@@ -9,7 +9,6 @@ ROOT = Path(__file__).resolve().parents[1]
 sys.path.insert(0, str(ROOT))
 from inf_writer.domain import ContractError, canonical
 from inf_writer.models import ModelReply
-
 from memory_runtime.continuity import apply, context_view, empty, guard
 
 
@@ -287,14 +286,19 @@ class ContinuityTests(unittest.TestCase):
                 "continuity_updates": [row],
             },
         ]
-        for reply in bad_replies:
 
-            class Gateway:
-                def complete(self, request):
-                    return ModelReply(canonical(reply), 0, 0, 0)
+        class Gateway:
+            def __init__(self, reply):
+                self.reply = reply
 
+            def complete(self, request):
+                return ModelReply(canonical(self.reply), 0, 0, 0)
+
+        for reply in bad_replies:
             with self.assertRaises(ContractError):
-                guard(state, [row], None, "无关内容\n\n" + bad, 2, [], Gateway(), [])
+                guard(
+                    state, [row], None, "无关内容\n\n" + bad, 2, [], Gateway(reply), []
+                )
 
 
 if __name__ == "__main__":
diff --git a/code/core_engine/memory_runtime/test_ending_intents.py b/code/core_engine/memory_runtime/test_ending_intents.py
index 12bd92f..438b44e 100644
--- a/code/core_engine/memory_runtime/test_ending_intents.py
+++ b/code/core_engine/memory_runtime/test_ending_intents.py
@@ -12,8 +12,6 @@ from unittest.mock import patch
 import write_novel as cli
 from inf_writer.domain import canonical
 from inf_writer.models import ModelReply
-from user_runtime import run_draft_trial
-
 from memory_runtime.narrative_planning import (
     pending_planning_jobs,
     thread_report,
@@ -23,6 +21,7 @@ from memory_runtime.narrative_repair import queue_ending_intent_review
 from memory_runtime.story_closure import StoryClosure
 from memory_runtime.test_event_first import ROOT
 from memory_runtime.writing import WritingSession, load_resume
+from user_runtime import run_draft_trial
 
 SOURCE = ROOT / "runs/event_first_30000_20261028_full_after_transfer_resume_a"
 
diff --git a/code/core_engine/memory_runtime/test_event_first.py b/code/core_engine/memory_runtime/test_event_first.py
index 9a3d01e..d991c80 100644
--- a/code/core_engine/memory_runtime/test_event_first.py
+++ b/code/core_engine/memory_runtime/test_event_first.py
@@ -15,7 +15,6 @@ sys.path.insert(0, str(ROOT))
 import write_novel as cli
 from inf_writer.domain import ContractError, canonical, digest
 from inf_writer.models import ModelReply
-
 from memory_runtime.continuity import empty
 from memory_runtime.event_first import prepare, project_memory, realize
 from memory_runtime.test_writing import Local, config
@@ -252,7 +251,6 @@ class EventFirstTests(unittest.TestCase):
 
     def test_real_r_prepared_chapter_fits_writer_budget_without_losing_events(self):
         from inf_writer.narrative_context import event_role_context
-
         from memory_runtime.event_first import writer_view
         from memory_runtime.writing import WritingSession
 
@@ -401,48 +399,48 @@ class EventFirstTests(unittest.TestCase):
         }
         memory = project_memory(MemoryEngine.empty(), [chapter], 1, [])
         original = copy.deepcopy(memory)
-        for second in ("valid", "invalid", "malformed", "duplicate"):
 
-            class Partial:
-                def __init__(self):
-                    self.requests = []
+        class Partial:
+            def __init__(self, second):
+                self.second = second
+                self.requests = []
 
-                def complete(self, request):
-                    self.requests.append(copy.deepcopy(request))
-                    rows = request.payload["items"]
-                    if len(self.requests) == 1:
-                        value = {
-                            "placements": [
-                                {
-                                    "id": r["id"],
-                                    "tier": "recent",
-                                    "priority": 3,
-                                    "reason": "已完成",
-                                }
-                                for r in rows[:-1]
-                            ]
-                        }
-                    elif second == "malformed":
-                        return ModelReply("not json", 1, 1, 0)
-                    else:
-                        value = {
-                            "placements": [
-                                {
-                                    "id": r["id"],
-                                    "tier": "recent"
-                                    if second != "invalid"
-                                    else "unknown",
-                                    "priority": 3,
-                                    "reason": "归档",
-                                }
-                                for r in rows
-                            ]
-                        }
-                        if second == "duplicate":
-                            value["placements"] *= 3
-                    return ModelReply(canonical(value), 1, 1, 0)
+            def complete(self, request):
+                second = self.second
+                self.requests.append(copy.deepcopy(request))
+                rows = request.payload["items"]
+                if len(self.requests) == 1:
+                    value = {
+                        "placements": [
+                            {
+                                "id": r["id"],
+                                "tier": "recent",
+                                "priority": 3,
+                                "reason": "已完成",
+                            }
+                            for r in rows[:-1]
+                        ]
+                    }
+                elif second == "malformed":
+                    return ModelReply("not json", 1, 1, 0)
+                else:
+                    value = {
+                        "placements": [
+                            {
+                                "id": r["id"],
+                                "tier": "recent" if second != "invalid" else "unknown",
+                                "priority": 3,
+                                "reason": "归档",
+                            }
+                            for r in rows
+                        ]
+                    }
+                    if second == "duplicate":
+                        value["placements"] *= 3
+                return ModelReply(canonical(value), 1, 1, 0)
 
-            gateway = Partial()
+        for second in ("valid", "invalid", "malformed", "duplicate"):
+            gateway = Partial(second)
             trace = []
             result, report = LayerAgent(gateway).run(
                 memory, [chapter], 1, "来信", trace
diff --git a/code/core_engine/memory_runtime/test_evidence_access.py b/code/core_engine/memory_runtime/test_evidence_access.py
index 0191bf3..e841b0d 100644
--- a/code/core_engine/memory_runtime/test_evidence_access.py
+++ b/code/core_engine/memory_runtime/test_evidence_access.py
@@ -10,7 +10,6 @@ from unittest.mock import patch
 import write_novel as cli
 from inf_writer.domain import canonical, digest
 from inf_writer.models import ModelReply
-
 from memory_runtime.evidence_access import context as material_context
 from memory_runtime.narrative_planning import (
     context,
diff --git a/code/core_engine/memory_runtime/test_generation_foundations.py b/code/core_engine/memory_runtime/test_generation_foundations.py
index 7648fa6..a90f365 100644
--- a/code/core_engine/memory_runtime/test_generation_foundations.py
+++ b/code/core_engine/memory_runtime/test_generation_foundations.py
@@ -10,7 +10,6 @@ from types import SimpleNamespace
 import write_novel as cli
 from inf_writer.domain import ContractError, canonical, digest
 from inf_writer.models import ModelReply
-
 from memory_runtime.continuity import empty
 from memory_runtime.length_control import adjust
 from memory_runtime.stage_planning import prepare_stages
@@ -41,13 +40,16 @@ class FoundationTests(unittest.TestCase):
             )
 
             class Replay:
+                def __init__(self, reply):
+                    self.reply = reply
+
                 def complete(self, request):
-                    return ModelReply(**r)
+                    return ModelReply(**self.reply)
 
             draft = q["payload"]["current_draft"]
             book = {"goal": "小说", "constraints": []}
             saved, report = adjust(
-                draft, 1, book, q["payload"]["chapter_number"], Replay(), []
+                draft, 1, book, q["payload"]["chapter_number"], Replay(r), []
             )
             self.assertEqual(saved, draft)
             self.assertEqual(report["adjustment"], "kept_original_incomplete_reply")
diff --git a/code/core_engine/memory_runtime/test_grounding_references.py b/code/core_engine/memory_runtime/test_grounding_references.py
index 5156632..ad90353 100644
--- a/code/core_engine/memory_runtime/test_grounding_references.py
+++ b/code/core_engine/memory_runtime/test_grounding_references.py
@@ -7,7 +7,6 @@ from unittest.mock import patch
 
 from inf_writer.domain import ContractError, canonical, digest, evidence_segments
 from inf_writer.models import ModelReply
-
 from memory_runtime.engine import MemoryEngine
 from memory_runtime.event_first import project_memory
 from memory_runtime.projection_grounding import _decision, ground, verify_grounding
@@ -86,7 +85,7 @@ class GroundingReferenceTests(unittest.TestCase):
                 c = chapter()
                 memory = project_memory(MemoryEngine.empty(), [c], 1, [])
 
-                def reply(rows, n):
+                def reply(rows, n, bad=bad):
                     rows = source_only(rows)
                     for row in rows:
                         row["support"][0]["evidence_position"] = bad
diff --git a/code/core_engine/memory_runtime/test_input_output_budget.py b/code/core_engine/memory_runtime/test_input_output_budget.py
index ea5466e..429b82a 100644
--- a/code/core_engine/memory_runtime/test_input_output_budget.py
+++ b/code/core_engine/memory_runtime/test_input_output_budget.py
@@ -11,7 +11,6 @@ from inf_writer.agents import JsonAgent
 from inf_writer.chat_provider import ChatCompletionProvider
 from inf_writer.domain import canonical, digest
 from inf_writer.models import ModelReply, ModelRequest
-
 from memory_runtime.input_budget import fit, select_qualified_state, size
 
 
@@ -196,7 +195,6 @@ class InputOutputBudgetTests(unittest.TestCase):
 
     def test_dependency_wrapper_never_allows_unknown_or_ambiguous_selector(self):
         from inf_writer.domain import ContractError
-
         from memory_runtime.reference_choices import compile_plan
         from memory_runtime.test_stage_repair import public_plan
 
diff --git a/code/core_engine/memory_runtime/test_interface_memory_repair.py b/code/core_engine/memory_runtime/test_interface_memory_repair.py
index 18d4d1c..1baa0af 100644
--- a/code/core_engine/memory_runtime/test_interface_memory_repair.py
+++ b/code/core_engine/memory_runtime/test_interface_memory_repair.py
@@ -12,7 +12,6 @@ from unittest.mock import patch
 import write_novel as cli
 from inf_writer.domain import ContractError, canonical
 from inf_writer.models import ModelReply
-
 from memory_runtime.continuity import empty
 from memory_runtime.engine import MemoryEngine
 from memory_runtime.event_contract import (
diff --git a/code/core_engine/memory_runtime/test_memory_meaning.py b/code/core_engine/memory_runtime/test_memory_meaning.py
index e42e203..f3a5a5e 100644
--- a/code/core_engine/memory_runtime/test_memory_meaning.py
+++ b/code/core_engine/memory_runtime/test_memory_meaning.py
@@ -18,7 +18,6 @@ from inf_writer.memory_meaning import (
 )
 from inf_writer.models import ModelReply
 from inf_writer.tiered_memory import apply_delta, empty_memory
-
 from memory_runtime.meaning_organizer import _annotate, _relation, organize
 
 
diff --git a/code/core_engine/memory_runtime/test_narrative_accountability.py b/code/core_engine/memory_runtime/test_narrative_accountability.py
index 3a548d9..ca98dd2 100644
--- a/code/core_engine/memory_runtime/test_narrative_accountability.py
+++ b/code/core_engine/memory_runtime/test_narrative_accountability.py
@@ -11,7 +11,6 @@ from unittest.mock import patch
 
 from inf_writer.domain import canonical, digest
 from inf_writer.models import ModelReply
-
 from memory_runtime.narrative_planning import (
     context,
     normalize,
diff --git a/code/core_engine/memory_runtime/test_narrative_planning.py b/code/core_engine/memory_runtime/test_narrative_planning.py
index 61afc85..ff4a89a 100644
--- a/code/core_engine/memory_runtime/test_narrative_planning.py
+++ b/code/core_engine/memory_runtime/test_narrative_planning.py
@@ -12,7 +12,6 @@ from unittest.mock import patch
 import write_novel as cli
 from inf_writer.domain import ContractError, canonical, digest
 from inf_writer.models import ModelReply
-
 from memory_runtime.narrative_planning import (
     context,
     design_units,
diff --git a/code/core_engine/memory_runtime/test_planner_boundary.py b/code/core_engine/memory_runtime/test_planner_boundary.py
index 9232e4a..88fb427 100644
--- a/code/core_engine/memory_runtime/test_planner_boundary.py
+++ b/code/core_engine/memory_runtime/test_planner_boundary.py
@@ -8,7 +8,6 @@ from inf_writer.agents import JsonAgent, validate
 from inf_writer.domain import ContractError
 from inf_writer.models import ModelReply
 from inf_writer.narrative_context import normalize_planner_metadata, parse_planner_json
-
 from memory_runtime.reference_choices import compile_plan
 from memory_runtime.test_event_first import ROOT
 
diff --git a/code/core_engine/memory_runtime/test_projection_grounding.py b/code/core_engine/memory_runtime/test_projection_grounding.py
index d7f6116..257822f 100644
--- a/code/core_engine/memory_runtime/test_projection_grounding.py
+++ b/code/core_engine/memory_runtime/test_projection_grounding.py
@@ -12,7 +12,6 @@ from unittest.mock import patch
 from inf_writer.domain import ContractError, canonical, digest
 from inf_writer.models import ModelReply
 from inf_writer.tiered_memory import select_context
-
 from memory_runtime.engine import MemoryEngine
 from memory_runtime.event_first import project_memory
 from memory_runtime.pipeline import recall_selection
@@ -136,7 +135,9 @@ class ProjectionGroundingTests(unittest.TestCase):
         ):
             with self.subTest(transform=transform):
                 chapters, memory = self.setup_memory()
-                p = Grounded(lambda rows, n: {"decisions": transform(rows)})
+                p = Grounded(
+                    lambda rows, n, transform=transform: {"decisions": transform(rows)}
+                )
                 result = ground(memory, chapters, 1, p, [])
                 self.assertTrue(result.get("projection_omissions"))
                 self.assertTrue(retryable_chapters(result))
@@ -217,7 +218,6 @@ class ProjectionGroundingTests(unittest.TestCase):
 
     def test_delayed_backfill_never_overwrites_later_current_value(self):
         chapters, memory = self.setup_memory()
-        first = chapters[0]["event_commit"]
         s = prepare(empty(), proposal(), 1)["candidate_state"]
         change = {"type": "transition", "fact_id": "location", "to_value": "楼上"}
         second = prepare(s, proposal([beat("up", "甲到了楼上。", [change])], 2), 2)[
@@ -365,9 +365,9 @@ class ProjectionGroundingTests(unittest.TestCase):
         self.assertEqual(latest["source_chapters"], [16])
 
     def test_launcher_exports_grounded_memory_and_next_context_reads_it(self):
-        import write_novel as cli
         from tools.testing.archived_plan_fixture import compile_archived_plan
 
+        import write_novel as cli
         from memory_runtime.writing import WritingSession, load_resume
 
         prose = "甲把来信拿进屋内，登记后放上桌面。"
diff --git a/code/core_engine/memory_runtime/test_projection_transfer.py b/code/core_engine/memory_runtime/test_projection_transfer.py
index 97dae99..afa5dc5 100644
--- a/code/core_engine/memory_runtime/test_projection_transfer.py
+++ b/code/core_engine/memory_runtime/test_projection_transfer.py
@@ -6,7 +6,6 @@ import unittest
 
 from inf_writer.domain import canonical
 from inf_writer.models import ModelReply
-
 from memory_runtime.projection_grounding import (
     ground,
     qualify_state_view,
diff --git a/code/core_engine/memory_runtime/test_prose_generation.py b/code/core_engine/memory_runtime/test_prose_generation.py
index 06de2b4..a5b97de 100644
--- a/code/core_engine/memory_runtime/test_prose_generation.py
+++ b/code/core_engine/memory_runtime/test_prose_generation.py
@@ -12,7 +12,6 @@ from unittest.mock import patch
 import write_novel as cli
 from inf_writer.domain import ContractError, canonical, digest
 from inf_writer.models import ModelReply
-
 from memory_runtime.continuity import empty
 from memory_runtime.event_first import prepare, project_memory
 from memory_runtime.numeric_grounding import sources
diff --git a/code/core_engine/memory_runtime/test_provider_stop.py b/code/core_engine/memory_runtime/test_provider_stop.py
index fbc47a1..f83d28c 100644
--- a/code/core_engine/memory_runtime/test_provider_stop.py
+++ b/code/core_engine/memory_runtime/test_provider_stop.py
@@ -14,10 +14,9 @@ from inf_writer.chat_provider import ChatCompletionProvider, ProviderError
 from inf_writer.domain import canonical
 from inf_writer.models import ModelReply, ModelRequest
 from inf_writer.trial import RecordedProvider
-from user_runtime import MeteredGateway, run_draft_trial
-
 from memory_runtime.test_event_first import ROOT
 from memory_runtime.writing import WritingSession, load_resume
+from user_runtime import MeteredGateway, run_draft_trial
 
 
 class ProviderStopTests(unittest.TestCase):
@@ -54,17 +53,19 @@ class ProviderStopTests(unittest.TestCase):
             self.assertNotIn("sensitive", canonical(error))
 
     def test_permanent_refusal_latches_across_writer_and_memory_without_new_calls(self):
-        for status in (401, 402, 403):
-            with self.subTest(status=status):
+        class Provider:
+            calls = 0
 
-                class Provider:
-                    calls = 0
+            def __init__(self, status):
+                self.status = status
 
-                    def complete(self, r):
-                        self.calls += 1
-                        raise ProviderError("sanitized", http_status=status)
+            def complete(self, r):
+                self.calls += 1
+                raise ProviderError("sanitized", http_status=self.status)
 
-                provider = Provider()
+        for status in (401, 402, 403):
+            with self.subTest(status=status):
+                provider = Provider(status)
                 gateway = MeteredGateway(provider)
                 for role in ("writer", "memory", "planner"):
                     with self.assertRaises(ProviderError):
@@ -74,19 +75,21 @@ class ProviderStopTests(unittest.TestCase):
                 self.assertEqual(gateway.provider_blocked["http_status"], status)
 
     def test_transient_or_payload_error_does_not_globally_latch(self):
-        for status in (400, 429, 500, 503):
-            with self.subTest(status=status):
+        class Provider:
+            calls = 0
 
-                class Provider:
-                    calls = 0
+            def __init__(self, status):
+                self.status = status
 
-                    def complete(self, r):
-                        self.calls += 1
-                        if self.calls == 1:
-                            raise ProviderError("sanitized", http_status=status)
-                        return ModelReply("正文", 1, 1, 0)
+            def complete(self, r):
+                self.calls += 1
+                if self.calls == 1:
+                    raise ProviderError("sanitized", http_status=self.status)
+                return ModelReply("正文", 1, 1, 0)
 
-                provider = Provider()
+        for status in (400, 429, 500, 503):
+            with self.subTest(status=status):
+                provider = Provider(status)
                 gateway = MeteredGateway(provider)
                 with self.assertRaises(ProviderError):
                     gateway.complete(ModelRequest("writer", "test", {}, 10))
diff --git a/code/core_engine/memory_runtime/test_quote_repair.py b/code/core_engine/memory_runtime/test_quote_repair.py
index 3546120..86985d9 100644
--- a/code/core_engine/memory_runtime/test_quote_repair.py
+++ b/code/core_engine/memory_runtime/test_quote_repair.py
@@ -8,7 +8,6 @@ from unittest.mock import patch
 
 from inf_writer.domain import ContractError, canonical
 from inf_writer.models import ModelReply
-
 from memory_runtime.engine import MemoryEngine
 from memory_runtime.event_first import project_memory
 from memory_runtime.projection_grounding import (
diff --git a/code/core_engine/memory_runtime/test_recall_search.py b/code/core_engine/memory_runtime/test_recall_search.py
index 2bbd06b..0c5be68 100644
--- a/code/core_engine/memory_runtime/test_recall_search.py
+++ b/code/core_engine/memory_runtime/test_recall_search.py
@@ -8,7 +8,6 @@ from pathlib import Path
 import write_novel
 from inf_writer.domain import ContractError, canonical
 from inf_writer.models import ModelReply
-
 from memory_runtime.pipeline import recall_selection
 from memory_runtime.recall_search import searches, selection, source_windows
 from memory_runtime.test_memory_meaning import fixture
diff --git a/code/core_engine/memory_runtime/test_regression.py b/code/core_engine/memory_runtime/test_regression.py
index 7cdb35e..16dba9e 100644
--- a/code/core_engine/memory_runtime/test_regression.py
+++ b/code/core_engine/memory_runtime/test_regression.py
@@ -8,7 +8,12 @@ from pathlib import Path
 ROOT = Path(__file__).resolve().parents[1]
 sys.path.insert(0, str(ROOT))
 sys.path.insert(0, str(ROOT / "memory_runtime/src"))
+from inf_writer.domain import ContractError, canonical
+from inf_writer.models import ModelReply, ModelRequest
+from inf_writer.temporal_agent import SYSTEM
+from inf_writer.tiered_runtime import MEMORY_SYSTEM
 from memory_runtime import pipeline
+from memory_runtime.engine import MemoryEngine
 
 sys.modules["components"] = pipeline
 spec = importlib.util.spec_from_file_location(
@@ -171,13 +176,6 @@ class ContinuousTests(fixtures.ContinuousTests):
         self.assertEqual(result["temporal_processed_through"], 11)
 
 
-from inf_writer.domain import ContractError, canonical
-from inf_writer.models import ModelReply, ModelRequest
-from inf_writer.temporal_agent import SYSTEM
-from inf_writer.tiered_runtime import MEMORY_SYSTEM
-
-from memory_runtime.engine import MemoryEngine
-
 _fixture_complete = fixtures.FixtureGateway.complete
 
 
@@ -673,7 +671,6 @@ class StructuralRegression(unittest.TestCase):
         import json
 
         from inf_writer.tiered_memory import apply_delta
-
         from memory_runtime.semantics import guard_extraction
 
         parent = ROOT / "runs/continuous_memory_stable_20261021_d"
@@ -735,7 +732,6 @@ class StructuralRegression(unittest.TestCase):
 
         from inf_writer.memory_temporality import annotated
         from inf_writer.tiered_memory import apply_delta, empty_memory
-
         from memory_runtime.semantics import guard_temporal
 
         prose = [
diff --git a/code/core_engine/memory_runtime/test_scene_memory_coordination.py b/code/core_engine/memory_runtime/test_scene_memory_coordination.py
index 1935395..b1d119c 100644
--- a/code/core_engine/memory_runtime/test_scene_memory_coordination.py
+++ b/code/core_engine/memory_runtime/test_scene_memory_coordination.py
@@ -7,7 +7,6 @@ from types import SimpleNamespace
 from unittest.mock import patch
 
 from inf_writer.domain import ContractError
-
 from memory_runtime.engine import MemoryEngine
 from memory_runtime.narrative_planning import design_units
 from memory_runtime.reference_choices import compile_plan
diff --git a/code/core_engine/memory_runtime/test_stage_format_preservation.py b/code/core_engine/memory_runtime/test_stage_format_preservation.py
index 516ce05..ee7cd17 100644
--- a/code/core_engine/memory_runtime/test_stage_format_preservation.py
+++ b/code/core_engine/memory_runtime/test_stage_format_preservation.py
@@ -7,7 +7,6 @@ import unittest
 from inf_writer.agents import JsonAgent
 from inf_writer.domain import ContractError, canonical
 from inf_writer.models import ModelReply
-
 from memory_runtime.completion import continue_prose
 from memory_runtime.test_event_first import ROOT
 
diff --git a/code/core_engine/memory_runtime/test_stage_repair.py b/code/core_engine/memory_runtime/test_stage_repair.py
index dc42022..448873d 100644
--- a/code/core_engine/memory_runtime/test_stage_repair.py
+++ b/code/core_engine/memory_runtime/test_stage_repair.py
@@ -9,7 +9,6 @@ from pathlib import Path
 import write_novel as cli
 from inf_writer.domain import ContractError, canonical, digest
 from inf_writer.models import ModelReply
-
 from memory_runtime.continuity import empty
 from memory_runtime.event_first import prepare, verify
 from memory_runtime.event_references import catalogue
diff --git a/code/core_engine/memory_runtime/test_state_recovery.py b/code/core_engine/memory_runtime/test_state_recovery.py
index f7f3d1b..ab834ec 100644
--- a/code/core_engine/memory_runtime/test_state_recovery.py
+++ b/code/core_engine/memory_runtime/test_state_recovery.py
@@ -9,7 +9,6 @@ from pathlib import Path
 import write_novel as cli
 from inf_writer.domain import ContractError, canonical, digest
 from inf_writer.models import ModelReply
-
 from memory_runtime.plan_repair import protect_targets
 from memory_runtime.reference_choices import compile_plan
 from memory_runtime.state_recovery import _packet, directory, verify_recoveries
diff --git a/code/core_engine/memory_runtime/test_story_closure.py b/code/core_engine/memory_runtime/test_story_closure.py
index a7e6d6c..8585d89 100644
--- a/code/core_engine/memory_runtime/test_story_closure.py
+++ b/code/core_engine/memory_runtime/test_story_closure.py
@@ -11,7 +11,6 @@ from unittest.mock import patch
 
 from inf_writer.domain import canonical
 from inf_writer.models import ModelReply
-
 from memory_runtime.story_closure import (
     CHUNK_CHARS,
     StoryClosure,
diff --git a/code/core_engine/memory_runtime/test_story_review.py b/code/core_engine/memory_runtime/test_story_review.py
index b63bf82..307840d 100644
--- a/code/core_engine/memory_runtime/test_story_review.py
+++ b/code/core_engine/memory_runtime/test_story_review.py
@@ -10,7 +10,6 @@ ROOT = Path(__file__).resolve().parents[1]
 sys.path.insert(0, str(ROOT))
 from inf_writer.domain import ContractError, canonical
 from inf_writer.models import ModelReply
-
 from memory_runtime.story_review import StoryReviewAgent, adjudicate_issues
 
 
@@ -72,7 +71,6 @@ class Replies:
 class EditorialTests(unittest.TestCase):
     def test_real_u_pending_review_shares_evidence_losslessly_under_same_budget(self):
         from inf_writer.light_memory import prepare_review
-
         from memory_runtime.story_review import (
             REVIEW_PROMPT,
             REVIEW_RULES,
@@ -132,7 +130,10 @@ class EditorialTests(unittest.TestCase):
         self,
     ):
         folder = ROOT / "runs/writing_tiered_30000_20261021_c"
-        read = lambda name: json.loads((folder / name).read_text(encoding="utf-8"))
+
+        def read(name):
+            return json.loads((folder / name).read_text(encoding="utf-8"))
+
         original = json.loads(read("call_006.response.json")["content"])
         ctx = read("call_006.request.json")["payload"]
         decisions = [
diff --git a/code/core_engine/memory_runtime/test_thread_closure.py b/code/core_engine/memory_runtime/test_thread_closure.py
index 1c7116d..a132b5a 100644
--- a/code/core_engine/memory_runtime/test_thread_closure.py
+++ b/code/core_engine/memory_runtime/test_thread_closure.py
@@ -12,7 +12,6 @@ from unittest.mock import patch
 
 from inf_writer.domain import ContractError, canonical, digest
 from inf_writer.models import ModelReply
-
 from memory_runtime.narrative_planning import (
     apply_thread_review,
     context,
diff --git a/code/core_engine/memory_runtime/test_time_calculation.py b/code/core_engine/memory_runtime/test_time_calculation.py
index baf032a..65acb4c 100644
--- a/code/core_engine/memory_runtime/test_time_calculation.py
+++ b/code/core_engine/memory_runtime/test_time_calculation.py
@@ -10,7 +10,6 @@ ROOT = Path(__file__).resolve().parents[1]
 sys.path.insert(0, str(ROOT))
 from inf_writer.domain import ContractError, canonical
 from inf_writer.models import ModelReply
-
 from memory_runtime.time_calculation import (
     calculate,
     render,
diff --git a/code/core_engine/memory_runtime/test_writing.py b/code/core_engine/memory_runtime/test_writing.py
index 446cf05..7037d4f 100644
--- a/code/core_engine/memory_runtime/test_writing.py
+++ b/code/core_engine/memory_runtime/test_writing.py
@@ -16,7 +16,6 @@ import write_novel as cli
 from inf_writer.domain import ContractError, canonical
 from inf_writer.light_memory import LightAgent, validate_light_review
 from inf_writer.models import ModelReply, ModelRequest
-
 from memory_runtime.story_review import StoryReferenceGateway
 from memory_runtime.writing import load_resume
 
@@ -213,6 +212,14 @@ class WritingIntegration(unittest.TestCase):
             "active_facts": [{"memory_id": "m_known", "value": "旧事实"}],
             "hard_references": {"fact_1": "旧事实"},
         }
+
+        class Saved:
+            def __init__(self, body):
+                self.body = body
+
+            def complete(self, request):
+                return ModelReply(canonical(self.body), 1, 1, 0)
+
         for identifier, quote in (("m_unknown", "旧事实"), ("m_known", "不存在的证据")):
             body = {
                 "approved": False,
@@ -227,12 +234,7 @@ class WritingIntegration(unittest.TestCase):
                 ],
                 "suggestions": [],
             }
-
-            class Saved:
-                def complete(self, request):
-                    return ModelReply(canonical(body), 1, 1, 0)
-
-            transport = StoryReferenceGateway(Saved())
+            transport = StoryReferenceGateway(Saved(body))
             request = ModelRequest("reviewer", "", payload, 8192)
             parsed = json.loads(transport.complete(request).content)
             with self.assertRaises(ContractError):
diff --git a/code/core_engine/memory_runtime/writing.py b/code/core_engine/memory_runtime/writing.py
index 6fcb382..0986983 100644
--- a/code/core_engine/memory_runtime/writing.py
+++ b/code/core_engine/memory_runtime/writing.py
@@ -841,7 +841,6 @@ class WritingSession:
         public_proposal = None
         last_public = None
         last_compiled = None
-        last_error = None
         last_design = {}
 
         def validate(value, *, preserve_design=False):
diff --git a/tests/integration/vue_ui_preview.py b/tests/integration/vue_ui_preview.py
index 0772aed..f51eed5 100644
--- a/tests/integration/vue_ui_preview.py
+++ b/tests/integration/vue_ui_preview.py
@@ -3,12 +3,13 @@
 Run with PYTHONPATH=code/core_engine;code/backend and open localhost:8766.
 All fixture books and configuration are disposable temporary files.
 """
+
 import argparse
 import copy
 import os
-from pathlib import Path
 import tempfile
 import time
+from pathlib import Path
 
 
 def main():
@@ -20,10 +21,13 @@ def main():
         os.environ["TOME_DATA_HOME"] = directory
         os.environ.pop("DEEPSEEK_API_KEY", None)
         if not args.unconfigured:
-            Path(directory, ".env").write_text("DEEPSEEK_API_KEY=sk-VUE_TEST_ONLY_NOT_REAL\n", encoding="utf-8")
-        from inf_backend import service, library, official_pricing
-        from inf_backend.web import WebServer, Handler
+            Path(directory, ".env").write_text(
+                "DEEPSEEK_API_KEY=sk-VUE_TEST_ONLY_NOT_REAL\n", encoding="utf-8"
+            )
+        from inf_backend import library, official_pricing, service
         from inf_backend.settings import Settings
+        from inf_backend.web import Handler, WebServer
+
         metrics = {"generation_calls": 0, "chapters_written": 0}
         states = {}
 
@@ -33,35 +37,69 @@ def main():
         def add_chapter(state):
             number = len(state["chapters"]) + 1
             text = f"这是第{number}章的测试正文。\n角色拿起钥匙，走向下一段故事。"
-            state["chapters"].append({"number": number, "title": f"测试章节{number}", "text": text})
+            state["chapters"].append(
+                {"number": number, "title": f"测试章节{number}", "text": text}
+            )
             state["memory"]["items"][f"fact-{number}"] = {
-                "id": f"fact-{number}", "subject": f"角色{number}", "attribute": "item", "claim": "持有钥匙",
-                "status": "active", "tier": "working", "revision": number, "kind": "event",
-                "sources": [{"chapter_number": number, "quote": "角色拿起钥匙。"}]}
+                "id": f"fact-{number}",
+                "subject": f"角色{number}",
+                "attribute": "item",
+                "claim": "持有钥匙",
+                "status": "active",
+                "tier": "working",
+                "revision": number,
+                "kind": "event",
+                "sources": [{"chapter_number": number, "quote": "角色拿起钥匙。"}],
+            }
 
         def load_book(book_id):
-            return {"metadata": service._metadata(book_id), "state": copy.deepcopy(states.setdefault(book_id, empty_state()))}
+            return {
+                "metadata": service._metadata(book_id),
+                "state": copy.deepcopy(states.setdefault(book_id, empty_state())),
+            }
 
         def generate(book_id, *, count, progress, **options):
             metrics["generation_calls"] += 1
             state = states.setdefault(book_id, empty_state())
             for index in range(count):
-                progress({"completed": index, "current_chapter": len(state["chapters"]) + 1})
-                time.sleep(.7)
+                progress(
+                    {"completed": index, "current_chapter": len(state["chapters"]) + 1}
+                )
+                time.sleep(0.7)
                 add_chapter(state)
                 metrics["chapters_written"] += 1
-                progress({"completed": index + 1, "current_chapter": len(state["chapters"])})
+                progress(
+                    {"completed": index + 1, "current_chapter": len(state["chapters"])}
+                )
 
         service.load_book = load_book
         service.generate = generate
-        official_pricing.get_table = lambda: {"models": official_pricing.SNAPSHOT, "checked_at": "test-fixture", "status": "verified_snapshot"}
+        official_pricing.get_table = lambda: {
+            "models": official_pricing.SNAPSHOT,
+            "checked_at": "test-fixture",
+            "status": "verified_snapshot",
+        }
         fixture_settings = Settings(api_key="VUE_TEST_ONLY")
-        service.create_book("vue-ui-main", "Vue迁移测试作品", "仅用于界面测试，不调用模型", 5, 5000,
-                            settings=fixture_settings, style={"instructions": "简洁短句。", "reference": "测试片段。"})
+        service.create_book(
+            "vue-ui-main",
+            "Vue迁移测试作品",
+            "仅用于界面测试，不调用模型",
+            5,
+            5000,
+            settings=fixture_settings,
+            style={"instructions": "简洁短句。", "reference": "测试片段。"},
+        )
         states["vue-ui-main"] = empty_state()
         add_chapter(states["vue-ui-main"])
         add_chapter(states["vue-ui-main"])
-        service.create_book("vue-ui-trash", "废案箱测试作品", "测试恢复及确认框", 2, 1000, settings=fixture_settings)
+        service.create_book(
+            "vue-ui-trash",
+            "废案箱测试作品",
+            "测试恢复及确认框",
+            2,
+            1000,
+            settings=fixture_settings,
+        )
         library.delete_book("vue-ui-trash")
 
         class PreviewHandler(Handler):
@@ -73,7 +111,10 @@ def main():
 
         server = WebServer(("127.0.0.1", args.port))
         server.RequestHandlerClass = PreviewHandler
-        print(f"Isolated Vue UI fixture: http://127.0.0.1:{server.server_port}/ (no model calls)", flush=True)
+        print(
+            f"Isolated Vue UI fixture: http://127.0.0.1:{server.server_port}/ (no model calls)",
+            flush=True,
+        )
         try:
             server.serve_forever()
         except KeyboardInterrupt:
'''


class PatchError(RuntimeError):
    pass


def parse_patch(text):
    """Return [{path, hunks: [[(op, line), ...]]}] from a git-style unified diff."""
    files = []
    current = None
    hunk = None
    for line in text.splitlines():
        if line.startswith("diff --git "):
            current = {"path": None, "hunks": []}
            files.append(current)
            hunk = None
            continue
        if current is None:
            continue
        if line.startswith("+++ "):
            path = line[4:].strip()
            if path.startswith("b/"):
                path = path[2:]
            current["path"] = path
            continue
        if line.startswith("@@"):
            hunk = []
            current["hunks"].append(hunk)
            continue
        if hunk is None or line.startswith("\\"):
            continue
        if line[:1] in (" ", "+", "-"):
            hunk.append((line[0], line[1:]))
        elif line == "":
            hunk.append((" ", ""))
    for entry in files:
        if not entry["path"] or not entry["hunks"]:
            raise PatchError(f"malformed diff entry: {entry}")
    return files


def _find(seq, block, start):
    if not block:
        return start
    limit = len(seq) - len(block)
    first = block[0]
    index = start
    while index <= limit:
        try:
            index = seq.index(first, index)
        except ValueError:
            return -1
        if seq[index : index + len(block)] == block:
            return index
        index += 1
    return -1


def _read(path):
    with open(path, encoding="utf-8", newline="") as handle:
        text = handle.read()
    # Decide the line ending from the first newline only: source files can embed
    # literal "\r\n" inside string literals, which would fool a counting test.
    first_newline = text.find("\n")
    if first_newline > 0 and text[first_newline - 1] == "\r":
        eol = "\r\n"
    else:
        eol = "\n"
    return text, eol, text.splitlines()


def _write(path, lines, eol, trailing_newline):
    body = eol.join(lines)
    if trailing_newline:
        body += eol
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(body)


def apply_patch(root, patch_text, check=False):
    """Apply a patch in-place. Returns [(path, applied_hunks, skipped_hunks)]."""
    root = pathlib.Path(root)
    report = []
    for entry in parse_patch(patch_text):
        path = root / entry["path"]
        if not path.is_file():
            raise PatchError(f"target missing: {path}")
        text, eol, lines = _read(path)
        cursor = 0
        applied = 0
        skipped = 0
        for hunk in entry["hunks"]:
            before = [line for op, line in hunk if op in (" ", "-")]
            after = [line for op, line in hunk if op in (" ", "+")]
            index_before = _find(lines, before, cursor)
            index_after = _find(lines, after, cursor)
            # Whichever form comes first wins; the earlier "after" form means the
            # hunk was already applied (idempotent re-run).
            if index_after >= 0 and (index_before < 0 or index_after <= index_before):
                cursor = index_after + len(after)
                skipped += 1
                continue
            if index_before >= 0:
                lines[index_before : index_before + len(before)] = after
                cursor = index_before + len(after)
                applied += 1
                continue
            raise PatchError(
                f"hunk does not apply to {entry['path']} "
                f"(context already changed?): {before[:1]}"
            )
        if applied and not check:
            _write(path, lines, eol, text.endswith("\n"))
        report.append((entry["path"], applied, skipped))
    return report


# New Python modules introduced by the refactor (created, never patched).
PY_NEW_FILES = {
    "tests/unit/test_quality_refactors.py": r'''"""Regression tests for the five refactors in ``docs/quality/quality_report.md``.

Four of these tests fail on the pre-refactor baseline (commit ``e4d23ce``) and
pass after the refactor; the fifth pins behaviour the refactor had to preserve.

    python -m unittest tests.unit.test_quality_refactors -v
"""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from inf_backend import migrate, service
from inf_writer.domain import ContractError
from inf_writer.narrative_context import parse_planner_json
from memory_runtime import continuity
from memory_runtime.identifiers import attribute_identifier

REPO = pathlib.Path(__file__).resolve().parents[2]


class RaiseChainTests(unittest.TestCase):
    """Refactor 1 — Pylint W0707 / Ruff B904: an exception raised while handling
    another one must declare whether it was caused by it."""

    def test_longform_pointer_error_keeps_contract_error_as_cause(self):
        pointer = mock.Mock()
        pointer.read_text.return_value = json.dumps({"checkpoint": 1, "extra": 2})
        with (
            mock.patch.object(service.database, "enabled", return_value=False),
            mock.patch.object(service, "_metadata", return_value={"title": "t"}),
            mock.patch.object(service, "_longform_plan", return_value={}),
            mock.patch.object(
                service,
                "_load_longform_book",
                side_effect=ContractError("写作运行时版本不一致，不能直接恢复旧检查点"),
            ),
            mock.patch.object(service, "_longform_pointer", return_value=pointer),
        ):
            with self.assertRaises(ValueError) as caught:
                service.load_longform("book-1")

        self.assertIsInstance(caught.exception.__cause__, ContractError)

    def test_migrate_failure_suppresses_the_underlying_exception(self):
        with mock.patch.object(sys, "argv", ["migrate", "reconcile", "--apply"]):
            with self.assertRaises(SystemExit) as caught:
                migrate.main()

        self.assertTrue(caught.exception.__suppress_context__)

    def test_planner_json_recovery_does_not_leak_the_parser_error(self):
        with self.assertRaises(ContractError) as caught:
            parse_planner_json('{"a": 1} trailing text')

        # The recovery attempt must not expose the JSON parser's exception: the
        # caller only needs the contract-level error and the recovery notes.
        self.assertIsNone(caught.exception.__cause__)
        self.assertTrue(caught.exception.__suppress_context__)


class LoopClosureTests(unittest.TestCase):
    """Refactor 2 — Pylint W0640: the per-record error payload must describe the
    row as it is at the moment of failure, not a stale pre-normalised copy."""

    def test_continuity_error_reports_the_normalised_attribute(self):
        prose = "甲看见了门外的信。"
        base = {
            "type": "fact",
            "subject": "甲",
            "attribute": "当前位置",
            "value": "门外",
            "kind": "state",
            "quote": prose,
        }
        first = dict(base, id="f_position_a")
        duplicate = dict(base, id="f_position_b", value="屋内")

        with self.assertRaises(continuity.ContinuityError) as caught:
            continuity.apply(continuity.empty(), [first, duplicate], prose, 1)

        proposed = caught.exception.repair_details["proposed"]
        self.assertEqual(proposed["attribute"], attribute_identifier("当前位置"))
        self.assertNotEqual(proposed["attribute"], "当前位置")


class ImportBootstrapTests(unittest.TestCase):
    """Refactor 4 — Pylint C0413 / Ruff E402: importing the package itself must
    expose the bundled ``inf_writer``, so no submodule needs a mid-file
    ``sys.path`` insert before its imports."""

    def test_importing_memory_runtime_exposes_the_bundled_inf_writer(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            [str(REPO / "code/core_engine"), str(REPO / "code/backend")]
        )
        probe = (
            "import sys, memory_runtime;"
            "print(int(any(p.replace('\\\\', '/').endswith('memory_runtime/src')"
            " for p in sys.path)))"
        )
        outcome = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=str(REPO),
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(outcome.stdout.strip(), "1", outcome.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
''',
}

FENCE = re.compile(r"^(?P<fence>`{3,})\s*[\w+-]*$")
MD_MARK = re.compile(
    r'<!--\s*fixes:file\s+target="(?P<target>[^"]+)"\s+mode="(?P<mode>\w+)"\s*-->'
)


def load_toml_bundle(path):
    """Return [{target, mode, content}] from fixes.toml."""
    data = tomllib.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return [
        {
            "target": item["target"],
            "mode": item.get("mode", "create"),
            "content": item.get("content", ""),
        }
        for item in data.get("file", [])
    ]


def _parse_simple_yaml(text):
    """Parse this bundle's own YAML subset (fallback when PyYAML is absent)."""
    entries = []
    current = None
    block_key = None
    block_indent = 0
    for line in text.splitlines():
        if block_key:
            if not line.strip():
                current[block_key] += "\n"
                continue
            if line.startswith(" " * block_indent):
                current[block_key] += line[block_indent:] + "\n"
                continue
            block_key = None
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- target:"):
            current = {
                "target": stripped.split(":", 1)[1].strip(),
                "mode": "create",
                "patch": "",
                "content": "",
            }
            entries.append(current)
            continue
        if current is None:
            continue
        if stripped.startswith("mode:"):
            current["mode"] = stripped.split(":", 1)[1].strip()
        elif stripped in ("patch: |", "content: |"):
            block_key = stripped.split(":", 1)[0]
            block_indent = len(line) - len(line.lstrip()) + 2
    for entry in entries:
        for key in ("patch", "content"):
            if entry[key].endswith("\n\n"):
                entry[key] = entry[key].rstrip("\n") + "\n"
    return entries


def load_yaml_bundle(path):
    """Return [{target, mode, patch, content}] from fixes.yaml.

    Uses PyYAML when available and otherwise a small parser for this file's own
    subset, so the bundle has no hard third-party dependency.
    """
    text = pathlib.Path(path).read_text(encoding="utf-8")
    try:
        import yaml
    except ImportError:
        raw = _parse_simple_yaml(text)
    else:
        raw = yaml.safe_load(text).get("files", [])
    return [
        {
            "target": item["target"],
            "mode": item.get("mode", "create"),
            "patch": item.get("patch") or "",
            "content": item.get("content") or "",
        }
        for item in raw
    ]


def load_md_bundle(path):
    """Return [{target, mode, patch, content}] from fixes.md."""
    lines = pathlib.Path(path).read_text(encoding="utf-8").splitlines()
    entries = []
    index = 0
    while index < len(lines):
        mark = MD_MARK.search(lines[index])
        if not mark:
            index += 1
            continue
        index += 1
        while index < len(lines) and not lines[index].strip():
            index += 1
        fence = FENCE.match(lines[index].strip())
        if not fence:
            raise SystemExit(f"missing code fence after marker ({path}:{index + 1})")
        ticks = fence.group("fence")
        index += 1
        block = []
        while index < len(lines) and lines[index].strip() != ticks:
            block.append(lines[index])
            index += 1
        index += 1
        text = "\n".join(block) + "\n"
        mode = mark.group("mode")
        entries.append(
            {
                "target": mark.group("target"),
                "mode": mode,
                "patch": text if mode == "patch" else "",
                "content": text if mode == "create" else "",
            }
        )
    return entries


def create_file(root, entry, check):
    """Create a bundle-provided file; refuse to clobber a different one."""
    path = pathlib.Path(root) / entry["target"]
    content = entry["content"]
    if path.exists():
        existing = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        if existing == content:
            return entry["target"], "already present"
        raise SystemExit(f"refusing to overwrite differing file: {path}")
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
    return entry["target"], "would create" if check else "created"


def run_entries(root, entries, check):
    rows = []
    for entry in entries:
        if entry["mode"] == "create":
            rows.append(create_file(root, entry, check))
        else:
            for rel, applied, _ in apply_patch(root, entry["patch"], check=check):
                rows.append(
                    (rel, f"{applied} hunk(s)" if applied else "already applied")
                )
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="fixes.py", description="Apply the code-quality fix bundles."
    )
    parser.add_argument(
        "--root",
        default=str(pathlib.Path(__file__).resolve().parent.parent),
        help="repository root (default: parent directory of fixes/)",
    )
    parser.add_argument(
        "--check", action="store_true", help="report only, write nothing"
    )
    parser.add_argument(
        "--only",
        choices=["py", "yaml", "toml", "md", "all"],
        default="py",
        help="which bundle to apply (default: py)",
    )
    parser.add_argument("--all", action="store_true", help="shorthand for --only all")
    args = parser.parse_args(argv)

    here = pathlib.Path(__file__).resolve().parent
    loaders = {
        "yaml": ("fixes.yaml", load_yaml_bundle),
        "toml": ("fixes.toml", load_toml_bundle),
        "md": ("fixes.md", load_md_bundle),
    }
    everything = ["py", "yaml", "toml", "md"]
    selected = everything if (args.all or args.only == "all") else [args.only]

    changed = 0
    for name in selected:
        if name == "py":
            rows = [
                create_file(
                    args.root, {"target": target, "content": content}, args.check
                )
                for target, content in PY_NEW_FILES.items()
            ]
            rows += [
                (rel, f"{applied} hunk(s)" if applied else "already applied")
                for rel, applied, _ in apply_patch(
                    args.root, PY_PATCH, check=args.check
                )
            ]
        else:
            filename, loader = loaders[name]
            rows = run_entries(args.root, loader(here / filename), args.check)
        print(f"[{name}] {len(rows)} target(s)")
        for rel, status in rows:
            print(f"  {rel}: {status}")
            if not status.startswith("already"):
                changed += 1

    suffix = " (dry run, nothing written)" if args.check else ""
    print(f"\nchanged targets: {changed}{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
