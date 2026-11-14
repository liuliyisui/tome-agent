"""Opt-in three-tier memory runtime; importing does not read credentials."""

from pathlib import Path

# Preserve existing ``memory_runtime.test_*`` imports after classifying tests.
_REGRESSION_TESTS = Path(__file__).resolve().parent / "regression_tests"
if _REGRESSION_TESTS.is_dir():
    __path__.append(str(_REGRESSION_TESTS))

# Keep the original memory_runtime module names while grouping implementation files.
for _group in (
    "writing_flow",
    "memory_processing",
    "events",
    "planning_review",
    "support",
):
    __path__.append(str(Path(__file__).resolve().parent / _group))
