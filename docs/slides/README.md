# 幻灯片与文档索引（docs/slides）

第一部分（1. 产品设计、2. 设计原则、3. 产品实现）的幻灯片与配套文档都在这个目录。

| 文件 | 给谁看 | 说明 |
| --- | --- | --- |
| [`slides.md`](slides.md) | **构建工具** | Slidev 源文件，34 页：1–18 为 1、2 节，19–34 为 3 节。含 HTML + UnoCSS 类名 + 内联 base64 图，不要当文档读 |
| [`style.css`](style.css) | 构建工具 | 主题：墨蓝 / 朱砂 / 纸白，标题、卡片、表格、占位框 |
| [`SLIDEV_README.md`](SLIDEV_README.md) | 开发 / 部署 | 本地 `pnpm dev`、GitHub Actions 四步上线、PDF 导出与排错 |
| [`Tome-Agent_第一部分_文字稿.md`](Tome-Agent_第一部分_文字稿.md) | **读** | 1、2 节的汇报正文稿（Markdown 标题 + 表格，无 HTML） |
| [`Tome-Agent_第一部分_产品设计与设计原则.pptx`](Tome-Agent_第一部分_产品设计与设计原则.pptx) | 投屏 / 交作业 | 1、2 节的 PPTX（18 页，可编辑） |
| [`Tome-Agent_第一部分_产品设计与设计原则.pdf`](Tome-Agent_第一部分_产品设计与设计原则.pdf) | 投屏 / 归档 | 与 PPTX 同版（18 页） |
| [`build_deck.py`](build_deck.py) / [`check_deck.py`](check_deck.py) | 生成 PPTX | `python build_deck.py` 重建 PPTX；`check_deck.py` 自检页数 / 越界 / 缺项 |
| [`check_slides.mjs`](check_slides.mjs) | 自检 | `node check_slides.mjs`：页数、小节与十二条原则覆盖、三个工作流 YAML 是否合法 |

> 说明：**PPTX / PDF / 文字稿只覆盖 1、2 节（18 页）**；第三部分「产品实现」目前在 Slidev 版里（第 19–34 页）。

## 本地预览

```powershell
cd docs\slides
pnpm install          # 首次
pnpm dev              # 浏览器打开 http://localhost:3030/
```

或静态预览（不依赖 dev server）：

```powershell
cd docs\slides
pnpm exec slidev build slides.md --out dist-local --base /
cd ..\..
python -m http.server 3040 --bind 127.0.0.1 --directory docs\slides\dist-local
```

## 部署（GitHub Actions）

工作流：[`.github/workflows/deploy-slides.yml`](../../.github/workflows/deploy-slides.yml)

- 触发：推送到 `main` / `master` 且改动 `docs/slides/**`；也可手动 `workflow_dispatch`
- 构建：`slidev build slides.md --out dist --base "/<仓库名>/"`
- 发布：`configure-pages` → `upload-pages-artifact` → `deploy-pages`
- 首次需要在 Settings → Pages → Source 选 `GitHub Actions`

详细步骤见 [SLIDEV_README.md](SLIDEV_README.md)。

## 改内容的三条路

1. 只改 Slidev：改 `slides.md`，`pnpm dev` 实时预览。
2. 只改 PPTX：直接编辑 `.pptx`（下次跑 `build_deck.py` 会覆盖，改动请同步回脚本）。
3. 两边都要一致：同时改 `slides.md` 与 `build_deck.py`，再各自重新生成。
