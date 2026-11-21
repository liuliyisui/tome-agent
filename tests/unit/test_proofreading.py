"""Offline findings use UTF-16 editor offsets and never echo private matches."""

import copy
import json
import unittest

from inf_backend import proofreading


def review(text, title="测试"):
    return proofreading.inspect([{"number": 1, "title": title, "text": text}])


class ProofreadingTests(unittest.TestCase):
    def test_typo_suggestion_is_conservative_and_does_not_modify_text(self):
        text = "他迫不急待地走进门。"
        result = review(text)
        issue = next(f for f in result["findings"] if f["category"] == "typo")
        self.assertEqual(issue["replacement"], "迫不及待")
        self.assertIn("疑似", issue["message"])
        self.assertEqual(text, "他迫不急待地走进门。")

    def test_private_values_are_not_echoed_but_can_be_located(self):
        text = "电话１３８００１３８０００，邮箱 writer@example.test。"
        result = review(text)
        self.assertEqual(
            {f["category"] for f in result["findings"]}, {"phone", "email"}
        )
        body = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("１３８００１３８０００", body)
        self.assertNotIn("writer@example.test", body)
        self.assertTrue(all(f["end"] > f["start"] for f in result["findings"]))

    def test_utf16_and_crlf_offsets_select_the_correct_word(self):
        text = "😀开场。\r\n他迫不急待地出发。"
        finding = next(f for f in review(text)["findings"] if f["category"] == "typo")
        normalized = text.replace("\r\n", "\n").encode("utf-16-le")
        selected = normalized[finding["start"] * 2 : finding["end"] * 2].decode(
            "utf-16-le"
        )
        self.assertEqual(selected, "迫不急待")

    def test_repeats_and_unclosed_quotes_are_not_automatically_deleted(self):
        result = review("“他说的的故事还没结束。")
        kinds = {f["category"] for f in result["findings"]}
        self.assertIn("repeated_word", kinds)
        self.assertIn("punctuation", kinds)

    def test_secret_later_in_a_long_report_still_blocks(self):
        text = "迫不急待。" * 240
        result = proofreading.inspect(
            [
                {"number": 1, "title": "章节", "text": text},
                {
                    "number": 2,
                    "title": "章节",
                    "text": "sk-FAKE_ONLY_FOR_TEST_1234567890",
                },
            ]
        )
        self.assertTrue(result["blocked"])
        self.assertTrue(result["truncated"])
        self.assertTrue(any(f["category"] == "credential" for f in result["findings"]))
        self.assertLessEqual(len(result["findings"]), proofreading.MAX_FINDINGS)

    def test_revision_changes_with_text_or_title_and_inputs_are_unchanged(self):
        chapters = [{"number": 1, "title": "标题", "text": "正文。"}]
        original = copy.deepcopy(chapters)
        signature = proofreading.inspect(chapters)["revision"]
        self.assertEqual(chapters, original)
        chapters[0]["title"] = "新标题"
        self.assertNotEqual(signature, proofreading.inspect(chapters)["revision"])


if __name__ == "__main__":
    unittest.main()
