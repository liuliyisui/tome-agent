"""Synthetic fixtures only: no real identifiers, credentials or model calls."""

import copy
import json
import unittest
from unittest.mock import Mock

from inf_backend import privacy
from tome_writer.models import ModelRequest

PHONE = "13800138000"
EMAIL = "writer@example.test"
KEY = "sk-" + "FAKE_NOT_A_REAL_SECRET_1234567890"
IDENTITY = "11010519491231002X"  # Published algorithm example, not user data.
CARD = "4111111111111111"  # Payment-network test number.


def report(text):
    return privacy.inspect_sources([("测试输入", text)])


class PrivacyRulesTests(unittest.TestCase):
    def test_phone_formats_and_unicode_normalization(self):
        result = report("+86 138-0013-8000，１３８００１３８０００，138\u200b00138000")
        self.assertEqual(result["findings"][0]["count"], 3)
        self.assertTrue(result["requires_confirmation"])
        self.assertFalse(result["blocked"])

    def test_numbers_in_identifiers_are_not_phones(self):
        self.assertEqual(
            report("c13800138000 v13800138000b 138001380001 12800138000")["total"], 0
        )

    def test_identity_requires_valid_date_and_checksum(self):
        self.assertEqual(report(IDENTITY)["findings"][0]["category"], "identity")
        self.assertEqual(report(IDENTITY[:-1] + "0")["total"], 0)
        self.assertEqual(report("11010519490231002X")["total"], 0)

    def test_bank_cards_require_context_and_luhn(self):
        self.assertEqual(report(CARD)["total"], 0)
        self.assertEqual(
            report("卡号：4111 1111 1111 1111")["findings"][0]["category"], "bank_card"
        )
        self.assertEqual(report("卡号：4111111111111112")["total"], 0)

    def test_email_and_reports_never_include_matches(self):
        result = report(f"请联系 {EMAIL}，电话 {PHONE}")
        encoded = json.dumps(result, ensure_ascii=False)
        for private in (EMAIL, PHONE):
            self.assertNotIn(private, encoded)
        self.assertEqual(
            {f["category"] for f in result["findings"]}, {"email", "phone"}
        )

    def test_secrets_block_even_with_confirmation_and_are_not_echoed(self):
        for text in (
            KEY,
            "api_key=" + "FAKE_CREDENTIAL_VALUE_123456",
            "-----BEGIN RSA PRIVATE KEY-----",
            "ghp_" + "a" * 36,
        ):
            with self.subTest(text=text):
                result = report(text)
                self.assertTrue(result["blocked"])
                with self.assertRaises(privacy.SensitiveInformationError) as raised:
                    privacy.enforce(result, True)
                self.assertNotIn(text, str(raised.exception))
                self.assertNotIn(text, json.dumps(result))

    def test_assignment_and_key_prefix_are_one_finding(self):
        self.assertEqual(report('api_key="' + KEY + '"')["total"], 1)

    def test_common_template_placeholder_does_not_block(self):
        self.assertEqual(report("api_key=YOUR_API_KEY_HERE")["total"], 0)

    def test_personal_information_requires_literal_true(self):
        result = report(EMAIL)
        for confirmation in (None, False, "true", 1):
            with self.assertRaises(privacy.SensitiveInformationError):
                privacy.enforce(result, confirmation)
        privacy.enforce(result, True)

    def test_book_sources_cover_feedback_memory_skills_and_style_without_mutation(self):
        book = {
            "metadata": {"title": "测试", "prompt": PHONE},
            "state": {
                "chapters": [{"title": "正文", "text": EMAIL}],
                "memory": {"items": {"fact": {"claim": PHONE}}},
            },
        }
        original = copy.deepcopy(book)
        result = privacy.inspect_book(
            book, {"reference": EMAIL}, [{"content": PHONE}], EMAIL
        )
        self.assertEqual(len(result["findings"]), 6)
        self.assertEqual(book, original)
        self.assertNotIn(PHONE, json.dumps(result))

    def test_gateway_blocks_before_provider_after_injected_context(self):
        provider = Mock()
        gateway = privacy.PrivacyGateway(provider)
        request = ModelRequest(
            "writer", "写作", {"writing_style": {"reference": EMAIL}}
        )
        with self.assertRaises(privacy.SensitiveInformationError):
            gateway.complete(request)
        provider.complete.assert_not_called()
        privacy.PrivacyGateway(provider, True).complete(request)
        provider.complete.assert_called_once_with(request)
        provider.reset_mock()
        with self.assertRaises(privacy.SensitiveInformationError):
            privacy.PrivacyGateway(provider, True).complete(
                ModelRequest("writer", "写作", {"feedback": KEY})
            )
        provider.complete.assert_not_called()

    def test_clean_fiction_passes_without_confirmation(self):
        provider = Mock()
        request = ModelRequest(
            "planner", "场景规划", {"story": "夜半，他走进武馆。", "chapter": 12}
        )
        privacy.PrivacyGateway(provider).complete(request)
        provider.complete.assert_called_once_with(request)


if __name__ == "__main__":
    unittest.main()
