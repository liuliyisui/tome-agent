---
theme: default
title: Tome Agent · 让一个点子，长成一部自洽的长篇
info: |
  Tome Agent 项目汇报
  01 产品设计 · 02 设计原则 · 03 产品实现
author: 宇宙无敌暴龙战士（查军益 / 秦宗鑫 / 谭钧浩 / 周涛）
transition: fade
colorSchema: light
mdc: true
fonts:
  sans: 'Noto Sans SC, Source Han Sans SC, Microsoft YaHei, sans-serif'
  serif: 'Noto Serif SC, Source Han Serif SC, Songti SC, SimSun, serif'
  mono: 'JetBrains Mono, Cascadia Code, Consolas, monospace'
  provider: none
layout: cover
class: cover
---

<div class="cover-top">
    <div class="cover-brand">TOME AGENT <span>/</span> 项目汇报</div>
  <div class="cover-kicker">创新工程实践营 · 项目汇报 · 2026.11</div>
</div>

<div class="cover-grid">
  <div class="cover-copy">
    <div class="kicker light">A writing system for long-form fiction</div>
    <div class="cover-title">Tome<br>Agent<span class="cover-dot">.</span></div>
    <div class="cover-sub">让一个点子，<br>长成一部自洽的长篇。</div>
    <div class="cover-tags">
      <span>01 产品设计</span>
      <span>02 设计原则</span>
      <span>03 产品实现</span>
    </div>
  </div>
  <div class="cover-side">
    <div class="cover-side-rule"></div>
    <div class="cover-vertical">ONE IDEA · ONE NOVEL</div>
  </div>
</div>

<div class="cover-footer">
  <div class="cover-team">
    <div><b>查军益</b><span>开发 · 生成框架</span></div>
    <div><b>秦宗鑫</b><span>创作与质量评估</span></div>
    <div><b>谭钧浩</b><span>环境与功能测试</span></div>
    <div><b>周涛</b><span>体验与成果文档</span></div>
  </div>
  <div class="cover-repo">github.com/liuliyisui/tome-agent</div>
</div>

<!-- 开场：Tome Agent 是一套把长篇创作当成状态系统来管理的工具。 -->

---
layout: default
---

<div class="kicker">问题 / 为什么</div>

<div class="rule"></div>

<div class="problem-lead">
  <div>
    <div class="problem-quote">真正卡住长篇的，<b>是跨章状态。</b></div>
    <p class="problem-copy">长篇持续数周：几十次模型调用、上百个设定、不断被推翻又重建的情节。每一次调用都可能改变人物、时间线或伏笔位置。</p>
  </div>
  <div class="problem-facts">
    <div><b>1</b><span>部完整作品</span></div>
    <div><b>8–10</b><span>章连续叙事</span></div>
    <div><b>N</b><span>次模型调用</span></div>
  </div>
</div>

<div class="symptom-grid">
  <div class="symptom"><div class="symptom-no">01</div><div class="symptom-title">人物漂移</div><div class="symptom-text">性格、口癖、关系随章节变化。</div></div>
  <div class="symptom"><div class="symptom-no">02</div><div class="symptom-title">伏笔失踪</div><div class="symptom-text">第 2 章埋下的信物，到第 8 章无人再提。</div></div>
  <div class="symptom"><div class="symptom-no">03</div><div class="symptom-title">设定过期</div><div class="symptom-text">角色已经知道真相，叙事还当他不知道。</div></div>
  <div class="symptom"><div class="symptom-no">04</div><div class="symptom-title">中断即重来</div><div class="symptom-text">一次超时或格式错误，几万字回到起点。</div></div>
  <div class="symptom"><div class="symptom-no">05</div><div class="symptom-title">成本黑箱</div><div class="symptom-text">生成前不知道花多少，生成后对不上账。</div></div>
</div>

<div class="root-cause">
  <div class="root-label">同一个根因</div>
  <div class="root-text">记忆问题本质上是状态管理问题。</div>
  <div class="root-note">上下文会截断，摘要会失真，向量检索不能判断事实是否过期。</div>
</div>

<div class="bottom-note">来源：docs/requirements/problem_definition.md · docs/requirements/user_stories.md</div>

---
layout: default
---

<div class="kicker">产品定义 / 用户与使命</div>

<div class="rule"></div>

<div class="mission-strip">
  <div class="mission-card compact">
    <div class="tag">使命</div>
    <div class="mission-text">把「创作一部长篇」的门槛，从「会不会写」降到<em>「说不说得清一个想法」</em>。</div>
    <div class="mission-foot">系统记住该记的，作者专注创作判断。</div>
  </div>
  <div class="slogan-card compact">
    <div class="tag">主口号</div>
    <div class="slogan">一个点子，<br>一部自洽的长篇。</div>
    <div class="slogan-en">ONE IDEA. ONE COHERENT NOVEL.</div>
  </div>
</div>

<div class="persona-grid compact-personas">
  <div class="persona compact">
    <div class="persona-top"><span class="persona-index">01</span><span class="tag">核心用户</span></div>
    <div class="persona-title">第一次写长篇的读者</div>
    <div class="persona-row"><b>卡在哪里</b><span>写到第三章人物就乱，不敢重读。</span></div>
    <div class="persona-row"><b>我们要给</b><span>从想法到第 1 章，再到完整故事。</span></div>
  </div>
  <div class="persona compact">
    <div class="persona-top"><span class="persona-index">02</span><span class="tag">高价值用户</span></div>
    <div class="persona-title">小说作者</div>
    <div class="persona-row"><b>卡在哪里</b><span>设定复杂、伏笔多，最怕前后矛盾。</span></div>
    <div class="persona-row"><b>我们要给</b><span>状态与来源可追溯，改设定不重读全书。</span></div>
  </div>
  <div class="persona compact">
    <div class="persona-top"><span class="persona-index">03</span><span class="tag">延展用户</span></div>
    <div class="persona-title">小型内容团队</div>
    <div class="persona-row"><b>卡在哪里</b><span>进度分散、成本不透明、人一换就断。</span></div>
    <div class="persona-row"><b>我们要给</b><span>任务、用量、导出和可恢复的流程。</span></div>
  </div>
</div>

---
layout: default
---

<div class="kicker">产品定义 / 价值、差异化与形态</div>

<div class="rule"></div>

<div class="story-list compact-stories">
  <div class="story"><div class="story-no">01</div><div class="story-body"><div class="story-role">第一次写长篇的读者</div><div class="story-text">只给题材、主角和走向，先看到第 1 章，判断故事值不值得写。</div></div><div class="story-value">先看到<br>故事成立</div></div>
  <div class="story"><div class="story-no">02</div><div class="story-body"><div class="story-role">正在连载的作者</div><div class="story-text">每次改动都能查到设定出处和版本，不用重读全书。</div></div><div class="story-value">改动<br>有据可查</div></div>
  <div class="story"><div class="story-no">03</div><div class="story-body"><div class="story-role">需要交接的团队</div><div class="story-text">中断后能续写，完成后能导出 Markdown，交付不被锁定。</div></div><div class="story-value">随时<br>能带走</div></div>
</div>

<table class="compare compact-compare">
  <thead><tr><th>能力</th><th>通用聊天</th><th>写作插件</th><th class="is-us">Tome Agent</th></tr></thead>
  <tbody>
    <tr><td>跨章记忆</td><td>靠上下文，随时截断</td><td>局部设定，缺少全局</td><td class="is-us">结构化人物、时间、事件状态</td></tr>
    <tr><td>设定出处</td><td>没有稳定来源</td><td>版本弱</td><td class="is-us">版本 + 变更理由 + 正文出处</td></tr>
    <tr><td>断点恢复</td><td>重开对话，从头再来</td><td>有限恢复</td><td class="is-us">阶段检查点，保留已完成正文</td></tr>
    <tr><td>成本可见</td><td>不透明</td><td>部分可见</td><td class="is-us">生成前预估，生成后记录用量</td></tr>
    <tr><td>数据归属</td><td>复制粘贴</td><td>留在平台</td><td class="is-us">整本 Markdown，随时带走</td></tr>
  </tbody>
</table>

<div class="form-strip"><b>形态</b><span>浏览器打开</span><span>本机运行</span><span>一章一次事务</span><span>Markdown 导出</span></div>

<div class="bottom-note">来源：docs/requirements/user_stories.md · docs/algorithm/research.md · README「核心功能」</div>

---
layout: center
class: section
---

<div class="section-grid">
  <div class="section-no">02</div>
  <div class="section-body">
    <div class="kicker light">Design principles</div>
    <h1>设计原则</h1>
    <p>四组，六条。<br>每条原则都要落到一个动作、一份证据。</p>
  </div>
</div>

<div class="section-foot">Tome Agent · 产品设计 / 设计原则 / 产品实现</div>

<!-- 第二部分：六条原则要能回到仓库里的决策。 -->

---
layout: default
class: principle-page
---

<div class="principle-head">
  <div>
    <div class="kicker">原则组 I–II · 方向与系统</div>
  </div>
</div>

<div class="rule"></div>

<div class="p-rows">
  <div class="p-row">
    <div class="p-no">01</div>
    <div class="p-body"><div class="p-title">需求定方向</div><div class="p-text">先把问题定义、功能规格、用户故事写成文档；再用真实仓库状态、测试记录和框架文档校准判断，决定做什么、不做什么。</div></div>
    <div class="p-ev"><span>证据</span><code>docs/requirements/</code><em>docs/algorithm/architecture.md</em></div>
  </div>
  <div class="p-row">
    <div class="p-no">02</div>
    <div class="p-body"><div class="p-title">创新才有落脚点</div><div class="p-text">创新落在“事件先行 + 三层记忆 + 可恢复提交”，围绕作者能感知的问题迭代。</div></div>
    <div class="p-ev"><span>证据</span><code>docs/software/LANGGRAPH_MIGRATION.md</code><em>graph_runtime.py</em></div>
  </div>
  <div class="p-row">
    <div class="p-no">03</div>
    <div class="p-body"><div class="p-title">把作品当系统设计</div><div class="p-text">人物、物品、时间、事件分别建模；状态变化带版本，正文是状态的一次投影。</div></div>
    <div class="p-ev"><span>证据</span><code>code/core_engine/memory_runtime/</code><em>tiered_memory · events/continuity</em></div>
  </div>
</div>

---
layout: default
---

<div class="kicker">原则详解 / 需求与创新</div>

<div class="rule"></div>

<div class="deep-grid">
  <div class="deep-card">
    <div class="deep-head"><span class="deep-no">01</span><span class="tag">需求</span></div>
    <div class="deep-title">需求定方向</div>
    <div class="deep-row"><b>问题</b><span>长篇创作里的失忆、矛盾和中断，先被写成问题定义，再拆成功能。</span></div>
    <div class="deep-row"><b>做法</b><span>问题定义、功能规格、用户故事进仓库；三类用户分别对应核心、高价值和延展需求。</span></div>
    <div class="deep-row"><b>结果</b><span>每个功能都能回到具体痛点，不做的边界也写清楚。</span></div>
    <div class="deep-ev">docs/requirements/ · problem_definition · functional_spec · user_stories</div>
  </div>
  <div class="deep-card">
    <div class="deep-head"><span class="deep-no">02</span><span class="tag">创新</span></div>
    <div class="deep-title">创新才有落脚点</div>
    <div class="deep-row"><b>切口</b><span>创新放在跨章状态；模型文笔交给模型。</span></div>
    <div class="deep-row"><b>机制</b><span>事件先行、三层记忆、可恢复提交；LangGraph 只换编排层，领域逻辑复用。</span></div>
    <div class="deep-row"><b>结果</b><span>长篇能续写、能恢复、能追溯，创新变成可测试的工程机制。</span></div>
    <div class="deep-ev">LANGGRAPH_MIGRATION.md · graph_runtime.py · memory_runtime/</div>
  </div>
</div>

<div class="deep-foot">需求决定做什么，创新决定在哪里做得不一样。</div>

<div class="bottom-note">来源：docs/requirements/ · docs/software/LANGGRAPH_MIGRATION.md · code/core_engine/memory_runtime/</div>

---
layout: default
class: principle-page
---

<div class="principle-head">
  <div>
    <div class="kicker">原则组 III–IV · 取舍与质量</div>
  </div>
</div>

<div class="rule"></div>

<div class="p-rows">
  <div class="p-row">
    <div class="p-no">04</div>
    <div class="p-body"><div class="p-title">能继承的不重造</div><div class="p-text">复用已接入的模型适配、事件推演与记忆函数；LangGraph 只替换编排层，控制迁移范围。</div></div>
    <div class="p-ev"><span>证据</span><code>code/core_engine/memory_runtime/writing_flow/</code><em>graph_runtime.py · LANGGRAPH_MIGRATION.md</em></div>
  </div>
  <div class="p-row">
    <div class="p-no">05</div>
    <div class="p-body"><div class="p-title">算清效益</div><div class="p-text">不引入 ASGI、前端构建链和向量库；标准库 HTTP 与 Vue runtime-only，把省下的复杂度放在状态一致性和恢复上。</div></div>
    <div class="p-ev"><span>证据</span><code>README.md</code><em>「技术选型」与选型理由</em></div>
  </div>
  <div class="p-row">
    <div class="p-no">06</div>
    <div class="p-body"><div class="p-title">量化验收</div><div class="p-text">先保证一致性，再补恢复，最后谈速度和文风；Ruff、测试与 CI 同一套标准，测试数、覆盖率、失败率和 token 用量都有记录。</div></div>
    <div class="p-ev"><span>证据</span><code>.github/workflows/tests.yml</code><em>tests/TEST_REPORT.md · CODE_QUALITY_FIXES.md</em></div>
  </div>
</div>

---
layout: default
---

<div class="kicker">3.1 用户体验 / UX</div>

<div class="rule"></div>

<div class="ux-grid">
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">01</span><span class="tag">可用性</span></div>
    <div class="ux-title">打开浏览器就能写</div>
    <div class="ux-text">登录后进入自己的作品空间，账号之间数据隔离，无需安装客户端。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">02</span><span class="tag">连续性</span></div>
    <div class="ux-title">中断后还能接着写</div>
    <div class="ux-text">每个阶段保存检查点，保留已完成章节和待处理任务，恢复后继续下一步。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">03</span><span class="tag">成本</span></div>
    <div class="ux-title">调用前知道大概花多少</div>
    <div class="ux-text">生成前给出费用预估，生成后记录 token 与用量，避免越写越不敢调用。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">04</span><span class="tag">容错</span></div>
    <div class="ux-title">失败时保住已有正文</div>
    <div class="ux-text">超时、截断、坏 JSON 对用户可见；局部失败时保留有效内容并标记待处理。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">05</span><span class="tag">可控</span></div>
    <div class="ux-title">写作流程由作者掌握</div>
    <div class="ux-text">创建作品、配置文风、逐章或批量生成、修改、复查，最后导出 Markdown。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">06</span><span class="tag">安全</span></div>
    <div class="ux-title">技能只作文本，密钥留在服务端</div>
    <div class="ux-text">写作 Skill 只注入模型文本；敏感信息在本地检查，模型密钥不回传网页。</div>
  </div>
</div>

<div class="bottom-note">来源：README「核心功能」 · docs/software/USER_GUIDE.md · code/backend/inf_backend/web.py</div>

<!-- 3.1 用户体验：可用、连续、成本、容错、可控、安全。 -->

---
layout: default
class: tech-page
---

<div class="kicker">3.2–3.3 技术选型与代码仓库</div>

<div class="rule"></div>

<div class="tech-repo">
  <div>
    <table class="compare tech-table compact-tech">
      <thead><tr><th>条目</th><th>选型</th><th>版本</th><th>原因</th></tr></thead>
      <tbody>
        <tr><td>语言</td><td>Python</td><td>3.11</td><td>复用写作引擎与标准库测试</td></tr>
        <tr><td>编排</td><td>LangGraph</td><td>1.2.17</td><td>状态图表达规划、写作、审核</td></tr>
        <tr><td>前端</td><td>Vue runtime-only + 原生 JS</td><td>3.5.44</td><td>无前端构建链，部署轻</td></tr>
        <tr><td>服务</td><td>Python http.server</td><td>随 3.11</td><td>单机与单服务够用</td></tr>
        <tr><td>数据</td><td>PostgreSQL + Psycopg</td><td>PG 17 · 3.3.3</td><td>可选持久化，未配置降级文件</td></tr>
        <tr><td>模型</td><td>大部分 AI 大模型</td><td>Chat Completions</td><td>复用接口、计费预估与故障处理</td></tr>
      </tbody>
    </table>
  </div>
  <div class="repo-mini">
    <div class="tag">仓库地址</div>
    <a class="repo-url" href="https://github.com/liuliyisui/tome-agent">github.com/liuliyisui/tome-agent</a>
    <div class="repo-stats"><div><b>217</b><span>次提交</span></div><div><b>4</b><span>位贡献者</span></div><div><b>5</b><span>个模块</span></div></div>
    <img class="repo-chart-mini" src="/pulse-committers.png" alt="Top committers">
    <div class="small">提交分布见 Insights → Pulse；看板与路线图在 docs/mgmt/。</div>
  </div>
</div>

<div class="bottom-note">来源：README「技术选型」 · code/frontend/ · code/backend/ · docs/mgmt/</div>

---
layout: default
class: agensi-single
---

<div class="kicker">3.3 外部邀约 / AGENSI</div>

<div class="rule"></div>

<div class="agensi-mail"><img src="/agensi-email.jpg" alt="Agensi 来信：邀请把 Tome Agent 的工作流打包成 skill"></div>

<div class="bottom-note">来源：2026-11-17 Agensi（Joeri Brons）来信 · agensi.io</div>

---
layout: default
class: lifecycle-page
---

<div class="kicker">3.4 问题分析 / 解决方案</div>

<div class="rule"></div>

<table class="compare issue-table">
  <thead>
    <tr><th>问题类别</th><th>问题名称</th><th>发生原因</th><th>解决办法</th></tr>
  </thead>
  <tbody>
    <tr><td>分析</td><td>需求边界反复</td><td>演示原型与真实生成容易混在一起</td><td>原型只作交互演示；正式服务单独验证</td></tr>
    <tr><td>设计</td><td>编排框架迁移</td><td>迁移可能破坏已验证的领域逻辑</td><td>复用领域函数；只换编排层，回归验证</td></tr>
    <tr><td>开发</td><td>模型调用失败</td><td>超时、截断、坏 JSON</td><td>记录错误与用量；降级保留正文</td></tr>
    <tr><td>开发</td><td>长篇生成中断</td><td>一次成稿多次调用，耗时长</td><td>阶段检查点；恢复时识别待处理任务</td></tr>
    <tr><td>测试</td><td>文件与数据库双写</td><td>两份记录不在同一事务</td><td>故障演练；明确未覆盖边界</td></tr>
    <tr><td>部署运维</td><td>旧版本无法续写</td><td>旧检查点哈希与新源码不一致</td><td>保留旧代码与作品；新版本重建检查点</td></tr>
    <tr><td>运维</td><td>成本不可预测</td><td>token 计费随上下文变化</td><td>费用预估、用量记录、用户确认</td></tr>
  </tbody>
</table>

<div class="bottom-note">来源：docs/software/ISSUES_SUMMARY.md · docs/software/architecture.md · tests/TEST_REPORT.md</div>

<!-- 3.4 全生命周期：主要问题、发生原因、解决办法与仓库证据。 -->

---
layout: default
---

<div class="kicker">3.5.1–3.5.2 架构与仓库结构</div>

<div class="rule"></div>

```mermaid {theme: 'base', themeCSS: '.node rect{fill:#F6F3E9 !important;stroke:#1E4A36 !important;rx:4px;ry:4px}.node polygon{fill:#F6F3E9 !important;stroke:#1E4A36 !important}.nodeLabel{fill:#1F3026 !important;font-family:Noto Sans SC,Microsoft YaHei,sans-serif !important;font-size:12.5px !important;line-height:1.35 !important}.edgePath .path{stroke:#7D9274 !important;stroke-width:1.5px !important}.marker{fill:#7D9274 !important;stroke:#7D9274 !important}.labelBkg{background:#F6F3E9 !important}.labelBkg p{background:transparent !important;color:#5D7355 !important}.edgeLabel{background:#F6F3E9 !important;color:#5D7355 !important}', scale: 0.82}
flowchart LR
  UI["界面层<br/>Vue · 书架 / 编辑"] -->|HTTP| API["服务层<br/>inf_backend/"]
  API -->|调用| ENGINE["引擎层<br/>core_engine/"]
  ENGINE -->|读写| STORE["存储层<br/>schema.sql · data/"]
  ENGINE -. "旁路调用" .-> MODEL["模型服务<br/>chat_provider.py"]
```

<div class="infra-row">
  <div class="ux-card"><div class="tag">前端</div><div class="ux-title">code/frontend/</div><div class="ux-text">Vue runtime-only；书架、编辑、导出。</div></div>
  <div class="ux-card"><div class="tag">服务</div><div class="ux-title">inf_backend/</div><div class="ux-text">HTTP 路由、参数校验、存储适配。</div></div>
  <div class="ux-card"><div class="tag">引擎</div><div class="ux-title">core_engine/</div><div class="ux-text">LangGraph 编排、三层记忆、写作流程。</div></div>
</div>

<div class="arch-legend">
  <span><i class="solid"></i>同步请求</span>
  <span><i class="dash"></i>模型旁路</span>
  <span class="legend-note">模型服务不直接访问存储</span>
</div>

<div class="arch-foot"><span>请求路径</span> 界面动作 → 服务层校验 → 引擎编排 → 检查点 / 数据库提交 → 结果回传。</div>

<div class="bottom-note">来源：docs/software/architecture.md · code/frontend/ · code/backend/inf_backend/ · code/core_engine/</div>

---
layout: default
---

<div class="kicker">3.5.3 智能体设计 · 五个组成</div>

<div class="workflow-figure"><img src="/agent-components.png" alt="Tome Agent 智能体五个组成与代码位置"></div>

<div class="bottom-note">来源：code/core_engine/ · planner.py · event_first.py · writing.py · tiered_memory.py · guardrails.py · editing.py</div>

---
layout: default
---

<div class="kicker">3.5.4 智能体要素 · 工作流</div>

<div class="workflow-figure"><img src="/story-workflow.png" alt="Tome Agent 故事创作工作流"></div>

<div class="bottom-note">读法：实线是主链，虚线是后续检索，回环是需要时有限次修订。来源：docs/algorithm/LANGGRAPH.mmd · code/core_engine/</div>

---
layout: default
---

<div class="kicker">3.5.4 智能体要素 · 类 RAG 流程</div>

<div class="workflow-figure"><img src="/rag-flow.png" alt="Tome Agent 类 RAG 流程"></div>

<div class="bottom-note">检索时工作记忆优先；近期与长期记忆按词面匹配、规则和预算选择；相关记忆、来源证据和故事状态一起组装上下文。来源：docs/algorithm/LANGGRAPH.mmd · code/core_engine/</div>

---
layout: default
---

<div class="kicker">3.5.5–3.5.6 接口与前端</div>

<div class="rule"></div>

<table class="compare interface-table compact-interface">
  <thead><tr><th>方法</th><th>路径</th><th>输入</th><th>输出</th></tr></thead>
  <tbody>
    <tr><td>GET</td><td><code>/api/books</code></td><td>—</td><td>作品列表</td></tr>
    <tr><td>POST</td><td><code>/api/books/{id}/generate</code></td><td>选项 / 模型配置</td><td>job_id</td></tr>
    <tr><td>POST</td><td><code>/api/books/{id}/chapters/{n}/edit</code></td><td>正文 / base_revision</td><td>保存结果</td></tr>
    <tr><td>GET</td><td><code>/api/jobs/{id}</code></td><td>—</td><td>进度 / 结果</td></tr>
    <tr><td>GET</td><td><code>/api/books/{id}/export</code></td><td>—</td><td>Markdown</td></tr>
  </tbody>
</table>

<div class="ui-shot-grid compact-shots">
  <div class="ui-shot"><img src="/frontend-login.png" alt="登录"><div class="ui-shot-cap"><b>登录</b><span>账号进入工作区</span></div></div>
  <div class="ui-shot"><img src="/frontend-home.png" alt="首页"><div class="ui-shot-cap"><b>首页</b><span>品牌入口与开始写作</span></div></div>
  <div class="ui-shot"><img src="/frontend-library.png" alt="书架"><div class="ui-shot-cap"><b>书架</b><span>作品列表与新建入口</span></div></div>
</div>

<div class="bottom-note">来源：code/backend/inf_backend/web.py · code/frontend/ · README「核心功能」</div>

---
layout: default
---

<div class="kicker">3.6–3.7 质量与代码</div>

<div class="rule"></div>

<div class="quality-stats compact-stats">
  <div class="q-stat"><div class="q-num">256</div><div class="q-label">测试通过</div></div>
  <div class="q-stat"><div class="q-num">0</div><div class="q-label">失败 / 跳过</div></div>
  <div class="q-stat"><div class="q-num">67.52%</div><div class="q-label">核心 8 模块覆盖率</div></div>
  <div class="q-stat"><div class="q-num">103</div><div class="q-label">超阈函数</div></div>
</div>

<div class="quality-code-grid">
  <div>
    <div class="subhead">质量工具</div>
    <div class="quality-row"><b>Ruff</b><span>format 191 文件符合 PEP8；check 0 违规</span></div>
    <div class="quality-row"><b>Pylint</b><span>9.62 / 10 · 0 error · 0 fatal</span></div>
    <div class="quality-row"><b>McCabe</b><span>阈值 10；103 个函数超阈，按文件分批重构</span></div>
    <div class="quality-row"><b>CI</b><span>lint / test / PostgreSQL 17–18 / hosted 回归</span></div>
  </div>
  <div>
    <div class="subhead">代码统计</div>
    <div class="code-ledger"><div><b>214</b><span>提交</span></div><div><b>129</b><span>生产文件</span></div><div><b>43,962</b><span>行 Python</span></div><div><b>5.4:1</b><span>生产:测试</span></div></div>
    <div class="quality-row"><b>测试</b><span>256 项；真实模型端到端 · PostgreSQL 验证</span></div>
    <div class="quality-row"><b>AI 比例</b><span>辅助约 80%；人工审查、测试后合入</span></div>
  </div>
</div>

<div class="bottom-note">来源：tests/TEST_REPORT.md · docs/software/quality/QUALITY_REPORT.md · docs/slides/slides.md</div>

---
layout: default
---

<div class="kicker">现场演示 / 2 MIN DEMO</div>

# 现场演示：2 分钟从想法到第 1 章。

<div class="rule"></div>

<div class="demo-grid">
  <div class="demo-card">
    <div class="demo-no">01</div>
    <div class="demo-title">书架</div>
    <div class="demo-text">打开工作台，选中已有作品或新建一部作品。</div>
  </div>
  <div class="demo-card">
    <div class="demo-no">02</div>
    <div class="demo-title">设定</div>
    <div class="demo-text">填题材、主角、走向和文风，确认费用预估。</div>
  </div>
  <div class="demo-card">
    <div class="demo-no">03</div>
    <div class="demo-title">生成</div>
    <div class="demo-text">触发第 1 章，展示规划、事件推演与正文进度。</div>
  </div>
  <div class="demo-card">
    <div class="demo-no">04</div>
    <div class="demo-title">记忆</div>
    <div class="demo-text">打开人物卡和事实来源，指出版本与正文出处。</div>
  </div>
  <div class="demo-card">
    <div class="demo-no">05</div>
    <div class="demo-title">恢复</div>
    <div class="demo-text">刷新或重进，展示检查点、已完成正文和待处理任务。</div>
  </div>
  <div class="demo-card">
    <div class="demo-no">06</div>
    <div class="demo-title">导出</div>
    <div class="demo-text">复查后导出 Markdown，回到书架，数据仍在。</div>
  </div>
</div>

<div class="bottom-note">来源：README「核心功能」 · docs/software/USER_GUIDE.md · tests/TEST_REPORT.md</div>

<!-- 现场演示：2 分钟从想法到第 1 章，六步路径固定。 -->

---
layout: default
---

<div class="kicker">小结 / SUMMARY</div>

<div class="rule"></div>

<div class="summary-grid">
  <div class="summary-col">
    <div class="summary-index">01</div>
    <div class="summary-title">产品</div>
    <div class="summary-line">一个点子，<br>一部自洽的长篇。</div>
    <div class="summary-detail">目标用户、价值主张、差异化与产品形态</div>
  </div>
  <div class="summary-col">
    <div class="summary-index">02</div>
    <div class="summary-title">原则</div>
    <div class="summary-line">四组六条，<br>每条都有证据。</div>
    <div class="summary-detail">从需求、系统、取舍到质量</div>
  </div>
  <div class="summary-col">
    <div class="summary-index">03</div>
    <div class="summary-title">实现</div>
    <div class="summary-line">状态图 + 三层记忆<br>+ 一章一事务。</div>
    <div class="summary-detail">四层架构、真实路由、可恢复提交</div>
  </div>
</div>

<div class="summary-stats">
  <div><b>185</b><span>次提交</span></div>
  <div><b>5</b><span>个模块</span></div>
  <div><b>6</b><span>张数据表</span></div>
  <div><b>4</b><span>类 CI job</span></div>
</div>

<div class="summary-links">
  <div><span>REPO</span>github.com/liuliyisui/tome-agent</div>
  <div><span>SLIDES</span>liuliyisui.github.io/tome-agent/</div>
</div>

<div class="bottom-note">来源：README.md · docs/software/architecture.md · tests/TEST_REPORT.md · git log</div>

<!-- 收束：产品、原则、实现三句话；最后给出仓库和幻灯片地址。 -->

