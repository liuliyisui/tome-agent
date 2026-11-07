"""Independent evidence retrieval must cover history as well as final status."""

import copy
import json
import unittest
from pathlib import Path

import write_novel
from inf_writer.domain import ContractError, canonical
from inf_writer.models import ModelReply
from memory_runtime.pipeline import recall_selection
from memory_runtime.recall_search import searches, selection, source_windows
from memory_runtime.test_memory_meaning import fixture


class RecallSearchTests(unittest.TestCase):
    def test_lookup_schema_is_bounded_and_never_accepts_facts_or_invented_modes(self):
        for value in (
            {"searches": []},
            {"searches": [{"query": "a", "focus": "truth"}]},
            {"searches": [{"query": "a" * 241, "focus": "latest"}]},
            {"searches": [], "answer": "已完成"},
        ):
            with self.assertRaises(ContractError):
                searches(value)

    def test_unannotated_legacy_memory_does_not_change_existing_protocol(self):
        m, c, ids = fixture()
        [r.pop("meaning_annotation") for r in m["items"].values()]

        class Never:
            def complete(self, r):
                raise AssertionError("No lookup for legacy memory")

        self.assertEqual(
            selection(m, "许闻", Never(), [], "test", recall_selection),
            recall_selection(m, "许闻"),
        )

    def test_lookup_outage_keeps_existing_retrieval_available(self):
        m, c, ids = fixture()

        class Offline:
            def complete(self, r):
                raise RuntimeError("offline")

        trace = []
        r = selection(m, "许闻", Offline(), trace, "test", recall_selection)
        self.assertEqual(r, recall_selection(m, "许闻"))
        self.assertEqual(trace[-1]["status"], "DEFERRED")

    def test_actual_multi_question_includes_past_action_and_initial_attitude(self):
        p = (
            Path(write_novel.ROOT)
            / "runs/event_first_30000_20261025_memory_b/final_state.json"
        )
        m = json.loads(p.read_text(encoding="utf-8"))["memory"]
        original = copy.deepcopy(m)
        queries = [
            {
                "query": "许闻 公开陈述 当众宣读 站外发言 实际发生",
                "focus": "action_history",
            },
            {"query": "老周 进站谈话 最初态度 愿意 拒绝 接受", "focus": "earliest"},
            {"query": "许闻 梁策 最终 岗位 安排 去向", "focus": "latest"},
        ]

        class Planner:
            def complete(self, r):
                return ModelReply(canonical({"searches": queries}), 1, 1, 0)

        trace = []
        result = selection(
            m,
            "许闻是否公开，老周最初是否愿意进站，两人岗位后来如何？",
            Planner(),
            trace,
            "test",
            recall_selection,
        )
        selected = set(result["selected_ids"])
        self.assertTrue(
            any(
                "站里他一步不踏" in row["claim"] and "老周肯谈" in row["claim"]
                for row in result["items"]
            )
        )
        self.assertIn("m_fb4710ebed65b7a2f3e8607a", selected)
        self.assertLessEqual(result["bytes"], 36000)
        self.assertEqual(m, original)
        self.assertEqual(trace[-1]["status"], "RETRIEVED")
        bindings = {}
        windows = source_windows(m, result, bindings)
        self.assertLessEqual(len(canonical(windows).encode("utf-8")), 24000)
        self.assertTrue(
            any(
                "我是档案室的许闻" in p["quote"]
                for w in windows
                for p in w["paragraphs"]
            )
        )
        for w in windows:
            for paragraph in w["paragraphs"]:
                row = m["items"][bindings[paragraph["memory_id"]]["memory_id"]]
                self.assertEqual(row["kind"], "prose_excerpt")
                self.assertTrue(
                    any(
                        s["quote"] == paragraph["quote"]
                        and s["evidence_id"] == paragraph["evidence_id"]
                        for s in row["sources"]
                    )
                )


if __name__ == "__main__":
    unittest.main()
