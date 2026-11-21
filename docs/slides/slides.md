---
theme: default
title: Tome Agent · 第一部分 产品设计与产品设计原则（8 分钟精简版）
info: |
  创新工程实践营项目汇报（8 分钟）
  1. 产品设计、2. 产品设计应用的原则、3. 产品实现
author: 宇宙无敌暴龙战士（查军益 / 秦宗鑫 / 谭钧浩 / 周涛）
transition: fade
colorSchema: light
mdc: true
fonts:
  sans: 'Noto Sans CJK SC, Noto Sans SC, Microsoft YaHei, sans-serif'
  mono: 'JetBrains Mono, Consolas, monospace'
  provider: none
layout: cover
class: cover
---

<div class="absolute top-0 left-0 w-full h-[6px] bg-[#1B3B5F]"></div>

<div class="absolute top-[163px] right-[72px] w-[300px]">
  <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAPIAAAA/CAYAAADaHpXOAAAE8UlEQVR4nO2dv2/TQBTHX6qOlB0k70gZ20goQmrGroyQgbGsUIm/AsSKEAuD+zdkDBLq4iKxdIA1AsrawBx0Ia5c17HP9t295+fvR2qrpu67F999/d79yN2ANoymR/eI6BsR7ZE85kR0nMSz79yOACCRgfk2mh49IaJT6ganSTybcjsBgCQGm0j8k7rH+ySeHXM7AYAUIf8govvUXfaSePaH2wkAONnpuIgNy03XAIBeC1kDp6Pp0UtuJwDgQouQDW8QmUFf0STkNDLf4XYCgNBoE7Jhye0AAKHRKGQzL/6a2wcAQqJSyER0wu0AACHRKmQTlWNuHwAIhVohE9FTbgcACMUuKcYsP03i2S9X9qLheFXn+sXF2XotOwC+0RyRqUMfBAGgFdqFPOF2AIAQaBcyAL3AeR95/u4jhWLy/FmwsgCQDCIyAArY5YyeRdG7zXUA9BXvEdkIzlZ0266DaAFgjMguBWhshex/SyIajs+JaL/J/9ady647V15WVjQcH242TrRhsrg4+2Thn3Obvu9NiPUEToWcFVqViKWL8u/y9+rBw8feK76sktuIKm+jqjG5KKuh2FLm0XC81U8fNm1pe29s60BcRPadCmtPtV2KKm/Td3Rw0egLIrtzmxz1sLHnNEsQN2ptI84eCPiwRuMxDWKQ/bIsY7WJbs5x1fCzdnzYdHj9dR3UWHw09/GgNrtoOjdqQz619iXSJJ41ikDmvlx+vSLfpAKskzq6SsdL0liWNhGASVU0rFEPt2xxrsVn+dCE9P7xtgeAr4pq2P/bxsTWlim3qGEbv12J2aUtBzbn6aEMFdfY+OD1vnU2te45c1cPh5r9r7mnaJFNOVNbrda957sQLmzmsRWhq0jqUvQihKy971sGdxrrI1puiVaNB3i2CUfC1JIURAgZ2GEbCRrMHTsZ/LLIFgbcNiPPguXyB0JmRFAUcNU/7ySRnHrojpC7MNAFQNdARGbC11xun6NSn2Hfs6vHA129TmelELldmrrqrZAB6BqRwOwlaGqN/jEAfkAfGQAFsKbWPe4fgw6zELhfOSIyAAoIJmT0jwHwByIyAApgEzL6xwC4AxGZD2nH2UjzJxQTEsxmR5fV5YdXN37m57KDCBn949v42LdJkz+S33cUYEFINBzvm3KSF4/Wv4/efr7x07ye9QMRGQAG0qha8lA4N2JNhZvHvJ4V847vSLwtGpf9rS9ImY+U4keX0uuoRVTO/2/R72UiLhIz+yFu6fUaB7+absPa1p7EtcDS0+toOPZev3X2ZqsScR7nQtYoyCYb29nCuWFbWj5X2ZJYNKwHFw/XNnWQCh6ffvL85M5vDJ+v0HRDOdtGVNVwXGyHC+pRVKdFr/usAwx2BaJiYINjGqS0vKbRyeIMK7E2Fw53xwwl4nRUGxFZQHqdmQaxisxFR4+42ODex1lT0m3m70eork6ViG0Gu7IgIgubb63xlF4fPZJ5+rc+pQL8p84RPE2w2Rk0HZG2Ebu5HkL2UBF1NnEP1ZB8N06NLBxvgl+zDg7KxJwVMevZT6FoevaTLSHO+2mR6nk5+a+vRM3q4cvi4uygbZmpcLMpd7YtQcgAKACpNQAKgJABUACEDIACIGQAlAh5SXrR/N4AuGY9fK11Csr31BMA0lLrE9KHxvcEQCE3ItZoenRFRHvUbZZJPLvL7QQAFJB/q86f2nROiG0AAAAASUVORK5CYII=" class="w-full" alt="tome" />
</div>

<div class="absolute left-[52px] top-[60px]">
  <div class="text-[62px] font-extrabold leading-none tracking-tight text-[#1D2B3A]">Tome Agent</div>
  <div class="text-[21px] font-bold mt-5 text-[#1B3B5F]">让一个点子，变成一部自洽的长篇小说</div>
  <div class="w-[160px] h-[3px] bg-[#B4472E] mt-6"></div>
  <div class="text-[12px] mt-5 text-[#3B4959]">第一部分 · 产品介绍 ｜ 1. 产品设计（1.1–1.2）　2. 产品设计应用的原则</div>
</div>

<div class="absolute left-[52px] right-[52px] bottom-[38px]">
  <div class="tag mb-2">汇报人</div>
  <div class="flex gap-10">
    <div>
      <div class="text-[18px] font-extrabold text-[#1D2B3A]">查军益</div>
      <div class="text-[10.5px] text-[#6C7784] mt-1">开发 · 生成框架</div>
    </div>
    <div>
      <div class="text-[18px] font-extrabold text-[#1D2B3A]">秦宗鑫</div>
      <div class="text-[10.5px] text-[#6C7784] mt-1">创作与质量评估</div>
    </div>
    <div>
      <div class="text-[18px] font-extrabold text-[#1D2B3A]">谭钧浩</div>
      <div class="text-[10.5px] text-[#6C7784] mt-1">环境与功能测试</div>
    </div>
    <div>
      <div class="text-[18px] font-extrabold text-[#1D2B3A]">周涛</div>
      <div class="text-[10.5px] text-[#6C7784] mt-1">体验与成果文档</div>
    </div>
  </div>
  <div class="mt-4 pt-3 border-t border-[#DAD2C6] flex items-end justify-between">
    <div class="text-[11.5px] text-[#3B4959]">汇报团队：<span class="font-bold text-[#1D2B3A]">宇宙无敌暴龙战士</span>　｜　苏州大学 计算机科学与技术 2025 级</div>
    <div class="text-[10.5px] text-[#A99C88]">2026-11 · 中文工作名：卷宗</div>
  </div>
</div>

<!-- 开场：我们做的是 Tome Agent，一个部署在云服务器上的长篇小说生成助手。这 8 分钟我负责第一部分：它是什么，以及为什么这么设计。 -->
---
layout: default
---
<div class="eyebrow">1.1.1 使命 · 1.1.2 口号</div>

# 让心里有故事的人，写出一部属于自己的自洽长篇

<div class="hr-line"></div>

<div class="card-dk px-6 py-4">
  <div class="text-[13.5px] font-bold leading-[1.7]">使命：把「创作一部长篇」的门槛，从「会不会写」降到「说不说得清一个想法」；把「记得住」交给系统，而不是交给更长的提示词。</div>
</div>

<div class="grid grid-cols-3 gap-3 mt-4">
  <div class="card-soft p-4">
    <div class="tag">门槛</div>
    <div class="body-text mt-2">读者只要给得出题材、主角和走向，就能拿到第 1 章；不需要学写作，也不需要学提示词。</div>
  </div>
  <div class="card-soft p-4">
    <div class="tag">质量</div>
    <div class="body-text mt-2">跨章一致性靠结构化事实管理：每个设定带版本、变更理由和正文出处，可逐条核验。</div>
  </div>
  <div class="card-soft p-4">
    <div class="tag">归属</div>
    <div class="body-text mt-2">作品存在账号空间，随时导出 Markdown；数据可迁移、服务端定期备份。</div>
  </div>
</div>

<div class="card px-4 py-3 mt-4">
  <div class="text-[11.5px] leading-[1.8]"><span class="tag text-[11px]">主口号（对外）：</span>一个点子，一部自洽的长篇。<span class="tag text-[11px]">　副口号（对内）：</span>先把「记得住」做对，再谈「写得好」。</div>
</div>

<!-- 1.1.1 + 1.1.2 合并：使命三件事 + 口号。 -->
---
layout: default
---
<div class="eyebrow">1.1.3 目标用户 · 1.1.4 如何获得用户</div>

# 想创作却不会写的读者：三类画像，三步获客

<div class="hr-line"></div>

<div class="grid grid-cols-3 gap-3">
  <div class="card-soft p-4">
    <div class="tag">画像一</div>
    <div class="text-[12.5px] font-bold mt-1">爱看小说的普通人</div>
    <div class="body-text mt-2">有明确口味（题材、主角、CP、爽点），就是写不出来。诉求：一个点子，先拿到第 1 章。</div>
  </div>
  <div class="card-soft p-4">
    <div class="tag">画像二</div>
    <div class="text-[12.5px] font-bold mt-1">「设定控」读者</div>
    <div class="body-text mt-2">对前后一致、伏笔回收敏感，受够 AI 的「吃设定」。诉求：能查到设定从哪章开始、哪章改变。</div>
  </div>
  <div class="card-soft p-4">
    <div class="tag">画像三</div>
    <div class="text-[12.5px] font-bold mt-1">短视频 / 图文创作者</div>
    <div class="body-text mt-2">需要设定自洽、可直接改的故事脚本。诉求：题材可定制，产物可编辑可导出。</div>
  </div>
</div>

<div class="grid grid-cols-[1.5fr_1fr] gap-3 mt-3">
  <div class="card-soft px-4 py-3">
    <div class="tag">获客三步</div>
    <div class="body-text mt-1 leading-[1.8]">0→100 种子：课程 / 社群内测 +「同题材对照生成」演示　｜　100→1000 内容：把「吃设定」做成可复现案例，README 作信任入口　｜　1000→ 口碑：作品可导出、可分享首章</div>
  </div>
  <div class="card px-4 py-3">
    <div class="tag">三个转化点</div>
    <div class="body-text mt-1 leading-[1.8]">费用可见<br>失败能续（检查点恢复）<br>首章就能判断合不合口味</div>
  </div>
</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">这一版不服务：专业作者的量产工具 ｜ 移动端 App 与多人协作编辑（在线账号已支持）。市场口径（估算）：网文读者 5.75 亿，SAM 290 万–1150 万。</div>

<!-- 1.1.3 + 1.1.4 合并。 -->
---
layout: default
---
<div class="eyebrow">1.1.5 团队优势 · 1.1.6 如何做到差异化</div>

# 四个人的链条，和「不比谁更会写」的差异化

<div class="hr-line"></div>

<div class="flex gap-2">
  <div class="card-soft px-3 py-2 flex-1"><div class="text-[12px] font-bold">查军益</div><div class="small mt-0.5">开发 · 生成框架</div></div>
  <div class="card-soft px-3 py-2 flex-1"><div class="text-[12px] font-bold">秦宗鑫</div><div class="small mt-0.5">创作与质量评估</div></div>
  <div class="card-soft px-3 py-2 flex-1"><div class="text-[12px] font-bold">谭钧浩</div><div class="small mt-0.5">环境与功能测试</div></div>
  <div class="card-soft px-3 py-2 flex-1"><div class="text-[12px] font-bold">周涛</div><div class="small mt-0.5">体验与成果文档</div></div>
</div>
<div class="small mt-2">开发 → 创作评估 → 测试 → 体验文档，每项交付至少一名非负责人复核；计算机专业背景，从「数据一致性、事务、可恢复」切入。</div>

<div class="grid grid-cols-3 gap-3 mt-3">
  <div class="card-soft p-4">
    <div class="tag">差异一</div>
    <div class="text-[12.5px] font-bold mt-1">面向读者，不是作者</div>
    <div class="body-text mt-2">只要一个点子就能出第一部小说；通用 AI 要会写提示词，写作工具要会写作。</div>
  </div>
  <div class="card-soft p-4">
    <div class="tag">差异二</div>
    <div class="text-[12.5px] font-bold mt-1">事实级记忆，不是摘要</div>
    <div class="body-text mt-2">设定带版本、变更理由与正文原句，可逐条核验；摘要会丢细节，事实可以查。</div>
  </div>
  <div class="card-soft p-4">
    <div class="tag">差异三</div>
    <div class="text-[12.5px] font-bold mt-1">提交是事务，不是覆盖</div>
    <div class="body-text mt-2">副本校验、幂等回执、整章原子提交；失败不改正式稿，中断可从检查点续写。</div>
  </div>
</div>

<div class="card-dk px-4 py-2.5 mt-3">
  <div class="text-[11px]">通用 AI 卖「会写」，写作工具卖「作者的效率」，Tome Agent 卖「读者零门槛写出一部自洽的长篇」；承诺边界只到验证过的篇幅（1 万字 / 8–10 章起）。</div>
</div>

<!-- 1.1.5 + 1.1.6 合并。 -->
---
layout: default
---
<div class="eyebrow">1.2 产品定义 · 1.2.1 解决的问题</div>

# 一个点子出一部自洽长篇，要解决的五个症状

<div class="hr-line"></div>

<div class="grid grid-cols-[1.02fr_1fr] gap-4">

<div>
  <div class="grid grid-cols-[78px_1fr] gap-x-3 gap-y-2 items-baseline">
    <div class="tag text-[10.5px]">对于</div><div class="text-[11px]">心里有想看的题材、却不会写小说的普通读者</div>
    <div class="tag text-[10.5px]">他们</div><div class="text-[11px]">想让 AI 写成前后连贯的长篇，但一写长就「吃设定」</div>
    <div class="tag text-[10.5px]">它是一个</div><div class="text-[11px]">部署在云服务器上的长篇小说生成助手</div>
    <div class="tag text-[10.5px]">它能够</div><div class="text-[11px]">用「规划 → 正文 → 事实变更 → 审核 → 提交」维护带出处与版本的记忆</div>
    <div class="tag text-[10.5px]">不同于</div><div class="text-[11px]">面向作者的复杂工作台，也不同于记不住设定的通用聊天</div>
    <div class="tag text-[10.5px]">我们的产品</div><div class="text-[11px]">让不会写小说的人，也能写出一部设定自洽、属于自己的长篇</div>
  </div>
</div>

<div>
  <div class="space-y-[6px]">
    <div class="flex gap-2 items-baseline"><div class="num text-[12px] w-[18px]">01</div><div class="text-[11px]">记不住设定——年龄、关系、能力、地点前后矛盾</div></div>
    <div class="flex gap-2 items-baseline"><div class="num text-[12px] w-[18px]">02</div><div class="text-[11px]">时间线与因果对不上——谁在场、先发生什么</div></div>
    <div class="flex gap-2 items-baseline"><div class="num text-[12px] w-[18px]">03</div><div class="text-[11px]">伏笔与义务不回收——前面埋的线后面忘了</div></div>
    <div class="flex gap-2 items-baseline"><div class="num text-[12px] w-[18px]">04</div><div class="text-[11px]">上下文不可持续——塞全文贵且衰减，摘要丢细节</div></div>
    <div class="flex gap-2 items-baseline"><div class="num text-[12px] w-[18px]">05</div><div class="text-[11px]">生成过程不可恢复——一次失败，成本与进度一起损失</div></div>
  </div>
  <div class="card-dk px-4 py-3 mt-3">
    <div class="text-[11px] font-bold leading-[1.7]">根因：「记忆能力」≠「上下文长度」——所以从「让状态可查、可验、可恢复」入手，而不是写更长的提示词。</div>
  </div>
</div>

</div>

<!-- 1.2 + 1.2.1 合并：模板六行 + 五个症状 + 根因。 -->
---
layout: default
---

<div class="eyebrow">1.2.2 对客户的价值</div>

# 用用户故事说价值：作为谁、完成了什么、带来什么

<div class="hr-line"></div>

<div class="grid grid-cols-2 gap-3">

<div class="card-soft p-4 border-l-[3px] border-l-[#1B3B5F]">
  <div class="tag">作为</div>
  <div class="text-[12.5px] font-bold mt-1">只想看自己想看故事的读者</div>
  <div class="body-text mt-2"><span class="font-bold text-[#1B3B5F]">完成 </span>用一两句话描述题材、主角和走向，生成并读完第 1 章</div>
  <div class="body-text mt-1"><span class="font-bold text-[#1B3B5F]">带来 </span>不必等更新，也不必迁就平台现成的套路</div>
</div>

<div class="card-soft p-4 border-l-[3px] border-l-[#1B3B5F]">
  <div class="tag">作为</div>
  <div class="text-[12.5px] font-bold mt-1">在意前后一致的连载读者</div>
  <div class="body-text mt-2"><span class="font-bold text-[#1B3B5F]">完成 </span>每章后看到人物与物品的关键设定、版本，以及它从哪章开始、哪章改变</div>
  <div class="body-text mt-1"><span class="font-bold text-[#1B3B5F]">带来 </span>后文沿用同一设定，矛盾当场被指出</div>
</div>

<div class="card-soft p-4 border-l-[3px] border-l-[#1B3B5F]">
  <div class="tag">作为</div>
  <div class="text-[12.5px] font-bold mt-1">业余写作者</div>
  <div class="body-text mt-2"><span class="font-bold text-[#1B3B5F]">完成 </span>为一部作品填写文风要求与参考片段，设定从下一章开始生效</div>
  <div class="body-text mt-1"><span class="font-bold text-[#1B3B5F]">带来 </span>后续章节保持相近口吻，已经写好的正文不变</div>
</div>

<div class="card-soft p-4 border-l-[3px] border-l-[#1B3B5F]">
  <div class="tag">作为</div>
  <div class="text-[12.5px] font-bold mt-1">想一次写完多章的作者</div>
  <div class="body-text mt-2"><span class="font-bold text-[#1B3B5F]">完成 </span>设好目标章节数与字数，连续生成并在目标处停下</div>
  <div class="body-text mt-1"><span class="font-bold text-[#1B3B5F]">带来 </span>一口气拿到多章初稿，并知道写到哪里、为什么停下</div>
</div>

</div>

<div class="mt-4 text-[10.5px] leading-[1.8] text-[#6C7784]">每条故事配 Gherkin 验收条件，见 <span class="mono">docs/requirements/user_stories.md</span>（按 INVEST 拆分，共 5 条）。</div>

<!-- 四条用户故事，都是业务语言：读者点单、设定可查、文风统一、连续批量。验收条件在仓库的 user_stories 文档里。 -->

---
layout: default
---
<div class="eyebrow">1.2.3 解决方案</div>

# 云端 Web 服务：浏览器打开就能写，一章一次事务提交

<div class="hr-line"></div>

<div class="text-[11px] leading-[1.7]"><span class="tag text-[11px]">形态：</span>云端 Web 服务，不是小程序 / App——免安装、服务端统一升级与备份、账号隔离作品、免应用商店审核。<span class="tag text-[11px]">　技术：</span>Vue 3.5.44（零构建）+ Python 标准库 HTTP + LangGraph 1.2.17 + PostgreSQL 17（可选）。</div>

<div class="flex gap-1 mt-3">
  <div class="flex-1"><div class="step">下一章规划</div><div class="stepnote">只改下一章</div></div>
  <div class="flex-1"><div class="step">正文候选</div><div class="stepnote">不能改存档</div></div>
  <div class="flex-1"><div class="step">事实变更</div><div class="stepnote">带出处版本</div></div>
  <div class="flex-1"><div class="step">独立审核</div><div class="stepnote">矛盾与遗漏</div></div>
  <div class="flex-1"><div class="step">整章提交</div><div class="stepnote">失败不改正式稿</div></div>
  <div class="flex-1"><div class="step step-alt">导出 Markdown</div><div class="stepnote">可改可投稿</div></div>
</div>

<div class="grid grid-cols-3 gap-3 mt-3">
  <div class="card-soft p-3"><div class="tag">不越权</div><div class="body-text mt-1">规划只提下一章；写作不能直接改存档；审核只判不改。</div></div>
  <div class="card-soft p-3"><div class="tag">可追溯</div><div class="body-text mt-1">每条事实带属性名、版本、变更理由与正文原句，可查从哪章开始、哪章改变。</div></div>
  <div class="card-soft p-3"><div class="tag">可恢复</div><div class="body-text mt-1">副本校验后整章提交；失败不改正式快照，中断从检查点继续。</div></div>
</div>

<div class="card-dk px-4 py-2.5 mt-3">
  <div class="text-[11px]">用户可见的三件事：生成前看得到预估 token 与费用；生成中逐章存检查点；生成后可读章、导出排版 Markdown。</div>
</div>

<!-- 1.2.3 合并形态 + 机制。 -->
---
layout: default
---
<div class="eyebrow">2. 产品设计应用的原则</div>

# 十二条原则，每条一句，且每条都能在仓库里找到证据

<div class="hr-line"></div>

<div class="grid grid-cols-2 gap-3">

<div class="card-soft p-4">
  <div class="tag">组一 · 需求 信息 创新</div>
  <div class="body-text mt-2 leading-[1.8]">
    <div><b>需求原则</b>：从「不会写、吃设定」出发，先冻结 MVP，明确不做清单</div>
    <div><b>信息原则</b>：竞品与长文本架构调研先行，结论写进问题定义</div>
    <div><b>创新原则</b>：事件先行 + 事实账本；提交是事务，不是覆盖</div>
  </div>
</div>

<div class="card-soft p-4">
  <div class="tag">组二 · 系统 收敛 优化</div>
  <div class="body-text mt-2 leading-[1.8]">
    <div><b>系统原则</b>：五阶段状态图，四角色契约固定，失败不污染正式快照</div>
    <div><b>收敛原则</b>：四种记忆方案发散后，收敛到结构化事实 + 三层记忆</div>
    <div><b>优化原则</b>：篇幅动态分配、失败降级、重规划只改未写章节</div>
  </div>
</div>

<div class="card-soft p-4">
  <div class="tag">组三 · 继承 效益 时间</div>
  <div class="body-text mt-2 leading-[1.8]">
    <div><b>继承原则</b>：LangGraph / 兼容协议 / Vue / PostgreSQL，不自造编排</div>
    <div><b>效益原则</b>：单台云服务器 + 用户自带 Key，成本可控、可备份迁移</div>
    <div><b>时间原则</b>：14 天交付计划，窗口期内用对照实验证明价值</div>
  </div>
</div>

<div class="card-soft p-4">
  <div class="tag">组四 · 定量 简化 审核</div>
  <div class="body-text mt-2 leading-[1.8]">
    <div><b>定量原则</b>：成功标准可测（1 万字 / 8–10 章、矛盾数、token 与费用）</div>
    <div><b>简化原则</b>：标准库 HTTP、零前端构建、零外部依赖即可跑</div>
    <div><b>审核原则</b>：独立审核角色 + PR 复核 + ruff / CI 四类 job</div>
  </div>
</div>

</div>

<!-- 十二条压成一页：每条一句做法，详情在完整版里。 -->
---
layout: default
---

<div class="eyebrow">3.1 用户体验设计考虑的因素</div>

# 从「能跑起来」到「敢让作者一直用下去」

<div class="hr-line"></div>

<div class="grid grid-cols-3 gap-3">

<div class="card-soft p-4">
  <div class="tag">可用性</div>
  <div class="text-[12.5px] font-bold mt-1">打开即用，账号隔离</div>
  <div class="body-text mt-2">浏览器访问站点域名，注册登录即进入工作室；每位用户独立数据目录，互不可见。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">连续性</div>
  <div class="text-[12.5px] font-bold mt-1">进度可续，不丢半成品</div>
  <div class="body-text mt-2">每个阶段保存检查点，中断后可恢复；保留已完成章节与待处理任务队列。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">成本</div>
  <div class="text-[12.5px] font-bold mt-1">费用可见，调用前确认</div>
  <div class="body-text mt-2">生成前给出费用预估并由用户确认；记录 token 与用量；模型密钥存在服务端用户目录，不回传网页。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">容错</div>
  <div class="text-[12.5px] font-bold mt-1">失败可见，降级保正文</div>
  <div class="body-text mt-2">超时、响应截断、坏 JSON 等错误对用户可见；局部规划或记忆处理失败时记录问题并保留有效正文。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">可控</div>
  <div class="text-[12.5px] font-bold mt-1">创作流程可控</div>
  <div class="body-text mt-2">创建作品、配置文风、逐章或批量生成、导出排版后的 Markdown；章节可按作者反馈重新生成。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">安全</div>
  <div class="text-[12.5px] font-bold mt-1">技能可控且安全</div>
  <div class="body-text mt-2">每部作品最多选择 5 个写作 Skill，仅以文本注入模型，不执行脚本、工具调用或文件操作。</div>
</div>

</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">来源：README「核心功能」「验证与使用说明」、docs/software/USER_GUIDE.md、code/backend/inf_backend/web.py（路由与错误处理）。</div>

<!-- 六项体验因素：从"能跑"到"敢一直用"。 -->

---
layout: default
---

<div class="eyebrow">3.2 编程语言 / IDE / 平台 / 框架</div>

# 技术选型与版本号

<div class="hr-line"></div>

| 条目名称 | 条目内容 | 版本号 | 选型原因与用途 |
| --- | --- | --- | --- |
| 程序设计语言 | Python | 3.11+（CI 固定 3.11） | 写作引擎、模型接口与后端服务；复用既有引擎与标准库测试 |
| 智能体编排 | LangGraph | 1.2.17 | 用状态图表达规划 / 写作 / 记忆 / 审核，支持条件边与重规划 |
| 前端框架 | Vue（runtime-only） | 3.5.44 | 仓库内置运行时组织交互组件，无需前端构建步骤 |
| 前端语言 | HTML / CSS / JavaScript | 浏览器原生 | 原生技术实现工作室界面，降低构建与部署复杂度 |
| Web 服务 | Python 标准库 `http.server` | 随 Python 版本 | 为服务端进程提供 HTTP 接口，避免再叠一层 Web 框架 |
| 数据库（可选） | PostgreSQL + Psycopg | PG 17（CI 覆盖 17/18）；Psycopg 3.3.3 | 持久化作品、章节与任务；未配置时降级为文件模式 |
| 模型服务 | DeepSeek / OpenAI 兼容接口 | Chat Completions | 沿用已接入接口，复用配置、计费预估与故障测试逻辑 |
| 开发工具 | VS Code 等 Python 编辑器 | 未锁定 | 编辑调试；Ruff + Pylance 方案 A，规则集中在仓库配置文件 |

<div class="card px-4 py-3 mt-4">
  <div class="text-[11px]"><span class="tag text-[11px]">选型原则：</span>「不要太重，也不要太轻」——不引入 ASGI 框架与前端构建链，把复杂度放在智能体编排与状态一致性上；代价是接口验证、错误转换与线程管理由项目自行维护。同一张表已写入仓库 README.md「技术选型」。</div>
</div>

<!-- 选型表：版本号 + 为什么这么选，一行都说清楚。 -->

---
layout: default
---

<div class="eyebrow">3.3 代码仓库链接与提交历史</div>

# 仓库、提交历史与协作看板

<div class="hr-line"></div>

<div class="grid grid-cols-[1fr_1fr] gap-5">

<div>
  <div class="card-soft px-4 py-3">
    <div class="tag">仓库地址</div>
    <div class="text-[11px] mt-1">https://github.com/liuliyisui/tome-agent</div>
    <div class="small mt-2">提交历史：仓库页 Pulse → Insights → Pulse</div>
  </div>
  <div class="card-soft px-4 py-3 mt-3">
    <div class="tag">看板与缺陷追踪</div>
    <div class="small mt-1 leading-[1.8]">任务与缺陷以 GitHub Issues 为正式记录，看板见 docs/mgmt/KANBAN.md（Issue #1–#6）；分工与分支策略见 TEAM_PLAN.md，路线图见 ROADMAP.md，风险与沟通见 COMMUNICATION_AND_RISK_PLAN.md。</div>
  </div>
</div>

<div>
  <div class="tag">每位成员的提交次数</div>
  <div class="text-[10px] mt-1 mb-2" style="color:#8A8072">由 GitHub API /contributors 统计（截至本次汇报）</div>
  <table>
    <thead><tr><th>贡献者</th><th>提交次数</th></tr></thead>
    <tbody>
      <tr><td>liuliyisui</td><td>54</td></tr>
      <tr><td>qinzongxin</td><td>43</td></tr>
      <tr><td>tjh-666-student</td><td>23</td></tr>
      <tr><td>Yulc9527</td><td>4</td></tr>
      <tr><td>合计</td><td>124（仓库 main 分支）</td></tr>
    </tbody>
  </table>
  <div class="ph mt-3" style="height:52px">此处粘贴 GitHub Pulse 提交历史截图（Insights → Pulse，可按成员筛选）</div>
</div>

</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">提交次数来源：GitHub REST API repos/liuliyisui/tome-agent/contributors（统计时间：本次汇报当日）。</div>

<!-- 仓库、提交、看板、缺陷：四个证据一起给。 -->

---
layout: default
---

<div class="eyebrow">3.4 全生命周期主要问题与解决方法</div>

# 问题汇总表（分析 · 设计 · 开发 · 测试 · 部署运维）

<div class="hr-line"></div>

| 问题类别 | 问题名称 | 发生原因 | 解决办法 |
| --- | --- | --- | --- |
| 分析 | 需求边界反复 | 长篇创作需求含糊，演示原型与真实生成混为一谈 | 区分 docs/software/prototype（模拟数据）与正式服务，原型不作为真实生成证据 |
| 设计 | 编排框架迁移 | LangGraph 迁移可能破坏已验证的领域逻辑 | 节点内复用既有模型适配、事件推演与记忆函数，控制迁移范围 |
| 开发 | 模型调用失败 | 网络超时、响应截断、坏 JSON | 记录错误与用量；失败降级，保留已完成正文并区分「请求失败 / 可能已计费 / 内容未审核」 |
| 开发 | 长篇生成中断 | 一次成稿需多次模型调用，耗时长 | 每阶段保存原子检查点，识别待处理任务与损坏检查点 |
| 测试 | 文件与数据库双写 | 数据库记录与文件检查点并非原子事务 | 故障演练确认恢复行为，明确列出未覆盖边界，不过度承诺 |
| 部署运维 | 旧版本无法续写 | 旧检查点运行时哈希与新版本源码不一致 | 禁止手改哈希绕过；升级前保留旧代码与作品 |

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">存储位置：本表已以 Markdown 存入项目仓库 docs/software/ISSUES_SUMMARY.md。来源：architecture.md、CODE_QUALITY_FIXES.md、retrospection/README.md。</div>

<!-- 六类问题：分析、设计、开发×2、测试、部署运维。 -->

---
layout: default
---

<div class="eyebrow">3.5.1 系统架构图</div>

# 系统架构：分层自下而上

<div class="hr-line"></div>

<div class="flex items-stretch gap-2 mt-3">

<div class="card-soft px-3 py-4 flex-1">
  <div class="tag">存储层</div>
  <div class="body-text mt-2 leading-[1.7]">应用原子检查点（本地文件）<br>PostgreSQL（可选）：作品 / 章节 / 任务 / 用量</div>
</div>

<div class="flex items-center text-[14px]" style="color:#A99C88">→</div>

<div class="card-soft px-3 py-4 flex-1">
  <div class="tag">引擎层</div>
  <div class="body-text mt-2 leading-[1.7]">LangGraph 状态图 · 事件推演<br>三层记忆 · 连续性校验 · 失败降级</div>
</div>

<div class="flex items-center text-[14px]" style="color:#A99C88">→</div>

<div class="card-soft px-3 py-4 flex-1">
  <div class="tag">服务层</div>
  <div class="body-text mt-2 leading-[1.7]">Python HTTP 服务<br>127.0.0.1:8765<br>WritingSession 会话入口</div>
</div>

<div class="flex items-center text-[14px]" style="color:#A99C88">→</div>

<div class="card-soft px-3 py-4 flex-1">
  <div class="tag">界面层</div>
  <div class="body-text mt-2 leading-[1.7]">正式 Vue 3 页面 code/frontend<br>书架 / 文风 / 费用确认 / 生成 / 导出</div>
</div>

</div>

<div class="grid grid-cols-[1fr_1fr] gap-4 mt-4">
  <div class="card px-4 py-3">
    <div class="tag">模型服务（服务层旁路调用）</div>
    <div class="small mt-1 leading-[1.7]">DeepSeek / OpenAI 兼容接口；chat_provider 封装请求、超时与用量。</div>
  </div>
  <div class="card px-4 py-3">
    <div class="tag">依赖方向</div>
    <div class="small mt-1 leading-[1.7]">界面 → 服务 → 引擎 → 存储；引擎不感知界面与传输层，便于替换与测试。</div>
  </div>
</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">图源：docs/software/architecture.md、docs/algorithm/LANGGRAPH.mmd、code/backend/inf_backend/、code/core_engine/memory_runtime/。</div>

<!-- 四层架构：存储→引擎→服务→界面，模型服务旁路。 -->

---
layout: default
---

<div class="eyebrow">3.5.2 基础设施图</div>

# 部署形态：单台云服务器，Nginx 前置 HTTPS

<div class="hr-line"></div>

<div class="flex items-stretch gap-2 mt-3">
  <div class="card-soft px-3 py-4 flex-1">
    <div class="tag">用户</div>
    <div class="body-text mt-2">浏览器访问 https://域名<br>注册 / 登录后进入工作室</div>
  </div>
  <div class="flex items-center text-[14px]" style="color:#A99C88">→</div>
  <div class="card-soft px-3 py-4 flex-1">
    <div class="tag">Nginx（443）</div>
    <div class="body-text mt-2">TLS 终止、反向代理<br>登录 / 注册接口限流</div>
  </div>
  <div class="flex items-center text-[14px]" style="color:#A99C88">→</div>
  <div class="card-soft px-3 py-4 flex-1">
    <div class="tag">应用（127.0.0.1:8765）</div>
    <div class="body-text mt-2">systemd 守护、只监听本机<br>进程池按用户隔离</div>
  </div>
  <div class="flex items-center text-[14px]" style="color:#A99C88">→</div>
  <div class="card-soft px-3 py-4 flex-1">
    <div class="tag">数据</div>
    <div class="body-text mt-2">/var/lib/tome-agent<br>账号 · 作品 · Skill · 配置</div>
  </div>
</div>

<div class="grid grid-cols-3 gap-3 mt-4">

<div class="card-soft p-4">
  <div class="tag">只开必要端口</div>
  <div class="body-text mt-2">8765 不对外暴露，防火墙仅放行 80 / 443；SSH 限定可信来源。代码在 /opt/tome-agent，数据在 /var/lib，不写入代码目录。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">隔离与并发</div>
  <div class="body-text mt-2">每位用户独立数据目录与进程；TOME_WORKER_LIMIT 控制常驻进程数（1–8，默认 3），空闲 5 分钟回收，超限时新请求排队重试。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">备份与恢复</div>
  <div class="body-text mt-2">备份覆盖账号、作品与模型配置（含密钥，需加密保存并限制访问），上线前必须做恢复演练；无自助改密，管理员可重置密码。</div>
</div>

</div>

<div class="card px-4 py-3 mt-3">
  <div class="text-[10.5px] leading-[1.75]"><span class="tag text-[10px]">已知边界与合规：</span>中国内地服务器对外提供域名服务需完成备案；单机方案不支持多实例共享同一数据目录；公开注册前需补滥用防护、监控、容量与恢复流程；服务重启可能中断生成，需按检查点续写。来源：docs/software/LINUX_HOSTED.md。</div>
</div>

<!-- 云部署：Nginx 443 → 应用仅本机 8765 → 数据目录；只开必要端口、进程池隔离、备份含密钥。 -->
---
layout: default
---

<div class="eyebrow">3.5.3 智能体技术设计（一）</div>

# 任务编排：状态图与事件先行

<div class="hr-line"></div>

<div class="flex items-center gap-1 mt-4">
  <div class="step flex-1">开始</div>
  <div class="text-[11px]" style="color:#A99C88">→</div>
  <div class="step flex-1">event_planner<br>事件规划</div>
  <div class="text-[11px]" style="color:#A99C88">→</div>
  <div class="step flex-1">event_writer<br>正文生成</div>
  <div class="text-[11px]" style="color:#A99C88">→</div>
  <div class="step flex-1">event_commit<br>提交章节</div>
  <div class="text-[11px]" style="color:#A99C88">→</div>
  <div class="step flex-1">memory<br>三层记忆</div>
  <div class="text-[11px]" style="color:#A99C88">→</div>
  <div class="step flex-1">reviewer<br>审核</div>
  <div class="text-[11px]" style="color:#A99C88">→</div>
  <div class="step step-alt flex-1">结束</div>
</div>

<div class="text-[9.5px] mt-2" style="color:#8A8072">event_writer → event_planner 之间存在 revise 修订回边；coordinator 亦由审核条件边选择提交或拒绝。</div>

<div class="grid grid-cols-2 gap-4 mt-4">
  <div class="card-soft p-4">
    <div class="tag">任务编排</div>
    <div class="body-text mt-2">规划、写作、提交、记忆、审核为独立节点；写作提出事件修订时经条件边返回规划节点（保留一次修订上限）。严格事务入口 Coordinator 决定提交或拒绝。</div>
  </div>
  <div class="card-soft p-4">
    <div class="tag">事件先行 + 三层记忆</div>
    <div class="body-text mt-2">先规划场景事件并推演状态，再生成正文；工作记忆、近期记忆、长期记忆分层保存并保留正文来源，避免整本重发。</div>
  </div>
</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">图源：docs/algorithm/LANGGRAPH.mmd（Mermaid 源文件，节点名与边标签与源码一致）。</div>

<!-- 状态图五个节点加 revise 回边；事件先行是这一节的核心创新。 -->

---
layout: default
---

<div class="eyebrow">3.5.3 智能体技术设计（二）</div>

# 记忆、护栏与专业知识库

<div class="hr-line"></div>

<div class="grid grid-cols-2 gap-3">

<div class="card-soft p-4">
  <div class="tag">连续性管理</div>
  <div class="body-text mt-2">跟踪人物、物品、时间、任务、知识来源与状态版本，由领域规则校验状态变化，结构化契约替代「整本重发」，减少上下文与调用成本。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">护栏与失败降级</div>
  <div class="body-text mt-2">记忆处理失败时记录问题并保留已生成的有效正文；失败状态与「内容未审核」严格区分；审核为模式开关，当前配置为正文审核关闭，不宣称每章均经模型审核。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">专业知识库：写作 Skill</div>
  <div class="body-text mt-2">作品级选择（每部作品最多 5 个）写作 Skill，生成正文时以文本注入模型，与记忆协作补充风格与要求；技能不执行脚本、工具调用或文件操作。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">模型选择与边界</div>
  <div class="body-text mt-2">本项目不训练算法模型，核心是 LangGraph 编排 + 事件先行 + 三层记忆；未采用向量检索（相似度不能判断事实是否过期），列为后续补充；未启用 LangGraph 原生 checkpoint，沿用应用自身原子检查点。</div>
</div>

</div>

<div class="card px-4 py-3 mt-3">
  <div class="text-[10px] leading-[1.8]"><span class="tag text-[10px]">开源框架与官方文档：</span>langchain.com/oss/python/langgraph · DeepSeek API 文档 · PostgreSQL 事务 · Psycopg 3 事务管理 · Vue 渲染函数 · Python http.server · Docker Compose 文档 · GitHub Actions Python CI 指南。</div>
</div>

<!-- 记忆/护栏/知识库/模型边界，四块拼成智能体设计。 -->

---
layout: default
---

<div class="eyebrow">3.5.4 数据库设计</div>

# PostgreSQL 数据模型（E-R 图）

<div class="hr-line"></div>

<div class="card-soft px-4 py-3">
  <div class="tag">tome_books 作品主表</div>
  <div class="small mt-1 leading-[1.7]">id (PK) · metadata jsonb · state jsonb · state_kind (snapshot/longform) · style jsonb · checkpoint · last_usage jsonb · pinned · deleted_at / restore_token</div>
</div>

<div class="grid grid-cols-3 gap-3 mt-3">

<div class="card-soft p-3">
  <div class="tag">tome_chapters 章节（1:N）</div>
  <div class="small mt-1 leading-[1.7]">book_id, number (PK, FK)<br>title · body · version</div>
</div>

<div class="card-soft p-3">
  <div class="tag">tome_jobs 生成任务（1:N）</div>
  <div class="small mt-1 leading-[1.7]">id (PK) · book_id (FK)<br>status(running/completed/failed/interrupted) · payload jsonb</div>
</div>

<div class="card-soft p-3">
  <div class="tag">tome_usage 用量记录</div>
  <div class="small mt-1 leading-[1.7]">book_id, checkpoint (PK)<br>payload jsonb · saved_at</div>
</div>

<div class="card-soft p-3">
  <div class="tag">tome_chapter_versions 章节版本</div>
  <div class="small mt-1 leading-[1.7]">book_id, number, version (PK)<br>title · body · created_at</div>
</div>

<div class="card-soft p-3">
  <div class="tag">tome_schema_version 结构版本</div>
  <div class="small mt-1 leading-[1.7]">version (PK) · applied_at<br>3 个索引 + 1 个唯一索引</div>
</div>

<div class="card px-3 py-2">
  <div class="tag">设计要点</div>
  <div class="small mt-1 leading-[1.7]">JSONB 承载结构化状态；回收站用 deleted_at + restore_token 实现软删除与恢复；未配置数据库时降级为文件模式。</div>
</div>

</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">来源：code/backend/inf_backend/schema.sql（6 张表 + 3 索引 + 1 唯一索引）逆生成；Mermaid 原始图见 docs/algorithm/ER.mmd。</div>

<!-- E-R：六张表 + 设计要点；由 schema.sql 逆生成。 -->

---
layout: default
---

<div class="eyebrow">3.5.5 接口设计</div>

# 真实 HTTP 路由（取自 web.py）

<div class="hr-line"></div>

| 接口名称 | 方法 | 接口功能 | 输出对象 |
| --- | --- | --- | --- |
| `/api/model-config` | GET / POST | 读取与保存模型服务配置 | 模型配置（密钥不回传） |
| `/api/skills` | GET / POST | 列出与安装写作 Skill | 技能列表 |
| `/api/books` | GET / POST | 书架列表 / 新建作品 | 作品列表 / 作品 id |
| `/api/books/{id}/generate` | POST | 触发生成任务 | 任务对象（HTTP 202） |
| `/api/books/{id}/estimate` | POST | 生成前费用预估 | 预估费用 |
| `/api/books/{id}/chapters/{n}/regenerate` | POST | 按作者反馈重写章节 | 任务对象 |
| `/api/books/{id}/export` | GET | 导出排版后的 Markdown | Markdown 文件 |
| `/api/jobs/{id}` | GET | 查询生成任务进度 | 状态与进度 |

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">来源：code/backend/inf_backend/web.py（do_GET / do_POST 路由分派）与 service.py；异常统一转为 JSON 错误响应，生成任务返回 202 表示已受理。完整参数见 Swagger / APIFox。</div>

<!-- 接口：12 行路由，覆盖模型配置、技能、作品、章节、任务、导出。 -->

---
layout: default
---

<div class="eyebrow">3.5.6 前端设计</div>

# 前端：渐进式 Vue 3，零构建、无 CDN

<div class="hr-line"></div>

<div class="grid grid-cols-2 gap-3">

<div class="card-soft p-4">
  <div class="tag">正式界面（code/frontend）</div>
  <div class="body-text mt-2">HTML / CSS / JavaScript 原生页面，由 Vue 3.5.44 渐进管理交互；采用仓库内置 runtime-only 运行时与 h() 渲染函数，无前端构建步骤、不依赖 CDN；响应式组件覆盖书架、废案箱、文风保存、删除恢复、费用确认与取消；生成任务在后台线程执行，页面轮询任务状态展示进度。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">独立交互原型（docs/software/prototype）</div>
  <div class="body-text mt-2">以模拟数据与 localStorage 展示交互流程，不调用模型、不读写正式存档；原型演示不作为真实生成或数据持久化的证据，答辩时可现场说明两者差别。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">选型取舍</div>
  <div class="body-text mt-2">相较立即重建 React/Vue 单页工程，渐进方案复用现有功能、缩小学习范围；代价是命令式交互与组件状态并存，必须明确接口、事件与重复提交控制。若后续面向公网多用户，则需重新评估构建链、鉴权与任务队列。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">界面与需求对应</div>
  <div class="body-text mt-2">界面动作与用户故事一一对应：创建作品、配置文风、确认费用、逐章生成、失败恢复、导出 Markdown（见 docs/requirements/user_stories.md），使 8 分钟演示可按故事线顺序进行。</div>
</div>

</div>

<!-- 前端：渐进式 Vue，为什么不上构建链，以及原型与正式界面的区别。 -->

---
layout: default
---

<div class="eyebrow">3.6 软件质量（3.6.1 方法 + 3.6.2 工具）</div>

# 质量控制与保证

<div class="hr-line"></div>

<div class="grid grid-cols-2 gap-3">

<div class="card-soft p-4">
  <div class="tag">3.6.1 方法与保证</div>
  <div class="body-text mt-2"><b>日志</b>：记录模型请求、用量与错误（超时、截断、格式不符），区分「请求失败 / 可能已计费 / 内容未审核」。<br><b>异常与错误处理</b>：失败降级保留已生成正文；检查点记录待处理任务；接口异常统一转 JSON 错误响应；版本指纹不一致时拒绝续写而非静默覆盖。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">3.6.2 工具使用</div>
  <div class="body-text mt-2"><b>Ruff 0.17.4</b>（Linter + Formatter 二合一，覆盖 PEP 8 风格与语义规则）：规则集 E、W、F、I、B、C4、UP，ignore = ["E501"]，line-length = 88，target-version = "py311"；规则集中于 code/backend/pyproject.toml，编辑器、预提交与 CI 共用同一份配置。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">整改结果（有据可查）</div>
  <div class="body-text mt-2">整改前基线 <b>75 处不合规</b>（E402 42、B023 14、B904 12、B007 3、F841 3、E731 1、I001 36）；整改后 <b>0 处</b>，ruff format 全仓库无差异；改动 44 个 .py 文件（+240 / −194 行）。详见 docs/software/CODE_QUALITY_FIXES.md。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">自动化与佐证</div>
  <div class="body-text mt-2"><b>预提交钩子</b>：ruff-pre-commit v0.17.4（ruff --fix、ruff-format）+ pre-commit-hooks v4.6.0（check-toml、check-yaml、end-of-file-fixer、trailing-whitespace）。<br><b>CI</b>：.github/workflows/tests.yml 含 lint、Windows 测试、postgresql（17/18 矩阵）、hosted-linux 四类 job。<br><b>代码复杂度</b>：可继续用 VS Code 插件（complexipy / Pylint）补测，当前以 Ruff 规则与测试覆盖为主要证据。</div>
</div>

</div>

<!-- 质量：日志与异常、Ruff 规则、75→0 的整改、CI 四类 job。 -->

---
layout: default
---

<div class="eyebrow">3.7 代码统计</div>

# 模块数与代码行数

<div class="hr-line"></div>

<div class="grid grid-cols-[1.2fr_1fr] gap-5">

<div>
  <table>
    <thead><tr><th>模块</th><th>文件数</th><th>行数</th></tr></thead>
    <tbody>
      <tr><td>code/core_engine（Python，写作与记忆引擎）</td><td>101</td><td>15,217</td></tr>
      <tr><td>code/backend（Python，后端服务）</td><td>8</td><td>1,018</td></tr>
      <tr><td>tests（Python，单元 + 集成）</td><td>11</td><td>1,117</td></tr>
      <tr><td>code/frontend（JS / HTML / CSS）</td><td>3</td><td>314</td></tr>
      <tr><td>合计</td><td>123</td><td>17,666</td></tr>
    </tbody>
  </table>
  <div class="small mt-2">统计口径：本地克隆快照逐文件累计（.py / .js / .html / .css），提交 0759e38；正式答辩请用 VS Code Counter 插件重跑并附截图。</div>
</div>

<div>
  <div class="card-soft px-4 py-3">
    <div class="tag">AI Vibe Coding 与团队自写代码比例</div>
    <div class="body-text mt-1">仓库未提供官方比例数据，需按统一口径统计后填入：建议按「提交作者 + 提交说明 + 是否 AI 生成」三要素归类，输出 AI 辅助生成行数 / 总行数比值，并注明统计工具（如 git log --numstat 结合人工抽查）。</div>
  </div>
  <div class="ph mt-3" style="height:96px">此处粘贴 VS Code Counter 统计截图<br>含按语言分行的行数统计，以及 AI 辅助编写比例的说明</div>
</div>

</div>

<!-- 代码统计：四模块 17,666 行；AI 比例需按口径统计后填。 -->

---
layout: default
---

<div class="eyebrow">小结</div>

# 第三部分到此：产品实现要点已覆盖 3.1 – 3.7

<div class="hr-line"></div>

<div class="grid grid-cols-2 gap-3">

<div class="card-soft px-4 py-3">
  <div class="tag">主要来源（可公开验证）</div>
  <div class="small mt-1 leading-[1.9]">
    <div>· 仓库：github.com/liuliyisui/tome-agent — README「技术选型」「核心功能」「验证与使用说明」</div>
    <div>· docs/software/architecture.md、docs/algorithm/LANGGRAPH.mmd</div>
    <div>· docs/software/code_quality.md、CODE_QUALITY_FIXES.md</div>
    <div>· docs/software/DEPLOY.md、WINDOWS_PORTABLE.md、LINUX_HOSTED.md、POSTGRESQL.md</div>
    <div>· code/backend/inf_backend/schema.sql、web.py / service.py</div>
    <div>· docs/mgmt/KANBAN.md、TEAM_PLAN.md、ROADMAP.md、COMMUNICATION_AND_RISK_PLAN.md</div>
  </div>
</div>

<div class="card-dk px-5 py-5 flex flex-col justify-center">
  <div class="text-[22px] font-extrabold">谢谢观看 · 欢迎提问</div>
  <div class="text-[11px] mt-3 leading-[1.9]" style="color:#E8E0D2">第一部分 1、2、3 三节合并完成：<br>产品设计（1.1–1.2）· 十二条设计原则（2）· 产品实现（3.1–3.7）</div>
</div>

</div>

<!-- 收尾：来源清单 + 谢谢。 -->
