# Tome Agent 代码评审（Python 代码质量整改后复审）

评审依据：[CodeReviewTemplate.md](https://github.com/bettermorn/ACMWDevHubPPT/blob/master/Methodology/CodeReviewTemplate.md)

本次聚焦「按 VS Code Python 代码质量指南落地的整改」在当前工作区的实际状态，并复核整改是否引入副作用。基线提交 `e4d23ce`，包含本地未提交修改（44 个 `.py` 文件 + 3 个新增配置文件）。逐条修改明细另见 [代码质量整改清单](CODE_QUALITY_FIXES.md)。未逐行审查引擎的语义正确性，也未调用真实模型、真实 PostgreSQL 或浏览器交互。

## 1. 关于代码

| 检查项目 | 结果 | 说明 |
|---|---|---|
| 模块名 | Tome Agent 工作室 | Vue 前端、Python 网页服务、INF 创作引擎与三档记忆运行时 |
| 审查人员 | DSH（DeepSeek Harness） | 自动辅助评审 |
| 版本 | `e4d23ce` + 工作区修改 | 44 个 `.py` 修改、3 个新文件尚未提交 |
| 日期 | 2026-11-07 | 本地时间 |
| 程序设计语言 | Python（目标 3.11）、JavaScript、HTML、CSS | Vue 3 前端 |
| 作者 | 多人及自动辅助 | 未逐一核验 |
| 文件数 | 171 个 Python 文件（不含 `.venv`/`__pycache__`/`runs`），本次改动 44 个 | 工作区状态，不代表逐行全量审查 |

## 2. 自动检查

| 检查项目 | 结果 | 说明 |
|---|---|---|
| 代码通过编译，没有错误 | 通过 | `python -m compileall -q code/backend code/core_engine tests` 退出码 0 |
| 代码通过编译，没有警告 | 通过（项目代码） | 追加 `-W error::SyntaxWarning` 全仓编译仍为 0；第三方 `langsmith` 在集成测试中触发 1 条 `DeprecationWarning`（`asyncio.iscoroutinefunction`），非本项目代码，未做依赖告警审计 |
| 存在单元测试 | 是 | `tests/` 127 项（97 单元 + 30 集成，7 跳过）；`tests/run_engine_regression.py` 42 项（3 跳过） |
| 源代码版本控制 | 是 | Git；HEAD `e4d23ce`；工作区仍有未提交改动 |
| 检查工具 | Ruff 0.17.4、unittest、compileall | Ruff 读取仓库根 `pyproject.toml`，规则集 `E,W,F,I,B,C4,UP`，`ignore=E501` |
| 检查结果 | 通过 | `ruff check .` 0 违规、`ruff format --check .` 179 个文件已格式化；测试 97 + 30 + 42 全通过（10 项跳过） |

## 3. 设计

| 检查项目 | 结果 | 说明 |
|---|---|---|
| 功能完成度 | 部分 | 写作、记忆推进与工作室流程可用；旧存档跨版本续写仍只有只读回退，缺通用迁移流程 |
| 算法模型选择 | 未评估 | 回归全部使用离线夹具，未调用真实模型或做质量对比 |
| 设计模式和代码结构 | 部分合理 | 端口/适配器边界清晰（`ports.py`、`ModelGateway`）、网页层与引擎层分离；但 `inf_writer` 存在两份逐字节相同的副本 |
| 缺失功能清晰标注 | 较好 | 全仓 `TODO/FIXME` 为 0；缺失历史夹具在 `tests/run_engine_regression.py:23-27` 用显式 `unavailable` 字典登记并跳过，属可核查的标注方式 |
| 存在设计文档 | 是 | `docs/algorithm/ARCHITECTURE.md`、`docs/software/architecture.md`，本次新增 `docs/software/CODE_QUALITY_FIXES.md` |
| 代码与文档相符 | 部分 | 本次整改已补文档；`e4d23ce` 新增的工作室导航/封面改动未见对应设计说明同步 |

## 4. 编写质量

| 分类 | 检查项目 | 结果 | 说明 |
|---|---|---|---|
| 风格 | 布局、名称、API | 通过（规则层） | Ruff 全绿；仍有 490 行超过 88 列，其中 416 行为中文提示词/长字符串字面量（formatter 不能拆分），74 行为其他代码 |
| 防御性编程 | 输入校验 | 部分 | 存档与记忆路径有 `ContractError` 校验、检查点路径有 `is_relative_to` 越权检查；未做模糊测试或攻击面审计 |
| 防御性编程 | 类型检查 | 弱 | 1633 个函数中仅 24 个有返回注解（1%），参数注解几乎全无；无 `mypy` 门禁，`Pylance basic` 只作用于编辑器 |
| 防御性编程 | 资源和并发 | 未确认 | 未做负载与并发审计；网页服务为线程模型 |
| 防御性编程 | 循环引用、编译器特性 | 未确认／不适用 | 未做全量引用分析；C/C++ 编译器检查不适用 |
| 错误处理 | 异常安全及错误传播 | 改善明显 | 本次补齐 14 处 `raise ... from`（`B904`），旧检查点回退统一 `from exc`，异常链不再被隐式丢弃 |
| 错误处理 | 断言 | 通过 | 测试使用 `assert`（`tests/**` 已按指南豁免 `S101`），生产输入校验使用显式异常；无裸 `except:` |
| 错误处理 | 日志 | 未评估 | 仅 2 个模块使用 `logging`，未评估轮转与敏感信息脱敏 |
| 错误处理 | 资源泄漏、线程安全、死锁 | 未确认 | 沿用线程与锁；未证明全部场景安全 |
| 结构 | 冗余、复制粘贴 | 有问题 | `inf_writer` 两份副本、35 个文件逐字节相同（见第 5 节 P2） |

## 5. 语句级审查

| 优先级 | 文件与位置 | 问题 | 建议 |
|---|---|---|---|
| P1 | `code/core_engine/memory_runtime/test_continuity.py:44`、`test_regression.py:20`、`test_writing.py:244` 等 9 个测试模块 | 这些脚本式测试模块依赖未入库夹具（`code/core_engine/runs/`、`docs/analysis/novel_review_20261021_c/paragraphs.json`、`tools/continuous_memory_20261021_i/test_run.py`），干净副本上会直接 `FileNotFoundError`／`setUpClass` 失败。CI 只跑 `tests/`（127 项）和 `tests/run_engine_regression.py`（42 项），这 9 个模块不在其中：`test_continuity`、`test_event_first`、`test_grounding_references`、`test_generation_foundations`、`test_projection_grounding`、`test_provider_stop`、`test_story_review`、`test_writing`、`test_regression`。实测这 9 个模块在当前副本上均有报错（单个模块 1~35 个用例受影响，`test_regression.py` 为导入期失败），其余用例通过。 | 夹具入库或改造成生成式夹具；把可运行部分并入 `tests/run_engine_regression.py` 的类清单，让 CI 真正覆盖。 |
| P2 | `code/core_engine/inf_writer/` 与 `code/core_engine/memory_runtime/src/inf_writer/`（各 35 个文件） | 两份副本逐字节相同，但 `import inf_writer` 命中哪一份取决于 `sys.path` 插入顺序（`write_novel.py:19`、`memory_runtime/__init__.py:14`、`check_memory.py:14` 各自插入不同目录）。本次整改不得不在两侧重复修改 `agents.py` 与 `narrative_context.py`，漏改一处就会让两个入口行为分叉。 | 保留单一源（删除一份改软链接，或改 `src/` 布局 + `pip install -e`）；CI 增加两树一致性校验（本次以逐文件哈希核验，35/35 相同）。 |
| P2 | `code/core_engine/memory_runtime/continuity.py:167` | `fail()` 闭包依赖循环变量 `row` 的晚绑定，而 `row` 在同一轮迭代内会被重新赋值（`row = copy.deepcopy(row)` 后改写 `attribute`）。本次以 `# noqa: B023` 加注释保留，因为改用默认参数会把错误详情冻结成未规范化的旧值；但该写法依赖「闭包只在当前迭代内调用」，将来若被缓存或跨迭代复用会静默错报。 | 改为显式传参（`fail(message, row, prior)`），或先算出规范化记录存进局部常量再闭包引用。 |
| P2 | 全仓类型注解 | 1633 个函数仅 24 个有返回注解；CI 无静态类型门禁。对 4 万行级引擎做结构性改动（如上面的去重）缺少编译期保护，只能靠测试兜底。 | 按模块增量补注解（先 `domain/`、`ports.py` 等接口层），在 `pyproject.toml` 增加 `[tool.mypy]` 并让 CI 逐步扩大检查范围。 |
| P3 | `code/core_engine/inf_writer/agents.py:13` 等 107 个文件 | 490 行超过 88 列，其中 416 行是中文提示词/长字符串（最长 1109 字符）。`ruff format` 不拆分字符串，`E501` 又被配置忽略，导致提示词既难 diff 也无法复用。 | 长提示词抽到独立的 `.md`/`.txt` 资源按段落加载；保留 `E501` 忽略以免噪音。 |
| P3 | `pyproject.toml:36-44` | 30 处 `E402`（`check_memory.py`、`write_novel.py`、`memory_runtime/test_*.py`）通过 `per-file-ignores` 豁免，根因是项目以「脚本 + `sys.path.insert`」方式运行（全仓 17 处），而非可安装包。 | 逐步改为可安装包布局并删除 `sys.path` 引导；短期保留豁免（配置内已注明理由）。 |
| P3 | `code/backend/pyproject.toml` 与根 `pyproject.toml` | 前者只做打包（`[project]`、`setuptools`），后者只做 Ruff 规则；同名文件、职责不同，且 `requires-python` 与 `target-version` 需人工同步（当前均为 3.11）。 | 在打包配置顶部或 README 注明分工，或把打包配置上移统一。 |

## 6. 跟踪调查与评审结论

| 检查项目 | 结果 | 说明 |
|---|---|---|
| 代码质量较好 | 是（规则层）／待改进（结构层） | Ruff 0 违规、格式统一、异常链补齐；但双副本、类型注解缺失、9 个测试模块不在 CI 覆盖 |
| 重新编写并验证 | 已完成 | 整改并验证 79 处不合规（首轮 75 + 新提交 4），明细见 [代码质量整改清单](CODE_QUALITY_FIXES.md) |
| 重新审查 | 已完成 | HEAD 由 `e085af4` 更新为 `e4d23ce` 后重跑全部检查，新增的 4 处已修复并复验 |
| 审查 | 通过（含遗留项） | 详见第 5 节 |
| 校验 | 部分通过 | `ruff check`／`ruff format --check`／`compileall`／`unittest`（97 + 30 + 42）全通过；未验证真实 PostgreSQL、真实模型调用与浏览器交互 |

补充说明：

1. **证据来源**：本地执行记录（Ruff 0.17.4、Python 3.14 运行、目标 3.11）。P1 建立在「干净副本上实测报错、且 `git stash` 前后结果一致」之上；P2 的副本问题来自逐文件哈希比对（35/35 相同）；P3 的行宽与注解比例由 AST 与行扫描脚本统计（490 行超宽、1633 个函数 24 个有返回注解）。
2. **规则集边界**：本次规则集不含 `BLE`（盲捕异常）与 `LOG`（日志格式），因此上一版评审在 `service.py:534`、`web.py:182/195/411` 报出的 2 条 `BLE001`、2 条 `LOG015` 不会在本轮被检出；全仓仍有 59 处 `except Exception:`。若需要覆盖，把 `"BLE"`、`"LOG"` 加入 `select` 即可，但会引入一批新问题。
3. **上一版评审的遗留项**：本次顺带复核了封面校验，`service.py:146-153` 仍只判断文件头签名（PNG/JPEG/WebP），未做解码与像素上限校验，该项仍未修复；数据库模式存档兼容状态、`style.css:55` 首页滚动两项未复核。
4. **沙箱环境差异**：本次核查在受限文件沙箱内进行，`tempfile.mkdtemp` 创建的 `0o700` 目录会触发 `PermissionError`（DSH 策略所致，非仓库缺陷）。涉及临时目录的脚本以绕过方式运行，结论已扣除该因素；直接运行会看到与代码无关的报错。
5. **改动边界**：整改只涉及导入顺序、异常链、循环变量绑定、死代码、格式，以及新增配置与文档；未改写任何业务分支判断。42 个文件的改动可用 `git diff` 逐处复核。
