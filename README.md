# Tome Agent

Tome Agent 是一个面向长篇小说生成的软件创新作业。核心代码基于 F 盘 INF Writer 的 `transfer_and_closure_20261028` 版本，并保留章节标题清理修改，后端默认使用事件先行和三层记忆流程。

上游记录的真实写作完成 18 章、33800 汉字，期间经历余额不足后恢复和规划重试；后续收束修复仅经独立调用验证，未重新从头生成整部作品。仍存在节奏和篇幅控制等问题。[此前版本记录](docs/software/ENGINE_UPDATE_20261024.md)仅供历史参考。

## 当前能力

- 事件先行：先规划场景事件并推演状态，再生成正文，避免正文先写完后再猜关键事实。
- 三层记忆：工作记忆、近期记忆和长期记忆分别保存，并保留正文来源。
- 连续性管理：跟踪人物、物品、时间、任务、知识来源和状态版本。
- 断点恢复：每个阶段保存检查点，失败时保留已经完成的章节和待处理任务。
- 长度控制：根据总字数、剩余章节和实际进度动态分配章节篇幅。
- 失败降级：局部规划或记忆处理失败时记录问题，尽量继续保存有效正文。
- DeepSeek 接入：使用 Python 标准库访问官方 Chat Completions 接口。
- 本地网页：创建作品、配置文风、确认费用后逐章或批量生成，支持导出排版后的 Markdown。

图形前端位于 `code/frontend/`，使用 HTML、CSS、JavaScript，并包含本地 Vue 运行时及交互组件。

## 目录

```text
.github/               GitHub 工作流和 Issue 模板
code/backend/          DeepSeek 配置、应用服务、启动脚本和本地作品数据
code/core_engine/      稳定长文本核心、三层记忆、检查点和发布清单
code/frontend/         本地网页工作室
docs/                  需求、设计、管理和使用文档
tests/                 单元测试与集成测试
```

仓库根目录只保留 `README.md` 和以上四个项目目录；`.git` 是 Git 自身的隐藏元数据。

## 快速验证（Windows）

```powershell
code\backend\setup.cmd
code\backend\run-web.cmd
```

打开 http://127.0.0.1:8765。生成正文前，在 `code/backend/.env` 配置 DeepSeek API 密钥。作品存放于 `code/backend/data/inf_books/`。运行自动测试：

```powershell
$env:PYTHONPATH="$PWD\code\core_engine;$PWD\code\backend"
code\backend\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

真实模型配置写入 `code/backend/.env`，该文件不会提交到 Git。配置模板见 `code/backend/.env.example`。

## 当前边界

本次通过 103 项应用回归。部分上游引擎测试依赖未包含在仓库中的历史运行数据，未能通过；未重新调用真实模型生成长篇作品。发布清单记录上游版本，合入的标题修正使部分文件与清单哈希不同。升级前请保留旧代码与作品：旧检查点的运行时哈希与新版不一致，不能直接续写。

模型生成仍可能出现情节质量、文风和事实判断问题。系统保存的结构化状态与模型审核结果都应视为辅助信息，最终作品仍需人工检查。

