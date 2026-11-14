"""Reconcile sourced open endings before extending already finished prose."""

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import write_novel as cli
from memory_runtime.narrative_planning import (
    pending_planning_jobs,
    thread_report,
    verify_ledger,
)
from memory_runtime.narrative_repair import queue_ending_intent_review
from memory_runtime.story_closure import StoryClosure
from memory_runtime.test_event_first import ROOT
from memory_runtime.writing import WritingSession, load_resume
from tome_writer.domain import canonical
from tome_writer.models import ModelReply
from user_runtime import run_draft_trial

SOURCE = ROOT / "runs/event_first_30000_20261028_full_after_transfer_resume_a"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


class MetadataOnly:
    def __init__(self, book, invalid_target=False):
        self.book = book
        self.requests = []
        self.invalid_target = invalid_target

    def complete(self, r):
        self.requests.append(copy.deepcopy(r))
        p = r.payload
        if r.role == "narrative_repair":
            needed = set(p["required_thread_ids"])
            text = "".join(part["text"] for part in p["saved_prose_parts"])
            rows = [
                {
                    "topic": row["topic"],
                    "question": row["question"],
                    "acceptance": row["acceptance"],
                    "importance": row["importance"],
                    "action": "leave_open",
                    "reason": "正文已交代不能确认与停止单方追查的后果",
                    "resolution_type": "open_ending",
                    "resolution_chapter": p["chapter"],
                    "resolution_quote": text,
                }
                for row in p["known_threads"]
                if row["thread_id"] in needed
            ]
            if self.invalid_target:
                for row in rows:
                    row.update(action="advance", target_chapter=p["chapter_limit"] + 1)
            return ModelReply(
                canonical(
                    {
                        "threads": rows,
                        "thread_review_note": "只核对已保存正文的收束意图",
                    }
                ),
                1,
                1,
                0,
            )
        if r.role in ("closure_reviewer", "closure_repair"):
            source = next(
                s
                for s in reversed(p["evidence_sources"])
                if s["chapter"] == p["chapter"]
            )
            value = {
                "thread_updates": [
                    {
                        "thread_id": t["thread_id"],
                        "status": "open_ending",
                        "reason": "模拟复核确认正文的开放式收束",
                        "evidence": [{"source_choice": source["source_choice"]}],
                    }
                    for t in p["narrative_threads"]["threads"]
                ]
            }
            if not p.get("thread_review_only"):
                value.update(
                    obligations=[
                        {
                            "id": o["id"],
                            "status": "resolved",
                            "reason": "模拟核心终局已发生",
                            "evidence": [{"source_choice": source["source_choice"]}],
                        }
                        for o in p.get("obligations", [])
                    ],
                    mainline_ended=True,
                    new_obligations=[],
                )
            return ModelReply(canonical(value), 1, 1, 0)
        raise AssertionError(
            "No prose writing or unrelated model call allowed: " + r.role
        )


class EndingIntentTests(unittest.TestCase):
    def test_actual_three_conflicts_are_queued_without_overriding_review_or_text(self):
        book = read(SOURCE / "final_state.json")
        before = copy.deepcopy(book)
        queue_ending_intent_review(book)
        job = pending_planning_jobs(book)[0]
        self.assertEqual(job["chapter"], 18)
        self.assertEqual(len(job["ending_intent_thread_ids"]), 3)
        self.assertEqual(book["chapters"], before["chapters"])
        self.assertEqual(book["writing_state"], before["writing_state"])
        self.assertEqual(
            book["narrative_planning"]["threads"],
            before["narrative_planning"]["threads"],
        )
        verify_ledger(book)

    def test_reconciled_intent_requires_fresh_review_and_reuses_same_definition_result(
        self,
    ):
        book = read(SOURCE / "final_state.json")
        provider = MetadataOnly(book)
        plan = cli.validate_config(read(SOURCE / "config.json"))
        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            session = WritingSession(
                Path(folder) / "working", provider, plan, book=book
            )
            session.attempt_narrative_repair(final=True)
            self.assertFalse(pending_planning_jobs(session.book))
            self.assertFalse(thread_report(session.book)["current_review_complete"])
            closure = StoryClosure(session)
            closure.initialize()
            closure.retry_thread_updates(final=True)
            self.assertTrue(closure.passed())
            self.assertTrue(
                thread_report(session.book)["important_threads_accounted_for"]
            )
            count = len(provider.requests)
            closure.retry_thread_updates(final=True)
            self.assertEqual(len(provider.requests), count)
            self.assertEqual(session.book["chapters"], book["chapters"])
            self.assertEqual(load_resume(session.latest_checkpoint, plan), session.book)

    def test_beyond_limit_target_is_not_accepted_as_completed_metadata(self):
        book = read(SOURCE / "final_state.json")
        provider = MetadataOnly(book, invalid_target=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            session = WritingSession(
                Path(folder) / "working",
                provider,
                cli.validate_config(read(SOURCE / "config.json")),
                book=book,
            )
            session.attempt_narrative_repair(final=True)
            self.assertTrue(pending_planning_jobs(session.book))
            self.assertIn(
                "chapter horizon", pending_planning_jobs(session.book)[0]["last_error"]
            )
            self.assertFalse(
                thread_report(session.book)["important_threads_accounted_for"]
            )

    def test_without_sourced_open_ending_review_does_not_invent_intent_repair(self):
        book = read(SOURCE / "final_state.json")
        for row in book["narrative_planning"]["threads"].values():
            row["prose_assessment"].update(
                status="pending", candidate_disposition="pending", evidence=[]
            )
        old = copy.deepcopy(book)
        queue_ending_intent_review(book)
        self.assertEqual(book, old)

    def test_completed_chapter16_repairs_metadata_before_any_chapter17_writer_call(
        self,
    ):
        book = next(
            read(p)["book"]
            for p in sorted(
                (SOURCE / "working").glob("checkpoint_*.json"), reverse=True
            )
            if len(read(p)["book"]["chapters"]) == 16
            and not read(p)["book"].get("prepared_events")
        )
        provider = MetadataOnly(book)
        plan = cli.validate_config(read(SOURCE / "config.json"))
        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            # Isolate the continuation decision; memory, state recovery and
            # historical closure replay are covered in their own regressions.
            with (
                patch("user_runtime.StoryClosure.initialize"),
                patch.object(WritingSession, "attempt_memory"),
                patch.object(WritingSession, "attempt_state_repair"),
                patch.object(WritingSession, "finish_structured_memory"),
                patch.object(WritingSession, "finish_memory_organization"),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                result = run_draft_trial(
                    Path(folder) / "book", provider, plan, resume_book=book
                )
            self.assertEqual(result["chapters"], 16)
            self.assertTrue(result["narrative_closure_model_passed"])
            self.assertIsNone(
                result["stop_reason"], str([r.role for r in provider.requests])
            )
            self.assertFalse(any(r.role == "writer" for r in provider.requests))

    def test_closure_and_repair_views_follow_book_replacement_without_detached_state(
        self,
    ):
        book = read(SOURCE / "final_state.json")
        plan = cli.validate_config(read(SOURCE / "config.json"))
        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            session = WritingSession(
                Path(folder) / "working", MetadataOnly(book), plan, book=book
            )
            closure = StoryClosure(session)
            old_state = closure.state
            session.book = copy.deepcopy(session.book)
            closure.state["coverage"]["17"] = "replacement-only"
            closure.repairs.jobs["new-job"] = {"status": "PENDING"}
            closure.repairs.history.append({"reason": "new book"})
            self.assertIs(closure.state, session.book["story_closure"])
            self.assertNotEqual(old_state["coverage"].get("17"), "replacement-only")
            self.assertNotIn("new-job", old_state["repair_jobs"])
            self.assertEqual(
                session.book["story_closure"]["repair_history"][-1]["reason"],
                "new book",
            )
