"""Opt-in three-tier memory runtime; importing does not read credentials."""

import sys
from pathlib import Path

# ``inf_writer`` is a top-level package that lives both in
# ``code/core_engine/inf_writer`` and in ``memory_runtime/src/inf_writer``, and it
# is never installed as a distribution. Submodules of this package (and the
# ``python memory_runtime/test_*.py`` suites) import it by name, so the bundled
# copy must be importable as soon as this package is imported. Bootstrapping it
# here keeps every import block in the submodules at the top of its file (E402).
_SOURCE = Path(__file__).resolve().parent / "src"
if str(_SOURCE) not in sys.path:
    sys.path.insert(0, str(_SOURCE))
