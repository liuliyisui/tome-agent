"""Serialized facts expose readable labels for canonical object records."""

import unittest

from inf_backend import web


class FactLabelTests(unittest.TestCase):
    def book(self):
        return {
            "id": "book-1",
            "metadata": {},
            "state": {
                "chapters": [],
                "writing_state": {
                    "objects": {
                        "n0003r0003": {
                            "id": "n0003r0003",
                            "label": "七号楼拆迁档案照片",
                        }
                    }
                },
                "memory": {
                    "items": {
                        "m1": {
                            "id": "m1",
                            "subject": "objects:n0003r0003",
                            "attribute": "canonical_record",
                            "kind": "state",
                            "claim": "一张照片",
                            "status": "active",
                            "revision": 1,
                            "tier": "recent",
                            "sources": [{"chapter_number": 3, "quote": "一张照片"}],
                        }
                    }
                },
            },
        }

    def test_object_subject_uses_canonical_label(self):
        facts = web.serialize(self.book())["state"]["facts"]
        self.assertEqual(facts["m1"]["label"], "七号楼拆迁档案照片")

    def test_subject_without_canonical_record_has_no_label(self):
        book = self.book()
        book["state"]["memory"]["items"]["m1"]["subject"] = "老周"
        facts = web.serialize(book)["state"]["facts"]
        self.assertNotIn("label", facts["m1"])


if __name__ == "__main__":
    unittest.main()
