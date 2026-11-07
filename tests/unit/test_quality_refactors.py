"""Regression tests for the five refactors in ``docs/software/quality/QUALITY_REPORT.md``.

Four of these tests fail on the pre-refactor baseline (commit ``e4d23ce``) and
pass after the refactor; the fifth pins behaviour the refactor had to preserve.

    python -m unittest tests.unit.test_quality_refactors -v
"""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from inf_backend import migrate, service
from inf_writer.domain import ContractError
from inf_writer.narrative_context import parse_planner_json
from memory_runtime import continuity
from memory_runtime.identifiers import attribute_identifier

REPO = pathlib.Path(__file__).resolve().parents[2]


class RaiseChainTests(unittest.TestCase):
    """Refactor 1 — Pylint W0707 / Ruff B904: an exception raised while handling
    another one must declare whether it was caused by it."""

    def test_longform_pointer_error_keeps_contract_error_as_cause(self):
        pointer = mock.Mock()
        pointer.read_text.return_value = json.dumps({"checkpoint": 1, "extra": 2})
        with (
            mock.patch.object(service.database, "enabled", return_value=False),
            mock.patch.object(service, "_metadata", return_value={"title": "t"}),
            mock.patch.object(service, "_longform_plan", return_value={}),
            mock.patch.object(
                service,
                "_load_longform_book",
                side_effect=ContractError("写作运行时版本不一致，不能直接恢复旧检查点"),
            ),
            mock.patch.object(service, "_longform_pointer", return_value=pointer),
        ):
            with self.assertRaises(ValueError) as caught:
                service.load_longform("book-1")

        self.assertIsInstance(caught.exception.__cause__, ContractError)

    def test_migrate_failure_suppresses_the_underlying_exception(self):
        with mock.patch.object(sys, "argv", ["migrate", "reconcile", "--apply"]):
            with self.assertRaises(SystemExit) as caught:
                migrate.main()

        self.assertTrue(caught.exception.__suppress_context__)

    def test_planner_json_recovery_does_not_leak_the_parser_error(self):
        with self.assertRaises(ContractError) as caught:
            parse_planner_json('{"a": 1} trailing text')

        # The recovery attempt must not expose the JSON parser's exception: the
        # caller only needs the contract-level error and the recovery notes.
        self.assertIsNone(caught.exception.__cause__)
        self.assertTrue(caught.exception.__suppress_context__)


class LoopClosureTests(unittest.TestCase):
    """Refactor 2 — Pylint W0640: the per-record error payload must describe the
    row as it is at the moment of failure, not a stale pre-normalised copy."""

    def test_continuity_error_reports_the_normalised_attribute(self):
        prose = "甲看见了门外的信。"
        base = {
            "type": "fact",
            "subject": "甲",
            "attribute": "当前位置",
            "value": "门外",
            "kind": "state",
            "quote": prose,
        }
        first = dict(base, id="f_position_a")
        duplicate = dict(base, id="f_position_b", value="屋内")

        with self.assertRaises(continuity.ContinuityError) as caught:
            continuity.apply(continuity.empty(), [first, duplicate], prose, 1)

        proposed = caught.exception.repair_details["proposed"]
        self.assertEqual(proposed["attribute"], attribute_identifier("当前位置"))
        self.assertNotEqual(proposed["attribute"], "当前位置")


class ImportBootstrapTests(unittest.TestCase):
    """Refactor 4 — Pylint C0413 / Ruff E402: importing the package itself must
    expose the bundled ``inf_writer``, so no submodule needs a mid-file
    ``sys.path`` insert before its imports."""

    def test_importing_memory_runtime_exposes_the_bundled_inf_writer(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            [str(REPO / "code/core_engine"), str(REPO / "code/backend")]
        )
        probe = (
            "import sys, memory_runtime;"
            "print(int(any(p.replace('\\\\', '/').endswith('memory_runtime/src')"
            " for p in sys.path)))"
        )
        outcome = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=str(REPO),
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(outcome.stdout.strip(), "1", outcome.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
