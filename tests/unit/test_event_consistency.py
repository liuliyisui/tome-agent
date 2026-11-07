"""Event-first contracts: planning must not invent or corrupt story facts."""

import copy
import unittest

from inf_writer.domain import ContractError, canonical
from memory_runtime.continuity import empty
from memory_runtime.event_first import prepare, realize


def proposal(number=1, *, scope="actual", kind="state", changes=None):
    fact = {
        "type": "fact",
        "id": "location",
        "subject": "甲",
        "attribute": "location",
        "value": "门外",
        "kind": kind,
    }
    return {
        "number": number,
        "title": "来信",
        "brief": "调查来信",
        "future_updates": [],
        "scenes": [
            {
                "id": "scene",
                "purpose": "调查",
                "participants": ["甲"],
                "beats": [
                    {
                        "id": "arrival",
                        "statement": "甲在门外登记了来信。",
                        "mode": scope,
                        "requires": [],
                        "changes": [fact] if changes is None else changes,
                    }
                ],
            }
        ],
    }


class EventConsistencyTests(unittest.TestCase):
    def test_planning_does_not_mutate_existing_state(self):
        state = empty()
        before = canonical(state)
        result = prepare(state, proposal(), 1)
        self.assertEqual(canonical(state), before)
        self.assertIn("location", result["candidate_state"]["facts"])

    def test_planned_action_does_not_become_fact(self):
        result = prepare(empty(), proposal(scope="planned"), 1)
        self.assertEqual(result["candidate_state"]["facts"], {})
        self.assertTrue(result["commit"]["scenes"][0]["beats"][0]["proposed_changes"])

    def test_unknown_or_duplicate_event_tokens_rejected(self):
        commit = prepare(empty(), proposal(), 1)["commit"]
        for prose in (
            "没有事件",
            "[[event:arrival]][[event:arrival]]",
            "[[event:unknown]]",
        ):
            with self.subTest(prose=prose), self.assertRaises(ContractError):
                realize(prose, commit)

    def test_immutable_fact_cannot_be_changed(self):
        state = prepare(empty(), proposal(kind="immutable"), 1)["candidate_state"]
        before = copy.deepcopy(state)
        change = {
            "type": "transition",
            "id": "move",
            "fact_id": "location",
            "expected_revision": 1,
            "from_value": "门外",
            "to_value": "门内",
        }
        with self.assertRaises(ContractError):
            prepare(state, proposal(2, changes=[change]), 2)
        self.assertEqual(state, before)

    def test_stale_revision_is_not_accepted(self):
        state = prepare(empty(), proposal(), 1)["candidate_state"]
        changed = proposal(2, changes=[])
        changed["scenes"][0]["beats"][0]["requires"] = [
            {"type": "fact", "id": "location", "revision": 2}
        ]
        with self.assertRaises(ContractError):
            prepare(state, changed, 2)


if __name__ == "__main__":
    unittest.main()
