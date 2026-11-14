"""Tome Agent's multi-agent writing foundation."""

__version__ = "0.1.0"

from pathlib import Path

# Preserve the public tome_writer.<module> imports after classifying sources.
for _group in (
    "model_io",
    "writing_flow",
    "memory_system",
    "review_system",
    "foundation",
):
    __path__.append(str(Path(__file__).resolve().parent / _group))
