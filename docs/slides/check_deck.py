# -*- coding: utf-8 -*-
"""交付前自检：页数、越界、空文本、备注、原则覆盖。"""
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

P = Path(__file__).resolve().parent / "Tome-Agent_第一部分_产品设计与设计原则.pptx"
prs = Presentation(str(P))
W, H = prs.slide_width, prs.slide_height
print(f"slide size: {W/914400:.3f} x {H/914400:.3f} in, slides: {len(prs.slides)}")

problems = []
for i, s in enumerate(prs.slides, 1):
    boxes = 0
    for sh in s.shapes:
        if sh.width is None or sh.height is None:
            continue
        if sh.left < 0 or sh.top < 0 or sh.left + sh.width > W + Emu(1000) or sh.top + sh.height > H + Emu(1000):
            problems.append(f"p{i}: shape '{sh.shape_type}' out of bounds")
        if sh.has_text_frame and sh.text_frame.text.strip():
            boxes += 1
    notes = s.notes_slide.notes_text_frame.text.strip() if s.has_notes_slide else ""
    print(f"p{i:02d}: shapes={len(s.shapes):3d} text_shapes={boxes:2d} notes={len(notes):3d} chars")

print("\nout-of-bounds:", problems or "none")

# 原则覆盖检查
all_text = []
for s in prs.slides:
    for sh in s.shapes:
        if sh.has_text_frame:
            all_text.append(sh.text_frame.text)
        if sh.has_table:
            for r in sh.table.rows:
                for c in r.cells:
                    all_text.append(c.text)
blob = "".join(all_text)
must = ["需求原则", "信息原则", "创新原则", "系统原则", "收敛原则", "优化原则",
        "继承原则", "效益原则", "时间原则", "定量原则", "简化原则", "审核原则",
        "1.1.1 使命", "1.1.2 口号", "1.1.3 目标用户", "1.1.4 如何获得用户",
        "1.1.5 团队优势", "1.1.6 如何做到差异化", "1.2 产品定义", "1.2.1 解决的问题",
        "1.2.2 对客户的价值", "1.2.3 解决方案"]
missing = [m for m in must if m not in blob]
print("missing markers:", missing or "none")
