"""Test-only adapter for event proposals recorded before formal validation."""

import copy

from memory_runtime.event_contract import validate_plan_shape


def compile_archived_plan(proposal, choices, chapter, **kwargs):
    """Validate archived event shapes and preserve their assigned IDs."""
    validate_plan_shape(proposal)
    return copy.deepcopy(proposal)
