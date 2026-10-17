import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from tome_agent.state import Workspace
from tome_agent.providers.deepseek import Settings


class WorkbenchTests(unittest.TestCase):
    def test_creation_screen_no_model_call(self):
        with patch("tome_agent.providers.deepseek.Settings.load", return_value=Settings("fake")), patch("tome_agent.service.list_books", return_value=[]):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
            self.assertFalse(app.exception)
            self.assertTrue(any(x.label == "生成分层大纲" for x in app.button))

    def test_existing_book_screen(self):
        book = Workspace("测试作品", "测试构想", [{"title": "开篇", "goal": "出发", "target_units": 100}])
        with patch("tome_agent.providers.deepseek.Settings.load", return_value=Settings("fake")), patch("tome_agent.service.list_books", return_value=["test-book"]), patch("tome_agent.checkpoints.load_checkpoint", return_value=book):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
            app.selectbox[0].select("test-book").run()
            self.assertFalse(app.exception)
            self.assertTrue(any(x.label == "开始续写" for x in app.button))
