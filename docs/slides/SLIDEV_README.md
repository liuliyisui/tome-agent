 Tome Agent 汇报幻灯片（Slidev 版）

这套幻灯片用 [Slidev](https://sli.dev) 写成：**内容是一份 Markdown**，样式在一个 CSS 里，构建、发布、导出 PDF 全部交给 GitHub Actions。
和 `../Tome-Agent_第一部分_产品设计与设计原则.pptx`（python-pptx 版）内容一致，两者可以互为备份。

```
docs/slides/
├── slides.md                 # 全部 18 页内容（每页之间用 --- 分隔，<!-- --> 是演讲备注）
├── style.css                 # 视觉规范：墨蓝 / 朱砂 / 纸白，标题、卡片、表格样式
├── package.json              # 依赖与命令（dev / build / export）
├── pnpm-workspace.yaml       # pnpm 策略：扁平 node_modules、不自动装 optional peer
├── pnpm-lock.yaml            # 锁文件，CI 用 --frozen-lockfile 安装
├── check_slides.mjs          # 自检：页数、小节覆盖、工作流 YAML 是否合法
└── .gitignore
.github/workflows/
├── deploy-slides.yml         # push → 构建 → 发布到 GitHub Pages
└── export-slides-pdf.yml     # 手动触发 → 导出 PDF → 上传 artifact
```

---

## 一、本地跑起来（3 条命令）

前置：Node.js ≥ 20、pnpm 11（`npm i -g pnpm@11.28.5`，或 Node 自带的 `corepack enable pnpm`）。

> **没装 pnpm 也能跑**：`node_modules` 里已经有 CLI 的启动脚本，直接调用即可（注意 `.CMD` 后缀）：
>
> ```powershell
> cd slides\slidev
> .\node_modules\.bin\slidev.CMD slides.md --open
> ```

```bash
cd docs/slides
pnpm install          # 装依赖（首次约 1–2 分钟）
pnpm dev              # 打开 http://localhost:3030 实时预览，改 slides.md 自动刷新
pnpm exec slidev build slides.md --out dist --base /tome-agent/   # 只构建不预览
```

`pnpm-workspace.yaml` 里有两个设置是刻意加的，别删：

- `nodeLinker: hoisted`：Windows 上 pnpm 默认的软链/junction 布局会让 Slidev 的 ESM 解析报
  `ERR_MODULE_NOT_FOUND: pathe`，改成扁平 node_modules 后恢复正常。
- `autoInstallPeers: false`：`playwright-chromium` 是 `@slidev/cli` 的 optional peer，自动装上会让
  `pnpm install` 因为没有批准 postinstall 而返回非 0（CI 直接失败），而且每次部署都多下 150 MB 浏览器。

`pnpm build` 脚本里已经写好 `--base /tome-agent/`，因为仓库是 `liuliyisui/tome-agent`；
**换了仓库名就要改这个 base**，否则发布后页面白屏（静态资源 404）。

---

## 二、GitHub Actions 步骤（首次配置 4 步）

### 第 1 步：提交文件

```bash
git add docs/slides .github/workflows/deploy-slides.yml .github/workflows/export-slides-pdf.yml
git commit -m "slides: add Slidev deck for part 1 and Pages deploy workflow"
git push origin master
```

`node_modules/` 和 `dist/` 已被 `.gitignore` 忽略，不要提交。

### 第 2 步：打开 Pages（只做一次）

仓库 → **Settings → Pages → Build and deployment → Source 选 `GitHub Actions`**。
不选这一步，`actions/configure-pages` 会报 *“Get Pages site failed / Pages is not enabled”*。

### 第 3 步：让它跑起来

推送到 `main` / `master` 且改动了 `docs/slides/**` 时自动触发；也可以在
**Actions → Deploy slides (Slidev) → Run workflow** 手动触发。

工作流 5 个关键环节：

| 环节 | 做什么 | 用到的 action / 命令 |
| --- | --- | --- |
| 1 | 装 pnpm（版本与 lockfile 对齐） | `pnpm/action-setup@v4`，`version: 11.28.5` |
| 2 | 装 Node 22 并缓存 pnpm 依赖 | `actions/setup-node@v4`，`cache: pnpm` |
| 3 | 装依赖 | `pnpm install --frozen-lockfile`（lockfile 不一致会直接失败，避免“本地能跑线上不一样”） |
| 4 | 构建 | `slidev build slides.md --out dist --base "/<仓库名>/"` |
| 5 | 发布 | `actions/configure-pages` → `actions/upload-pages-artifact` → `actions/deploy-pages` |

### 第 4 步：访问

构建完成后，Actions 里 `Deploy` 任务会打出地址：
`https://<用户名>.github.io/<仓库名>/` —— 本次应为
**https://liuliyisui.github.io/tome-agent/**。

首次部署生效可能需要 1–2 分钟，`github-pages` 环境下能看到部署记录与历史版本。

### 方案 B：静态预览（dev server 起不来时用这个）

构建一份以 `/` 为基准的副本，再用 Python 自带的静态服务器托管 —— 不依赖 HMR、不占 Node 端口：

```powershell
cd slides\slidev
pnpm exec slidev build slides.md --out dist-local --base /
cd ..\..
python -m http.server 3040 --bind 127.0.0.1 --directory slides\slidev\dist-local
```

浏览器打开 **http://127.0.0.1:3040/**（IPv4，比 dev server 的 `localhost` 兼容性更好）。
注意 `--base /` 和 GitHub Pages 用的 `--base /仓库名/` 是两回事：前者用于本地根路径托管，后者用于项目站子路径。

放映快捷键：`←/→` 或空格翻页，`o` 总览，`p` 演讲者视图（含备注），`f` 全屏，`d` 暗色。

---

## 三、导出 PDF（可选）

两条路：

1. **云端**：Actions → **Export slides PDF (Slidev)** → Run workflow，跑完在 Artifacts 下载 `slides-pdf`。
2. **本地**：

   ```bash
   cd docs/slides
   pnpm add -D playwright-chromium@1.65.1 --ignore-scripts   # 临时装导出用的浏览器驱动
   pnpm exec playwright install chromium                     # 只需一次，约 120 MB
   pnpm export                                               # 输出 dist/tome-agent-part1.pdf
   ```

   导完如果不想让 `pnpm install` 每次都装上它，`pnpm remove playwright-chromium` 即可——
   工作流里的做法也一样：先 `pnpm add --ignore-scripts`，再 `playwright install chromium`。

导出必须装 Chromium 和**中文字体**，否则 PDF 里的中文会变成方框。工作流里已经加了
`fonts-noto-cjk`，本地 Windows / macOS 自带中文字体，无需额外处理。

---

## 四、改内容与常见问题

| 现象 | 原因与处理 |
| --- | --- |
| `pnpm : 无法将“pnpm”项识别为 cmdlet…` | 系统没装 pnpm（Node 装了不代表 pnpm 装了）。`npm i -g pnpm@11.28.5`，或改用 `.\node_modules\.bin\slidev.CMD slides.md` |
| VS Code 里点 “Slidev: Open Preview” 没反应 | 没装扩展 `antfu.slidev`；或在 VS Code 自带 Markdown 预览里看 `slides.md`（只能看到裸露的 HTML）。用终端启动后开浏览器 |
| 页面白屏、控制台大量 404 | `base` 与仓库名不一致。改 `package.json` 的 `build` 脚本，或工作流里的 `--base` |
| Actions 报 lockfile 不一致 | 本地 pnpm 版本和 `version: 11.28.5` 不同。用同一版本重新 `pnpm install` 后提交 lockfile |
| PDF 中文变方框 | 缺少 CJK 字体；确认执行了 `fonts-noto-cjk` 那一步 |
| 导出超时 | 页数多或机器慢；把 `--timeout` 从 180000 调大 |
| 只改 CSS 没重新构建 | `paths` 只匹配 `docs/slides/**`，CSS 在该目录内，会触发；改工作流本身也会触发 |
| 想改单页 | 在 `slides.md` 里找对应 `---` 分隔块；`<!-- ... -->` 是演讲备注，不在放映画面里显示 |

**版式约定**（`style.css` 已定义，写新页直接套）：

- 页眉：`<div class="eyebrow">章节号</div>` + `# 一句话结论`
- 分隔线：`<div class="hr-line"></div>`
- 卡片：`card`（浅）/ `card-soft`（更浅）/ `card-dk`（墨蓝底白字）
- 小标签：`tag`；正文：`body-text`；次要说明：`small`
- 网格直接用 UnoCSS：`grid grid-cols-3 gap-3`

改完跑一下自检（页数、小节覆盖、两个工作流 YAML 是否合法）：

```bash
node check_slides.mjs
# 期望：页数 17 / 缺少的小节·原则: 无 / 三个工作流 OK
```

---

## 五、为什么用 Slidev + Actions 而不是直接交 PPTX

- **可 diff**：内容在 Markdown 里，改一个标题就是一个单行 diff，评审和协作都看得见。
- **不会丢版**：构建产物由 CI 生成，谁拉代码都能得到同一份页面，不依赖某台电脑上的 Office 版本。
- **顺手多一个 PDF**：同一个源，`export` 就能出 PDF 交作业，网页版还能在浏览器里当演示稿翻页。
- **代价**：设计自由度不如手摆 PPT，图表、复杂矢量图仍建议在 PPTX 里做，用 Slidev 做“讲得清”的那部分。
