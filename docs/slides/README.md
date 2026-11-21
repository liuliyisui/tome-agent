# Tome Agent 汇报幻灯片（Slidev）

[Slidev](https://cn.sli.dev/) 把一页页 Markdown 构建成可翻页的网页演示，并能导出 PDF。本目录包含 23 页中文幻灯片，覆盖：

- 01 产品设计：问题、使命、用户、价值主张、差异化、产品形态
- 02 设计原则：四组共十二条，每条原则对应仓库证据
- 03 产品实现：四层架构、LangGraph 编排、三层记忆、数据接口、质量保障

部署后地址：<https://liuliyisui.github.io/tome-agent/>

## 目录

| 文件 | 作用 |
| --- | --- |
| `slides.md` | 幻灯片正文；`---` 分隔页面，`<!-- -->` 是演讲备注 |
| `style.css` | 纸白 / 墨蓝 / 朱砂主题，封面、章节页、卡片、表格样式 |
| `package.json` | Slidev 依赖及 `dev` / `build` / `check` / `export` 命令 |
| `package-lock.json` | CI 使用 `npm ci` 的锁定版本 |
| `scripts/check-build.mjs` | 构建后检查 `index.html`、base 路径和静态资源是否存在 |
| `scripts/export-pdf.mjs` | 逐页渲染 PNG，再用 `pdf-lib` 合成 PDF |
| `public/` | 需要原样复制到构建产物的静态文件 |

架构图和 LangGraph 状态图由 Mermaid 代码块生成，不依赖外部图片：

```mermaid
flowchart LR
  PLAN["规划"] --> WRITE["写作"] --> COMMIT["提交"] --> MEMORY["记忆"] --> REVIEW["审核"]
  WRITE -. "revise" .-> PLAN
```

## 本地预览

前置：Node.js 20+（CI 使用 22）。

```bash
cd docs/slides
npm ci
npm run dev
```

浏览器打开 <http://localhost:3030>。快捷键：`←` / `→` 翻页，`o` 总览，`p` 演讲者视图，`f` 全屏。

只构建、不启动 dev server：

```bash
npm run build:local
python -m http.server 3040 --bind 127.0.0.1 --directory dist-local
# 打开 http://127.0.0.1:3040/
```

`build:local` 使用 `--base /`；部署到 GitHub Pages 时必须使用仓库子路径，见下文。

## GitHub Actions 部署

工作流：[`.github/workflows/slides-pages.yml`](../../.github/workflows/slides-pages.yml)

触发条件：

- push 到 `main` 且改动 `docs/slides/**` 或该工作流本身
- Pull Request 改动同一范围：只构建和校验，不发布
- 手动 `workflow_dispatch`

流程：

1. `actions/setup-node@v5` 安装 Node 22，并按 `docs/slides/package-lock.json` 缓存 npm
2. `npm ci` 安装锁定依赖
3. `npm run build -- --base "/<仓库名>/"` 构建
4. 内联校验 `dist/index.html`、base 路径以及 JS/CSS 资源
5. `actions/configure-pages@v5` 配置 Pages，并尝试用 `enablement: true` 自动启用
6. `actions/upload-pages-artifact@v5` 上传构建产物
7. `actions/deploy-pages@v5` 发布到 GitHub Pages

首次使用前，仓库 owner 需要做一次设置：

> **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。

工作流调用了 `actions/configure-pages@v5` 的 `enablement: true`，在仓库策略允许时会尝试自动创建 Pages 站点；如果组织策略不允许，仍会报 “Get Pages site failed / Pages is not enabled”，此时按上面的设置手动开启即可。这是仓库设置问题，不是构建脚本问题。

访问地址：`https://<用户名>.github.io/<仓库名>/`。本项目为 <https://liuliyisui.github.io/tome-agent/>。

## 导出 PDF

工作流：[`.github/workflows/slides-pdf.yml`](../../.github/workflows/slides-pdf.yml)

在 Actions 页面选择 **Slides / Export PDF → Run workflow**，可以填写要导出的 Markdown 文件名（默认 `slides.md`）。工作流会：

- 安装 `fonts-noto-cjk`，避免中文变成方框
- 临时安装 `playwright-chromium`，再安装 Chromium
- 用 `npm run export` 逐页渲染 PNG，再用 `pdf-lib` 合成 PDF
- 将 PDF 上传为 `slides-pdf` artifact

> PDF 采用“逐页渲染 + 图片合成”，保证 Mermaid、CSS 渐变和中文在 GitHub Actions 里与网页版一致；代价是 PDF 里的文字不可选中。需要可选中文字时，请在本地用浏览器打印网页版。

本地导出：

```bash
cd docs/slides
npm install --no-save --ignore-scripts playwright-chromium@1.65.1
npx playwright install chromium
npm run export
# 输出 dist/tome-agent-slides.pdf
```

`npm run export` 调用 `scripts/export-pdf.mjs`：先执行 `slidev export --format png --per-slide`，再用 `pdf-lib` 按 960×540 pt 拼成 23 页 PDF。`pdf-lib` 已写入 `devDependencies`。

本地 Windows / macOS 通常已有中文字体；Linux 需要先安装 `fonts-noto-cjk`。

## 修改幻灯片

1. 在 `slides.md` 中找到目标页的 `---` 分隔块。
2. 页首 frontmatter 控制布局，例如 `layout: cover`、`layout: center`、`class: section`。
3. 视觉样式集中在 `style.css`；新增页尽量复用 `.kicker`、`.rule`、`.cols`、`.card`、`.tag`、`.bottom-note` 等类。
4. Mermaid 图直接写 ` ```mermaid ` 代码块；节点文字要短，避免图过高。
5. 改完运行：

```bash
npm run build:local
```

构建失败时先看终端里的 Slidev / Vite 错误；`Element is missing end tag` 通常表示 Markdown 里 HTML 标签没有闭合。

## 常见问题

| 现象 | 原因与处理 |
| --- | --- |
| 页面白屏、资源 404 | `--base` 与仓库名不一致。Pages 构建使用 `/<仓库名>/`；本地根路径预览用 `/` |
| `npm ci` 报 lockfile 不一致 | 本地 Node/npm 版本与 CI 不同；用 Node 22 和 npm 11 重新 `npm install` 后提交 `package-lock.json` |
| Actions 报 Pages 未启用 | 在 Settings → Pages 把 Source 改为 GitHub Actions |
| PDF 中文变方框 | 缺少 CJK 字体；确认安装了 `fonts-noto-cjk` |
| Mermaid 图溢出页面 | 缩短节点文字，使用 `flowchart LR`，避免 `flowchart TB` 叠太高 |
| 修改 CSS 后线上没变 | 确认 push 改动了 `docs/slides/**`；工作流按路径触发 |

## 设计约定

- **纸白底、墨蓝字、朱砂强调**：`--paper` / `--navy` / `--red` 三个变量控制全局。
- **每页一个结论**：标题写判断，正文给证据；来源放在页脚。
- **少即是多**：一页最多三张卡片或一组表格；需要更多内容时拆页。
- **图和文互补**：Mermaid 负责结构，卡片负责解释，避免图里重复长句。
