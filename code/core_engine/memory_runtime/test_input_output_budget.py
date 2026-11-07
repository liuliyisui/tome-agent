"""Request-view sizing and output truncation at the real protocol boundary."""

import copy
import io
import json
import unittest
from unittest.mock import patch

import write_novel
from inf_writer.agents import JsonAgent
from inf_writer.chat_provider import ChatCompletionProvider
from inf_writer.domain import canonical, digest
from inf_writer.models import ModelReply, ModelRequest

from memory_runtime.input_budget import fit, select_qualified_state, size


class InputOutputBudgetTests(unittest.TestCase):
    def test_length_adjustment_uses_actual_han_count_and_never_blocks_on_failure(self):
        from memory_runtime.length_control import adjust

        class Better:
            def complete(self, request):
                return ModelReply("甲" * 100, 1, 1, 0)

        class Broken:
            def complete(self, request):
                raise RuntimeError("offline")

        book = {"goal": "小说", "constraints": []}
        original = "甲" * 200
        result, report = adjust(original, 100, book, 1, Better(), [])
        self.assertEqual(len(result), 100)
        self.assertEqual(report["adjustment"], "accepted")
        result, report = adjust(original, 100, book, 1, Broken(), [])
        self.assertEqual(result, original)
        self.assertEqual(report["adjustment"], "kept_original_failure")

    def test_large_unicode_chapters_fit_without_editing_sources_or_reference_indices(
        self,
    ):
        prose = "风雨中的档案。" * 7000
        payload = {
            "recent_chapters": [
                {"number": i, "title": "旧卷", "text": prose, "sha256": digest(prose)}
                for i in (1, 2)
            ],
            "event_plan_state": {
                "records": [{"record_id": "known", "value": "甲仍在门外"}]
            },
            "reference_choices": ["fact_record:known"],
            "reference_choices_by_kind": {"fact_record": [1]},
        }
        original = copy.deepcopy(payload)
        bounded = fit(payload, 24000)
        self.assertLessEqual(size(bounded), 24000)
        self.assertEqual(payload, original)
        self.assertEqual(bounded["event_plan_state"], original["event_plan_state"])
        self.assertEqual(bounded["reference_choices"], original["reference_choices"])
        self.assertTrue(bounded["input_selection"]["stored_sources_unchanged"])
        for chapter in bounded["recent_chapters"]:
            self.assertEqual(chapter["source_sha256"], digest(prose))
            self.assertEqual(chapter["sha256"], digest(chapter["text"]))
            self.assertLessEqual(len(chapter["text"].encode("utf-8")), 12000)

    def test_small_request_is_unchanged(self):
        payload = {"goal": "调查", "recent_chapters": []}
        self.assertEqual(fit(payload, 84000), payload)

    def test_state_budget_counts_meaning_labels_before_reference_allocation(self):
        rows = [
            {
                "reference_id": "fact_record:" + str(i),
                "record_id": str(i),
                "value": "已记录",
                "memory_meaning": {
                    "units": [
                        {
                            "text": "实际原文" * 100,
                            "epistemic_status": "reported_unverified",
                        }
                    ]
                },
            }
            for i in range(12)
        ]
        view = {"records": rows, "omitted_count": 0}
        original = copy.deepcopy(view)
        selected = select_qualified_state(view, 5000)
        self.assertLessEqual(size(selected), 5000)
        self.assertLess(len(selected["records"]), len(rows))
        self.assertEqual(view, original)
        self.assertEqual(
            len(selected["records"]) + selected["omitted_count"], len(rows)
        )
        self.assertTrue(all(r in rows for r in selected["records"]))

    def test_actual_chapter_five_capacity_failure_keeps_choices_consistent(self):
        from memory_runtime.writing import WritingSession

        root = write_novel.ROOT
        p = (
            root
            / "runs/event_first_30000_20261025_memory_a/working/checkpoint_0030.json"
        )
        saved = json.loads(p.read_text(encoding="utf-8"))
        book = saved["book"]
        original = copy.deepcopy(book)
        config = json.loads(
            (
                root
                / "docs/verification/event_first_30000_20261025_memory_a/test_config.json"
            ).read_text(encoding="utf-8")
        )
        session = object.__new__(WritingSession)
        session.book = book
        session.plan = write_novel.validate_config(config)
        context = session.context(
            "继续调查旧日志，保持已保存的状态与人物说法区别", "许闻 梁策 日志"
        )
        self.assertLessEqual(size(context), 84000)
        records = context["event_plan_state"]["records"]
        self.assertTrue(records)
        self.assertEqual(
            context["reference_choices"], [r["reference_id"] for r in records]
        )
        self.assertEqual(
            [r["record_choice"] for r in records], list(range(1, len(records) + 1))
        )
        self.assertTrue(all("memory_meaning" in r for r in records))
        self.assertGreater(context["event_plan_state"]["omitted_count"], 0)
        self.assertEqual(book, original)

    def test_completed_intentions_are_optional_without_altering_active_references(self):
        c = {
            "resolved_intentions": [
                {"record": {"value": "已完成" * 1000}} for _ in range(20)
            ],
            "event_plan_state": {
                "records": [{"reference_id": "fact_record:1", "value": "仍有效"}]
            },
            "reference_choices": ["fact_record:1"],
        }
        bounded = fit(c, 4000)
        self.assertLessEqual(size(bounded), 4000)
        self.assertEqual(bounded["event_plan_state"], c["event_plan_state"])
        self.assertEqual(bounded["reference_choices"], c["reference_choices"])

    def test_large_coverage_catalogs_keep_counts_without_trimming_reference_choices(
        self,
    ):
        c = {
            "memory_coverage": {
                "omitted_ids": ["m_" + str(i) * 20 for i in range(2000)],
                "selected_ids": [],
            },
            "event_plan_state": {
                "records": [{"reference_id": "fact_record:1", "value": "当前状态"}]
            },
            "reference_choices": ["fact_record:1"],
        }
        original = copy.deepcopy(c)
        bounded = fit(c, 4000)
        self.assertLessEqual(size(bounded), 4000)
        self.assertEqual(bounded["memory_coverage"]["omitted_ids_count"], 2000)
        self.assertEqual(bounded["reference_choices"], c["reference_choices"])
        self.assertEqual(c, original)

    def test_actual_last_chapter_dependency_wrappers_compile_without_changing_targets(
        self,
    ):
        from memory_runtime.reference_choices import compile_plan

        root = write_novel.ROOT / "runs/event_first_30000_20261025_memory_b"
        request = json.loads(
            (root / "call_105.request.json").read_text(encoding="utf-8")
        )["payload"]
        raw = json.loads(
            json.loads((root / "call_105.response.json").read_text(encoding="utf-8"))[
                "content"
            ]
        )
        raw.pop("narrative_plan", None)
        compiled = compile_plan(
            raw,
            request["reference_choices"],
            15,
            reference_records=request["event_plan_state"]["records"],
        )
        first = compiled["scenes"][0]["beats"][0]["requires"][0]["reference_id"]
        self.assertEqual(first, request["reference_choices"][6])
        last = compiled["scenes"][2]["beats"][2]["requires"][1]["reference_id"]
        self.assertEqual(last, request["reference_choices"][8])
        self.assertTrue(last.startswith("evidence_object:"))
        self.assertIn("fact_ref", raw["scenes"][0]["beats"][0]["requires"][0])

    def test_dependency_wrapper_never_allows_unknown_or_ambiguous_selector(self):
        from inf_writer.domain import ContractError

        from memory_runtime.reference_choices import compile_plan
        from memory_runtime.test_stage_repair import public_plan

        for value in (
            {"fact_ref": {"record_choice": 999}},
            {"made_up_ref": {"record_choice": 1}},
            {"fact_ref": {"record_choice": 1}, "intention_ref": {"record_choice": 1}},
        ):
            raw = public_plan()
            raw["scenes"][0]["beats"][0]["requires"] = [value]
            with self.assertRaises(ContractError):
                compile_plan(raw, ["fact_record:real"], 1)

    def test_truncated_agent_reply_is_retained_and_repair_has_double_allowance(self):
        requests = []

        class Provider:
            def complete(self, request):
                requests.append(request)
                return (
                    ModelReply('{"text":', 1, 1, 0, "length")
                    if len(requests) == 1
                    else ModelReply('{"text":"正文"}', 1, 1, 0)
                )

        trace = []
        result = JsonAgent(
            "writer", Provider(), compact_narrative=True, max_output_tokens=16384
        ).run({}, trace)
        self.assertEqual(result["text"], "正文")
        self.assertEqual([r.max_output_tokens for r in requests], [16384, 32768])
        self.assertEqual(trace[0]["raw_output"], '{"text":')
        self.assertEqual(trace[0]["finish_reason"], "length")

    def test_http_length_reply_keeps_prose_usage_and_plain_mode_does_not_force_json(
        self,
    ):
        sent = []
        raw = canonical(
            {
                "choices": [
                    {
                        "finish_reason": "length",
                        "message": {"content": "尚未写完的正文"},
                    }
                ],
                "usage": {
                    "prompt_tokens": 5,
                    "completion_tokens": 10,
                    "total_tokens": 15,
                },
            }
        ).encode("utf-8")

        class Connection:
            def __init__(self, *args, **kwargs):
                pass

            def request(self, *args):
                sent.append(json.loads(args[2]))

            def getresponse(self):
                response = io.BytesIO(raw)
                response.status = 200
                return response

            def close(self):
                pass

        provider = ChatCompletionProvider(
            "https://api.deepseek.com/chat/completions",
            "deepseek-flash",
            "placeholder",
            0.3,
            1.2,
            allow_remote=True,
        )
        with patch("inf_writer.chat_provider.http.client.HTTPSConnection", Connection):
            reply = provider.complete(
                ModelRequest(
                    "writer", "只写正文", {"output_mode": "plain_prose"}, 16384
                )
            )
            provider.complete(ModelRequest("planner", "方案", {}, 16384))
        self.assertEqual(reply.content, "尚未写完的正文")
        self.assertEqual(reply.finish_reason, "length")
        self.assertEqual(reply.output_tokens, 10)
        self.assertGreater(reply.cost_usd, 0)
        self.assertNotIn("response_format", sent[0])
        self.assertIn("response_format", sent[1])


if __name__ == "__main__":
    unittest.main()
