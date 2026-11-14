import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from inf_backend import service
from tome_writer.models import ModelRequest


class SkillTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        for name, value in (("DATA", root), ("BOOKS", root / "books")):
            p = patch.object(service, name, value)
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(service, "BUILTIN_SKILLS", root / "builtin")
        p.start()
        self.addCleanup(p.stop)
        p = patch.object(service, "_metadata", return_value={})
        p.start()
        self.addCleanup(p.stop)
        p = patch.object(service.database, "enabled", return_value=False)
        p.start()
        self.addCleanup(p.stop)

    def test_install_and_per_book_selection_persist(self):
        first = service.install_skill("悬疑", "---\nname: suspense\n---\n缓慢揭示线索")
        second = service.install_skill("对白", "对白自然")
        self.assertEqual(service.list_skills(), [first, second])
        service.save_book_skills("book-a", [first["id"]])
        self.assertEqual(service.load_book_skills("book-a"), [first["id"]])
        self.assertEqual(service.load_book_skills("book-b"), [])
        service.save_book_skills("book-a", [])
        self.assertEqual(service.load_book_skills("book-a"), [])
        with self.assertRaises(ValueError):
            service.save_book_skills("book-a", ["unknown"])
        with self.assertRaises(ValueError):
            service.install_skill("x", "x" * 12001)

    def test_builtin_skills_load_without_install_and_keep_existing_ids(self):
        service.BUILTIN_SKILLS.mkdir()
        (service.BUILTIN_SKILLS / "内置.md").write_text("内置写法", encoding="utf-8")
        builtin = service.list_skills()[0]
        self.assertTrue(builtin["id"].startswith("builtin-"))
        self.assertEqual(service.list_skills()[0]["id"], builtin["id"])
        self.assertFalse((service.DATA / "skills.json").exists())
        item = service.install_skill("已有技能", "内置写法")
        self.assertEqual(service.list_skills(), [item])
        service.save_book_skills("book-a", [item["id"]])
        self.assertEqual(service.load_book_skills("book-a"), [item["id"]])

    def test_repository_builtins_are_available_to_fresh_install(self):
        root = (
            Path(__file__).resolve().parents[2]
            / "code"
            / "core_engine"
            / "writing_skills"
        )
        with patch.object(service, "BUILTIN_SKILLS", root):
            names = {skill["name"] for skill in service.list_skills()}
        self.assertEqual(
            names,
            {
                "去AI味·自然化重写",
                "网文工坊·通用写作指令",
                "章末钩子与爽点",
                "长篇结构·节奏与连续性",
            },
        )

    def test_only_writer_receives_selected_skill(self):
        inner = Mock()
        skills = [{"id": "one", "name": "悬疑", "content": "缓慢揭示线索"}]
        gateway = service.SkillGateway(inner, skills)
        writer = ModelRequest("writer", "保持原格式", {"chapter": 1})
        gateway.complete(writer)
        forwarded = inner.complete.call_args.args[0]
        self.assertEqual(forwarded.payload["writing_skills"], skills)
        self.assertNotIn("writing_skills", writer.payload)
        planner = ModelRequest("planner", "规划", {})
        gateway.complete(planner)
        self.assertIs(inner.complete.call_args.args[0], planner)

    def test_generation_loads_selection_and_records_skill_hash(self):
        item = service.install_skill("悬疑", "逐步揭示线索")
        service.save_book_skills("book-a", [item["id"]])
        captured = Mock()
        config = Mock()
        config.public_config.return_value = {"model": "demo"}
        meta = {
            "title": "测试",
            "target_chapters": 1,
            "target_units": 1000,
            "model": {"model": "demo"},
        }

        class FakeSession:
            def __init__(self, output, gateway, plan, book=None):
                self.output = output
                self.output.mkdir(parents=True)
                self.gateway = gateway
                self.book = {"chapters": []}
                self.latest_checkpoint = output / "checkpoint.json"
                self.latest_checkpoint.write_text("{}", encoding="utf-8")

            def write_next(self, instruction):
                self.gateway.complete(ModelRequest("writer", "写作", {}))
                self.book["chapters"].append(
                    {"number": 1, "title": "第一章", "text": "正文"}
                )
                return {"status": "DRAFT_UNCHECKED"}

        with (
            patch.object(service, "_metadata", return_value=meta),
            patch.object(service, "_longform_plan", return_value={}),
            patch.object(service, "_load_longform_book", return_value=None),
            patch.object(service, "WritingSession", FakeSession),
        ):
            service.generate_longform("book-a", gateway=captured, settings=config)
        forwarded = captured.complete.call_args.args[0]
        self.assertEqual(forwarded.payload["writing_skills"], [item])
        runs = list(
            (service.book_path("book-a") / "longform-runs").glob("*/skills-used.json")
        )
        self.assertEqual(len(runs), 1)
        self.assertIn(item["id"], runs[0].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
