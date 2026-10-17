import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from tome_agent.service import new_book_id, book_labels
from tome_agent.state import Workspace
from tome_agent.checkpoints import save_checkpoint
from tome_agent.providers.deepseek import Settings


class BookIdentityTests(unittest.TestCase):
    def test_generated_ids_and_duplicate_titles_preserve_legacy_ids(self):
        with tempfile.TemporaryDirectory() as tmp, patch("tome_agent.service.BOOKS", Path(tmp)):
            ids = ["old-manual-id", new_book_id()]
            self.assertNotEqual(ids[1], new_book_id())
            book = Workspace("灯塔来信", "构想", [{"title": "一", "goal": "出发"}])
            for book_id in ids:
                save_checkpoint(book, Path(tmp) / book_id / "book.json")
            labels = book_labels(ids)
            self.assertEqual(len(set(labels.values())), 2)
            self.assertTrue(all(label.startswith("灯塔来信") for label in labels.values()))
            self.assertEqual(book_labels([ids[0]])[ids[0]], "灯塔来信")
            self.assertIn("无法读取", book_labels(["broken"])["broken"])

    def test_sidebar_uses_title_and_creation_opens_new_book(self):
        import streamlit as st
        st.cache_data.clear()
        with tempfile.TemporaryDirectory() as tmp, patch("tome_agent.service.BOOKS", Path(tmp)), patch("tome_agent.providers.deepseek.Settings.load", return_value=Settings("fake")), patch("tome_agent.service.new_book_id", return_value="book-test"):
            book = Workspace("中文书名", "构想", [{"title": "一", "goal": "出发"}])
            def create(book_id, title, prompt, chapters, target):
                self.assertEqual(book_id, "book-test")
                save_checkpoint(book, Path(tmp) / book_id / "book.json")
            with patch("tome_agent.service.create_book", side_effect=create) as creator:
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
                app.text_input[0].set_value("中文书名")
                app.text_area[0].set_value("构想")
                app.checkbox[0].set_value(True)
                app.button[0].click().run()
                self.assertFalse(app.exception)
                creator.assert_called_once()
                self.assertEqual(app.selectbox[0].value, "book-test")
                self.assertIn("中文书名", app.selectbox[0].options)
