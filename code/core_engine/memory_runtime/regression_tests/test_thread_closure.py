"""Persistent narrative commitments use the existing planner and ending path."""

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from memory_runtime.narrative_planning import (
    apply_thread_review,
    context,
    normalize,
    publish,
    thread_report,
    thread_review_input,
    thread_setup_sources,
    verify_ledger,
)
from memory_runtime.story_closure import StoryClosure, evidence_sources
from memory_runtime.test_event_first import ROOT, EventLocal, cli, event_config
from memory_runtime.writing import load_resume
from tome_writer.domain import ContractError, canonical, digest
from tome_writer.models import ModelReply


def chapter(n, text, threads=()):
    design, _ = normalize({"threads": list(threads)}, 1)
    return {"number": n, "text": text, "sha256": digest(text), "narrative_plan": design}


def book_with_threads():
    book = {"chapters": []}
    c = chapter(
        1,
        "甲发现三种笔迹，并决定核对。",
        [
            {
                "topic": "三种笔迹",
                "importance": "major",
                "question": "分别是谁写的",
                "acceptance": "正文展示三份签名的关系与依据",
                "next_step": "核对签名",
            },
            {
                "topic": "丢失的报告",
                "importance": "major",
                "question": "报告去向及能否找回",
                "acceptance": "明确报告去向，或说明无法找回的原因与选择",
                "next_step": "查明去向",
            },
            {"topic": "窗边的花", "importance": "minor", "next_step": "背景细节"},
        ],
    )
    book["chapters"].append(c)
    publish(book, c, c["narrative_plan"])
    c = chapter(
        2,
        "甲确认三份签名由不同的人写成。报告已烧毁，无法补回，甲将这个缺口写入记录。",
        [
            {"topic": "三种笔迹", "action": "advance", "reason": "正文已推进签名比对"},
            {"topic": "丢失的报告", "action": "advance", "reason": "正文说明报告已毁"},
        ],
    )
    book["chapters"].append(c)
    publish(book, c, c["narrative_plan"])
    return book


def controller(book, gateway=None):
    book["story_closure"] = {
        "status": "MODEL_PASSED",
        "obligations": [
            {
                "id": "O1",
                "question": "是否公开",
                "acceptance": "公开结果",
                "status": "resolved",
                "evidence": [],
                "blocking": True,
            }
        ],
        "coverage": {str(c["number"]): digest(c["text"]) for c in book["chapters"]},
        "failures": [],
        "checks": [
            {
                "chapter": book["chapters"][-1]["number"],
                "final_check": True,
                "ending_closed": True,
                "update_complete": True,
                "chapter_sha256": digest(book["chapters"][-1]["text"]),
            }
        ],
    }
    return StoryClosure(
        SimpleNamespace(
            book=book,
            gateway=gateway,
            _save=lambda *a: None,
            plan={
                "goal": "公开记录",
                "constraints": [],
                "chapters": 2,
                "closure_enabled": True,
            },
        )
    )


def decisions(book, sources, statuses):
    return {
        "thread_updates": [
            {
                "thread_id": r["thread_id"],
                "status": statuses.get(r["topic"], "pending"),
                "reason": "依据实际正文判断",
                "evidence": [{"source_choice": 1}]
                if statuses.get(r["topic"]) in ("resolved", "ruled_out", "open_ending")
                else [],
            }
            for r in thread_review_input(book)["threads"]
        ]
    }


class ThreadClosureTests(unittest.TestCase):
    def test_existing_open_threads_prevent_silent_combined_pass(self):
        book = book_with_threads()
        c = controller(book)
        self.assertFalse(c.passed())
        self.assertTrue(c.state["basic_mainline_model_passed"])
        self.assertEqual(len(thread_report(book)["unhandled_important_thread_ids"]), 2)

    def test_repeating_next_step_is_not_progress_and_missing_decisions_are_visible(
        self,
    ):
        book = book_with_threads()
        book["chapters"][1]["narrative_plan"] = {}
        publish(book, book["chapters"][1], {})
        view = context(book, 3)
        self.assertEqual(len(view["required_thread_decisions"]), 2)
        self.assertEqual(
            len(view["previous_planning_coverage"]["missing_thread_ids"]), 2
        )
        c = chapter(
            3,
            "甲仍在等候。",
            [
                {
                    "topic": "三种笔迹",
                    "next_step": "以后核对",
                    "action": "defer",
                    "reason": "等原件",
                    "target_chapter": 3,
                }
            ],
        )
        book["chapters"].append(c)
        publish(book, c, c["narrative_plan"])
        row = next(
            r
            for r in book["narrative_planning"]["threads"].values()
            if r["topic"] == "三种笔迹"
        )
        self.assertNotIn("last_progress_chapter", row)
        coverage = book["narrative_planning"]["chapters"]["3"]["thread_accountability"]
        self.assertTrue(coverage["missing_thread_ids"])
        self.assertTrue(coverage["incomplete_decision_thread_ids"])

    def test_plan_alone_never_settles_thread_or_demotes_existing_importance(self):
        book = book_with_threads()
        c = chapter(
            3,
            "甲继续等候。",
            [
                {
                    "topic": "三种笔迹",
                    "importance": "minor",
                    "action": "resolve",
                    "reason": "准备结账",
                    "next_step": "本章查清",
                }
            ],
        )
        book["chapters"].append(c)
        publish(book, c, c["narrative_plan"])
        row = next(
            r
            for r in book["narrative_planning"]["threads"].values()
            if r["topic"] == "三种笔迹"
        )
        self.assertEqual(row["importance"], "major")
        self.assertNotIn("prose_assessment", row)

    def test_planner_can_update_only_bound_saved_outcome(self):
        book = book_with_threads()
        quote = book["chapters"][1]["text"]
        c = chapter(
            3,
            "甲保留记录。",
            [
                {
                    "topic": "丢失的报告",
                    "action": "leave_open",
                    "reason": "原件已毁，缺口已告知",
                    "resolution_type": "open_ending",
                    "resolution_chapter": 2,
                    "resolution_quote": quote,
                }
            ],
        )
        book["chapters"].append(c)
        publish(book, c, c["narrative_plan"])
        verify_ledger(book)
        row = next(
            r
            for r in book["narrative_planning"]["threads"].values()
            if r["topic"] == "丢失的报告"
        )
        self.assertEqual(row["prose_assessment"]["status"], "open_ending")
        self.assertEqual(row["last_progress_chapter"], 2)
        row["prose_assessment"]["evidence"][0]["quote"] = "不存在的句子"
        with self.assertRaises(ContractError):
            verify_ledger(book)

    def test_valid_open_ending_counts_without_forcing_all_minor_threads(self):
        book = book_with_threads()
        c = controller(book)
        book["narrative_planning"]["threads"][digest("丢失的报告")[:24]][
            "planning_decision"
        ] = {"action": "leave_open", "reason": "报告已毁，明确交代不可恢复"}
        sources = evidence_sources(
            {2: book["chapters"][1]["text"]}, 2, 0, len(book["chapters"][1]["text"]), []
        )
        value = decisions(
            book, sources, {"三种笔迹": "resolved", "丢失的报告": "open_ending"}
        )
        self.assertEqual(apply_thread_review(book, value, sources, 2), [])
        self.assertTrue(c.passed())
        self.assertTrue(thread_report(book)["important_threads_accounted_for"])
        verify_ledger(book)

    def test_bad_missing_and_boolean_sources_do_not_erase_valid_peers(self):
        for bad in ("missing", "duplicate", "boolean", "fabricated"):
            with self.subTest(bad=bad):
                book = book_with_threads()
                sources = evidence_sources(
                    {2: book["chapters"][1]["text"]}, 2, 0, 1000, []
                )
                value = decisions(
                    book, sources, {"三种笔迹": "resolved", "丢失的报告": "resolved"}
                )
                target = next(
                    r
                    for r in value["thread_updates"]
                    if r["thread_id"] == digest("丢失的报告")[:24]
                )
                if bad == "missing":
                    value["thread_updates"].remove(target)
                elif bad == "duplicate":
                    value["thread_updates"].append(copy.deepcopy(target))
                else:
                    target["evidence"] = [
                        {"source_choice": True if bad == "boolean" else 999}
                    ]
                self.assertTrue(apply_thread_review(book, value, sources, 2))
                rows = book["narrative_planning"]["threads"]
                self.assertEqual(
                    rows[digest("三种笔迹")[:24]]["prose_assessment"]["status"],
                    "resolved",
                )
                self.assertFalse(controller(book).passed())

    def test_new_text_or_new_definition_invalidates_prior_final_disposition(self):
        book = book_with_threads()
        sources = evidence_sources({2: book["chapters"][1]["text"]}, 2, 0, 1000, [])
        apply_thread_review(
            book,
            decisions(
                book, sources, {"三种笔迹": "resolved", "丢失的报告": "ruled_out"}
            ),
            sources,
            2,
        )
        self.assertTrue(thread_report(book)["current_review_complete"])
        book["narrative_planning"]["threads"][digest("三种笔迹")[:24]]["question"] = (
            "是否同一人伪造"
        )
        self.assertFalse(thread_report(book)["current_review_complete"])

    def test_old_review_policy_cannot_certify_new_ending_on_resume(self):
        book = book_with_threads()
        sources = evidence_sources({2: book["chapters"][1]["text"]}, 2, 0, 1000, [])
        apply_thread_review(
            book,
            decisions(
                book, sources, {"三种笔迹": "resolved", "丢失的报告": "ruled_out"}
            ),
            sources,
            2,
        )
        rows = book["narrative_planning"]["threads"]
        old_hash = digest(
            canonical(
                {
                    k: {
                        f: r.get(f)
                        for f in ("topic", "question", "acceptance", "importance")
                    }
                    for k, r in rows.items()
                }
            )
        )
        book["narrative_planning"]["latest_thread_review"]["definition_sha256"] = (
            old_hash
        )
        self.assertFalse(controller(book).passed())
        self.assertFalse(thread_report(book)["current_review_complete"])
        book["chapters"][1]["text"] += "后来证词被推翻。"
        self.assertFalse(thread_report(book)["current_review_complete"])

    def test_untransmitted_important_threads_never_count_as_handled(self):
        book = book_with_threads()
        self.assertTrue(thread_review_input(book, limit=1)["omitted_thread_ids"])
        self.assertFalse(thread_report(book)["important_threads_accounted_for"])

    def test_bounded_review_rotates_and_accumulates_coverage_without_losing_threads(
        self,
    ):
        book = {"chapters": []}
        c = chapter(
            1,
            "已保存的实际回应。",
            [
                {
                    "topic": f"待回应的问题{i}",
                    "importance": "major",
                    "question": f"问题{i}",
                    "acceptance": "正文展示回答",
                    "next_step": "查明",
                }
                for i in range(100)
            ],
        )
        book["chapters"].append(c)
        publish(book, c, c["narrative_plan"])
        sources = evidence_sources({1: c["text"]}, 1, 0, len(c["text"]), [])
        for _ in range(8):
            selected = thread_review_input(book)
            value = {
                "thread_updates": [
                    {
                        "thread_id": r["thread_id"],
                        "status": "resolved",
                        "reason": "夹具设定已回应",
                        "evidence": [{"source_choice": 1}],
                    }
                    for r in selected["threads"]
                ]
            }
            apply_thread_review(book, value, sources, 1)
            if thread_report(book)["important_threads_accounted_for"]:
                break
        self.assertEqual(len(book["narrative_planning"]["threads"]), 100)
        self.assertTrue(thread_report(book)["important_threads_accounted_for"])

    def test_real_baseline_preserves_eight_open_threads_and_source_files(self):
        path = ROOT / "runs/event_first_30000_20261027_baseline_a/final_state.json"
        raw = path.read_bytes()
        book = json.loads(raw)
        report = thread_report(book)
        self.assertEqual(report["total"], 8)
        self.assertFalse(report["important_threads_accounted_for"])
        self.assertIn("流程单背面的陌生铅笔问号", [r["topic"] for r in report["items"]])
        self.assertEqual(path.read_bytes(), raw)

    def test_real_baseline_review_includes_original_questions_and_source_identity(self):
        book = json.loads(
            (
                ROOT / "runs/event_first_30000_20261027_baseline_a/final_state.json"
            ).read_text(encoding="utf-8")
        )
        rows = thread_review_input(book)["threads"]
        row = next(r for r in rows if "问号" in r["topic"])
        self.assertTrue(row["original_setup"]["competing_explanations"])
        sources = thread_setup_sources(book)
        matching = [r for r in sources if r["thread_id"] == row["thread_id"]]
        self.assertTrue(all(s["chapter"] == 5 for s in matching))
        self.assertTrue(any("问号" in s["quote"] for s in matching))
        for source in sources:
            text = book["chapters"][source["chapter"] - 1]["text"]
            self.assertEqual(source["quote"], text[source["start"] : source["end"]])
        self.assertLessEqual(
            sum(len(s["quote"]) for s in thread_setup_sources(book, 700)), 700
        )

    def test_partial_answer_cannot_clear_composite_thread(self):
        book = book_with_threads()
        sources = evidence_sources({2: book["chapters"][1]["text"]}, 2, 0, 1000, [])
        value = decisions(
            book, sources, {"三种笔迹": "resolved", "丢失的报告": "ruled_out"}
        )
        next(
            r
            for r in value["thread_updates"]
            if r["thread_id"] == digest("三种笔迹")[:24]
        )["remaining_questions"] = ["第三位书写人仍未回应"]
        apply_thread_review(book, value, sources, 2)
        self.assertFalse(thread_report(book)["important_threads_accounted_for"])
        self.assertEqual(
            book["narrative_planning"]["threads"][digest("三种笔迹")[:24]][
                "prose_assessment"
            ]["status"],
            "pending",
        )

    def test_generic_quitting_cannot_close_unplanned_or_undefined_threads(self):
        book = book_with_threads()
        sources = evidence_sources({2: book["chapters"][1]["text"]}, 2, 0, 1000, [])
        rows = book["narrative_planning"]["threads"]
        rows[digest("三种笔迹")[:24]].pop("acceptance")
        apply_thread_review(
            book,
            decisions(
                book, sources, {"三种笔迹": "resolved", "丢失的报告": "open_ending"}
            ),
            sources,
            2,
        )
        self.assertEqual(
            rows[digest("三种笔迹")[:24]]["prose_assessment"]["status"], "uncertain"
        )
        self.assertEqual(
            rows[digest("丢失的报告")[:24]]["prose_assessment"]["status"], "pending"
        )
        self.assertFalse(thread_report(book)["important_threads_accounted_for"])

    def test_real_launcher_repairs_missing_thread_update_then_exports_and_restores(
        self,
    ):
        self.launch("repair")

    def test_real_launcher_keeps_writing_when_thread_remains_pending(self):
        self.launch("pending")

    def test_real_launcher_keeps_prose_when_thread_repair_service_fails(self):
        self.launch("outage")

    def launch(self, mode):
        class Provider(EventLocal):
            def complete(self, r):
                p = r.payload
                if r.role == "planner":
                    self.requests.append(copy.deepcopy(r))
                    n = p["chapter_number"]
                    self.number = n
                    value = {
                        "number": n,
                        "title": "来信",
                        "brief": "甲处理来信",
                        "future_updates": [],
                        "scenes": [
                            {
                                "purpose": "处理",
                                "participants": ["甲"],
                                "beats": [
                                    {
                                        "statement": "甲公开了来信。",
                                        "assertion_scope": "performed_action",
                                        "requires": [],
                                        "changes": [],
                                    }
                                ],
                            }
                        ],
                        "narrative_plan": {
                            "threads": [
                                {
                                    "topic": "来信身份",
                                    "importance": "major",
                                    "question": "是谁寄信",
                                    "acceptance": "交代无法查明寄件人的原因和人物选择",
                                    "action": "leave_open",
                                    "reason": "夹具设定明确留白",
                                    "next_step": "说明来源",
                                }
                            ]
                        },
                    }
                    return ModelReply(canonical(value), 1, 1, 0)
                if r.role == "closure_planner":
                    self.requests.append(copy.deepcopy(r))
                    return ModelReply(
                        canonical(
                            {
                                "obligations": [
                                    {"question": "是否公开", "acceptance": "正文公开"}
                                ]
                            }
                        ),
                        1,
                        1,
                        0,
                    )
                if r.role in ("closure_reviewer", "closure_repair"):
                    self.requests.append(copy.deepcopy(r))
                    if r.role == "closure_repair" and mode == "outage":
                        raise RuntimeError("offline outage")
                    updates = []
                    if mode == "pending":
                        updates = [
                            {
                                "thread_id": x["thread_id"],
                                "status": "pending",
                                "reason": "身份仍未交代",
                                "evidence": [],
                            }
                            for x in p["narrative_threads"]["threads"]
                        ]
                    elif r.role == "closure_repair":
                        updates = [
                            {
                                "thread_id": x["thread_id"],
                                "status": "open_ending",
                                "reason": "夹具设定：有明确留白依据",
                                "evidence": [
                                    {
                                        "source_choice": p["evidence_sources"][0][
                                            "source_choice"
                                        ]
                                    }
                                ],
                            }
                            for x in p["narrative_threads"]["threads"]
                        ]
                    value = {
                        "obligations": [
                            {
                                "id": x["id"],
                                "status": "resolved",
                                "reason": "夹具主线已公开",
                                "evidence": [
                                    {
                                        "source_choice": p["evidence_sources"][0][
                                            "source_choice"
                                        ]
                                    }
                                ],
                            }
                            for x in p.get("obligations", [])
                        ],
                        "mainline_ended": True,
                        "new_obligations": [],
                        "thread_updates": updates,
                    }
                    return ModelReply(canonical(value), 1, 1, 0)
                return super().complete(r)

        with tempfile.TemporaryDirectory(dir=ROOT / "runs") as folder:
            output = Path(folder) / "book"
            provider = Provider()
            cfg = dict(
                event_config(1, review=False), max_chapters=2, closure_enabled=True
            )
            output_log = io.StringIO()
            with (
                patch.object(cli, "read_secret", return_value="offline"),
                patch.object(cli, "ChatCompletionProvider", return_value=provider),
                contextlib.redirect_stdout(output_log),
            ):
                result = cli.launch(cfg, output)
            state = json.loads(
                (output / "final_state.json").read_text(encoding="utf-8")
            )
            self.assertTrue(result["generation_completed"])
            self.assertTrue((output / "正文.md").is_file())
            self.assertEqual(
                load_resume(
                    Path(result["resume_checkpoint"]), cli.validate_config(cfg)
                ),
                state,
            )
            report = json.loads((output / "问题清单.json").read_text(encoding="utf-8"))
            self.assertEqual(report["story_review_status"], "DISABLED_NOT_CHECKED")
            self.assertIn("narrative_thread_dispositions", report)
            self.assertFalse(any(r.role == "reviewer" for r in provider.requests))
            if mode == "repair":
                self.assertTrue(result["draft_completed"])
                self.assertTrue(result["important_threads_accounted_for"])
                self.assertIn("主线与重要线索处置检查通过", output_log.getvalue())
                self.assertTrue(
                    any(r.payload.get("thread_review_only") for r in provider.requests)
                )
            else:
                self.assertFalse(result["draft_completed"])
                self.assertTrue(result["basic_mainline_model_passed"])
                self.assertIn(
                    "主线已有结果；重要线索处置尚未确认", output_log.getvalue()
                )
                self.assertEqual(result["chapters"], 1 if mode == "outage" else 2)
                if mode == "outage":
                    self.assertEqual(
                        result["stop_reason"], "NARRATIVE_METADATA_PENDING"
                    )
                self.assertFalse(result["important_threads_accounted_for"])


if __name__ == "__main__":
    unittest.main()
