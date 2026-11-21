#!/usr/bin/env python3
"""合并三人分栏填写结果，并校验「不可编辑列」没有被改动。

用法（在任意目录执行均可）：
    python docs/software/user-test/merge.py

规则：
1. 以 `原始-用户测试表-学生版.md` 为权威底稿；如已存在 `用户测试表.md`，
   则以它为骨架（这样记录区、统计区、结论区的手工内容不会被覆盖）。
2. `parts/*.md` 里每个 33 题行按「编号」整行替换，不改行序、不改表头。
3. 校验「编号 / 问题 / 考察目标」三列与底稿逐字一致，任何一处被改都会中止合并，
   并指出是哪个文件、哪个题号、哪一列。
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASELINE = HERE / "原始-用户测试表-学生版.md"
PARTS_DIR = HERE / "parts"
OUTPUT = HERE / "用户测试表.md"

SECTIONS = {
    "P": ("产品价值", 5),
    "I": ("界面设计", 4),
    "V": ("视觉设计", 4),
    "H": ("通用可用性", 9),
    "A": ("智能体专项", 11),
}
ROW_RE = re.compile(r"^\|\s*([PIVHA]\d{1,2})\s*\|")
EDITABLE_START = 3  # 第 0、1、2 列（编号/问题/考察目标）不可改
TOTAL_COLUMNS = 7


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_rows(text: str, *, strict: bool = False) -> dict[str, tuple[str, list[str]]]:
    """按题号收集表格行。strict=True 时，列数不对的题号行直接报错（单元格里混入 | 的典型症状）。"""
    rows: dict[str, tuple[str, list[str]]] = {}
    bad: list[str] = []
    for line in text.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        parts = cells(line)
        if len(parts) != TOTAL_COLUMNS:  # 六/七/八节的短表不参与替换
            bad.append(f"{m.group(1)}（{len(parts)} 列，应为 {TOTAL_COLUMNS} 列）")
            continue
        rows[m.group(1)] = (line, parts)
    if strict and bad:
        fail("以下行被拆成了多列，通常是单元格里写了 |，请改成 ／：\n  - " + "\n  - ".join(bad))
    return rows


def expected_ids() -> list[str]:
    ids: list[str] = []
    for prefix, (_, count) in SECTIONS.items():
        ids.extend(f"{prefix}{i}" for i in range(1, count + 1))
    return ids


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(message: str) -> None:
    print(f"[失败] {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    baseline = read(BASELINE)
    base_rows = parse_rows(baseline)
    if set(base_rows) != set(expected_ids()):
        fail(f"底稿题号不完整：{sorted(set(expected_ids()) ^ set(base_rows))}")

    skeleton = read(OUTPUT) if OUTPUT.exists() else baseline
    skeleton_rows = parse_rows(skeleton)
    if set(skeleton_rows) != set(base_rows):
        fail(f"测试表与底稿题号不一致：{sorted(set(base_rows) ^ set(skeleton_rows))}")

    edited: dict[str, tuple[str, list[str], str]] = {}
    for part in sorted(PARTS_DIR.glob("*.md")):
        for rid, (line, cols) in parse_rows(read(part), strict=True).items():
            if rid in edited:
                fail(f"题号 {rid} 在 {edited[rid][2]} 和 {part.name} 中重复出现")
            edited[rid] = (line, cols, part.name)

    problems: list[str] = []
    for rid, (line, cols, part_name) in edited.items():
        base_cols = base_rows[rid][1]
        for index in range(EDITABLE_START):
            if cols[index] != base_cols[index]:
                name = ("编号", "问题", "考察目标")[index]
                problems.append(
                    f"{part_name} 的 {rid} 改了「{name}」列：\n"
                    f"    底稿：{base_cols[index]}\n"
                    f"    现状：{cols[index]}"
                )
    if problems:
        fail("不可编辑列被改动，未生成测试表：\n  - " + "\n  - ".join(problems))

    merged: list[str] = []
    used: set[str] = set()
    for line in skeleton.splitlines():
        m = ROW_RE.match(line)
        if m and len(cells(line)) == TOTAL_COLUMNS and m.group(1) in edited:
            line = edited[m.group(1)][0]
            used.add(m.group(1))
        merged.append(line)

    OUTPUT.write_text("\n".join(merged) + "\n", encoding="utf-8")

    # 摘要：哪些题已填「实测结果」、统计各维度计数
    stats: dict[str, Counter[str]] = {p: Counter() for p in SECTIONS}
    blanks: list[str] = []
    for rid in expected_ids():
        value = cells(edited[rid][0])[3] if rid in edited else ""
        stats[rid[0]][value or "（空）"] += 1
        if not value:
            blanks.append(rid)

    print(f"已合并 {len(used)} / {len(expected_ids())} 行 → {OUTPUT.name}")
    for prefix, (name, count) in SECTIONS.items():
        detail = "，".join(f"{k} {v}" for k, v in stats[prefix].items())
        print(f"  {name}（{count} 题）：{detail}")
    if blanks:
        print(f"  仍为空的题：{'、'.join(blanks)}")
    if len(used) < len(expected_ids()):
        print("  提示：未提供的题号沿用测试表/底稿中的原有内容。")


if __name__ == "__main__":
    main()
