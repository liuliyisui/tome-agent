import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import streamlit as st
from streamlit.testing.v1 import AppTest
from tome_agent.state import Workspace
from tome_agent.providers.deepseek import Settings


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        st.cache_data.clear()

    def test_creation_screen_no_model_call(self):
        with patch("tome_agent.providers.deepseek.Settings.load", return_value=Settings("fake")), patch("tome_agent.service.list_books", return_value=[]):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
            self.assertFalse(app.exception)
            self.assertTrue(any(x.label == "生成分层大纲" for x in app.button))
            self.assertEqual([x.label for x in app.text_input], ["作品名称"])

    def test_existing_book_screen(self):
        book = Workspace("测试作品", "测试构想", [{"title": "开篇", "goal": "出发", "target_units": 100}])
        with patch("tome_agent.providers.deepseek.Settings.load", return_value=Settings("fake")), patch("tome_agent.service.list_books", return_value=["test-book"]), patch("tome_agent.checkpoints.load_checkpoint", return_value=book):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
            app.selectbox[0].select("test-book").run()
            self.assertFalse(app.exception)
            self.assertTrue(any(x.label == "开始续写" for x in app.button))

    def test_memory_lists_and_json_toggles(self):
        book = Workspace("测试作品", "构想", [{"title": "开篇", "goal": "出发"}])
        book.state.future_requirements = {
            "find_sender": {"description": "寻找寄信人", "resolved": False},
            "open_letter": {"description": "打开信件", "resolved": True, "resolved_chapter": 1}}
        book.state.facts = {"fact": {"subject": "林舟", "key": "location", "value": "灯塔",
            "revision": 1, "category": "behavior_constraint", "epistemic_status": "objective",
            "status": "active", "evidence": {"chapter": 1}}}
        with patch("tome_agent.providers.deepseek.Settings.load", return_value=Settings("fake")), patch("tome_agent.service.list_books", return_value=["memory-book"]), patch("tome_agent.checkpoints.load_checkpoint", return_value=book):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
            app.selectbox[0].select("memory-book").run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.json), 0)
            self.assertEqual(len(app.dataframe), 1)
            self.assertIn("出处", app.dataframe[0].value.columns)
            self.assertTrue(any("待完成" in x.value for x in app.markdown))
            self.assertTrue(any(x.label == "已完成义务（1）" for x in app.expander))
            self.assertTrue(any("第1章完成" in x.value for x in app.text))
            app.toggle[0].set_value(True).run()
            self.assertEqual(len(app.json), 1)
            app.toggle[1].set_value(True).run()
            self.assertEqual(len(app.json), 3)

    def test_export_cache_uses_displayed_snapshot_and_refreshes(self):
        from tome_agent.service import export_markdown
        book = Workspace("导出测试", "构想", [{"title": "开篇", "goal": "出发"}])
        newer = deepcopy(book)
        newer.chapters = {1: "已更新的正文"}
        with patch("tome_agent.providers.deepseek.Settings.load", return_value=Settings("fake")), patch("tome_agent.service.list_books", return_value=["export-book"]), patch("tome_agent.checkpoints.load_checkpoint", return_value=book) as loader, patch("tome_agent.service.export_markdown", wraps=export_markdown) as exporter:
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
            app.selectbox[0].select("export-book").run()
            self.assertFalse(app.exception)
            self.assertEqual(loader.call_count, 1)
            self.assertEqual(exporter.call_count, 1)
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(exporter.call_count, 1)
            loader.return_value = newer
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(exporter.call_count, 2)
            self.assertEqual(exporter.call_args.args[0].chapters, newer.chapters)

    def test_failed_checkpoint_read_has_no_export(self):
        with patch("tome_agent.providers.deepseek.Settings.load", return_value=Settings("fake")), patch("tome_agent.service.list_books", return_value=["missing-book"]), patch("tome_agent.checkpoints.load_checkpoint", side_effect=FileNotFoundError), patch("tome_agent.service.export_markdown") as exporter:
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
            app.selectbox[0].select("missing-book").run()
            self.assertFalse(app.exception)
            self.assertTrue(app.error)
            exporter.assert_not_called()
