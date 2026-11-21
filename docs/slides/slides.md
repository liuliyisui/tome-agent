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

<div class="kicker">问题 / WHY</div>

# 模型能写好一段，<br>却记不住一整部。

<div class="rule"></div>

<div class="cols cols-2 gap-lg">
  <div>
    <p class="lede">长篇创作持续数周：几十次模型调用、上百个设定、不断被推翻又重建的情节。</p>
    <div class="stat-row">
      <div class="stat-cell">
        <div class="stat-num">1</div>
        <div class="stat-label">部完整作品</div>
      </div>
      <div class="stat-cell">
        <div class="stat-num">8–10</div>
        <div class="stat-label">章连续叙事</div>
      </div>
      <div class="stat-cell">
        <div class="stat-num">N</div>
        <div class="stat-label">次模型调用</div>
      </div>
    </div>
    <p class="muted mt-2">每一次调用都可能改变人物状态、时间线或伏笔位置。难点在下一章：人物、时间线和伏笔是否还记得住。</p>
  </div>

  <div class="card-dark quote-card">
    <div class="quote-mark">“</div>
    <div class="quote">真正卡住长篇的，<br>是<b>跨章状态</b>。</div>
    <div class="quote-sub">人物、物品、时间、伏笔、知识来源——只要有一个漂移，读者就会出戏。</div>
    <div class="quote-line"></div>
    <div class="quote-foot">Tome Agent 的答案：把长篇拆成可提交、可恢复、可追溯的状态变更。</div>
  </div>
</div>

<div class="bottom-note">来源：docs/requirements/problem_definition.md · docs/software/architecture.md</div>

<!-- 先给判断：长篇的瓶颈在跨章状态。 -->

---
layout: default
---

<div class="kicker">问题 / 五个症状</div>

# 读者先感到“看不下去了”，<br>问题通常已经积累了几章。

<div class="rule"></div>

<div class="symptom-grid">
  <div class="symptom">
    <div class="symptom-no">01</div>
    <div class="symptom-title">人物漂移</div>
    <div class="symptom-text">上一章左撇子，下一章用右手开门。性格、口癖、关系随章节变化。</div>
  </div>
  <div class="symptom">
    <div class="symptom-no">02</div>
    <div class="symptom-title">伏笔失踪</div>
    <div class="symptom-text">第 2 章埋下的信物，到第 8 章没有人再提起，读者比作者记得更清楚。</div>
  </div>
  <div class="symptom">
    <div class="symptom-no">03</div>
    <div class="symptom-title">设定过期</div>
    <div class="symptom-text">角色已经知道真相，叙事却还当他不知道；时间线悄悄倒退。</div>
  </div>
  <div class="symptom">
    <div class="symptom-no">04</div>
    <div class="symptom-title">中断即重来</div>
    <div class="symptom-text">一次超时、一次格式错误，几万字的进度回到起点，作者不敢再写。</div>
  </div>
  <div class="symptom">
    <div class="symptom-no">05</div>
    <div class="symptom-title">成本黑箱</div>
    <div class="symptom-text">生成前不知道要花多少，生成后对不上账，越写越不敢调用。</div>
  </div>
</div>

<div class="root-cause">
  <div class="root-label">同一个根因</div>
  <div class="root-text">记忆问题本质上是状态管理问题。</div>
  <div class="root-note">上下文窗口会截断，摘要会失真，向量检索不能判断一条事实是否已经过期。</div>
</div>

<div class="bottom-note">来源：docs/requirements/problem_definition.md · docs/requirements/user_stories.md</div>

<!-- 五个症状对应五类用户痛点，最后收束到一个根因。 -->

---
layout: default
---

<div class="kicker">产品定义 / 使命与口号</div>

# 先把「记得住」做对，<br>再谈「写得好」。

<div class="rule"></div>

<div class="cols cols-2 gap-lg">
  <div class="mission-card">
    <div class="tag">使命</div>
    <div class="mission-text">把「创作一部长篇」的门槛，<br>从「会不会写」降到<br><em>「说不说得清一个想法」</em>。</div>
    <div class="mission-foot">把系统该记的东西交还给系统，让作者专注创作判断。</div>
  </div>

  <div class="slogan-card">
    <div class="tag">主口号</div>
    <div class="slogan">一个点子，<br>一部自洽的长篇。</div>
    <div class="slogan-en">ONE IDEA. ONE COHERENT NOVEL.</div>
    <div class="slogan-line"></div>
    <div class="small">对外一句话，界面、README、答辩开场都用同一句，不另起说法。</div>
  </div>
</div>

<div class="criteria">
  <div class="criterion">
    <div class="criterion-num">A</div>
    <div><b>门槛</b><span>给得出题材、主角和走向，就能拿到第 1 章。</span></div>
  </div>
  <div class="criterion">
    <div class="criterion-num">B</div>
    <div><b>质量</b><span>每条设定都有版本、变更理由和正文出处，可逐条核验。</span></div>
  </div>
  <div class="criterion">
    <div class="criterion-num">C</div>
    <div><b>归属</b><span>作品随时导出 Markdown，不被工具锁死。</span></div>
  </div>
</div>

<div class="bottom-note">来源：docs/requirements/problem_definition.md · README「产品优势」</div>

<!-- 使命讲能做什么，口号讲凭什么选我们；三条判据分别对应门槛、质量、归属。 -->

---
layout: default
---

<div class="kicker">目标用户 / WHO</div>

# 服务「想写却写不完」的人。<br>为普通作者补上工程能力。

<div class="rule"></div>

<div class="persona-grid">
  <div class="persona">
    <div class="persona-top"><span class="persona-index">01</span><span class="tag">核心用户</span></div>
    <div class="persona-title">第一次写长篇的读者</div>
    <div class="persona-row"><b>他们是谁</b><span>脑子里有一个世界，但没受过写作训练，也没写过十万字。</span></div>
    <div class="persona-row"><b>卡在哪里</b><span>写到第三章人物就乱了，不知道该怎么继续，也不敢重读。</span></div>
    <div class="persona-row"><b>我们要给</b><span>一条能走完的路：从想法到第 1 章，再到一个完整的故事。</span></div>
  </div>

  <div class="persona">
    <div class="persona-top"><span class="persona-index">02</span><span class="tag">高价值用户</span></div>
    <div class="persona-title">类型小说作者</div>
    <div class="persona-row"><b>他们是谁</b><span>有稳定更新需求，设定复杂、伏笔多，最怕前后矛盾。</span></div>
    <div class="persona-row"><b>卡在哪里</b><span>灵感充足，一致性难守；每次改设定都要重读全书。</span></div>
    <div class="persona-row"><b>我们要给</b><span>可追溯的状态与来源，让修改只影响该影响的地方。</span></div>
  </div>

  <div class="persona">
    <div class="persona-top"><span class="persona-index">03</span><span class="tag">延展用户</span></div>
    <div class="persona-title">小型内容团队</div>
    <div class="persona-row"><b>他们是谁</b><span>需要稳定交付、多人交接，不能把内容锁在一个工具里。</span></div>
    <div class="persona-row"><b>卡在哪里</b><span>进度分散、成本不透明、人员一换就接不上。</span></div>
    <div class="persona-row"><b>我们要给</b><span>任务、用量、导出和可恢复的工程化流程。</span></div>
  </div>
</div>

<div class="bottom-note">来源：docs/requirements/user_stories.md · docs/requirements/functional_spec.md</div>

<!-- 三类用户，从个人到团队；边界同样重要。 -->

---
layout: default
---

<div class="kicker">价值主张 / VALUE</div>

# 用用户故事说价值：<br>少重读，少试错，有退路。

<div class="rule"></div>

<div class="story-list">
  <div class="story">
    <div class="story-no">01</div>
    <div class="story-body">
      <div class="story-role">作为第一次写长篇的读者</div>
      <div class="story-text">我希望只给出题材、主角和走向，就能先看到第 1 章，<b>以便判断这个故事值不值得写下去。</b></div>
    </div>
    <div class="story-value">先看到<br>故事成立</div>
  </div>

  <div class="story">
    <div class="story-no">02</div>
    <div class="story-body">
      <div class="story-role">作为正在连载的作者</div>
      <div class="story-text">我希望每次改动都能查到设定出处和版本，<b>以便不用重读全书。</b></div>
    </div>
    <div class="story-value">改动<br>有据可查</div>
  </div>

  <div class="story">
    <div class="story-no">03</div>
    <div class="story-body">
      <div class="story-role">作为需要交接的团队</div>
      <div class="story-text">我希望中断后能续写、完成后能导出 Markdown，<b>以便交付不被工具锁定。</b></div>
    </div>
    <div class="story-value">随时<br>能带走</div>
  </div>
</div>

<div class="value-bottom">
  <div class="value-quote">价值落在让作者<b>敢继续写下去</b>。</div>
  <div class="value-side">对应交付：创建作品 · 配置文风 · 费用确认 · 逐章生成 · 失败恢复 · 导出 Markdown</div>
</div>

<div class="bottom-note">来源：docs/requirements/user_stories.md · README「核心功能」</div>

<!-- 三条用户故事分别对应第一次写作、连载修改、团队交接。 -->

---
layout: default
---

<div class="kicker">差异化 / DIFFERENCE</div>

# 把长篇写下去，<br>靠记得住、不糊弄。

<div class="rule"></div>

<table class="compare">
  <thead>
    <tr>
      <th>能力</th>
      <th>通用聊天</th>
      <th>写作插件</th>
      <th class="is-us">Tome Agent</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>跨章记忆</td><td>靠上下文窗口，随时截断</td><td>局部设定，缺少全局状态</td><td class="is-us">结构化事件、人物与时间状态</td></tr>
    <tr><td>设定出处</td><td>没有稳定来源</td><td>有设定，但版本弱</td><td class="is-us">版本 + 变更理由 + 正文出处</td></tr>
    <tr><td>断点恢复</td><td>重开对话，从头再来</td><td>有限恢复</td><td class="is-us">阶段检查点，保留已完成正文</td></tr>
    <tr><td>成本可见</td><td>不透明</td><td>部分可见</td><td class="is-us">生成前预估，生成后用量记录</td></tr>
    <tr><td>数据归属</td><td>复制粘贴</td><td>留在平台内</td><td class="is-us">整本 Markdown，随时带走</td></tr>
  </tbody>
</table>

<div class="compare-bottom">
  <div class="compare-line"></div>
  <div class="compare-note">差异化落在<b>可管理</b>：状态有版本，失败可恢复，成本可解释，内容可迁移。</div>
</div>

<div class="bottom-note">来源：docs/requirements/problem_definition.md · docs/algorithm/research.md</div>

<!-- 与通用聊天和写作插件对比，优势集中在可管理性。 -->

---
layout: default
---

<div class="kicker">产品形态 / FORM</div>

# 浏览器打开就能写，<br>一章一次事务提交。

<div class="rule"></div>

<div class="cols cols-2 gap-lg form-layout">
  <div class="app-mock">
    <div class="mock-bar">
      <i></i><i></i><i></i>
      <span>tome.example.com</span>
    </div>
    <div class="mock-body">
      <aside class="mock-side">
        <div class="mock-logo">T</div>
        <div class="mock-nav active">书架</div>
        <div class="mock-nav">第 3 章</div>
        <div class="mock-nav">文风</div>
        <div class="mock-nav">用量</div>
      </aside>
      <main class="mock-main">
        <div class="mock-chips"><span>第 3 章</span><span>草案</span></div>
        <div class="mock-title">潮汐抵达之前</div>
        <div class="mock-copy">
          <div class="mock-line w92"></div>
          <div class="mock-line w84"></div>
          <div class="mock-line w88"></div>
          <div class="mock-line w58"></div>
        </div>
        <div class="mock-meta"><span>人物 12</span><span>伏笔 7</span><span>约 2,400 字</span></div>
        <div class="mock-action">提交本章 <span>→</span></div>
      </main>
    </div>
  </div>

  <div class="flow-list">
    <div class="flow-step">
      <span class="step-no">01</span>
      <div><b>规划</b><span>拆章、定场景、确认本章目标</span></div>
    </div>
    <div class="flow-step">
      <span class="step-no">02</span>
      <div><b>事件推演</b><span>先改状态，再写正文</span></div>
    </div>
    <div class="flow-step">
      <span class="step-no">03</span>
      <div><b>正文生成</b><span>按事件写，不自由发挥</span></div>
    </div>
    <div class="flow-step">
      <span class="step-no">04</span>
      <div><b>记忆归档</b><span>事实、版本、出处一起落盘</span></div>
    </div>
    <div class="flow-step accent">
      <span class="step-no">05</span>
      <div><b>审核提交</b><span>一章一次事务，正文与状态同批写入</span></div>
    </div>
  </div>
</div>

<div class="form-note">形态选择：云端 Web 服务。浏览器访问域名，登录账号即可写作；本地文件存储可降级运行，PostgreSQL 作为可选增强。</div>

<div class="bottom-note">来源：README「核心功能」 · docs/requirements/functional_spec.md · code/frontend/</div>

<!-- 先给用户看到的形态，再给后台的五段流程。 -->

---
layout: center
class: section
---

<div class="section-grid">
  <div class="section-no">02</div>
  <div class="section-body">
    <div class="kicker light">Design principles</div>
    <h1>设计原则</h1>
    <p>四组，十二条。<br>每条原则都要落到一个动作、一份证据。</p>
  </div>
</div>

<div class="section-foot">Tome Agent · 产品设计 / 设计原则 / 产品实现</div>

<!-- 第二部分：十二条原则要能回到仓库里的决策。 -->

---
layout: default
---

<div class="kicker">原则总览 / 4 × 3</div>

# 十二条原则，<br>一条主线：让作者敢一直用下去。

<div class="rule"></div>

<div class="principle-grid">
  <div class="principle-col">
    <div class="pg-head"><span>01</span>方向</div>
    <div class="pg-item"><b>需求定方向</b><span>先写清楚给谁、解决什么。</span></div>
    <div class="pg-item"><b>信息校准方向</b><span>用真实状态修正判断。</span></div>
    <div class="pg-item"><b>创新才有落脚点</b><span>创新放在状态与恢复。</span></div>
  </div>
  <div class="principle-col">
    <div class="pg-head"><span>02</span>系统</div>
    <div class="pg-item"><b>把作品当系统</b><span>人物、物品、时间分别建模。</span></div>
    <div class="pg-item"><b>先发散后收敛</b><span>候选方案都评估，再选型。</span></div>
    <div class="pg-item"><b>逐项优化</b><span>先一致性，再速度与文风。</span></div>
  </div>
  <div class="principle-col">
    <div class="pg-head"><span>03</span>取舍</div>
    <div class="pg-item"><b>能继承的不重造</b><span>只换编排层，保留领域逻辑。</span></div>
    <div class="pg-item"><b>算清效益</b><span>不上不必要的框架。</span></div>
    <div class="pg-item"><b>抢住时间窗口</b><span>先闭环，再增强。</span></div>
  </div>
  <div class="principle-col">
    <div class="pg-head"><span>04</span>质量</div>
    <div class="pg-item"><b>量化验收</b><span>测试、覆盖率、用量都有数。</span></div>
    <div class="pg-item"><b>能简就简</b><span>少一个运行时变量。</span></div>
    <div class="pg-item"><b>每一步都审</b><span>规则、评审、CI 同源。</span></div>
  </div>
</div>

<div class="overview-note">
  <div class="overview-mark">“</div>
  <div>原则要能解释取舍：<b>为什么选这个、不选那个</b>。</div>
</div>

<div class="bottom-note">结构对应：需求与信息 → 系统与迭代 → 继承与效益 → 定量、简化与审核</div>

<!-- 四组原则，从方向到系统，再到取舍和质量。 -->

---
layout: default
class: principle-page
---

<div class="principle-head">
  <div class="principle-big">01</div>
  <div>
    <div class="kicker">原则组 I · 方向</div>
    <h1>先问需求，再用信息校准</h1>
  </div>
</div>

<div class="rule"></div>

<div class="p-rows">
  <div class="p-row">
    <div class="p-no">01</div>
    <div class="p-body">
      <div class="p-title">需求定方向</div>
      <div class="p-text">先把问题定义、功能规格、非功能约束和用户故事写成文档，再决定做什么、不做什么。</div>
    </div>
    <div class="p-ev"><span>证据</span><code>docs/requirements/</code><em>problem_definition · functional_spec · user_stories</em></div>
  </div>

  <div class="p-row">
    <div class="p-no">02</div>
    <div class="p-body">
      <div class="p-title">信息校准方向</div>
      <div class="p-text">用真实仓库状态、测试记录和框架文档修正判断，不靠印象，也不把“框架能力”当成“产品能力”。</div>
    </div>
    <div class="p-ev"><span>证据</span><code>docs/algorithm/architecture.md</code><em>能力边界与备选方案对比</em></div>
  </div>

  <div class="p-row">
    <div class="p-no">03</div>
    <div class="p-body">
      <div class="p-title">创新才有落脚点</div>
      <div class="p-text">把创新放在“事件先行 + 三层记忆 + 可恢复提交”，围绕作者可感知的问题持续迭代。</div>
    </div>
    <div class="p-ev"><span>证据</span><code>docs/software/LANGGRAPH_MIGRATION.md</code><em>graph_runtime.py</em></div>
  </div>
</div>

<div class="p-foot">判断标准：这个决定，能不能在仓库里找到对应文件与测试？</div>

<div class="p-quote">先写清楚，再动手；先看证据，再下判断。</div>

<!-- 第一组：方向。每条原则后面都跟证据，不空喊。 -->

---
layout: default
class: principle-page
---

<div class="principle-head">
  <div class="principle-big">02</div>
  <div>
    <div class="kicker">原则组 II · 系统</div>
    <h1>把作品当系统，<br>人物、时间与事件分别建模。</h1>
  </div>
</div>

<div class="rule"></div>

<div class="p-rows">
  <div class="p-row">
    <div class="p-no">04</div>
    <div class="p-body">
      <div class="p-title">把作品当系统设计</div>
      <div class="p-text">人物、物品、时间、事件分别建模；状态变化带版本，正文只是状态的一次投影。</div>
    </div>
    <div class="p-ev"><span>证据</span><code>tome_writer/memory_system/</code><em>tiered_memory · events/continuity</em></div>
  </div>

  <div class="p-row">
    <div class="p-no">05</div>
    <div class="p-body">
      <div class="p-title">先发散后收敛</div>
      <div class="p-text">全量上下文、自然语言摘要、向量检索、事件状态四种方案都评估，再按一致性、成本和可恢复性收敛。</div>
    </div>
    <div class="p-ev"><span>证据</span><code>docs/algorithm/architecture.md</code><em>备选策略对比表</em></div>
  </div>

  <div class="p-row">
    <div class="p-no">06</div>
    <div class="p-body">
      <div class="p-title">逐项优化</div>
      <div class="p-text">先保证跨章一致性，再补恢复能力，最后才谈速度与文风；一次只改一个变量，避免“越优化越乱”。</div>
    </div>
    <div class="p-ev"><span>证据</span><code>docs/mgmt/ROADMAP.md</code><em>docs/retrospection/README.md</em></div>
  </div>
</div>

<div class="p-foot">系统视角：先定义状态，再定义操作；先保证正确，再追求好看。</div>

<div class="p-quote">状态先于文本，结构先于生成。</div>

<!-- 第二组：系统。先建模，再比较方案，最后按顺序优化。 -->

---
layout: default
class: principle-page
---

<div class="principle-head">
  <div class="principle-big">03</div>
  <div>
    <div class="kicker">原则组 III · 取舍</div>
    <h1>用既有能力，<br>换确定性。</h1>
  </div>
</div>

<div class="rule"></div>

<div class="p-rows">
  <div class="p-row">
    <div class="p-no">07</div>
    <div class="p-body">
      <div class="p-title">能继承的不重造</div>
      <div class="p-text">复用已接入的模型适配、事件推演与记忆函数；LangGraph 只替换编排层，控制迁移范围。</div>
    </div>
    <div class="p-ev"><span>证据</span><code>memory_runtime/writing_flow/</code><em>graph_runtime.py · LANGGRAPH_MIGRATION.md</em></div>
  </div>

  <div class="p-row">
    <div class="p-no">08</div>
    <div class="p-body">
      <div class="p-title">算清效益</div>
      <div class="p-text">不引入 ASGI 框架、前端构建链和向量库；把省下的复杂度放在状态一致性与恢复上。</div>
    </div>
    <div class="p-ev"><span>证据</span><code>README.md</code><em>「技术选型」与选型理由</em></div>
  </div>

  <div class="p-row">
    <div class="p-no">09</div>
    <div class="p-body">
      <div class="p-title">抢住时间窗口</div>
      <div class="p-text">先做出可演示、可验证的完整闭环：本地 Web + 文件存储；PostgreSQL 与 hosted 模式按需增强。</div>
    </div>
    <div class="p-ev"><span>证据</span><code>docs/software/DEPLOY.md</code><em>WINDOWS_PORTABLE.md · LINUX_HOSTED.md</em></div>
  </div>
</div>

<div class="p-foot">取舍标准：新增的每一层，都要能回答“它替作者解决了什么”。</div>

<div class="p-quote">只造真正影响体验的能力。</div>

<!-- 第三组：取舍。把工程资源花在确定性上。 -->

---
layout: default
class: principle-page
---

<div class="principle-head">
  <div class="principle-big">04</div>
  <div>
    <div class="kicker">原则组 IV · 质量</div>
    <h1>把质量做成<br>默认动作。</h1>
  </div>
</div>

<div class="rule"></div>

<div class="p-rows">
  <div class="p-row">
    <div class="p-no">10</div>
    <div class="p-body">
      <div class="p-title">量化验收</div>
      <div class="p-text">单元测试、集成测试、PostgreSQL 17/18 矩阵、hosted 回归；测试数、覆盖率、失败率和 token 用量都有记录。</div>
    </div>
    <div class="p-ev"><span>证据</span><code>.github/workflows/tests.yml</code><em>tests/TEST_REPORT.md</em></div>
  </div>

  <div class="p-row">
    <div class="p-no">11</div>
    <div class="p-body">
      <div class="p-title">能简就简</div>
      <div class="p-text">标准库 HTTP 服务、Vue runtime-only、无 CDN、无前端构建步骤；少一个运行时变量，就少一类线上问题。</div>
    </div>
    <div class="p-ev"><span>证据</span><code>code/frontend/</code><em>README「技术选型」</em></div>
  </div>

  <div class="p-row">
    <div class="p-no">12</div>
    <div class="p-body">
      <div class="p-title">每一步都审</div>
      <div class="p-text">Ruff 规则、pre-commit 与 CI 共用同一份配置；代码评审、质量报告与整改记录都留在仓库。</div>
    </div>
    <div class="p-ev"><span>证据</span><code>docs/software/CODE_QUALITY_FIXES.md</code><em>code_review.md · .pre-commit-config.yaml</em></div>
  </div>
</div>

<div class="p-foot">质量是每次提交都在走的默认路径。</div>

<div class="p-quote">每次提交都留下可复查的证据。</div>

<!-- 第四组：质量。定量验收、简化、审核，三件事都变成默认动作。 -->

---
layout: default
---

<div class="kicker">取舍 / WHAT WE DON'T DO</div>

# 我们刻意不做的事，<br>定义了产品是什么。

<div class="rule"></div>

<div class="tradeoff-grid">
  <div class="tradeoff">
    <div class="tradeoff-x">×</div>
    <div class="tradeoff-title">不做“一键神作”</div>
    <div class="tradeoff-body">不承诺无限长度，也不把演示原型当成真实生成能力。篇幅承诺只到验证过的 8–10 章。</div>
    <div class="tradeoff-arrow">改做 → 可验证的完整闭环</div>
  </div>
  <div class="tradeoff">
    <div class="tradeoff-x">×</div>
    <div class="tradeoff-title">不做“全量上下文”</div>
    <div class="tradeoff-body">每次发送全书正文，成本随篇幅线性增长，还不保证模型真的用上所有历史。</div>
    <div class="tradeoff-arrow">改做 → 事件状态 + 按需记忆</div>
  </div>
  <div class="tradeoff">
    <div class="tradeoff-x">×</div>
    <div class="tradeoff-title">不做“平台锁定”</div>
    <div class="tradeoff-body">作品不能只活在某个工具里。生成结果必须能整本导出，数据要能迁移。</div>
    <div class="tradeoff-arrow">改做 → Markdown 导出 + 开放存储</div>
  </div>
  <div class="tradeoff">
    <div class="tradeoff-x">×</div>
    <div class="tradeoff-title">不做“看起来很重”的架构</div>
    <div class="tradeoff-body">不上 ASGI、前端构建链、向量库；这些复杂度没有直接改善跨章一致性。</div>
    <div class="tradeoff-arrow">改做 → 标准库 + 渐进式 Vue</div>
  </div>
</div>

<div class="tradeoff-foot">取舍标准只有一个：<b>作者能不能一直用下去。</b></div>

<div class="bottom-note">来源：README「技术选型」 · docs/software/architecture.md · docs/software/DEPLOY.md</div>

<!-- 不做什么，和做什么一样重要。四条取舍都指向长期可用。 -->

---
layout: center
class: section
---

<div class="section-grid">
  <div class="section-no">03</div>
  <div class="section-body">
    <div class="kicker light">Product implementation</div>
    <h1>产品实现</h1>
    <p>从体验与选型，到概要设计、架构与质量。<br>把设计原则变成代码、测试和部署记录。</p>
  </div>
</div>

<div class="section-foot">Tome Agent · 产品设计 / 设计原则 / 产品实现</div>

<!-- 第三部分：每个设计决定都能在仓库里找到落点。 -->

---
layout: default
---

<div class="kicker">3.1 用户体验 / UX</div>

# 写作工具先要让人敢一直用。

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

<div class="ux-foot">六个因素围绕同一个目标：<b>让作者把注意力留在故事上。</b></div>

<div class="bottom-note">来源：README「核心功能」 · docs/software/USER_GUIDE.md · code/backend/inf_backend/web.py</div>

<!-- 3.1 用户体验：可用、连续、成本、容错、可控、安全。 -->

---
layout: default
---

<div class="kicker">3.2 技术选型 / STACK</div>

# 够用、可验证，避免过度设计。

<div class="rule"></div>

<table class="compare tech-table">
  <thead>
    <tr><th>条目</th><th>选型</th><th>版本</th><th>选型原因</th></tr>
  </thead>
  <tbody>
    <tr><td>程序设计语言</td><td>Python</td><td>3.11（CI 3.11）</td><td>复用写作引擎与标准库测试，部署简单</td></tr>
    <tr><td>智能体编排</td><td>LangGraph</td><td>1.2.17</td><td>状态图表达规划、写作、记忆、审核与条件边</td></tr>
    <tr><td>前端</td><td>Vue runtime-only + 原生 HTML/CSS/JS</td><td>Vue 3.5.44</td><td>仓库内置运行时，无前端构建链</td></tr>
    <tr><td>Web 服务</td><td>Python 标准库 <code>http.server</code></td><td>随 Python 3.11</td><td>单机与单服务够用，不额外引入 ASGI</td></tr>
    <tr><td>运行平台</td><td>Windows 本地 / Linux 托管</td><td>Python 3.11</td><td>同一套服务代码，CI 覆盖 Ubuntu</td></tr>
    <tr><td>数据库</td><td>PostgreSQL + Psycopg</td><td>PG 17（CI 17/18）· Psycopg 3.3.3</td><td>持久化作品、章节与任务；未配置时降级文件模式</td></tr>
    <tr><td>模型服务</td><td>DeepSeek / OpenAI 兼容</td><td>Chat Completions</td><td>复用已接入接口、计费预估与故障处理</td></tr>
    <tr><td>开发工具</td><td>VS Code + Ruff</td><td>Ruff 0.17.4</td><td>编辑、格式化与静态检查共用一套规则</td></tr>
  </tbody>
</table>

<div class="tech-note">版本与选型理由同步写在 <code>README.md</code>「技术选型」；依赖版本见 <code>requirements.txt</code> 与 <code>pyproject.toml</code>。</div>

<div class="bottom-note">来源：README「技术选型」 · code/backend/requirements.txt · code/backend/pyproject.toml · docs/software/LANGGRAPH_MIGRATION.md</div>

<!-- 3.2 技术选型：语言、IDE、平台、框架与版本。 -->

---
layout: default
---

<div class="kicker">3.3 代码仓库 / REPOSITORY</div>

# 仓库与提交历史：真实协作留痕。

<div class="rule"></div>

<div class="repo-layout">
  <div class="repo-left">
    <div class="tag">仓库地址</div>
    <a class="repo-url" href="https://github.com/liuliyisui/tome-agent">github.com/liuliyisui/tome-agent</a>
    <div class="repo-stats">
      <div><b>217</b><span>次提交</span></div>
      <div><b>5</b><span>位贡献者</span></div>
      <div><b>5</b><span>个代码模块</span></div>
    </div>
    <div class="repo-note">提交分布可在仓库 Insights → Pulse 复查；任务与缺陷以 GitHub Issues 记录，看板、分工和路线图保存在 docs/mgmt/。</div>
    <div class="repo-links">
      <span>KANBAN.md</span><span>TEAM_PLAN.md</span><span>ROADMAP.md</span>
    </div>
  </div>
  <div class="repo-right">
    <div class="tag">GitHub Pulse · Top committers</div>
    <img src="/pulse-committers.png" alt="Top committers">
    <div class="small">横轴为贡献者，纵轴为提交次数；截图截至 2026-11-21。</div>
  </div>
</div>

<div class="bottom-note">来源：github.com/liuliyisui/tome-agent · docs/mgmt/KANBAN.md · docs/mgmt/TEAM_PLAN.md · docs/mgmt/ROADMAP.md</div>

<!-- 3.3 代码仓库：链接、提交分布与协作记录。 -->

---
layout: default
---

<div class="kicker">3.4 全生命周期 / LIFECYCLE</div>

# 主要问题与处理记录。

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

<div class="issue-note">问题清单已保存为 <code>docs/software/ISSUES_SUMMARY.md</code>，按分析、设计、开发、测试、部署运维顺序维护。</div>

<div class="bottom-note">来源：docs/software/ISSUES_SUMMARY.md · docs/software/architecture.md · tests/TEST_REPORT.md</div>

<!-- 3.4 全生命周期：主要问题、发生原因、解决办法与仓库证据。 -->

---
layout: default
---

<div class="kicker">3.5 软件概要设计 / DESIGN</div>

# 概要设计：先把边界和依赖画清楚。

<div class="rule"></div>

<div class="ux-grid">
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">01</span><span class="tag">3.5.1</span></div>
    <div class="ux-title">系统架构</div>
    <div class="ux-text">界面、服务、引擎、存储四层边界，模型服务从引擎层旁路调用。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">02</span><span class="tag">3.5.2</span></div>
    <div class="ux-title">基础设施</div>
    <div class="ux-text">单台 Linux 服务器，Nginx 负责 HTTPS 与反向代理，服务只监听本机。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">03</span><span class="tag">3.5.3</span></div>
    <div class="ux-title">智能体设计</div>
    <div class="ux-text">LangGraph 编排事件、写作、提交、记忆与审核；三层记忆负责跨章状态。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">04</span><span class="tag">3.5.4</span></div>
    <div class="ux-title">数据库</div>
    <div class="ux-text">6 张表覆盖作品、章节、版本、任务与用量；PostgreSQL 可选，文件模式可降级。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">05</span><span class="tag">3.5.5</span></div>
    <div class="ux-title">接口</div>
    <div class="ux-text">作品、生成、编辑、复查、任务状态和导出都走真实 HTTP 路由。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">06</span><span class="tag">3.5.6</span></div>
    <div class="ux-title">前端</div>
    <div class="ux-text">Vue runtime-only 页面承载书架、文风、生成、编辑、复查与导出。</div>
  </div>
</div>

<div class="ux-foot">设计文档入口：<b>docs/software/architecture.md</b> · <b>docs/algorithm/LANGGRAPH.mmd</b> · <b>schema.sql</b></div>

<div class="bottom-note">来源：docs/software/architecture.md · docs/algorithm/LANGGRAPH.mmd · code/backend/inf_backend/schema.sql</div>

<!-- 3.5 软件概要设计：设计文档索引，具体展开见 3.5.1–3.5.6。 -->

---
layout: default
---

<div class="kicker">3.5.0 使用工具 / TOOLING</div>

# 图源、讲稿和代码放在同一个仓库。

<div class="rule"></div>

<div class="tool-grid">
  <div class="tool-card">
    <div class="ux-top"><span class="ux-no">01</span><span class="tag">画图</span></div>
    <div class="tool-name">Mermaid</div>
    <div class="tool-role">架构图 · 状态图 · E-R 图</div>
    <div class="tool-list">
      <div>用 <code>flowchart</code> / <code>erDiagram</code> 写图源</div>
      <div>状态图源文件：<code>docs/algorithm/LANGGRAPH.mmd</code></div>
      <div>图随代码一起 review、一起 diff</div>
    </div>
  </div>
  <div class="tool-card">
    <div class="ux-top"><span class="ux-no">02</span><span class="tag">讲稿</span></div>
    <div class="tool-name">Slidev</div>
    <div class="tool-role">Markdown → 网页 / PDF</div>
    <div class="tool-list">
      <div>幻灯片本身就是 Markdown</div>
      <div>Mermaid 代码块在页面内直接渲染</div>
      <div>GitHub Actions 构建并发布 Pages</div>
    </div>
  </div>
  <div class="tool-card">
    <div class="ux-top"><span class="ux-no">03</span><span class="tag">工程</span></div>
    <div class="tool-name">VS Code + Git</div>
    <div class="tool-role">编辑 · 检查 · 提交</div>
    <div class="tool-list">
      <div>Markdown、Mermaid、Python 在同一编辑器</div>
      <div>Ruff / Pylance 做格式与静态检查</div>
      <div>图源、讲稿和实现进入同一次提交</div>
    </div>
  </div>
</div>

<div class="tool-note">工具选择标准：图能 diff，稿能构建，结果能复查。</div>

<div class="bottom-note">来源：docs/algorithm/LANGGRAPH.mmd · docs/slides/slides.md · README「技术选型」</div>

<!-- 3.5.0 使用工具：Mermaid、Slidev、VS Code + Git。 -->

---
layout: default
---

<div class="kicker">3.5.1 架构 / ARCHITECTURE</div>

# 四层边界：界面不碰模型，模型不碰存储。

<div class="rule"></div>

```mermaid {theme: 'base', themeCSS: '.node rect{fill:#F6F3E9 !important;stroke:#1E4A36 !important;rx:4px;ry:4px}.node polygon{fill:#F6F3E9 !important;stroke:#1E4A36 !important}.nodeLabel{fill:#1F3026 !important;font-family:Noto Sans SC,Microsoft YaHei,sans-serif !important;font-size:13px !important}.edgePath .path{stroke:#7D9274 !important;stroke-width:1.5px !important}.marker{fill:#7D9274 !important;stroke:#7D9274 !important}.labelBkg{background:#F6F3E9 !important;color:#5D7355 !important}.labelBkg p{background:transparent !important;color:#5D7355 !important}.edgeLabel rect{fill:#F6F3E9 !important;opacity:1 !important}.edgeLabel{background:#F6F3E9 !important;color:#5D7355 !important}.edgeLabel span{color:#5D7355 !important}', scale: 0.9}
flowchart LR
  UI["界面层"]
  API["服务层"]
  ENGINE["引擎层"]
  STORE["存储层"]
  MODEL["模型服务"]

  UI --> API
  API --> ENGINE
  ENGINE --> STORE
  ENGINE -. "旁路调用" .-> MODEL
```

<div class="cols cols-3 gap-md arch-notes">
  <div class="arch-note">
    <div class="arch-p-no">01</div>
    <div><b>界面只表达意图</b><span>不拼提示词，不直接调模型。</span></div>
  </div>
  <div class="arch-note">
    <div class="arch-p-no">02</div>
    <div><b>引擎只做编排</b><span>不依赖具体 HTTP 路由和页面。</span></div>
  </div>
  <div class="arch-note">
    <div class="arch-p-no">03</div>
    <div><b>存储可替换</b><span>文件模式与 PostgreSQL 共享同一套领域语义。</span></div>
  </div>
</div>

<div class="arch-foot"><span>请求路径</span> 界面动作 → 服务层校验 → 引擎编排 → 检查点 / 数据库提交 → 结果回传。</div>

<div class="arch-quote">好的架构让<b>每一层都能被替换、被测试、被解释</b>。</div>

<div class="bottom-note">来源：docs/software/architecture.md · code/backend/inf_backend/service.py · code/core_engine/</div>

<!-- 四层架构，重点是边界。 -->

---
layout: default
---

<div class="kicker">3.5.2 基础设施 / INFRA</div>

# 单机部署：入口、应用、数据三段就够。

<div class="rule"></div>

<div class="ux-grid">
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">01</span><span class="tag">入口</span></div>
    <div class="ux-title">Nginx · 443 / TLS</div>
    <div class="ux-text">负责 HTTPS、反向代理和请求限流；证书续期独立于应用。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">02</span><span class="tag">应用</span></div>
    <div class="ux-title">systemd · Python 3.11</div>
    <div class="ux-text">服务只监听 <code>127.0.0.1:8765</code>，崩溃自动重启，后台任务上限为 3。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">03</span><span class="tag">数据</span></div>
    <div class="ux-title">/var/lib/tome-agent</div>
    <div class="ux-text">保存作品、Skill、模型配置和检查点；定期备份，PostgreSQL 作为可选增强。</div>
  </div>
</div>

<div class="ux-foot">部署边界只有三段：<b>Nginx、Python 服务、持久化目录。</b></div>

<div class="bottom-note">来源：docs/software/LINUX_HOSTED.md · docs/software/DEPLOY.md · code/backend/compose.yaml</div>

<!-- 3.5.2 基础设施：单机部署，入口、应用、数据三段。 -->

---
layout: default
---

<div class="kicker">3.5.3 智能体设计 / AGENT</div>

# 智能体设计：编排、记忆、护栏、工具各有边界。

<div class="rule"></div>

<div class="agent-grid">
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">01</span><span class="tag">编排</span></div>
    <div class="ux-title">LangGraph 状态图</div>
    <div class="ux-text">规划、写作、提交、记忆、审核五个节点；写作可条件边回到规划，最多一次。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">02</span><span class="tag">记忆</span></div>
    <div class="ux-title">工作 / 近期 / 长期</div>
    <div class="ux-text">当前章、最近章节、全书事实分层保存；长期事实带版本、变更理由和正文出处。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">03</span><span class="tag">护栏</span></div>
    <div class="ux-title">结构、来源、失败与审核</div>
    <div class="ux-text">JSON 结构校验、来源追踪、失败降级和提交前审核门共同约束输出。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">04</span><span class="tag">工具与知识</span></div>
    <div class="ux-title">内部函数 + 文本 Skill</div>
    <div class="ux-text">模型接口、文件/数据库读写和敏感信息检查由服务内部完成；写作 Skill 以文本注入。</div>
  </div>
</div>

<div class="ux-foot">当前知识主要来自 Skill 文本和结构化记忆；<b>未引入向量库或知识图谱。</b></div>

<div class="bottom-note">来源：docs/software/architecture.md · docs/software/LANGGRAPH_MIGRATION.md · code/core_engine/memory_runtime/ · code/core_engine/writing_skills/</div>

<!-- 3.5.3 智能体设计：编排、记忆、护栏、工具与知识。 -->

---
layout: default
---

<div class="kicker">3.5.3 编排 / LANGGRAPH</div>

# 事件先行：先改状态，再写正文。

<div class="rule"></div>

```mermaid {theme: 'base', themeCSS: '.node rect{fill:#F6F3E9 !important;stroke:#1E4A36 !important;rx:4px;ry:4px}.node polygon{fill:#F6F3E9 !important;stroke:#1E4A36 !important}.nodeLabel{fill:#1F3026 !important;font-family:Noto Sans SC,Microsoft YaHei,sans-serif !important;font-size:13px !important}.edgePath .path{stroke:#7D9274 !important;stroke-width:1.5px !important}.marker{fill:#7D9274 !important;stroke:#7D9274 !important}.labelBkg{background:#F6F3E9 !important;color:#5D7355 !important}.labelBkg p{background:transparent !important;color:#5D7355 !important}.edgeLabel rect{fill:#F6F3E9 !important;opacity:1 !important}.edgeLabel{background:#F6F3E9 !important;color:#5D7355 !important}.edgeLabel span{color:#5D7355 !important}', scale: 0.9}
flowchart LR
  PLAN["规划"]
  WRITE["写作"]
  COMMIT["提交"]
  MEMORY["记忆"]
  REVIEW["审核"]

  PLAN --> WRITE
  WRITE --> COMMIT
  COMMIT --> MEMORY
  MEMORY --> REVIEW
  WRITE -. "revise" .-> PLAN
```

<div class="cols cols-3 gap-md flow-notes">
  <div class="card">
    <div class="tag">事件先行</div>
    <div class="card-title">不让正文猜事实</div>
    <div class="card-text">先规划场景事件并推演人物、物品和时间状态，再把状态写进正文。避免“正文写完才发现关键事实对不上”。</div>
  </div>
  <div class="card">
    <div class="tag">条件边</div>
    <div class="card-title">修订有上限</div>
    <div class="card-text">写作提出事件修订时，经条件边回到规划节点；保留一次修订上限，防止无限循环。</div>
  </div>
  <div class="card">
    <div class="tag">检查点</div>
    <div class="card-title">失败不丢正文</div>
    <div class="card-text">每个阶段保存原子检查点；恢复时识别待处理任务与损坏检查点，不把已经完成的章节推倒重来。</div>
  </div>
</div>

<div class="flow-quote"><span>修订上限</span> 让系统回到可收敛的路径，减少无效的重复生成。</div>

<div class="bottom-note">来源：docs/algorithm/LANGGRAPH.mmd · code/core_engine/memory_runtime/writing_flow/graph_runtime.py</div>

<!-- 编排图：规划→写作→提交→记忆→审核，修订回到规划，最多一次。 -->

---
layout: default
---

<div class="kicker">3.5.3 记忆 / MEMORY</div>

# 每条设定都带版本、<br>变更理由和正文出处。

<div class="rule"></div>

<div class="cols cols-2 gap-lg memory-layout">
  <div class="memory-stack">
    <div class="memory-layer">
      <div class="memory-tag">工作记忆</div>
      <div class="memory-name">当前章</div>
      <div class="memory-desc">本章计划、草稿、待提交变更；只服务这一次生成。</div>
    </div>
    <div class="memory-layer">
      <div class="memory-tag">近期记忆</div>
      <div class="memory-name">最近章节</div>
      <div class="memory-desc">近期事件、人物状态、未收线索；按需进入上下文。</div>
    </div>
    <div class="memory-layer long">
      <div class="memory-tag">长期记忆</div>
      <div class="memory-name">全书事实</div>
      <div class="memory-desc">人物、物品、时间、知识来源；每条带版本、变更理由和正文出处。</div>
    </div>
  </div>

  <div class="guardrails">
    <div class="guardrail"><span>01</span><div><b>结构校验</b><p>模型输出必须是合法 JSON；坏格式不写入状态。</p></div></div>
    <div class="guardrail"><span>02</span><div><b>来源追踪</b><p>设定变更记录来自哪一章、哪段正文，可回溯。</p></div></div>
    <div class="guardrail"><span>03</span><div><b>失败降级</b><p>局部规划或记忆失败时，保留已完成正文，标记待处理。</p></div></div>
    <div class="guardrail"><span>04</span><div><b>审核门</b><p>提交前检查连续性、人物状态与伏笔闭合情况。</p></div></div>
  </div>
</div>

<div class="memory-note"><b>三层记忆用结构化状态管理事实。</b>检索只能找到相似内容，不能判断一条事实是否已经过期；状态需要版本和来源。</div>

<div class="bottom-note">来源：docs/software/architecture.md「事件先行与三层记忆」 · code/core_engine/memory_runtime/</div>

<!-- 记忆分层，不等于把所有历史都塞进提示词。 -->

---
layout: default
---

<div class="kicker">3.5.4 数据库 / DATABASE</div>

# 六张表把作品、任务和成本分开记。

<div class="rule"></div>

```mermaid {theme: 'base', themeCSS: '.node rect{fill:#F6F3E9 !important;stroke:#1E4A36 !important;rx:4px;ry:4px}.node polygon{fill:#F6F3E9 !important;stroke:#1E4A36 !important}.nodeLabel{fill:#1F3026 !important;font-family:Noto Sans SC,Microsoft YaHei,sans-serif !important;font-size:12px !important}.edgePath .path{stroke:#7D9274 !important;stroke-width:1.4px !important}.marker{fill:#7D9274 !important;stroke:#7D9274 !important}.labelBkg{background:#F6F3E9 !important;color:#5D7355 !important}.labelBkg p{background:transparent !important;color:#5D7355 !important}', scale: 0.8}
flowchart LR
  BOOKS["tome_books<br/>作品"] -->|1:N| CHAPTERS["tome_chapters<br/>章节"]
  CHAPTERS -->|1:N| VERSIONS["tome_chapter_versions<br/>版本"]
  BOOKS -->|1:N| JOBS["tome_jobs<br/>任务"]
  BOOKS -->|1:N| USAGE["tome_usage<br/>用量"]
```

<div class="cols cols-2 gap-lg data-layout">
  <div>
    <div class="subhead">聚合关系</div>
    <div class="data-note">作品是聚合根：章节、版本、任务和用量都按 <code>book_id</code> 归属。版本表保留章节历史；任务表记录进度；用量表保留 token 与费用。</div>
    <div class="data-note"><code>tome_schema_version</code> 独立维护迁移版本，不参与作品聚合。</div>
  </div>
  <div>
    <div class="subhead">存储与降级</div>
    <div class="data-note">PostgreSQL 可选；未配置时降级为文件模式，两种存储共享同一套领域语义。</div>
    <div class="data-note">数据库保存作品、章节、版本、任务和用量；文件模式保存检查点与作品文件，便于本地运行和迁移。</div>
  </div>
</div>

<div class="bottom-note">来源：code/backend/inf_backend/schema.sql · docs/software/POSTGRESQL.md · code/backend/inf_backend/database.py</div>

<!-- 3.5.4 数据库：6 张表、关系与两种存储模式。 -->

---
layout: default
---

<div class="kicker">3.5.5 接口 / API</div>

# 生成、编辑、复查、导出都有固定入口。

<div class="rule"></div>

<table class="compare interface-table">
  <thead>
    <tr><th>方法</th><th>路径</th><th>输入</th><th>输出</th></tr>
  </thead>
  <tbody>
    <tr><td>GET</td><td><code>/api/books</code></td><td>—</td><td>作品列表</td></tr>
    <tr><td>POST</td><td><code>/api/books/{id}/generate</code></td><td>生成选项 / 模型配置</td><td>job_id</td></tr>
    <tr><td>POST</td><td><code>/api/books/{id}/chapters/{n}/edit</code></td><td>标题 / 正文 / base_revision</td><td>保存结果</td></tr>
    <tr><td>POST</td><td><code>/api/books/{id}/chapters/{n}/review</code></td><td>检查项 / 作者确认</td><td>复查报告</td></tr>
    <tr><td>GET</td><td><code>/api/jobs/{id}</code></td><td>—</td><td>进度 / 结果</td></tr>
    <tr><td>GET</td><td><code>/api/books/{id}/export</code></td><td>—</td><td>Markdown</td></tr>
  </tbody>
</table>

<div class="tx-line"><span>事务边界</span> 章节内容 + 版本记录 + 用量，同批提交；任务状态单独记录，失败保留已完成部分。</div>

<div class="data-note">后台任务通过 job id 查询；页面刷新不打断生成。导出使用复查后的正文版本。</div>

<div class="bottom-note">来源：code/backend/inf_backend/web.py · code/backend/inf_backend/schema.sql · README「核心功能」</div>

<!-- 3.5.5 接口：真实路由、输入输出和事务边界。 -->

---
layout: default
---

<div class="kicker">3.5.6 前端 / FRONTEND</div>

# 前端设计：零构建、同源、渐进增强。

<div class="rule"></div>

<div class="ux-grid">
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">01</span><span class="tag">技术</span></div>
    <div class="ux-title">Vue runtime-only</div>
    <div class="ux-text">Vue 3.5.44 + 原生 HTML/CSS/JS；仓库内置运行时，无 CDN、无前端构建链。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">02</span><span class="tag">页面</span></div>
    <div class="ux-title">五个工作区</div>
    <div class="ux-text">书架、文风与费用、生成、编辑与复查、导出；动作与用户故事一一对应。</div>
  </div>
  <div class="ux-card">
    <div class="ux-top"><span class="ux-no">03</span><span class="tag">交互</span></div>
    <div class="ux-title">任务可查询</div>
    <div class="ux-text">生成任务通过 job id 查询；刷新不打断后台；错误详情可定位，导出 Markdown。</div>
  </div>
</div>

<div class="ux-foot">与后端同源部署，静态文件由 Python 服务或 Nginx 提供。</div>

<div class="bottom-note">来源：code/frontend/ · code/backend/inf_backend/web.py · README「核心功能」</div>

<!-- 3.5.6 前端：Vue runtime-only、五个工作区与任务查询。 -->

---
layout: default
---

<div class="kicker">3.6 质量 / QUALITY</div>

# 质量是每次提交的<br>默认动作。

<div class="rule"></div>

<div class="quality-stats">
  <div class="q-stat"><div class="q-num">256</div><div class="q-label">测试通过</div></div>
  <div class="q-stat"><div class="q-num">0</div><div class="q-label">失败 / 跳过</div></div>
  <div class="q-stat"><div class="q-num">61.01%</div><div class="q-label">核心逻辑覆盖率</div></div>
  <div class="q-stat"><div class="q-num">4</div><div class="q-label">类 CI job</div></div>
</div>

<div class="cols cols-2 gap-lg quality-layout">
  <div>
    <div class="subhead">测试矩阵</div>
    <div class="quality-row"><b>lint</b><span>Ruff check + Ruff format 全仓库校验</span></div>
    <div class="quality-row"><b>test</b><span>Windows · unittest · 覆盖率脚本</span></div>
    <div class="quality-row"><b>postgresql</b><span>PostgreSQL 17 / 18 矩阵 · 独立 schema</span></div>
    <div class="quality-row"><b>hosted-linux</b><span>账号、hosted 服务与 worker 回归</span></div>
  </div>
  <div>
    <div class="subhead">把质量做成资产</div>
    <div class="quality-row"><b>Ruff</b><span>75 处不合规 → 0；规则集中在 pyproject.toml</span></div>
    <div class="quality-row"><b>pre-commit</b><span>格式化、YAML/TOML 校验与 CI 同源</span></div>
    <div class="quality-row"><b>Code Review</b><span>问题、修复与复核记录留在仓库</span></div>
    <div class="quality-row"><b>失败降级</b><span>保留已生成正文，区分请求失败 / 可能已计费 / 未审核</span></div>
  </div>
</div>

<div class="quality-note">最近一次完整记录：tests/TEST_REPORT.md（2026-10-24）——256 项通过、0 失败、0 跳过；含真实模型端到端生成与真实 PostgreSQL 验证。</div>

<div class="bottom-note">来源：tests/TEST_REPORT.md · .github/workflows/tests.yml · docs/software/CODE_QUALITY_FIXES.md</div>

<!-- 质量数字来自仓库里的测试报告，不手填“感觉良好”。 -->

---
layout: default
---

<div class="kicker">3.6.1–3.6.2 质量控制 / TOOLS</div>

# 规矩写成工具，<br>才不会靠人记得。

<div class="rule"></div>

<div class="cols cols-2 gap-lg quality-layout">
  <div>
    <div class="subhead">静态检查：提交前拦下</div>
    <div class="quality-row"><b>Ruff format</b><span>191 个文件符合 PEP8，本地与 CI 跑同一条命令</span></div>
    <div class="quality-row"><b>Ruff check</b><span>0 违规；规则集中在 pyproject.toml，例外要写明理由</span></div>
    <div class="quality-row"><b>Pylint</b><span>9.62 / 10 · 0 error · 0 fatal（pylint 4.1.4）</span></div>
    <div class="quality-row"><b>McCabe</b><span>复杂度阈值 10；14 个超阈函数列入重构清单</span></div>
  </div>
  <div>
    <div class="subhead">运行时：失败也要留下证据</div>
    <div class="quality-row"><b>日志</b><span>统一 logger 输出；生成进度同时写入 tome_jobs</span></div>
    <div class="quality-row"><b>异常</b><span>后端 69 个 try 块 / 219 个函数；引擎 138 个 / 1,196 个</span></div>
    <div class="quality-row"><b>抛出</b><span>1,054 处 raise，区分可重试与不可重试</span></div>
    <div class="quality-row"><b>降级</b><span>失败保留已完成正文；错误详情脱敏后回传</span></div>
  </div>
</div>

<div class="subhead assert-title">把症状写成断言</div>
<div class="assert-band">
  <div><b>设定过期</b><span>过期修订与旧事实直接拒绝</span><em>test_event_consistency</em></div>
  <div><b>中断即重来</b><span>进度不能无证据回退</span><em>test_core_boundaries</em></div>
  <div><b>成本黑箱</b><span>缺少 usage 不得标记完成</span><em>test_streaming_progress</em></div>
  <div><b>凭证泄漏</b><span>失败日志自动脱敏</span><em>test_logging</em></div>
</div>

<div class="quality-note">复现：<code>ruff check .</code> · <code>ruff format --check .</code> · <code>pylint --rcfile code/backend/pyproject.toml</code>。Pylint 的 30 处导入误报来自 memory_runtime 动态扩展 <code>__path__</code>，已单独排除。</div>

<div class="bottom-note">来源：code/backend/pyproject.toml · .github/workflows/tests.yml · Ruff 0.17.4 / Pylint 4.1.4 本地实测</div>

<!-- 质量工具只列仓库里真实启用的检查，不把“打算上”的工具写成“已经用”。 -->

---
layout: default
---

<div class="kicker">3.7 代码统计 / CODE</div>

# 代码行数只是中间产物，<br>真正的考验在于持续维护。

<div class="rule"></div>

<div class="code-ledger">
  <div><b>214</b><span>次提交</span></div>
  <div><b>129</b><span>个生产文件</span></div>
  <div><b>43,962</b><span>行 Python 生产代码</span></div>
  <div><b>5.4 : 1</b><span>生产代码 : 测试代码</span></div>
</div>

<div class="cols cols-2 gap-lg">
  <div>
    <div class="subhead">语言分布（行）</div>
    <div class="code-lang">
      <div><b>Python</b><span class="bar"><i style="width:100%"></i></span><em>52,414</em></div>
      <div><b>Markdown</b><span class="bar"><i style="width:14%"></i></span><em>7,423</em></div>
      <div><b>JavaScript</b><span class="bar"><i style="width:13%"></i></span><em>6,750</em></div>
      <div><b>HTML / CSS</b><span class="bar"><i style="width:9%"></i></span><em>4,948</em></div>
      <div><b>其他</b><span class="bar"><i style="width:2%"></i></span><em>613</em></div>
    </div>
    <div class="data-note">Python 含测试与脚本；其他为 SQL / YAML / TOML。统计排除 <code>.venv</code>、<code>node_modules</code>、<code>dist</code> 与运行数据。</div>
  </div>

  <div>
    <div class="subhead">结构</div>
    <div class="quality-row"><b>模块</b><span>3 个 Python 包 · 11 个子模块</span></div>
    <div class="quality-row"><b>后端</b><span>24 文件 · 5,809 行</span></div>
    <div class="quality-row"><b>引擎</b><span>105 文件 · 38,153 行</span></div>
    <div class="quality-row"><b>测试</b><span>44 文件 · 8,145 行 · 256 项用例</span></div>
    <div class="quality-row"><b>前端</b><span>5,815 行 JS / HTML / CSS</span></div>
  </div>
</div>

<div class="ai-split">
  <div class="ai-head"><b>AI 辅助 ≈ 80%</b><span>团队手写 ≈ 20%</span></div>
  <div class="ai-bar"><i style="width:80%"></i><em style="width:20%"></em></div>
  <div class="ai-note">团队自评区间 70–90%；AI 产出经人工审查、测试与代码复核后合入。</div>
</div>

<div class="bottom-note">来源：仓库文件统计（Python 3.12）· git log · tests/TEST_REPORT.md</div>

<!-- 代码量按真实仓库统计，AI 比例为团队自评区间，不伪装成精确测量。 -->

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

<div class="demo-note">演示路径固定，不切窗口；生成慢时直接看检查点和已保存正文。</div>

<div class="bottom-note">来源：README「核心功能」 · docs/software/USER_GUIDE.md · tests/TEST_REPORT.md</div>

<!-- 现场演示：2 分钟从想法到第 1 章，六步路径固定。 -->

---
layout: default
---

<div class="kicker">小结 / SUMMARY</div>

# 把复杂留给系统，<br>把简单留给作者。

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
    <div class="summary-line">四组十二条，<br>每条都有证据。</div>
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

---
layout: center
class: end
---

<div class="end-wrap">
  <div class="end-kicker">Tome Agent · 2026.11</div>
  <div class="end-title">先把「记得住」做对，<br>再谈「写得好」。</div>
  <div class="end-rule"></div>
  <div class="end-sub">谢谢观看 · 欢迎提问</div>
  <div class="end-meta">宇宙无敌暴龙战士 · 查军益 / 秦宗鑫 / 谭钧浩 / 周涛</div>
</div>

<!-- 结束页：留白，不堆信息。 -->
