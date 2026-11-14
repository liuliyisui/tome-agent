"""Equivalence classes and boundary values for new-book input fields.

The ``chapters`` and ``target_units`` fields are the two numeric inputs of
``service.create_book``.  Every valid class keeps only the boundary values,
every invalid class takes one representative, and rejected input must not
leave a half-created book on disk.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inf_backend import service
from inf_backend.settings import Settings

VALID_CHAPTERS = (1, 50, 100)
INVALID_CHAPTERS = (0, -1, 101, 1.5, "10", True, None)
VALID_TARGETS = (500, 1000, 200000)
INVALID_TARGETS = (499, -1, 200001, 500.0, "5000", True, None)
INVALID_TITLES = ("", "   ", None, 123)
INVALID_PROMPTS = ("", "  \t", None, 5)


class BookInputValidationTests(unittest.TestCase):
    def setUp(self):
        self._folder = tempfile.TemporaryDirectory()
        self.books = Path(self._folder.name)
        self._patches = [
            patch.object(service, "BOOKS", self.books),
            patch.object(service.database, "enabled", return_value=False),
        ]
        for item in self._patches:
            item.start()
        self.settings = Settings(api_key="fake")

    def tearDown(self):
        for item in reversed(self._patches):
            item.stop()
        self._folder.cleanup()

    def create(self, name, chapters=1, target=500, title="作品", prompt="故事"):
        return service.create_book(
            name, title, prompt, chapters, target, settings=self.settings
        )

    def test_valid_equivalence_classes_create_book(self):
        for index, chapters in enumerate(VALID_CHAPTERS):
            with self.subTest(field="chapters", value=chapters):
                book = self.create(f"valid-chapters-{index}", chapters=chapters)
                self.assertEqual(book["metadata"]["target_chapters"], chapters)
        for index, target in enumerate(VALID_TARGETS):
            with self.subTest(field="target_units", value=target):
                book = self.create(f"valid-target-{index}", target=target)
                self.assertEqual(book["metadata"]["target_units"], target)

    def test_invalid_chapters_rejected_without_creating_folder(self):
        for index, value in enumerate(INVALID_CHAPTERS):
            with self.subTest(value=value):
                name = f"bad-chapters-{index}"
                with self.assertRaises(ValueError):
                    self.create(name, chapters=value)
                self.assertFalse((self.books / name).exists())

    def test_invalid_target_units_rejected_without_creating_folder(self):
        for index, value in enumerate(INVALID_TARGETS):
            with self.subTest(value=value):
                name = f"bad-target-{index}"
                with self.assertRaises(ValueError):
                    self.create(name, target=value)
                self.assertFalse((self.books / name).exists())

    def test_invalid_title_and_prompt_rejected(self):
        for index, value in enumerate(INVALID_TITLES):
            with self.subTest(field="title", value=value):
                name = f"bad-title-{index}"
                with self.assertRaises(ValueError):
                    self.create(name, title=value)
                self.assertFalse((self.books / name).exists())
        for index, value in enumerate(INVALID_PROMPTS):
            with self.subTest(field="prompt", value=value):
                name = f"bad-prompt-{index}"
                with self.assertRaises(ValueError):
                    self.create(name, prompt=value)
                self.assertFalse((self.books / name).exists())

    def test_chapters_boundary_values(self):
        cases = (
            (0, False),
            (1, True),
            (2, True),
            (99, True),
            (100, True),
            (101, False),
        )
        for index, (value, valid) in enumerate(cases):
            with self.subTest(value=value):
                name = f"chapter-boundary-{index}"
                if valid:
                    book = self.create(name, chapters=value)
                    self.assertEqual(book["metadata"]["target_chapters"], value)
                else:
                    with self.assertRaises(ValueError):
                        self.create(name, chapters=value)
                    self.assertFalse((self.books / name).exists())

    def test_target_units_boundary_values(self):
        cases = (
            (499, False),
            (500, True),
            (501, True),
            (199999, True),
            (200000, True),
            (200001, False),
        )
        for index, (value, valid) in enumerate(cases):
            with self.subTest(value=value):
                name = f"target-boundary-{index}"
                if valid:
                    book = self.create(name, target=value)
                    self.assertEqual(book["metadata"]["target_units"], value)
                else:
                    with self.assertRaises(ValueError):
                        self.create(name, target=value)
                    self.assertFalse((self.books / name).exists())

    def test_duplicate_book_id_is_rejected(self):
        self.create("duplicate")
        with self.assertRaises(ValueError):
            self.create("duplicate")
