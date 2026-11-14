"""Boundary and continuity contracts with synthetic, independent data."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inf_backend import service
from inf_backend.settings import Settings
from memory_runtime.continuity import apply, context_view, empty
from tome_writer.domain import ContractError, canonical


def event(identifier, date, quote, mode="present"):
    return {
        "type": "event",
        "id": identifier,
        "date": date,
        "quote": quote,
        "mode": mode,
        "objects": [],
        "after": [],
    }


def missing_document():
    return {
        "type": "object",
        "id": "attachment",
        "label": "7-B",
        "form": "original",
        "status": "missing",
        "origin": "accident",
        "quote": "7-B原件未见。",
    }


def state_with_missing_document():
    text = "1998年事故发生。\n7-B原件未见。"
    return apply(
        empty(),
        [
            event("accident", "1998", "1998年事故发生。", "historical"),
            missing_document(),
        ],
        text,
        1,
    )


class BookBoundaryTests(unittest.TestCase):
    def test_target_size_and_chapter_count_equivalence_classes(self):
        cases = [
            (1, 500, True),
            (100, 200000, True),
            (0, 500, False),
            (101, 500, False),
            (1, 499, False),
            (1, 200001, False),
            (True, 500, False),
            (1, True, False),
        ]
        with (
            tempfile.TemporaryDirectory() as folder,
            patch.object(service, "BOOKS", Path(folder)),
            patch.object(service.database, "enabled", return_value=False),
        ):
            for index, (chapters, target, valid) in enumerate(cases):
                with self.subTest(chapters=chapters, target=target):
                    args = (f"boundary-{index}", "测试", "故事", chapters, target)
                    if valid:
                        result = service.create_book(
                            *args, settings=Settings(api_key="fake")
                        )
                        self.assertEqual(result["metadata"]["target_units"], target)
                    else:
                        with self.assertRaises(ValueError):
                            service.create_book(
                                *args, settings=Settings(api_key="fake")
                            )
                        self.assertFalse((Path(folder) / f"boundary-{index}").exists())


class ContinuityContractTests(unittest.TestCase):
    def test_context_view_respects_budget_and_excludes_source_quotes(self):
        state = state_with_missing_document()
        plan = {
            "next": {
                "id": "letter",
                "chapter": 2,
                "quote": "原文",
                "source_sha256": "hash",
                "summary": "寻找信件",
            }
        }
        view = context_view(state, "letter 7-B", max_bytes=10000, plans=plan)
        self.assertEqual(view["omitted_count"], 0)
        self.assertTrue(any(row["type"] == "plan" for row in view["records"]))
        self.assertTrue(
            all(
                "quote" not in row and "source_sha256" not in row
                for row in view["records"]
            )
        )
        limited = context_view(state, "letter 7-B", max_bytes=200, plans=plan)
        self.assertGreater(limited["omitted_count"], 0)
        self.assertEqual(state["objects"]["attachment"]["status"], "missing")

    def test_date_validation_rejects_fabricated_precision_and_invalid_day(self):
        for date, text in (("2024-04-01", "2024年4月"), ("2023-02-29", "2023-02-29")):
            with self.subTest(date=date), self.assertRaises(ContractError):
                apply(empty(), [event("dated", date, text)], text, 1)
        valid = "2024-02-29"
        self.assertEqual(
            apply(empty(), [event("leap", valid, valid)], valid, 1)["present_cursor"][
                "date"
            ],
            valid,
        )

    def test_identity_resolution_preserves_signer_history(self):
        initial = "库方刘与不明签收人完成交接。"
        handoff = {
            "type": "handoff",
            "id": "handoff",
            "quote": initial,
            "signers": ["刘", "unknown_sender"],
            "non_signers": ["青年"],
            "attendees": ["青年"],
            "signer_count": 2,
        }
        state = apply(empty(), [handoff], initial, 1)
        later = "确认不明签收人是周。"
        identify = {
            "type": "identify",
            "id": "resolve_sender",
            "quote": later,
            "unknown_id": "unknown_sender",
            "person_id": "周",
        }
        updated = apply(
            state,
            [identify, {**handoff, "quote": later, "signers": ["刘", "周"]}],
            later,
            2,
        )
        self.assertEqual(updated["handoffs"]["handoff"]["signers"], ["刘", "周"])
        with self.assertRaises(ContractError):
            apply(state, [{**identify, "person_id": "青年"}], later, 2)

    def test_signing_records_reject_person_in_both_lists(self):
        text = "刘和青年出席交接。"
        row = {
            "type": "handoff",
            "id": "handoff",
            "quote": text,
            "signers": ["刘", "青年"],
            "non_signers": ["青年"],
            "attendees": ["刘", "青年"],
            "signer_count": 2,
        }
        with self.assertRaisesRegex(ContractError, "both sign"):
            apply(empty(), [row], text, 1)
        row["signers"] = ["刘", "unknown_sender"]
        result = apply(empty(), [row], text, 1)
        self.assertEqual(
            result["handoffs"]["handoff"]["signers"], ["刘", "unknown_sender"]
        )

    def test_progress_cannot_move_backwards_without_evidenced_new_pass(self):
        first, second = "已完成十七页。", "第二次完成八页。"
        row = {
            "type": "progress",
            "id": "pages",
            "pass_id": "first",
            "completed": 17,
            "total": 17,
            "quote": first,
        }
        state = apply(empty(), [row], first, 1)
        with self.assertRaisesRegex(ContractError, "backwards"):
            apply(state, [{**row, "completed": 8, "quote": second}], second, 2)
        with self.assertRaisesRegex(ContractError, "explicit prose"):
            apply(
                state,
                [{**row, "pass_id": "second", "completed": 8, "quote": second}],
                second,
                2,
            )
        reason = "这是第二轮逐字细核。"
        revised = {
            **row,
            "pass_id": "second",
            "completed": 8,
            "quote": second,
            "restart_quote": reason,
        }
        updated = apply(state, [revised], second + "\n" + reason, 2)
        self.assertEqual(updated["progress"]["pages"]["completed"], 8)

    def test_missing_document_cannot_be_directly_observed(self):
        text = "甲检查了原件。"
        observation = {
            "type": "observe",
            "id": "check",
            "quote": text,
            "object_id": "attachment",
            "method": "direct",
            "source_id": None,
        }
        state = state_with_missing_document()
        before = canonical(state)
        with self.assertRaisesRegex(ContractError, "missing original"):
            apply(state, [observation], text, 2)
        self.assertEqual(canonical(state), before)

    def test_photo_requires_an_available_carrier_bound_to_original(self):
        text = "旧照片仍在，来源注明7-B。"
        photo = {
            "type": "object",
            "id": "old_photo",
            "label": "7-B页缘照片",
            "form": "photo",
            "status": "available",
            "origin": None,
            "source": "attachment",
            "quote": text,
        }
        observation = {
            "type": "observe",
            "id": "photo_check",
            "quote": text,
            "object_id": "attachment",
            "method": "photo",
            "source_id": "old_photo",
        }
        state = state_with_missing_document()
        with self.assertRaisesRegex(ContractError, "carrier"):
            apply(state, [observation], text, 2)
        updated = apply(state, [photo, observation], text, 2)
        self.assertEqual(updated["objects"]["attachment"]["status"], "missing")
        self.assertEqual(
            updated["observations"]["photo_check"]["source_id"], "old_photo"
        )

    def test_missing_document_becomes_available_only_through_find_event(self):
        state = state_with_missing_document()
        found = "2024年4月发现7-B，原件收回。"
        with self.assertRaises(ContractError):
            apply(
                state,
                [{**missing_document(), "status": "available"}],
                "7-B原件未见。",
                2,
            )
        finding = event("found", "2024-04", found)
        finding["objects"] = ["attachment"]
        document = {
            **missing_document(),
            "status": "available",
            "event_id": "found",
            "quote": found,
        }
        updated = apply(state, [finding, document], found, 2)
        self.assertEqual(updated["objects"]["attachment"]["status"], "available")

    def test_present_time_cannot_move_backwards_but_history_can(self):
        first = "2024年4月完成取样。"
        state = apply(empty(), [event("sample", "2024-04", first)], first, 1)
        snapshot = canonical(state)
        earlier = "2024年3月登记。"
        with self.assertRaises(ContractError):
            apply(state, [event("register", "2024-03", earlier)], earlier, 2)
        self.assertEqual(canonical(state), snapshot)
        recovered = apply(
            state, [event("register", "2024-03", earlier, "historical")], earlier, 2
        )
        self.assertEqual(recovered["present_cursor"]["date"], "2024-04")

    def test_missing_or_invented_evidence_does_not_change_state(self):
        state = empty()
        snapshot = canonical(state)
        with self.assertRaises(ContractError):
            apply(state, [event("event", "2024-04", "不存在的引文")], "实际正文", 1)
        self.assertEqual(canonical(state), snapshot)

    def test_retelling_does_not_duplicate_event(self):
        first = "2024年4月取样。"
        row = event("sample", "2024-04", first)
        state = apply(empty(), [row], first, 1)
        second = "回忆2024年4月取样的经过。"
        state = apply(
            state, [{**row, "mode": "historical", "quote": second}], second, 2
        )
        self.assertEqual(len(state["events"]), 1)
        self.assertEqual(state["present_cursor"]["date"], "2024-04")


if __name__ == "__main__":
    unittest.main()
