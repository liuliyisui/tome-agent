# 幻灯片与文档索引

| 文件 | 给谁看 | 说明 |
| --- | --- | --- |
| [`Tome-Agent_第一部分_产品设计与设计原则.pptx`](Tome-Agent_第一部分_产品设计与设计原则.pptx) | 投屏 / 交作业 | 18 页，可编辑；用 PowerPoint / WPS 打开 |
| [`Tome-Agent_第一部分_产品设计与设计原则.pdf`](Tome-Agent_第一部分_产品设计与设计原则.pdf) | 投屏 / 归档 | 与 PPTX 同版，18 页 |
| [`Tome-Agent_第一部分_文字稿.md`](Tome-Agent_第一部分_文字稿.md) | **读** | 汇报正文稿：Markdown 标题、表格、要点，没有 HTML 和图片编码 |
| [`slidev/slides.md`](slidev/slides.md) | **不要直接读** | Slidev 源文件：HTML + UnoCSS 类名 + 内联 base64 图，给构建工具用 |
| [`slidev/`](slidev/) | 开发 / 部署 | `pnpm dev` 预览；GitHub Actions 构建并发布到 Pages，见 [slidev/README.md](slidev/README.md) |
| `build_deck.py` / `check_deck.py` | 生成 PPTX | `python build_deck.py` 重新生成 PPTX；`check_deck.py` 自检页数、越界、缺项 |

## 常见困惑

- **在 VS Code 里打开 `slidev/slides.md` 看到一堆 `<div class="...">` 和长串 base64**：这是正常的，那是待编译的源码，不是给人读的。
- **要看内容**：读 `Tome-Agent_第一部分_文字稿.md`（文字稿），或者直接打开 PPTX / PDF。
- **要看效果**：`cd slidev && pnpm dev`，浏览器打开 http://localhost:3030/ 。

## 改内容的三条路

1. 只改 PPTX → 直接编辑 `.pptx`（但下次跑 `build_deck.py` 会覆盖，改动请同步回脚本）。
2. 只改 Slidev → 改 `slidev/slides.md`，`pnpm dev` 实时预览。
3. 两边都要一致 → 同时改 `slidev/slides.md` 与 `build_deck.py`，再各自重新生成。
