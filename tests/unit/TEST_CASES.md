# Tome Agent 单元测试用例

> 版本 v1.0 ｜ 依据：《Tome Agent 产品说明》《技术方案》《第 4 天第 1 部分实践任务》
> 被测系统：面向长篇小说创作的多智能体写作工作室
> 技术栈：Python 3.11+ / LangGraph 1.2.17 / unittest + pytest 9.2.0 / coverage.py 7.17.2
> 本文档范围：`tests/unit/` 下的单元测试用例（F-01~F-05）；集成与 E2E 用例见 [../integration/TEST_CASES.md](../integration/TEST_CASES.md)。

---

## 0. 测试范围与策略

### 0.1 被测边界

```text
[前端 Vue] --HTTP--> [Web 层 http.server] --> [应用服务 service] --> [写作引擎 WritingSession]
                                                                    planning → event → prose → memory → review
```

| 层 | 是否在本文档覆盖 | 说明 |
|---|---|---|
| 输入校验（`service.create_book`） | ✅ 单元测试 | 纯校验，精确断言，等价类 + 边界值 |
| 长度控制（`memory_runtime.length_control`） | ✅ 单元测试 | 容差规则与降级路径，FakeGateway 隔离模型 |
| 证据绑定（`inf_writer.domain.checked_support`） | ✅ 单元测试 | 纯函数，精确断言引文与偏移 |
| 支持审核（`inf_writer.domain.validate_support_review`） | ✅ 单元测试 | 纯函数，检查覆盖与状态 |
| 事件、连续性、记忆分层（`event_first` / `continuity` / `tiered_memory`） | ✅ 单元测试（既有） | 状态机与契约校验 |
| 长文生成、检查点、导出（`service.generate` / `export_markdown`） | ⭕ 集成测试 | 见 [../integration/TEST_CASES.md](../integration/TEST_CASES.md) |
| 浏览器交互（创建 → 生成 → 刷新） | ⭕ E2E 冒烟 | 见 [../integration/TEST_CASES.md](../integration/TEST_CASES.md) |
| 真实模型质量、性能、真实 PostgreSQL | ⭕ 专项测试 | 不在默认门禁 |

### 0.2 确定性分层原则

- **必须精确断言**：输入区间边界、拒绝原因、长度调整报告字段
- **必须交互断言**：长度已在容差内时 `gateway.requests == []`；无效输入不得写出作品目录
- **禁止断言整段模型措辞**：模型输出只断言结构与属性（章节号、调整前后字数）
- **完全离线**：默认不联网、不读取真实 API Key、不调用付费模型

### 0.3 需求追溯矩阵（单元用例 ↔ 功能编号）

| 功能 | 名称 | 覆盖用例 |
|---|---|---|
| F-01 | 作品创建与输入校验 | UT-BOOK-01~17、BV-C01~06、BV-T01~06 |
| F-02 | 章节长度控制 | UT-LEN-01~12 |
| F-03 | 记忆证据绑定 | UT-DOM-01~16 |
| F-04 | 支持审核 | UT-REV-01~09 |
| F-05 | 事件先行、连续性、记忆分层、草稿与计划 | UT-EVT、UT-CONT、UT-MEM、UT-DRAFT、UT-PLAN、UT-TITLE |

---

## 1. 测试环境与测试替身

### 1.1 环境矩阵

| 项 | 单元测试 |
|---|---|
| Python | 3.11（CI）/ 3.12（本地） |
| 模型 | FakeGateway / 固定回复 |
| 存储 | `tmp_path` + `patch BOOKS` |
| 数据库 | `database.enabled() == False` |
| 网络 | 禁止 |
| 标记 | `tests/unit` |
| 单次耗时 | < 0.1s |

### 1.2 关键 Fixture 设计

```python
# tests/unit/test_book_input_validation.py —— 隔离作品目录与数据库
class BookInputValidationTests(unittest.TestCase):
    def setUp(self):
        self._folder = tempfile.TemporaryDirectory()
        self.books = Path(self._folder.name)
        self._patches = [
            patch.object(service, "BOOKS", self.books),
            patch.object(service.database, "enabled", return_value=False),
        ]
        for item in self._patches:
            item.start()
        self.settings = Settings(api_key="fake")
```

```python
# tests/unit/test_length_control.py —— 记录调用次数，区分“容差内不调用”
class FakeGateway:
    def __init__(self, reply=None, error=None):
        self.reply = reply
        self.error = error
        self.requests = []

    def complete(self, request):
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return self.reply
```

### 1.3 测试数据

| 数据集 | 条目 | 用途 |
|---|---|---|
| 章节数合法值 | 1、50、100 | 有效等价类与上下边界 |
| 章节数非法值 | 0、-1、101、1.5、"10"、True、None | 无效等价类 |
| 篇幅合法值 | 500、1000、200000 | 有效等价类与上下边界 |
| 篇幅非法值 | 499、-1、200001、500.0、"5000"、True、None | 无效等价类 |
| 空标题/空构想 | ""、"   "、None、非字符串 | 必填字段防御 |
| 长度控制语料 | 899 / 900 / 1100 / 1101 汉字 | 容差边界 |
| 证据语料 | "第一行证据。\n第二行证据。" | 证据 ID 与引文定位 |

---

## 2. 单元测试用例

> 目录：`tests/unit/`；全部离线，单用例 < 100ms。

### 2.1 `service.create_book` —— 作品输入校验（F-01）

被测函数：`create_book(book_id, title, prompt, chapters, target_units, ...)`

**等价类划分**

| 用例编号 | 用例名称 | 前置 | 输入 | 预期结果 | 优先级 |
|---|---|---|---|---|---|
| UT-BOOK-01 | 章节数有效下限 | 已进入新建作品 | `chapters=1` | 创建成功，`target_chapters == 1` | P0 |
| UT-BOOK-02 | 章节数有效中间值 | 同上 | `chapters=50` | 创建成功 | P1 |
| UT-BOOK-03 | 章节数有效上限 | 同上 | `chapters=100` | 创建成功 | P0 |
| UT-BOOK-04 | 章节数下限外 | 同上 | `chapters=0` | 抛 `ValueError`，不创建目录 | P0 |
| UT-BOOK-05 | 章节数为负数 | 同上 | `chapters=-1` | 抛 `ValueError`，不创建目录 | P0 |
| UT-BOOK-06 | 章节数上限外 | 同上 | `chapters=101` | 抛 `ValueError`，不创建目录 | P0 |
| UT-BOOK-07 | 章节数为小数 | 同上 | `chapters=1.5` | 抛 `ValueError` | P0 |
| UT-BOOK-08 | 章节数为字符串 | 同上 | `chapters="10"` | 抛 `ValueError` | P0 |
| UT-BOOK-09 | 章节数为布尔值 | 同上 | `chapters=True` | 抛 `ValueError` | P0 |
| UT-BOOK-10 | 章节数为空值 | 同上 | `chapters=None` | 抛 `ValueError` | P0 |
| UT-BOOK-11 | 篇幅有效下限 | 同上 | `target_units=500` | 创建成功 | P0 |
| UT-BOOK-12 | 篇幅有效中间值 | 同上 | `target_units=1000` | 创建成功 | P1 |
| UT-BOOK-13 | 篇幅有效上限 | 同上 | `target_units=200000` | 创建成功 | P0 |
| UT-BOOK-14 | 篇幅下限外 | 同上 | `target_units=499` | 抛 `ValueError` | P0 |
| UT-BOOK-15 | 篇幅上限外 | 同上 | `target_units=200001` | 抛 `ValueError` | P0 |
| UT-BOOK-16 | 篇幅类型错误 | 同上 | `500.0` / `"5000"` / `True` / `None` | 抛 `ValueError` | P0 |
| UT-BOOK-17 | 标题或构想为空 | 同上 | `""` / `"   "` / `None` / `123` | 抛 `ValueError`，不创建目录 | P0 |

**边界值分析（`chapters` 与 `target_units`）**

| 用例编号 | 用例名称 | 输入 | 预期结果 | 优先级 |
|---|---|---|---|---|
| BV-C01 | 章节下边界外 | `chapters=0` | 拒绝，无作品目录 | P0 |
| BV-C02 | 章节下边界 | `chapters=1` | 创建成功 | P0 |
| BV-C03 | 章节下边界内侧 | `chapters=2` | 创建成功 | P1 |
| BV-C04 | 章节上边界内侧 | `chapters=99` | 创建成功 | P1 |
| BV-C05 | 章节上边界 | `chapters=100` | 创建成功 | P0 |
| BV-C06 | 章节上边界外 | `chapters=101` | 拒绝，无作品目录 | P0 |
| BV-T01 | 篇幅下边界外 | `target_units=499` | 拒绝，无作品目录 | P0 |
| BV-T02 | 篇幅下边界 | `target_units=500` | 创建成功 | P0 |
| BV-T03 | 篇幅下边界内侧 | `target_units=501` | 创建成功 | P1 |
| BV-T04 | 篇幅上边界内侧 | `target_units=199999` | 创建成功 | P1 |
| BV-T05 | 篇幅上边界 | `target_units=200000` | 创建成功 | P0 |
| BV-T06 | 篇幅上边界外 | `target_units=200001` | 拒绝，无作品目录 | P0 |

> 注 1：UT-BOOK-09 与 UT-BOOK-16 是关键反转用例。Python 中 `True` 是 `int` 的子类，若只用 `isinstance(value, int)` 会把 `True` 当作 1 接受，因此实现使用 `type(value) is not int` 严格判断。
>
> 注 2：所有拒绝用例同时断言作品目录不存在，防止“先建目录再校验”留下半成品。

```python
# tests/unit/test_book_input_validation.py 片段
def test_target_units_boundary_values(self):
    cases = (
        (499, False),
        (500, True),
        (501, True),
        (199999, True),
        (200000, True),
        (200001, False),
    )
    for index, (value, valid) in enumerate(cases):
        with self.subTest(value=value):
            name = f"target-boundary-{index}"
            if valid:
                book = self.create(name, target=value)
                self.assertEqual(book["metadata"]["target_units"], value)
            else:
                with self.assertRaises(ValueError):
                    self.create(name, target=value)
                self.assertFalse((self.books / name).exists())
```

### 2.2 `length_control.adjust` —— 章节长度控制（F-02）

被测函数：`adjust(draft, target, book, number, gateway, trace, *, stage_task=None) -> (draft, report)`

容差区间：`max(1, floor(target * 0.9)) <= actual <= ceil(target * 1.1)`

| 用例编号 | 用例名称 | 前置 | 输入 | 预期结果 | 优先级 |
|---|---|---|---|---|---|
| UT-LEN-01 | 汉字计数只统计 CJK | 无 | `""`、"你好，世界！"、"abc123"、"㐀" | 分别为 0、4、0、1 | P1 |
| UT-LEN-02 | 容差下限内不调整 | FakeGateway 就绪 | target=1000，actual=900 | `adjustment == "not_needed"`，调用 0 次 | P0 |
| UT-LEN-03 | 下限外触发调整 | 同上 | target=1000，actual=899 | 调用 1 次 | P0 |
| UT-LEN-04 | 容差上限内不调整 | 同上 | target=1000，actual=1100 | `not_needed`，调用 0 次 | P0 |
| UT-LEN-05 | 上限外触发调整 | 同上 | target=1000，actual=1101 | 调用 1 次 | P0 |
| UT-LEN-06 | 极小目标仍保留非空容差 | 同上 | target=1，actual=1/2 | `not_needed` | P1 |
| UT-LEN-07 | 更接近目标的回复被接受 | 同上 | actual=500，回复 1000 字 | 返回新稿，`after=1000`，`accepted` | P0 |
| UT-LEN-08 | 更差的回复被丢弃 | 同上 | actual=500，回复 400 字 | 返回原稿，`kept_original_no_improvement` | P0 |
| UT-LEN-09 | 上下文超限不调用模型 | 同上 | constraints 约 9 万汉字 | 返回原稿，`kept_original_context_limit` | P1 |
| UT-LEN-10 | 模型异常降级 | 同上 | gateway 抛 `RuntimeError` | 返回原稿，`kept_original_failure`，记录 `error_type` | P0 |
| UT-LEN-11 | 未完成回复降级 | 同上 | `finish_reason="length"` | 返回原稿，`kept_original_incomplete_reply` | P0 |
| UT-LEN-12 | 空回复降级 | 同上 | 回复为空白 | 返回原稿，`kept_original_no_improvement` | P1 |

> 注：UT-LEN-03 与 UT-LEN-05 分别只比边界多 1 个汉字，用于守住“边界值本身应通过、边界外应触发”的规则。

```python
# tests/unit/test_length_control.py 片段
def test_lower_tolerance_boundary_is_kept(self):
    draft = "汉" * 900
    gateway = FakeGateway(Reply(draft))
    result, trace = self.adjust(draft, 1000, gateway)
    self.assertEqual(result[0], draft)
    self.assertEqual(result[1]["adjustment"], "not_needed")
    self.assertEqual(gateway.requests, [])
    self.assertEqual(trace, [])
```

### 2.3 `domain.checked_support` —— 证据绑定（F-03）

被测函数：`checked_support(support, draft, value=None, check_value=True, retire=False, resolved=False)`

| 用例编号 | 用例名称 | 前置 | 输入 | 预期结果 | 优先级 |
|---|---|---|---|---|---|
| UT-DOM-01 | 合法主张规范化 | 正文含两段证据 | 1 条 claim + 1 条证据 | 返回 claim 与引文 | P0 |
| UT-DOM-02 | support 必须为非空列表 | 无 | `None`、`{}`、`[]`、17 条 | 抛 `ContractError` | P0 |
| UT-DOM-03 | 重复主张标签被拒绝 | 无 | 两个 "结论A" | 抛 `ContractError` | P0 |
| UT-DOM-04 | claim 字段必须精确 | 无 | 缺 claim / 缺 evidence / 多余字段 | 抛 `ContractError` | P0 |
| UT-DOM-05 | 每条主张 1~8 条证据 | 无 | 0 条、9 条 | 抛 `ContractError` | P0 |
| UT-DOM-06 | 未知 evidence_id 被拒绝 | 无 | `e9999` | 抛 `ContractError` | P0 |
| UT-DOM-07 | 引文不在证据片段内 | 无 | 不存在的句子 | 抛 `ContractError` | P0 |
| UT-DOM-08 | 未解析时允许匹配的偏移 | 无 | start=0，end=5 | 通过并保留偏移 | P1 |
| UT-DOM-09 | 偏移必须成对出现 | 无 | 只有 start | 抛 `ContractError` | P0 |
| UT-DOM-10 | 已解析偏移必须匹配原文 | 无 | start=1，end=6 | 抛 `ContractError` | P0 |
| UT-DOM-11 | 已解析时缺少字段被拒绝 | 无 | 缺少 start/end | 抛 `ContractError` | P1 |
| UT-DOM-12 | 同一主张内重复证据被拒绝 | 无 | 两条相同证据 | 抛 `ContractError` | P0 |
| UT-DOM-13 | retire 要求空值与单条主张 | 无 | 非空值 / 多条主张 | 抛 `ContractError` | P0 |
| UT-DOM-14 | 字符串值必须等于单条主张 | 无 | 值 "另一个结论" | 抛 `ContractError` | P0 |
| UT-DOM-15 | 列表值必须按序匹配主张 | 无 | 多出或缺失结论 | 抛 `ContractError` | P0 |
| UT-DOM-16 | 可关闭值检查 | 无 | `check_value=False` | 忽略 value 差异 | P1 |

### 2.4 `domain.validate_support_review` —— 支持审核（F-04）

被测函数：`validate_support_review(result, context)`

| 用例编号 | 用例名称 | 前置 | 输入 | 预期结果 | 优先级 |
|---|---|---|---|---|---|
| UT-REV-01 | 每项预期检查都存在 | context 含 claim 与 removal | 两条检查 | 原样返回 | P0 |
| UT-REV-02 | 缺少任一检查被拒绝 | 同上 | 只有 claim | 抛 `ContractError` | P0 |
| UT-REV-03 | support_checks 必须为列表 | 同上 | `{}` | 抛 `ContractError` | P0 |
| UT-REV-04 | 每条检查仅允许三个字段 | 同上 | 缺 reason / 多字段 | 抛 `ContractError` | P0 |
| UT-REV-05 | 未知引用被拒绝 | 同上 | `memory_9/claim_9` | 抛 `ContractError` | P0 |
| UT-REV-06 | 重复引用被拒绝 | 同上 | 同一 ref 两次 | 抛 `ContractError` | P0 |
| UT-REV-07 | 非法状态被拒绝 | 同上 | `maybe` | 抛 `ContractError` | P0 |
| UT-REV-08 | 部分支持不得批准或标记充分 | 同上 | `partial` + `approved` / `sufficient` | 抛 `ContractError` | P0 |
| UT-REV-09 | 部分支持但未批准可返回 | 同上 | `unsupported`，无 approved | 原样返回 | P1 |

### 2.5 既有核心逻辑用例（F-05）

| 用例编号 | 模块 | 测试位置 | 覆盖要点 | 优先级 |
|---|---|---|---|---|
| UT-EVT-01~08 | 事件先行与状态一致性 | `unit/test_event_consistency.py` | 计划不自动成为事实、未知事件拒绝、版本冲突 | P0 |
| UT-CONT-01~11 | 连续性状态机 | `unit/test_core_boundaries.py` | 时间倒退、原件缺失、照片载体、进度回退 | P0 |
| UT-MEM-01~05 | 记忆分层与修复 | `unit/test_memory_layers.py` | 部分结果只修复缺失项 | P0 |
| UT-DRAFT-01~15 | 写作草稿与审核 | `unit/test_drafting.py` | 证据解析、空稿拒绝、审核失败继续 | P0 |
| UT-PLAN-01~03 | 作品计划边界 | `unit/test_plan_bounds.py` | 未来事件不能改动当前或过去章节 | P1 |
| UT-TITLE-01~06 | 章节标题清洗 | `unit/test_title_sanitization.py` | 指令回声、回退标题 | P1 |

### 2.6 单元测试执行与覆盖门槛

```bash
pytest tests/unit -q --cov=code/backend/inf_backend --cov=code/core_engine/inf_writer --cov=code/core_engine/memory_runtime
```

| 模块范围 | 目标语句覆盖 | 实测语句覆盖 | 实测分支覆盖 | 实测综合覆盖 |
|---|---|---|---|---|
| 8 个核心模块（`run_coverage.py` 定义） | ≥ 60% | **63.58%** | 52.72% | **60.25%** |
| 8 个核心模块 + 引擎回归 | ≥ 60% | **70.57%** | 58.24% | **66.79%** |
| 整个后端与引擎范围 | — | 39.43% | 28.55% | 36.08% |

> 核心模块指 `writing.py`、`event_first.py`、`pipeline.py`、`continuity.py`、`graph_runtime.py`、`domain.py`、`agents.py`、`tiered_memory.py`。综合覆盖率为 coverage.py 的语句与分支合计口径，由 `tests/run_coverage.py` 自动检查并写入 `code/backend/data/`。

---

## 3. 执行、门禁与已知缺陷

### 3.1 命令

```powershell
$env:PYTHONPATH="$PWD\code\core_engine;$PWD\code\backend"
.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/unit
.venv\Scripts\python.exe tests/run_coverage.py
```

### 3.2 CI 门禁

| 阶段 | 触发 | 执行 | 阻塞条件 |
|---|---|---|---|
| Lint | 每次 push | ruff check / format | 任一失败 |
| Unit | 每次 push | `unittest discover` + `pytest tests/unit` | 任一失败 |
| Coverage | 每次 push | `tests/run_coverage.py` | 核心模块语句覆盖 < 60% 或合并综合覆盖 < 60% |

### 3.3 已知缺陷与限制登记

| 编号 | 现象 | 影响 | 处理方式 |
|---|---|---|---|
| R-01 | 3 项引擎回归依赖未随仓库提供的历史运行样本 | 本机跳过 | 记录为 `skip`，不记为通过 |
| R-02 | 核心模块分支覆盖率 52.72%，低于语句覆盖率 | 部分异常分支未被覆盖 | 后续按 `missing_branches` 补测 |
| R-03 | 整个后端与引擎范围覆盖率 36.08% | 非核心辅助模块覆盖不足 | 核心门禁只约束 8 个核心模块 |
| R-06 | 无 `xfail(strict=True)` 用例 | 已知问题以 R-01~R-05 登记 | 修复后更新本表 |

### 3.4 用例统计

| 层级 | 用例数 | P0 | P1 | 测试方法数 |
|---|---:|---:|---:|---:|
| 单元测试 §2.1 输入校验（含边界值） | 29 | 23 | 6 | 7 |
| 单元测试 §2.2 长度控制 | 12 | 8 | 4 | 12 |
| 单元测试 §2.3 证据绑定 | 16 | 12 | 4 | 16 |
| 单元测试 §2.4 支持审核 | 9 | 8 | 1 | 9 |
| **合计** | **66** | **51** | **15** | **44 个新增方法 + 既有用例** |

> 以上 44 个新增测试方法全部离线、可重复执行；等价类与边界值覆盖 `chapters`、`target_units` 两个输入字段。集成与 E2E 用例统计见 [../integration/TEST_CASES.md](../integration/TEST_CASES.md)。

---

## 附录 A：本目录结构

```text
tests/unit/
├── TEST_CASES.md                       # 本文件
├── README.md
├── test_book_input_validation.py       # UT-BOOK-01~17、BV-C/T
├── test_length_control.py              # UT-LEN-01~12
├── test_domain_support_contract.py     # UT-DOM-01~16、UT-REV-01~09
├── test_core_boundaries.py             # UT-CONT（既有）
├── test_core.py                        # 领域事务（既有）
├── test_drafting.py                    # UT-DRAFT（既有）
├── test_event_consistency.py           # UT-EVT（既有）
├── test_memory_layers.py               # UT-MEM（既有）
└── test_plan_bounds.py                 # UT-PLAN（既有）
```
