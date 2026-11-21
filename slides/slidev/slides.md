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

<div class="mt-4 text-[11.5px] leading-[1.9] text-[#3B4959]">
  <div class="font-bold text-[#1D2B3A] mb-1">使命同时划掉两件事：</div>
  <div class="text-[#6C7784]">× 不做「一键生成爆款」的流量工具——它奖励套路，不奖励自洽；　× 这一版也不做「作者量产」的效率工具——那是另一群用户、另一套需求。</div>
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

<div class="card-soft px-4 py-3 mt-6">
  <div class="text-[11.5px] leading-[1.8]"><span class="tag text-[11px]">口号纪律：</span>只承诺能验证的三件事——自洽（矛盾可查）、可恢复（失败能续）、可导出（作品归你）；不使用「最强」「超越」「一键成神」这类无法证伪的词。</div>
</div>

<div class="absolute left-[52px] bottom-[18px] text-[9px] text-[#A99C88]">口号出现在：封面、工作台首屏、演示结尾、仓库 README 第一行</div>

<!-- 主口号给用户，副口号给我们自己：先把记得住做对。口号纪律是不用无法证伪的词。 -->

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

<div class="px-4 py-3 mt-4 rounded-[10px] bg-[#F7ECE8]">
  <div class="text-[11.5px]"><span class="tag text-[11px]">自曝一条风险：</span>成员开发经验有差距，核心框架集中在一人。对策：任务拆小、关键操作结对、改公共接口前先通知、交叉复核不省略。</div>
</div>

<!-- 四个人是一条链：开发、创作评估、测试、体验文档，每项交付都有第二个人复核。风险也说了：经验差距、核心集中在一人。 -->

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

<div class="mt-4 text-[10.5px] text-[#6C7784]"><span class="font-bold text-[#1B3B5F]">自检：</span>把这段念给一个没看过代码的人，他能复述出「给谁、解决什么、哪里不一样」，定义才算过。</div>

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
  <div class="mt-4">
    <div class="tag">一条诚实说明</div>
    <div class="small mt-1">「状态记忆能减少跨章矛盾」目前是待验证假设：要用同输入、同模型、有 / 无记忆的对照实验来证明，在跑完对照前不把它当结论。</div>
  </div>
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

<div class="mt-4 text-[10.5px] leading-[1.8] text-[#6C7784]"><span class="tag text-[10.5px]">写法纪律：</span>用用户的业务语言，不出现「向量」「检查点」「JSON 契约」；每条故事配 Gherkin 验收条件，见 <span class="mono">docs/requirements/user_stories.md</span>（按 INVEST 拆分，共 5 条）。</div>

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
