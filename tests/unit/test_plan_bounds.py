import unittest

from memory_runtime.writing import record_future_plan


class FuturePlanBoundsTests(unittest.TestCase):
    def test_entries_beyond_the_chapter_cap_are_not_recorded(self):
        book = {"plan": {}}
        proposal = {"future_updates": [
            {"number": 2, "title": "底账缺页", "brief": "翻查底账。"},
            {"number": 3, "title": "旧名字", "brief": "核对名单。"},
        ]}
        record_future_plan(book, proposal, 2)
        self.assertEqual(list(book["plan"]), ["2"])

    def test_single_chapter_story_keeps_no_future_entries(self):
        book = {"plan": {}}
        record_future_plan(book, {"future_updates": [{"number": 2, "title": "多余", "brief": "不会被写出。"}]}, 1)
        self.assertEqual(book["plan"], {})

    def test_entries_without_integer_numbers_are_ignored(self):
        book = {"plan": {}}
        record_future_plan(book, {"future_updates": [{"number": "2"}, {"title": "缺少编号"}]}, 5)
        self.assertEqual(book["plan"], {})


if __name__ == "__main__":
    unittest.main()
