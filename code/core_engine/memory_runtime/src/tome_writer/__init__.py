"""Compatibility entry point for the shared multi-agent writing package."""

from pathlib import Path

__version__ = "0.1.0"

# The historical runtime entry point shares the canonical package modules.
_SHARED_PACKAGE = Path(__file__).resolve().parents[3] / "tome_writer"
if _SHARED_PACKAGE.is_dir():
    __path__.append(str(_SHARED_PACKAGE))

    for _group in (
        "model_io",
        "writing_flow",
        "memory_system",
        "review_system",
        "foundation",
    ):
        __path__.append(str(_SHARED_PACKAGE / _group))
