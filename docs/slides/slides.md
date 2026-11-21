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

# 三个部分、28 页：8 分钟讲完设计与实现

<div class="hr-line"></div>

<div class="grid grid-cols-2 gap-6">

<div>

<div class="text-[12.5px] font-bold text-[#1B3B5F]">1 · 产品设计</div>
<div class="mt-1">
<div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.1.1 使命</div><div class="text-[11px] font-bold text-[#1B3B5F]">P3</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.1.2 口号</div><div class="text-[11px] font-bold text-[#1B3B5F]">P4</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.1.3 目标用户</div><div class="text-[11px] font-bold text-[#1B3B5F]">P5</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.1.4 如何获得用户</div><div class="text-[11px] font-bold text-[#1B3B5F]">P6</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.1.5 团队优势</div><div class="text-[11px] font-bold text-[#1B3B5F]">P7</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.1.6 如何做到差异化</div><div class="text-[11px] font-bold text-[#1B3B5F]">P8</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.2 产品定义</div><div class="text-[11px] font-bold text-[#1B3B5F]">P9</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.2.1 解决的问题</div><div class="text-[11px] font-bold text-[#1B3B5F]">P10</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.2.2 对客户的价值</div><div class="text-[11px] font-bold text-[#1B3B5F]">P11</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">1.2.3 解决方案</div><div class="text-[11px] font-bold text-[#1B3B5F]">P12</div></div>
</div>

<div class="text-[12.5px] font-bold text-[#1B3B5F] mt-4">2 · 产品设计应用的原则</div>
<div class="mt-1">
<div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">十二条原则：四组，每组三条</div><div class="text-[11px] font-bold text-[#1B3B5F]">P13–14</div></div>
</div>

</div>

<div>

<div class="text-[12.5px] font-bold text-[#1B3B5F]">3 · 产品实现</div>
<div class="mt-1">
<div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.1 体验设计考虑的因素</div><div class="text-[11px] font-bold text-[#1B3B5F]">P15</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.2 语言 / IDE / 平台 / 框架</div><div class="text-[11px] font-bold text-[#1B3B5F]">P16</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.3 代码仓库与提交历史</div><div class="text-[11px] font-bold text-[#1B3B5F]">P17</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.4 全生命周期问题</div><div class="text-[11px] font-bold text-[#1B3B5F]">P18</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.1 系统架构图</div><div class="text-[11px] font-bold text-[#1B3B5F]">P19</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.2 基础设施与部署</div><div class="text-[11px] font-bold text-[#1B3B5F]">P20</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.3 智能体技术设计</div><div class="text-[11px] font-bold text-[#1B3B5F]">P21–22</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.4 数据库设计（E-R）</div><div class="text-[11px] font-bold text-[#1B3B5F]">P23</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.5 接口设计</div><div class="text-[11px] font-bold text-[#1B3B5F]">P24</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.5.6 前端设计</div><div class="text-[11px] font-bold text-[#1B3B5F]">P25</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.6 软件质量（方法 + 工具）</div><div class="text-[11px] font-bold text-[#1B3B5F]">P26</div></div><div class="flex items-baseline justify-between py-[5px] border-b border-[#EFE9DC]"><div class="text-[11.5px]">3.7 代码统计</div><div class="text-[11px] font-bold text-[#1B3B5F]">P27</div></div>
</div>

</div>

</div>

<!-- 目录按实际放映顺序生成，页码由分页脚本计算。 -->
---
layout: default
---
<div class="eyebrow">1.1.1 使命</div>

# 把「创作一部长篇」的门槛，降到「说得清一个想法」

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
  <div class="text-[11.5px] leading-[1.8]"><span class="tag text-[11px]">使命的三条判据：</span>读者不必会写、不必学提示词；每条设定都查得到出处与版本；成稿随时能整本带走。</div>
</div>

<!-- 1.1.1 使命：一句话 + 门槛/质量/归属三条判据。 -->
---
layout: default
---
<div class="eyebrow">1.1.2 口号</div>

# 一个点子，一部自洽的长篇

<div class="hr-line"></div>

<div class="card px-6 py-5">
  <div class="tag text-[11px]">主口号（对外）</div>
  <div class="text-[26px] font-extrabold mt-2 text-[#1B3B5F]">一个点子，一部自洽的长篇。</div>
  <div class="text-[11.5px] mt-2 leading-[1.75]" style="color:#6C7784">对读者说的一句话：输入是一个想法，输出是一整部前后一致的长篇——中间不需要写作技巧，也不需要提示词工程。</div>
</div>

<div class="card px-6 py-4 mt-3">
  <div class="tag text-[11px]">副口号（对内）</div>
  <div class="text-[17px] font-bold mt-1.5">先把「记得住」做对，再谈「写得好」。</div>
  <div class="text-[11.5px] mt-2 leading-[1.75]" style="color:#6C7784">对团队说的取舍：优先级是状态一致性与可恢复，辞藻与风格放在其后。这条决定了功能排序，也决定了我们放弃做「文笔润色工具」。</div>
</div>

<div class="grid grid-cols-3 gap-3 mt-3">
  <div class="card-soft px-4 py-3">
    <div class="tag">用在哪</div>
    <div class="body-text mt-1.5">README 首屏、答辩开场第一句、界面空状态文案，三处同一句话，不另起说法。</div>
  </div>
  <div class="card-soft px-4 py-3">
    <div class="tag">不承诺什么</div>
    <div class="body-text mt-1.5">不说「一键成神作」，不说「无限长度」；篇幅承诺只到验证过的 1 万字 / 8–10 章。</div>
  </div>
  <div class="card-soft px-4 py-3">
    <div class="tag">和使命的关系</div>
    <div class="body-text mt-1.5">使命讲「我们能做多大」，口号讲「凭什么选我们」；副口号把使命落到开发优先级上。</div>
  </div>
</div>

<!-- 1.1.2 口号：主口号对外 + 副口号对内 + 使用边界。 -->
---
layout: default
---
<div class="eyebrow">1.1.3 目标用户</div>

# 想创作却不会写的读者：三类画像

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

<div class="card px-5 py-4 mt-3">
  <div class="tag text-[11px]">为什么是这三类</div>
  <div class="body-text mt-1.5">三类人共同点：<b>有想法、缺写作能力、对前后一致敏感</b>。他们的痛点不是「写得好不好」，而是「写不长、写不一致」，正好落在我们的能力范围里。</div>
</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">这一版不服务：专业作者的量产工具 ｜ 移动端 App 与多人协作编辑（在线账号已支持）。市场口径（估算）：网文读者 5.75 亿，SAM 290 万–1150 万。</div>

<!-- 1.1.3 目标用户：三类画像 + 不服务谁 + 市场口径。 -->
---
layout: default
---
<div class="eyebrow">1.1.4 如何获得用户</div>

# 从种子到口碑：三步获客

<div class="hr-line"></div>

<div class="grid grid-cols-3 gap-3">
  <div class="card-soft p-4">
    <div class="tag">第一步 · 0 → 100</div>
    <div class="text-[12.5px] font-bold mt-1">种子内测</div>
    <div class="body-text mt-2">课程与社群内能直接接触到的读者，用「同题材对照生成」现场演示：同一设定下，通用聊天 vs Tome Agent，看谁不吃设定。</div>
  </div>
  <div class="card-soft p-4">
    <div class="tag">第二步 · 100 → 1000</div>
    <div class="text-[12.5px] font-bold mt-1">内容与信任</div>
    <div class="body-text mt-2">把「吃设定」做成可复现的案例（同一提示词跑三章），README 与仓库作为可核验的信任入口，不靠口号。</div>
  </div>
  <div class="card-soft p-4">
    <div class="tag">第三步 · 1000 →</div>
    <div class="text-[12.5px] font-bold mt-1">口碑与自传播</div>
    <div class="body-text mt-2">作品可导出、可分享首章；读者拿到成品后，下一个点子会自己回来用。</div>
  </div>
</div>

<div class="grid grid-cols-2 gap-3 mt-3">
  <div class="card px-4 py-3">
    <div class="tag">三个转化点</div>
    <div class="body-text mt-1.5 leading-[1.8]">费用可见（生成前预估并确认）<br>失败能续（检查点恢复，不丢半成品）<br>首章就能判断合不合口味</div>
  </div>
  <div class="card px-4 py-3">
    <div class="tag">为什么先做内测而不是投放</div>
    <div class="body-text mt-1.5 leading-[1.8]">产品还在验证期，投放会放大「承诺-交付」的差距；先在小范围把首章通过率与续写完成率跑出来，再谈渠道。</div>
  </div>
</div>

<!-- 1.1.4 如何获得用户：三步获客 + 三个转化点 + 渠道节奏。 -->
---
layout: default
---
<div class="eyebrow">1.1.5 团队优势</div>

# 四个人的链条：开发和验证在同一条线上

<div class="hr-line"></div>

<div class="flex gap-2">
  <div class="card-soft px-3 py-2 flex-1"><div class="text-[12px] font-bold">查军益</div><div class="small mt-0.5">开发 · 生成框架</div></div>
  <div class="card-soft px-3 py-2 flex-1"><div class="text-[12px] font-bold">秦宗鑫</div><div class="small mt-0.5">创作与质量评估</div></div>
  <div class="card-soft px-3 py-2 flex-1"><div class="text-[12px] font-bold">谭钧浩</div><div class="small mt-0.5">环境与功能测试</div></div>
  <div class="card-soft px-3 py-2 flex-1"><div class="text-[12px] font-bold">周涛</div><div class="small mt-0.5">体验与成果文档</div></div>
</div>
<div class="small mt-2">开发 → 创作评估 → 测试 → 体验文档，每项交付至少一名非负责人复核；计算机专业背景，从「数据一致性、事务、可恢复」切入。</div>

<div class="grid grid-cols-3 gap-3 mt-4">
  <div class="card-soft p-4">
    <div class="tag">优势一</div>
    <div class="text-[12.5px] font-bold mt-1">评估的人写测试</div>
    <div class="body-text mt-2">负责「写得对不对」的成员同时维护质量评估口径，标准由评估者自己落地成用例，不靠口头对齐。</div>
  </div>
  <div class="card-soft p-4">
    <div class="tag">优势二</div>
    <div class="text-[12.5px] font-bold mt-1">测试的人管环境</div>
    <div class="body-text mt-2">同一人负责本机、容器与云服务器三种跑法，问题在环境差异上第一次出现时就有人接手。</div>
  </div>
  <div class="card-soft p-4">
    <div class="tag">优势三</div>
    <div class="text-[12.5px] font-bold mt-1">文档的人盯体验</div>
    <div class="body-text mt-2">成果文档与体验走查同一个人做，写不出人话的地方就是界面需要改的地方。</div>
  </div>
</div>

<div class="card px-4 py-3 mt-3">
  <div class="text-[11px] leading-[1.7]"><span style="color:#B4472E">复核机制：</span>PR 必须由非作者本人复核；关键路径（记忆、提交、部署）改动要求附一条可复现的验证命令。</div>
</div>

<!-- 1.1.5 团队优势：四人链条 + 三条结构性优势 + 复核机制。 -->
---
layout: default
---
<div class="eyebrow">1.1.6 如何做到差异化</div>

# 不比谁更会写，比谁记得住

<div class="hr-line"></div>

<div class="grid grid-cols-3 gap-3">
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

<div class="card px-5 py-4 mt-3">
  <div class="tag text-[11px]">差异化怎么被验证</div>
  <div class="body-text mt-1.5">三条都能落到可对照的实验：同一设定分别用通用聊天与 Tome Agent 写三章，统计设定冲突次数、伏笔回收率与单章费用；数值放在第三部分。</div>
</div>

<div class="card px-4 py-2.5 mt-3">
  <div class="text-[11px]">通用 AI 卖「会写」，写作工具卖「作者的效率」，Tome Agent 卖「读者零门槛写出一部自洽的长篇」；承诺边界只到验证过的篇幅（1 万字 / 8–10 章起）。</div>
</div>

<!-- 1.1.6 差异化：三条差异 + 验证方式 + 承诺边界。 -->
---
layout: default
---
<div class="eyebrow">1.2 产品定义</div>

# 一句话讲清：给谁、做什么、不同于谁

<div class="hr-line"></div>

<div class="grid grid-cols-[92px_1fr] gap-x-4 gap-y-3 items-baseline">
  <div class="tag text-[11px]">对于</div><div class="text-[12.5px]">心里有想看的题材、却不会写小说的普通读者</div>
  <div class="tag text-[11px]">他们</div><div class="text-[12.5px]">想让 AI 写成前后连贯的长篇，但一写长就「吃设定」</div>
  <div class="tag text-[11px]">它是一个</div><div class="text-[12.5px]">部署在云服务器上的长篇小说生成助手</div>
  <div class="tag text-[11px]">它能够</div><div class="text-[12.5px]">用「规划 → 正文 → 事实变更 → 审核 → 提交」维护带出处与版本的记忆</div>
  <div class="tag text-[11px]">不同于</div><div class="text-[12.5px]">面向作者的复杂工作台，也不同于记不住设定的通用聊天</div>
  <div class="tag text-[11px]">我们的产品</div><div class="text-[12.5px]">让不会写小说的人，也能写出一部设定自洽、属于自己的长篇</div>
</div>

<div class="card px-5 py-4 mt-4">
  <div class="text-[11.5px] leading-[1.75]"><span style="color:#B4472E">为什么这样定义：</span>把「不会写」和「吃设定」两个约束写进定义里，后面所有设计决定（事实账本、事务提交、费用确认）都是这两条的推论；定义之外的功能一律进「不做清单」。</div>
</div>

<!-- 1.2 产品定义：模板六行单独成页。 -->
---
layout: default
---
<div class="eyebrow">1.2.1 解决的问题</div>

# 五个症状，一个根因

<div class="hr-line"></div>

<div class="grid grid-cols-2 gap-3">
  <div class="card-soft px-4 py-3"><div class="tag text-[10.5px]">01 记不住设定</div><div class="body-text mt-1">年龄、关系、能力、地点前后矛盾。</div></div>
  <div class="card-soft px-4 py-3"><div class="tag text-[10.5px]">02 时间线与因果</div><div class="body-text mt-1">谁在场、先发生什么，前后对不上。</div></div>
  <div class="card-soft px-4 py-3"><div class="tag text-[10.5px]">03 伏笔与义务</div><div class="body-text mt-1">前面埋的线后面忘了回收。</div></div>
  <div class="card-soft px-4 py-3"><div class="tag text-[10.5px]">04 上下文不可持续</div><div class="body-text mt-1">塞全文贵且衰减，摘要丢细节。</div></div>
  <div class="card-soft px-4 py-3"><div class="tag text-[10.5px]">05 过程不可恢复</div><div class="body-text mt-1">一次失败，成本与进度一起损失。</div></div>
  <div class="card px-4 py-3"><div class="tag text-[10.5px]">共同点</div><div class="body-text mt-1">都不是「文笔」问题，而是<b>状态管理</b>问题。</div></div>
</div>

<div class="card px-5 py-4 mt-3">
  <div class="text-[11.5px] font-bold leading-[1.75]"><span style="color:#B4472E">根因：</span>「记忆能力」≠「上下文长度」——所以从「让状态可查、可验、可恢复」入手，而不是写更长的提示词。</div>
</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">这五个症状在第三部分的架构与记忆设计里逐条对应到机制：事实账本、审计记录、检查点、费用预估。</div>

<!-- 1.2.1 解决的问题：五个症状 + 根因，单独成页。 -->
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
    <div class="text-[20px] font-extrabold text-[#1B3B5F] leading-none">194</div>
    <div class="text-[9.5px] mt-1" style="color:#6C7784">源码文件</div>
  </div>
</div>

<div class="text-[9.5px] mt-1.5 leading-[1.6]" style="color:#8A8072">目录：<b>code/core_engine</b>（105 个 .py）· <b>code/backend</b>（24，另 tools/ 3）· <b>tests</b>（43）· <b>code/frontend</b>（5 个 js/html/css）· <b>docs</b>（7 个脚本）；包：inf_backend、memory_runtime、tome_writer、tests 及两个子包。</div>

<table class="mt-2.5">
  <thead><tr><th>语言</th><th>文件</th><th>代码</th><th>注释</th><th>空行</th></tr></thead>
  <tbody>
    <tr><td>Python（.py）</td><td>179</td><td>49,404</td><td>1,082</td><td>4,132</td></tr>
    <tr><td>JavaScript</td><td>10</td><td>6,109</td><td>29</td><td>54</td></tr>
    <tr><td>HTML（.html）</td><td>2</td><td>2,031</td><td>2</td><td>2</td></tr>
    <tr><td>CSS（.css）</td><td>3</td><td>631</td><td>30</td><td>83</td></tr>
    <tr><td>合计</td><td>194</td><td>58,175</td><td>1,143</td><td>4,271</td></tr>
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

<div class="text-[9px] mt-1" style="color:#8A8072">VS Code Counter 3.8.1 输出（前 5 行：Python / Markdown / JS / YAML / HTML；完整输出见仓库 .VSCodeCounter/）</div>

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
