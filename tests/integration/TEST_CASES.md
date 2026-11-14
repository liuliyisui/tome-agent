# Tome Agent 集成测试用例

> 版本 v1.0 ｜ 依据：《Tome Agent 产品说明》《技术方案》《第 4 天第 1 部分实践任务》
> 被测系统：面向长篇小说创作的多智能体写作工作室
> 技术栈：Python 3.11+ / LangGraph 1.2.17 / unittest + pytest 9.2.0 / coverage.py 7.17.2
> 本文档范围：`tests/integration/` 下的集成测试与 E2E 冒烟用例（F-06~F-09）；单元用例见 [../unit/TEST_CASES.md](../unit/TEST_CASES.md)。

---

## 0. 测试范围与策略

### 0.1 被测边界

```text
[前端 Vue] --HTTP--> [Web 层 http.server] --> [应用服务 service] --> [写作引擎 WritingSession]
                                                                    planning → event → prose → memory → review
```

| 层 | 是否在本文档覆盖 | 说明 |
|---|---|---|
| 长文生成、检查点、导出（`service.generate` / `export_longform` / `export_markdown`） | ✅ 集成测试 | 临时作品目录 + 确定性写作会话替身 |
| 服务入口契约、参数校验、模型配置一致性 | ✅ 集成测试 | 不调用模型，断言异常与副作用 |
| 故障注入与断点恢复 | ✅ 集成测试 | 第 2 章返回 `NO_DRAFT`，验证已提交章节不丢失 |
| Web/API 与托管部署 | ✅ 集成测试（既有） | http.server 路由、账户隔离 |
| PostgreSQL 持久化 | ✅ 集成测试（需真实数据库） | `TOME_TEST_DATABASE_URL` 启用 |
| 浏览器交互（创建 → 生成 → 刷新） | ✅ E2E 冒烟（既有） | Playwright，离线夹具 |
| 输入校验、长度控制、证据绑定等纯函数 | ⭕ 单元测试 | 见 [../unit/TEST_CASES.md](../unit/TEST_CASES.md) |

### 0.2 确定性分层原则

- **必须精确断言**：章节编号与正文、检查点内容、Markdown 缩进、异常消息
- **必须交互断言**：失败时已提交章节仍可读取；越界请求不产生运行目录
- **禁止断言整段模型措辞**：替身写作会话返回固定正文
- **完全离线**：默认不联网、不读取真实 API Key、不调用付费模型

### 0.3 需求追溯矩阵（集成用例 ↔ 功能编号）

| 功能 | 名称 | 覆盖用例 |
|---|---|---|
| F-06 | 长文生成与 Markdown 导出 | IT-SVC-01~04、IT-FLOW-01、IT-EXP-01~03 |
| F-07 | 失败保留与断点恢复 | IT-FLOW-02~03、IT-FAULT-01~04 |
| F-08 | Web/API 契约 | IT-API-01~16（既有） |
| F-09 | 浏览器主流程冒烟 | E2E-01~03（既有） |

---

## 1. 测试环境与测试替身

### 1.1 环境矩阵

| 项 | 集成测试 | 浏览器冒烟 |
|---|---|---|
| Python | 3.11（CI）/ 3.12（本地） | 同左 |
| 模型 | `SuccessfulSession` / `FailingSecondChapter` | 离线夹具 |
| 存储 | `tmp_path` + 真实 `FileStore` | 临时作品目录 |
| 数据库 | `database.enabled() == False` | 同左 |
| 网络 | 禁止 | 仅 localhost |
| 标记 | `tests/integration` | `tests/integration/test_browser_smoke.py` |
| 单次耗时 | < 0.1s | 秒级 |

### 1.2 关键 Fixture 设计

```python
# tests/integration/test_story_flow_e2e.py —— 真正写检查点，不调用模型
class SuccessfulSession:
    def __init__(self, run, gateway, plan, book=None):
        self.run = Path(run)
        self.run.mkdir(parents=True, exist_ok=True)
        self.book = book or {"chapters": []}
        self.chapter_length_target = None
        self.book.setdefault("chapters", [])
        self.latest_checkpoint = self.run / "checkpoint_0.json"
        self.save()

    def write_next(self, instruction):
        number = len(self.book["chapters"]) + 1
        self.book["chapters"].append({...})
        self.latest_checkpoint = self.run / f"checkpoint_{number}.json"
        self.save()
        return {"status": "DRAFT_UNCHECKED", "chapter_number": number}
```

```python
# tests/integration/test_story_flow_e2e.py —— 故障注入替身
class FailingSecondChapter(SuccessfulSession):
    def write_next(self, instruction):
        if len(self.book["chapters"]) == 1:
            return {
                "status": "NO_DRAFT",
                "chapter_number": 2,
                "errors": ["模型连接超时"],
            }
        return super().write_next(instruction)
```

### 1.3 测试数据

| 数据集 | 条目 | 用途 |
|---|---|---|
| 作品规模 | 3 章 / 3000 字 | 场景法主流程 |
| 生成数量 | `count=2` | 主流程与失败注入 |
| 越界数量 | `count=0`、`count=4` | 参数边界 |
| 章节正文 | 固定两段中文正文 | 检查点与导出断言 |
| 导出语料 | 含 `\r\n`、全角空格、Unicode 行分隔符 | 段落缩进规范化 |

---

## 2. 集成测试用例

> 目录：`tests/integration/`；临时作品目录 + 确定性写作会话替身；全程离线。

### 2.1 服务入口契约（F-06）

| 用例编号 | 用例名称 | 前置 | 请求 / 输入 | 预期结果 | 优先级 |
|---|---|---|---|---|---|
| IT-SVC-01 | 默认生成入口走长文流程 | 已创建作品 | `generate is generate_longform` | 断言为同一函数 | P1 |
| IT-SVC-02 | 模型配置与作品不一致时拒绝 | 创建后切换模型 | `settings.public_config() != metadata.model` | 抛 `ValueError` | P0 |
| IT-SVC-03 | 章节数超出剩余范围 | 作品共 3 章 | `count=0` / `count=4` | 抛 `ValueError`，不产生运行目录 | P0 |
| IT-SVC-04 | 导出不修改原稿 | 作品含两段正文 | `export_markdown(book)` | 返回排版文本，`state["chapters"][0]["text"]` 不变 | P0 |

### 2.2 场景法：从创建作品到导出 Markdown（F-06/F-07）

**主场景（基本流）**

| 用例编号 | 用例名称 | 步骤 | 预期结果（含交互断言） | 优先级 |
|---|---|---|---|---|
| IT-FLOW-01 | 创建 → 生成两章 → 导出 | ① `create_book`（3 章 / 3000 字）② `generate(count=2)` ③ 读取检查点索引 ④ `export_markdown` | ① 元数据保留 3 章上限 ② 返回章节 `[1, 2]` ③ 检查点包含相同章节 ④ 导出含书名、两级标题、全角缩进段落 | P0 |
| IT-FLOW-02 | 备选流：后续章节失败 | ① 创建 ② 第 2 章返回 `NO_DRAFT` ③ `generate(count=2)` | 抛 `RuntimeError("第2章未生成正文")`；检查点仍保留第 1 章正文 | P0 |
| IT-FLOW-03 | 备选流：章节数越界 | 剩余 3 章 | `count=0` / `count=4` | 抛 `ValueError`；不产生 `longform-runs/` 目录 | P0 |

> 注：IT-FLOW-01 是本文件的关键业务流程用例，串起“创建 → 生成 → 检查点 → 导出”四个环节；IT-FLOW-02 验证失败时已提交章节不丢失，对应产品的“断点恢复”承诺。

```python
# tests/integration/test_story_flow_e2e.py 片段
def test_main_flow_create_generate_and_export_markdown(self):
    self.create()
    with patch.object(service, "WritingSession", SuccessfulSession):
        result = service.generate(
            self.book_id, count=2, gateway=object(), settings=self.settings
        )
    chapters = result["state"]["chapters"]
    self.assertEqual([item["number"] for item in chapters], [1, 2])
    self.assertEqual(self.checkpoint()["chapters"], chapters)
    markdown = service.export_markdown(result)
    self.assertIn("# 灯塔手记", markdown)
    self.assertIn("　　这是第1章的第一段。", markdown)
```

### 2.3 故障注入与恢复（F-07）

| 用例编号 | 用例名称 | 注入手法 | 预期结果 | 优先级 |
|---|---|---|---|---|
| IT-FAULT-01 | 第 2 章无正文 | 写作会话返回 `NO_DRAFT` | 抛错前已保存第 1 章；检查点可读取 | P0 |
| IT-FAULT-02 | 批量生成中途失败 | 第 2 章返回错误 | 第 1 章已落盘，后续章节未写入 | P0 |
| IT-FAULT-03 | 操作锁被崩溃进程遗留 | 锁文件记录已退出 PID | 锁可被回收 | P1 |
| IT-FAULT-04 | 锁被运行中进程持有 | 锁文件记录存活 PID | 新操作被阻塞 | P1 |

### 2.4 持久化与导出（F-06）

| 用例编号 | 用例名称 | 条件 | 预期结果 | 优先级 |
|---|---|---|---|---|
| IT-EXP-01 | Markdown 段落缩进 | 含 `\r\n`、全角空格、Unicode 行分隔符 | 每段前加两个全角空格；保留段落顺序；不改原稿 | P0 |
| IT-EXP-02 | 检查点索引安全 | 索引指向作品目录外 | 拒绝并抛 `ValueError` | P0 |
| IT-EXP-03 | 逐章持久化 | 生成 3 章 | 每章完成后检查点含对应章节 | P0 |

### 2.5 既有 Web/API 集成测试（摘要）

| 用例编号 | 范围 | 测试位置 | 覆盖要点 | 优先级 |
|---|---|---|---|---|
| IT-API-01~06 | Web API | `integration/test_web.py` | 创建/编辑/删除、估算与确认生成、任务进度、CORS | P0 |
| IT-API-07~08 | 托管部署 | `integration/test_hosted.py` | 账户隔离、工作区边界 | P0 |
| IT-API-09~16 | PostgreSQL | `integration/test_postgresql.py` | 版本回滚、会话锁、任务恢复（需真实数据库） | P1 |

---

## 3. 端到端（E2E）冒烟用例

> 工具：Playwright + 本地 HTTP 服务 + 离线夹具；文件 `tests/integration/test_browser_smoke.py`。

| 用例编号 | 场景 | 步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|
| E2E-01 | 浏览器主流程 | 打开工作室 → 创建作品 → 查看预估 → 确认生成 → 检查正文 → 刷新重开 | 章节仍可读取，正文与刷新前一致 | P0 |
| E2E-02 | 首次配置 | 首次打开，未配置模型 | 显示配置引导；密钥不回显 | P1 |
| E2E-03 | 创建校验 | 标题或构想留空后提交 | 行内提示，不发请求 | P1 |

---

## 4. 执行、门禁与已知缺陷

### 4.1 命令

```powershell
# 快速反馈（离线，秒级）
$env:PYTHONPATH="$PWD\code\core_engine;$PWD\code\backend"
.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/integration/test_story_flow_e2e.py

# 全量集成测试（含需要数据库的用例会按环境变量自动跳过）
.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/integration

# 覆盖率（含 60% 门槛检查，并生成 JSON）
.venv\Scripts\python.exe tests/run_coverage.py
```

### 4.2 CI 门禁

| 阶段 | 触发 | 执行 | 阻塞条件 |
|---|---|---|---|
| Integration | 每次 push | `pytest tests/integration`（跳过需真实资源用例） | 任一失败 |
| PostgreSQL | 每次 push | `test_postgresql`（PG 17/18） | 数据库集成失败 |
| Hosted | 每次 push | 账户与托管工作区测试 | 任一失败 |
| Browser | 每次 push | Playwright 冒烟 | 任一失败（未安装 Chromium 时跳过） |

### 4.3 已知缺陷与限制登记

| 编号 | 现象 | 影响 | 处理方式 |
|---|---|---|---|
| R-04 | 数据库集成需要真实 PostgreSQL | 默认离线测试不覆盖 | 使用 `TOME_TEST_DATABASE_URL` 单独运行 |
| R-05 | 浏览器冒烟需要 Playwright Chromium | 未安装时跳过 | CI 安装后再执行 |
| R-07 | 真实模型生成质量与耗时不在集成测试范围 | 只验证结构与持久化 | 由 `tests/eval/` 单独评测 |

### 4.4 用例统计

| 层级 | 用例数 | P0 | P1 | 测试方法数 |
|---|---:|---:|---:|---:|
| 集成测试 §2.1 服务入口契约 | 4 | 3 | 1 | 既有 + 新增 |
| 集成测试 §2.2 场景法主流程 | 3 | 3 | 0 | 3（新增） |
| 集成测试 §2.3 故障注入与恢复 | 4 | 2 | 2 | 既有 + 新增 |
| 集成测试 §2.4 持久化与导出 | 3 | 3 | 0 | 既有 + 新增 |
| 集成测试 §2.5 既有 Web/API | 16 | 12 | 4 | 既有 |
| E2E 冒烟 §3 | 3 | 1 | 2 | 3（既有） |
| **合计** | **33** | **24** | **9** | **3 个新增方法 + 既有用例** |

> 新增的 3 个方法位于 `test_story_flow_e2e.py`，覆盖基本流与两个备选流；全部离线、可重复执行。单元用例统计见 [../unit/TEST_CASES.md](../unit/TEST_CASES.md)。

---

## 附录 A：本目录结构

```text
tests/integration/
├── TEST_CASES.md                       # 本文件
├── README.md
├── test_story_flow_e2e.py              # IT-FLOW-01~03（新增）
├── test_service.py                     # IT-SVC、IT-FAULT（既有）
├── test_web.py                         # IT-API（既有）
├── test_hosted.py                      # 托管部署（既有）
├── test_postgresql.py                  # 数据库集成（既有）
└── test_browser_smoke.py               # E2E-01~03（既有）
```
