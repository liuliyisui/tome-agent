# -*- coding: utf-8 -*-
"""统计 AI 辅助 / 团队自写代码比例（基于提交与人工标注）。

用法：
    python docs/slides/ai_ratio.py                      # 只看提交分解
    python docs/slides/ai_ratio.py --make-labels        # 生成待标注的 ai-labels.csv（按新增行数排序）
    python docs/slides/ai_ratio.py --labels docs/slides/ai-labels.csv   # 按标注算比例

标注方法：在 ai-labels.csv 的 ai_assisted 列填 yes / no，留空表示未标注。
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
from pathlib import Path

EXCLUDE = re.compile(r"format|quality|ruff|lint|style|migrat|revert|docs|chore|rename|清理|格式化", re.I)
FEATURE = re.compile(r"feat|add|implement|support|新增|实现|支持|引入|重写|redesign|upgrade", re.I)


def commits() -> list[dict]:
    out = subprocess.run(
        ["git", "log", "--no-merges", "--numstat", "--pretty=format:__C__%h|%an|%s"],
        capture_output=True, text=True, encoding="utf-8", errors="ignore",
    ).stdout
    items: list[dict] = []
    cur = None
    for line in out.splitlines():
        if line.startswith("__C__"):
            h, author, subject = line[5:].split("|", 2)
            cur = {"hash": h, "author": author, "subject": subject, "added": 0, "deleted": 0, "files": 0}
            items.append(cur)
        elif line.strip() and cur is not None:
            parts = line.split("\t")
            if len(parts) == 3 and parts[0].isdigit():
                cur["added"] += int(parts[0])
                cur["deleted"] += int(parts[1])
                cur["files"] += 1
    return items


def bucket(c: dict) -> str:
    if EXCLUDE.search(c["subject"]):
        return "格式化 / 迁移 / 文档"
    if FEATURE.search(c["subject"]):
        return "功能开发"
    return "修复 / 重构 / 其他"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", type=Path, help="标注过的 ai-labels.csv")
    ap.add_argument("--make-labels", action="store_true", help="生成待标注 CSV")
    ap.add_argument("--top", type=int, default=30)
    args = ap.parse_args()

    items = commits()
    total = sum(c["added"] for c in items)

    if args.make_labels:
        target = Path("docs/slides/ai-labels.csv")
        rows = sorted(items, key=lambda c: -c["added"])[: args.top]
        with target.open("w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["hash", "author", "added", "deleted", "files", "subject", "ai_assisted"])
            for c in rows:
                w.writerow([c["hash"], c["author"], c["added"], c["deleted"], c["files"], c["subject"], ""])
        cover = sum(c["added"] for c in rows) / total if total else 0
        print(f"已生成 {target}（{len(rows)} 条，覆盖新增行 {cover:.0%}）；填 yes/no 后重跑 --labels")
        return

    groups: dict[str, list[dict]] = {}
    for c in items:
        groups.setdefault(bucket(c), []).append(c)

    print(f"提交 {len(items)} 次，新增 {total:,} 行")
    for name, cs in sorted(groups.items(), key=lambda kv: -sum(c["added"] for c in kv[1])):
        adds = sum(c["added"] for c in cs)
        print(f"  {name:<18}{len(cs):>4} 次   +{adds:>8,} 行   ({adds / total:.0%})")

    if not args.labels:
        return

    with args.labels.open(encoding="utf-8-sig") as fh:
        labelled = [r for r in csv.DictReader(fh) if r["ai_assisted"].strip()]
    ai = sum(int(r["added"]) for r in labelled if r["ai_assisted"].strip().lower() in {"yes", "y", "1", "ai"})
    human = sum(int(r["added"]) for r in labelled if r["ai_assisted"].strip().lower() in {"no", "n", "0"})
    covered = ai + human
    print(f"\n已标注 {len(labelled)} 条，覆盖新增 {covered:,} 行（{covered / total:.0%}）")
    if covered:
        print(f"  AI 辅助：{ai:,} 行（{ai / covered:.0%}）")
        print(f"  人工自写/改写：{human:,} 行（{human / covered:.0%}）")


if __name__ == "__main__":
    main()
