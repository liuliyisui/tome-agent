"""Evidence-binding and support-review contracts in ``inf_writer.domain``.

These functions decide whether a memory change is backed by literal prose.
They are pure and offline, so every rejection branch can be pinned exactly.
"""

import unittest

from inf_writer.domain import (
    ContractError,
    checked_support,
    evidence_segments,
    validate_support_review,
)

DRAFT = "第一行证据。\n第二行证据。"


def segment(index=1):
    return evidence_segments(DRAFT)[index - 1]


def claim(identifier="e0001", quote="第一行证据"):
    return {"claim": "结论A", "evidence": [{"evidence_id": identifier, "quote": quote}]}


class CheckedSupportTests(unittest.TestCase):
    def test_valid_claim_is_normalized(self):
        result = checked_support([claim()], DRAFT, "结论A")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["claim"], "结论A")
        self.assertEqual(result[0]["evidence"][0]["quote"], "第一行证据")

    def test_support_must_be_a_nonempty_list(self):
        for value in (None, {}, [], [claim()] * 17):
            with self.subTest(value=type(value).__name__):
                with self.assertRaises(ContractError):
                    checked_support(value, DRAFT, "结论A")

    def test_duplicate_claim_labels_are_rejected(self):
        with self.assertRaises(ContractError):
            checked_support([claim(), claim()], DRAFT, "结论A")

    def test_claim_requires_exactly_claim_and_evidence_fields(self):
        for value in (
            {"evidence": []},
            {"claim": "结论A"},
            {"claim": "结论A", "evidence": [], "extra": 1},
        ):
            with self.subTest(value=value):
                with self.assertRaises(ContractError):
                    checked_support([value], DRAFT, "结论A")

    def test_evidence_count_must_be_between_one_and_eight(self):
        for items in ([], [claim()["evidence"][0]] * 9):
            with self.subTest(count=len(items)):
                with self.assertRaises(ContractError):
                    checked_support(
                        [{"claim": "结论A", "evidence": items}], DRAFT, "结论A"
                    )

    def test_unknown_evidence_id_is_rejected(self):
        with self.assertRaises(ContractError):
            checked_support([claim("e9999")], DRAFT, "结论A")

    def test_quote_absent_from_segment_is_rejected(self):
        with self.assertRaises(ContractError):
            checked_support([claim(quote="并不存在的句子")], DRAFT, "结论A")

    def test_unresolved_claim_accepts_matching_offsets(self):
        item = {"evidence_id": "e0001", "quote": "第一行证据", "start": 0, "end": 5}
        result = checked_support(
            [{"claim": "结论A", "evidence": [item]}], DRAFT, "结论A"
        )
        self.assertEqual(result[0]["evidence"][0]["start"], 0)

    def test_supplied_offsets_must_be_complete(self):
        item = {"evidence_id": "e0001", "quote": "第一行证据", "start": 0}
        with self.assertRaises(ContractError):
            checked_support([{"claim": "结论A", "evidence": [item]}], DRAFT, "结论A")

    def test_resolved_claim_with_matching_offsets_passes(self):
        item = {"evidence_id": "e0001", "quote": "第一行证据", "start": 0, "end": 5}
        result = checked_support(
            [{"claim": "结论A", "evidence": [item]}],
            DRAFT,
            "结论A",
            resolved=True,
        )
        self.assertEqual(result[0]["evidence"][0]["start"], 0)
        self.assertEqual(result[0]["evidence"][0]["end"], 5)

    def test_resolved_claim_with_mismatched_offsets_is_rejected(self):
        item = {"evidence_id": "e0001", "quote": "第一行证据", "start": 1, "end": 6}
        with self.assertRaises(ContractError):
            checked_support(
                [{"claim": "结论A", "evidence": [item]}],
                DRAFT,
                "结论A",
                resolved=True,
            )

    def test_resolved_claim_requires_both_offsets(self):
        item = {"evidence_id": "e0001", "quote": "第一行证据", "start": 0}
        with self.assertRaises(ContractError):
            checked_support(
                [{"claim": "结论A", "evidence": [item]}],
                DRAFT,
                "结论A",
                resolved=True,
            )

    def test_duplicate_evidence_within_claim_is_rejected(self):
        item = {"evidence_id": "e0001", "quote": "第一行证据"}
        with self.assertRaises(ContractError):
            checked_support(
                [{"claim": "结论A", "evidence": [item, dict(item)]}],
                DRAFT,
                "结论A",
            )

    def test_retire_requires_null_value_and_single_claim(self):
        support = [
            {
                "claim": "唯一主张",
                "evidence": [{"evidence_id": "e0001", "quote": segment()["text"][:5]}],
            }
        ]
        checked_support(support, DRAFT, None, retire=True)
        with self.assertRaises(ContractError):
            checked_support(support, DRAFT, "唯一主张", retire=True)
        with self.assertRaises(ContractError):
            checked_support([claim(), claim()], DRAFT, None, retire=True)

    def test_string_value_must_equal_the_single_claim(self):
        with self.assertRaises(ContractError):
            checked_support([claim()], DRAFT, "另一个结论")

    def test_list_value_must_match_claims_in_order(self):
        with self.assertRaises(ContractError):
            checked_support([claim()], DRAFT, ["结论A", "多余结论"])
        result = checked_support([claim()], DRAFT, ["结论A"])
        self.assertEqual(result[0]["claim"], "结论A")

    def test_value_check_can_be_disabled(self):
        result = checked_support([claim()], DRAFT, "任意值", check_value=False)
        self.assertEqual(result[0]["claim"], "结论A")


def review_context():
    return {
        "memory_changes": [
            {"support": [{"claim": "结论A"}], "removals": [{"id": "old"}]}
        ]
    }


def check(ref, status="supported"):
    return {"claim_ref": ref, "status": status, "reason": "有明确正文依据"}


class SupportReviewTests(unittest.TestCase):
    def test_every_expected_check_must_be_present(self):
        result = {
            "support_checks": [
                check("memory_1/claim_1"),
                check("memory_1/removal_1"),
            ]
        }
        self.assertIs(validate_support_review(result, review_context()), result)

    def test_missing_check_is_rejected(self):
        result = {"support_checks": [check("memory_1/claim_1")]}
        with self.assertRaises(ContractError):
            validate_support_review(result, review_context())

    def test_support_checks_must_be_a_list(self):
        with self.assertRaises(ContractError):
            validate_support_review({"support_checks": {}}, review_context())

    def test_each_check_needs_exactly_the_three_fields(self):
        for value in (
            {"claim_ref": "memory_1/claim_1", "status": "supported"},
            {
                "claim_ref": "memory_1/claim_1",
                "status": "supported",
                "reason": "ok",
                "extra": 1,
            },
        ):
            with self.subTest(value=value):
                with self.assertRaises(ContractError):
                    validate_support_review(
                        {"support_checks": [value]}, review_context()
                    )

    def test_unknown_and_duplicate_refs_are_rejected(self):
        for checks in (
            [check("memory_9/claim_9")],
            [check("memory_1/claim_1"), check("memory_1/claim_1")],
        ):
            with self.subTest(count=len(checks)):
                with self.assertRaises(ContractError):
                    validate_support_review(
                        {"support_checks": checks}, review_context()
                    )

    def test_invalid_status_is_rejected(self):
        result = {
            "support_checks": [
                check("memory_1/claim_1", "maybe"),
                check("memory_1/removal_1"),
            ]
        }
        with self.assertRaises(ContractError):
            validate_support_review(result, review_context())

    def test_partial_claim_cannot_be_approved_or_sufficient(self):
        rows = [
            check("memory_1/claim_1", "partial"),
            check("memory_1/removal_1"),
        ]
        for extra in ({"approved": True}, {"memory_check": {"status": "sufficient"}}):
            with self.subTest(extra=extra):
                with self.assertRaises(ContractError):
                    validate_support_review(
                        {"support_checks": rows, **extra}, review_context()
                    )

    def test_partial_claim_without_approval_is_returned(self):
        rows = [
            check("memory_1/claim_1", "unsupported"),
            check("memory_1/removal_1"),
        ]
        result = {"support_checks": rows}
        self.assertIs(validate_support_review(result, review_context()), result)


if __name__ == "__main__":
    unittest.main()
