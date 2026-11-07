"""Measure unit and core writing coverage without putting artifacts in the root."""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "code" / "backend" / "data"
SOURCE = "code/backend/inf_backend,code/core_engine/inf_writer,code/core_engine/memory_runtime"
OMIT = "*/test_*,*/src/*"
CORE = ",".join(
    f"*/{path}"
    for path in (
        "memory_runtime/writing.py",
        "memory_runtime/event_first.py",
        "memory_runtime/pipeline.py",
        "memory_runtime/continuity.py",
        "memory_runtime/graph_runtime.py",
        "inf_writer/domain.py",
        "inf_writer/agents.py",
        "inf_writer/tiered_memory.py",
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
        ("单元测试：全部后端与引擎", unit_all),
        ("单元测试：核心模块", unit_core),
        ("单元测试 + 引擎回归：核心模块", combined),
    ):
        print(
            f"{title}: 综合 {data['percent_covered']:.2f}%（语句 {data['percent_statements_covered']:.2f}%，分支 {data['percent_branches_covered']:.2f}%）",
            flush=True,
        )
    if unit_core["percent_statements_covered"] < 60:
        raise SystemExit("核心模块单元测试语句覆盖率低于 60%")
    if combined["percent_covered"] < 60:
        raise SystemExit("核心模块综合覆盖率低于 60%")


if __name__ == "__main__":
    main()
