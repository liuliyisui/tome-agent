"""Package grouping must preserve both import entrances and checkpoint identity."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_memory import source_hashes
from tome_writer.domain import ContractError


class WriterLayoutTests(unittest.TestCase):
    def test_imports_work_in_both_orders(self):
        core = Path(__file__).resolve().parents[2] / "code" / "core_engine"
        self.assertFalse((core / "memory_runtime" / "src").exists())
        script = """
import importlib, pathlib, sys
core = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(core))
if sys.argv[2] == 'memory-first':
    import memory_runtime
for name, group in [('chat_provider', 'model_io'), ('agents', 'writing_flow'), ('tiered_memory', 'memory_system'), ('review_policy', 'review_system'), ('domain', 'foundation')]:
    module = importlib.import_module('tome_writer.' + name)
    assert pathlib.Path(module.__file__).parent.name == group, module.__file__
"""
        for entry in ("canonical", "memory-first"):
            with self.subTest(entry=entry):
                subprocess.run(
                    [sys.executable, "-c", script, str(core), entry], check=True
                )

    def test_ambiguous_shared_module_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for group in ("model_io", "writing_flow"):
                path = root / "tome_writer" / group
                path.mkdir(parents=True)
                (path / "duplicate.py").write_text("pass\n", encoding="utf-8")
            (root / "memory_runtime").mkdir()
            with patch("check_memory.ROOT", root), self.assertRaises(ContractError):
                source_hashes()
