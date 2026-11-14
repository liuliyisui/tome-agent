"""The reviewed layout change retains old fingerprints and rejects tampering."""

import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_memory import _source_hashes_compatible, source_hashes
from memory_runtime import test_completion, test_stage_repair
from tome_writer.domain import ContractError


class MemoryLayoutTests(unittest.TestCase):
    def test_model_provider_supports_both_import_orders(self):
        core = Path(__file__).resolve().parents[2] / "code" / "core_engine"
        for first in ("memory_runtime", "tome_writer"):
            with self.subTest(first=first):
                program = (
                    "import sys,inspect; sys.path.insert(0,sys.argv[1]); "
                    "__import__(sys.argv[2]); "
                    "from tome_writer.chat_provider import ChatCompletionProvider; "
                    "assert 'token_limit_field' in inspect.signature(ChatCompletionProvider).parameters"
                )
                subprocess.run(
                    [sys.executable, "-c", program, str(core), first], check=True
                )

    def test_runtime_modules_are_grouped_and_keep_original_imports(self):
        from memory_runtime import (
            continuity,
            engine,
            narrative_planning,
            numeric_grounding,
            writing,
        )

        for module, group in (
            (writing, "writing_flow"),
            (engine, "memory_processing"),
            (continuity, "events"),
            (narrative_planning, "planning_review"),
            (numeric_grounding, "support"),
        ):
            with self.subTest(module=module.__name__):
                self.assertEqual(Path(module.__file__).parent.name, group)
                self.assertTrue(module.__name__.startswith("memory_runtime."))

    def test_original_import_names_remain_available(self):
        self.assertEqual(
            test_completion.CompletionTests.__module__, "memory_runtime.test_completion"
        )
        self.assertEqual(
            test_stage_repair.StageRepairTests.__module__,
            "memory_runtime.test_stage_repair",
        )

    def test_reviewed_previous_fingerprints_and_tampering(self):
        current = source_hashes()
        previous = copy.deepcopy(current)
        previous["__init__.py"] = (
            "975bd3f06cd496a8bd99d99467758577b900f26dbeedaa777540bf6a5cf7033e"
        )
        previous["writing.py"] = (
            "4dfe525d3bd41eb370a9aa1399685a2aa157e7ff7199493dc697475c8391a2ee"
        )
        self.assertTrue(_source_hashes_compatible(previous, current))
        previous["test_completion.py"] = "unexpected"
        self.assertFalse(_source_hashes_compatible(previous, current))

    def test_duplicate_logical_source_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            runtime = root / "memory_runtime"
            classified = runtime / "regression_tests"
            classified.mkdir(parents=True)
            (runtime / "test_duplicate.py").write_text("first", encoding="utf-8")
            (classified / "test_duplicate.py").write_text("second", encoding="utf-8")
            with patch("check_memory.ROOT", root), self.assertRaises(ContractError):
                source_hashes()


if __name__ == "__main__":
    unittest.main()
