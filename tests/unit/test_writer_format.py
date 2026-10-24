"""Narrow writer-format compatibility; no real models or credentials."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from inf_writer.agents import JsonAgent, build_agents, validate
from inf_writer.demo import DemoModel
from inf_writer.domain import ContractError, Snapshot
from inf_writer.models import Budget, ModelGateway, ModelReply
from inf_writer.runtime import Coordinator
from inf_writer.storage import FileStore

BODY = "灯塔下，林澄展开了那份档案。\n\n她没有立刻说话。"


class WriterFormatTests(unittest.TestCase):
    def test_plain_output_remains_supported(self):
        self.assertEqual(validate("writer", {"text": BODY}), {"text": BODY})

    def test_known_json_object_metadata_normalizes_without_mutation(self):
        original = {"type": "json_object", "text": BODY}
        result = validate("writer", original)
        self.assertEqual(result, {"text": BODY})
        self.assertEqual(original, {"type": "json_object", "text": BODY})

    def test_body_preserved_exactly_including_whitespace(self):
        body = "  \n" + BODY + "\n  "
        self.assertEqual(validate("writer", {"type": "json_object", "text": body})["text"], body)

    def test_unknown_fields_not_silently_dropped(self):
        for name in ("title", "tool_calls", "reasoning", "approved", "memory_changes"):
            with self.subTest(name=name), self.assertRaises(ContractError):
                validate("writer", {"type": "json_object", "text": BODY, name: "extra"})

    def test_wrapper_labels_do_not_select_operations(self):
        for kind in ('chapter_text','tool_call','text','image'):
            self.assertEqual(validate('writer',{'type':kind,'text':BODY}),{'text':BODY})

    def test_invalid_type_rejected(self):
        for kind in (None, True, 3, [], {}):
            with self.subTest(kind=kind), self.assertRaises(ContractError):
                validate("writer", {"type": kind, "text": BODY})

    def test_missing_empty_and_wrong_type_body_rejected(self):
        for value in ({"type": "json_object"}, {"type": "json_object", "text": " "},
                      {"type": "json_object", "text": 5}, {"type": "json_object", "text": [BODY]},
                      [{"type": "json_object", "text": BODY}]):
            with self.subTest(value=value), self.assertRaises(ContractError):
                validate("writer", value)

    def test_known_wrapper_no_retry_and_raw_trace_preserved(self):
        class Wrapped:
            def complete(self, request):
                return ModelReply(json.dumps({"type": "json_object", "text": BODY}, ensure_ascii=False), 0, 0, 0)
        budget = Budget(max_calls=2)
        agent = JsonAgent("writer", ModelGateway(Wrapped(), budget))
        trace = []
        self.assertEqual(agent.run({}, trace), {"text": BODY})
        self.assertEqual(budget.calls, 1)
        self.assertEqual(json.loads(trace[0]["raw_output"])["type"], "json_object")
        self.assertEqual(trace[0]["normalizations"][0]["rule"], "writer_json_object_type")

    def test_invalid_type_keeps_bounded_repair(self):
        class Invalid:
            def complete(self, request):
                return ModelReply(json.dumps({"type": [], "text": BODY}), 0, 0, 0)
        budget = Budget(max_calls=2)
        agent = JsonAgent("writer", ModelGateway(Invalid(), budget))
        with self.assertRaises(ContractError):
            agent.run({}, [])
        self.assertEqual(budget.calls, 2)

    def test_duplicate_json_keys_still_rejected(self):
        class Duplicated:
            def complete(self, request):
                return ModelReply('{"type":"json_object","text":"first","text":"second"}', 0, 0, 0)
        with self.assertRaises(ContractError):
            JsonAgent("writer", ModelGateway(Duplicated(), Budget(max_calls=2))).run({}, [])

    def test_two_chapter_strict_pipeline_accepts_wrapped_writer(self):
        class WrappedDemo(DemoModel):
            def complete(self, request):
                reply = super().complete(request)
                if request.role == "writer":
                    value = json.loads(reply.content)
                    value["type"] = "json_object"
                    return ModelReply(json.dumps(value, ensure_ascii=False), 0, 0, 0)
                return reply
        root = Path(__file__).resolve().parents[1] / "runs" / "test-tmp"
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as folder:
            store = FileStore(folder)
            store.initialize(Snapshot("formatdemo", "离线验证"))
            budget = Budget(max_calls=8)
            runner = Coordinator(store, build_agents(ModelGateway(WrappedDemo(), budget)))
            self.assertEqual(runner.write_next("formatdemo", "c1").status, "COMMITTED")
            self.assertEqual(runner.write_next("formatdemo", "c2").status, "COMMITTED")
            self.assertEqual(budget.calls, 8)
            self.assertEqual(len(store.load("formatdemo").chapters), 2)


if __name__ == "__main__":
    unittest.main()
