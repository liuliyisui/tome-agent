# Tome Agent 测试用例文档总览

测试用例文档按测试层级拆分，并与对应的测试代码同目录存放。

| 文档 | 层级 | 覆盖功能 | 用例数 |
|---|---|---|---|
| [unit/TEST_CASES.md](unit/TEST_CASES.md) | 单元测试 | F-01 输入校验、F-02 长度控制、F-03 证据绑定、F-04 支持审核、F-05 既有核心逻辑 | 66 |
| [integration/TEST_CASES.md](integration/TEST_CASES.md) | 集成测试 + E2E | F-06 长文生成与导出、F-07 失败保留与恢复、F-08 Web/API、F-09 浏览器冒烟 | 17 + 既有 API 16 |

## 共同约定

- 依据：《Tome Agent 产品说明》《技术方案》《第 4 天第 1 部分实践任务》
- 技术栈：Python 3.11+ / unittest + pytest 9.2.0 / coverage.py 7.17.2 / Playwright
- 默认完全离线，不联网、不读取真实 API Key、不调用付费模型
- 核心 8 模块综合覆盖率 **60.25%**（语句 63.58% / 分支 52.72%），满足 ≥ 60% 要求
- 本期设计用例合计 **83 条**：单元 66 + 集成场景 14 + E2E 3；其中 47 个新增测试方法

## 快速执行

```powershell
$env:PYTHONPATH="$PWD\code\core_engine;$PWD\code\backend"
.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/unit tests/integration/test_story_flow_e2e.py
.venv\Scripts\python.exe tests/run_coverage.py
```
