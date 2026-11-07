# LangGraph 迁移 · 2026-10-24

当前版本：`langgraph-20261024`，固定依赖 `langgraph==1.2.17`，Python 3.11。

## 决策与范围

用户明确选择把现有编排改用 LangGraph，以满足课程使用现有框架的要求。迁移仅修改本地项目代码、依赖、相关测试和说明；不推送 GitHub，不改数据库，不调用付费模型，不修改已有小说正文。

选择 LangGraph 作为编排层，继续复用原有 DeepSeek 模型适配、事件推演、三层记忆、证据检查与原子提交。可行替代是保留原有自定义编排，但不符合本次已选定的框架方向。若依赖安装、事务回滚或已有入口回归失败，则应停止采用新版并用迁移前备份恢复代码，不能以只添加依赖冒充完成迁移。

## 实际变更

| 入口 | 迁移后执行方式 |
| --- | --- |
| 网页长篇生成 | service → WritingSession → 编译后的 StateGraph |
| 命令行长篇生成 | write_novel → user_runtime → WritingSession → StateGraph |
| 基础严格四角色事务 | Coordinator → StateGraph，审核条件分支选择提交或拒绝 |
| 已有章节的待处理任务 | WritingSession.finish_pending → 图的恢复入口 → memory → reviewer |

`memory_runtime/graph_runtime.py` 定义真实图节点与条件边；`writing.py` 保留领域逻辑，并将规划、写作和章节提交拆成对应方法。不是把整个原循环包成单个图节点。`inf_writer/runtime.py` 与 `memory_runtime/src/inf_writer/runtime.py` 同时迁移，避免不同入口导入不同编排框架。

重规划通过图的条件边执行，仍有一次修订上限。模型输出格式修复、事件阶段处理、记忆顺序队列等局部逻辑留在节点内部。三层记忆是项目已有的领域能力，并非 LangGraph 自动理解了小说。

## 安装与运行

网页后端继续运行 `code/backend/setup.cmd` 安装依赖；已有环境应重新安装：

```powershell
code\backend\.venv\Scripts\python.exe -m pip install -r code\backend\requirements.txt
```

单独使用核心命令行时，在使用的 Python 环境安装：

```powershell
python -m pip install -r code\core_engine\requirements.txt
```

模型配置和前端操作保持原接口。没有引入必须注册的 LangSmith 服务，也没有自动配置远程追踪。

## 保存、恢复与兼容性

- 正文和状态继续写入应用原有的原子检查点，图没有第二套持久化数据库。
- 检查点额外记录 `orchestration: langgraph`，运行时指纹包含 LangGraph 版本和源码哈希。
- 中断后，新版继续用 `load_resume()` 恢复已经保存的事件阶段、正文和待处理任务；不会为了恢复而重复生成已完成的阶段。
- 迁移前检查点因源码或依赖指纹不同，被显式拒绝直接续写。原文件不被修改，没有自动替换哈希或绕过检查。若需继续旧作品，应使用原版代码，或另做显式存档迁移。
- 本次未接入 LangGraph 原生 checkpointer、任意节点级重放或人工 `interrupt()` 暂停。不要将框架提供的功能描述为已经接入的产品能力。
- 事件先行模式继续沿用原有的正文审核关闭策略；传统模式的审核保持原策略。此迁移不等于修复了人物复活、叙述重复等内容质量问题。

## 验证

从项目根目录，在已安装依赖的环境运行：

```powershell
$env:PYTHONPATH="$PWD\code\core_engine;$PWD\code\backend"
python -m unittest discover -s tests -v
python tests\run_engine_regression.py
```

应用回归共 112 项：105 项通过，7 项因没有配置真实 PostgreSQL 而跳过。新增 8 项 LangGraph 专项测试覆盖真实图执行、重规划回边、记忆失败保留草稿、中断后复用已准备事件、待处理任务专用入口、原子保存失败回滚、运行时不匹配拒绝恢复，以及严格审核拒绝分支。

长篇入口回归共 42 项：39 项通过，3 项明确因历史运行资产缺失而跳过。包括连续 25 章的离线故障注入夹具、分阶段正文恢复、规划修复、记忆及审核服务故障、检查点完整性校验。离线夹具验证控制流程，不证明真实模型的文笔或一致性。

本次未运行真实 PostgreSQL 集成，也未调用真实 DeepSeek；并发负载、部署恢复和真实长篇质量均未测。迁移前的 `stable_release_manifest.json` 与历史真实作品记录保持原样，不作为新版运行证据。当前代码哈希记录在 `code/core_engine/langgraph_release_manifest.json`。

## 回滚

实施时将被修改的原有文件逐字节备份在项目旁的 `langgraph-migration-backup/`，`before.json` 保存原始 SHA-256。该本机备份不进入发布包。

需要回滚时先备份新版工作和作品，再只恢复该备份清单中的原文件，移除本次新增的图模块、专用依赖文件和专项测试，并使用原版依赖环境。不要对原本已有大量改动的仓库执行整体 reset。新版检查点也不能交给旧版引擎直接续写。回滚后应重新运行原应用回归，恢复其他文件不构成验证。

## 官方依据

- [LangGraph 概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [StateGraph、节点和条件边](https://docs.langchain.com/oss/python/langgraph/graph-api)

图的定义与编译由官方 LangGraph 库执行；本项目继续负责小说领域规则与存档完整性。
