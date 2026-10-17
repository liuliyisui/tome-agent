"""Unit tests."""

import sys
from pathlib import Path

# Sources live in code/core_engine and code/backend. Make them importable even
# when the runner does not provide PYTHONPATH (e.g. GitHub Actions).
_ROOT = Path(__file__).resolve().parents[2]
for _name in ("core_engine", "backend"):
    _path = str(_ROOT / "code" / _name)
    if _path not in sys.path:
        sys.path.insert(0, _path)
