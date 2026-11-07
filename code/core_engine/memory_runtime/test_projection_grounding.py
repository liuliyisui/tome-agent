"""Source-bound structured memory, partial repair and delayed replay safety."""

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inf_writer.domain import ContractError, canonical, digest
from inf_writer.models import ModelReply
from inf_writer.tiered_memory import select_context
from memory_runtime.engine import MemoryEngine
from memory_runtime.event_first import project_memory
from memory_runtime.pipeline import recall_selection
from memory_runtime.projection_grounding import (
    ground,
    retryable_chapters,
    verify_grounding,
)
from memory_runtime.test_event_first import (
    ROOT,
    EventLocal,
    beat,
    empty,
    event_config,
    fact,
    prepare,
    proposal,
)


def chapter(prose="甲把信带进屋，在屋内桌前登记。", number=1, commit=None):
    commit = (
        commit
        or prepare(
            empty(), proposal([beat(statement="甲在门外登记了来信。")], number), number
        )["commit"]
    )
    return {
        "number": number,
        "title": "来信",
        "text": prose,
        "sha256": digest(prose),
        "event_commit": commit,
        "prose_policy": "unchecked",
        "prose_encoding": "literal",
        "realization_template": prose,
    }


class Grounded(EventLocal):
    def __init__(self, behavior=None):
        super().__init__()
        self.behavior = behavior
        self.ground_calls = 0

    def complete(self, request):
        p = request.payload
        if request.role == "memory" and "candidates" in p and "evidence" in p:
            self.ground_calls += 1
            self.requests.append(copy.deepcopy(request))
            rows = [
                dict(
                    candidate_position=r["candidate_position"],
                    outcome="matched",
                    support=[
                        {"evidence_position": 1, "quote": p["evidence"][0]["text"]}
                    ],
                    reason="正文实际表达",
                    **({"task_status": "planned"} if r["kind"] == "task" else {}),
                )
                for r in p["candidates"]
            ]
            value = (
                self.behavior(rows, self.ground_calls)
                if self.behavior
                else {"decisions": rows}
            )
            if isinstance(value, Exception):
                raise value
            return ModelReply(canonical(value), 1, 1, 0)
        return super().complete(request)


class ProjectionGroundingTests(unittest.TestCase):
    def setup_memory(self):
        c = chapter()
        return [c], project_memory(MemoryEngine.empty(), [c], 1, [])

    def test_paraphrase_stores_actual_text_not_unrealized_plan_and_is_idempotent(self):
        chapters, before = self.setup_memory()
        original = copy.deepcopy(before)
        p = Grounded()
        result = ground(before, chapters, 1, p, [])
        self.assertFalse(result.get("projection_omissions"))
        self.assertTrue(verify_grounding(result, chapters))
        states = [r for r in result["items"].values() if r["kind"] == "state"]
        self.assertEqual(states[0]["claim"], chapters[0]["text"])
        self.assertNotIn("门外", states[0]["claim"])
        self.assertEqual(before, original)
        self.assertEqual(ground(result, chapters, 1, p, []), result)
        self.assertEqual(p.ground_calls, 1)
        selected = select_context(result, query="甲 来信 位置", max_bytes=22000)
        self.assertTrue(
            any(
                r["kind"] == "state" and r["claim"] == chapters[0]["text"]
                for r in selected["items"]
            )
        )

    def test_invalid_peer_is_repaired_without_repeating_accepted_rows(self):
        chapters, memory = self.setup_memory()

        def behavior(rows, attempt):
            if attempt == 1:
                rows[1]["support"][0]["quote"] = "编造的证据"
            return {"decisions": rows}

        p = Grounded(behavior)
        trace = []
        result = ground(memory, chapters, 1, p, trace)
        self.assertEqual(p.ground_calls, 2)
        self.assertEqual(len(p.requests[1].payload["candidates"]), 1)
        self.assertFalse(result.get("projection_omissions"))
        self.assertTrue(verify_grounding(result, chapters))

    def test_missing_duplicate_and_unknown_positions_do_not_become_facts(self):
        for transform in (
            lambda rows: rows[:-1],
            lambda rows: rows + [copy.deepcopy(rows[0])],
            lambda rows: [dict(rows[0], candidate_position=999)],
        ):
            with self.subTest(transform=transform):
                chapters, memory = self.setup_memory()
                p = Grounded(
                    lambda rows, n, transform=transform: {"decisions": transform(rows)}
                )
                result = ground(memory, chapters, 1, p, [])
                self.assertTrue(result.get("projection_omissions"))
                self.assertTrue(retryable_chapters(result))
                self.assertTrue(verify_grounding(result, chapters))

    def test_absent_plan_retains_gap_but_is_not_retried_as_transport_failure(self):
        chapters, memory = self.setup_memory()
        p = Grounded(
            lambda rows, n: {
                "decisions": [
                    {
                        "candidate_position": r["candidate_position"],
                        "outcome": "absent",
                        "support": [],
                        "reason": "本章没有写出",
                    }
                    for r in rows
                ]
            }
        )
        result = ground(memory, chapters, 1, p, [])
        self.assertEqual(retryable_chapters(result), [])
        self.assertTrue(result["projection_content_gaps"]["1"])
        self.assertTrue(
            all(r["kind"] == "prose_excerpt" for r in result["items"].values())
        )

    def test_service_failure_keeps_excerpts_and_pending_work(self):
        chapters, memory = self.setup_memory()
        p = Grounded(lambda rows, n: RuntimeError("offline"))
        result = ground(memory, chapters, 1, p, [])
        self.assertEqual(result["items"], memory["items"])
        self.assertEqual(retryable_chapters(result), [1])

    def test_false_negative_is_reconsidered_at_final_pass_with_history_retained(self):
        chapters, memory = self.setup_memory()
        p = Grounded(
            lambda rows, n: {
                "decisions": [
                    {
                        "candidate_position": r["candidate_position"],
                        "outcome": "absent",
                        "support": [],
                        "reason": "模型第一次漏读",
                    }
                    for r in rows
                ]
            }
        )
        memory = ground(memory, chapters, 1, p, [])
        self.assertTrue(memory["projection_content_gaps"])
        repaired = MemoryEngine(Grounded()).repair_structured_memory(
            memory, chapters, []
        )
        self.assertFalse(repaired.get("projection_omissions"))
        self.assertFalse(repaired.get("projection_content_gaps"))
        self.assertTrue(repaired["projection_grounding"]["1"]["decision_revisions"])
        self.assertTrue(verify_grounding(repaired, chapters))

    def test_restore_rejects_quote_candidate_hash_or_record_tampering(self):
        chapters, memory = self.setup_memory()
        result = ground(memory, chapters, 1, Grounded(), [])
        for change in ("quote", "source_hash", "claim", "candidate"):
            with self.subTest(change=change):
                bad = copy.deepcopy(result)
                journal = bad["projection_grounding"]["1"]
                entry = next(iter(journal["decisions"].values()))
                if change == "quote":
                    entry["support"][0]["quote"] = "编造"
                elif change == "source_hash":
                    journal["chapter_sha256"] = "wrong"
                elif change == "claim":
                    bad["items"][entry["memory_id"]]["claim"] = "篡改"
                else:
                    entry["candidate_position"] = 999
                with self.assertRaises(ContractError):
                    verify_grounding(bad, chapters)

    def test_delayed_backfill_never_overwrites_later_current_value(self):
        chapters, memory = self.setup_memory()
        s = prepare(empty(), proposal(), 1)["candidate_state"]
        change = {"type": "transition", "fact_id": "location", "to_value": "楼上"}
        second = prepare(s, proposal([beat("up", "甲到了楼上。", [change])], 2), 2)[
            "commit"
        ]
        chapters.append(chapter("甲上楼，信放在楼上的桌子上。", 2, second))
        memory = project_memory(memory, chapters, 2, [])
        memory = ground(memory, chapters, 2, Grounded(), [])
        newest = copy.deepcopy(
            next(r for r in memory["items"].values() if r["kind"] == "state")
        )
        result = ground(memory, chapters, 1, Grounded(), [])
        self.assertEqual(result["items"][newest["id"]], newest)
        self.assertTrue(verify_grounding(result, chapters))
        self.assertTrue(result["history"])

    def test_real_d_first_chapter_fixture_has_actual_source_binding(self):
        book = json.loads(
            (
                ROOT / "runs/event_first_30000_20261024_d_resume/final_state.json"
            ).read_text(encoding="utf-8")
        )
        chapters = book["chapters"][:1]
        before = project_memory(MemoryEngine.empty(), chapters, 1, [])
        result = ground(before, chapters, 1, Grounded(), [])
        self.assertTrue(verify_grounding(result, chapters))
        self.assertFalse(result.get("projection_omissions"))
        # A fake semantic matcher validates engineering only, not actual meaning.

    def test_missing_journal_cannot_hide_unprojected_rows(self):
        chapters, memory = self.setup_memory()
        memory["projection_omissions"] = {}
        with self.assertRaises(ContractError):
            verify_grounding(memory, chapters)
        result = ground(
            project_memory(MemoryEngine.empty(), chapters, 1, []),
            chapters,
            1,
            Grounded(),
            [],
        )
        result["projection_grounding"]["1"]["decisions"] = {}
        with self.assertRaises(ContractError):
            verify_grounding(result, chapters)

    def test_final_bounded_retry_reuses_layers_without_transaction_collision(self):
        def behavior(rows, attempt):
            if attempt <= 2:
                rows[0]["support"][0]["quote"] = "不在正文中的引文"
            return {"decisions": rows}

        p = Grounded(behavior)
        engine = MemoryEngine(p)
        chapters = [chapter()]
        memory, _ = engine.advance(MemoryEngine.empty(), chapters, 1, [])
        self.assertEqual(retryable_chapters(memory), [1])
        repaired = engine.repair_structured_memory(memory, chapters, [])
        self.assertEqual(retryable_chapters(repaired), [])
        self.assertTrue(verify_grounding(repaired, chapters))
        self.assertEqual(p.ground_calls, 3)

    def test_same_chapter_late_early_beat_repair_preserves_final_state(self):
        packet = prepare(
            empty(),
            proposal(
                [
                    beat("early", "甲开始在门外。", [fact()]),
                    beat(
                        "late",
                        "甲最后到门内。",
                        [
                            {
                                "type": "transition",
                                "fact_id": "location",
                                "to_value": "门内",
                            }
                        ],
                    ),
                ]
            ),
            1,
        )
        chapters = [
            chapter("甲起初站在门外。\n\n甲现在走到了门内。", commit=packet["commit"])
        ]
        memory = project_memory(MemoryEngine.empty(), chapters, 1, [])

        def behavior(rows, attempt):
            for row in rows:
                position = row["candidate_position"]
                index = 1 if position <= 2 else 2
                row["support"] = [
                    {
                        "evidence_position": index,
                        "quote": (
                            "甲起初站在门外。" if index == 1 else "甲现在走到了门内。"
                        ),
                    }
                ]
                if position == 2 and attempt <= 2:
                    row["support"][0]["quote"] = "错误引文"
            return {"decisions": list(reversed(rows))}

        result = ground(memory, chapters, 1, Grounded(behavior), [])
        newest = copy.deepcopy(
            next(i for i in result["items"].values() if i["kind"] == "state")
        )
        fixed = ground(result, chapters, 1, Grounded(), [])
        self.assertEqual(fixed["items"][newest["id"]], newest)
        self.assertIn("门内", newest["claim"])
        self.assertTrue(verify_grounding(fixed, chapters))

    def test_recall_reserves_latest_relevant_record_and_reports_source_order(self):
        memory = MemoryEngine.empty()
        for n in range(12):
            identifier = f"old{n}"
            memory["items"][identifier] = {
                "id": identifier,
                "subject": "许闻",
                "attribute": f"earlier_{n}",
                "claim": "许闻卷宗核查最终处置安排仍在准备中。" * 12,
                "kind": "state",
                "status": "active",
                "tier": "recent",
                "revision": 1,
                "sources": [{"chapter_number": 1, "evidence_id": "e0001"}],
            }
        memory["items"]["final"] = {
            "id": "final",
            "subject": "许闻",
            "attribute": "final_result",
            "claim": "核查结项，调离岗位。",
            "kind": "state",
            "status": "active",
            "tier": "long",
            "revision": 1,
            "sources": [{"chapter_number": 16, "evidence_id": "e0001"}],
        }
        selected = recall_selection(
            memory, "许闻卷宗核查最终处置是什么？", max_bytes=2500
        )
        self.assertIn("final", selected["selected_ids"])
        latest = next(i for i in selected["items"] if i["id"] == "final")
        self.assertEqual(latest["recorded_through_chapter"], 16)
        self.assertEqual(latest["source_chapters"], [16])

    def test_launcher_exports_grounded_memory_and_next_context_reads_it(self):
        from tools.testing.archived_plan_fixture import compile_archived_plan

        import write_novel as cli
        from memory_runtime.writing import WritingSession, load_resume

        prose = "甲把来信拿进屋内，登记后放上桌面。"
        p = Grounded()
        p.writer = lambda payload: {
            "new_stage_text" if "stage_task" in payload else "text": prose
        }
        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as temp:
            from memory_runtime.length_control import han_count

            output = Path(temp) / "run"
            config = dict(event_config(1), target_han_chars=han_count(prose))
            with (
                patch.object(cli, "read_secret", return_value="offline"),
                patch.object(cli, "ChatCompletionProvider", return_value=p),
                patch(
                    "memory_runtime.reference_choices.compile_plan",
                    side_effect=compile_archived_plan,
                ),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                result = cli.launch(config, output)
            self.assertTrue(result["draft_completed"])
            self.assertTrue(result["memory_projection_complete"])
            self.assertEqual(result["structured_memory_pending_chapters"], [])
            plan = cli.validate_config(config)
            book = load_resume(result["resume_checkpoint"], plan)
            session = WritingSession(Path(temp) / "next", p, plan, book=book)
            context = session.context("继续追踪来信", "甲 来信 位置")
            self.assertTrue(
                any("拿进屋内" in r["value"] for r in context["retrieved_memory"])
            )
            self.assertTrue(
                any(r["kind"] == "state" for r in book["memory"]["items"].values())
            )


if __name__ == "__main__":
    unittest.main()
