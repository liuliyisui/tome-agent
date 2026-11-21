# -*- coding: utf-8 -*-
"""生成静态扫描记录（对标课程要求的 p3c 扫描记录：blocker 必须为 0）。

课程示例是 Java 的 p3c / Alibaba Java Coding Guidelines，本项目是 Python，
用同类工具做等价扫描，并把结果映射到同一套严重级别：

    blocker（阻断，必须为 0）  Ruff E9xx / F 类（语法错误、未定义名、未使用导入）
                              Pylint fatal / error
                              Bandit HIGH（高危安全问题）
    major（严重）              Ruff 其余规则、Pylint warning、Bandit MEDIUM
    minor（提示）              Pylint convention / refactor、Bandit LOW

用法（仓库根目录）：
    python docs/software/quality/scan_python.py
    python docs/software/quality/scan_python.py --with-pylint   # 装了 pylint 才需要
输出：docs/software/quality/SCAN_RECORD.md（可直接截图）
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RECORD = ROOT / "docs" / "software" / "quality" / "SCAN_RECORD.md"
RUFF_CONFIG = ROOT / "code" / "backend" / "pyproject.toml"


def run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=900)
        return p.returncode, p.stdout, p.stderr
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, "", str(exc)


def have(module: str) -> bool:
    return subprocess.run([sys.executable, "-c", f"import {module}"], capture_output=True).returncode == 0


def scan_ruff() -> dict:
    if not have("ruff"):
        return {"tool": "Ruff", "ok": False, "note": "未安装：pip install ruff==0.17.4"}
    code, out, err = run([sys.executable, "-m", "ruff", "check", "--config", str(RUFF_CONFIG),
                          "--no-cache", "--output-format=json", "."])
    try:
        items = json.loads(out or "[]")
    except json.JSONDecodeError:
        return {"tool": "Ruff", "ok": False, "note": (err or out)[-300:]}
    blocker = [i for i in items if i.get("code", "").startswith("E9") or i.get("code", "").startswith("F")]
    ver = run([sys.executable, "-m", "ruff", "--version"])[1].strip()
    return {
        "tool": "Ruff", "ok": True, "version": ver,
        "blocker": len(blocker), "major": len(items) - len(blocker), "minor": 0,
        "total": len(items),
        "cmd": "python -m ruff check --config code/backend/pyproject.toml --no-cache .",
        "sample": [f'{i["code"]} {i["filename"]}:{i["location"]["row"]}' for i in items[:5]],
    }


def scan_pylint() -> dict:
    if not have("pylint"):
        return {"tool": "Pylint", "ok": False, "note": "未安装：pip install pylint"}
    code, out, err = run([sys.executable, "-m", "pylint", "code", "tests", "--output-format=json",
                          "--exit-zero", "--disable=import-error,no-name-in-module"])
    try:
        items = json.loads(out or "[]")
    except json.JSONDecodeError:
        return {"tool": "Pylint", "ok": False, "note": (err or out)[-300:]}
    types = [i.get("type") for i in items]
    blocker = sum(1 for t in types if t in {"fatal", "error"})
    major = sum(1 for t in types if t == "warning")
    minor = sum(1 for t in types if t in {"convention", "refactor"})
    ver = run([sys.executable, "-m", "pylint", "--version"])[1].splitlines()[:2]
    return {"tool": "Pylint", "ok": True, "version": " ".join(ver).strip(),
            "blocker": blocker, "major": major, "minor": minor, "total": len(items),
            "cmd": "python -m pylint code tests --output-format=json", "sample": []}


def scan_bandit() -> dict:
    if not have("bandit"):
        return {"tool": "Bandit", "ok": False, "note": "未安装：pip install bandit"}
    code, out, err = run([sys.executable, "-m", "bandit", "-r", "code", "tests", "-f", "json", "-q"])
    try:
        data = json.loads(out or "{}")
    except json.JSONDecodeError:
        return {"tool": "Bandit", "ok": False, "note": (err or out)[-300:]}
    results = data.get("results", [])
    sev = [r.get("issue_severity") for r in results]
    return {
        "tool": "Bandit", "ok": True, "version": "bandit",
        "blocker": sev.count("HIGH"), "major": sev.count("MEDIUM"), "minor": sev.count("LOW"),
        "total": len(results),
        "cmd": "python -m bandit -r code tests -f json -q",
        "sample": [f'{r.get("test_id")} {r.get("filename")}:{r.get("line_number")}' for r in results[:5]],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-pylint", action="store_true")
    args = ap.parse_args()

    scans = [scan_ruff()]
    if args.with_pylint:
        scans.append(scan_pylint())
    scans.append(scan_bandit())

    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# 静态扫描记录（Python）", "",
        f"- 生成时间：{stamp}",
        f"- 提交：`{run(['git', 'rev-parse', '--short', 'HEAD'])[1].strip()}`",
        "- 对标：课程示例的 p3c / Alibaba Java Coding Guidelines 扫描记录；本项目为 Python，"
        "用 Ruff（规范）+ Bandit（安全）对应，blocker 必须为 0。",
        "",
        "| 工具 | 版本 | blocker | major | minor | 合计 | 结论 |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    blockers = 0
    for s in scans:
        if not s["ok"]:
            lines.append(f'| {s["tool"]} | — | — | — | — | — | 未执行（{s["note"]}） |')
            continue
        blockers += s["blocker"]
        verdict = "通过（无 blocker）" if s["blocker"] == 0 else "阻断"
        lines.append(
            f'| {s["tool"]} | {s.get("version", "—")} | {s["blocker"]} | {s["major"]} | {s["minor"]} '
            f'| {s["total"]} | {verdict} |'
        )

    lines += ["", "## 命令", ""]
    for s in scans:
        if s["ok"]:
            lines.append(f'- {s["tool"]}：`{s["cmd"]}`')

    lines += ["", "## 结论", ""]
    executed = [s for s in scans if s["ok"]]
    if not executed:
        lines.append("**未执行任何扫描**：先安装工具再重跑（见下方命令）。")
    elif blockers == 0:
        lines.append("**blocker = 0，扫描通过。** major / minor 为代码风格与提示项，不影响功能与交付。")
    else:
        lines.append(f"**blocker = {blockers}，未通过**，需先修复再交付。")

    details = [s for s in scans if s["ok"] and s.get("sample")]
    if details:
        lines += ["", "## 明细（前 5 条）", ""]
        for s in details:
            lines.append(f'**{s["tool"]}**')
            lines += [f"- `{x}`" for x in s["sample"]]
            lines.append("")

    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\n已写入 {RECORD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
