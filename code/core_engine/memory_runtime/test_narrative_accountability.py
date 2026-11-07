"""Whole missing optional designs cannot bypass accountability or recovery."""

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inf_writer.domain import canonical, digest
from inf_writer.models import ModelReply

from memory_runtime.narrative_planning import (
    context,
    normalize,
    pending_planning_jobs,
    publish,
    thread_report,
    verify_ledger,
)
from memory_runtime.test_event_first import ROOT, EventLocal, cli, event_config
from memory_runtime.writing import WritingSession, load_resume


def repair_reply(payload):
    required = set(payload["required_thread_ids"])
    return {
        "threads": [
            {
                "topic": r["topic"],
                "question": r["question"],
                "acceptance": r["acceptance"],
                "importance": r["importance"],
                "next_step": r["next_step"],
                "action": "advance",
                "reason": "基于当前保存章节补登记",
            }
            for r in payload["known_threads"]
            if r["thread_id"] in required
        ],
        "thread_review_note": "已检查保存正文，无新增未登记事项",
    }


class AccountabilityTests(unittest.TestCase):
    def test_missing_whole_design_records_discovery_gap_even_without_old_threads(self):
        text = "甲发现一份没有署名的来信。"
        c = {"number": 1, "text": text, "sha256": digest(text)}
        book = {"chapters": [c]}
        publish(book, c, {})
        row = book["narrative_planning"]["chapters"]["1"]["thread_accountability"]
        self.assertEqual(row["design_status"], "MISSING")
        self.assertTrue(pending_planning_jobs(book)[0]["discovery_review_required"])
        self.assertFalse(thread_report(book)["important_threads_accounted_for"])
        self.assertEqual(thread_report(book)["pending_planning_chapters"], [1])
        self.assertTrue(context(book, 2)["pending_planning_repairs"])
        verify_ledger(book)

    def test_empty_or_invalid_design_does_not_mean_no_threads(self):
        for raw in (None, [], {"threads": "not-an-array"}, {"threads": []}):
            with self.subTest(raw=raw):
                text = "甲整理了来信。"
                c = {"number": 1, "text": text, "sha256": digest(text)}
                book = {"chapters": [c]}
                design, _ = normalize(raw, 0)
                c["narrative_plan"] = design
                publish(book, c, design)
                self.assertTrue(pending_planning_jobs(book))
        design, _ = normalize(
            {
                "threads": [],
                "thread_review_note": "本章只有日常整理，没有引入待回应事项",
            },
            0,
        )
        c["narrative_plan"] = design
        book = {"chapters": [c]}
        publish(book, c, design)
        self.assertFalse(pending_planning_jobs(book))

    def stopped_book(self):
        folder = ROOT / "runs/event_first_30000_20261028_threads_a"
        path = sorted((folder / "working").glob("checkpoint_*.json"))[-1]
        return folder, path, json.loads(path.read_text(encoding="utf-8"))["book"]

    def test_actual_chapters_seven_eight_backfill_and_restore_without_rewriting(self):
        source, path, book = self.stopped_book()
        raw = path.read_bytes()
        original = copy.deepcopy(book)

        class Gateway:
            def complete(self, r):
                return ModelReply(canonical(repair_reply(r.payload)), 1, 1, 0)

        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            plan = cli.validate_config(
                json.loads((source / "config.json").read_text(encoding="utf-8"))
            )
            session = WritingSession(
                Path(folder) / "working", Gateway(), plan, book=book
            )
            self.assertEqual(
                sorted(j["chapter"] for j in pending_planning_jobs(session.book)),
                [1, 7, 8],
            )
            for n in (7, 8):
                coverage = session.book["narrative_planning"]["chapters"][str(n)][
                    "thread_accountability"
                ]
                self.assertTrue(coverage["missing_thread_ids"])
                self.assertEqual(coverage["design_status"], "MISSING")
            session.attempt_narrative_repair(final=True)
            self.assertFalse(pending_planning_jobs(session.book))
            self.assertEqual(session.book["chapters"], original["chapters"])
            self.assertEqual(session.book["writing_state"], original["writing_state"])
            self.assertEqual(load_resume(session.latest_checkpoint, plan), session.book)
            verify_ledger(session.book)
        self.assertEqual(path.read_bytes(), raw)

    def test_backfill_does_not_overwrite_newer_thread_definitions(self):
        source, path, book = self.stopped_book()
        old = copy.deepcopy(book["narrative_planning"]["threads"])

        class Gateway:
            def complete(self, r):
                value = repair_reply(r.payload)
                # Backfill chapter 1 with an existing name, not a new future fact.
                r0 = r.payload["known_threads"][0]
                value["threads"] = [
                    {
                        "topic": r0["topic"],
                        "question": "较早的问题表述",
                        "acceptance": "较早的回应标准",
                        "action": "advance",
                        "reason": "历史补录",
                        "next_step": "较早下一步",
                    }
                ]
                return ModelReply(canonical(value), 1, 1, 0)

        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            plan = cli.validate_config(
                json.loads((source / "config.json").read_text(encoding="utf-8"))
            )
            session = WritingSession(
                Path(folder) / "working", Gateway(), plan, book=book
            )
            session.attempt_narrative_repair()
            first = next(k for k in old if old[k].get("importance") == "major")
            for key in ("question", "acceptance", "next_step", "last_planned_chapter"):
                self.assertEqual(
                    session.book["narrative_planning"]["threads"][first][key],
                    old[first][key],
                )

    def test_repair_outage_persists_and_same_boundary_does_not_repeat(self):
        source, path, book = self.stopped_book()
        calls = []

        class Gateway:
            def complete(self, r):
                calls.append(r)
                raise RuntimeError("offline outage")

        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            plan = cli.validate_config(
                json.loads((source / "config.json").read_text(encoding="utf-8"))
            )
            session = WritingSession(
                Path(folder) / "working", Gateway(), plan, book=book
            )
            session.attempt_narrative_repair()
            session.attempt_narrative_repair()
            # Different queued items may be tried, but never charge the same item twice.
            self.assertEqual(len({r.payload["chapter"] for r in calls}), len(calls))
            self.assertTrue(pending_planning_jobs(session.book))
            self.assertEqual(load_resume(session.latest_checkpoint, plan), session.book)

    def test_real_launcher_omitted_design_is_repaired_after_prose_save(self):
        self.launch(fail=False)

    def test_real_launcher_repair_failure_keeps_chapters_and_feedback(self):
        self.launch(fail=True)

    def launch(self, fail):
        class Provider(EventLocal):
            def complete(self, r):
                p = r.payload
                if p.get("task") == "repair_narrative_accountability":
                    self.requests.append(copy.deepcopy(r))
                    if fail:
                        raise RuntimeError("offline outage")
                    return ModelReply(canonical(repair_reply(p)), 1, 1, 0)
                if r.role == "planner":
                    self.requests.append(copy.deepcopy(r))
                    n = p["chapter_number"]
                    self.number = n
                    value = {
                        "number": n,
                        "title": "来信",
                        "brief": "继续处理来信",
                        "future_updates": [],
                        "scenes": [
                            {
                                "purpose": "处理来信",
                                "participants": ["甲"],
                                "beats": [
                                    {
                                        "statement": "甲保存了来信。",
                                        "assertion_scope": "performed_action",
                                        "requires": [],
                                        "changes": [],
                                    }
                                ],
                            }
                        ],
                    }
                    if n == 1:
                        value["narrative_plan"] = {
                            "threads": [
                                {
                                    "topic": "来信身份",
                                    "importance": "major",
                                    "question": "谁寄来了信",
                                    "acceptance": "正文展示来源或明确为何不能获知",
                                    "action": "advance",
                                    "reason": "登记问题",
                                }
                            ]
                        }
                    return ModelReply(canonical(value), 1, 1, 0)
                return super().complete(r)

        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            provider = Provider()
            output = Path(folder) / "book"
            cfg = dict(event_config(3, review=False), closure_enabled=False)
            with (
                patch.object(cli, "read_secret", return_value="offline"),
                patch.object(cli, "ChatCompletionProvider", return_value=provider),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                result = cli.launch(cfg, output)
            state = json.loads(
                (output / "final_state.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(state["chapters"]), 3)
            self.assertTrue(result["generation_completed"])
            self.assertEqual(
                load_resume(
                    Path(result["resume_checkpoint"]), cli.validate_config(cfg)
                ),
                state,
            )
            for n in (2, 3):
                self.assertIn(str(n), state["narrative_planning"]["chapters"])
            self.assertNotIn("narrative_plan", state["chapters"][1])
            report = json.loads((output / "问题清单.json").read_text(encoding="utf-8"))
            if fail:
                self.assertEqual(report["pending_narrative_planning_chapters"], [2, 3])
                last_plan = next(
                    r
                    for r in provider.requests
                    if r.role == "planner" and r.payload.get("chapter_number") == 3
                )
                self.assertTrue(
                    last_plan.payload["narrative_continuity"][
                        "pending_planning_repairs"
                    ]
                )
                self.assertFalse(result["important_threads_accounted_for"])
            else:
                self.assertEqual(report["pending_narrative_planning_chapters"], [])
                self.assertIn(
                    "recovered_design", state["narrative_planning"]["chapters"]["2"]
                )


if __name__ == "__main__":
    unittest.main()
