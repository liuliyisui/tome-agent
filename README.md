# Tome Agent

Tome Agent 是一个面向长篇小说生成的软件创新作业，使用 LangGraph 编排。

## 当前能力

- LangGraph 编排：规划、写作、提交、记忆处理和审核为独立节点，写作请求修订时通过条件边返回规划节点。
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
code/core_engine/      LangGraph 长文本编排、三层记忆、检查点和发布清单
code/frontend/         本地网页工作室
docs/                  需求、设计、管理和使用文档
tests/                 单元测试与集成测试
```


## 快速验证（Windows）

数据库采用 PostgreSQL。首次使用请按 [本机数据库启动与迁移说明](docs/software/POSTGRESQL.md) 配置本地数据库、初始化表并导入旧作品；现有 .env 需要补充 DATABASE_URL。引擎检查点继续保留在本地文件中。

```powershell
code\backend\setup.cmd
# 按数据库说明填写 code/backend/.env
code\backend\run-db.cmd
code\backend\migrate-db.cmd init
code\backend\run-web.cmd
```

打开 http://127.0.0.1:8765。生成正文前，在 `code/backend/.env` 配置 DeepSeek API 密钥。作品存放于 `code/backend/data/inf_books/`。运行自动测试：

```powershell
$env:PYTHONPATH="$PWD\code\core_engine;$PWD\code\backend"
code\backend\.venv\Scripts\python.exe -m unittest discover -s tests -v
code\backend\.venv\Scripts\python.exe tests\run_engine_regression.py
```

真实模型配置写入 `code/backend/.env`，该文件不会提交到 Git。配置模板见 `code/backend/.env.example`。

## 当前边界

合并版本的应用回归运行 127 项，通过 120 项，7 项因未配置 PostgreSQL 跳过；长篇引擎回归运行 42 项，通过 39 项，3 项因缺少历史数据跳过。部分额外上游测试也依赖未包含的历史运行数据。尚未重新调用真实模型生成长篇作品。发布清单是上游历史记录，不代表当前源码逐字节一致。升级前请保留旧代码与作品：旧检查点的运行时哈希与新版不一致，不能直接续写。

模型生成仍可能出现情节质量、文风和事实判断问题。系统保存的结构化状态与模型审核结果都应视为辅助信息，最终作品仍需人工检查。

