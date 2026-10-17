# Tome Agent

Tome Agent 是一个面向长篇小说生成的软件创新作业。当前版本采用 INF writer 架构：规划、写作、记忆维护和审核四个角色依次处理下一章，只有通过契约校验与审核的候选状态才写入正式存档。

## 当前能力

- 四角色协作：planner、writer、memory、reviewer。
- 版本化事实记忆：记录主体、属性、值、版本、正文引文和变更历史。
- 逐章事务：正文、章节计划和事实变更一起提交，失败不污染正式状态。
- 原子存档：文件替换、版本比较和作品锁降低并发或中断造成的损坏风险。
- DeepSeek 接入：使用 Python 标准库访问官方 Chat Completions 接口。
- 离线演示：固定生成两章，不联网、不消耗额度。

图形前端尚未重新接入；`code/frontend/` 是后续界面的预留目录。

## 目录

```text
.github/               GitHub 工作流和 Issue 模板
code/backend/          DeepSeek 配置、应用服务、启动脚本和本地作品数据
code/core_engine/      INF writer 核心
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

离线测试只能证明程序流程和存档规则按预期工作，不能证明真实模型生成质量。长文本一致性、完成率、token 用量和费用仍需使用相同题材做对照实验后再下结论。

