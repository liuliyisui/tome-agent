"""Offline launcher regression, with unavailable historical assets explicit.

Run separately from the fast application suite:
    python tests/run_engine_regression.py
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / 'code' / 'core_engine'
sys.path.insert(0, str(CORE))


def suite():
    # The upstream tests create disposable run folders under this directory.
    (CORE / 'runs').mkdir(exist_ok=True)
    from memory_runtime.test_writing import WritingIntegration
    from memory_runtime.test_completion import CompletionTests
    from memory_runtime.test_stage_repair import StageRepairTests
    unavailable = {
        'test_actual_chapter_eleven_review_reference_replays_without_changing_rejection':
            'runs/writing_tiered_30000_20261021_a/final_state.json',
        'test_actual_ap_chapter_fifteen_input_overflow_continues_without_mutating_old_run':
            'runs/event_first_50000_20261023_ap',
        'test_original_ar_intention_failure_now_passes_without_manual_scope_change':
            'runs/event_first_50000_20261023_ar',
    }
    result = unittest.TestSuite()
    loader = unittest.TestLoader()
    for cls in (WritingIntegration, CompletionTests, StageRepairTests):
        for name in loader.getTestCaseNames(cls):
            asset = unavailable.get(name)
            if asset and not (CORE / asset).exists():
                original = getattr(cls, name)
                setattr(cls, name, unittest.skip('Historical fixture not supplied: ' + asset)(original))
            result.addTest(cls(name))
    return result


if __name__ == '__main__':
    outcome = unittest.TextTestRunner(verbosity=2).run(suite())
    sys.exit(not outcome.wasSuccessful())
