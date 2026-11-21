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

# 三个部分、23 页：8 分钟讲完设计与实现

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
  <div class="flex items-baseline justify-between py-[7px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">十二条原则：四组，每组三条</div><div class="text-[11px] font-bold text-[#1B3B5F]">P9</div></div>
<div class="text-[10.5px] mt-1 leading-[1.7]" style="color:#8A8072">需求 / 信息 / 创新 · 系统 / 收敛 / 优化 · 继承 / 效益 / 时间 · 定量 / 简化 / 审核</div>
</div>

</div>

<div>

<div class="text-[12.5px] font-bold text-[#1B3B5F]">3 · 产品实现</div>
<div class="mt-1">
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.1 用户体验设计考虑的因素</div><div class="text-[11px] font-bold text-[#1B3B5F]">P10</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.2 编程语言 / IDE / 平台 / 框架</div><div class="text-[11px] font-bold text-[#1B3B5F]">P11</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.3 代码仓库链接与提交历史</div><div class="text-[11px] font-bold text-[#1B3B5F]">P12</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.4 全生命周期问题与解决方法</div><div class="text-[11px] font-bold text-[#1B3B5F]">P13</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.1 系统架构图</div><div class="text-[11px] font-bold text-[#1B3B5F]">P14</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.2 基础设施与部署形态</div><div class="text-[11px] font-bold text-[#1B3B5F]">P15</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.3 智能体技术设计（编排 / 记忆 / 护栏）</div><div class="text-[11px] font-bold text-[#1B3B5F]">P16–17</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.4 数据库设计（E-R）</div><div class="text-[11px] font-bold text-[#1B3B5F]">P18</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.5 接口设计</div><div class="text-[11px] font-bold text-[#1B3B5F]">P19</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.6 前端设计</div><div class="text-[11px] font-bold text-[#1B3B5F]">P20</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.6 软件质量（方法与工具）</div><div class="text-[11px] font-bold text-[#1B3B5F]">P21</div></div>
  <div class="flex items-baseline justify-between py-[6px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.7 代码统计</div><div class="text-[11px] font-bold text-[#1B3B5F]">P22</div></div>
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
    <thead><tr><th>语言</th><th>文件</th><th>代码</th><th>注释</th><th>空行</th></tr></thead>
    <tbody>
      <tr><td>Python（.py）</td><td>180</td><td>49,700</td><td>1,088</td><td>4,196</td></tr>
      <tr><td>JavaScript（.js）</td><td>10</td><td>6,095</td><td>29</td><td>54</td></tr>
      <tr><td>HTML（.html）</td><td>2</td><td>2,031</td><td>2</td><td>2</td></tr>
      <tr><td>CSS（.css / PostCSS）</td><td>3</td><td>619</td><td>29</td><td>82</td></tr>
      <tr><td>合计</td><td>195</td><td>58,445</td><td>1,148</td><td>4,334</td></tr>
    </tbody>
  </table>
  <div class="small mt-2 leading-[1.7]">模块（目录 / 包）：<b>code/core_engine</b>、<b>code/backend</b>、<b>code/frontend</b>、<b>tests</b>、<b>docs/slides</b> 共 5 个。<br>工具：VS Code Counter 3.8.1（useGitignore），提交 2431b7c；Markdown / YAML / JSON 等文档与配置不计入源码行数。</div>
</div>

<div>
  <div class="card-soft px-4 py-3">
    <div class="tag">AI Vibe Coding 与团队自写代码比例</div>
    <div class="body-text mt-1">按「提交作者 + 提交说明 + 是否 AI 生成」三要素归类，用 <b>git log --numstat</b> 汇总后人工抽查，得到 AI 辅助行数 / 总行数比值。</div>
  </div>
  <div class="tag mt-3">工具输出（VS Code Counter 3.8.1）</div>
  <img src="data:image/png;base64,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" class="mt-1.5 w-full rounded-[8px] border border-[#DAD2C6]" alt="VS Code Counter 输出" />
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

<div class="card px-5 py-5 flex flex-col justify-center">
  <div class="text-[22px] font-extrabold">谢谢观看 · 欢迎提问</div>
  <div class="text-[11px] mt-3 leading-[1.9]" style="color:#6C7784">第一部分 1、2、3 三节合并完成：<br>产品设计（1.1–1.2）· 十二条设计原则（2）· 产品实现（3.1–3.7）</div>
</div>

</div>

<!-- 收尾：来源清单 + 谢谢。 -->
