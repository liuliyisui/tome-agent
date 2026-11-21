# -*- coding: utf-8 -*-
"""生成 Tome Agent 汇报幻灯片（第一部分 1、2 小节）。

运行：python slides/build_deck.py
输出：slides/Tome-Agent_第一部分_产品设计与设计原则.pptx
"""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
OUT = HERE / "Tome-Agent_第一部分_产品设计与设计原则.pptx"

# ---------------------------------------------------------------- 视觉规范
FONT = "微软雅黑"
MONO = "Consolas"

INK = RGBColor(0x1D, 0x2B, 0x3A)
INK_SOFT = RGBColor(0x3B, 0x49, 0x59)
MUTED = RGBColor(0x6C, 0x77, 0x84)
PRIMARY = RGBColor(0x1B, 0x3B, 0x5F)
PRIMARY_L = RGBColor(0x2E, 0x58, 0x86)
ACCENT = RGBColor(0xB4, 0x47, 0x2E)
PAPER = RGBColor(0xFB, 0xF8, 0xF2)
CARD = RGBColor(0xF2, 0xEC, 0xE1)
CARD_SOFT = RGBColor(0xF6, 0xF2, 0xE9)
LINE = RGBColor(0xDA, 0xD2, 0xC6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

W, H = 13.333, 7.5
ML, MR = 0.85, 0.85
CW = W - ML - MR  # 11.633

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)
BLANK = prs.slide_layouts[6]

FOOTER = "Tome Agent · 创新工程实践营项目汇报 · 第一部分"
TOTAL = 17


# ---------------------------------------------------------------- 基础工具
def new_slide(bg: RGBColor = PAPER):
    s = prs.slides.add_slide(BLANK)
    shape = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg
    shape.line.fill.background()
    shape.shadow.inherit = False
    return s


def tb(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    tf.paragraphs[0].text = ""
    return tf


def para(tf, text="", size=12, color=INK, bold=False, font=FONT,
         align=PP_ALIGN.LEFT, space_before=0, space_after=4, line=1.32,
         first=False, italic=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.space_after = Pt(space_after)
    p.line_spacing = line
    if text:
        r = p.add_run()
        r.text = text
        f = r.font
        f.name = font
        f.size = Pt(size)
        f.bold = bold
        f.italic = italic
        f.color.rgb = color
        # 中文字形需要显式设置 east-asian 字体
        rPr = r._r.get_or_add_rPr()
        ea = rPr.find(qn("a:ea"))
        if ea is None:
            ea = rPr.makeelement(qn("a:ea"), {})
            rPr.append(ea)
        ea.set("typeface", font)
    return p


def rich(p, parts, size=12, color=INK):
    """parts: [(text, {size/bold/color/font})]"""
    for text, style in parts:
        r = p.add_run()
        r.text = text
        f = r.font
        f.name = style.get("font", FONT)
        f.size = Pt(style.get("size", size))
        f.bold = style.get("bold", False)
        f.color.rgb = style.get("color", color)
        rPr = r._r.get_or_add_rPr()
        ea = rPr.find(qn("a:ea"))
        if ea is None:
            ea = rPr.makeelement(qn("a:ea"), {})
            rPr.append(ea)
        ea.set("typeface", f.name)
    return p


def card(slide, x, y, w, h, fill=CARD, radius=0.06, line_color=None):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.adjustments[0] = radius
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line_color is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(1)
    shape.shadow.inherit = False
    return shape


def bar(slide, x, y, w, h, color=ACCENT):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def hairline(slide, x, y, w, color=LINE):
    return bar(slide, x, y, w, 0.012, color)


def header(slide, eyebrow, title, num, note=None):
    tf = tb(slide, ML, 0.46, 7.2, 0.28)
    para(tf, eyebrow, size=10.5, color=ACCENT, bold=True, first=True, space_after=0)
    tf = tb(slide, ML, 0.74, CW, 0.7)
    para(tf, title, size=26, color=INK, bold=True, first=True, space_after=0)
    hairline(slide, ML, 1.55, CW)
    # 页码
    tf = tb(slide, W - MR - 1.0, H - 0.42, 1.0, 0.24)
    para(tf, f"{num:02d} / {TOTAL}", size=9, color=MUTED, align=PP_ALIGN.RIGHT, first=True, space_after=0)
    # 页脚
    tf = tb(slide, ML, H - 0.42, 7.6, 0.24)
    para(tf, FOOTER, size=9, color=MUTED, first=True, space_after=0)
    if note:
        tf = tb(slide, W - MR - 5.0, H - 0.42, 3.9, 0.24)
        para(tf, note, size=8.5, color=MUTED, align=PP_ALIGN.RIGHT, first=True, space_after=0)


def plain_table(slide, x, y, w, col_widths, rows, header_fill=PRIMARY,
                size=9.5, header_size=9.5, row_h=0.5, header_h=0.42,
                first_col_bold=True, zebra=CARD_SOFT):
    """rows[0] 为表头。单元格文本支持 str。"""
    n_rows, n_cols = len(rows), len(rows[0])
    shape = slide.shapes.add_table(
        n_rows, n_cols, Inches(x), Inches(y), Inches(w), Inches(header_h + row_h * (n_rows - 1))
    )
    table = shape.table
    tbl = table._tbl
    tblPr = tbl.tblPr
    for el in tblPr.findall(qn("a:tableStyleId")):
        tblPr.remove(el)
    style = tblPr.makeelement(qn("a:tableStyleId"), {})
    style.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"  # No Style, No Grid
    tblPr.append(style)

    for i, cw in enumerate(col_widths):
        table.columns[i].width = Inches(cw)
    table.rows[0].height = Inches(header_h)
    for r in range(1, n_rows):
        table.rows[r].height = Inches(row_h)

    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.margin_left = Inches(0.09)
            cell.margin_right = Inches(0.07)
            cell.margin_top = Inches(0.03)
            cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if r == 0:
                cell.fill.fore_color.rgb = header_fill
            elif r % 2 == 0 and zebra is not None:
                cell.fill.fore_color.rgb = zebra
            else:
                cell.fill.fore_color.rgb = PAPER
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.space_before = Pt(0)
            p.space_after = Pt(0)
            p.line_spacing = 1.15
            run = p.add_run()
            run.text = str(value)
            f = run.font
            f.name = FONT
            f.size = Pt(header_size if r == 0 else size)
            f.bold = (r == 0) or (c == 0 and first_col_bold)
            f.color.rgb = WHITE if r == 0 else (INK if c == 0 else INK_SOFT)
    return table


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


# ================================================================ 01 封面
s = new_slide()
bar(s, 0, 0, W, 0.16, PRIMARY)
# 右侧信息面板
card(s, 8.62, 0.16, W - 8.62, H - 0.16, fill=PRIMARY, radius=0.0)
tf = tb(s, 9.15, 1.15, 3.6, 0.3)
para(tf, "一句话说明", size=10, color=RGBColor(0xC9, 0xB9, 0x9F), bold=True, first=True, space_after=0)
tf = tb(s, 9.15, 1.5, 3.6, 1.1)
para(tf, "「规划 → 写作 → 记忆 → 审核 → 提交」", size=13, color=WHITE, bold=True,
     first=True, space_after=0, line=1.4)
steps = ["逐章规划：只改下一章", "事实记忆：带版本与出处", "独立审核：矛盾与遗漏", "原子提交：失败不改正式稿"]
tf = tb(s, 9.15, 3.05, 3.55, 2.2)
for i, t in enumerate(steps):
    para(tf, t, size=10.5, color=RGBColor(0xE8, 0xE0, 0xD2), first=(i == 0), space_after=9)
hairline(s, 9.15, 4.95, 3.2, RGBColor(0x54, 0x72, 0x92))
tf = tb(s, 9.15, 5.15, 3.5, 1.2)
para(tf, "本地运行 · 作品留在本机 · 按 token 透明计费", size=10, color=RGBColor(0xC9, 0xB9, 0x9F),
     first=True, space_after=0, line=1.5)

tf = tb(s, ML, 1.05, 7.2, 0.3)
para(tf, "创新工程实践营 · 项目汇报（8 分钟）", size=11, color=ACCENT, bold=True, first=True, space_after=0)
tf = tb(s, ML, 1.5, 7.4, 1.4)
para(tf, "Tome Agent", size=52, color=INK, bold=True, first=True, space_after=0, line=1.0)
tf = tb(s, ML, 2.72, 7.2, 0.9)
para(tf, "让一个点子，变成一部自洽的长篇小说", size=21, color=PRIMARY, bold=True, first=True, space_after=0, line=1.3)
hairline(s, ML, 3.72, 2.6, ACCENT)
tf = tb(s, ML, 3.95, 7.2, 0.9)
para(tf, "第一部分 · 产品介绍 ｜ 1. 产品设计（1.1–1.2）　2. 产品设计应用的原则", size=12.5,
     color=INK_SOFT, first=True, space_after=0, line=1.5)
tf = tb(s, ML, 5.55, 7.3, 1.0)
para(tf, "汇报团队：宇宙无敌暴龙战士", size=11.5, color=INK, bold=True, first=True, space_after=3)
para(tf, "查军益（开发）· 秦宗鑫（创作与评估）· 谭钧浩（测试）· 周涛（体验与文档）", size=9.5, color=MUTED, space_after=0)
tf = tb(s, ML, 6.62, 4.0, 0.3)
para(tf, "2026-11 · 产品名中文工作名：卷宗", size=9.5, color=MUTED, first=True, space_after=0)
notes(s, "开场：我们做的是 Tome Agent，一个本地运行的长篇小说生成助手。这 8 分钟里，我负责第一部分——它是什么，以及为什么这么设计。")

# ================================================================ 02 汇报地图
s = new_slide()
header(s, "本篇范围", "这一段要回答两个问题：这个产品是什么，为什么这样设计", 2,
       note="完整汇报 8 分钟；本篇约 4 分钟")
cards = [
    ("01", "1.1 产品使命、口号和策略", "使命 · 口号 · 目标用户 · 如何获得用户 · 团队优势 · 差异化", "6 项"),
    ("02", "1.2 产品定义", "定位模板 · 解决的问题 · 用户故事（价值）· 解决方案形态", "4 项"),
    ("03", "2. 产品设计应用的原则", "需求·信息·创新 / 系统·收敛·优化 / 继承·效益·时间 / 定量·简化·审核", "12 条"),
]
y = 1.88
for num, title, body, cnt in cards:
    card(s, ML, y, CW, 1.22, fill=CARD_SOFT)
    bar(s, ML, y, 0.055, 1.22, PRIMARY)
    tf = tb(s, ML + 0.32, y + 0.2, 0.7, 0.4)
    para(tf, num, size=20, color=ACCENT, bold=True, first=True, space_after=0)
    tf = tb(s, ML + 1.05, y + 0.18, 8.4, 0.9)
    para(tf, title, size=14.5, color=INK, bold=True, first=True, space_after=3)
    para(tf, body, size=10.5, color=MUTED, space_after=0)
    tf = tb(s, W - MR - 1.2, y + 0.42, 1.0, 0.4)
    para(tf, cnt, size=13, color=PRIMARY, bold=True, align=PP_ALIGN.RIGHT, first=True, space_after=0)
    y += 1.42

tf = tb(s, ML, 6.28, CW, 0.4)
rich(para(tf, first=True, space_after=0),
     [("下一篇（第二部分）：", {"bold": True, "color": INK, "size": 10.5}),
      ("3. 产品实现——技术选型与版本、仓库与提交历史、架构与数据库、接口、质量工具、代码统计。", {"color": MUTED, "size": 10.5})])
notes(s, "先用一页交代结构：1.1 讲策略六项，1.2 讲定义，2 讲十二条设计原则；第 3 部分产品实现放在后面。")

# ================================================================ 03 使命
s = new_slide()
header(s, "1.1.1 使命", "让心里有故事的人，写出一部属于自己的自洽长篇", 3)
card(s, ML, 1.85, CW, 1.5, fill=PRIMARY)
tf = tb(s, ML + 0.45, 2.02, CW - 0.9, 1.2, anchor=MSO_ANCHOR.MIDDLE)
para(tf, "使命：把「创作一部长篇」的门槛，从「会不会写」降到「说不说得清一个想法」；\n"
         "把「记得住」这件事，交给系统而不是交给更长的提示词。", size=15, color=WHITE, bold=True,
     first=True, space_after=0, line=1.55)

items = [
    ("门槛", "读者只要给得出题材、主角和走向，就能拿到第 1 章；不需要学写作，也不需要学提示词。"),
    ("质量", "跨章的一致性靠结构化事实来管：每个设定带版本、变更理由和正文出处，可以逐条核验。"),
    ("归属", "作品文件存在本机，可以导出；不为平台锁定，也不为订阅付费。"),
]
x = ML
for label, text in items:
    card(s, x, 3.62, (CW - 0.5) / 3, 1.42, fill=CARD_SOFT)
    tf = tb(s, x + 0.28, 3.78, (CW - 0.5) / 3 - 0.5, 0.32)
    para(tf, label, size=12.5, color=ACCENT, bold=True, first=True, space_after=0)
    tf = tb(s, x + 0.28, 4.18, (CW - 0.5) / 3 - 0.5, 0.78)
    para(tf, text, size=10.5, color=INK_SOFT, first=True, space_after=0, line=1.45)
    x += (CW - 0.5) / 3 + 0.25

tf = tb(s, ML, 5.32, CW, 0.95)
rich(para(tf, first=True, space_after=6),
     [("使命同时划掉两件事：", {"bold": True, "color": INK})])
rich(para(tf, space_after=0),
     [("× 不做「一键生成爆款」的流量工具——它奖励套路，不奖励自洽；", {"color": MUTED}),
      ("　× 这一版也不做「作者量产」的效率工具——那是另一群用户、另一套需求。", {"color": MUTED})])
tf = tb(s, ML, 6.6, CW, 0.3)
para(tf, "依据：docs/requirements/problem_definition.md（问题定义与产品描述）", size=9, color=MUTED, first=True, space_after=0)
notes(s, "使命一句话：让心里有故事的人把它写出来。注意两个着力点——门槛降到「说清一个想法」，一致性交给结构化事实。")

# ================================================================ 04 口号
s = new_slide()
header(s, "1.1.2 口号", "对外一句记得住的话，对内一句不许走偏的话", 4)
tf = tb(s, ML, 1.95, CW, 0.4)
para(tf, "主口号（对外）", size=10.5, color=ACCENT, bold=True, first=True, space_after=0)
tf = tb(s, ML, 2.3, CW, 1.0)
para(tf, "一个点子，一部自洽的长篇。", size=44, color=INK, bold=True, first=True, space_after=0, line=1.1)
hairline(s, ML, 3.42, CW)

card(s, ML, 3.72, 5.55, 1.28, fill=CARD_SOFT)
tf = tb(s, ML + 0.3, 3.86, 4.95, 1.0)
para(tf, "副口号（对内 / README 首行）", size=9.5, color=ACCENT, bold=True, first=True, space_after=4)
para(tf, "先把「记得住」做对，再谈「写得好」。", size=15, color=PRIMARY, bold=True, space_after=0, line=1.3)

tf = tb(s, 6.75, 3.72, 5.7, 1.9)
para(tf, "备选（按场景取用）", size=9.5, color=ACCENT, bold=True, first=True, space_after=6)
for t in ["「想看的，自己写出来。」——面向读者，情绪最直接",
          "「不会写，也能写完。」——强调完成度，适合首屏",
          "「设定不丢，故事才长。」——强调一致性，适合技术读者"]:
    para(tf, t, size=10.5, color=INK_SOFT, space_after=5, line=1.35)

card(s, ML, 5.28, CW, 1.02, fill=CARD)
tf = tb(s, ML + 0.32, 5.42, CW - 0.64, 0.78)
rich(para(tf, first=True, space_after=0, line=1.5),
     [("口号纪律：", {"bold": True, "color": ACCENT}),
      ("只承诺能验证的三件事——自洽（矛盾可查）、可恢复（失败能续）、可导出（作品归你）；"
       "不使用「最强」「超越」「一键成神」这类无法证伪的词。", {"color": INK_SOFT})])
tf = tb(s, ML, 6.58, CW, 0.3)
para(tf, "口号出现在：封面、工作台首屏、演示结尾、仓库 README 第一行", size=9, color=MUTED, first=True, space_after=0)
notes(s, "主口号给用户，副口号给我们自己：先把记得住做对。口号纪律是不用无法证伪的词。")

# ================================================================ 05 目标用户
s = new_slide()
header(s, "1.1.3 目标用户", "用户是「想创作却不会写」的读者，不是专业作者", 5)
users = [
    ("爱看小说的普通人", "有明确口味：题材、主角、CP、爽点都在心里，就是写不出来。",
     "诉求：一个点子，先拿到第 1 章看看合不合口味。"),
    ("「设定控」读者", "对前后一致、伏笔回收特别敏感，受够了 AI 的「吃设定」。",
     "诉求：能查到某个设定从哪一章开始、又在哪一章改变。"),
    ("短视频 / 图文创作者", "需要设定自洽、可以直接改的故事脚本，但自己不会写小说。",
     "诉求：题材能定制，产物能直接编辑和导出。"),
]
x = ML
for name, desc, need in users:
    card(s, x, 1.8, 3.62, 2.15, fill=CARD_SOFT)
    bar(s, x, 1.8, 3.62, 0.05, ACCENT)
    tf = tb(s, x + 0.26, 2.0, 3.1, 1.8)
    para(tf, name, size=12.5, color=INK, bold=True, first=True, space_after=6, line=1.25)
    para(tf, desc, size=10, color=INK_SOFT, space_after=6, line=1.45)
    para(tf, need, size=10, color=PRIMARY, bold=True, space_after=0, line=1.45)
    x += 3.62 + 0.32

card(s, ML, 4.12, 7.0, 1.25, fill=CARD)
tf = tb(s, ML + 0.3, 4.24, 6.4, 1.05)
para(tf, "这一版明确不服务谁", size=10, color=ACCENT, bold=True, first=True, space_after=5)
para(tf, "专业作者的量产工具（AI 文笔还撑不起量产质量）｜ 多人协作团队 ｜ 移动端与在线账号（首版单用户、本地运行）",
     size=10.5, color=INK_SOFT, space_after=0, line=1.5)

tf = tb(s, 8.3, 4.12, 4.2, 1.25)
para(tf, "市场口径（估算，非统计口径）", size=9.5, color=ACCENT, bold=True, first=True, space_after=6)
rich(para(tf, space_after=2),
     [("TAM ", {"bold": True, "color": PRIMARY, "size": 10.5}),
      ("网文读者 5.75 亿", {"size": 10.5, "color": INK_SOFT})])
rich(para(tf, space_after=2),
     [("SAM ", {"bold": True, "color": PRIMARY, "size": 10.5}),
      ("愿尝试 AI 创作为 0.5%–2% → 约 290 万–1150 万", {"size": 10.5, "color": INK_SOFT})])
rich(para(tf, space_after=0),
     [("种子 ", {"bold": True, "color": PRIMARY, "size": 10.5}),
      ("首年 100–500 名真实读者（课程阶段可达成）", {"size": 10.5, "color": INK_SOFT})])

bar(s, ML, 5.55, CW, 0.7, PRIMARY)
tf = tb(s, ML + 0.32, 5.55, CW - 0.64, 0.7, anchor=MSO_ANCHOR.MIDDLE)
rich(para(tf, first=True, space_after=0, line=1.3),
     [("用户判据：", {"bold": True, "color": RGBColor(0xE8, 0xB9, 0x6B), "size": 10.5}),
      ("一个没写过小说的人，10 分钟内能不能拿到一部属于自己口味的第一章？", {"color": WHITE, "size": 10.5})])

tf = tb(s, ML, 6.45, CW, 0.3)
para(tf, "数据来源：《2024 中国网络文学蓝皮书》（2025-06）；SAM / SOM 为基于公开总量的比例假设，需实测校准。",
     size=9, color=MUTED, first=True, space_after=0)
notes(s, "我们的用户不是作者，是想创作却不会写的读者。三类画像，各自要的是「第一章」「查设定」「可改的脚本」。")

# ================================================================ 06 获客
s = new_slide()
header(s, "1.1.4 如何获得用户", "从 0 到 1000：种子、内容、口碑三步走", 6)
stages = [
    ("0 → 100", "种子：先把身边人变成用户",
     ["课程、社团、写作群内测邀请", "现场做「同题材对照生成」演示", "每位受邀者试读并填反馈表"],
     "首章读完率 / 二次生成率"),
    ("100 → 1000", "内容：把「吃设定」做成可复现的案例",
     ["同题材、同模型，有无状态记忆对比", "B 站 / 知乎 / 小红书 + 仓库 README 作信任入口", "开源仓库即试用入口，一条命令跑通"],
     "仓库访问 → 本地跑通率"),
    ("1000 →", "口碑：作品本身是最好的广告",
     ["每部作品可导出、可分享首章", "读者晒「我生成的小说」，带作品名回链", "把对照实验更新成季度报告"],
     "自然分享带来的新增"),
]
x = ML
for stage, title, actions, kpi in stages:
    card(s, x, 1.82, 3.62, 3.3, fill=CARD_SOFT)
    tf = tb(s, x + 0.26, 1.98, 3.1, 0.34)
    para(tf, stage, size=11, color=ACCENT, bold=True, first=True, space_after=0)
    tf = tb(s, x + 0.26, 2.34, 3.1, 0.5)
    para(tf, title, size=11, color=INK, bold=True, first=True, space_after=0, line=1.3)
    tf = tb(s, x + 0.26, 2.92, 3.1, 1.6)
    for i, a in enumerate(actions):
        para(tf, "· " + a, size=9.5, color=INK_SOFT, first=(i == 0), space_after=5, line=1.4)
    tf = tb(s, x + 0.26, 4.55, 3.1, 0.45)
    rich(para(tf, first=True, space_after=0, line=1.3),
         [("看板指标：", {"size": 9, "bold": True, "color": PRIMARY}),
          (kpi, {"size": 9, "color": MUTED})])
    x += 3.62 + 0.32

card(s, ML, 5.32, CW, 1.1, fill=CARD)
tf = tb(s, ML + 0.32, 5.46, CW - 0.64, 0.85)
para(tf, "三个必须做对的转化点", size=9.5, color=ACCENT, bold=True, first=True, space_after=6)
rich(para(tf, space_after=0, line=1.5),
     [("① 生成前看得见费用（预估 token 与人民币）　", {"color": INK_SOFT}),
      ("② 失败能续（检查点恢复，不从头再来）　", {"color": INK_SOFT}),
      ("③ 首章就能判断合不合口味（先读再批量）", {"color": INK_SOFT})])
tf = tb(s, ML, 6.56, CW, 0.3)
para(tf, "说明：获客路径为计划，尚未实测；种子目标 100–500 人，指标口径随第一轮试用校准。",
     size=9, color=MUTED, first=True, space_after=0)
notes(s, "获客三步：种子、内容、口碑。真正决定转化的是三点——费用看得见、失败能续、首章就能判断口味。")

# ================================================================ 07 团队优势
s = new_slide()
header(s, "1.1.5 团队优势", "四个人的分工是一条完整链条，不是一个开发带三个旁观者", 7)
tf = tb(s, ML, 1.8, 5.7, 0.3)
para(tf, "分工（苏州大学 计算机科学与技术 2025 级）", size=9.5, color=ACCENT, bold=True, first=True, space_after=0)
members = [
    ("查军益", "项目负责人 / 核心开发", "生成框架、模型接口、代码集成"),
    ("秦宗鑫", "项目协调 / 创作评估", "创作需求、小说质量评估、风险"),
    ("谭钧浩", "测试 / 问题跟踪", "环境安装、功能测试、缺陷记录"),
    ("周涛", "体验 / 文档", "页面体验、文档整理、成果展示"),
]
y = 2.15
for name, role, task in members:
    card(s, ML, y, 5.7, 0.82, fill=CARD_SOFT)
    tf = tb(s, ML + 0.22, y + 0.09, 1.05, 0.62)
    para(tf, name, size=11, color=INK, bold=True, first=True, space_after=0)
    tf = tb(s, ML + 1.28, y + 0.08, 4.2, 0.68)
    para(tf, role, size=9, color=ACCENT, bold=True, first=True, space_after=2)
    para(tf, task, size=9.5, color=MUTED, space_after=0, line=1.3)
    y += 0.92

tf = tb(s, 6.95, 1.8, 5.5, 0.3)
para(tf, "三条可验证的优势", size=9.5, color=ACCENT, bold=True, first=True, space_after=0)
adv = [
    ("链条完整", "开发 → 创作评估 → 测试 → 体验文档，每项交付至少一名非负责人复核，避免「一个人测自己写的代码」。"),
    ("视角对", "计算机专业背景，从「数据一致性、事务、可恢复」切入长文本生成，而不是从「提示词技巧」切入。"),
    ("可复现", "两周计划、Issue / Kanban 留痕、真实调用记录 token 与费用；换一台电脑能按脚本跑起来。"),
]
y = 2.15
for t, body in adv:
    tf = tb(s, 6.95, y, 5.5, 0.95)
    para(tf, t, size=11.5, color=PRIMARY, bold=True, first=True, space_after=3)
    para(tf, body, size=9.8, color=INK_SOFT, space_after=0, line=1.45)
    y += 1.06

card(s, ML, 5.95, CW, 0.86, fill=RGBColor(0xF7, 0xEC, 0xE8))
tf = tb(s, ML + 0.3, 6.06, CW - 0.6, 0.7)
rich(para(tf, first=True, space_after=0, line=1.45),
     [("自曝一条风险：", {"bold": True, "color": ACCENT}),
      ("成员开发经验有差距，核心框架集中在一人。对策：任务拆小、关键操作结对、改公共接口前先通知、交叉复核不省略。",
       {"color": INK_SOFT, "size": 10})])
notes(s, "四个人是一条链：开发、创作评估、测试、体验文档，每项交付都有第二个人复核。风险也说了：经验差距、核心集中在一人。")

# ================================================================ 08 差异化
s = new_slide()
header(s, "1.1.6 如何做到差异化", "不比「谁更会写」，比「谁记得住、谁不糊弄」", 8,
       note="竞品信息：公开产品页与第三方横评（2026-04），属市场观察")
rows = [
    ["维度", "通用 AI 聊天", "面向作者的写作工具", "网文阅读平台", "Tome Agent"],
    ["目标用户", "会用提示词的任何人", "会写的作者", "读者（读现成的）", "想创作却不会写的读者"],
    ["输入方式", "一段提示词", "大纲、设定、章节指令", "—", "一个点子：题材 + 主角 + 走向"],
    ["记忆方式", "上下文窗口，越长越贵、越衰减", "多为摘要或设定表", "—", "带版本与正文出处的事实账本"],
    ["生成单位", "一次回答", "一段 / 一章", "—", "一章一事务，校验后提交"],
    ["失败处理", "重新生成一遍", "手工修改", "—", "检查点恢复，正式稿不被污染"],
    ["承诺边界", "不承诺篇幅", "不承诺篇幅", "—", "只承诺验证过的篇幅（1 万字 / 8–10 章起）"],
    ["成本与归属", "订阅", "订阅 + 云端", "平台内阅读", "本地运行、自带 Key、作品留本机"],
]
plain_table(s, ML, 1.78, CW, [1.55, 2.45, 2.45, 2.05, 3.13], rows,
            size=9.2, header_size=9.5, row_h=0.485, header_h=0.4)
card(s, ML, 6.02, CW, 0.78, fill=PRIMARY)
tf = tb(s, ML + 0.32, 6.12, CW - 0.6, 0.6, anchor=MSO_ANCHOR.MIDDLE)
rich(para(tf, first=True, space_after=0, line=1.3),
     [("一句话差异化：", {"bold": True, "color": RGBColor(0xE8, 0xB9, 0x6B), "size": 11}),
      ("通用 AI 卖「会写」，写作工具卖「作者的效率」，Tome Agent 卖「读者零门槛写出一部自洽的长篇」。",
       {"color": WHITE, "size": 11})])
notes(s, "差异化四层：面向读者而非作者、事实级记忆而非摘要、提交是事务而非覆盖、本地归属。最后一列只承诺验证过的篇幅。")

# ================================================================ 09 产品定义
s = new_slide()
header(s, "1.2 产品定义", "用定位模板把产品说清楚：给谁、解决什么、凭什么不同", 9)
lines = [
    ("对于", "心里有想看的题材、却不会写小说的普通读者"),
    ("他们", "想让 AI 把想法写成一部前后连贯的长篇，但通用 AI 一写长就「吃设定」"),
    ("Tome Agent 是一个", "本地运行的长篇小说生成助手"),
    ("它能够", "用「逐章规划 → 正文 → 事实变更 → 独立审核 → 原子提交」维护带出处和版本的记忆，生成可暂停、可恢复、可导出"),
    ("不同于", "面向作者的复杂写作工作台，也不同于记不住设定的通用 AI 聊天"),
    ("我们的产品", "让不会写小说的人，也能创作出一部设定自洽、属于自己的长篇小说"),
]
y = 1.85
for label, text in lines:
    tf = tb(s, ML, y + 0.04, 1.95, 0.4)
    para(tf, label, size=11.5, color=ACCENT, bold=True, first=True, space_after=0)
    tf = tb(s, ML + 2.05, y, CW - 2.05, 0.62)
    para(tf, text, size=11.5, color=INK, first=True, space_after=0, line=1.4)
    hairline(s, ML, y + 0.68, CW, RGBColor(0xE8, 0xE1, 0xD5))
    y += 0.74

tf = tb(s, ML, 6.35, CW, 0.4)
rich(para(tf, first=True, space_after=0, line=1.4),
     [("自检：", {"bold": True, "color": PRIMARY}),
      ("把这段念给一个没看过代码的人，他能复述出「给谁、解决什么、哪里不一样」，定义才算过。",
       {"color": MUTED, "size": 9.5})])
notes(s, "定位模板逐行念一遍：对于谁、他们有什么诉求、我们是什么、能做什么、不同于谁、最终给到什么。")

# ================================================================ 10 解决的问题
s = new_slide()
header(s, "1.2.1 解决的问题", "五个症状，一个根因：记忆能力撑不起一部书", 10)
pains = [
    ("01", "记不住设定", "年龄、关系、能力、地点——稍微写长一点就开始前后矛盾。"),
    ("02", "时间线与因果对不上", "事件顺序、谁在场、发生过什么，跨章之后对不齐。"),
    ("03", "伏笔与义务不回收", "前面埋下的线索、答应过的走向，后面忘了提。"),
    ("04", "上下文不可持续", "全文塞进长上下文：贵、注意力衰减；改成摘要：细节又丢了。"),
    ("05", "生成过程不可恢复", "一次失败就要重来，成本和进度一起损失。"),
]
y = 1.8
for num, title, body in pains:
    tf = tb(s, ML, y + 0.02, 0.55, 0.4)
    para(tf, num, size=15, color=ACCENT, bold=True, first=True, space_after=0)
    tf = tb(s, ML + 0.62, y, 6.0, 0.85)
    para(tf, title, size=12, color=INK, bold=True, first=True, space_after=2)
    para(tf, body, size=10, color=MUTED, space_after=0, line=1.4)
    hairline(s, ML, y + 0.86, 6.4, RGBColor(0xE8, 0xE1, 0xD5))
    y += 0.96

card(s, 7.55, 1.8, 4.93, 3.1, fill=PRIMARY)
tf = tb(s, 7.9, 2.0, 4.25, 3.0)
para(tf, "根因判断", size=9.5, color=RGBColor(0xE8, 0xB9, 0x6B), bold=True, first=True, space_after=10)
para(tf, "「记忆能力」≠「上下文长度」", size=17, color=WHITE, bold=True, space_after=10, line=1.3)
para(tf, "模型不是不想记。是「把前文再喂一遍」这种记忆方式，撑不起一部书——越往后越贵、越模糊。",
     size=10.5, color=RGBColor(0xE6, 0xDF, 0xD2), space_after=10, line=1.55)
para(tf, "所以我们不从「再写一段更长的提示词」入手，而从「怎么让故事状态可查、可验、可恢复」入手。",
     size=10.5, color=WHITE, bold=True, space_after=0, line=1.55)

tf = tb(s, 7.55, 5.35, 4.93, 1.3)
para(tf, "一条诚实说明", size=9.5, color=ACCENT, bold=True, first=True, space_after=5)
para(tf, "「状态记忆能减少跨章矛盾」目前是待验证假设：要用同输入、同模型、有/无记忆的对照实验来证明，"
         "在跑完对照前不把它当结论。", size=9.5, color=MUTED, space_after=0, line=1.45)
notes(s, "五个症状，一个根因：记忆能力不等于上下文长度。最后那句诚实说明很重要——一致性提升目前还是待验证假设。")

# ================================================================ 11 用户故事
s = new_slide()
header(s, "1.2.2 对客户的价值", "用用户故事说价值：作为谁、完成了什么、带来什么", 11)
stories = [
    ("只想看自己想看故事的读者",
     "用一两句话描述题材、主角和走向，生成并读完第 1 章",
     "不必等更新，也不必迁就平台现成的套路"),
    ("在意前后一致的连载读者",
     "每章后看到人物与物品的关键设定、版本，以及它从哪章开始、哪章改变",
     "后文沿用同一设定，矛盾当场被指出"),
    ("业余写作者",
     "为一部作品填写文风要求与参考片段，设定从下一章开始生效",
     "后续章节保持相近口吻，已经写好的正文不变"),
    ("想一次写完多章的作者",
     "设好目标章节数与字数，连续生成并在目标处停下",
     "一口气拿到多章初稿，并知道写到哪里、为什么停下"),
]
pos = [(ML, 1.8), (6.72, 1.8), (ML, 3.88), (6.72, 3.88)]
for (x, y), (who, what, value) in zip(pos, stories):
    card(s, x, y, 5.6, 1.8, fill=CARD_SOFT)
    bar(s, x, y, 0.05, 1.8, PRIMARY)
    tf = tb(s, x + 0.3, y + 0.16, 5.05, 1.55)
    para(tf, "作为", size=9, color=ACCENT, bold=True, first=True, space_after=1)
    para(tf, who, size=11.5, color=INK, bold=True, space_after=8, line=1.25)
    rich(para(tf, space_after=3, line=1.35),
         [("完成 ", {"size": 9, "bold": True, "color": PRIMARY}),
          (what, {"size": 9.8, "color": INK_SOFT})])
    rich(para(tf, space_after=0, line=1.35),
         [("带来 ", {"size": 9, "bold": True, "color": PRIMARY}),
          (value, {"size": 9.8, "color": PRIMARY, "bold": True})])

tf = tb(s, ML, 6.02, CW, 0.4)
rich(para(tf, first=True, space_after=0, line=1.4),
     [("写法纪律：", {"bold": True, "color": ACCENT}),
      ("用用户的业务语言，不出现「向量」「检查点」「JSON 契约」；每条故事配 Gherkin 验收条件，见 "
       "docs/requirements/user_stories.md（按 INVEST 拆分，共 5 条）。", {"color": MUTED, "size": 9.3})])
notes(s, "四条用户故事，都是业务语言：读者点单、设定可查、文风统一、连续批量。验收条件在仓库的 user_stories 文档里。")

# ================================================================ 12 解决方案
s = new_slide()
header(s, "1.2.3 解决方案", "形态选「本地网站」：作品和密钥留在本机，浏览器打开就能用", 12)
tf = tb(s, ML, 1.76, CW, 0.5)
rich(para(tf, first=True, space_after=0, line=1.4),
     [("为什么是网站，不是小程序 / App：", {"bold": True, "color": ACCENT, "size": 10.5}),
      ("作品文件与 API Key 必须留在本机、成本按 token 透明、不经过上架审核；本地网页用浏览器即可打开，"
       "不需要账号、不需要装客户端。", {"size": 10.5, "color": INK_SOFT})])

steps = [("下一章规划", "只改下一章"), ("正文候选", "不能改存档"), ("事实变更候选", "带出处版本"),
         ("独立审核", "矛盾与遗漏"), ("整章提交", "失败不改正式稿"), ("导出 Markdown", "可改可投稿")]
cw_chev = 1.98
x = ML
for i, (title, sub) in enumerate(steps):
    shp = s.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(x), Inches(2.62), Inches(cw_chev), Inches(0.66))
    shp.fill.solid()
    shp.fill.fore_color.rgb = PRIMARY if i < 5 else ACCENT
    shp.line.fill.background()
    shp.shadow.inherit = False
    tf2 = shp.text_frame
    tf2.word_wrap = False
    tf2.margin_left = Inches(0.16)
    tf2.margin_right = Inches(0.1)
    p = tf2.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = title
    r.font.size = Pt(9.5)
    r.font.bold = True
    r.font.name = FONT
    r.font.color.rgb = WHITE
    rPr = r._r.get_or_add_rPr()
    ea = rPr.makeelement(qn("a:ea"), {})
    ea.set("typeface", FONT)
    rPr.append(ea)
    tf3 = tb(s, x + 0.24, 3.36, cw_chev - 0.34, 0.3)
    para(tf3, sub, size=8.2, color=MUTED, align=PP_ALIGN.CENTER, first=True, space_after=0)
    x += cw_chev - 0.22

tf = tb(s, ML, 3.85, 5.6, 2.2)
para(tf, "技术组成（版本见 README）", size=9.5, color=ACCENT, bold=True, first=True, space_after=7)
tech = [
    ("界面", "Vue 3.5.44 内置运行时，无前端构建步骤；本地 HTTP 服务 http://127.0.0.1:8765"),
    ("编排", "LangGraph 1.2.17 把五个阶段建成状态图，支持条件分支与重规划"),
    ("存储", "文件模式零配置即可跑；需要持久化时用 PostgreSQL 17 + Psycopg 3.3.3"),
    ("模型", "Chat Completions 兼容接口：DeepSeek、OpenAI 及其他兼容服务"),
]
y = 4.14
for k, v in tech:
    tf2 = tb(s, ML, y, 0.72, 0.3)
    para(tf2, k, size=10, color=PRIMARY, bold=True, first=True, space_after=0)
    tf2 = tb(s, ML + 0.8, y, 4.9, 0.45)
    para(tf2, v, size=9.5, color=INK_SOFT, first=True, space_after=0, line=1.4)
    y += 0.52

card(s, 6.86, 3.85, 5.62, 2.35, fill=CARD_SOFT)
tf = tb(s, 7.14, 4.0, 5.1, 2.05)
para(tf, "用户看到的三件事", size=9.5, color=ACCENT, bold=True, first=True, space_after=8)
for t in ["生成前：显示本次预估输入/输出 token 与人民币费用，确认后才调用模型",
          "生成中：逐章保存检查点，中断后从断点继续，正式稿只在整章校验通过后写入",
          "生成后：在工作台读章、导出排版好的 Markdown，作品目录在本机随手可备份"]:
    para(tf, "· " + t, size=9.8, color=INK_SOFT, space_after=7, line=1.45)
tf = tb(s, 6.86, 6.32, 5.62, 0.4)
para(tf, "对应课程要求「网站 / 微信小程序 / Android 应用」中的「网站」形态。", size=9, color=MUTED, first=True, space_after=0)
notes(s, "形态选网站：作品和密钥留在本机。六个阶段一串，核心是提交是事务，失败不动正式稿。技术栈版本都在 README。")

# ================================================================ 13 设计原则总览
s = new_slide()
header(s, "2. 产品设计应用的原则", "十二条原则，一条主线：每条都要能在仓库里找到证据", 13)
groups = [
    ("组一", "需求 · 信息 · 创新", "先有真需求，再用信息校准，最后才谈创新", "01"),
    ("组二", "系统 · 收敛 · 优化", "把作品当系统，先发散后收敛，再逐项优化", "02"),
    ("组三", "继承 · 效益 · 时间", "能继承的不重造，算清效益，抢住窗口", "03"),
    ("组四", "定量 · 简化 · 审核", "能测就测，能简就简，每一步都审", "04"),
]
pos = [(ML, 1.82), (6.72, 1.82), (ML, 3.62), (6.72, 3.62)]
for (x, y), (g, names, motto, n) in zip(pos, groups):
    card(s, x, y, 5.6, 1.6, fill=CARD_SOFT)
    tf = tb(s, x + 0.3, y + 0.2, 1.0, 0.35)
    para(tf, n, size=13, color=ACCENT, bold=True, first=True, space_after=0)
    tf = tb(s, x + 0.95, y + 0.18, 4.4, 1.3)
    para(tf, names, size=14, color=INK, bold=True, first=True, space_after=4)
    para(tf, motto, size=9.8, color=MUTED, space_after=0, line=1.35)
    tf = tb(s, x + 0.95, y + 1.2, 4.2, 0.28)
    para(tf, f"详见第 {13 + int(n)} 页", size=8.5, color=RGBColor(0x9A, 0x8F, 0x7E),
         align=PP_ALIGN.RIGHT, first=True, space_after=0)

tf = tb(s, ML, 5.45, CW, 0.55)
rich(para(tf, first=True, space_after=0, line=1.5),
     [("为什么是这十二条：", {"bold": True, "color": PRIMARY}),
      ("它们来自产品设计的基础原则体系（需求 / 信息 / 创新；系统 / 收敛 / 优化；继承 / 效益 / 时间；定量 / 简化 / 审核），"
       "正好覆盖我们这轮设计要做判断的四个层面——要不要做、怎么成形、拿什么换、怎么验收。", {"color": INK_SOFT})])
tf = tb(s, ML, 6.5, CW, 0.4)
para(tf, "参考：产品设计小文集锦（需求/信息/创新、系统/收敛/优化、继承/效益/时间、定量/简化/审核 四篇）；"
         "机械工业出版社《现代产品设计指南》1.5 节产品设计和开发的原则。", size=8.8, color=MUTED, first=True, space_after=0)
notes(s, "十二条原则分四组。我用一条判定：每条原则都要能在仓库里找到一次具体的设计决策或一份证据。")

# ================================================================ 14 需求 信息 创新
def principle_slide(num: int, eyebrow: str, base_title: str, cols, note_text: str, foot: str | None = None):
    s = new_slide()
    header(s, eyebrow, base_title, num)
    width = (CW - 0.44) / 3
    x = ML
    for name, gist, appl in cols:
        card(s, x, 1.8, width, 4.05, fill=CARD_SOFT)
        bar(s, x, 1.8, width, 0.05, PRIMARY)
        tf = tb(s, x + 0.28, 2.0, width - 0.56, 1.15)
        para(tf, name, size=15, color=PRIMARY, bold=True, first=True, space_after=5)
        para(tf, gist, size=9.3, color=MUTED, space_after=0, line=1.45)
        tf = tb(s, x + 0.28, 3.22, width - 0.56, 2.5)
        para(tf, "本产品的做法", size=8.8, color=ACCENT, bold=True, first=True, space_after=6)
        for a in appl:
            para(tf, "· " + a, size=9.8, color=INK_SOFT, space_after=8, line=1.45)
        x += width + 0.22
    if foot:
        card(s, ML, 6.02, CW, 0.62, fill=CARD)
        tf = tb(s, ML + 0.3, 6.02, CW - 0.6, 0.62, anchor=MSO_ANCHOR.MIDDLE)
        rich(para(tf, first=True, space_after=0, line=1.3), foot)
    notes(s, note_text)
    return s


principle_slide(
    14, "2. 产品设计应用的原则 · 组一", "需求定方向，信息校准方向，创新才有落脚点",
    [
        ("需求原则",
         "功能要求来自客观需求：显需求推动改进，隐需求催生创新。",
         ["需求从「不会写」和「吃设定」出发，不是从「模型能干什么」出发",
          "先冻结 MVP：单用户、本地、中文、顺序逐章；多人协作 / 移动端 / 自动出版明确不做",
          "显需求 = 把想法变成第 1 章；隐需求 = 设定可查、失败可续"]),
        ("信息原则",
         "全面、充分、正确、可靠地掌握市场、技术、测试信息，用它引导设计。",
         ["设计前完成竞品与长文本架构调研：网文读者 5.75 亿、三类竞品对照、长上下文 / 摘要 / 检索方案比较",
          "结论「记忆能力是真实短板」写进问题定义，而不是拍脑袋定功能",
          "调研、架构、验证记录都进仓库，成为下一轮决策的输入"]),
        ("创新原则",
         "大胆创新，冲破传统观念与惯例的束缚。",
         ["事件先行：先推演场景事件与状态，再写正文，而不是写完再回头猜关键事实",
          "事实账本：每条设定带稳定属性名、版本、变更理由和正文原句",
          "提交是事务不是覆盖：在副本上校验通过才整体写入"]),
    ],
    "组一的关键词是「别自嗨」：需求来自用户的痛点，创新要有证据支撑。",
    [("一句话：", {"bold": True, "color": PRIMARY}),
     ("需求回答「该不该做」，信息回答「凭什么这样设计」，创新回答「我们做了什么别人没做的」。",
      {"color": MUTED, "size": 9.5})],
)

principle_slide(
    15, "2. 产品设计应用的原则 · 组二", "把作品当系统设计，先发散后收敛，再逐项优化",
    [
        ("系统原则",
         "用系统论方法求功能结构，通过分析、综合与评价，达到综合最优。",
         ["写作被建成「规划—写作—记忆—审核—提交」的状态系统，用 LangGraph 状态图表达",
          "四个角色职责与 JSON 契约固定：规划只改下一章、写作不能改存档、审核只判不改",
          "任何环节失败都不污染正式快照——系统边界优先于单点效果"]),
        ("收敛原则",
         "先发散思维构思方案，再综合多种信息收敛。",
         ["记忆方案先发散四种：全文塞上下文 / 摘要压缩 / 向量检索 / 结构化事实",
          "按「可核验、可恢复、成本」三个标准收敛到结构化事实 + 三层记忆",
          "首版只带最近两章、最多 128 条有效事实：先收敛到能验证的规模"]),
        ("优化原则",
         "方案择优、参数优化、总体方案优化：高效、优质、经济。",
         ["篇幅按「总字数 − 已写 − 剩余章节」动态分配，而不是每章固定字数",
          "局部失败降级：规划或记忆处理失败时记录问题，尽量保住有效正文",
          "审核格式错误最多修一次，避免无限循环；重规划只改尚未写作的章节"]),
    ],
    "组二的关键词是「有边界」：系统定边界，收敛定范围，优化定参数。",
    [("一句话：", {"bold": True, "color": PRIMARY}),
     ("系统原则让我们定义务边界，收敛原则让我们砍掉炫技方案，优化原则让我们在真实约束下调参数。",
      {"color": MUTED, "size": 9.5})],
)

principle_slide(
    16, "2. 产品设计应用的原则 · 组三", "能继承的不重造，算清效益，抢住时间窗口",
    [
        ("继承原则",
         "批判地吸收前人成果，推陈出新，为我所用。",
         ["编排用 LangGraph、接口用 Chat Completions 兼容协议、界面用 Vue 运行时、存储用 PostgreSQL",
          "继承的是成熟模式：状态图、事务提交、检查点恢复、幂等回执",
          "不继承的是形态：不复制「面向作者的复杂写作工作台」那一套功能堆叠"]),
        ("效益原则",
         "既讲技术经济效益，也讲社会效益。",
         ["本地运行 + 自带 Key + 按 token 计费，生成前显示预估人民币费用",
          "单用户本地存档，省掉服务器与运维成本；换机器只要拷作品目录",
          "社会效益：降低创作门槛，作品留在作者手里，可导出、不被平台锁定"]),
        ("时间原则",
         "加快研制节奏，并预测同类产品在开发期可能发生的变化。",
         ["14 天交付计划：需求冻结 → 原型联调 → 真实模型 → 对照修复 → 交付演练",
          "窗口期判断：通用模型记忆能力在增强，所以必须尽早用可复现对照实验证明价值",
          "先交付能演示的最小闭环，把「更好文笔」留给模型升级，而不是自己造"]),
    ],
    "组三的关键词是「不做无谓功」：能继承的继承，花出去的每一分要能算回来，节奏要抢在窗口关闭前。",
    [("一句话：", {"bold": True, "color": PRIMARY}),
     ("继承省时间，效益定取舍，时间定顺序——三者一起决定了我们的两周计划长什么样。",
      {"color": MUTED, "size": 9.5})],
)

principle_slide(
    17, "2. 产品设计应用的原则 · 组四", "能测就测，能简就简，每一步都审",
    [
        ("定量原则",
         "在方案选择、性能评价、效益评价上尽量采用科学的定量方法。",
         ["成功标准写成可测指标：约 1 万字 / 8–10 章、跨章矛盾数对比基线、token 与费用、恢复成功率",
          "回归测试 127 项（120 通过、7 项无数据库时跳过）+ 长篇引擎 42 项",
          "用户测试表逐项打分，试读问卷量化「愿不愿意读完」"]),
        ("简化原则",
         "保证功能的前提下力求简化，降低成本、保证质量。",
         ["后端用 Python 标准库 http.server，不额外引入 Web 框架",
          "前端用内置 Vue 运行时，零构建步骤；文件模式零配置即可运行",
          "首版只做中文 + 顺序逐章 + 单用户，把复杂度留给后续迭代"]),
        ("审核原则",
         "随时审核每个设计步骤的信息，确保每一步正确。",
         ["每章一个独立审核角色：查硬矛盾、因果问题和重要记忆遗漏，只判不改",
          "提交前在副本上整体校验章节、计划与记忆；PR 必须由另一名成员审阅",
          "代码走 ruff 等质量检查，密钥与作品数据不得进入 Git"]),
    ],
    "组四的关键词是「可验收」：定量给标准，简化控成本，审核保证每一步没跑偏。",
    [("落点：", {"bold": True, "color": ACCENT}),
     ("十二原则最终收敛成一句话——先把「记得住」做对，再把「写得好」交给模型迭代。",
      {"color": INK, "size": 10, "bold": True})],
)

# ---------------------------------------------------------------- 元数据
prs.core_properties.title = "Tome Agent · 第一部分 产品设计与产品设计原则"
prs.core_properties.author = "宇宙无敌暴龙战士（查军益 / 秦宗鑫 / 谭钧浩 / 周涛）"
prs.core_properties.subject = "创新工程实践营项目汇报"
prs.core_properties.comments = "第一部分 1.1 产品使命口号策略、1.2 产品定义、2 产品设计应用的原则"

prs.save(OUT)
print(f"saved: {OUT}")
print(f"slides: {len(prs.slides.__iter__.__self__._sldIdLst)}")
