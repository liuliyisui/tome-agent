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
  <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA2wAAAIiCAYAAAC0SUv5AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAFiUAABYlAUlSJPAAAGCtSURBVHhe7d15fBT14f/x9+yRTZaQhJBwSBCQQwQERLAoRcWDWo8W0apovyLe9UK/BbVeFDy+FezP4tEiWrF+Fb8oWhSwFqtSEaUiyiGonEGCAiEk2ZBN9pr5/ZFrd0iAkAQm5PV8PObh7ufzmZmd2Q3uez8zn49hWZYlAAAAAIDjuOwFAAAAAABnILABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4FIENAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4FIENAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4FIENAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4FIENAAAAABzKsCzLshc2tZhpqihQqtKycpWFIopEozLNw/4yAAAAABwFXC5DXo9HKT6vWqUkKyOtldyuo6Nv6rAGtkg0pl17ilVQVGKvAgAAAIBG0zajtdplpsvrcdurmpXDFtgKikr04+7C6p601q1SlJ7qlz85SV6v56hJwAAAAAAOr5hpKhKJKlgeVvHeoEpKy6TKnreOWW3UNqO1fZVm47AEth93Fyp/T0CSlN7ar/aZ6Ur2JdmbAQAAAECDlYfC2rmnWMUlQUlSdmaaOma1sTdrFpo8sMWHtZz2bZWZnmpvAgAAAACNbk/xXuXtLJCacWhr0usQC4pKqsNa12OyCWsAAAAADpvM9FR1PSZbkpS/J9Asx9JossAWicb04+5CqbJnLS3Vb28CAAAAAE0qLdWvnPZtpcqr/yLRmL2JozVZYNu1p1imaSm9tZ+eNQAAAABHTGZ6qtJb+2WalnbtKbZXO1qTBLaYaVZ3N7bPTLdXAwAAAMBhVZVLCopKFDNNe7VjNUlgKwqUSpVD9zMaJAAAAIAjLdmXpNatUqS4vNIcNElgKy0rlySlc98aAAAAAIeoyidVeaU5aJLAVhaKSJL8yfSuAQAAAHCGqnxSlVeagyYJbJFoVJLk9XrsVQAAAABwRFTlk6q80hw0SWAzzYq5uN2uJtk8AAAAANRbVT6pyivNAYkKAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4FIENAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4FIENAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4FIENAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4FIENAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQhmVZlr2woVav3ypJ6t+ri70KAAAAQBPbsjVPs159Qxs35yaU9+zeVdf91+U6NueYhPKWpLllFXrYAMcr0ca503XP/Q/o0VdXKhCz1wMAANTYuHmrpjw+fZ+wJkkbNuXq9//zJ32f94O9Cg7VsnrYPpyorjcusJcekl/O/EbTz7KXAo3vyynDNfrl3dXP0y5/TssfPV2+hFYAAAAV/vjMC1qxco29OMEpJw/Qnb+51l7cIjg2q9SBHjbA0fK0YnlNWJOkwJz5+jShBAAAoMaadd9WPx54Yh9d8ovzdMkvztOAfidUl69cs676MZyNwAY4WrLS0m1FXXLU2VYEAAAgSeu+26hwOFL9/JJf/lyX/KJmqRIOR/Tt+k3Vz+FcLeuSyG/e1D2vfGUvrRBYp3n/+Eah6oIcnXb5T+r8Yjzo14/o8pofKYCms+N93fOb+zVnTYnU5UJNf3WaftnB3qhScLfWLl+kf8yZrzmBkXrrlXF1foarHco6AADAkf722pv65wcfS5L8KSl64ek/JNRfe9vdKi+v+MZ7/rln6teXX5xQ3xI4NqvUoWUFtv3ZOkvnnD1VG6sLLtSsjdM0IqER4GD2ezRPuFtL5h8gfB3KOgAA4IgoD4X0zw8+1vx/fKBgWZn69+2twSedqJMHnqhAyV79fcE/9fmKVdXtTz1lkG6/cWzCNqbPmKX/fLGy+vlPBg/UqAtGqnVqqlasXKMVK9do9dpv5fen6KLzztZ555whX1JSwjaau+aWVbgkEgAAAGgGXpv7jua8tUDBsjJJ0uq13+rFV97QrRMe0u8mT00Ia5L083POTHguSb88/1ylpCRXP//PFyv1u8lTddvEhzTr1Te0em3F/W/BYJnmvLVAc95qnAH7cOgIbAAAAIDDrft2g97/6BN7ca1SW/l1712/UY/j9u1B6npsjn576/Vq5ffbq2r13r/+re82bLYX4zAisAEAAAAON+vVN6of+/0puvC8s/eZ/DqzTbp+ffnFeurx36t/394JdfH69O6ppx6fpF9fNkqZbRJHNzs25xhdeN7Z8vtTqstejNs3Dj/uYavSkHvYQru19sP5ennOm/pwbZ7yC6uGLvEpLSdH/YZdohuuvVIjuu9/5qxtz4/W8Me/qSkY9ZxynzhdkhT45k09/fgszVu9SfkBVW77BI246jeacPXp6rz/TR+S0KaP9fKLszRn6VptzCupqWiTo75DLtTVv7lKo07Mqns+sFhIG5e/qXkvz9ec1ZuUv6NmG74OOerR/yC2of3dZxXStn/P1hNPv6j31uxWKCbJ11p9f36nHr7/Sg1qE7+RmnM4Z/kmBUKS3K2V3b2vRt3+sCb8PKfO11Dn+xIr0dq//0WPvjhXn66vPLa07jrtkvF6fMK5tvek9teafcIZuv3eh3T14NbxjRPUuX/Vcm726wTd/8FbumHTIaxT659ySPlrFuhvf5mrOcu/qfncp2WpR/8zdPm4cbr6p93lc9vXq2R/7dXva4m+fHWKHvzjAq0NSOpys976YLwGxa+rkPLXfKx5/zdbc/69Vhttn63OPX6iy68cp6tHdq/zfQUAoLn4avVaTXtqZvXz228cq1NPqfg/4+49hdqVX6A2GWnq2L5d3FoH78cdu1RYHFD77Cy1zcyQJH2y7Av9+YX/rW5zz503J0wL0Jw1t6xCD1uDhLTtHw/rnEHDdcHtUzXnk01xYa2iPpC3SZ/OmapxPxuoITfO0peBuOqDESvRR1MuVP+LHtDzn1SFNVVue6XefvwmDR80Rk+sjAtUDbXjfd1z/kAd/7Ob9OicZYlhTZIK87R20Qzdc/Hjdc4HFvhilsadMVDn/PphPbNoZUJYk6TQjqptDNfx5z+s93YkVB9YbLfevuscDb9uqt5eWRmAJClUorXzHtbooRfqoWVV+yzRp3HnMFD1FsVKlL9+mZ6//VwNue5NbazaxsEIrNQTVw3XBffOqglrkhTYpE9n3aHhZ96kOVUj5cY2ac51tb/W/JUL9NAVp2j4lGWq70fjiCr8WI+e/xMNufiBivc3/nMf2K2Nn7ypR6+7UMefMVFv1+u9LdFHE87X6EmVYU2StuapOL5J9b7vqPh81vLZ2vjJm3r06Y+1K6EGAIDmadXXNT/cdmifXR3WJCkrs436HN+j1rC2YVOu5r/3gZ5+7iU9/dxLmv/eB9q4uSKsxOvYoZ36HN+jOqxJ0k+HDla77LbVz9dU3tuGw4/AdshK9NH952j47bO1MT6j7Uf+h1M1+mcT9dFBfzPP10f3nK9xLx9gjozQSj1z+Vg9f4BmByOw7GENP+MOzVl/kAdVi42zxqj/FVP10cF+UV8/WzefMboerz9f791zscbPT5xQOkFsk14ee7/eDkhfTjlfVx7gHAb+/YBufjHPXly72Do9P3aMnvliP+co/2Pdc+N0rY3t1pyxF+qef+/ntUra9vIdevDD/WzPSTbN0uif3qTnD+YzsmOBxl988J/5/Pn3a9y8/ZyrwMcaf/5B7hsAgKOEaZrVj4sDJcr9fv/fWcrKyvXsC/+rSf/zpF6b+44+W/6VPlv+lV6b+44eeuz/aeZLr1UP7V+X3O/zFCjZW/280S/Jw0EjsB2ijc+P1bg5ti+WXYbqhslPafa7S7T8swWa/cTdunxoVmKb/AUaN3aWtiWW1m7pnzR+3m7JnaVB4x7UjFcWaPln72vhXx/UDfbtxr7Ro5PeVH5iaf1smqUxY2drm62nKXvoJbr/iee0cPESLX93lmZMHqdBdcwDFvhwokY/WjNUrCQp7QT98p5pmvX396tf/20juye2iX2jR3/9gD4KJhbX6ptZenTebil7oG6YPEv/qtzm5b1sF7/F3tcTN47RNS9XvE+dL7pbs96tOIbpt52ubNulehv/MkufHkwv2/zpenSNpO4X6v6n39KSzxZo9hM3a4T9nGydobuvulH3LJOkLA0a94gWLl6iJX9/TlOush2/SvT2zEN4/4Y9pOWfLalYnjg3sa7XzXqrqu6zJVr+2d90dc4hrlMl8LHG/3qqvoz7Nz77rLs1+5OVyt34jXI3rtTqd5/S5fGHl79A4+5dcBA9iF9p5p/etxcm+PSPE/R2/EnqcLpu++sCrV77TcX+v1up1Z8t0OzJ43RaU1wnDAA4YooDJVq67AvNf+8Dfbnqa0UiNZNDH8im3O+16MMlWvThEm3ZelDfwiRJkUhEK1Z+rfnvfaCl/1mh4kAjXtFUD4MG9Kt+XFZWroenPV1rT5kklZeHdO/kqVq67At7VbXFnyzTvZMfrzO0rd+4WVOmPpVQf8qgAQltcPhwD1uV+tzDtmO2Rv/0YX0ZV9T56ue08P7TlVbL/Tr58+/Q2Xe9H/eFtbV+OXOJpp+V+IVyn3uVJCn7XE3/+1O1TJQc0sYZY3TOE/Htc3Tb39/XhBPjig5anp6/6Fw9Gr8530Dd9upMTRhYy/1VsRJ9+fR8ld95pU6rLlumh4aM08tx38zTznhQb/35SvWo5btzYOV0jbl8htbGhaQe97yvf90QnxBquddJkrIv1Kx/TtOItLiy2CY9f+mFFWHKpu89C7TwhsSQFFg0UUNuWZAwWXpt56/W9+XEu/WvuePUI/79Dnys8T+7KTFQSJKy9MuZ72r6WYnnceOM0bb371xNX/2UfmkbtGmf/cffwxbPfp4OZk61eq7z5ZThGl0ZgFXHeZUqAvgTI0frmer/l+Totvnva0L8pe/2fVfpcLruf+JRXT00S75YSGv/b4FCV12iQfpGT5w5Ws9U/6hY+/sFADj6fP3Nej32x2cTyjLS0zR18r1KTW2VUG73/N/+Tx8t+Syh7KzTT9P1V1+eUGZXsrdU90z6g4qKE39yfGDCberTu2dC2eHw5J9f1PIva4bt9/mSNHXy75SdlZnQbsas2fp46X+qnx/X9Vj17N5Vlmlpw+Yt2rK1pnfuzOFDdePYMdXPJWnnrt26d/LjCoXC1WXDhg7Wrdf/V0K75qy5ZRV62A7B2ldmJYQ1DX1Ebz1Ue1iTpOyLpmn6qPgv6yV6e+77cUGhLlm6+unawpok+dTj5pmaMji+LE9z/mkLFgdr2SwlZAf3Cbr/nddqD2uqGLBjUHxYkxR6d3ZCWFP2lXppZu1hTZLSBo7XjIRv8NLGV9/U2oSS2p330COJYU2S3N11wz1X7jvIxAl3a0YtoSJt5LVKzIZ5Wpt74HdFytFtj9nCmiSlna4HbhtoK5R8ox7VVFtYk6QeV19r+0HgG23Y/5WbR1bwfc18Na5XucvNml7LeZUqPj9jbxwaV5Cn9z7Z/+UbUmUQf/c53TC0ciAat099r7qkcsCRkAIH7qYDAByF5i34p71IRcUB/evfS+3FCfJ379knrEnShx9/qj2FRfbiBIs+XLJPWJOkee/u/2qQpnLXLdfq5IE1PW2hUFjzFi5KaFNUHEgIa7+59td65IHfauyYS3TNVZfq0Qcn6vqrr6iuX7xkmQIlib2Gc9/5R0JYGzKo/1EV1pojAlu9faN/LIj/4tlaV992ibLjSvbl04ixVyW2+WBZnQN2VDvhWt2QEMjssvTzi+O/FEv5K9fV/7I6SV8ump8QIH1X3K26vovXLqT3/pH4D9ig236jQfZQY9P5Kltoyfu3Pj3Q93r3hbp85D6xrEL/kxJCpCSNuPHKOnqMTlC/kxJLtu04iLN3wpW6vI5BkrL7D7V9FnJ0w9jT9w2RkuQ/QSf3ii/I07aD2P2REvpgvt6L7w294hL1iG9gk939uITj3rjuwD8mjLjvoX2DeLUc9e0T/zxPz0x4QO9tOpiQDQBozrbUcc9WfG9Rbb7P+8FeVO1A94F9n7fdXiRJyq3HJZWN7be33aB+J9R8edi4JfGyyLXfrK9+nJ3VVsNPG5JQL0lnnX5qwuAia7/ZkFC/YdOW6scD+p2gu265LqEehx+Brb5iedqW8Pd9hmr5W9jXiSfprPjwElunjbVfelzNN+SkOoJGjew+AxMDQnFA5fHPD0qeViyP/3UlRzdcmhgEDyxP23Ljn3fXWfb77GrjH6jTEi5p+0Zf1/xbU7teffbt3ariT1Pi9/3uOrlPrXFJktSuzb49Xwd0fPe635e0NCXOZjJQ/RJCRrx0ZSdexeBoG79LDFwbHz9XXXucUPdyxezEXuSNeQe4d/NCXX7+/t6PLI264ZLE93fTm7r5ZwPV9exxuuf5j7XxYO6BBAA0Oy6Dr6xVTji+5ufS8vLEb31rv60JX106J87RFq/rsTWXGK1Z911CXTRa8+ts7171+vUeTYRPf33l5SVespeTo851hYcEx6lHQm/KgXXueBCBZ5+AcCg2K260WEk56lzrZZj7s10bEoLWcercMf55XXLUo0n/LUiSz2Mvq5Hd0Xa/XBOocx4yZaldvc/zkbNrx/5/iWywE/qob53nqoLvjEf01qP7Dhijrcs05/GbdE7/gTpnwmx9WWirBwA0a9261v5TaY9ux9qLEnQ5tpO9qFrXY2vfZpVuXWqv797NOfc92UeiCIcPbiCW+PX2u06jj3SBQ0Fgayi/r/bL3Zq1LKU3uOfHJ9/Rd2IQr02OsnPqsbRrnA9Ej8uf0yefzNKUUbUl/ZA2zntYo4cO1z2LjsxIXgCAxjf2itHKSE+8hqZX92666OfnJJTZZWW20a8vv9herLFjLlFmm/3/5H3+uSPU47iuCWXpaa31X1fsu73D6bsNm6sf+5K8CXXxAfVgLwe1h2Gvp+aX7m8dfXN9y0Fgqy9/mhKmJVy/6SAnXN6sjQk9UOlKs40GeEi+Wxc3sqWk9DQlxz8/SMkJPRbfaGPC5Y0HI02J/44e7DbytDHh34LWtu3AKdLTEi9X7HvLLC1f/P7BL3+t617C+vNlD9XVTyxQ7uolWviHcTqtu+1SythuzbllrJ7h/zMAcFTodEwHTZ3yOz0w8XY9MPF2PXT3Hfr97+60N6vV+eeeqWlx6057+D797OxaRlu2SUryasp9d+nByvUemHi7nnjkPh3Tob296WEz7amZWh03gXXP7t0S6rt0rglsu/IL9Mrr8xLqJeml2XMTBlyJX0eSjosLcKu+/kZ/fOaFhHocfgS2+srurh4JgeLf+nR5/PM6fPNV4hxfacep5/5HKjmoQRq+XPbvhOe+Xt0PMABKbfpoUMJ9eJv04bL9TF5cK/uAEAe5jeA3WrEuvqCv+jrnSgPE6Xx834Tna9fW/MJ3xPiz1PfSuzX7n59r9f/drdMSPvzf6IkXP44vAAA0Y6mt/OpzfA/1Ob5Hve+t6nRMh+p1O3WsX+A6oXK9Psf3UCt/Y/zafmie/POL+mp1zY05Pl+SLr7wZwlt+vftrd49a87Nu4s+0r2/f1x/e+1NvfjKG7rn949r0YdLquv7HN8jYRATSbr0l+fL50uqfr5i5RpNnzEroQ0OLwJbvQ3UiLPin5fo5ZcPPCnwp//3asKAC76Lzq0cqnw/3p2vt/e34cACPf1q4mVf5/1032HlDyxLJw9OvJfry2ce10f72/c+snTaGYlDJ3754qsJc6zVJv/vLyaMPKjB5+qs+idOHAbZ/Qcm9pDNn7v/z+dhljZ4nGZPvjCxcPWmAwx0AgCA861csy5hDraUlGTd/9vb9pmDTZLuvOVaZWe1rX7+fd4P+ucHH+tfiz/RtrjLJLOz2urO31xb/bxKxw7t9Lv/vkXJyTW3Mvzni5VaFzegCQ4vAtshGDH25sQvrosmaswTK+sMbfnz79DNCcEqRzdccRCjMMbe1/ixs2q/5DK2W2/f/7g+iq/LvlJjz4h7Xg89rrhZp8VfFpm/QOPGTq978IZYib780+yEqQk6X36tRsRvY+sMjblzgfJre/2VE2dfM2VlQtl5Yw80RQLq1KV74jD733ylLw80amJ91jnhEl0dn8lj72v82On6sq4PviQppPwPp2r8y40xYMnHevSuN7WtPqP4H+IlwgAAOMnyL1dXP05JSdZDd9+hHsfVfklSWutU/WHS3frp0Lrnhjp92E/0h0l31znpeK/u3fTQ3XckhLYvVq5JaIPDh8B2KE68WVMuTxzBce2MMep/9jg9+urHWpu3W/n5eVr779l69NfDNeSu9xPCXOebn5Jtvui6rZmqc84Yp0fnfqNt+ZXb/cd0jTtjuMb/I/GSwxH33XnAec/q1OESTbG/qDUzNHrocI2+f5be/nfl/tcv09vPP6DRZ5yi0c98lThse9qFmnJv4jYC/5ioIUNGa/zzC/Tp+t3Kz9+tjcsW6PkJF6r/pTMSe+BGTtPUnzfOwBQtks8+AM77Gn/pw5qzJk/5ed/ovT9N1Rz7VBL1WidHV0+wDau/ZoZGn3phwvubn79b+Xnf6KNXp+rKs3+iITfO0tr6hKz92DX/AQ0fdKHGP/++1uaVVH/+QoHd2vjv6bpy0oKE9p0H9+EHAABAs+dy1XxlT2udus99Z3YpKcm65fr/0u9/d6fGXHKRTh1ykk49ZZDGXPoLTbnvv3XzuCuVkrL/nzS7HpujtNap1c/jXwMOL878IfFpxJSX9PgZtmH3ty7T85Nu0gVnDteQU8/VBdc9rOdt93GljXpKC+86yLR2xoX6ZbakHcv0/L2jNfzUyu3ePkMf7UhsmjbqOU2/aH9zWB1Yjxv+plm2IKrYbn05Z6rGX1e5//PHafzjb+pL2/6rdB73N82+2nZdeeAbvf34RF15/nANOXW4zvn1RD06zzYaxInj9a8nL7TNoYZ6yblIl9t/TFs/W/dcfK6GnDlaNz+zbN9e4Hqu4zvjEb11j+3zG9qU8P4OOXW4hpw5WuMmzdKnWxspqcULbdLbj9+hC848RcdXzvl2/KDhOue6Gfo0fuLxXjdrxu0H+bcGAICDDRpQcx/5zl279ennK6qf795TqHXfbdSPO3dVl1WpGknz9puu0e03jtVF551da8/cjzt2ad13G1Wwp2YwkiWfLdeu/ILq5yf2Ob76MQ4vAtuhcnfX5TPf1Vu3HeQ9Y+4sjbjnNX3yxLlKO9hesDYXaforj9gGUrDzqce45/TJ46c3QthprRGP/kv/mlzLPFe18aXVMqVBa5320Jta8ocLD24b8qnHVU9p+dyb1WPfjaFesnT1o3cfcC6zRPVfp8cNb2n5kwf7/kpKO0EjTtrvh7jRZZ91t976v/H1Oi4AAJzqpP591bFDzTjlL77yhmbPfUf3/v5x3XH37/XItKf12/sf1R13/17vvr9Y5eUH/sG0rKxc776/WLdNfEi/feBRPTLtad1+9yT9bvJUzZ77jma9+kZ125xjOmhAP34EPVIIbA3hbq1Bd76m3NULNOueS3RarxylxYeOtCxlDzxXt02epSWrl2jWDQPrH6q6X6LZi9/XjNvOVd82cRtv012nXX63Zn3wH/3r/tMPPgQekE89rnpOy1e/r9mTb9aIgXUc0x/e0vIvH9RpcVU1fOp86TQtX71EC/9QsY3s+AP3tVZ2r6G6/J6ntHD5Sv1r8rkH/+Uf+9d9nBYue01TRg1UdvznJS1LfUddVXv4P4R1si+apuWr39ese8bt+xlxt1Z2TneddtHNmvLKAn23/C3dP7gx0vjpmvrZW5pR+beW8Jlyt1Z2zkCNGHe3Zv1zpZbPHKdB9f5jAwDAua799a+qHweDZVrw3gf7zLW2e0+hXpnzd91xz++1ck3CMNwJvlz1te64Z7JemfN37SksTqjbum27Frz3QULou+6/Lk9og8PLsCz7HOkNt3p9xU0v/Xvt2+WKum17frSGPx43lP+o55T7xIHnCQEAAMDRb87fF+jthe/bi+v08P3/re7dEr+Pf7t+k6ZMfSqhbH9GX3SeLv3lz+3FzVpzyyr0sAEAAADNwOUXX6gbxl6hnt27KrNNhgYN6Kdrf/0rPTNtin5/73h1zjkmof0/3k+cr1eS/vlB4hylXTp30u9/d6eemTZF11x5qQYN6KfMNhnq3bO7fnPtr4+6sNYc0cPmIPSwAQAAoCFefu0tvfdBRVDzp6Tohaf/kFB/3e33qKysXJJ03jln6OorRifUtwTNLavQwwYAAAAcJQafdGL142BZmbZs3Vb9fOPmrdVhTZJOGTSg+jGci8AGAAAAHCX69O4pr9db/fyNee/qzXf+Ub1U8SUlqXcv21RMcCQCGwAAAHAUGXJS/+rHK9es05vvvKc333lPq76uufVmyKCaNnA2AhsAAABwFLns4gvk8yXZi6slJ/t0+eiL7MVwKAIbAAAAcBRpl91WUyffqzOHD7VX6Zwzf6qpU36ntpkZ9io4FKNEAgAAAGgxmltWoYcNAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4FIENAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4FIENAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4FIENAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4FIENAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4FIENAAAAAByKwAYAAAAADkVgAwAAAACHIrABAAAAgEMR2AAAAADAoQhsAAAAAOBQBDYAAAAAcCgCGwAAAAA4lGFZlmUvbKjV67dKkvr36mKvwuEWXKKpd8zVSnt5vAFXa/btJ9tLpW0f6dFp87Q2KEle+dNTlFQeUFGoojr71Jv0P9f1kd+2GgAAAOBUzS2rENiOdtsXauKkRdruO1n3P3u1+trr62Lm6tV7ntTCQsnf51L9z+3Dle2VpIjyP5ip3722XkF5NWTcw7prWIp9bQAAAMCRmltW4ZLIliK9rTLsZftRtOgNLSyU1G6EJt9ZFdYkyavss2/VA2emSYpo+byFyk1cFQAAAEAjIbAd7bbnabsq3ukke12ddmrxx3mSpIHn/UydavmUdB09UgMlqXCVPt9srwUAAADQGGr5Ko6jUvsOyraX1aVwnb7aJUm9dMrgOi539PdS3w6SFNDa9QF7LQAAAIBGQGA7yhXtOYQwtWmLNkhSVif1rHNEkfbqdEzFo+3bK3rjAAAAADQuAttRrjRYVvFg1cu68vrxFctv7tUtk57TvM93KmJfQVLR7oKKB1lt1c5eGSe7Q1tJUrBqHwAAAAAaFYHtaGdW/tebooz0FFUM9Fimou3r9PrMx3T9pLnasDdxleqQ5/NXtD+Q4oCK7GUAAAAAGozAdpTrdOlDmv3CdM3+yx/05z/+QX97YbpmPztRd53dVRkuKbJ9iSbNWKKgfcX6CAZVai8DAAAA0GDMw9aCBT9/TnfMXKeg0jTqvod12XEV5dvfmqKJ7xbUPaF2pep2vS/V3yYMP7jeuCZWVBJUUcDWZWiTkZaqjNa135y3Y3eRykNhe3GCDlkZSvbVPuZm7vZd9qJ9dO1U+4Wm5aGwduzef19lsi9JHbJqn6CBY2+Zx14YKFVxyf5/Mjlaj70lv+8cO8deF46dY7c7ksfuVM0tq9DD1oL5TxmlC9tJUkArV++0Vx+8g710EgAAAEC90MPWwi1/eryeXCV1Ov8+TRvdvqJw6XO6ctY6qd1ITXvsAnWyr1Rp7V8n6NHPIup03kRNuzTHXn1ERGOmotGovTiBx+ORx137bxXhSESmuf8/iaQkr1yGYS+WKn9FO5C6fsEyLUvhcG3DwNRwuQwleWuPxxw7x14Xjp1jt+PYOfa6cOwcu11Djt2pmltWIbC1cLUGtm3zNHHyR9ru6qO7ZtykIbX+/Qe06JEH9VKuNOzG6br1FHs9AAAA4DzNLavU+lUcLUWutnxf8Sg7M62muHMv9fVJMjfoqzU1xQmCq7QyV5Krlwb2s1cCAAAAaAwEthYsuHih5hVWhK5hp6TE1fTRmT9NkxTR4vkf1Tpk//Z3P9JKSf7BIzSs9ntcAQAAADQQge2otkqvTn5Ni78tSJwgO1KgtW89qTteWS9J6nr+pfuErq4XjdRAl6TceZr01xUqqt5ARPkfPKtJ7xVIrhxdNrpP4ooAAAAAGg33sB3VVujZ61/WUkmSV/70FCXFylS0typ9edX17Bv1wJheqq2TLLjqZf3u2RXKN1W9voIBBSOSXGkaeet9umZAfM8cAAAA4GzNLasQ2I5qZdqw4DW98sl65e4pU8SsKPX626prn5N14aiRGtKh9hGJqu1apddffluLNhVUBDVfirr2PktXXT1SfdPtjQEAAABna25ZhcAGAAAAoMVoblmFe9gAAAAAwKEIbAAAAADgUAQ2AAAAAHAoAhsAAAAAOBSBDQAAAAAcisAGAAAAAA5FYAMAAAAAhyKwAQAAAIBDEdgAAAAAwKEIbAAAAADgUAQ2AAAAAHAoAhsAAAAAOBSBDQAAAAAcisAGAAAAAA5FYAMAAAAAhyKwAQAAAIBDEdgAAAAAwKEIbAAAAADgUAQ2AAAAAHAoAhsAAAAAOBSBDQAAAAAcisAGAAAAAA5FYAMAAAAAhyKwAQAAAIBDEdgAAAAAwKEIbAAAAADgUAQ2AAAAAHAoAhsAAAAAOBSBDQAAAAAcisAGAAAAAA5FYAMAAAAAhyKwAQAAAIBDEdgAAAAAwKEIbAAAAADgUAQ2AAAAAHAoAhsAAAAAOBSBDQAAAAAcisAGAAAAAA5FYDsMijYv0eszXtTMGS/q9Y93KmJvAAAAAAC1ILA1grV/naArrx+vSQsK7FXaPu8xjX9sruZ9sUqLv1ileS8/pt88vUJBe0MAAAAAsCGwNVie1m6ISOqlEWe1Taza/ZFmvlvRo5bReaiuGj1UPVOl4KqX9czHZYltAQAAAMCGwNZgO5W/W1JWJ/X0J9bkvv+hNpiS/8QxemLSGF1w/hhNfuAC9ZS08vMvuDQSAAAAwH4R2BqLy5v43FynRZ8EJLXVhZcOVXWWy+qjvlmStmzR+sQ1AAAAACABga3B2is7S1JxgYrMmtLIJx9pcUhS56E6s1N8e6+SXJJCZdzHBgAAAGC/CGwNlqNTBqRJoRV69a1cRUwpsnuZZs6t6D8bOGK4MhLal6k0lFAAAAAAALUisDWCrheN1ECXlPvekxp743iNvfc1LQ1K6jBSV52ekti4cIvWF0vqkKOuiTUAAAAAkIDA1hhSh+uuey9Q39SaIm+7obr/3guUcDWkpKKlX2iDpIzefZVtqwMAAACAeIZlWZa9sKFWr98qSerfq4u96qgXKQ6o1J2ijFTbICSVInsDKo1ISalp8tfeBAAAAEATaW5ZhR62RuZNT6szrEmSNzVNGW0IawAAAAAOjMDWYLlaNONFzZyzSkX2qlrt1NKXX9TMeeuYhw0AAADAfhHYGqxAG75YpcWr8lRqr6pD/rertPj9L5iHDQAAAMB+EdgOu8ph/ZmHDQAAAMABENjqLaJgYUBF1UuwomfNLLOV77vkf7tKC//8Vy0slpTellEiAQAAAOwXo0TWW0CLHnlQL+Xay+un56UPafJ5be3FAAAAAJpQc8sq9LDVW5pOGZxjLzw43hRldOqlUVffpwcIawAAAAAOgB62BluhZ69/WUvbjdS0x/adKBsAAACAczS3rEIPGwAAAAA4FD1sDRZRsLBMYVeKMtKZDRsAAABwsuaWVehhazCv/G3SCGsAAAAAGh09bPVRnKuVXxcro98AdU2vKqzsYUtseRC8atUmRcQ8AAAA4PBpblmFwHbQ1uulO57VoqAk/1BNfmqMeko1g47Ymx9QH931wk0aYi8GAAAA0GSaW1bhksiDliS/r/Khz0vPGAAAAIAmRw9bfYTytPaLgDIG91GnqvAGAAAAoNloblmFHrb68OWo7zDCGgAAAIDDg8AGAAAAAA5FYAMAAAAAh+IetkYU2bZOiz5Zpu3bd2jlj2X2aps+uvGPYzTQXozDZumWtfo092t7cYNMHHG5vQgAAAAO0tyyCoGtMZh5WjTtGb204UAhLR7D+h9pS7es1eiXJtmLG2Tn5Ln2IgAAADhIc8sqBLZGsP2tKZr4boEkyduhl4b17am+x6bZm9lkqu+wXsqwF+OwIbABAAC0PM0tqxDYGixXr/72SS0s9mrgmN/p7rPb2hvAoQhsAAAALU9zyyoMOtJgBSoqlpQ+VJcR1gAAAAA0IgJbg6WolU+SL0VeexUAAAAANACBrcG6qWd3SbtzlRu01wEAAADAoeMetsawbaHue3iRdnW9QA9MHKmudLU1C83hHraLZzXu6zutax+mHgAAAC1ac8sqBLZGElz1mibNWKbtrvYacvZwjRw0QJ3S7a3iedWqDZdRHknNJbB9mrvWXnzIJpz5KwIbAABo0ZpbViGwNZZdy/TSs/O0aPvBzsXGPGxHGoENAACg5WluWYV72BrDtoW674HX6hHWAAAAAODA6GFrsDIt/X/36tl1klK76rJxV+uCE9vKSxR2PHrYAAAAWp7mllWIFQ22Xiu/laQcXfXAXRo1gLAGAAAAoHEQLRosKpmS2vXRwCx7HQAAAAAcOgJbg/VUz66SzIi9AgAAAAAahHvYGkHkixf1mxlbNOKeh3VVT3vtkVe0eYnmzf5In2wvUDAiSV75s9rrp+f+SqNGdFVGHbF9+1tTNPHdAntxnLa6bPJDGtXJXt48cA8bAABAy9PcskodX9VRH97B/6UHzk/Rov83RTM/3inn9LUVaOn0e3XLY3O1KLdAQaUoIz1Nfm9Ewd15WvTakxo/eaG2m/b1KkQq0h0AAACAI4QetgZbpZd+O1efSwoHAxU9WN4UZfgPNCV2H934xzEaaC9uVCv07PUv6/N2A3TjjWN0SteaibqL1szV1KeXKNeU/KfepBeu62NbV1r+9Hg9uUrqeenDmnxemr262aOHDQAAoOVpblmFHrYGi6q0OKCi4sqwJkmRMhVVlu1vafr+K4+6nnmr/vLYtRoWF9YkKePES/XAlb0kScH/LNHyOnrZJKld5tEX1gAAAIDmgB62BivQhqUbtMtefECZ6juslzLsxYeTuUxP3vialtd6L9pOzbvvMb2+Sxp283TdOji+7uhADxsAAEDL09yyCj1sDdZWPYcN1bB6L0c4rEmSy6ske9k+2qpTR3sZAAAAgMOBwNaSFQYqewbbKqONvbJARcX2MgAAAACHE4GtBSta+oU2SFLnnhrot9eWqTQkSQV6fdJ4XXl9xTL2zimaNGuJcglzAAAAQJPjHrbGFClT7rpV2r49T2u/D9hrbbpp5M0j1NVefLhsW6j7Hl6kXDNFw26epFsHpyTWV9/fJnlT09QqElBRKK7elaIhV07UXWe2jSs88opKgioK7LUXJ8hIS1VGa3+T3MP2nxv/bC/aR9dO7exFkqTyUFg7dhcllP1m/pP68scNCWUNcdtpo/Tgz35tL5Yk7dhdpPJQ2F6coENWhpJ9tV9Im7v9wHdy1ufY7ZJ9SeqQVfuFxPV532vTnI+9MFCq4pJSe3GCo/XYW/L7zrFz7HXh2Dl2uyN57E7V3LIKPWyNokwb3npSt9x6r+57+jU9+9YSLf5i1QGW9cq3b+Zw2bVEU6ctUq4pdT3/tn3DmiS5huquF6Zr9gvT9bc/Paw/Pztds194Qn+ecKnObOeVzDItf+VPerXxsgQAAAAAG3rYGkFw8bO6/pX1FU+8Kcpo11kDO9YSghIcmR62oi9e1qSZK5RvetX17Bv1wJheqv33mP0w8zTvoWl6fYekPmP0t/8emjBlwJEUjZmKRqP24gQej0cet6tJeti23jfbXrSPun7BMi1L4XDiZA+Xv/Kwln3/TUJZQ/z3GZfqnrOusBdLksKRiExz//8cJCV55TIMe7FU+QvigdTn2O1cLkNJ3to/afV532vDsXPsdeHYOXY7jn3/OPZ9teRjd6rmllUIbA1WM/x99qnXavK4Acqo/e/lyDIDWjlrmqZ+FpC8bTXyujt1zeAGzK/2+XO6cuY6yTVAd8+8toknAG8aTRHYGNYfAADA2ZpbVnFitGhm8rR9lyTfybrRqWFt73q9PnmKpn4WkLfTcN3/h4caFtYkqVOOOkmSGTkME4ADAAAALZMT40Uz46k4i+ltHRrWVujZ+57VvO1S17Nv1V8mX6q+6fZGAAAAAJzIiRGjmemmnsdKKi5QkWmvO9IKtOhPL2tpUOp6/p167FDuV6tDZFOutqsiqGbbKwEAAAA0CgJbg6VpxHkD5A+t0Kuz1ytorz6SVi3U67mSOl+gu0fn2GsPnZmr1+dXDLKSPXjwYR84BQAAAGgpCGyNwDv4Wk2+sL22L35Wd0x6TYu/3amgA27sWvvFagUldTpxgGqf2aNu2xc8pyffWqHt8XOvSYpsW6Zn73lSCwsl+Qdo3C+JawAAAEBTYZTIxhLZqaXPP6NnvzzQhNlV+uiuF27SEHtxI1r+9Hg9ucpeWpfE17P9rSma+G5BxRNfijKSvQoHAzVBNLWPbrzvJp3ZvOZJTMAokQAAAC1Pc8sq9LA1hr0r9OzEx+oR1pyv009HalTv9srwe6VQmYqKAwrGvMro1EujxtylP/+/5h3WAAAAgOaAHrZGsHbmBD36eURypajviFG6bEQfZfvsrey8atUmxTETTrdE9LABAAC0PM0tq9DD1mDrtHxVRFKaLpj4B90/Zqh6dkhTRpsDLYQ1AAAAAPtHYGuwMpWGJGWdrDN72usAAAAA4NAR2BosR53aSXLRXwYAAACgcRHYGqy9zjw9R9q1Tit32+sAAAAA4NAR2BpBxnnX6tY+BXr18Re1dIcDJmADAAAAcFRglMgGy9WiGR8qVxHlrlun3KBX/k7ddErHFHtDm24aefMIMe30kcMokQAAAC1Pc8sq9LA1WIE2fLFKi79Yp9ygJEUU3L5ei79YdYBlvfLtmwIAAACAOAS2BmurnoMH6Mx6L72Ubd8UAAAAAMThkki0WFwSCQAA0PI0t6xCDxsAAAAAOBSBDQAAAAAcisDWyCLbVmjerGd1328f1C1Vy73TNPOtZcottrcGAAAAgLoR2BqLmadFj9+rsZNf1utL1yu3OKCiqmV3nha/+5ru++0E3ffaegXt6wIAAABALQhsjWKnFj40TS9tKJPkVXbXobpq3BjdPeE+TZ9wrW4dd4FG9W4rryLK/eBZTZi1zr4BAAAAANgHga0RRD6eq1d3SPL30o2P/I+mPzBGFwwbqoG92yu79wANGzZSl014SC88cqkG+qWipS/rpTX2rQAAAABAIgJbgwX00cfrJXl15nW36swOXnuDat4Ow3X3dSfLrzItWrzCXg0AAAAACQhsDbZFG76X5OuvYQPsdbUYMFg/9UnK3aJcex0AAAAAxCGwNVhUMiWlt1WGvapWbZWRLqm4QPn2KgAAAACIQ2BrME/FWTQj9oo6RBQ27WUAAAAAsC8CW4N1U89jJe3eoJW77XW12L1Oa3dL6pCjrvY6AAAAAIhDYGuwNJ0yMEdSnl6dsUj5++s9MwNa/NJCbZCU3bevsu31AAAAABCHwNYIMs6/QCP9knIXasIDL2rptn0vj4xsW6aZD0zRzG8l+fvo1xfRvwYAAABg/whsjcHVR9dMHKW+fimya5WenTxBV944Qbf89kHd8tsHdf1vxmvs5Ne0eFdEcrXXZRNv0pBU+0YAAAAAIBGBrbF0HqH7/3ifbh3cXt7KQUiKigMqKg4oGJEkr7J7j9T90+7TqM72lQEAAABgX4ZlWZa9sKFWr98qSerfq4u9qmUwIwoW79H2TVu0K5Sidt27qVPbNPnrnlMbR8DSLWs1+qVJ9uIG2Tl5rr2oQS6eNUmf5q61Fx+yCWf+ShNHXG4vBgAAaDGaW1ahh60puLzyt2mvnoOHatiwAerZgbAGAAAAoP4IbPUVKVNRYUBFhWXad2iRA4koWBhQUWFAkf2NJgkAAAAABLb6y53zmG6Z+KBumbXKXnUQovpq1oO6ZeKDevKTMnslAAAAACQgsNXLTq39NiBJGjhogOp/lWOKThnUS5K08uv19koAAAAASEBgq5cC5RdKUlv16plirzwo3p5d1UmS8vK03V4JAAAAAHEIbPVSptKQJLVXp072uoPUqYO6StLuncq31wEAAABAHALbkWJGDmHQEgAAAAAtCYGtXjyVZyyq0qC9DgAAAAAaFxNn10tAix55UC/lejVy/BO65kR7/UHYNk8TJ3+k7enD9dgfL624PBJHBBNnN1xzOIcAAADxmltWoYetXtLUq3uapIg++WydvfKgFK3aUDHYSMf2FYOPAAAAAEAdCGz11PXc4eopKfj5XL2+zV57AMFVenVRniSpZ79DmRYAAAAAQEtCYKuvrJG67NQUSQWaN+05LS+2N6iDWaDFM17T0qAkXx9deHqavQUAAAAAJCCwHYK+467WyFRJwXV68t4pmvnxzv2O+BjZsUwzH/gfzVxXJilFw8ZerSF+eysAAAAASERgOxSuPrrmkas1LFVSpECLX35MY299UJOmz9XCpcu0tHJZ+NqLmvrABI194DUt3hWR5FXXC2/Tracc2qTbAAAAAFoWAtuhSj1Zt067T7cObltxL1oooA1rlujVWa/p2crl1Q9WaeWOyr43X45GjX9Ij43KsW0IAAAAAGpHYGsIb3sNu/kh/e3Zibrr/KEa2ClNGf6qoUS88qenqWvvobrsxon629MTddmJ3LcGAAAA4OAR2BqDL0dDRo/R3ZMf1p+fekKzX5iu2S88oRf++LAemzBGo07JkZczDQAAAKCeiBEAAAAA4FAENgAAAABwKAIbAAAAADgUgQ0AAAAAHIrABgAAAAAORWADAAAAAIcisAEAAACAQxHYAAAAAMChCGwAAAAA4FAENgAAAABwKAIbAAAAADgUgQ0AAAAAHIrABgAAAAAORWADAAAAAIcisAEAAACAQxHYAAAAAMChCGwAAAAA4FAENgAAAABwKAIbAAAAADgUgQ0AAAAAHIrABgAAAAAORWADAAAAAIcisAEAAACAQxHYAAAAAMChCGwAAAAA4FAENgAAAABwKAIbAAAAADiUYVmWZS9sqNXrt0qS+vfqYq8CHGPplrUa/dIke3GD7Jw8117UIBfPmqRPc9faiw/ZhDN/pYkjLrcXHzLOIQAAaG6aW1ahhw0AAAAAHIrABgAAAAAORWADAAAAAIcisAEAAACAQxHYAAAAAMChCGwAAAAA4FAENgAAAABwKAIbAAAAADgUgQ0AAAAAHIrAhv2L7NTSWdM08Y4JuvL68bry+gm6ftJzmvf5TkXsbQEAAAA0KgIb6rbtIz3628f07NI8bQ9K/vQ0ZfgiCm5fp9dnPqYJf12noH0dAAAAAI2GwIbambl69al5WhuU/H0u1fS/PKEX/viw/vzsE5o+ppf8kvI/e1HPLS2zrwkAAACgkRDYUKuiRW9oYaGkdiM0+c7hyvZW1XiVffateuDMNEkRLZ+3ULmJqwIAAABoJAQ21GKnFn+cJ0kaeN7P1KmWT0nX0SM1UJIKV+nzzfZaAAAAAI2hlq/iaPEK1+mrXZLUS6cMTrHXVvD3Ut8OkhTQ2vUBey2AQ7B0y9pGXwAAQPNmWJZl2QsbavX6rZKk/r262KvQHHzxoq6csUrKGqFpfxilTvb6Siv/PF5Tv5T8p96kF67rY692vKVb1mr0S5PsxQ2yc/Jce1GDXDxrkj7Nbbwv3RPO/JUmjrjcXnzIOIeNq/2kS+1FDfLWNZM1rFtfezEAAC1ac8sq9LBhH0W7CyoeZLVVO3tlnOwObSVJwSADjwAAAABNgcCGfZRWBTCfX9VjjexPcUBF9jIAAAAADUZgQ8MFgyq1lwEAAABoMO5hwz62vzVFE98tkAZcrdm3n2yvrlbdrvel+tuE4QfXG9fEtu0oUGlZub04gdvlktvt0pc/bLBXKRozdaA/CbfbJZdh2IslSf2yu9mL9pHk9diLJEmmZSkajSWUffXjxoTnhmHI4679d5aYaco09//aXS5DQ3KOtxdLkiLR2AGP3eNxJxx7/DmM2F57bbwet71Iqjz2WMyUJJ3UsYe9Wqo89rrWj8VMxcyK9e2qzqHLZcjtqv3c1fd9H3RMz4S6cCSa8Lw2B/O+29/vKg1530/q2KP6M1+bQ3nf4zXWsdflUN/3Khw7x27HsXPsdeHYG//YJem4nPb2oiOuuWUVAhv2Ue/AdoB2h1PuD/kK7A3aiwEAAHCYpfqTCWyNgMCGfS19TlfOWie1G6lpj11Q5yiRa/86QY9+FlGn8yZq2qU59uojIm9ngaKVPTV18bhd8rhr/xUrHInKPMCfRJLXU+evUOXhiL1oH8lJtfdFmpZ1wF+xXIZR569Y0ViMY98Pjp1jt3P6sbtdLnk9bhmGIcuyEv4biUYP6ti9Hs8+61qWpUg0dsBf7KuO3b6uYRgqC4VlyJClus9f/LHHrxszTUUiMVmy6txGbe971TZiMVORWKx63dq2Udf7bhiGQuGILEt1rqsDvO+hcDRh3dq2caD33b5u/DZqO/Yq8Z95+7pV/63r2LWfz3z8Nrxed/XVCPaviPv7zFdtI8WXVP1eK24bh/qZV+U2DvbvvbbPvCSFwpFajz2e/X2P30Z5KLLP+2xX2/se/5mvUtt29ve+x3/mq9i3caD3vbZDj9+G/djjxb/v8a9Bcduo7dirdMjKsBcdcc0tqxDYsK9t8zRx8kfa7uqju2bcpCG19rAHtOiRB/VSrjTsxum69RR7PQAAAOA8zS2r1PpVHC1c517q65NkbtBXa+yVlYKrtDJXkquXBvazVwIAAABoDAQ21KKPzvxpmqSIFs//qNYh+7e/+5FWSvIPHqFhfnstAAAAgMZAYEOtul40UgNdknLnadJfV6io+vLliPI/eFaT3iuQXDm6bHSfxBUBAAAANBruYUOdgqte1u+eXaF8U5K88qenSMGAghFJrjSNvPU+XTMgxb4aAAAA4FjNLavQw4Y6+QdcremPXKtRvdvK740oWBxQ0JWirgMu0P3THiasAQAAAE2MHjYAAAAALUZzyyr0sAEAAACAQxHYAAAAAMChCGwAAAAA4FAENgAAAABwKAIbAAAAADgUgQ0AAAAAHIrABgAAAAAORWADAAAAAIcisAEAAACAQxHYAAAAAMChCGwAAAAA4FAENgAAAABwKAIbAAAAADgUgQ0AAAAAHIrABgAAAAAORWADAAAAAIcisAEAAACAQxHYAAAAAMChCGwAAAAA4FAENgAAAABwKAIbAAAAADgUgQ0AAAAAHIrABgAAAAAORWADAAAAAIcyLMuy7IUNtXr9VklS/15d7FWAI+wNlmv7rj0KhSP2qkbRGJ99XiOvsbE0xmsEAOBo0dyyCj1saJGa8stxY+E1Ng5eIwAAaM7oYUOLVPUZ7dfrWBmWKUMxSWZFpeWS5JHkkmlIMcOUFJWliCyZsiRZcklyS3Ir2XLJsFySZaiyUvIm7u9QVL3G9HSvXJZUXlKqDxe9r9xNWxQJheRJ8qrDMR2V07Wrju97gtpkZMjlcsmyLBmGIdOseDGmZckdK5fH49aaNV9rwYJ3VbC7UP/72v/Zd1lvVa+xS/sMe1WjSE9PtxfVW9VrDBXvslc1iiFDhtiL6q05nEcAAI4WzS2rENjQIlV9Rk/smSNJMuIrLZckQ5YkoyqAyZQMs+KJ5a7onK78y4l5zarWlY1jcikpfouHpOo1Hte9o4yYpdUrvtRLf31RsVBYhiXFLFOWYSgmS6FIWH379tW5554rS9LXa9Zo586dKi4uVigU0rGd2snv92vFF19q796gWrVK1az//V/7LuvNHjSs6vOVyDDsJ/ngNEbQOGoCm2VJ5r6n13AZ+55bS7LMmpYZmfvZLgAALUxzyypcEokWzZBkWC5Zcsuy3DLllmkYMo2KDjOpMoBYLsn0SKZXMl1SVFJMUlSyLJdicisml6JyKyqPbS8NY1mWkpK82rVrl8xYTKZpyrIsud1uGYYhw7IULivXyhVf6skn/qgX/jJDn3/6mTZv2KiCnfkqLtijr1ev0/JlXygaNuVxeVVWWm7fTYNZlhQuNlW8JaLizTVLyfcRxcL2mOF8hmHIMAy5XK6Epar8cLPClkJrixX6srBmWVUkszRqbyqzNKrQ6qLqdgAAoPkisKFlq8oRlipCWkIHkaWoO6xyb6nKvaUKeUsU9pYoklSiaPJeRZNLFUsJymOqZrEkt9W4f1YuwyUzZmrXrl2KRCIyTbMitJmWotGo9gZKZEWiymjVWl65pJgpKxKTFY5KsZjcliHDcisWNRSNWnK7PUpK8tl303CWVFYQ084VIe38ombZ9VVY0bLmE9gMw5Db7ZbP51NaWpoyMzPVrl07tWvXTm3btlV6erqSk5Pl8XjkcjXue70/VsRU8IOd2vvuj9VL6Xs/ygzse++bWRJR6Xs7qtsBAIDm6/B92wAcqSJIVMUJ05LMWEguY69cKpArFpI71koe0y9FfHKbSTJiror73sywDDMoWT/IsLbLMH6QK/K93JHtCXtoKNMyFTNjsqyK+9EqyixFohFJllJbtVKbtHSZ0aiSPB4ZpiUrFpNLFVdxGpYll1zyuD1yy5DbcMndVB1EVsXVo5aVuOxzHZ8DVQW1lJQUde/eXX369FHPnj3VrVs3de7cWZ07d1bXrl3Vo0cPnXDCCerZs6f8fr99M03Hkiyz6kNatdgbVbJs7QAAQLNFYEMLV/lltjLAxCJ7VVK8VevXfqSVy97Ud1+8rO8++X/aumKmQtvnK5i3QGU/vqvSHxaqbMe7Ktv1D+358SMV71ysgm3/VPHuxQrs/ihhDw0VjURVXl6uFL9fllXRqxaNRhWLxSoHFjFkuFxyezySYSgai8nt8cjldstwGTIMlyRLbpchj8ctt9slV1MFtmbKMAwlJyerW7duOuGEE5Senl59yaldVbBLTU1V79697dUAAACNisCGlq3iJraKh0ZEblepSgNbtHfP1wqXrJERWq22qZvVPv0HeWIbZES+V6R0myLBfO0t3qm9xfkqLS1VcXGRIpESRaP5CpXn2vfSMIbk9XqVnp6uaDQqM1bRhWUYLrlchuSqGPKkahASw+1WKBJWOBpRNBZT1IrJkKVYLCKv1yXLDKtbt872vbRYLpdLqampOu6445Senl5rSAMAADhSCGxo8SxZkhGTobA87nL5XCXq1M6l3t38OiYnXb6sdirzttbWPdKuskwVxbor5j9V3szz5Mm8QGnpwxUOH6cdO5K1efNelZU17hd+X1KSkpKSlJmZKTNmyrRMyZDcLpdcropeNNOwFDVjCkfCCkfCcnk8MtxuWS5DliGVlwcVCZcrGgmplT9Z55xzpn03jcLlkdw+I2FxeY19/qWxTMmMWIqWJS5mxKq47O8wMQxDrVq10nHHHaekpCTl5eWpqKio+l5By7Kq7xm0L9FoVMXFxfZNNhnDa8iV4parlad6MXwuWVFLZkk0YbGilgyfq7odAABovhjWHy1S1We0d69j5JJXHlOSFZG0Uzt2LZcVy5U3uksxM0OlsU4qLAxp/oKPNWTIOdqzJ6JfXnylUvzJMiVFSko0f/5cFZfs1I9563XcsW009jd/tO+y3qpe4/G9OsmKxJS7abMm3f+gzEhUviSf3JWhLBKNKBqNKtnnU3JKcuXlfB65DEOlwVIlJycrFgqpsHCPgmWlcrsNXXnlFfr5qMvsu6y3hOHoLSkWrgheCfesuSRvqiFX3I1zZkzavqRM4eLEdJaU7lKnnybL5alo25TD+lddBtm9e3clJyertLRU3333nSzLUkpKijIzM+Xz+VRaWqpYLFa9TtVgI0VFRQoGgzr55JMTtnsoDmZYfytmydwTlhWLO7kxS6X/3KFYYTi+qdxtvPKP7CDDU5GU2x7fPqEeAICWrLllFXrY0KIlmaY8phSRFHZ7FQgb+nrd9wqXt1JMHbW3rL02b5A+/WSbkjw5+v77gDzeVP3rg/dlGFJ5eamWrlii447vqWg4Wa1TT5Ar6UT7bhrGjEmy1DazjQxJbo9HMdNSzLQUjZmKRGPKyspSdrt28vmS5fMly+12V9zDZrjk8XjlT22tjp1y1DotQ96kZM17Z4F9Lw1nVPSu+TJc8rWJW9JdCWFNqrh1MBayFAkmLrFyW9hrQi6XS8ccc4ySk5MlSeFwWJZlybIsBYNBbd++XZs3b9aOHTuUn5+v/Px87dq1Sz/88IPy8vK0d+9emebh6w403Ibc2T55OiRXL+5sn6yIKTMQSVissCVPdk07AADQfBHY0LKFY1K44g9hr6SSqKUPZi9SyvdepRRmKbt1d5UFYxp62hkafNpP9bNf/kJZx3bSll3btdcKy9XKp5g7Sa2T0tU9q4tGn3+puvRs3MBWdUuV1+uVx+2p7uExLVOhUEhdju2irMxsmTEp1d9aKcl+ueSWIZfaZGRKpqFkX7JchlsdOx6jDh06Kbbv1F0timEYSkpKUkZGRvU9a0lJSQn3r1WFNwAAgCOJwIYWLZIsyTDljkjpkrRll67uc5a+nfOpCjeXyTAyVRo0lZHZUR99vFRv/P3vKijco17du0vhiAK78tXjhBP0+tt/V2q7LC3+8gv5O+XYd9MglmnJ5TK0Y8cOudwVf7Jut0vlZeU69tguauVvJV+ST4ZVMWdbx/YdlZ2VrbTUNHndXhUXFattVrbS0jKUnpaplJRWOrFff/tuWhSXy6XOnTtXz6NmWZZKS0sJaAAAwHEIbGjhvJJhyEqyFFNQ6Xvylf/aOyp79xN9/+kKuV1e9e9/iubOfVuZ6VnasyNfx2W112k9+iplV4k6lXvU2ZusG2+8RsFWUQVSQvp63Vf2nTSIaZlyGS5t2rSputenNBhU586dlZ2dpdTU1vJ4PPKn+BUOhVVWVqb8/HwVFhaqvLxchgx9//33Ki4uUiBQrMLCIuXv3mPfTYthGIa8Xq9atWpVXRaLxZSfn+/swGZasiKmrHDNomjFADSG15WwyJCsaFw7AADQbBHY0KLtlVeKSkZpSN7iHxXYu0UnDeuh1tGASub/S9+++o6653TTNVf8l665bIzuvflWndL9eCX9WKg1b76nb99YpA1/+7vyPvlUHbL8umLUufrFCb3su2kQwzAUiUb13Xffye1yKxIOq3Vqa2W0yZBpWdqelyefN0k/OWWIPG6Xvs/dKjMalRUzFQ2H1aF9O+3dW6yy8lKFwiGVl5cpGo3Yd9Oi+Hw+ud3u6ufl5eUKhUIJbZzGCpsq+b/vVTxrS83yylb5z2in9Gu7JSz+M9sp8OrW6nYAAKD5IrChRWslSeG9Kv9xo7b+858KvLVQ2954R/6ych3Ts5uy2rVXyZY8tQpHZQWKVZC7RWs+/kSbV6zUsSlt1DW5jfqb6epl+dU3NUOpO3fJv36zfTcNUlpaKtM09eOPO2RJikajSvGnyDBcKgkE5HJJx3U/Vl27dpbbIxmumNxuyTBiMgxTWdlt1L17V0WjIZlmRKmpKTLNlnsTW1UPW9X9apZlKRQKObt3TZIVsRTdFVL0h7LqJbYrJFdrjzzHpCQsrtYexfJr2gIAgOaLwIYWbafC2rl1vTY9/b8qe3quyj74UoWxmMqO66asnoPVwddOpd9u0tb/rNCWr75Scf4OnTiov5JaJctISlJyVpbUpp127y6VURLRyn9/qtde+Zt9Nw1SNRdYMFiqUHm52mRmypChYDCocDii9PTW6tO7l47t3FEnDThRyUlu+XxuJfvcMmMhbdu6RZs2r1fe9q0q2Vuo1mmt5K68F66l8ngS5yZjsmwAAOBULftbG1q8zsFytbfcat8uXf7UZEUsQ/4Ox2p3yKeigiR5Ax5ly62U8rDSfUlKSUmS0lPkTvdrR6hEu8oCWu2JKJCZoal/nqlpM2Zo7hdL7LtpkJQUvzwej8rLQyoPlSs5OVler7f6fraOHTtox848zXjuWe3Zs0sDTzpRnTt3VK9e3TXklEH6ydCT1blzR42+ZJTS0lrppJNOlL9Vkn03LZp9hEgAAACnILChZYulKdLzGGVdMUI723aSmT1Iha07qO8vT1enQR317a5vNPXlpzXuzht198SJeuYPf9Tmjz9TQe4WJbvDCkcK1Kp7Wx07pKe8WSnK7NJJycccY99Lw7i9MtweZbdrr3A0KjMak2XG5DakZJ9HJcXFWvDOu3K7ferc9ThlHZOjS6+5RhdceYXO/dUlOm7wIB2X0UHhH4vVr9sJapfRQUmGz76XFiUcrhicpaysTOXl5TJNk8AGAAAcicCGFs1Kkrwlpdr57Xc67tQBGvrf12tAv54qXLtGq5d9rDkLX9eyrz+XLyNZO0t2S6lebdn9g1rltFOrY9sp5ycD1H3gicrKydEZZ52lXj26aeuGb+y7aRDD5VIsFtPJJ58sQ5JpmkpKSpLb7ZLX61UkEtYvLrpQaamt9O26tcrdtEmx8nIpGpXLNJWVnq70Npnq1r27OuV0VigcUTgas++m4SwpWm6pvNBU+Z79L6HimDzJhpLbuBIWT4qhUKCmXVOwLEuxWExJSUnyeDyKxWKyLEutW7d2RmizJHNvVNEfa+5Vi/5QplhhWO42Xnk6plQv7myfzJJoQrvoD2UyS6IVk2xXtgMAAM2XYTXBnfar12+VJPXv1cVeBThC1We0W88uci/9UN9//rGO6ddfpdt2qOOm77Vt+Qq9890G5R2TrVMvvVDz/vGuvs3N1Uk/Gap7739AOR07y/D4JNNQzJ8hyyxT/o+bNPn+u+UrLdf0tz+077Leql5jjx7HyG0ZKi7Yo9t+c4uy22QqXB5Sx07HqCwUUr8+x+vcEadr1cpVSvGnKMXv1yk/OUVlZWWKxUzFzJgUDGlPUbFaZbTRq6+/ofzdBfqfJ6bad1lvVa+xS/sMWaYUyI1o55dh6QD/rBguQzlnJMuXnvibUShgKu/f5bJiFesPub5TQv2hqHqNoeJdUuX9asnJyerdu3f1SJFVA49s2LBB4XC4XgOQDBkyxF5UbwnnMWYptLpIpe/tkMya12H4XGp9xbHyZCdXl1lRU4FXtyqWnzjCpTvbp7Qru1QM8S8po12bhHoAAFqy5pZV6GFDixY1pGRfKxnJaUobNFDhnCwtWbtCO3b+oLLScpWFyvXPf/1Dx3TuqD79++j8iy9U1GsonOyWmeKV6fcqHCuTy2MpPT1Nt956h353/+/tu2kw0zSVmpqq/v37q9MxndS1WzcVFRWpdetU/bA9Tzt2/Kj+A/qpe7euGtC3j3K/W68fN+fqxy252rT6a8njUVJqK23J26aiQIk8SU1zD5tlSlbUkhnVfhfLtGS4DLm8iYthGLJiNes3BcuyFIlEKuaoMyr2qcqh/nv16qXs7OzqUSTr6nGrqktqovOoqJUw35oVNiVTMjwuGb64xeuSrIoh//dp661pBwAAmi/+T44WzSfJ1a27epz7c1mpWeryk9M06NILlNyvh4acM1IjzjxXw4cN008GD9Zv77xTfXr1VnrrDFmGS1FJlsejJI8plxmRLylJnbv0kNGqrX03DWK4XMrNzdWChQtUXl6urOwsuV0uxWKmgsEyhcJhFRUXKSnJJ7+/lQxL8nl9SvJ4lZHaWmn+VBXuLdHG3Fx9s36DigIBlZU7e86xpmaaprZt21Z9eeSWLVu0c+dOeb1eHXvsserXr5969+6trKysfUKb2+1Wx44d1bdvX/Xr1y+hDgAAoLER2NCipcQktcmQunRTNClN8rWS1a2D1L+bjhlyki745a/0i1+M1pCTh6pdZnu1Sc1QkuGRKyZZkZhCwXJFy0oVC5XLsAx5fK3kTmvcwKbK0SDXrPla4VBYGzds1I87flRZWVnFcP9lIX3y2edas/Ybbdi0RRs3b1XMMhSOWvro35/o7+8s0FPPPqsXXnxRi/75vlxyKVTWsgObZVkqKytTSUmJXC6XunTponA4rJKSEqkylCUnJ6u8vHyfyyNN05RpmvL5fHK5+CcUAAA0Lb5toEUzLCnmshRLSpblqviL2BkLyOzcWu6cTO0KB+VtnamMdp2UlNxayb5UJbl9SnJ55DFc8hiSL7mV3F6/XF6/fMl+eVNq7jFqDKZlqV37dsrOzlYsFlMoFNLu/N2KRMIKBAIyLWnj5q36y8y/asbzL2rqk9P16LQ/6k9/maF3P/hQG7fladv2H1RQsEdJHq88Lo+2bf3evptGYbgkw2PIcGu/i1yGYmFLkWDiEgtXXCpZ3a6JVM1tt337dkUiEblcLmVkZCgvL095eXkqLS1Vfn6+ysrK5PF4ZBiG/H6/DMOQx+NRQUGBLMvap/et0bgNGV6j4rLGykWSrGBUZnGkZimJSlbl5Y8JbS2Ze2vaAgCA5otBR9AiVX9Gj+skGRHJlayIYcgV2aHtq+YrWrhbKcm9lNahrwx/ilyGS5Ykl8cjT5JP7uQkqbJ3xTRS5IqFK4b3s0yZhiVXcivbHuuv6jUe172j3Ja06N1/aMlH/1bhrt3Ky8uTDKlV61R1yumsQCCg3QUFcrvdchmGwuGwkpJ88vmS5HK5VFS0W0lenzp3OlayXCosLNSrb75m32W9JQyWYdXcv6YD/KtiWdIPS8sVCSaOBOnxG+o0LLk6CLXtmJFQfyjsg47Ec7lcSk9PV9euXWUYhnbu3Kn8/HwprictOTlZZWVlyszMVGFhoTp06KBdu3bpxBNP3GcC7kMVfx5lWbJCpqyImXAerZilwCtbZZXHjfBpGGp9WWe5M7w1ZZJiRRGVvLGtetCSbo/8JKEeAICWrLllFXrY0KJFYuVSzJQVKZcZK1M0VqaIGZPLZ2hX8XcyvYVyJRtSkiF3ik+upGTJ7VHMtBSOhRWxIoqaYUWtsGSWSmaRXNEd9t00nGEop0sX9enXT+ltM+X2elRaGlRZaVAle4NKSknVrp27VLq3SKHyIhlWmQxXmcLRvUpNT1abNunyej0qKipUSSCgSLjxe10MQ3J5DXlSDHn8+1/cPkOWZSlalrjIlNxJNe2ammmaCgQCys3NVSwWU/v27dWjRw916dJFOTk5CZc8Vg004nK5mq5nTRUn0kh2y9XaK1dazWJ4XLLCZkXPWeVilcdkeIyEdhVtDVnlsep2AACg+SKwoUWLWG4FTZfKTVOKlElhS+XRVtpTZsqXEtLG75ZoT8H3isWC8njcCkdNRS2XQqapiBlTyCxXuLxI0VipguWF2p2/Wcs/fde+mwZxuz2Sy1Cffn014tyz1Sa7rYpKAorGovL5fPK6k7R3b7natcuSP0k6/bQB6tKptXp1b6fBg3ppwoRb9JNTTpahmEqDexUoKZbP10SjGzZDsVhMxcXF2rx5s4LBoPx+vzIyMpSampoQ2Koex4e1JrhAAQAAIAGBDS2aGXXJjLoUi7oVi/pUHvLJ7esob0oXuZKPlZGUrcKSoL7+doN25O9RKBJVKGoqXLVELMViXhUXRbRj517t3hNVm+zj7btpGMuUFTNlRmP6Yft2rfzqK2W2aaPMzEy5XC6Vh8q1d2+x0tJaq0vXLrru+hs0+eFHdOf4/9att9wmrydJPXr2kMfrVps2GWqb3Vb+Vn77Xlo00zS1d+9ebdy4UZs3b1Z5eblisYpLD6sCWnx4syxL4XBYW7dWXFIBAADQVAhsaNHMWExmzKoMbR7JaK2Onfvr+AFnq0e/kepz0lk6tltv9RswWFntj1FMLsntkVxeGa4kGa4keZP88qdmKKvdscrpeqK6Hn+KfTcNEotEZVgVf6xlpUHFYrGKQTMsU7GYqeLiPfKnJCkWi6hVamu5PUkqDYbkdifJkFtfffGVeh9/vHJyOlXOLyZlZTfySJaHxJCMiv8kLEdI1RD/RUVF+vbbb7V582ZFo1FFoxWXFFZNqF1UVCTTNPXdd9+poKDAvpmmYz9Pxn7+Bbe3AwAAzVZd/7sHWgTTKq9cQopZUZmGSzHDp70Rn0qifoUsv6JKUnlUCoajcvuSFbMsxSwpZhqKmS6FwmWKxiKKyVDU8GhvuHG/IbstKViyVx+8/y/Nnz9frVNba29pqbzeJMXMmCRTe0sKZVkxZbRpo5K9Qe3ML5DL7VN5WUTnnnWurFhMHTt2VPce3XTeeT/TrbffZt/NYWUYUpueXmWfmJSwtOmZJMPVuOevPqpGj4xEIgqFQjJNszqoFRYWyrIslZSUyDRNRaNRmWbioClNyfAaShmWJf+I9jXL6e3kSt134BNXqkf+M9pVtwMAAM0Xo0SiRar6jB6T5ZYhQ7LcktyS5ZZlGLJkyJIlQ6YMWZIMWXJVtpMsQ5JMyTDlsSpGiLTkkmUYMuVSu8ysxB0egqrXaJQX643X31Bh4R55PF7tDQSUty1PwbKgUlJS5HYbisXC6t7jOP1k6Ck6dehPlORxq6y0TD/k/ahdP+7S2vVrlJWVrWE/PUOpaZnKzMxSu2M62ndZbwmjG9aHVTFS5D6jSRoVYa6qVyg9Pd3WoP72N0pkYxgyZIi9qN4O6jyaVq3nzHBVTJOQwNY2o+1+tgsAQAvT3LIKPWxo0aJmRNFYWLFYWFY0JDNWLjNa8TxqRhWJmYrGLEWjlmJRU7FYRLFYRGY0IjMWkRmNyYxWllWVR8P23TTIS399UVs2bpJMqTwYVHFxsTxej7KysnXTjTfpnnsmaPLv79d/33WHzjrrLJWFwlrx1Wq9Ofdt/f2td7Thuw1q3z5b5513nrZt26ZIJKyS0oB9N4eXUTlnm32ONheX8NXJZchwGxXz3MUt+4S1WtoCAIDmix42tEjf5f6gUBMMbV+lMT77vEZeY2NpjNcIAMDRorllFXrY0CJ1apcpX1LiZMNOw2tsHLxGAADQnNHDBgAAAKDFaG5ZhR42AAAAAHAoAhsAAAAAOBSBDQAAAAAcisAGAAAAAA5FYAMAAAAAhyKwAQAAAIBDEdgAAAAAwKEIbAAAAADgUAQ2AAAAAHAoAhsAAAAAOBSBDQAAAAAcisAGAAAAAA5FYAMAAAAAhyKwAQAAAIBDEdgAAAAAwKEIbAAAAADgUAQ2AAAAAHAoAhsAAAAAOBSBDQAAAAAcisAGAAAAAA5FYAMAAAAAhyKwAQAAAIBDEdgAAAAAwKEIbAAAAADgUAQ2AAAAAHAoAhsAAAAAOBSBDQAAAAAcisAGAAAAAA5FYAMAAAAAhyKwAQAAAIBDEdgAAAAAwKEIbAAAAADgUAQ2AAAAAHCoJglsLpchSYqZpr0KAAAAAI6IqnxSlVeagyYJbF6PR5IUiUTtVQAAAABwRFTlk6q80hw0SWBL8XklScHysL0KAAAAAI6IqnxSlVeagyYJbK1SkiVJxXuD9ioAAAAAOCKq8klVXmkOmiSwZaS1kiSVlJapPEQvGwAAAIAjqzwUVklpmRSXV5qDJglsbpdLbTNaS5J27im2VwMAAADAYVWVS9pmtJbb1SQxqEk02Sttl5kul8tQcUlQe4r32qsBAAAA4LDYU7xXxSVBuVyG2mWm26sdrckCm9fjVsesNpKkvJ0FCnA/GwAAAIDDLLA3qLydBZKkjllt5PW47U0crckCmyq7G7Mz0yRJuT/k09MGAAAA4LDZU7xXuT/kS5KyM9Oqb9tqTgzLsix7YWP7cXeh8vcEJEnprf1qn5muZF+SvRkAAAAANFh5KKyde4pVXFJxlV92Zlr11X/NzWEJbJJUUFSiH3cXyjQrdte6VYrSU/3yJyfJ6/U0qxv/AAAAADhHzDQViUQVLA+reG+wejRIl8tQx6w2zbJnrcphC2ySFInGtGtPsQqKSuxVAAAAANBo2ma0VrvM9GZ3z5rdYQ1sVWKmqaJAqUrLylUWiigSjVb3vAEAAABAfbhchrwej1J8XrVKSVZGWquj5gq+IxLYAAAAAAAHdnTETgAAAAA4ChHYAAAAAMChCGwAAAAA4FAENgAAAABwKAIbAAAAADgUgQ0AAAAAHIrABgAAAAAORWADAAAAAIcisAEAAACAQxHYAAAAAMChCGwAAAAA4FAENgAAAABwKAIbAAAAADgUgQ0AAAAAHIrABgAAAAAORWADAAAAAIcisAEAAACAQxHYAAAAAMChCGwAAAAA4FAENgAAAABwKAIbAAAAADgUgQ0AAAAAHIrABgAAAAAORWADAAAAAIcisAEAAACAQxHYAAAAAMChCGwAAAAA4FAENgAAAABwKAIbAAAAADgUgQ0AAAAAHIrABgAAAAAORWADAAAAAIcisAEAAACAQxHYAAAAAMChCGwAAAAA4FAENgAAAABwKAIbAAAAADgUgQ0AAAAAHIrABgAAAAAORWADAAAAAIcisAEAAACAQxHYAAAAAMChCGwAAAAA4FAENgAAAABwKAIbAAAAADgUgQ0AAAAAHIrABgAAAAAORWADAAAAAIcisAEAAACAQxHYAAAAAMCh/j8ksb2lLj2UIAAAAABJRU5ErkJggg==" class="mt-2 w-full rounded-[8px] border border-[#DAD2C6]" alt="GitHub Pulse · Top committers" />
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
      <tr><td>Python（.py）</td><td>177</td><td>49,216</td><td>1,052</td><td>4,087</td></tr>
      <tr><td>JavaScript（.js / .mjs / .cjs）</td><td>10</td><td>6,095</td><td>29</td><td>54</td></tr>
      <tr><td>HTML（.html）</td><td>2</td><td>2,031</td><td>2</td><td>2</td></tr>
      <tr><td>CSS（.css / PostCSS）</td><td>3</td><td>631</td><td>30</td><td>83</td></tr>
      <tr><td>合计</td><td>192</td><td>57,973</td><td>1,113</td><td>4,226</td></tr>
    </tbody>
  </table>
  <div class="small mt-2 leading-[1.7]">模块（目录 / 包）：<b>code/core_engine</b>、<b>code/backend</b>、<b>code/frontend</b>、<b>tests</b>、<b>docs/slides</b> 共 5 个。<br>口径：仓库内 git 跟踪的 .py / .js / .html / .css，已排除 3 个本地辅助脚本与依赖、构建产物；Markdown / YAML / JSON 不计入源码行数。复核：<b>python docs/slides/count_lines.py</b>。</div>
</div>

<div>
  <div class="card-soft px-4 py-3">
    <div class="tag">AI Vibe Coding 与团队自写代码比例</div>
    <div class="body-text mt-1">口径：<b>git log --numstat</b> 汇总 148 次提交、新增 15.4 万行。剔除格式化 / 迁移（8.7 万行，占 57%）后：功能开发 4.6 万行、修复重构 2.0 万行。逐条标注 AI 起草（30 条覆盖 94%）后计算比例，脚本 <b>docs/slides/ai_ratio.py</b>。</div>
    <div class="text-[10px] mt-1.5" style="color:#8A8072">待团队填写：AI 起草 ≈ __% ／ 人工改写与自写 ≈ __%（标注表 ai-labels.csv）</div>
  </div>
  <div class="tag mt-3">工具输出（VS Code Counter 3.8.1）</div>
  <img src="data:image/png;base64,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" class="mt-1.5 w-full rounded-[8px] border border-[#DAD2C6]" alt="VS Code Counter Languages 输出" />
  <div class="text-[9.5px] mt-1" style="color:#8A8072">截取前 5 行；完整输出（含 Markdown / YAML / JSON 等）见仓库 .VSCodeCounter/</div>
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
