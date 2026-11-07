"""Format-only retries cannot replace a complete draft with its continuation."""

import copy
import json
import unittest

from inf_writer.agents import JsonAgent
from inf_writer.domain import ContractError, canonical
from inf_writer.models import ModelReply
from memory_runtime.completion import continue_prose
from memory_runtime.test_event_first import ROOT


class StageFormatPreservationTests(unittest.TestCase):
    def actual(self):
        folder = ROOT / "runs/event_first_30000_20261028_threads_b"
        request = json.loads(
            (folder / "call_003.request.json").read_text(encoding="utf-8")
        )
        response = json.loads(
            (folder / "call_003.response.json").read_text(encoding="utf-8")
        )
        return request["payload"], response["content"]

    def test_actual_first_draft_with_type_is_accepted_once_without_prose_change(self):
        payload, raw = self.actual()
        expected = json.loads(raw)["new_stage_text"]
        calls = []

        class Replay:
            def complete(self, r):
                calls.append(r)
                return ModelReply(raw, 1, 1, 0)

        trace = []
        result = JsonAgent("writer", Replay(), compact_narrative=True).run(
            payload, trace
        )
        self.assertEqual(result["text"], expected)
        self.assertEqual(len(calls), 1)
        self.assertIn("“无人到闸”，和“闸上有人影”", expected)
        self.assertIn("我先把补件做完", expected)
        self.assertEqual(trace[0]["status"], "ACCEPTED")
        self.assertEqual(
            trace[0]["normalizations"][0]["rule"], "writer_json_object_type"
        )

    def test_unknown_extra_field_still_rejected_but_same_prose_can_be_repaired(self):
        payload, _ = self.actual()
        body = "甲先接过卷宗，再发现结论与证言不同。"
        calls = []

        class Replay:
            def complete(self, r):
                calls.append(copy.deepcopy(r))
                value = (
                    {"new_stage_text": body, "unexpected": "reject"}
                    if len(calls) == 1
                    else {"new_stage_text": body}
                )
                return ModelReply(canonical(value), 1, 1, 0)

        result = JsonAgent("writer", Replay(), compact_narrative=True).run(payload, [])
        self.assertEqual(result["text"], body)
        self.assertEqual(len(calls), 2)
        self.assertIn("尚未保存", calls[1].payload["repair"]["instruction"])

    def test_changed_retry_is_rejected_and_fallback_keeps_first_unit(self):
        payload, _ = self.actual()
        first = canonical(
            {"new_stage_text": "甲接过卷宗，发现了措辞差异。", "extra": True}
        )
        second = canonical({"new_stage_text": "先前的记录还在台上，甲开始处理新材料。"})
        calls = []
        trace = []

        class Replay:
            def complete(self, r):
                calls.append(r)
                return ModelReply(first if len(calls) == 1 else second, 1, 1, 0)

        with self.assertRaises(ContractError):
            JsonAgent("writer", Replay(), compact_narrative=True).run(payload, trace)
        self.assertIn("changed stage prose", trace[-1]["error"])

        class Never:
            def complete(self, r):
                raise AssertionError("A complete first draft is already available")

        result = continue_prose(Never(), {}, "", 1, [], [first, second])
        self.assertEqual(result, json.loads(first)["new_stage_text"])


if __name__ == "__main__":
    unittest.main()
