"""Measure unit and core writing coverage without putting artifacts in the root."""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "code" / "backend" / "data"
SOURCE = "code/backend/inf_backend,code/core_engine/tome_writer,code/core_engine/memory_runtime"
OMIT = "*/test_*,*/src/*"
CORE = ",".join(
    f"*/{path}"
    for path in (
        "memory_runtime/writing_flow/writing.py",
        "memory_runtime/events/event_first.py",
        "memory_runtime/memory_processing/pipeline.py",
        "memory_runtime/events/continuity.py",
        "memory_runtime/writing_flow/graph_runtime.py",
        "tome_writer/foundation/domain.py",
        "tome_writer/writing_flow/agents.py",
        "tome_writer/memory_system/tiered_memory.py",
    )
)


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        (str(ROOT / "code/core_engine"), str(ROOT / "code/backend"))
    )
    env["DATABASE_URL"] = ""
    env["COVERAGE_FILE"] = str(DATA / ".coverage-assignment")
    python = [sys.executable, "-m", "coverage"]
    common = ["--branch", f"--source={SOURCE}", f"--omit={OMIT}"]

    def run(*args):
        subprocess.run([*python, *args], cwd=ROOT, env=env, check=True)

    def snapshot(name, include=None):
        path = DATA / f"coverage-{name}.json"
        args = ["json", "-o", str(path)]
        if include:
            args.append(f"--include={include}")
        run(*args)
        return json.loads(path.read_text(encoding="utf-8"))["totals"]

    run("run", *common, "-m", "pytest", "-p", "no:cacheprovider", "-q", "tests/unit")
    unit_all = snapshot("unit-all")
    unit_core = snapshot("unit-core", CORE)
    run("run", "-a", *common, "tests/run_engine_regression.py")
    combined = snapshot("core-combined", CORE)
    for title, data in (
        ("Unit tests: backend and engine", unit_all),
        ("Unit tests: core modules", unit_core),
        ("Unit and engine regression tests: core modules", combined),
    ):
        print(
            f"{title}: total {data['percent_covered']:.2f}% (statements {data['percent_statements_covered']:.2f}%, branches {data['percent_branches_covered']:.2f}%)",
            flush=True,
        )
    if unit_core["percent_statements_covered"] < 60:
        raise SystemExit("Core unit test statement coverage is below 60%")
    if combined["percent_covered"] < 60:
        raise SystemExit("Core combined coverage is below 60%")


if __name__ == "__main__":
    main()
