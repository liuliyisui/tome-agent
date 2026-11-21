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

<!-- 开场：我们做的是 Tome Agent，一个部署在云服务器上的长篇小说生成助手。这 8 分钟我负责第一部分：它是什么，以及为什么这么设计。 -->

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

<div class="card px-6 py-5">
  <div class="text-[14px] font-bold leading-[1.75]"><span style="color:#B4472E">使命：</span>把「创作一部长篇」的门槛，从「会不会写」降到「说不说得清一个想法」；把「记得住」交给系统，而不是交给更长的提示词。</div>
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
  <div class="body-text mt-2">作品存在账号空间，随时可导出 Markdown；数据可迁移、服务端定期备份，不锁定平台。</div>
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
  <div class="body-text mt-1">专业作者的量产工具（AI 文笔还撑不起量产质量）｜ 多人协作团队 ｜ 移动端 App 与多人协作编辑（在线账号已支持）</div>
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

<div class="card px-4 py-3 mt-4 flex items-center">
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
  <div class="small mt-3"><span class="font-bold text-[#1B3B5F]">看板指标：</span>站点访问 → 注册转化率</div>
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
| 成本与归属 | 订阅 | 订阅 + 云端 | 平台内阅读 | 云端托管、自带 Key、作品可导出 |

<div class="card px-5 py-3 mt-4">
  <div class="text-[11.5px]"><span class="tag text-[11px]"><span style="color:#B4472E">一句话差异化：</span></span>通用 AI 卖「会写」，写作工具卖「作者的效率」，Tome Agent 卖「读者零门槛写出一部自洽的长篇」。</div>
</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">竞品信息：公开产品页与第三方横评（2026-04），属市场观察，不是严格测评。</div>

<!-- 差异化四层：面向读者而非作者、事实级记忆而非摘要、提交是事务而非覆盖、数据可迁移。最后一列只承诺验证过的篇幅。 -->

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
  <div class="text-[12.5px]">部署在云服务器上的长篇小说生成助手</div>
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
  <div class="card px-5 py-4">
    <div class="tag">根因判断</div>
    <div class="text-[16px] font-extrabold mt-2 leading-snug">「记忆能力」≠「上下文长度」</div>
    <div class="text-[11px] mt-3 leading-[1.75] text-[#6C7784]">模型不是不想记。是「把前文再喂一遍」这种记忆方式，撑不起一部书——越往后越贵、越模糊。</div>
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

# 形态选「云端 Web 服务」：浏览器访问域名，登录账号即可写作

<div class="hr-line"></div>

<div class="text-[11.5px] leading-[1.7]"><span class="tag text-[11px]">为什么是云端 Web 服务，不是小程序 / App：</span>用户不必安装客户端，浏览器打开域名即可用；服务端统一升级、备份与限流；账号体系隔离各自作品；成本按 token 透明计费，不需要应用商店上架审核。</div>

<div class="grid grid-cols-[1.05fr_1fr] gap-5 mt-6">

<div>
  <div class="tag">技术组成（版本见 README）</div>
  <div class="mt-2 space-y-[7px]">
    <div class="grid grid-cols-[52px_1fr] gap-2 items-baseline"><div class="text-[11px] font-bold text-[#1B3B5F]">界面</div><div class="small">Vue 3.5.44 内置运行时，无前端构建；服务端 <span class="mono">127.0.0.1:8765</span> 经 Nginx 443 对外</div></div>
    <div class="grid grid-cols-[52px_1fr] gap-2 items-baseline"><div class="text-[11px] font-bold text-[#1B3B5F]">编排</div><div class="small">LangGraph 1.2.17 把五个阶段建成状态图，支持条件分支与重规划</div></div>
    <div class="grid grid-cols-[52px_1fr] gap-2 items-baseline"><div class="text-[11px] font-bold text-[#1B3B5F]">存储</div><div class="small">默认文件存储，零外部依赖；需要时切 PostgreSQL 17 + Psycopg 3.3.3</div></div>
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

<div class="card px-5 py-3 mt-4">
  <div class="text-[11.5px]">一次生成 = 「规划 → 写作 → 记忆 → 审核 → 提交」；服务端托管、作品存于账号空间、按 token 透明计费。</div>
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
    <div>· 先冻结 MVP：单用户账号、中文、顺序逐章；多人协作 / 移动端 / 自动出版明确不做</div>
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
    <div>· 单台云服务器托管，用户各自配置模型 Key，按 token 计费；生成前显示预估人民币费用</div>
    <div>· 一台机器 + 进程池即可服务多用户（上限可调），省掉集群与运维复杂度；数据目录可整体备份迁移</div>
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
| 3.5.2 基础设施图 | 云服务器部署拓扑（Nginx + systemd + HTTPS） |
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
    <thead><tr><th>模块</th><th>文件数</th><th>行数</th></tr></thead>
    <tbody>
      <tr><td>code/core_engine（Python，写作与记忆引擎）</td><td>105</td><td>35,359</td></tr>
      <tr><td>code/backend（Python，后端服务）</td><td>24</td><td>5,270</td></tr>
      <tr><td>tests（Python，单元 + 集成）</td><td>43</td><td>6,671</td></tr>
      <tr><td>code/frontend（JS / HTML / CSS）</td><td>5</td><td>4,996</td></tr>
      <tr><td>合计</td><td>177</td><td>52,296</td></tr>
    </tbody>
  </table>
  <div class="small mt-2">统计口径：git 跟踪的 code/ 与 tests/ 下 .py / .js / .html / .css 的代码行（不含注释与空行；另含注释 414 行、空行 3,779 行），提交 2431b7c；答辩前用 VS Code Counter 重跑并附截图。</div>
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

<div class="card px-5 py-5 flex flex-col justify-center">
  <div class="text-[22px] font-extrabold">谢谢观看 · 欢迎提问</div>
  <div class="text-[11px] mt-3 leading-[1.9]" style="color:#6C7784">第一部分 1、2、3 三节合并完成：<br>产品设计（1.1–1.2）· 十二条设计原则（2）· 产品实现（3.1–3.7）</div>
</div>

</div>

<!-- 收尾：来源清单 + 谢谢。 -->
