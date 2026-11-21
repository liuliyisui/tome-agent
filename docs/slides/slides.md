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
</div>

<div class="absolute left-[52px] right-[52px] bottom-[76px]">
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

<div class="eyebrow">汇报目录</div>

# 三个部分、24 页：8 分钟讲完设计与实现

<div class="hr-line"></div>

<div class="grid grid-cols-2 gap-6">

<div>

<div class="text-[12.5px] font-bold text-[#1B3B5F]">1 · 产品设计</div>
<div class="mt-1">
  <div class="flex items-baseline justify-between py-[7px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.1.1 使命 · 1.1.2 口号</div><div class="text-[11px] font-bold text-[#1B3B5F]">P3</div></div>
  <div class="flex items-baseline justify-between py-[7px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.1.3 目标用户 · 1.1.4 如何获得用户</div><div class="text-[11px] font-bold text-[#1B3B5F]">P4</div></div>
  <div class="flex items-baseline justify-between py-[7px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.1.5 团队优势 · 1.1.6 差异化</div><div class="text-[11px] font-bold text-[#1B3B5F]">P5</div></div>
  <div class="flex items-baseline justify-between py-[7px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.2 产品定义 · 1.2.1 五个症状</div><div class="text-[11px] font-bold text-[#1B3B5F]">P6</div></div>
  <div class="flex items-baseline justify-between py-[7px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.2.2 对客户的价值（用户故事）</div><div class="text-[11px] font-bold text-[#1B3B5F]">P7</div></div>
  <div class="flex items-baseline justify-between py-[7px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.2.3 解决方案（形态 + 机制）</div><div class="text-[11px] font-bold text-[#1B3B5F]">P8</div></div>
</div>

<div class="text-[12.5px] font-bold text-[#1B3B5F] mt-5">2 · 产品设计应用的原则</div>
<div class="mt-1">
  <div class="flex items-baseline justify-between py-[7px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">十二条原则：四组，每组三条</div><div class="text-[11px] font-bold text-[#1B3B5F]">P9–10</div></div>
<div class="text-[10.5px] mt-1 leading-[1.7]" style="color:#8A8072">需求 / 信息 / 创新 · 系统 / 收敛 / 优化 · 继承 / 效益 / 时间 · 定量 / 简化 / 审核</div>
</div>

</div>

<div>

<div class="text-[12.5px] font-bold text-[#1B3B5F]">3 · 产品实现</div>
<div class="mt-1">
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.1 用户体验设计考虑的因素</div><div class="text-[11px] font-bold text-[#1B3B5F]">P11</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.2 编程语言 / IDE / 平台 / 框架</div><div class="text-[11px] font-bold text-[#1B3B5F]">P12</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.3 代码仓库链接与提交历史</div><div class="text-[11px] font-bold text-[#1B3B5F]">P13</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.4 全生命周期问题与解决方法</div><div class="text-[11px] font-bold text-[#1B3B5F]">P14</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.1 系统架构图</div><div class="text-[11px] font-bold text-[#1B3B5F]">P15</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.2 基础设施与部署形态</div><div class="text-[11px] font-bold text-[#1B3B5F]">P16</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.3 智能体技术设计（编排 / 记忆 / 护栏）</div><div class="text-[11px] font-bold text-[#1B3B5F]">P17–18</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.4 数据库设计（E-R）</div><div class="text-[11px] font-bold text-[#1B3B5F]">P19</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.5 接口设计</div><div class="text-[11px] font-bold text-[#1B3B5F]">P20</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.6 前端设计</div><div class="text-[11px] font-bold text-[#1B3B5F]">P21</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.6 软件质量（方法与工具）</div><div class="text-[11px] font-bold text-[#1B3B5F]">P22</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.7 代码统计</div><div class="text-[11px] font-bold text-[#1B3B5F]">P23</div></div>
</div>

</div>

</div>

<!-- 目录页：把封面上的范围说明搬到这里并补全到每个小节。 -->
---
layout: default
---
<div class="eyebrow">1.1.1 使命 · 1.1.2 口号</div>

# 让心里有故事的人，写出一部属于自己的自洽长篇

<div class="hr-line"></div>

<div class="card px-6 py-4">
  <div class="text-[13.5px] font-bold leading-[1.7]"><span style="color:#B4472E">使命：</span>把「创作一部长篇」的门槛，从「会不会写」降到「说不说得清一个想法」；把「记得住」交给系统，而不是交给更长的提示词。</div>
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

<div class="card px-4 py-2.5 mt-3">
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
  <div class="card px-4 py-3 mt-3">
    <div class="text-[11px] font-bold leading-[1.7]"><span style="color:#B4472E">根因：</span>「记忆能力」≠「上下文长度」——所以从「让状态可查、可验、可恢复」入手，而不是写更长的提示词。</div>
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

<div class="card px-4 py-2.5 mt-3">
  <div class="text-[11px]">用户可见的三件事：生成前看得到预估 token 与费用；生成中逐章存检查点；生成后可读章、导出排版 Markdown。</div>
</div>

<!-- 1.2.3 合并形态 + 机制。 -->
---
layout: default
---
<div class="eyebrow">2. 产品设计应用的原则（1/2）</div>

# 需求定方向，信息校准方向，创新才有落脚点

<div class="hr-line"></div>

<div class="grid grid-cols-2 gap-3">

<div class="card-soft px-4 py-3">
  <div class="tag">组一 · 需求 信息 创新</div>

  <div class="mt-2">
    <div class="text-[12px] font-bold text-[#1B3B5F]">需求原则</div>
    <div class="text-[10px] leading-[1.55]" style="color:#6C7784">功能要求来自客观需求；显需求推动改进，隐需求催生创新。</div>
    <div class="body-text mt-1">先冻结 MVP 与「不做」清单：单用户账号、中文、顺序逐章；多人协作 / 移动端 / 自动出版明确不做。<span class="ev">problem_definition.md</span></div>
  </div>

  <div class="mt-2.5">
    <div class="text-[12px] font-bold text-[#1B3B5F]">信息原则</div>
    <div class="text-[10px] leading-[1.55]" style="color:#6C7784">全面、充分、正确地掌握市场与技术信息，用它引导设计。</div>
    <div class="body-text mt-1">先做竞品与长文本方案对比（长上下文 / 摘要 / 向量 / 结构化事实），结论写进问题定义，再定功能。<span class="ev">architecture.md</span></div>
  </div>

  <div class="mt-2.5">
    <div class="text-[12px] font-bold text-[#1B3B5F]">创新原则</div>
    <div class="text-[10px] leading-[1.55]" style="color:#6C7784">冲破传统观念与惯例的束缚，做别人没做的。</div>
    <div class="body-text mt-1">事件先行 + 事实账本：每条设定带版本与正文原句；提交是事务，失败不改正式稿。<span class="ev">LANGGRAPH.mmd</span></div>
  </div>
</div>

<div class="card-soft px-4 py-3">
  <div class="tag">组二 · 系统 收敛 优化</div>

  <div class="mt-2">
    <div class="text-[12px] font-bold text-[#1B3B5F]">系统原则</div>
    <div class="text-[10px] leading-[1.55]" style="color:#6C7784">把产品看作技术系统，用系统论求功能结构、取综合最优。</div>
    <div class="body-text mt-1">写作拆成「规划—写作—记忆—审核—提交」的状态系统，四角色契约固定，任何环节失败都不污染正式快照。<span class="ev">LANGGRAPH.mmd</span></div>
  </div>

  <div class="mt-2.5">
    <div class="text-[12px] font-bold text-[#1B3B5F]">收敛原则</div>
    <div class="text-[10px] leading-[1.55]" style="color:#6C7784">先发散构思，再综合多种信息收敛。</div>
    <div class="body-text mt-1">记忆方案对比四种后收敛到「结构化事实 + 三层记忆」；首版只带最近两章、最多 128 条有效事实。<span class="ev">architecture.md L75</span></div>
  </div>

  <div class="mt-2.5">
    <div class="text-[12px] font-bold text-[#1B3B5F]">优化原则</div>
    <div class="text-[10px] leading-[1.55]" style="color:#6C7784">方案择优、参数优化、总体优化：高效、优质、经济。</div>
    <div class="body-text mt-1">篇幅按目标字数与剩余章节动态分配；局部失败降级保正文；审核格式错误最多修一次。<span class="ev">README</span></div>
  </div>
</div>

</div>

<!-- 原则 1/2：组一、组二。 -->

---
layout: default
---

<div class="eyebrow">2. 产品设计应用的原则（2/2）</div>

# 能继承的不重造，算清效益，抢住时间窗口

<div class="hr-line"></div>

<div class="grid grid-cols-2 gap-3">

<div class="card-soft px-4 py-3">
  <div class="tag">组三 · 继承 效益 时间</div>

  <div class="mt-2">
    <div class="text-[12px] font-bold text-[#1B3B5F]">继承原则</div>
    <div class="text-[10px] leading-[1.55]" style="color:#6C7784">批判地吸收前人成果，为我所用，才能集中精力解决主要问题。</div>
    <div class="body-text mt-1">编排 / 接口 / 前端 / 存储全部复用成熟方案（LangGraph、兼容接口、Vue、PostgreSQL），只重写业务逻辑。<span class="ev">README 技术选型</span></div>
  </div>

  <div class="mt-2.5">
    <div class="text-[12px] font-bold text-[#1B3B5F]">效益原则</div>
    <div class="text-[10px] leading-[1.55]" style="color:#6C7784">既讲技术经济效益，也讲社会效益。</div>
    <div class="body-text mt-1">生成前给出费用预估、单台服务器托管、用户自带 Key；成本可算、可省，作品可备份迁移。<span class="ev">official_pricing.py</span></div>
  </div>

  <div class="mt-2.5">
    <div class="text-[12px] font-bold text-[#1B3B5F]">时间原则</div>
    <div class="text-[10px] leading-[1.55]" style="color:#6C7784">加快研制节奏，并预测同类产品在开发期的变化。</div>
    <div class="body-text mt-1">两周交付计划 + M1–M4 里程碑；窗口期内用对照实验证明「状态记忆减少吃设定」。<span class="ev">TEAM_PLAN.md</span></div>
  </div>
</div>

<div class="card-soft px-4 py-3">
  <div class="tag">组四 · 定量 简化 审核</div>

  <div class="mt-2">
    <div class="text-[12px] font-bold text-[#1B3B5F]">定量原则</div>
    <div class="text-[10px] leading-[1.55]" style="color:#6C7784">方案选择与成果评价尽量采用科学的定量方法。</div>
    <div class="body-text mt-1">成功标准可测（约 1 万字 / 8–10 章、跨章矛盾数、token 与费用）；127 项应用回归 + 42 项引擎回归。<span class="ev">VALIDATION.md</span></div>
  </div>

  <div class="mt-2.5">
    <div class="text-[12px] font-bold text-[#1B3B5F]">简化原则</div>
    <div class="text-[10px] leading-[1.55]" style="color:#6C7784">保证功能的前提下力求简化，降成本、保质量。</div>
    <div class="body-text mt-1">标准库 HTTP、零前端构建、零外部依赖即可跑；不引入 ASGI 框架与前端构建链。<span class="ev">README</span></div>
  </div>

  <div class="mt-2.5">
    <div class="text-[12px] font-bold text-[#1B3B5F]">审核原则</div>
    <div class="text-[10px] leading-[1.55]" style="color:#6C7784">随时审核每个设计步骤的信息，确保每一步正确。</div>
    <div class="body-text mt-1">独立审核节点（查矛盾与遗漏、只判不改）+ PR 必他人复核 + ruff / CI 四类 job。<span class="ev">tests.yml</span></div>
  </div>
</div>

</div>

<div class="absolute left-[52px] bottom-[16px] text-[9px] text-[#A99C88]">每条先写原则要求，再写本产品的做法，末尾为该做法在仓库中的位置；找不到对应实践的条目不列入。</div>

<!-- 原则 2/2：组三、组四。 -->
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
  <div class="body-text mt-2">创建作品、配置文风、逐章或批量生成；支持逐章本地修改与复查（易错词、重复标点、敏感信息）后再导出 Markdown；章节可按作者反馈重写。</div>
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
  <div class="card-soft px-5 py-4">
    <div class="tag text-[11px]">仓库地址</div>
    <div class="text-[13.5px] mt-2">https://github.com/liuliyisui/tome-agent</div>
    <div class="text-[12px] mt-2" style="color:#6C7784">提交历史：仓库页 Pulse → Insights → Pulse</div>
  </div>
  <div class="card-soft px-5 py-4 mt-3">
    <div class="tag text-[11px]">看板与缺陷追踪</div>
    <div class="text-[12.5px] mt-2 leading-[1.9]" style="color:#3B4959">任务与缺陷以 GitHub Issues 为正式记录，看板见 docs/mgmt/KANBAN.md（Issue #1–#6）；分工与分支策略见 TEAM_PLAN.md，路线图见 ROADMAP.md，风险与沟通见 COMMUNICATION_AND_RISK_PLAN.md。</div>
  </div>
</div>

<div>
  <div class="tag">每位成员的提交次数</div>
  <img src="data:image/png;base64,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" class="mt-2 w-full rounded-[8px] border border-[#DAD2C6]" alt="GitHub Pulse · Top committers" />
  <div class="text-[12px] mt-2 leading-[1.7]" style="color:#6C7784">Top committers：仓库 Insights → Pulse（近 12 个月，截至 2026-11-21）；横轴为贡献者，纵轴为提交次数。</div>
</div>

</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">提交分布来源：GitHub Pulse → Top committers（仓库 Insights → Pulse，近 12 个月）。</div>

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
  <div class="body-text mt-2 leading-[1.7]">Python HTTP 服务<br>127.0.0.1:8765<br>WritingSession 会话入口<br>编辑 / 复查 / 隐私检查</div>
</div>

<div class="flex items-center text-[14px]" style="color:#A99C88">→</div>

<div class="card-soft px-3 py-4 flex-1">
  <div class="tag">界面层</div>
  <div class="body-text mt-2 leading-[1.7]">正式 Vue 3 页面 code/frontend<br>书架 / 文风 / 费用 / 生成 / 编辑 / 导出</div>
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
  <div class="body-text mt-2">HTML / CSS / JavaScript 原生页面，由 Vue 3.5.44 渐进管理交互；仓库内置 runtime-only 运行时与 h() 渲染函数，无前端构建步骤、不依赖 CDN；覆盖书架、废案箱、文风保存、费用确认、全屏本地编辑工作台（自动增高、段首缩进）、复查并导出、写作摘要与修改说明、暗色主题与视图缓存。</div>
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
  <div class="body-text mt-2"><b>Ruff 0.17.4</b>（Linter + Formatter 二合一，覆盖 PEP 8 风格与语义规则）：规则集 E、W、F、I、B、C4、UP，ignore = ["E501"]，line-length = 88，target-version = "py311"；规则集中于 code/backend/pyproject.toml，编辑器、预提交与 CI 共用同一份配置。<br><b>扫描记录</b>：Ruff + Bandit，blocker（E9/F 级、Bandit HIGH）= <b>0</b>，见 docs/software/quality/SCAN_RECORD.md（课程示例的 p3c 对应 Python 的这套口径）。</div>
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

# 模块数、分语言行数、AI 比例

<div class="hr-line"></div>

<div class="grid grid-cols-[1.12fr_1fr] gap-4">

<div>

<div class="grid grid-cols-3 gap-2">
  <div class="card-soft px-2 py-2 text-center">
    <div class="text-[20px] font-extrabold text-[#1B3B5F] leading-none">5</div>
    <div class="text-[9.5px] mt-1" style="color:#6C7784">代码目录</div>
  </div>
  <div class="card-soft px-2 py-2 text-center">
    <div class="text-[20px] font-extrabold text-[#1B3B5F] leading-none">6</div>
    <div class="text-[9.5px] mt-1" style="color:#6C7784">Python 包</div>
  </div>
  <div class="card-soft px-2 py-2 text-center">
    <div class="text-[20px] font-extrabold text-[#1B3B5F] leading-none">191</div>
    <div class="text-[9.5px] mt-1" style="color:#6C7784">源码文件</div>
  </div>
</div>

<div class="text-[9.5px] mt-1.5 leading-[1.6]" style="color:#8A8072">目录：<b>code/core_engine</b>（105 个 .py）· <b>code/backend</b>（24，另 tools/ 3）· <b>tests</b>（43）· <b>code/frontend</b>（5 个 js/html/css）· <b>docs</b>（7 个脚本）；包：inf_backend、memory_runtime、tome_writer、tests 及两个子包。</div>

<table class="mt-2.5">
  <thead><tr><th>语言</th><th>文件</th><th>代码</th><th>注释</th><th>空行</th></tr></thead>
  <tbody>
    <tr><td>Python（.py）</td><td>179</td><td>49,611</td><td>767</td><td>4,061</td></tr>
    <tr><td>JavaScript</td><td>7</td><td>5,597</td><td>25</td><td>15</td></tr>
    <tr><td>HTML（.html）</td><td>2</td><td>2,033</td><td>0</td><td>0</td></tr>
    <tr><td>CSS（.css）</td><td>3</td><td>598</td><td>63</td><td>80</td></tr>
    <tr><td>合计</td><td>191</td><td>57,839</td><td>855</td><td>4,156</td></tr>
  </tbody>
</table>

<div class="text-[9px] mt-1.5 leading-[1.6]" style="color:#A99C88">口径：git 跟踪的 .py / .js / .mjs / .cjs / .html / .css，排除依赖与构建产物；复核脚本 docs/slides/count_lines.py。</div>

</div>

<div>

<div class="card-soft px-4 py-3">
  <div class="tag">AI Vibe Coding 与团队自写比例</div>
  <div class="text-[19px] font-extrabold mt-1 text-[#1B3B5F]">AI 起草 64%<span class="text-[13px] font-normal" style="color:#6C7784"> ／ 人工改写与自写 36%</span></div>
  <div class="text-[9.5px] mt-1.5 leading-[1.6]" style="color:#6C7784">剔除格式化 / 迁移 / 文档（8.8 万行）后，非机械性新增 67,317 行；大块功能提交 42,927 行记为 AI 起草，小步功能与修复重构记为人工。标注表 <b>ai-labels.csv</b>、脚本 <b>ai_ratio.py</b>。</div>
</div>

<img src="data:image/png;base64,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" class="mt-1.5 w-[66%] rounded-[8px] border border-[#DAD2C6]" alt="VS Code Counter Languages 输出" />

<div class="text-[9px] mt-1" style="color:#8A8072">VS Code Counter 3.8.1 输出（前 7 行；取自上游 a4a7d45 之前的运行，差 2 个文件、约 400 行；完整输出见 .VSCodeCounter/）</div>

</div>

</div>

<!-- 代码统计：模块数 + 分语言行数 + 工具截图 + AI 比例，四块对应任务书四条要求。 -->
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

<div class="card px-5 py-5 flex flex-col justify-center">
  <div class="text-[22px] font-extrabold">谢谢观看 · 欢迎提问</div>
  <div class="text-[11px] mt-3 leading-[1.9]" style="color:#6C7784">第一部分 1、2、3 三节合并完成：<br>产品设计（1.1–1.2）· 十二条设计原则（2）· 产品实现（3.1–3.7）</div>
</div>

</div>

<!-- 收尾：来源清单 + 谢谢。 -->
