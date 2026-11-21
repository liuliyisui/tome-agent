---
theme: default
title: Tome Agent · 第一部分 产品设计与产品设计原则
info: |
  创新工程实践营项目汇报（8 分钟）
  第一部分：1. 产品设计（1.1–1.2）、2. 产品设计应用的原则
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

<!-- 开场：我们做的是 Tome Agent，一个本地运行的长篇小说生成助手。这 8 分钟我负责第一部分：它是什么，以及为什么这么设计。 -->

---
layout: default
---

<div class="mt-[54px] space-y-5">

<div class="card-soft flex items-center gap-6 px-7 py-9 bar-top">
  <div class="num text-[22px]">01</div>
  <div class="flex-1">
    <div class="text-[17px] font-extrabold">1.1 产品使命、口号和策略</div>
    <div class="small mt-2">使命 · 口号 · 目标用户 · 如何获得用户 · 团队优势 · 差异化</div>
  </div>
  <div class="text-[13px] font-bold text-[#1B3B5F]">6 项</div>
</div>

<div class="card-soft flex items-center gap-6 px-7 py-9 bar-top">
  <div class="num text-[22px]">02</div>
  <div class="flex-1">
    <div class="text-[17px] font-extrabold">1.2 产品定义</div>
    <div class="small mt-2">定位模板 · 解决的问题 · 用户故事（价值）· 解决方案形态</div>
  </div>
  <div class="text-[13px] font-bold text-[#1B3B5F]">4 项</div>
</div>

<div class="card-soft flex items-center gap-6 px-7 py-9 bar-top">
  <div class="num text-[22px]">03</div>
  <div class="flex-1">
    <div class="text-[17px] font-extrabold">2. 产品设计应用的原则</div>
    <div class="small mt-2">需求·信息·创新 / 系统·收敛·优化 / 继承·效益·时间 / 定量·简化·审核</div>
  </div>
  <div class="text-[13px] font-bold text-[#1B3B5F]">12 条</div>
</div>

</div>

<!-- 只放结构，不写“这一段要讲什么”“下一篇是什么”这类过渡语。 -->

---
layout: default
---

<div class="eyebrow">1.1.1 使命</div>

# 让心里有故事的人，写出一部属于自己的自洽长篇

<div class="hr-line"></div>

<div class="card-dk px-6 py-5">
  <div class="text-[14px] font-bold leading-[1.75]">使命：把「创作一部长篇」的门槛，从「会不会写」降到「说不说得清一个想法」；把「记得住」交给系统，而不是交给更长的提示词。</div>
</div>

<div class="grid grid-cols-3 gap-3 mt-4">

<div class="card-soft p-4">
  <div class="tag">门槛</div>
  <div class="body-text mt-2">读者只要给得出题材、主角和走向，就能拿到第 1 章；不需要学写作，也不需要学提示词。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">质量</div>
  <div class="body-text mt-2">跨章一致性靠结构化事实来管：每个设定带版本、变更理由和正文出处，可以逐条核验。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">归属</div>
  <div class="body-text mt-2">作品文件存在本机，可以导出；不为平台锁定，也不为订阅付费。</div>
</div>

</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">依据：docs/requirements/problem_definition.md（问题定义与产品描述）</div>

<!-- 使命一句话：让心里有故事的人把它写出来。两个着力点——门槛降到「说清一个想法」，一致性交给结构化事实。 -->

---
layout: default
---

<div class="eyebrow">1.1.2 口号</div>

# 对外一句记得住的话，对内一句不许走偏的话

<div class="hr-line"></div>

<div class="tag mt-3">主口号（对外）</div>
<div class="text-[40px] font-extrabold leading-tight mt-2 text-[#1D2B3A]">一个点子，一部自洽的长篇。</div>

<div class="grid grid-cols-[1fr_1.1fr] gap-6 mt-7">

<div class="card-soft p-4">
  <div class="tag">副口号（对内 / README 首行）</div>
  <div class="text-[15px] font-bold mt-2 text-[#1B3B5F] leading-relaxed">先把「记得住」做对，再谈「写得好」。</div>
</div>

<div>
  <div class="tag">备选（按场景取用）</div>
  <div class="body-text mt-2 leading-[1.9]">
    <div>「想看的，自己写出来。」——面向读者，情绪最直接</div>
    <div>「不会写，也能写完。」——强调完成度，适合首屏</div>
    <div>「设定不丢，故事才长。」——强调一致性，适合技术读者</div>
  </div>
</div>

</div>

<!-- 主口号给用户，副口号给我们自己：先把记得住做对。 -->

---
layout: default
---

<div class="eyebrow">1.1.3 目标用户</div>

# 用户是「想创作却不会写」的读者，不是专业作者

<div class="hr-line"></div>

<div class="grid grid-cols-3 gap-3">

<div class="card-soft p-4 bar-accent">
  <div class="text-[13px] font-bold">爱看小说的普通人</div>
  <div class="body-text mt-2">有明确口味：题材、主角、CP、爽点都在心里，就是写不出来。</div>
  <div class="body-text mt-2 text-[#1B3B5F] font-bold">诉求：一个点子，先拿到第 1 章看看合不合口味。</div>
</div>

<div class="card-soft p-4 bar-accent">
  <div class="text-[13px] font-bold">「设定控」读者</div>
  <div class="body-text mt-2">对前后一致、伏笔回收特别敏感，受够了 AI 的「吃设定」。</div>
  <div class="body-text mt-2 text-[#1B3B5F] font-bold">诉求：能查到某个设定从哪一章开始、又在哪一章改变。</div>
</div>

<div class="card-soft p-4 bar-accent">
  <div class="text-[13px] font-bold">短视频 / 图文创作者</div>
  <div class="body-text mt-2">需要设定自洽、可以直接改的故事脚本，但自己不会写小说。</div>
  <div class="body-text mt-2 text-[#1B3B5F] font-bold">诉求：题材能定制，产物能直接编辑和导出。</div>
</div>

</div>

<div class="grid grid-cols-[1.55fr_1fr] gap-4 mt-4">

<div class="card px-4 py-3">
  <div class="tag">这一版明确不服务谁</div>
  <div class="body-text mt-1">专业作者的量产工具（AI 文笔还撑不起量产质量）｜ 多人协作团队 ｜ 移动端与在线账号（首版单用户、本地运行）</div>
</div>

<div>
  <div class="tag">市场口径（估算，非统计口径）</div>
  <div class="text-[10.5px] leading-[1.8] text-[#3B4959] mt-1">
    <div><span class="font-bold text-[#1B3B5F]">TAM</span> 网文读者 5.75 亿</div>
    <div><span class="font-bold text-[#1B3B5F]">SAM</span> 愿尝试 AI 创作为 0.5%–2% → 约 290 万–1150 万</div>
    <div><span class="font-bold text-[#1B3B5F]">种子</span> 首年 100–500 名真实读者</div>
  </div>
</div>

</div>

<div class="card-dk px-4 py-3 mt-4 flex items-center">
  <div class="text-[12px]"><span class="tag text-[11px]">用户判据：</span>一个没写过小说的人，10 分钟内能不能拿到一部属于自己口味的第一章？</div>
</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">数据来源：《2024 中国网络文学蓝皮书》（2025-06）；SAM / SOM 为基于公开总量的比例假设，需实测校准。</div>

<!-- 我们的用户不是作者，是想创作却不会写的读者。三类画像，各自要的是「第一章」「查设定」「可改的脚本」。 -->

---
layout: default
---

<div class="eyebrow">1.1.4 如何获得用户</div>

# 从 0 到 1000：种子、内容、口碑三步走

<div class="hr-line"></div>

<div class="grid grid-cols-3 gap-3">

<div class="card-soft p-4 flex flex-col">
  <div class="tag">0 → 100</div>
  <div class="text-[12.5px] font-bold mt-1">种子：先把身边人变成用户</div>
  <div class="body-text mt-3 leading-[1.8] flex-1">
    <div>· 课程、社团、写作群内测邀请</div>
    <div>· 现场做「同题材对照生成」演示</div>
    <div>· 每位受邀者试读并填反馈表</div>
  </div>
  <div class="small mt-3"><span class="font-bold text-[#1B3B5F]">看板指标：</span>首章读完率 / 二次生成率</div>
</div>

<div class="card-soft p-4 flex flex-col">
  <div class="tag">100 → 1000</div>
  <div class="text-[12.5px] font-bold mt-1">内容：把「吃设定」做成可复现的案例</div>
  <div class="body-text mt-3 leading-[1.8] flex-1">
    <div>· 同题材、同模型，有无状态记忆对比</div>
    <div>· B 站 / 知乎 / 小红书 + README 作信任入口</div>
    <div>· 开源仓库即试用入口，一条命令跑通</div>
  </div>
  <div class="small mt-3"><span class="font-bold text-[#1B3B5F]">看板指标：</span>仓库访问 → 本地跑通率</div>
</div>

<div class="card-soft p-4 flex flex-col">
  <div class="tag">1000 →</div>
  <div class="text-[12.5px] font-bold mt-1">口碑：作品本身是最好的广告</div>
  <div class="body-text mt-3 leading-[1.8] flex-1">
    <div>· 每部作品可导出、可分享首章</div>
    <div>· 读者晒「我生成的小说」，带作品名回链</div>
    <div>· 把对照实验更新成季度报告</div>
  </div>
  <div class="small mt-3"><span class="font-bold text-[#1B3B5F]">看板指标：</span>自然分享带来的新增</div>
</div>

</div>

<div class="card px-4 py-3 mt-4">
  <div class="tag">三个必须做对的转化点</div>
  <div class="text-[11.5px] mt-1 text-[#3B4959]">① 生成前看得见费用（预估 token 与人民币）　② 失败能续（检查点恢复，不从头再来）　③ 首章就能判断合不合口味（先读再批量）</div>
</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">说明：获客路径为计划，尚未实测；种子目标 100–500 人，指标口径随第一轮试用校准。</div>

<!-- 获客三步：种子、内容、口碑。真正决定转化的是三点——费用看得见、失败能续、首章就能判断口味。 -->

---
layout: default
---

<div class="eyebrow">1.1.5 团队优势</div>

# 四个人的分工是一条完整链条，不是一个开发带三个旁观者

<div class="hr-line"></div>

<div class="grid grid-cols-[1fr_1fr] gap-6">

<div>
  <div class="tag mb-2">分工（苏州大学 计算机科学与技术 2025 级）</div>
  <div class="space-y-2">
    <div class="card-soft flex items-center px-3 py-2">
      <div class="w-[62px] text-[11px] font-bold">查军益</div>
      <div class="flex-1"><div class="tag">项目负责人 / 核心开发</div><div class="small mt-0.5">生成框架、模型接口、代码集成</div></div>
    </div>
    <div class="card-soft flex items-center px-3 py-2">
      <div class="w-[62px] text-[11px] font-bold">秦宗鑫</div>
      <div class="flex-1"><div class="tag">项目协调 / 创作评估</div><div class="small mt-0.5">创作需求、小说质量评估、风险</div></div>
    </div>
    <div class="card-soft flex items-center px-3 py-2">
      <div class="w-[62px] text-[11px] font-bold">谭钧浩</div>
      <div class="flex-1"><div class="tag">测试 / 问题跟踪</div><div class="small mt-0.5">环境安装、功能测试、缺陷记录</div></div>
    </div>
    <div class="card-soft flex items-center px-3 py-2">
      <div class="w-[62px] text-[11px] font-bold">周涛</div>
      <div class="flex-1"><div class="tag">体验 / 文档</div><div class="small mt-0.5">页面体验、文档整理、成果展示</div></div>
    </div>
  </div>
</div>

<div>
  <div class="tag mb-2">三条可验证的优势</div>
  <div class="space-y-4">
    <div>
      <div class="text-[12px] font-bold text-[#1B3B5F]">链条完整</div>
      <div class="body-text mt-1">开发 → 创作评估 → 测试 → 体验文档，每项交付至少一名非负责人复核，避免「一个人测自己写的代码」。</div>
    </div>
    <div>
      <div class="text-[12px] font-bold text-[#1B3B5F]">视角对</div>
      <div class="body-text mt-1">计算机专业背景，从「数据一致性、事务、可恢复」切入长文本生成，而不是从「提示词技巧」切入。</div>
    </div>
    <div>
      <div class="text-[12px] font-bold text-[#1B3B5F]">可复现</div>
      <div class="body-text mt-1">两周计划、Issue / Kanban 留痕、真实调用记录 token 与费用；换一台电脑能按脚本跑起来。</div>
    </div>
  </div>
</div>

</div>

<!-- 四个人是一条链：开发、创作评估、测试、体验文档，每项交付都有第二个人复核。 -->

---
layout: default
---

<div class="eyebrow">1.1.6 如何做到差异化</div>

# 不比「谁更会写」，比「谁记得住、谁不糊弄」

<div class="hr-line"></div>

| 维度 | 通用 AI 聊天 | 面向作者的写作工具 | 网文阅读平台 | Tome Agent |
| --- | --- | --- | --- | --- |
| 目标用户 | 会用提示词的任何人 | 会写的作者 | 读者（读现成的） | 想创作却不会写的读者 |
| 输入方式 | 一段提示词 | 大纲、设定、章节指令 | — | 一个点子：题材 + 主角 + 走向 |
| 记忆方式 | 上下文窗口，越长越贵、越衰减 | 多为摘要或设定表 | — | 带版本与正文出处的事实账本 |
| 生成单位 | 一次回答 | 一段 / 一章 | — | 一章一事务，校验后提交 |
| 失败处理 | 重新生成一遍 | 手工修改 | — | 检查点恢复，正式稿不被污染 |
| 承诺边界 | 不承诺篇幅 | 不承诺篇幅 | — | 只承诺验证过的篇幅（1 万字 / 8–10 章起） |
| 成本与归属 | 订阅 | 订阅 + 云端 | 平台内阅读 | 本地运行、自带 Key、作品留本机 |

<div class="card-dk px-5 py-3 mt-4">
  <div class="text-[11.5px]"><span class="tag text-[11px]">一句话差异化：</span>通用 AI 卖「会写」，写作工具卖「作者的效率」，Tome Agent 卖「读者零门槛写出一部自洽的长篇」。</div>
</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">竞品信息：公开产品页与第三方横评（2026-04），属市场观察，不是严格测评。</div>

<!-- 差异化四层：面向读者而非作者、事实级记忆而非摘要、提交是事务而非覆盖、本地归属。最后一列只承诺验证过的篇幅。 -->

---
layout: default
---

<div class="eyebrow">1.2 产品定义</div>

# 用定位模板把产品说清楚：给谁、解决什么、凭什么不同

<div class="hr-line"></div>

<div class="mt-2">

<div class="grid grid-cols-[150px_1fr] gap-x-5 items-baseline py-[9px] border-b border-[#E8E1D5]">
  <div class="tag text-[11px]">对于</div>
  <div class="text-[12.5px]">心里有想看的题材、却不会写小说的普通读者</div>
</div>

<div class="grid grid-cols-[150px_1fr] gap-x-5 items-baseline py-[9px] border-b border-[#E8E1D5]">
  <div class="tag text-[11px]">他们</div>
  <div class="text-[12.5px]">想让 AI 把想法写成一部前后连贯的长篇，但通用 AI 一写长就「吃设定」</div>
</div>

<div class="grid grid-cols-[150px_1fr] gap-x-5 items-baseline py-[9px] border-b border-[#E8E1D5]">
  <div class="tag text-[11px]">Tome Agent 是一个</div>
  <div class="text-[12.5px]">本地运行的长篇小说生成助手</div>
</div>

<div class="grid grid-cols-[150px_1fr] gap-x-5 items-baseline py-[9px] border-b border-[#E8E1D5]">
  <div class="tag text-[11px]">它能够</div>
  <div class="text-[12.5px]">用「逐章规划 → 正文 → 事实变更 → 独立审核 → 原子提交」维护带出处和版本的记忆，生成可暂停、可恢复、可导出</div>
</div>

<div class="grid grid-cols-[150px_1fr] gap-x-5 items-baseline py-[9px] border-b border-[#E8E1D5]">
  <div class="tag text-[11px]">不同于</div>
  <div class="text-[12.5px]">面向作者的复杂写作工作台，也不同于记不住设定的通用 AI 聊天</div>
</div>

<div class="grid grid-cols-[150px_1fr] gap-x-5 items-baseline py-[9px] border-b border-[#E8E1D5]">
  <div class="tag text-[11px]">我们的产品</div>
  <div class="text-[12.5px]">让不会写小说的人，也能创作出一部设定自洽、属于自己的长篇小说</div>
</div>

</div>



<!-- 定位模板逐行念一遍：对于谁、他们有什么诉求、我们是什么、能做什么、不同于谁、最终给到什么。 -->

---
layout: default
---

<div class="eyebrow">1.2.1 解决的问题</div>

# 五个症状，一个根因：记忆能力撑不起一部书

<div class="hr-line"></div>

<div class="grid grid-cols-[1.25fr_1fr] gap-6">

<div>
  <div class="flex gap-3 items-start py-[7px] border-b border-[#E8E1D5]">
    <div class="num w-[30px]">01</div>
    <div><div class="text-[12px] font-bold">记不住设定</div><div class="small mt-0.5">年龄、关系、能力、地点——稍微写长一点就开始前后矛盾。</div></div>
  </div>
  <div class="flex gap-3 items-start py-[7px] border-b border-[#E8E1D5]">
    <div class="num w-[30px]">02</div>
    <div><div class="text-[12px] font-bold">时间线与因果对不上</div><div class="small mt-0.5">事件顺序、谁在场、发生过什么，跨章之后对不齐。</div></div>
  </div>
  <div class="flex gap-3 items-start py-[7px] border-b border-[#E8E1D5]">
    <div class="num w-[30px]">03</div>
    <div><div class="text-[12px] font-bold">伏笔与义务不回收</div><div class="small mt-0.5">前面埋下的线索、答应过的走向，后面忘了提。</div></div>
  </div>
  <div class="flex gap-3 items-start py-[7px] border-b border-[#E8E1D5]">
    <div class="num w-[30px]">04</div>
    <div><div class="text-[12px] font-bold">上下文不可持续</div><div class="small mt-0.5">全文塞进长上下文：贵、注意力衰减；改成摘要：细节又丢了。</div></div>
  </div>
  <div class="flex gap-3 items-start py-[7px]">
    <div class="num w-[30px]">05</div>
    <div><div class="text-[12px] font-bold">生成过程不可恢复</div><div class="small mt-0.5">一次失败就要重来，成本和进度一起损失。</div></div>
  </div>
</div>

<div>
  <div class="card-dk px-5 py-4">
    <div class="tag">根因判断</div>
    <div class="text-[16px] font-extrabold mt-2 leading-snug">「记忆能力」≠「上下文长度」</div>
    <div class="text-[11px] mt-3 leading-[1.75] text-[#E6DFD2]">模型不是不想记。是「把前文再喂一遍」这种记忆方式，撑不起一部书——越往后越贵、越模糊。</div>
    <div class="text-[11px] font-bold mt-3 leading-[1.75]">所以我们不从「再写一段更长的提示词」入手，而从「怎么让故事状态可查、可验、可恢复」入手。</div>
  </div>
  <div class="mt-4 text-[10.5px] leading-[1.7] text-[#6C7784]">「状态记忆能减少跨章矛盾」目前是待验证假设：用同输入、同模型、有 / 无记忆的对照实验来证明。</div>
</div>

</div>

<!-- 五个症状，一个根因：记忆能力不等于上下文长度。最后那句诚实说明很重要——一致性提升目前还是待验证假设。 -->

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

# 形态选「本地网站」：作品和密钥留在本机，浏览器打开就能用

<div class="hr-line"></div>

<div class="text-[11.5px] leading-[1.7]"><span class="tag text-[11px]">为什么是网站，不是小程序 / App：</span>作品文件与 API Key 必须留在本机、成本按 token 透明、不经过上架审核；本地网页用浏览器即可打开，不需要账号、不需要装客户端。</div>

<div class="grid grid-cols-[1.05fr_1fr] gap-5 mt-6">

<div>
  <div class="tag">技术组成（版本见 README）</div>
  <div class="mt-2 space-y-[7px]">
    <div class="grid grid-cols-[52px_1fr] gap-2 items-baseline"><div class="text-[11px] font-bold text-[#1B3B5F]">界面</div><div class="small">Vue 3.5.44 内置运行时，无前端构建；本地服务 <span class="mono">http://127.0.0.1:8765</span></div></div>
    <div class="grid grid-cols-[52px_1fr] gap-2 items-baseline"><div class="text-[11px] font-bold text-[#1B3B5F]">编排</div><div class="small">LangGraph 1.2.17 把五个阶段建成状态图，支持条件分支与重规划</div></div>
    <div class="grid grid-cols-[52px_1fr] gap-2 items-baseline"><div class="text-[11px] font-bold text-[#1B3B5F]">存储</div><div class="small">文件模式零配置即可跑；需要持久化时用 PostgreSQL 17 + Psycopg 3.3.3</div></div>
    <div class="grid grid-cols-[52px_1fr] gap-2 items-baseline"><div class="text-[11px] font-bold text-[#1B3B5F]">模型</div><div class="small">Chat Completions 兼容接口：DeepSeek、OpenAI 及其他兼容服务</div></div>
  </div>
</div>

<div class="card-soft px-4 py-3">
  <div class="tag">用户看到的三件事</div>
  <div class="body-text mt-1 leading-[1.8]">
    <div>· 生成前：显示本次预估输入 / 输出 token 与人民币费用，确认后才调用模型</div>
    <div>· 生成中：逐章保存检查点，中断后从断点继续，正式稿只在整章校验通过后写入</div>
    <div>· 生成后：在工作台读章、导出排版好的 Markdown，作品目录在本机随手可备份</div>
  </div>
</div>

</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">对应课程要求「网站 / 微信小程序 / Android 应用」中的「网站」形态。</div>

<!-- 形态选网站：作品和密钥留在本机。技术栈版本都在 README。 -->

---
layout: default
---

<div class="eyebrow">1.2.3 解决方案 · 运行机制</div>

# 一章是怎么生成的：五个阶段，一次事务提交

<div class="hr-line"></div>

<div class="flex gap-1 mt-4">
  <div class="flex-1"><div class="step">下一章规划</div><div class="stepnote">只改下一章</div></div>
  <div class="flex-1"><div class="step">正文候选</div><div class="stepnote">不能改存档</div></div>
  <div class="flex-1"><div class="step">事实变更候选</div><div class="stepnote">带出处与版本</div></div>
  <div class="flex-1"><div class="step">独立审核</div><div class="stepnote">矛盾与遗漏</div></div>
  <div class="flex-1"><div class="step">整章事务提交</div><div class="stepnote">失败不改正式稿</div></div>
  <div class="flex-1"><div class="step step-alt">导出 Markdown</div><div class="stepnote">可改可投稿</div></div>
</div>

<div class="grid grid-cols-3 gap-3 mt-6">

<div class="card-soft p-4">
  <div class="tag">不越权</div>
  <div class="body-text mt-1">规划只提下一章计划；写作角色不能直接改正式存档；审核角色只判不改。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">可追溯</div>
  <div class="body-text mt-1">每条事实带稳定属性名、版本、变更理由和正文原句，能查到某个设定从哪一章开始、又在哪一章改变。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">可恢复</div>
  <div class="body-text mt-1">先在副本上校验章节、计划与记忆，通过后整章提交；失败不改变正式快照，中断后从检查点继续。</div>
</div>

</div>

<div class="card-dk px-5 py-3 mt-4">
  <div class="text-[11.5px]">一次生成 = 「规划 → 写作 → 记忆 → 审核 → 提交」；本地运行、作品留在本机、按 token 透明计费。</div>
</div>

<!-- 这一页专讲机制：五段一串，核心是提交是事务、失败不动正式稿。功能细节不放在封面，放到这里。 -->

---
layout: default
---

<div class="eyebrow">2. 产品设计应用的原则</div>

# 十二条原则，一条主线：每条都要能在仓库里找到证据

<div class="hr-line"></div>

<div class="grid grid-cols-2 gap-3">

<div class="card-soft px-5 py-4">
  <div class="flex items-baseline gap-3"><div class="num">01</div><div class="text-[14px] font-bold">需求 · 信息 · 创新</div></div>
  <div class="small mt-2">先有真需求，再用信息校准，最后才谈创新</div>
</div>

<div class="card-soft px-5 py-4">
  <div class="flex items-baseline gap-3"><div class="num">02</div><div class="text-[14px] font-bold">系统 · 收敛 · 优化</div></div>
  <div class="small mt-2">把作品当系统，先发散后收敛，再逐项优化</div>
</div>

<div class="card-soft px-5 py-4">
  <div class="flex items-baseline gap-3"><div class="num">03</div><div class="text-[14px] font-bold">继承 · 效益 · 时间</div></div>
  <div class="small mt-2">能继承的不重造，算清效益，抢住窗口</div>
</div>

<div class="card-soft px-5 py-4">
  <div class="flex items-baseline gap-3"><div class="num">04</div><div class="text-[14px] font-bold">定量 · 简化 · 审核</div></div>
  <div class="small mt-2">能测就测，能简就简，每一步都审</div>
</div>

</div>

<div class="mt-5 text-[11.5px] leading-[1.85]"><span class="font-bold text-[#1B3B5F]">为什么是这十二条：</span>它们来自产品设计的基础原则体系（需求 / 信息 / 创新；系统 / 收敛 / 优化；继承 / 效益 / 时间；定量 / 简化 / 审核），正好覆盖我们这轮设计要做判断的四个层面——要不要做、怎么成形、拿什么换、怎么验收。</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">参考：产品设计小文集锦（四篇）；机械工业出版社《现代产品设计指南》1.5 节产品设计和开发的原则。</div>

<!-- 十二条原则分四组。我用一条判定：每条原则都要能在仓库里找到一次具体的设计决策或一份证据。 -->

---
layout: default
---

<div class="eyebrow">2. 产品设计应用的原则 · 组一</div>

# 需求定方向，信息校准方向，创新才有落脚点

<div class="hr-line"></div>

<div class="grid grid-cols-3 gap-3">

<div class="card-soft px-4 py-4 border-t-[3px] border-t-[#1B3B5F]">
  <div class="text-[16px] font-extrabold text-[#1B3B5F]">需求原则</div>
  <div class="text-[10.5px] text-[#6C7784] mt-1 leading-relaxed">功能要求来自客观需求：显需求推动改进，隐需求催生创新。</div>
  <div class="tag mt-3">本产品的做法</div>
  <div class="body-text mt-1 leading-[1.75]">
    <div>· 需求从「不会写」和「吃设定」出发，不是从「模型能干什么」出发</div>
    <div>· 先冻结 MVP：单用户、本地、中文、顺序逐章；多人协作 / 移动端 / 自动出版明确不做</div>
    <div>· 显需求 = 把想法变成第 1 章；隐需求 = 设定可查、失败可续</div>
  </div>
</div>

<div class="card-soft px-4 py-4 border-t-[3px] border-t-[#1B3B5F]">
  <div class="text-[16px] font-extrabold text-[#1B3B5F]">信息原则</div>
  <div class="text-[10.5px] text-[#6C7784] mt-1 leading-relaxed">全面、充分、正确、可靠地掌握市场、技术、测试信息，用它引导设计。</div>
  <div class="tag mt-3">本产品的做法</div>
  <div class="body-text mt-1 leading-[1.75]">
    <div>· 设计前完成竞品与长文本架构调研：网文读者 5.75 亿、三类竞品对照、长上下文 / 摘要 / 检索方案比较</div>
    <div>· 结论「记忆能力是真实短板」写进问题定义，而不是拍脑袋定功能</div>
    <div>· 调研、架构、验证记录都进仓库，成为下一轮决策的输入</div>
  </div>
</div>

<div class="card-soft px-4 py-4 border-t-[3px] border-t-[#1B3B5F]">
  <div class="text-[16px] font-extrabold text-[#1B3B5F]">创新原则</div>
  <div class="text-[10.5px] text-[#6C7784] mt-1 leading-relaxed">大胆创新，冲破传统观念与惯例的束缚。</div>
  <div class="tag mt-3">本产品的做法</div>
  <div class="body-text mt-1 leading-[1.75]">
    <div>· 事件先行：先推演场景事件与状态，再写正文，而不是写完再回头猜关键事实</div>
    <div>· 事实账本：每条设定带稳定属性名、版本、变更理由和正文原句</div>
    <div>· 提交是事务不是覆盖：在副本上校验通过才整体写入</div>
  </div>
</div>

</div>

<div class="card px-4 py-3 mt-4">
  <div class="text-[11px]"><span class="font-bold text-[#1B3B5F]">一句话：</span>需求回答「该不该做」，信息回答「凭什么这样设计」，创新回答「我们做了什么别人没做的」。</div>
</div>

<!-- 组一的关键词是「别自嗨」：需求来自用户的痛点，创新要有证据支撑。 -->

---
layout: default
---

<div class="eyebrow">2. 产品设计应用的原则 · 组二</div>

# 把作品当系统设计，先发散后收敛，再逐项优化

<div class="hr-line"></div>

<div class="grid grid-cols-3 gap-3">

<div class="card-soft px-4 py-4 border-t-[3px] border-t-[#1B3B5F]">
  <div class="text-[16px] font-extrabold text-[#1B3B5F]">系统原则</div>
  <div class="text-[10.5px] text-[#6C7784] mt-1 leading-relaxed">用系统论方法求功能结构，通过分析、综合与评价，达到综合最优。</div>
  <div class="tag mt-3">本产品的做法</div>
  <div class="body-text mt-1 leading-[1.75]">
    <div>· 写作被建成「规划—写作—记忆—审核—提交」的状态系统，用 LangGraph 状态图表达</div>
    <div>· 四个角色职责与 JSON 契约固定：规划只改下一章、写作不能改存档、审核只判不改</div>
    <div>· 任何环节失败都不污染正式快照——系统边界优先于单点效果</div>
  </div>
</div>

<div class="card-soft px-4 py-4 border-t-[3px] border-t-[#1B3B5F]">
  <div class="text-[16px] font-extrabold text-[#1B3B5F]">收敛原则</div>
  <div class="text-[10.5px] text-[#6C7784] mt-1 leading-relaxed">先发散思维构思方案，再综合多种信息收敛。</div>
  <div class="tag mt-3">本产品的做法</div>
  <div class="body-text mt-1 leading-[1.75]">
    <div>· 记忆方案先发散四种：全文塞上下文 / 摘要压缩 / 向量检索 / 结构化事实</div>
    <div>· 按「可核验、可恢复、成本」三个标准收敛到结构化事实 + 三层记忆</div>
    <div>· 首版只带最近两章、最多 128 条有效事实：先收敛到能验证的规模</div>
  </div>
</div>

<div class="card-soft px-4 py-4 border-t-[3px] border-t-[#1B3B5F]">
  <div class="text-[16px] font-extrabold text-[#1B3B5F]">优化原则</div>
  <div class="text-[10.5px] text-[#6C7784] mt-1 leading-relaxed">方案择优、参数优化、总体方案优化：高效、优质、经济。</div>
  <div class="tag mt-3">本产品的做法</div>
  <div class="body-text mt-1 leading-[1.75]">
    <div>· 篇幅按「总字数 − 已写 − 剩余章节」动态分配，而不是每章固定字数</div>
    <div>· 局部失败降级：规划或记忆处理失败时记录问题，尽量保住有效正文</div>
    <div>· 审核格式错误最多修一次，避免无限循环；重规划只改尚未写作的章节</div>
  </div>
</div>

</div>

<div class="card px-4 py-3 mt-4">
  <div class="text-[11px]"><span class="font-bold text-[#1B3B5F]">一句话：</span>系统原则让我们定义务边界，收敛原则让我们砍掉炫技方案，优化原则让我们在真实约束下调参数。</div>
</div>

<!-- 组二的关键词是「有边界」：系统定边界，收敛定范围，优化定参数。 -->

---
layout: default
---

<div class="eyebrow">2. 产品设计应用的原则 · 组三</div>

# 能继承的不重造，算清效益，抢住时间窗口

<div class="hr-line"></div>

<div class="grid grid-cols-3 gap-3">

<div class="card-soft px-4 py-4 border-t-[3px] border-t-[#1B3B5F]">
  <div class="text-[16px] font-extrabold text-[#1B3B5F]">继承原则</div>
  <div class="text-[10.5px] text-[#6C7784] mt-1 leading-relaxed">批判地吸收前人成果，推陈出新，为我所用。</div>
  <div class="tag mt-3">本产品的做法</div>
  <div class="body-text mt-1 leading-[1.75]">
    <div>· 编排用 LangGraph、接口用 Chat Completions 兼容协议、界面用 Vue 运行时、存储用 PostgreSQL</div>
    <div>· 继承的是成熟模式：状态图、事务提交、检查点恢复、幂等回执</div>
    <div>· 不继承的是形态：不复制「面向作者的复杂写作工作台」那一套功能堆叠</div>
  </div>
</div>

<div class="card-soft px-4 py-4 border-t-[3px] border-t-[#1B3B5F]">
  <div class="text-[16px] font-extrabold text-[#1B3B5F]">效益原则</div>
  <div class="text-[10.5px] text-[#6C7784] mt-1 leading-relaxed">既讲技术经济效益，也讲社会效益。</div>
  <div class="tag mt-3">本产品的做法</div>
  <div class="body-text mt-1 leading-[1.75]">
    <div>· 本地运行 + 自带 Key + 按 token 计费，生成前显示预估人民币费用</div>
    <div>· 单用户本地存档，省掉服务器与运维成本；换机器只要拷作品目录</div>
    <div>· 社会效益：降低创作门槛，作品留在作者手里，可导出、不被平台锁定</div>
  </div>
</div>

<div class="card-soft px-4 py-4 border-t-[3px] border-t-[#1B3B5F]">
  <div class="text-[16px] font-extrabold text-[#1B3B5F]">时间原则</div>
  <div class="text-[10.5px] text-[#6C7784] mt-1 leading-relaxed">加快研制节奏，并预测同类产品在开发期可能发生的变化。</div>
  <div class="tag mt-3">本产品的做法</div>
  <div class="body-text mt-1 leading-[1.75]">
    <div>· 14 天交付计划：需求冻结 → 原型联调 → 真实模型 → 对照修复 → 交付演练</div>
    <div>· 窗口期判断：通用模型记忆能力在增强，所以必须尽早用可复现对照实验证明价值</div>
    <div>· 先交付能演示的最小闭环，把「更好文笔」留给模型升级，而不是自己造</div>
  </div>
</div>

</div>

<div class="card px-4 py-3 mt-4">
  <div class="text-[11px]"><span class="font-bold text-[#1B3B5F]">一句话：</span>继承省时间，效益定取舍，时间定顺序——三者一起决定了我们的两周计划长什么样。</div>
</div>

<!-- 组三的关键词是「不做无谓功」：能继承的继承，花出去的每一分要能算回来，节奏要抢在窗口关闭前。 -->

---
layout: default
---

<div class="eyebrow">2. 产品设计应用的原则 · 组四</div>

# 能测就测，能简就简，每一步都审

<div class="hr-line"></div>

<div class="grid grid-cols-3 gap-3">

<div class="card-soft px-4 py-4 border-t-[3px] border-t-[#1B3B5F]">
  <div class="text-[16px] font-extrabold text-[#1B3B5F]">定量原则</div>
  <div class="text-[10.5px] text-[#6C7784] mt-1 leading-relaxed">在方案选择、性能评价、效益评价上尽量采用科学的定量方法。</div>
  <div class="tag mt-3">本产品的做法</div>
  <div class="body-text mt-1 leading-[1.75]">
    <div>· 成功标准写成可测指标：约 1 万字 / 8–10 章、跨章矛盾数对比基线、token 与费用、恢复成功率</div>
    <div>· 回归测试 127 项（120 通过、7 项无数据库时跳过）+ 长篇引擎 42 项</div>
    <div>· 用户测试表逐项打分，试读问卷量化「愿不愿意读完」</div>
  </div>
</div>

<div class="card-soft px-4 py-4 border-t-[3px] border-t-[#1B3B5F]">
  <div class="text-[16px] font-extrabold text-[#1B3B5F]">简化原则</div>
  <div class="text-[10.5px] text-[#6C7784] mt-1 leading-relaxed">保证功能的前提下力求简化，降低成本、保证质量。</div>
  <div class="tag mt-3">本产品的做法</div>
  <div class="body-text mt-1 leading-[1.75]">
    <div>· 后端用 Python 标准库 http.server，不额外引入 Web 框架</div>
    <div>· 前端用内置 Vue 运行时，零构建步骤；文件模式零配置即可运行</div>
    <div>· 首版只做中文 + 顺序逐章 + 单用户，把复杂度留给后续迭代</div>
  </div>
</div>

<div class="card-soft px-4 py-4 border-t-[3px] border-t-[#1B3B5F]">
  <div class="text-[16px] font-extrabold text-[#1B3B5F]">审核原则</div>
  <div class="text-[10.5px] text-[#6C7784] mt-1 leading-relaxed">随时审核每个设计步骤的信息，确保每一步正确。</div>
  <div class="tag mt-3">本产品的做法</div>
  <div class="body-text mt-1 leading-[1.75]">
    <div>· 每章一个独立审核角色：查硬矛盾、因果问题和重要记忆遗漏，只判不改</div>
    <div>· 提交前在副本上整体校验章节、计划与记忆；PR 必须由另一名成员审阅</div>
    <div>· 代码走 ruff 等质量检查，密钥与作品数据不得进入 Git</div>
  </div>
</div>

</div>

<div class="card px-4 py-3 mt-4">
  <div class="text-[11px]"><span class="tag text-[11px]">落点：</span>十二原则最终收敛成一句话——<span class="font-bold text-[#1B3B5F]">先把「记得住」做对，再把「写得好」交给模型迭代。</span></div>
</div>

<!-- 组四的关键词是「可验收」：定量给标准，简化控成本，审核保证每一步没跑偏。十二原则收束。 -->

---
layout: default
---

<div class="eyebrow">3. 产品实现</div>

# 设计与原则落到仓库里：体验、选型、架构、质量、统计

<div class="hr-line"></div>

<div class="grid grid-cols-4 gap-3 mt-2">
  <div class="card-soft px-4 py-3"><div class="tag">3.1</div><div class="text-[12.5px] font-bold mt-1">用户体验设计的因素</div></div>
  <div class="card-soft px-4 py-3"><div class="tag">3.2</div><div class="text-[12.5px] font-bold mt-1">语言 / IDE / 平台 / 框架</div></div>
  <div class="card-soft px-4 py-3"><div class="tag">3.3</div><div class="text-[12.5px] font-bold mt-1">仓库链接与提交历史</div></div>
  <div class="card-soft px-4 py-3"><div class="tag">3.4</div><div class="text-[12.5px] font-bold mt-1">全生命周期问题汇总</div></div>
  <div class="card-soft px-4 py-3"><div class="tag">3.5</div><div class="text-[12.5px] font-bold mt-1">概要设计：架构 / 数据 / 接口</div></div>
  <div class="card-soft px-4 py-3"><div class="tag">3.6</div><div class="text-[12.5px] font-bold mt-1">软件质量：方法 / 工具 / 整改</div></div>
  <div class="card-soft px-4 py-3"><div class="tag">3.7</div><div class="text-[12.5px] font-bold mt-1">代码统计：模块 / 行数 / AI 占比</div></div>
  <div class="card-soft px-4 py-3"><div class="tag">仓库</div><div class="mono text-[10px] mt-1 leading-relaxed">github.com/liuliyisui/tome-agent</div></div>
</div>

<!-- 第 3 部分：从设计走到仓库。七个小节对应任务书的 3.1–3.7，每页底部标注交付证据的来源。 -->

---
layout: default
---

<div class="eyebrow">3.0 本部分覆盖的考核要点</div>

# 每条要求对应的交付证据

<div class="hr-line"></div>

| 课程要求（对应任务书 3. 产品实现） | 交付证据 |
| --- | --- |
| 3.1 用户体验设计考虑的因素 | 六项体验因素，含失败可见性 |
| 3.2 编程语言 / IDE / 平台 / 框架（含版本号） | 版本表 + 选型原因（已写入 README） |
| 3.3 代码仓库链接与提交历史 | 仓库地址、每人提交次数、看板与缺陷追踪 |
| 3.4 全生命周期问题与解决方法汇总 | 六类问题表 + 仓库内 `docs/software/ISSUES_SUMMARY.md` |
| 3.5.1 系统架构图 | 自底向上四层架构（界面 / 服务 / 引擎 / 存储） |
| 3.5.2 基础设施图 | 单机本地部署形态（从架构图说明理由） |
| 3.5.3 智能体技术设计 | 任务编排状态图、事件先行与三层记忆、护栏、写作 Skill 知识库、参考文献 |
| 3.5.4 数据库设计 | 由 `schema.sql` 逆向生成的 E-R 图与设计要点 |
| 3.5.5 接口设计 | 真实 HTTP 路由表（取自 `web.py`）与方法描述 |
| 3.5.6 前端设计 | 渐进式 Vue 3 方案与原型边界说明 |
| 3.6 软件质量（3.6.1 / 3.6.2） | 日志与异常处理、Ruff 规则集与整改结果、CI 四类 job |
| 3.7 代码统计 | 模块数、分语言行数、AI 辅助编写比例口径 |

<div class="mt-3 text-[9.5px]" style="color:#8A8072">参考文档要求「引用的相关开源代码、文献需要给出来源」：本部分每页标注来源，最后一页列出完整清单。</div>

<!-- 索引页：让评委能直接对着任务书勾。 -->

---
layout: default
---

<div class="eyebrow">3.1 用户体验设计考虑的因素</div>

# 从「能跑起来」到「敢让作者一直用下去」

<div class="hr-line"></div>

<div class="grid grid-cols-3 gap-3">

<div class="card-soft p-4">
  <div class="num text-[15px]">01</div>
  <div class="text-[12.5px] font-bold mt-1">本地即用，零部署门槛</div>
  <div class="body-text mt-2">浏览器打开 <span class="mono">127.0.0.1:8765</span> 即进入工作室；本机单用户定位，无需注册、无需公网服务。</div>
</div>

<div class="card-soft p-4">
  <div class="num text-[15px]">02</div>
  <div class="text-[12.5px] font-bold mt-1">进度可续，不丢半成品</div>
  <div class="body-text mt-2">每个阶段保存检查点，中断后可恢复；保留已完成章节与待处理任务队列。</div>
</div>

<div class="card-soft p-4">
  <div class="num text-[15px]">03</div>
  <div class="text-[12.5px] font-bold mt-1">费用可见，调用前确认</div>
  <div class="body-text mt-2">生成前给出费用预估并由用户确认；记录 token 与用量；API 密钥仅存本机 <span class="mono">.env</span>，不回传网页。</div>
</div>

<div class="card-soft p-4">
  <div class="num text-[15px]">04</div>
  <div class="text-[12.5px] font-bold mt-1">失败可见，降级保正文</div>
  <div class="body-text mt-2">超时、响应截断、坏 JSON 等错误对用户可见；局部规划或记忆处理失败时记录问题并保留有效正文。</div>
</div>

<div class="card-soft p-4">
  <div class="num text-[15px]">05</div>
  <div class="text-[12.5px] font-bold mt-1">创作流程可控</div>
  <div class="body-text mt-2">创建作品、配置文风、逐章或批量生成、导出排版后的 Markdown；章节可按作者反馈重新生成。</div>
</div>

<div class="card-soft p-4">
  <div class="num text-[15px]">06</div>
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
| 前端语言 | HTML / CSS / JavaScript | 浏览器原生 | 原生技术实现本地工作室，降低构建与部署复杂度 |
| Web 服务 | Python 标准库 `http.server` | 随 Python 版本 | 为本地单用户提供 HTTP 接口，避免再叠一层 Web 框架 |
| 数据库（可选） | PostgreSQL + Psycopg | PG 17（CI 覆盖 17/18）；Psycopg 3.3.3 | 持久化作品、章节与任务；未配置时降级为文件模式 |
| 模型服务 | DeepSeek / OpenAI 兼容接口 | Chat Completions | 沿用已接入接口，复用配置、计费预估与故障测试逻辑 |
| 开发工具 | VS Code 等 Python 编辑器 | 未锁定 | 编辑调试；Ruff + Pylance 方案 A，规则集中在仓库配置文件 |

<div class="card px-4 py-3 mt-4">
  <div class="text-[11px]"><span class="tag text-[11px]">选型原则：</span>「不要太重，也不要太轻」——不引入 ASGI 框架与前端构建链，把复杂度放在智能体编排与状态一致性上；代价是接口验证、错误转换与线程管理由项目自行维护。同一张表已写入仓库 <span class="mono">README.md</span>「技术选型」。</div>
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
    <div class="mono text-[11px] mt-1">https://github.com/liuliyisui/tome-agent</div>
    <div class="small mt-2">提交历史：仓库页 Pulse → Insights → Pulse</div>
  </div>
  <div class="card-soft px-4 py-3 mt-3">
    <div class="tag">看板与缺陷追踪</div>
    <div class="small mt-1 leading-[1.8]">任务与缺陷以 GitHub Issues 为正式记录，看板见 <span class="mono">docs/mgmt/KANBAN.md</span>（Issue #1–#6）；分工与分支策略见 <span class="mono">TEAM_PLAN.md</span>，路线图见 <span class="mono">ROADMAP.md</span>，风险与沟通见 <span class="mono">COMMUNICATION_AND_RISK_PLAN.md</span>。</div>
  </div>
</div>

<div>
  <div class="tag">每位成员的提交次数</div>
  <div class="text-[10px] mt-1 mb-2" style="color:#8A8072">由 GitHub API <span class="mono">/contributors</span> 统计（截至本次汇报）</div>
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
| 分析 | 需求边界反复 | 长篇创作需求含糊，演示原型与真实生成混为一谈 | 区分 <span class="mono">docs/software/prototype</span>（模拟数据）与正式服务，原型不作为真实生成证据 |
| 设计 | 编排框架迁移 | LangGraph 迁移可能破坏已验证的领域逻辑 | 节点内复用既有模型适配、事件推演与记忆函数，控制迁移范围 |
| 开发 | 模型调用失败 | 网络超时、响应截断、坏 JSON | 记录错误与用量；失败降级，保留已完成正文并区分「请求失败 / 可能已计费 / 内容未审核」 |
| 开发 | 长篇生成中断 | 一次成稿需多次模型调用，耗时长 | 每阶段保存原子检查点，识别待处理任务与损坏检查点 |
| 测试 | 文件与数据库双写 | 数据库记录与文件检查点并非原子事务 | 故障演练确认恢复行为，明确列出未覆盖边界，不过度承诺 |
| 部署运维 | 旧版本无法续写 | 旧检查点运行时哈希与新版本源码不一致 | 禁止手改哈希绕过；升级前保留旧代码与作品 |

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">存储位置：本表已以 Markdown 存入项目仓库 <span class="mono">docs/software/ISSUES_SUMMARY.md</span>。来源：architecture.md、CODE_QUALITY_FIXES.md、retrospection/README.md。</div>

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
  <div class="body-text mt-2 leading-[1.7]">Python HTTP 服务<br><span class="mono">127.0.0.1:8765</span><br>WritingSession 会话入口</div>
</div>

<div class="flex items-center text-[14px]" style="color:#A99C88">→</div>

<div class="card-soft px-3 py-4 flex-1">
  <div class="tag">界面层</div>
  <div class="body-text mt-2 leading-[1.7]">正式 Vue 3 页面 <span class="mono">code/frontend</span><br>书架 / 文风 / 费用确认 / 生成 / 导出</div>
</div>

</div>

<div class="grid grid-cols-[1fr_1fr] gap-4 mt-4">
  <div class="card px-4 py-3">
    <div class="tag">模型服务（服务层旁路调用）</div>
    <div class="small mt-1 leading-[1.7]">DeepSeek / OpenAI 兼容接口；<span class="mono">chat_provider</span> 封装请求、超时与用量。</div>
  </div>
  <div class="card px-4 py-3">
    <div class="tag">依赖方向</div>
    <div class="small mt-1 leading-[1.7]">界面 → 服务 → 引擎 → 存储；引擎不感知界面与传输层，便于替换与测试。</div>
  </div>
</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">图源：<span class="mono">docs/software/architecture.md</span>、<span class="mono">docs/algorithm/LANGGRAPH.mmd</span>、<span class="mono">code/backend/inf_backend/</span>、<span class="mono">code/core_engine/memory_runtime/</span>。</div>

<!-- 四层架构：存储→引擎→服务→界面，模型服务旁路。 -->

---
layout: default
---

<div class="eyebrow">3.5.2 基础设施图</div>

# 部署形态：单机本地

<div class="hr-line"></div>

<div class="grid grid-cols-3 gap-3">

<div class="card-soft p-4">
  <div class="tag">本地单机</div>
  <div class="body-text mt-2">本机单用户工作室定位，不以公网多租户服务为设计目标；无多节点、无负载均衡，故按参考文档「只有一台服务器可不画」从略。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">存储可切换</div>
  <div class="body-text mt-2">默认文件模式：作品存于 <span class="mono">code/backend/data/inf_books/</span>；配置 <span class="mono">DATABASE_URL</span> 后切换 PostgreSQL，引擎检查点仍留在本地文件。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">启动方式</div>
  <div class="body-text mt-2">Windows：<span class="mono">setup.cmd</span> + <span class="mono">run-web.cmd</span>；另提供便携版与 Linux 托管部署说明（DEPLOY.md、WINDOWS_PORTABLE.md、LINUX_HOSTED.md）。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">容器与 CI</div>
  <div class="body-text mt-2">Compose 文件描述本地 PostgreSQL 服务、健康检查与数据卷；GitHub Actions 覆盖 PostgreSQL 17/18 版本矩阵与托管 Linux 运行。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">运行时版本</div>
  <div class="body-text mt-2">Python 3.11+（CI 固定 3.11）；依赖锁定 <span class="mono">requirements.txt</span>：psycopg[binary]==3.3.3、langgraph==1.2.17。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">密钥与数据</div>
  <div class="body-text mt-2">模型密钥写入本机 <span class="mono">.env</span>，不提交 Git；<span class="mono">.env.example</span> 为配置模板，作品数据与技能文件留在本机目录。</div>
</div>

</div>

<!-- 单机本地：为什么没有基础设施图（只有一台机器），以及存储/启动/密钥怎么放。 -->

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

<div class="text-[9.5px] mt-2" style="color:#8A8072">event_writer → event_planner 之间存在 <span class="mono">revise</span> 修订回边；coordinator 亦由审核条件边选择提交或拒绝。</div>

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

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">图源：<span class="mono">docs/algorithm/LANGGRAPH.mmd</span>（Mermaid 源文件，节点名与边标签与源码一致）。</div>

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
  <div class="text-[10px] leading-[1.8]"><span class="tag text-[10px]">开源框架与官方文档：</span><span class="mono">langchain.com/oss/python/langgraph</span> · DeepSeek API 文档 · PostgreSQL 事务 · Psycopg 3 事务管理 · Vue 渲染函数 · Python <span class="mono">http.server</span> · Docker Compose 文档 · GitHub Actions Python CI 指南。</div>
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
  <div class="small mono mt-1 leading-[1.7]">id (PK) · metadata jsonb · state jsonb · state_kind (snapshot/longform) · style jsonb · checkpoint · last_usage jsonb · pinned · deleted_at / restore_token</div>
</div>

<div class="grid grid-cols-3 gap-3 mt-3">

<div class="card-soft p-3">
  <div class="tag">tome_chapters 章节（1:N）</div>
  <div class="small mono mt-1 leading-[1.7]">book_id, number (PK, FK)<br>title · body · version</div>
</div>

<div class="card-soft p-3">
  <div class="tag">tome_jobs 生成任务（1:N）</div>
  <div class="small mono mt-1 leading-[1.7]">id (PK) · book_id (FK)<br>status(running/completed/failed/interrupted) · payload jsonb</div>
</div>

<div class="card-soft p-3">
  <div class="tag">tome_usage 用量记录</div>
  <div class="small mono mt-1 leading-[1.7]">book_id, checkpoint (PK)<br>payload jsonb · saved_at</div>
</div>

<div class="card-soft p-3">
  <div class="tag">tome_chapter_versions 章节版本</div>
  <div class="small mono mt-1 leading-[1.7]">book_id, number, version (PK)<br>title · body · created_at</div>
</div>

<div class="card-soft p-3">
  <div class="tag">tome_schema_version 结构版本</div>
  <div class="small mono mt-1 leading-[1.7]">version (PK) · applied_at<br>3 个索引 + 1 个唯一索引</div>
</div>

<div class="card px-3 py-2">
  <div class="tag">设计要点</div>
  <div class="small mt-1 leading-[1.7]">JSONB 承载结构化状态；回收站用 <span class="mono">deleted_at</span> + <span class="mono">restore_token</span> 实现软删除与恢复；未配置数据库时降级为文件模式。</div>
</div>

</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">来源：<span class="mono">code/backend/inf_backend/schema.sql</span>（6 张表 + 3 索引 + 1 唯一索引）逆生成；Mermaid 原始图见 <span class="mono">docs/algorithm/ER.mmd</span>。</div>

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
| `/api/model-test` | POST | 模型连通性与能力测试 | 测试结果 / 错误信息 |
| `/api/skills` | GET / POST | 列出与安装写作 Skill | 技能列表 |
| `/api/config` | GET / POST | 读取与保存默认设置 | 配置对象 |
| `/api/books` | GET / POST | 书架列表 / 新建作品 | 作品列表 / 作品 id |
| `/api/books/{id}/generate` | POST | 触发生成任务 | 任务对象（HTTP 202） |
| `/api/books/{id}/estimate` | POST | 生成前费用预估 | 预估费用 |
| `/api/books/{id}/chapters/{n}/regenerate` | POST | 按作者反馈重写章节 | 任务对象 |
| `/api/books/{id}/style` | POST | 保存文风（次章生效） | 文风对象 |
| `/api/books/trash` `/restore` `/trash/purge` | GET / POST | 废案箱、恢复与彻底删除 | 列表 / 操作结果 |
| `/api/books/{id}/export` | GET | 导出排版后的 Markdown | Markdown 文件 |
| `/api/jobs/{id}` | GET | 查询生成任务进度 | 状态与进度 |

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">来源：<span class="mono">code/backend/inf_backend/web.py</span>（do_GET / do_POST 路由分派）与 <span class="mono">service.py</span>；异常统一转为 JSON 错误响应，生成任务返回 202 表示已受理。完整参数见 Swagger / APIFox。</div>

<!-- 接口：12 行路由，覆盖模型配置、技能、作品、章节、任务、导出。 -->

---
layout: default
---

<div class="eyebrow">3.5.6 前端设计</div>

# 前端：渐进式 Vue 3 与本地资源

<div class="hr-line"></div>

<div class="grid grid-cols-2 gap-3">

<div class="card-soft p-4">
  <div class="tag">正式界面（code/frontend）</div>
  <div class="body-text mt-2">HTML / CSS / JavaScript 原生页面，由 Vue 3.5.44 渐进管理交互；采用仓库内置 runtime-only 运行时与 <span class="mono">h()</span> 渲染函数，无前端构建步骤、不依赖 CDN；响应式组件覆盖书架、废案箱、文风保存、删除恢复、费用确认与取消；生成任务在后台线程执行，页面轮询任务状态展示进度。</div>
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
  <div class="body-text mt-2">界面动作与用户故事一一对应：创建作品、配置文风、确认费用、逐章生成、失败恢复、导出 Markdown（见 <span class="mono">docs/requirements/user_stories.md</span>），使 8 分钟演示可按故事线顺序进行。</div>
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
  <div class="body-text mt-2"><b>Ruff 0.17.4</b>（Linter + Formatter 二合一，覆盖 PEP 8 风格与语义规则）：规则集 E、W、F、I、B、C4、UP，ignore = ["E501"]，line-length = 88，target-version = "py311"；规则集中于 <span class="mono">code/backend/pyproject.toml</span>，编辑器、预提交与 CI 共用同一份配置。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">整改结果（有据可查）</div>
  <div class="body-text mt-2">整改前基线 <b>75 处不合规</b>（E402 42、B023 14、B904 12、B007 3、F841 3、E731 1、I001 36）；整改后 <b>0 处</b>，<span class="mono">ruff format</span> 全仓库无差异；改动 44 个 <span class="mono">.py</span> 文件（+240 / −194 行）。详见 <span class="mono">docs/software/CODE_QUALITY_FIXES.md</span>。</div>
</div>

<div class="card-soft p-4">
  <div class="tag">自动化与佐证</div>
  <div class="body-text mt-2"><b>预提交钩子</b>：ruff-pre-commit v0.17.4（ruff --fix、ruff-format）+ pre-commit-hooks v4.6.0（check-toml、check-yaml、end-of-file-fixer、trailing-whitespace）。<br><b>CI</b>：<span class="mono">.github/workflows/tests.yml</span> 含 lint、Windows 测试、postgresql（17/18 矩阵）、hosted-linux 四类 job。<br><b>代码复杂度</b>：可继续用 VS Code 插件（complexipy / Pylint）补测，当前以 Ruff 规则与测试覆盖为主要证据。</div>
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
  <div class="small mt-2">统计口径：本地克隆快照逐文件累计（.py / .js / .html / .css），提交 <span class="mono">0759e38</span>；正式答辩请用 VS Code Counter 插件重跑并附截图。</div>
</div>

<div>
  <div class="card-soft px-4 py-3">
    <div class="tag">AI Vibe Coding 与团队自写代码比例</div>
    <div class="body-text mt-1">仓库未提供官方比例数据，需按统一口径统计后填入：建议按「提交作者 + 提交说明 + 是否 AI 生成」三要素归类，输出 AI 辅助生成行数 / 总行数比值，并注明统计工具（如 <span class="mono">git log --numstat</span> 结合人工抽查）。</div>
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
    <div>· 仓库：<span class="mono">github.com/liuliyisui/tome-agent</span> — README「技术选型」「核心功能」「验证与使用说明」</div>
    <div>· <span class="mono">docs/software/architecture.md</span>、<span class="mono">docs/algorithm/LANGGRAPH.mmd</span></div>
    <div>· <span class="mono">docs/software/code_quality.md</span>、<span class="mono">CODE_QUALITY_FIXES.md</span></div>
    <div>· <span class="mono">docs/software/DEPLOY.md</span>、<span class="mono">WINDOWS_PORTABLE.md</span>、<span class="mono">LINUX_HOSTED.md</span>、<span class="mono">POSTGRESQL.md</span></div>
    <div>· <span class="mono">code/backend/inf_backend/schema.sql</span>、<span class="mono">web.py</span> / <span class="mono">service.py</span></div>
    <div>· <span class="mono">docs/mgmt/KANBAN.md</span>、<span class="mono">TEAM_PLAN.md</span>、<span class="mono">ROADMAP.md</span>、<span class="mono">COMMUNICATION_AND_RISK_PLAN.md</span></div>
  </div>
</div>

<div class="card-dk px-5 py-5 flex flex-col justify-center">
  <div class="text-[22px] font-extrabold">谢谢观看 · 欢迎提问</div>
  <div class="text-[11px] mt-3 leading-[1.9]" style="color:#E8E0D2">第一部分 1、2、3 三节合并完成：<br>产品设计（1.1–1.2）· 十二条设计原则（2）· 产品实现（3.1–3.7）</div>
</div>

</div>

<!-- 收尾：来源清单 + 谢谢。 -->
