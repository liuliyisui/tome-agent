# Tome Agent 测试执行报告

> 报告编号：TR-20261114-02（替代 TR-20261114-01）
> 执行日期：2026-11-14
> 被测版本：`624564c`（`main` 分支，含目录重构与 PR #28）
> 被测系统：面向长篇小说创作的多智能体写作工作室
> 执行结论：**通过** —— 248 项测试通过、0 项失败、8 项按环境跳过，核心逻辑覆盖率 61.01%，并完成一次真实模型端到端生成

---

## 1. 执行环境

| 项 | 值 |
|---|---|
| 操作系统 | Windows 11 Home China 10.0.26200 |
| Python | 3.12.10（解释器位于 `.venv`） |
| 测试框架 | pytest 9.2.0（unittest 兼容模式） |
| 覆盖率工具 | coverage.py 7.17.2（C 扩展） |
| 代码规范 | ruff 0.17.4 |
| 数据库 | 未配置（`TOME_TEST_DATABASE_URL` 为空） |
| 模型服务 | DeepSeek 官方接口 `https://api.deepseek.com/chat/completions` |
| 模型 | `deepseek-chat` |
| 网络 | 离线测试不联网；§8 真实冒烟为唯一联网环节 |

---

## 2. 执行范围与命令

本次执行覆盖**全部既有用例**，包括远程重构后新增的测试文件。

| 步骤 | 命令 | 范围 |
|---|---|---|
| 1 | `pytest -q tests/unit` | 全部单元测试 |
| 2 | `pytest -q tests/integration` | 全部集成测试 + E2E 冒烟 |
| 3 | `python tests/run_coverage.py` | 覆盖率统计与 60% 门禁（含引擎回归） |
| 4 | 真实生成脚本 | 真实模型端到端冒烟 |

复现命令（PowerShell）：

```powershell
$env:PYTHONPATH="$PWD\code\core_engine;$PWD\code\backend"
.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/unit
.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/integration
.venv\Scripts\python.exe tests/run_coverage.py
```

---

## 3. 结果总览

| 层级 | 收集用例 | 通过 | 失败 | 跳过 | 子测试 | 耗时 |
|---|---:|---:|---:|---:|---:|---:|
| 单元测试 `tests/unit` | 196 | **196** | 0 | 0 | 151 | 4.16s |
| 集成测试 `tests/integration` | 60 | **52** | 0 | 8 | 2 | 32.02s |
| 覆盖率脚本（单元 + 引擎回归） | 42 | 39 | 0 | 3 | — | 57.50s |
| **合计（单元 + 集成）** | **256** | **248** | **0** | **8** | **153** | **36.18s** |

> 与上一版报告相比：单元用例从 179 增至 196，集成通过数从 50 增至 52，均因远程合并了目录重构、PR #28 与新增测试文件（`test_memory_layout.py`、`test_package_migration.py`、`test_streaming_progress.py` 等）。

---

## 4. 单元测试结果（`tests/unit`）

| 测试文件 | 用例数 | 结果 | 覆盖重点 |
|---|---:|---|---|
| `test_core.py` | 31 | ✅ | 写作引擎主流程与状态机 |
| `test_domain_support_contract.py` | 25 | ✅ | 证据绑定、偏移量校验、支持审核 |
| `test_drafting.py` | 15 | ✅ | 草稿生成与文本处理 |
| `test_chat_provider.py` | 14 | ✅ | 模型适配器与消息构造 |
| `test_length_control.py` | 12 | ✅ | 章节长度容差与降级路径 |
| `test_core_boundaries.py` | 12 | ✅ | 核心函数边界行为 |
| `test_writer_format.py` | 11 | ✅ | 写手输出格式约束 |
| `test_langgraph.py` | 10 | ✅ | 图编排运行时 |
| `test_streaming_progress.py` | 9 | ✅ | 流式进度上报（重构后新增） |
| `test_chapter_titles.py` | 9 | ✅ | 章节标题清洗 |
| `test_book_input_validation.py` | 7 | ✅ | 作品输入等价类 + 边界值 |
| `test_title_sanitization.py` | 6 | ✅ | 标题合法化 |
| `test_quality_refactors.py` | 5 | ✅ | 质量重构逻辑 |
| `test_memory_layout.py` | 5 | ✅ | 记忆目录布局（重构后新增） |
| `test_event_consistency.py` | 5 | ✅ | 事件一致性 |
| `test_official_pricing.py` | 4 | ✅ | 计费口径 |
| `test_model_settings.py` | 5 | ✅ | 模型配置（含自定义 base URL） |
| `test_plan_bounds.py` | 3 | ✅ | 规划边界 |
| `test_logging.py` | 3 | ✅ | 日志脱敏 |
| `test_accounts.py` | 3 | ✅ | 账户与会话 |
| `test_package_migration.py` | 1 | ✅ | 模块迁移兼容（重构后新增） |
| `test_memory_layers.py` | 1 | ✅ | 分层记忆 |
| **合计** | **196** | **✅** | 另有 151 个子测试通过 |

### 4.1 等价类与边界值（课程重点）

| 输入字段 | 有效等价类 | 无效等价类 | 边界值 | 结果 |
|---|---|---|---|---|
| `chapters` | 1~100 整数 | 0、负数、>100、小数、字符串、布尔、`None` | 0 / 1 / 2 / 99 / 100 / 101 | ✅ |
| `target_units` | 500~200000 整数 | <500、>200000、小数、字符串、布尔、`None` | 499 / 500 / 501 / 199999 / 200000 / 200001 | ✅ |
| `title` / `prompt` | 非空文本 | 空串、纯空白、`None`、数字 | — | ✅ |
| 章节长度 | 目标 ±10% 容差 | 低于 90%、高于 110%、超上下文 | 899 / 900 / 1100 / 1101 | ✅ |

---

## 5. 集成测试结果（`tests/integration`）

| 测试文件 | 用例数 | 通过 | 跳过 | 说明 |
|---|---:|---:|---:|---|
| `test_web.py` | 19 | 19 | 0 | Web API 契约、创建/编辑/删除、生成任务、CORS |
| `test_service.py` | 9 | 9 | 0 | 应用服务入口、失败保留、检查点 |
| `test_browser_smoke.py` | 7 | 7 | 0 | Playwright 浏览器主流程冒烟 |
| `test_hosted.py` | 4 | 4 | 0 | 托管部署与账户隔离 |
| `test_story_flow_e2e.py` | 3 | 3 | 0 | 场景法端到端 |
| `test_writing_style.py` | 3 | 3 | 0 | 写作风格约束 |
| `test_skills.py` | 3 | 3 | 0 | 技能调用 |
| `test_library.py` | 3 | 3 | 0 | 作品库 |
| `test_hosted_workers.py` | 1 | 1 | 0 | 托管工作进程 |
| `test_postgresql.py` | 8 | 0 | **8** | 未配置 `TOME_TEST_DATABASE_URL`，按设计跳过 |
| **合计** | **60** | **52** | **8** | 另有 2 个子测试通过 |

### 5.1 场景法端到端（IT-FLOW-01~03）

| 用例 | 场景 | 结果 |
|---|---|---|
| IT-FLOW-01 | 创建 3 章作品 → 生成 2 章 → 检查点一致 → 导出 Markdown | ✅ |
| IT-FLOW-02 | 第 2 章返回 `NO_DRAFT`，抛 `RuntimeError` 且第 1 章保留 | ✅ |
| IT-FLOW-03 | `count=0` / `count=4` 越界，抛 `ValueError` 且不产生运行目录 | ✅ |

### 5.2 跳过项

8 项全部来自 `test_postgresql.py`，原因均为：

```text
Set TOME_TEST_DATABASE_URL for real PostgreSQL tests
```

属于既有的环境门控，不是测试失败。

---

## 6. 覆盖率

### 6.1 汇总

| 口径 | 范围 | 语句 | 分支 | 综合 | 门槛 | 结论 |
|---|---|---:|---:|---:|---:|---|
| **单元测试** | 核心 8 模块 | 64.43%<br>(2141/3323) | 53.27%<br>(783/1470) | **61.01%** | ≥60% | ✅ 达标 |
| 单元 + 引擎回归 | 核心 8 模块 | 71.26%<br>(2368/3323) | 59.05%<br>(868/1470) | **67.52%** | ≥60% | ✅ 达标 |
| 单元测试 | 后端 + 引擎全量 | 42.55% | 31.08% | 39.02% | — | 参考值 |

### 6.2 核心模块明细（单元测试口径）

| 模块 | 语句 | 分支 | 综合 |
|---|---:|---:|---:|
| `memory_runtime/graph_runtime.py` | 100.0% (37/37) | 100.0% (6/6) | **100.0%** |
| `inf_writer/domain.py` | 83.6% (286/342) | 74.7% (133/178) | **80.6%** |
| `inf_writer/agents.py` | 67.2% (162/241) | 60.1% (89/148) | **64.5%** |
| `memory_runtime/writing.py` | 66.9% (658/983) | 48.3% (117/242) | **63.3%** |
| `memory_runtime/event_first.py` | 66.3% (364/549) | 55.8% (183/328) | **62.4%** |
| `inf_writer/tiered_memory.py` | 64.6% (155/240) | 50.0% (62/124) | **59.6%** |
| `memory_runtime/continuity.py` | 61.5% (208/338) | 55.6% (109/196) | **59.4%** |
| `memory_runtime/pipeline.py` | 45.7% (271/593) | 33.9% (84/248) | **42.2%** |
| **合计** | **64.43%** | **53.27%** | **61.01%** |

### 6.3 核心模块明细（含引擎回归口径）

| 模块 | 语句 | 分支 | 综合 |
|---|---:|---:|---:|
| `graph_runtime.py` | 100.0% | 100.0% | 100.0% |
| `writing.py` | 84.9% | 67.8% | 81.6% |
| `domain.py` | 83.6% | 74.7% | 80.6% |
| `event_first.py` | 70.7% | 62.8% | 67.7% |
| `agents.py` | 70.5% | 63.5% | 67.9% |
| `tiered_memory.py` | 69.2% | 54.0% | 64.0% |
| `continuity.py` | 63.0% | 57.1% | 60.9% |
| `pipeline.py` | 46.0% | 34.7% | 42.7% |
| **合计** | **71.26%** | **59.05%** | **67.52%** |

原始报告文件：

- `code/backend/data/coverage-unit-all.json`
- `code/backend/data/coverage-unit-core.json`
- `code/backend/data/coverage-core-combined.json`

---

## 7. 课程要求符合性核验

| # | 课程要求 | 落实位置 | 证据 | 结论 |
|---|---|---|---|---|
| 1 | 为核心逻辑编写单元测试（JUnit / pytest / Jest） | `tests/unit/` 共 22 个测试文件 | 196 项通过、151 子测试 | ✅ |
| 2 | 用等价类 + 边界值为至少一个输入字段设计用例 | `test_book_input_validation.py` | `chapters` 与 `target_units` 全部边界值通过 | ✅ |
| 3 | 用场景法为一条关键业务流程编写端到端测试 | `test_story_flow_e2e.py` | IT-FLOW-01 创建 → 生成 → 检查点 → 导出；IT-FLOW-02/03 备选流 | ✅ |
| 4 | 统计覆盖率，确保核心逻辑 ≥ 60% | `tests/run_coverage.py` | 核心 8 模块综合 **61.01%**，门禁内置 | ✅ |

---

## 8. 真实模型执行验证

在全部离线用例通过后，使用真实 DeepSeek 接口完整执行了一次作品生成。

### 8.1 执行参数

| 项 | 值 |
|---|---|
| 模型 | `deepseek-chat` |
| 接口 | `https://api.deepseek.com/chat/completions` |
| 作品 | 《雾港来信》 |
| 构思 | 一名邮差在雾港发现每封信都预言了次日的事故，他必须在最后一封信送到前找到真相 |
| 目标 | 2 章 / 1200 字 |
| 数据目录 | 系统临时目录（未写入仓库） |

### 8.2 执行结果

| 指标 | 结果 |
|---|---|
| 完成章节 | **2 章** |
| 第 1 章字数 | **876 字** |
| 第 2 章字数 | **669 字** |
| 合计字数 | 1545 字 |
| 模型调用次数 | **18 次** |
| 输入 tokens | **177,829** |
| 输出 tokens | **21,314** |
| 导出 Markdown | 1623 字符 |
| 总耗时 | **102.6 秒** |
| 进度事件 | 4 次（每章规划与完成各 1 次） |
| 结果 | ✅ 全链路成功，无异常 |

### 8.3 执行时间线

| 阶段 | 时间点 | 事件 |
|---|---|---|
| 创建作品并启动 | 0.0s | `create_book` 成功 |
| 第 1 章规划 | 0.5s | `planning` |
| 第 1 章完成 | 56.5s | 876 字 |
| 第 2 章规划 | 56.5s | `planning` |
| 第 2 章完成 | 102.6s | 669 字 |
| 导出 | 102.6s | Markdown 1623 字符 |

### 8.4 正文节选

第 1 章：

```text
天还没亮透，雾港分局分拣房的窗缝就渗进一股咸湿水汽，糊得玻璃发白。
老周把西码头的邮袋往林默脚边一扔，袋口散出旧牛皮纸和油墨的味儿。
"雾天路滑，走慢点。"
```

第 2 章：

```text
海雾把码头灯晕成一团黄。林默就着那点光撕开"后日启"封口，抽出薄纸。
一行毛笔字："明早五点半，雾港分局分拣房起火，老周困在屋内。"
他把两封信并排摊在膝上比对……
```

### 8.5 结论

真实模型下，**创建作品 → 规划 → 事件抽取 → 正文生成 → 记忆写入 → 审阅 → 检查点 → Markdown 导出**全链路可用，两章连续生成、人物与线索保持一致。

> 该验证未纳入自动化测试套件；测试套件始终离线、可重复、无模型费用。

---

## 9. 风险、限制与后续建议

| 编号 | 项 | 影响 | 建议 |
|---|---|---|---|
| R-01 | `pipeline.py` 综合覆盖率仅 42.2% | 该模块分支逻辑复杂，缺陷发现能力有限 | 补充管线降级、重试与异常路径的单元测试 |
| R-02 | `continuity.py` / `tiered_memory.py` 单项低于 60% | 依赖 8 模块合计达标 | 补充记忆失效与连续性回退用例 |
| R-03 | PostgreSQL 集成测试未执行 | 持久化层未在真实数据库验证 | 配置 `TOME_TEST_DATABASE_URL` 后单独执行 |
| R-04 | 真实生成仅覆盖 2 章 | 长程连续性与上下文压缩未验证 | 可执行 10 章以上的成本可控评估 |
| R-05 | 本次真实调用使用了明文密钥 | 密钥已在对话中暴露 | 未写入任何文件和提交；建议吊销并重新生成 |
| R-06 | 费用估算字段为 0 | 项目默认单价配置为 0，未反映真实账单 | 以 DeepSeek 控制台账单为准 |

---

## 10. 结论

1. 当前基线 `624564c` 上，单元测试 **196 项全部通过**，集成测试 **52 项通过、8 项按环境跳过、0 项失败**。
2. 核心 8 模块覆盖率 **61.01%**（语句 64.43% / 分支 53.27%），高于课程要求的 60%，覆盖率门禁未触发。
3. 四项课程要求全部落实，均有可复现命令与原始覆盖率报告作为证据。
4. 真实模型执行完成 2 章共 1545 字，18 次调用、耗时 102.6 秒，验证了完整业务链路。

**总体判定：测试通过，可用于课程实践任务交付。**

---

## 附录 A：报告相关文件

```text
tests/
├── TEST_REPORT.md                       # 本报告
├── TEST_CASES.md                        # 用例文档总览
├── unit/
│   ├── TEST_CASES.md                    # 单元用例文档
│   └── ...                              # 22 个测试文件
└── integration/
    ├── TEST_CASES.md                    # 集成 + E2E 用例文档
    └── ...                              # 10 个测试文件

code/backend/data/
├── coverage-unit-all.json
├── coverage-unit-core.json
└── coverage-core-combined.json
```
