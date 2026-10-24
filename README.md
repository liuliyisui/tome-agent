# Tome Agent

Tome Agent 是一个面向长篇小说生成的软件创新作业。核心代码已更新为 F 盘的 `stable-ar-20261023` 稳定版本，后端默认使用事件先行和三层记忆流程。

该稳定版本曾从空状态连续完成 25 章、50107 个汉字，中途没有人工续跑。这个结果证明流程具备连续生成和恢复能力，不代表小说内容质量已经通过人工评价。

## 当前能力

- 事件先行：先规划场景事件并推演状态，再生成正文，避免正文先写完后再猜关键事实。
- 三层记忆：工作记忆、近期记忆和长期记忆分别保存，并保留正文来源。
- 连续性管理：跟踪人物、物品、时间、任务、知识来源和状态版本。
- 断点恢复：每个阶段保存检查点，失败时保留已经完成的章节和待处理任务。
- 长度控制：根据总字数、剩余章节和实际进度动态分配章节篇幅。
- 失败降级：局部规划或记忆处理失败时记录问题，尽量继续保存有效正文。
- DeepSeek 接入：使用 Python 标准库访问官方 Chat Completions 接口。
- 离线演示：固定生成两章，不联网、不消耗额度。

图形前端尚未重新接入；`code/frontend/` 是后续界面的预留目录。

## 目录

```text
.github/               GitHub 工作流和 Issue 模板
code/backend/          DeepSeek 配置、应用服务、启动脚本和本地作品数据
code/core_engine/      稳定长文本核心、三层记忆、检查点和发布清单
code/frontend/         前端预留目录
docs/                  需求、设计、管理和使用文档
tests/                 单元测试与集成测试
```

仓库根目录只保留 `README.md` 和以上四个项目目录；`.git` 是 Git 自身的隐藏元数据。

## 快速验证（Windows）

```powershell
code\backend\setup.cmd
code\backend\run-demo.cmd
```

离线演示结果保存在 `code/backend/data/runs/`。运行自动测试：

```powershell
$env:PYTHONPATH="$PWD\code\core_engine;$PWD\code\backend"
code\backend\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

真实模型配置写入 `code/backend/.env`，该文件不会提交到 Git。配置模板见 `code/backend/.env.example`。

## 当前边界

本仓库已通过 71 项本地回归；稳定版的 68 个发布代码文件也通过发布清单哈希核验。F 盘随附的历史回归中有一部分依赖未随稳定包保留的旧运行样本和工具，因此不能在当前精简包内单独重放。真实五万字测试证据保存在 `docs/software/stable_verification/`。

模型生成仍可能出现情节质量、文风和事实判断问题。系统保存的结构化状态与模型审核结果都应视为辅助信息，最终作品仍需人工检查。

