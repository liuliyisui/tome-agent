# -*- coding: utf-8 -*-
"""代码统计口径自检：与 VS Code Counter 的 Files / Code / Comment / Blank 对齐。

用法（仓库根目录）：
    python docs/slides/count_lines.py              # 全仓库 .py/.js/.html/.css（排除依赖与构建产物）
    python docs/slides/count_lines.py --scope code # 只统计 code/ 与 tests/
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

EXTS = (".py", ".js", ".html", ".css")
COMMENT_PREFIX = ("#", "//", "/*", "*", '"""', "'''")


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines() if f.endswith(EXTS)]


def measure(paths: list[str]) -> dict[str, dict[str, int]]:
    stat: dict[str, dict[str, int]] = {}
    for f in paths:
        ext = Path(f).suffix.lower()
        row = stat.setdefault(ext, {"files": 0, "code": 0, "comment": 0, "blank": 0})
        row["files"] += 1
        for line in Path(f).read_text(encoding="utf-8", errors="ignore").splitlines():
            s = line.strip()
            if not s:
                row["blank"] += 1
            elif s.startswith(COMMENT_PREFIX):
                row["comment"] += 1
            else:
                row["code"] += 1
    return stat


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", choices=["all", "code"], default="all")
    args = ap.parse_args()

    files = tracked_files()
    if args.scope == "code":
        files = [f for f in files if f.startswith(("code/", "tests/"))]

    stat = measure(files)
    print(f"{'语言':<8}{'文件':>6}{'代码':>9}{'注释':>8}{'空行':>8}{'总行':>9}")
    tf = tc = tm = tb = 0
    for ext, v in sorted(stat.items(), key=lambda x: -x[1]["code"]):
        total = v["code"] + v["comment"] + v["blank"]
        print(f"{ext:<8}{v['files']:>6}{v['code']:>9}{v['comment']:>8}{v['blank']:>8}{total:>9}")
        tf += v["files"]
        tc += v["code"]
        tm += v["comment"]
        tb += v["blank"]
    print(f"{'合计':<8}{tf:>6}{tc:>9}{tm:>8}{tb:>8}{tc + tm + tb:>9}")
    print(f"\n口径：git 跟踪的 .py/.js/.html/.css；scope={args.scope}；"
          f"代码行 = 非空且非注释行（不含依赖、dist、.venv）")


if __name__ == "__main__":
    main()
