# Tome Agent

Tome Agent 是一个面向长篇小说创作的多智能体写作工作室。它将章节规划、事件推演、正文生成、记忆维护和内容审核串联起来，帮助创作者把故事从构思持续推进到完整篇章。

项目基于 LangGraph 编排，结合事件先行写作和三层记忆机制，为长篇创作提供连续性管理、进度保存与本地可视化操作。详见 [LangGraph 迁移说明](docs/software/LANGGRAPH_MIGRATION.md)。

## 产品优势

- **面向长篇的创作流程**：从故事规划到逐章写作，再到记忆整理和审核，为持续创作提供完整工作流。
- **让故事状态有迹可循**：围绕事件、人物和物品维护结构化状态，将重要记忆与正文来源关联，方便后续章节参考。
- **创作过程可继续、可追踪**：通过检查点保存阶段进度和待处理任务，支持在中断后恢复工作。
- **操作直观，部署灵活**：在本地网页中管理作品、调整文风、确认费用、生成章节并导出 Markdown；可按需选择文件或 PostgreSQL 存储。
- **技术组合轻量实用**：LangGraph 负责流程编排，Vue 提供交互界面，Python 标准库提供本地 Web 服务。

## 核心功能

- LangGraph 编排：规划、写作、提交、记忆处理和审核为独立节点，写作请求修订时通过条件边返回规划节点。
- 事件先行：先规划场景事件并推演状态，再生成正文，避免正文先写完后再猜关键事实。
- 三层记忆：工作记忆、近期记忆和长期记忆分别保存，并保留正文来源。
- 连续性管理：跟踪人物、物品、时间、任务、知识来源和状态版本。
- 断点恢复：每个阶段保存检查点，失败时保留已经完成的章节和待处理任务。
- 长度控制：根据总字数、剩余章节和实际进度动态分配章节篇幅。
- 失败降级：局部规划或记忆处理失败时记录问题，尽量继续保存有效正文。
- 多模型接入：支持 DeepSeek、OpenAI，以及提供 Chat Completions 兼容接口的其他服务；在设置中填写模型、接口地址和对应密钥。
- 本地网页：创建作品、配置文风、确认费用后逐章或批量生成，支持导出排版后的 Markdown。
- 写作 Skill：在作品页面导入 `SKILL.md`，为每部作品选择写作技能，后续正文生成时自动加载。

图形前端位于 `code/frontend/`，使用 HTML、CSS、JavaScript，并包含本地 Vue 运行时及交互组件。

## 技术选型

| 条目 | 技术 | 版本 | 选择原因与用途 |
| --- | --- | --- | --- |
| 编程语言 | Python | 3.11 及以上；CI 使用 3.11 | 用于写作引擎、模型接口和后端服务，便于组织多智能体逻辑。 |
| 前端语言 | HTML、CSS、JavaScript | 无单独锁定版本 | 使用浏览器原生技术实现本地工作室，降低构建与部署复杂度。 |
| 前端框架 | Vue | 3.5.44 | 使用仓库内置运行时组织交互组件，无需前端构建步骤。 |
| 智能体编排 | LangGraph | 1.2.17 | 用状态图表达规划、写作、记忆与审核流程，支持条件分支和重规划。 |
| Web 服务 | Python 标准库 `http.server` | 随 Python 版本提供 | 为本地单用户工作室提供 HTTP 接口，减少额外服务框架依赖。 |
| 数据库 | PostgreSQL（可选） | CI 测试 17、18；Docker 配置使用 17 | 需要持久化数据库时保存作品、章节和任务；未配置时使用文件模式。 |
| 数据库驱动 | Psycopg | 3.3.3 | 为 Python 后端提供 PostgreSQL 连接和事务支持。 |
| 运行平台 | Windows；其他平台可运行 Python 服务与测试 | Python 3.11+ | 提供 Windows 启动脚本；CI 也在 Linux 上测试数据库集成。 |
| 开发工具 | VS Code 等支持 Python 的编辑器 | 项目未锁定版本 | 用于编辑和调试；可按团队习惯选择，运行项目不依赖特定 IDE。 |

Python 依赖版本见 [`code/backend/requirements.txt`](code/backend/requirements.txt)；前端 Vue 版本以仓库内置文件为准。

## 目录

```text
.github/                         GitHub 工作流和问题模板
code/
├── backend/                     后端服务
├── frontend/                    前端工作室
└── core_engine/                 核心写作与记忆引擎
docs/
├── requirements/
│   ├── problem_definition.md    问题定义
│   ├── functional_spec.md       功能需求规格
│   ├── nonfunctional_spec.md    非功能需求规格
│   └── user_stories.md          用户故事与验收标准
├── algorithm/
│   └── research.md              算法与技术调研
├── software/
│   ├── prototype/               原型设计
│   ├── architecture.md          系统架构
│   ├── code_quality.md          代码质量
│   ├── code_review.md           代码评审
│   └── deployment.md            系统部署
├── mgmt/
│   ├── communication_mgmt_plan.md  沟通管理计划
│   └── risk_mgmt_plan.md        风险管理计划
└── retrospection/               复盘总结
tests/
├── unit/                        单元测试
├── integration/                 集成测试
└── tome_agent_demo_user_test.md 用户测试方案
README.md                        项目说明
```

上表列出课程要求的主要目录和文件；各目录下还保留项目的代码、测试和历史文档。


代码质量检查配置位于 `code/backend/pyproject.toml`。从项目根目录运行 `ruff check --config code/backend/pyproject.toml --no-cache .`；预提交钩子配置及用法见[代码质量说明](docs/software/CODE_QUALITY_FIXES.md)。

## 快速验证（Windows）

可以先使用文件模式。运行 `setup.cmd` 后，将 `code/backend/.env` 中的 `DATABASE_URL` 留空，再启动本地工作室：

```powershell
code\backend\setup.cmd
code\backend\run-web.cmd
```

打开 http://127.0.0.1:8765，在「设置 → 配置模型服务」中填写所选服务商的 API Key 和模型名称。选择其他兼容服务时，需填写以 `/chat/completions` 结尾的完整 HTTPS 接口地址；模型须支持 Chat Completions、JSON 对象输出和用量返回。文件模式下作品存放于 `code/backend/data/inf_books/`。如需使用 PostgreSQL，请按[数据库说明](docs/software/POSTGRESQL.md)配置 `DATABASE_URL`、初始化数据库，并按需导入旧作品；引擎检查点仍保存在本地文件中。

新作品使用当前模型配置，已有作品继续使用创建时绑定的模型和对应接口；切换服务不会覆盖原 DeepSeek 密钥。更换相同接口的密钥后，该接口下的作品使用新密钥。密钥保存在本机 `.env` 中，不会返回网页。其他服务的价格暂不能自动核验，系统也不能按金额限制这些服务的调用，生成前请到服务商处确认费用和额度；兼容接口和具体模型的能力、上下文长度及计费可能不同。

在作品页面的「写作 Skill」中选择 Markdown 文件即可安装；勾选技能后，下次生成正文时生效，每部作品最多选择 5 个。技能以文本形式提供给写作模型，不执行文件中的脚本、工具调用或文件操作，也不保证兼容其他产品的技能运行机制。安装的技能保存在 `code/backend/data/skills.json`，作品的选择保存在对应作品目录中；技能文本会增加模型输入量，请只导入信任的内容。

运行自动测试：

```powershell
$env:PYTHONPATH="$PWD\code\core_engine;$PWD\code\backend"
code\backend\.venv\Scripts\python.exe -m unittest discover -s tests -v
code\backend\.venv\Scripts\python.exe tests\run_engine_regression.py
```

真实模型配置写入 `code/backend/.env`，该文件不会提交到 Git。配置模板见 `code/backend/.env.example`。

## 验证与使用说明

应用回归运行 127 项，其中 120 项通过、7 项在未设置测试数据库连接时跳过；这 7 项随后使用本机 PostgreSQL 独立运行并全部通过。长篇引擎回归运行 42 项，其中 39 项通过，3 项因缺少历史数据跳过。部分额外上游测试也依赖未包含的历史运行数据。尚未重新调用真实模型生成长篇作品。发布清单是上游历史记录，不代表当前源码逐字节一致。升级前请保留旧代码与作品：旧检查点的运行时哈希与新版不一致，不能直接续写。

模型生成仍可能出现情节质量、文风和事实判断问题。系统保存的结构化状态与模型审核结果都应视为辅助信息，最终作品仍需人工检查。

