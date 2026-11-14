# 核心功能测试用例与覆盖率

## 测试范围

本次验收的核心写作流程包括章节生成与恢复（`memory_runtime/writing_flow/writing.py`）、事件推演（`event_first.py`）、连续性（`continuity.py`）、记忆处理（`pipeline.py`、`tome_writer/tiered_memory.py`）、流程编排（`graph_runtime.py`）、基础数据契约（`tome_writer/domain.py`）和角色请求（`tome_writer/agents.py`）。这 8 个模块覆盖从规划、状态更新到正文保存与记忆维护的主要链路；它们不是整个项目，也不包含网页、数据库和全部辅助模块。

测试代码主要位于 `tests/unit/` 和 `tests/integration/`。引擎回归入口为 `tests/run_engine_regression.py`，其中复用 `code/core_engine/memory_runtime/` 的现有测试。模型回复使用离线模拟，不访问付费模型。

## 等价类与边界值

`tests/unit/test_core_boundaries.py` 对新建作品参数执行真实校验，并检查无效输入不会创建作品：

| 编号 | 输入 | 等价类或边界 | 预期 |
| --- | --- | --- | --- |
| B01 | 1 章，500 字 | 两项有效下限 | 创建成功 |
| B02 | 100 章，200000 字 | 两项有效上限 | 创建成功 |
| B03 | 0 章，500 字 | 章节下限外 | 拒绝且不创建作品 |
| B04 | 101 章，500 字 | 章节上限外 | 拒绝且不创建作品 |
| B05 | 1 章，499 字 | 篇幅下限外 | 拒绝且不创建作品 |
| B06 | 1 章，200001 字 | 篇幅上限外 | 拒绝且不创建作品 |
| B07–B08 | 章节数或篇幅为布尔值 | 无效类型 | 拒绝且不创建作品 |

## 核心逻辑单元用例

| 编号 | 场景 | 预期 | 测试位置 |
| --- | --- | --- | --- |
| U01 | 准备事件方案 | 原状态保持不变，候选状态记录新事实 | `unit/test_event_consistency.py` |
| U02 | 计划中的动作 | 不直接变成已发生事实 | 同上 |
| U03 | 未知、重复或缺失事件标记 | 拒绝不合法正文绑定 | 同上 |
| U04 | 修改不可变事实或使用过期版本 | 拒绝变更，保留原状态 | 同上 |
| U05 | 当前时间倒退、历史回述 | 拒绝倒退；允许历史事件且不重置当前时间 | `unit/test_core_boundaries.py` |
| U06 | 引文不在正文中 | 拒绝更新且不修改原状态 | 同上 |
| U07 | 原件缺失时直接观察 | 拒绝无依据的观察 | 同上 |
| U08 | 以照片观察缺失原件 | 只有载体存在且来源关联正确时才接受 | 同上 |
| U09 | 缺失原件重新出现 | 需要有明确的发现事件 | 同上 |
| U10 | 切换模型后恢复已有作品 | 保留原作品模型和检查点完整性 | `unit/test_model_settings.py` |
| U11 | 记忆分层返回部分结果，后续修复有效、无效、重复或格式错误 | 只重试缺失项；保留已验证结果与原事实，未解决项进入待处理队列 | `unit/test_memory_layers.py` |
| U12 | 签收、身份确认、进度倒退和重新核对 | 不得将同一人同时记为签收与未签收；新一轮核对须有正文依据 | `unit/test_core_boundaries.py` |
| U13 | 日期精度、无效日期、闰日和上下文长度限制 | 不凭空补充日期精度；无效日期被拒绝；上下文超限时记录省略 | 同上 |

## 端到端场景

`integration/test_browser_smoke.py::BrowserSmokeTests.test_create_generate_save_and_reload_offline` 使用真实浏览器、本地 HTTP 服务、写作引擎和临时作品目录：打开工作室 → 创建作品 → 查看预估 → 确认生成 → 检查正文 → 刷新并重新打开作品，验证章节仍可读取。模型回复由离线夹具提供；这验证的是软件流程，不评价真实模型的生成质量。

## 覆盖率与复现

基于 2026-11-07 拉取的 `280dd85`，在 Windows、Python 3.11、pytest 9.2.0、coverage.py 7.17.2 下测得：

| 测试范围 | 语句覆盖 | 分支覆盖 | 综合覆盖 |
| --- | ---: | ---: | ---: |
| 补测前 `tests/unit`，上述 8 个核心模块 | 50.35% | 33.93% | 45.31% |
| `tests/unit`，整个后端与引擎统计范围 | 38.79% | 27.21% | 35.18% |
| `tests/unit`，上述 8 个核心模块 | **60.32%** | 48.34% | 56.64% |
| `tests/unit` + 引擎回归，上述 8 个核心模块 | 68.17% | 54.83% | **64.08%** |

综合覆盖率采用 coverage.py 的语句与分支合计口径。核心模块的单元测试**语句覆盖率**达到 60%，但其分支覆盖率为 48.34%，语句与分支合计的综合覆盖率为 56.64%；64.08% 是单元测试与引擎回归合并后的综合结果。整个后端与引擎的单元测试覆盖没有达到 60%。`memory_runtime/memory_processing/pipeline.py`、`continuity.py` 等仍需继续补测。引擎回归有 3 项因缺少历史样本而跳过；测试代码与重复的 `memory_runtime/src/` 副本未计入统计分母。

从项目根目录运行：

```powershell
code\backend\.venv\Scripts\python.exe -m pip install -r tests\requirements.txt
code\backend\.venv\Scripts\python.exe -m playwright install chromium
$env:PYTHONPATH="$PWD\code\core_engine;$PWD\code\backend"
code\backend\.venv\Scripts\python.exe tests\run_coverage.py
code\backend\.venv\Scripts\python.exe -m unittest tests.integration.test_browser_smoke.BrowserSmokeTests.test_create_generate_save_and_reload_offline
```

覆盖率数据和 JSON 报告写入已忽略的 `code/backend/data/`；脚本分别对核心模块的单元测试语句覆盖率和合并后的综合覆盖率执行 60% 检查。GitHub 工作流会安装测试依赖和 Chromium 并执行该脚本。未安装 Playwright 或浏览器时端到端测试会跳过，不应记为通过。全量数据库测试需要独立配置 `TOME_TEST_DATABASE_URL`，不属于上述覆盖率统计。
