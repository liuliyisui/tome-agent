"""Memory placement repair preserves validated decisions and source facts."""

import copy
import unittest

from memory_runtime.continuity import empty
from memory_runtime.engine import MemoryEngine
from memory_runtime.event_first import prepare, project_memory, realize
from memory_runtime.pipeline import LayerAgent
from tests.unit.test_event_consistency import proposal
from tome_writer.domain import canonical, digest
from tome_writer.models import ModelReply


class PartialPlacementGateway:
    def __init__(self, repair):
        self.repair = repair
        self.requests = []

    def complete(self, request):
        self.requests.append(copy.deepcopy(request))
        rows = request.payload["items"]
        if len(self.requests) == 1:
            rows = rows[:-1]
        elif self.repair == "malformed":
            return ModelReply("not json", 1, 1, 0)
        values = [
            {
                "id": row["id"],
                "tier": "unknown"
                if len(self.requests) > 1 and self.repair == "invalid"
                else "recent",
                "priority": 3,
                "reason": "测试归档",
            }
            for row in rows
        ]
        if len(self.requests) > 1 and self.repair == "duplicate":
            values *= 3
        return ModelReply(canonical({"placements": values}), 1, 1, 0)


class MemoryLayerTests(unittest.TestCase):
    def test_partial_placement_repairs_only_missing_items(self):
        commit = prepare(empty(), proposal(), 1)["commit"]
        template = "[[event:arrival]]"
        prose = realize(template, commit)
        chapter = {
            "number": 1,
            "title": "来信",
            "text": prose,
            "sha256": digest(prose),
            "event_commit": commit,
            "realization_template": template,
        }
        memory = project_memory(MemoryEngine.empty(), [chapter], 1, [])
        original = copy.deepcopy(memory)
        for repair in ("valid", "invalid", "malformed", "duplicate"):
            with self.subTest(repair=repair):
                gateway = PartialPlacementGateway(repair)
                updated, report = LayerAgent(gateway).run(
                    memory, [chapter], 1, "来信", []
                )
                self.assertEqual(memory, original)
                self.assertEqual(len(gateway.requests), 2)
                self.assertEqual(len(gateway.requests[1].payload["items"]), 1)
                self.assertEqual(set(updated["items"]), set(memory["items"]))
                self.assertEqual(
                    report["status"],
                    "APPLIED" if repair == "valid" else "APPLIED_WITH_DEFERRED",
                )
                self.assertEqual(
                    len(report["deferred_ids"]), 0 if repair == "valid" else 1
                )
                for key, row in updated["items"].items():
                    self.assertEqual(row["claim"], memory["items"][key]["claim"])


if __name__ == "__main__":
    unittest.main()
