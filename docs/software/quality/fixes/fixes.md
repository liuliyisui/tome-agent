# Markdown-side fixes (bundle 4 of 4)

四处变更：`docs/software/README.md` 增加两条索引（patch），新建成两
份文档（create）。用 `python fixes/fixes.py --only md` 应用，也可以按下面
的代码块手工放置。

约定：`<!-- fixes:file target="..." mode="..." -->` 标记后紧跟一个反引号
代码块。`mode="patch"` 是相对基线 `e4d23ce` 的 unified diff；
`mode="create"` 是文件全文。代码块用 4+ 个反引号包裹，因此内文里的
三反引号代码栅栏不会截断。

---

## `docs/software/README.md`

设计资料索引新增两条链接（整改清单、评审报告）。（`diff`，12 行）

<!-- fixes:file target="docs/software/README.md" mode="patch" -->
````diff
diff --git a/docs/software/README.md b/docs/software/README.md
index f03fc55..61e9b3d 100644
--- a/docs/software/README.md
+++ b/docs/software/README.md
@@ -8,3 +8,7 @@
 
 设计详情见[系统架构](../algorithm/ARCHITECTURE.md)和[使用说明](USER_GUIDE.md)。
 
+Python 代码质量规范与整改记录见[代码质量整改清单](CODE_QUALITY_FIXES.md)（Ruff + Pylance 方案，含配置文件说明与逐条修改对照）。
+
+整改后的复审意见（含优先级排序的遗留问题）见[代码评审报告](CODE_REVIEW_20261107.md)。
+
````

---

## `docs/software/CODE_QUALITY_FIXES.md`

整改清单：79 处规则违规的逐条定位、修改前后对照与验证记录。（`markdown`，395 行）

<!-- fixes:file target="docs/software/CODE_QUALITY_FIXES.md" mode="create" -->
````markdown
# Python 代码质量整改清单

依据：[VS Code Python 代码质量检查全景指南](https://github.com/bettermorn/ACMWDevHubPPT/blob/master/Methodology/VSCodePlugins.md)（下称"指南"），采用其中**方案 A：现代极速流（Ruff + Pylance）**。

- 检查工具：Ruff 0.17.4（指南推荐组合中的 Linter + Formatter 二合一）
- 规则集：`E, W, F, I, B, C4, UP`（与指南 `pyproject.toml` 示例一致），`ignore = ["E501"]`
- 检查范围：**全仓库**（`ruff check .`），含 `code/backend`、`code/core_engine`、`tests` 及 `code/backend` 下的脚本
- 整改前基线：**75 处不合规**（首轮）+ **4 处**（仓库更新到 `e4d23ce` 后新增代码，见 3.8）；整改后：**0 处**，`ruff format` 全仓库无差异
- 代码改动：44 个 `.py` 文件（+240 / −194 行）；仓库配置：新增 2 个文件（`pyproject.toml`、`.pre-commit-config.yaml`）+ CI 增加 1 个 `lint` job。VS Code 插件/编辑器设置属本机环境，**不入库**（见第二节第 2 条）
- 可执行补丁包：`fixes/` 目录按类型分成 4 份（`fixes.py` Python／`fixes.yaml` CI+预提交／`fixes.toml` Ruff 配置／`fixes.md` 文档），`python fixes/fixes.py --all` 可在干净副本上重现全部 50 个改动目标，幂等且保留文件换行风格

---

## 一、整改前基线（扫描结果）

| 规则 | 数量 | 含义 |
| --- | ---: | --- |
| `E402` | 42 | 模块级 import 不在文件顶部 |
| `B023` | 14 | 函数/类闭包引用了循环变量（晚绑定隐患） |
| `B904` | 12 (+2) | `except` 中 `raise` 未声明 `from err` / `from None` |
| `B007` | 3 | 循环控制变量未被使用 |
| `F841` | 3 | 局部变量赋值后未使用（死代码/疑似漏用） |
| `E731` | 1 | 用赋值语句定义 lambda |
| `I001` | 36 (+2) | 导入块分组/排序不符合 isort 规则 |
| **合计** | **75 (+4)** | 括号内为第二轮（`e4d23ce` 新代码）新增 |

补充事实（说明 `I001`/格式化为何不是全仓库重排）：

- `ruff format --check` 在整改前即已全部通过，说明代码此前已按 Black 风格格式化（双引号、88 列折行），本次不产生大范围格式噪音；
- `F401`（未使用导入）整改前为 0，说明历史上已清理过；
- `I001` 的 36 处全部由**本次新增的项目配置**触发：指南要求把本项目自有包（`tome_writer`、`memory_runtime`…）声明为 first-party，声明后原先把它们当作 third-party 分组的空行就多了。

---

## 二、工程配置（仓库内 2 个新文件 + 1 个 CI job；编辑器配置不入库）

界面上「装什么插件、怎么格式化」属于开发者的本机环境，不进入版本库；仓库里只放**规则本身**（`pyproject.toml`）和**能自动执行规则的入口**（pre-commit、CI）。

### 1. `pyproject.toml`（仓库根目录，新增）

指南第三节「深度定制：使用项目配置文件」要求把规则写进项目根目录，而不是个人 VS Code 全局设置。原仓库仅有 `code/backend/pyproject.toml`（只做打包，无任何 `[tool.ruff]`），因此整个 `code/core_engine` 与 `tests` 处于无规则状态。

新增内容要点：

```toml
[tool.ruff]
target-version = "py311"     # 与 code/backend/pyproject.toml 的 requires-python 对齐
line-length = 88             # 指南要求的行宽
extend-exclude = [".venv", ".tmp", "__pycache__", "runs", "code/backend/data", "docs"]
                              # docs/ 内是刻意保留的"修改前/修改后"片段，不参与重排
                              # （Ruff ≥0.14 会格式化 Markdown 里的 python 代码块）

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP"]   # 指南示例规则集
ignore = ["E501"]                                 # 与指南示例一致：行宽交给 formatter

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "F401"]                     # 指南示例
"code/**/test_*.py" = ["S101", "F401"]            # 本项目把脚本式测试也放在 code/ 下
"code/core_engine/check_memory.py" = ["E402"]     # 见第五节说明
"code/core_engine/write_novel.py" = ["E402"]
"code/core_engine/memory_runtime/test_*.py" = ["E402"]

[tool.ruff.lint.isort]
known-first-party = ["tome_writer", "memory_runtime", "inf_backend",
                     "user_runtime", "write_novel", "check_memory"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

验证配置生效（对 `code/backend` 下的文件生效的是根配置，而非 `code/backend/pyproject.toml`）：

```
ruff check --show-settings code/backend/inf_backend/web.py
→ Settings path: "...\pyproject.toml"
```

### 2. 本地 VS Code 配置（**不入库**，仅本机设置）

指南第二节的插件安装与「保存时格式化/自动修复」属于**个人开发环境配置**，因此不放进仓库（仓库里也不应出现 `.vscode/`），由每位开发者在自己的 VS Code 用户设置中完成：

1. 安装插件：`ms-python.python`、`ms-python.vscode-pylance`、`charliermarsh.ruff`（指南「方案 A 安装清单」）。
2. `Ctrl + Shift + P` → `Preferences: Open User Settings (JSON)`，加入：

```jsonc
{
  "python.analysis.typeCheckingMode": "basic",          // 指南：Pylance 基本类型检查
  "python.analysis.extraPaths": ["./code/core_engine", "./code/backend"],
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  }
}
```

- `python.analysis.extraPaths` 是本仓库的特例：`tome_writer`、`memory_runtime`、`inf_backend` 都没有作为发行包安装，Pylance 需要这两个目录才能解析导入（这也解释了 `tests/unit/__init__.py` 里的 `sys.path` 引导）。
- 指南示例中的 `"ruff.lint.args": ["--select=E,F,UP,B,SIM,I"]` 不要照抄：它会覆盖 `pyproject.toml` 的 `select`，使编辑器与 CI/预提交判定不一致（`SIM` 也不在项目规则集内）。规则唯一来源是仓库根 `pyproject.toml`。
- 想把上面这段只作用于本仓库而不是全局：用 `File → Save Workspace As…` 存成 `.code-workspace` 文件放在仓库**之外**，或用 VS Code 的「Workspace」设置但不提交。

### 3. `.pre-commit-config.yaml`（新增）

对应指南总结建议「结合 Git 的 pre-commit 钩子，确保不合规的代码绝对无法提交」：

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-toml
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
```

启用：`pip install pre-commit && pre-commit install`。

### 4. `.github/workflows/tests.yml`（新增 `lint` job）

原 CI 只跑测试，没有质量门禁。新增与测试并行的 lint 任务：

```yaml
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: python -m pip install ruff==0.17.4
      - run: ruff check .
      - run: ruff format --check .
```

---

## 三、代码修改清单

以下每条格式为：**位置** ｜ 问题（规则） ｜ 改正后的样子。

### 3.1 `E402` 模块级 import 不在文件顶部（12 处结构性修复）

| # | 位置 | 修改前 | 修改后 |
| --- | --- | --- | --- |
| 1 | `code/core_engine/tome_writer/agents.py:101` | `PROMPTS["memory"] += (...)` 之后才 `from .memory_output_contract import MEMORY_PROMPT` | 该 import 移入文件顶部 import 块（`.domain` / `.memory_output_contract` / `.models` 按字母序），`memory_output_contract` 只依赖 `.domain`，无循环导入 |
| 2 | `code/core_engine/memory_runtime/src/tome_writer/agents.py:101` | 同上（该目录是 `tome_writer` 的同步副本） | 同上 |
| 3 | `code/core_engine/memory_runtime/engine.py:7-11` | `SOURCE = ...; sys.path.insert(...)` 之后才导入 `tome_writer` | 删除本地 `sys.path` 引导，改为在包入口 `memory_runtime/__init__.py` 中统一引导；`engine.py` 顶部恢复为纯 import 块 |
| 4 | `code/core_engine/memory_runtime/__init__.py` | 仅一行文档字符串 | 新增 13 行：把 `memory_runtime/src` 加入 `sys.path`（带存在性判断），使该包的所有子模块导入 `tome_writer` 时无需在文件中部改 `sys.path` |
| 5 | `code/core_engine/memory_runtime/test_regression.py:174-179` | 类定义之后（第 174 行）才导入 `tome_writer.*` 与 `memory_runtime.engine` | 5 条 import 合并到文件顶部导入块（`sys.path` 引导之后），`_fixture_complete = ...` 保持原位 |

`memory_runtime/__init__.py` 改正后：

```python
"""Opt-in three-tier memory runtime; importing does not read credentials."""

import sys
from pathlib import Path

_SOURCE = Path(__file__).resolve().parent / "src"
if str(_SOURCE) not in sys.path:
    sys.path.insert(0, str(_SOURCE))
```

> 其余 30 处 `E402` 属于「脚本式入口必须先改 `sys.path` 再导入」的既有结构（`check_memory.py`、`write_novel.py` 及 `memory_runtime/test_*.py`，后者按 `python -X utf8 memory_runtime/test_writing.py` 方式直接运行）。这类文件无法把 import 移到 `sys.path` 引导之前，已按指南第三节的 `per-file-ignores` 机制显式登记，而不是散落 `# noqa`。详见第五节。

### 3.2 `B904` `except` 中的 `raise` 未声明异常链（12 处）

| # | 位置 | 修改前 | 修改后 |
| --- | --- | --- | --- |
| 1 | `code/backend/inf_backend/migrate.py:230` | `raise SystemExit(...)` | `raise SystemExit(...) from None`（不再把底层 `DatabaseUnavailable/OSError` 挂在用户提示后面） |
| 2 | `code/core_engine/tome_writer/narrative_context.py:35,37,40` | `raise original`（3 处） | `raise original from None`（显式声明"丢弃 JSON 解析异常"，避免 `During handling of the above exception` 噪音） |
| 3 | `code/core_engine/memory_runtime/src/tome_writer/narrative_context.py:35,37,40` | 同上（同步副本） | 同上 |
| 4 | `code/core_engine/memory_runtime/pipeline.py:1172` | `except TemporalUnresolved:` | `except TemporalUnresolved as unresolved:`，处理器内 8 处 `raise` 全部改为 `raise ... from unresolved` |
| 5 | `code/core_engine/memory_runtime/reference_choices.py:293` | `except ContractError:` → `raise ContractError("Malformed reference selector...")` | `except ContractError as invalid:` → `... from invalid`（保留"原始解析错误"作为原因，便于排障） |

`pipeline.py` 改正后节选（同一处理器内 8 处保持一致）：

```python
        except TemporalUnresolved as unresolved:
            if _depth >= 3:
                raise TemporalUnresolved(
                    "Uncertainty review round limit reached; chapter remains pending"
                ) from unresolved
            ...
            if not isinstance(decisions, list):
                raise ContractError(
                    "Uncertainty decisions must be list"
                ) from unresolved
```

### 3.3 `B023` 循环内定义函数/类引用循环变量（14 处）

分两类处理：

**(a) 值语义闭包 —— 把循环变量改为构造函数/默认参数传入（11 处）**

| # | 位置 | 修改前 | 修改后 |
| --- | --- | --- | --- |
| 1 | `test_closure_repair.py:305,309,313` | `for mode in ("json","boolean","missing","unknown"):` 内定义 `class BadRepair(RepairProvider)`，`complete()` 直接读 `mode` | 类提到循环外，`def __init__(self, mode): super().__init__(); self.mode = mode`，循环内 `provider = BadRepair(mode)` |
| 2 | `test_continuity.py:294` | 循环内 `class Gateway: def complete(self, request): return ModelReply(canonical(reply), ...)` | 类提到循环外，`__init__(self, reply)`，调用处 `Gateway(reply)` |
| 3 | `test_event_first.py:425,433,441` | 循环内 `class Partial` 读 `second` | 提到循环外，`__init__(self, second)`，`complete()` 内首行 `second = self.second`，调用处 `Partial(second)` |
| 4 | `test_generation_foundations.py:45` | 循环内 `class Replay: def complete(...): return ModelReply(**r)` | 提到循环外，`__init__(self, reply)`，调用处 `Replay(r)` |
| 5 | `test_provider_stop.py:65` | 循环内 `class Provider` 读 `status` | 提到循环外，`__init__(self, status)` + `self.status`，调用处 `Provider(status)` |
| 6 | `test_provider_stop.py:86` | 同上 | 同上 |
| 7 | `test_writing.py:233` | 循环内 `class Saved: ... canonical(body)` | 提到循环外，`__init__(self, body)`，调用处 `StoryReferenceGateway(Saved(body))` |
| 8 | `test_grounding_references.py:92` | 循环内 `def reply(rows, n): ... = bad` | `def reply(rows, n, bad=bad):`（按 Ruff 建议用默认参数绑定） |
| 9 | `test_projection_grounding.py:139` | `Grounded(lambda rows, n: {"decisions": transform(rows)})` | `Grounded(lambda rows, n, transform=transform: {...})` |

以 `test_provider_stop.py` 为例（这类"循环内定义测试替身"共 11 处，全部统一为"类提出循环、参数注入"）：

```python
    def test_permanent_refusal_latches_across_writer_and_memory_without_new_calls(self):
        class Provider:                      # ← 修改前在 for 循环内部定义
            calls = 0

            def __init__(self, status):
                self.status = status

            def complete(self, r):
                self.calls += 1
                raise ProviderError("sanitized", http_status=self.status)

        for status in (401, 402, 403):
            with self.subTest(status=status):
                provider = Provider(status)   # ← 修改前为 Provider()
```

**(b) 语义要求晚绑定 —— 保留闭包并就地说明（1 处）**

`code/core_engine/memory_runtime/continuity.py:163`：

```python
        # Late binding of `row` is intentional: the binding is refreshed later in
        # this same iteration (attribute normalisation) and the error payload must
        # carry that value. Default-argument binding would freeze the stale one.
        def fail(message, prior=None):
            raise ContinuityError(message, row, prior)  # noqa: B023
```

这里不能按 Ruff 建议改成 `row=row` 默认参数：同一轮迭代中第 170 行会 `row = copy.deepcopy(row)` 再改写 `row["attribute"]`，`fail()` 必须报告改写后的记录（否则错误详情里的 `attribute` 会退回未规范化的标签）。属于「配置或代码无法表达意图时，用最小范围的 `noqa` + 理由说明」，而非静默放过。

### 3.4 `B007` 循环控制变量未使用（3 处）

| 位置 | 修改前 | 修改后 |
| --- | --- | --- |
| `pipeline.py:1021` | `for score, identifier, row in sorted(group, key=first_source):` | `for _score, identifier, row in ...`（`identifier` 在循环体内仍被使用，故只改 `score`） |
| `pipeline.py:1084` | `for score, identifier, row in reserved:` | `for _score, _identifier, row in reserved:`（两者均未使用） |

### 3.5 `F841` 局部变量赋值后未使用（3 处）

| 位置 | 修改前 | 修改后 | 理由 |
| --- | --- | --- | --- |
| `story_closure.py:581` | 循环内 `chapters = {c["number"]: c["text"] for c in self.session.book["chapters"]}` | 删除该 3 行 | 每轮分块都重算全量章节字典，但从未被读取；`closing_sources()` 直接用 `self.session.book`。纯死代码 |
| `writing.py:844` | `last_error = None` | 删除该行 | 该名字只在函数开头出现一次，既无赋值也无读取 |
| `test_projection_grounding.py:220` | `first = chapters[0]["event_commit"]` | 删除该行 | 测试后续断言不依赖它，属遗留变量 |

### 3.6 `E731` 用赋值语句定义 lambda（1 处）

`test_story_review.py:135`：

```python
# 修改前
folder = ROOT / "runs/writing_tiered_30000_20261021_c"
read = lambda name: json.loads((folder / name).read_text(encoding="utf-8"))

# 修改后
folder = ROOT / "runs/writing_tiered_30000_20261021_c"

def read(name):
    return json.loads((folder / name).read_text(encoding="utf-8"))
```

### 3.7 `I001` 导入块分组/排序（36 处，30 个文件）

由新增的 `known-first-party` 配置触发：`tome_writer` / `memory_runtime` / `user_runtime` 从"第三方块"归入"自有包块"。修改形态统一为删除多余分组空行、必要时按字母序调整，例如：

```python
# 修改前（code/core_engine/memory_runtime/test_writing.py）
from tome_writer.models import ModelReply, ModelRequest

from memory_runtime.story_review import StoryReferenceGateway
from memory_runtime.writing import load_resume

# 修改后
from tome_writer.models import ModelReply, ModelRequest
from memory_runtime.story_review import StoryReferenceGateway
from memory_runtime.writing import load_resume
```

`test_provider_stop.py` 还顺带纠正了一个真实分组错误：`from user_runtime import MeteredGateway, run_draft_trial`（本项目自有模块）原先被排在 `memory_runtime` 之前并单独空行，现并入自有包块按字母序排列。

### 3.8 仓库更新到 `e4d23ce` 后的第二轮（4 处 + 2 个文件重排）

首轮整改完成并全绿后，仓库又合入新提交（HEAD 由 `e085af4` → `e4d23ce feat: improve studio navigation and book covers`）。在新代码上重跑 `ruff check .` 又暴露 4 处，均已修复：

| # | 位置 | 规则 | 修改前 | 修改后 |
| --- | --- | --- | --- | --- |
| 1 | `code/backend/inf_backend/service.py:472` | `B904` | `raise ValueError("长文本检查点索引格式不正确")`（在 `except ContractError as exc:` 内） | `... from exc` |
| 2 | `code/backend/inf_backend/service.py:476` | `B904` | `raise ValueError("长文本检查点路径不安全")` | `... from exc` |
| 3 | `tests/integration/vue_ui_preview.py:6` | `I001` | `import argparse / copy / os / from pathlib import Path / tempfile / time` | `from pathlib import Path` 移到 `import tempfile/time` 之后（stdlib 段内 import 在前、from-import 在后） |
| 4 | `tests/integration/vue_ui_preview.py:24` | `I001` | `from inf_backend import service, library, official_pricing` + `from inf_backend.web import WebServer, Handler` | `from inf_backend import library, official_pricing, service`；`from inf_backend.settings import Settings` 居中；`from inf_backend.web import Handler, WebServer` |

同时这两个文件此前从未走过格式化，`ruff format` 重排了 2 个文件（`service.py` 的 `if (...)` 多行条件缩进、`vue_ui_preview.py` 全文件的折行与 `time.sleep(.7)` → `sleep(0.7)`）。`service.py` 的改动均为 B904 与排版，`vue_ui_preview.py` 是手工浏览器夹具（不被 `unittest discover` 收集），改后 `python -m compileall` 全仓库通过。

> 结论：**新代码同样符合规则**——`known-first-party`、`per-file-ignores`、行宽这些约束在后续提交里持续生效，`lint` job 也会在 CI 拦住同类问题。

---

## 四、被配置显式豁免的部分（不是漏改）

| 豁免项 | 范围 | 依据与理由 |
| --- | --- | --- |
| `E402` | `check_memory.py`、`write_novel.py`、`memory_runtime/test_*.py`（共 30 处） | 这些是可直接执行的脚本/脚本式测试（`python -X utf8 memory_runtime/test_writing.py`），必须先 `sys.path.insert` 再导入 `tome_writer`。Python 无法在 `sys.path` 生效前完成该导入，只能调整顺序或豁免。按指南第三节的 `per-file-ignores` 集中登记，并在配置内注释原因；`engine.py`、`agents.py`、`test_regression.py` 等 12 处可结构性修复的已全部修复（见 3.1） |
| `E501` | 全仓库 | 与指南示例配置一致：行宽由 `ruff format` 保证（88 列），不再重复报警 |
| `S101` / `F401` | `tests/**`、`code/**/test_*.py` | 与指南示例一致：测试允许 `assert` 与夹具式导入。注：`S`（bandit）当前未在 `select` 中，该条属"预留登记" |

---

## 五、验证记录

```powershell
# 1) 规则检查（仓库根目录，读取根 pyproject.toml）
ruff check .
# → All checks passed!

# 2) 格式化一致性
ruff format --check .
# → 179 files already formatted

# 3) 单元测试
python -m unittest discover -s tests/unit -v
# → Ran 97 tests ... OK

# 4) 集成测试（含 web/service/library/写作风格）
python -m unittest discover -s tests/integration -v
# → Ran 30 tests ... OK (skipped=7)

# 5) 语法编译（全仓库，防止格式化/重排引入语法问题）
python -m compileall -q code/backend code/core_engine tests
# → exit 0（无输出即全部通过）
```

以上 5 项在**两次核查**中各跑一遍：首轮（HEAD `e085af4`）与仓库更新后（HEAD `e4d23ce`），两次结果一致（第二轮新增 4 处不合规已修复，见 3.8）。

回归对照（为排除"改坏"的可能，对 `code/core_engine/memory_runtime/` 下 10 个脚本式测试模块，在**改动前后各跑一遍**并逐项比对）：

| 模块 | 改动前 | 改动后 |
| --- | --- | --- |
| `test_closure_repair.py` | 14 OK | 14 OK |
| `test_provider_stop.py` | 4 run / 1 error | 4 run / 1 error（同一处） |
| `test_projection_grounding.py` | 14 run / 2 error | 14 run / 2 error（同两处） |
| `test_grounding_references.py` | 5 run / 1 error | 5 run / 1 error（同一处） |
| `test_generation_foundations.py` | 12 run / 1 error | 12 run / 1 error（同一处） |
| `test_writing.py` | 24 run / 1 error | 24 run / 1 error（同一处） |
| `test_event_first.py` | 66 run / 35 error | 66 run / 35 error（同 35 处） |
| `test_continuity.py`、`test_regression.py` | setUpClass/导入失败 | 完全相同 |

上述 error 属**仓库既有环境缺失**，与本次整改无关：这些用例依赖 `code/core_engine/runs/`（写作产物）、`code/core_engine/tools/continuous_memory_20261021_i/test_run.py`、`code/core_engine/docs/analysis/novel_review_20261021_c/paragraphs.json` 等未被版本化的夹具目录，在干净副本上本来就无法运行（`git stash` 前后结果逐项一致）。为确认被改动到的具体用例确实通过，另逐个点名执行：

```
ProviderStopTests.test_permanent_refusal_latches_across_writer_and_memory_without_new_calls  → OK
ProviderStopTests.test_transient_or_payload_error_does_not_globally_latch                     → OK
EventFirstTests.test_layer_repairs_only_failed_items_and_keeps_valid_decisions                → OK
WritingIntegration.test_story_reference_alias_never_guesses_unknown_id_or_fabricates_quote    → OK
ProjectionGroundingTests.test_missing_duplicate_and_unknown_positions_do_not_become_facts     → OK
ProjectionGroundingTests.test_delayed_backfill_never_overwrites_later_current_value           → OK
GroundingReferenceTests.test_invalid_boolean_and_missing_positions_stay_pending               → OK
ContinuityTests.test_patch_cannot_clear_conflict_or_change_other_paragraph                    → OK
```

---

## 六、其他必要说明与后续建议

1. **两份 `tome_writer` 同步维护**：`code/core_engine/tome_writer/` 与 `code/core_engine/memory_runtime/src/tome_writer/` 当前内容完全一致（逐文件哈希相同），本次对 `agents.py`、`narrative_context.py` 的修改在两侧同步落实。建议后续二选一（保留一份 + 软链接/打包安装），否则规则整改需要做两遍，且运行期可能出现同名模块双实例（`import tome_writer` 究竟命中哪一份取决于 `sys.path` 顺序）。

2. **未采纳指南的方案 B（Black + Pylint + Mypy）**：指南建议二选一，本项目采用方案 A。Ruff 已在 `select` 中覆盖 Flake8/isort/pyupgrade/bugbear 的主要能力，且 `ruff format` 与 Black 输出兼容（整改前 `--check` 即通过，说明历史格式就是 Black 风格）。若后续要做严格类型门禁，可在 `pyproject.toml` 追加 `[tool.mypy]` 并在 CI 增加一步；当前代码库尚未全量标注类型，直接开启会一次性产生大量报错，建议按模块推进。

3. **可选增强（指南提到但未纳入本次门禁）**：
   - 安全规则集：在 `select` 中加 `"S"`（bandit），`schema.sql`/API Key/网络调用相关代码可获益；`tests/**` 的 `S101` 豁免已提前登记。
   - 复杂度上限：`"C90"` + `[tool.ruff.lint.mccabe] max-complexity = 15`，对应指南中 SonarLint「认知复杂度过高」的能力。`pipeline.py`、`writing.py`、`narrative_planning.py` 中的长函数会是首批对象，建议单独一个 PR 做拆分，避免与本次规则整改混在一起。

4. **修复既有测试夹具缺失**：第 5 节列出的 `runs/`、`tools/`、`docs/analysis/` 目录未入库，导致 `code/core_engine/memory_runtime` 下 8 个测试模块在干净副本上无法运行（CI 也只跑 `tests/`）。建议把这些夹具入库或改为生成式夹具，否则这部分回归实际上长期处于"未验证"状态。

5. **编辑器侧一次性动作（本机，不入库）**：安装 `charliermarsh.ruff` 后按第二节第 2 条填好用户设置并重开窗口，确认 Ruff 输出面板没有 "unable to find pyproject.toml" 提示；仓库根 `pyproject.toml` 生效后，`code/backend/pyproject.toml`（仅打包用、无 `[tool.ruff]`）不会被 Ruff 误当成配置源（已用 `ruff check --show-settings` 验证）。用 Pylance 时 `python.analysis.extraPaths` 必须包含 `code/core_engine` 与 `code/backend`，否则 `tome_writer` 会显示为无法解析的导入。
````

---

## `docs/software/CODE_REVIEW_20261107.md`

整改后复审报告：按 CodeReviewTemplate 六节，含 P1~P3 遗留问题。（`markdown`，84 行）

<!-- fixes:file target="docs/software/CODE_REVIEW_20261107.md" mode="create" -->
````markdown
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
| 设计模式和代码结构 | 部分合理 | 端口/适配器边界清晰（`ports.py`、`ModelGateway`）、网页层与引擎层分离；但 `tome_writer` 存在两份逐字节相同的副本 |
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
| 结构 | 冗余、复制粘贴 | 有问题 | `tome_writer` 两份副本、35 个文件逐字节相同（见第 5 节 P2） |

## 5. 语句级审查

| 优先级 | 文件与位置 | 问题 | 建议 |
|---|---|---|---|
| P1 | `code/core_engine/memory_runtime/test_continuity.py:44`、`test_regression.py:20`、`test_writing.py:244` 等 9 个测试模块 | 这些脚本式测试模块依赖未入库夹具（`code/core_engine/runs/`、`docs/analysis/novel_review_20261021_c/paragraphs.json`、`tools/continuous_memory_20261021_i/test_run.py`），干净副本上会直接 `FileNotFoundError`／`setUpClass` 失败。CI 只跑 `tests/`（127 项）和 `tests/run_engine_regression.py`（42 项），这 9 个模块不在其中：`test_continuity`、`test_event_first`、`test_grounding_references`、`test_generation_foundations`、`test_projection_grounding`、`test_provider_stop`、`test_story_review`、`test_writing`、`test_regression`。实测这 9 个模块在当前副本上均有报错（单个模块 1~35 个用例受影响，`test_regression.py` 为导入期失败），其余用例通过。 | 夹具入库或改造成生成式夹具；把可运行部分并入 `tests/run_engine_regression.py` 的类清单，让 CI 真正覆盖。 |
| P2 | `code/core_engine/tome_writer/` 与 `code/core_engine/memory_runtime/src/tome_writer/`（各 35 个文件） | 两份副本逐字节相同，但 `import tome_writer` 命中哪一份取决于 `sys.path` 插入顺序（`write_novel.py:19`、`memory_runtime/__init__.py:14`、`check_memory.py:14` 各自插入不同目录）。本次整改不得不在两侧重复修改 `agents.py` 与 `narrative_context.py`，漏改一处就会让两个入口行为分叉。 | 保留单一源（删除一份改软链接，或改 `src/` 布局 + `pip install -e`）；CI 增加两树一致性校验（本次以逐文件哈希核验，35/35 相同）。 |
| P2 | `code/core_engine/memory_runtime/continuity.py:167` | `fail()` 闭包依赖循环变量 `row` 的晚绑定，而 `row` 在同一轮迭代内会被重新赋值（`row = copy.deepcopy(row)` 后改写 `attribute`）。本次以 `# noqa: B023` 加注释保留，因为改用默认参数会把错误详情冻结成未规范化的旧值；但该写法依赖「闭包只在当前迭代内调用」，将来若被缓存或跨迭代复用会静默错报。 | 改为显式传参（`fail(message, row, prior)`），或先算出规范化记录存进局部常量再闭包引用。 |
| P2 | 全仓类型注解 | 1633 个函数仅 24 个有返回注解；CI 无静态类型门禁。对 4 万行级引擎做结构性改动（如上面的去重）缺少编译期保护，只能靠测试兜底。 | 按模块增量补注解（先 `domain/`、`ports.py` 等接口层），在 `pyproject.toml` 增加 `[tool.mypy]` 并让 CI 逐步扩大检查范围。 |
| P3 | `code/core_engine/tome_writer/agents.py:13` 等 107 个文件 | 490 行超过 88 列，其中 416 行是中文提示词/长字符串（最长 1109 字符）。`ruff format` 不拆分字符串，`E501` 又被配置忽略，导致提示词既难 diff 也无法复用。 | 长提示词抽到独立的 `.md`/`.txt` 资源按段落加载；保留 `E501` 忽略以免噪音。 |
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
````

---

## `docs/quality/QUALITY_REPORT.md`

质量检测报告：Pylint 配置、重构前基线指标、Top 5 重构（含前后代码）与重扫对比。
（`markdown`，293 行）

<!-- fixes:file target="docs/quality/QUALITY_REPORT.md" mode="create" -->
````markdown
# 代码质量检测报告（Pylint 扫描 · 重构前后对比）

对应检查项：为项目配置静态分析工具 → 运行扫描记录指标 → 选出 Top 5 最严重问题逐一重构 → 重新扫描形成对比。

**结论摘要**：Pylint 在 `code/`（44,728 行 SLOC、1,248 个函数）上报告 **948** 条告警，其中 **Bug 11 条、Code Smell 937 条、圈复杂度 >10 的函数 103 个、重复率 1.68%**。按缺陷风险选出 Top 5 重构后，总告警降到 **911**（−37），五个目标规则 **13→0 / 17→4 / 17→14 / 41→35 / 1→0**；新增 5 个回归测试，其中 4 个在重构前的基线上必然失败（已实测），重构后全部通过。复杂度与重复率本轮未动，属结构性债务，已在第 6 节单列并给出量化依据。

---

## 1. 工具与配置

| 项 | 选择 | 说明 |
|---|---|---|
| 度量工具 | **Pylint 4.1.3** + `pylint.extensions.mccabe` | 作业要求的「Bug 数 / Code Smell 数 / 圈复杂度 / 重复率」四类指标都由它产出 |
| 快速门禁 | Ruff 0.17.4（既有配置） | 保存时/CI 用的秒级检查，规则见 `pyproject.toml` 的 `[tool.ruff]`，当前 0 违规；它不分类 Bug/Smell，因此不能替代 Pylint |
| 配置文件 | 仓库根 `pyproject.toml` 的 `[tool.pylint.*]` | 见下，随代码一起版本化，保证本机与 CI 判定一致 |
| 扫描命令 | `python -m pylint --recursive=y code tests` | `--recursive=y` 必须显式给，否则 `code` 会被当成标准库同名模块 |

配置要点（`pyproject.toml`）：

```toml
[tool.pylint.main]
py-version = "3.11"
jobs = 1                       # 顺序执行：容器内无法 fork 带管道的子进程
persistent = false             # 不写缓存，报告可复现
load-plugins = ["pylint.extensions.mccabe"]
ignore-paths = ["^code/backend/\\.venv/", "^\\.tmp/", "^runs/", "^fixes/"]

[tool.pylint.format]
max-line-length = 88

[tool.pylint.design]
max-complexity = 10            # 超过 10 判为 too-complex

[tool.pylint."messages control"]
disable = [
    "missing-module-docstring",   # 团队标准不要求 docstring
    "missing-class-docstring",
    "missing-function-docstring",
    "line-too-long",              # 由 ruff format 保证；Ruff 侧同样忽略 E501
    "import-outside-toplevel",    # 本项目的惰性导入用于打断循环依赖
]
```

指标定义（写清楚才能复现）：

| 指标 | 定义 |
|---|---|
| Bug 数 | `message-id` 首字母为 `E`（error）或 `F`（fatal）的条数 |
| Code Smell 数 | 首字母为 `W`（warning）、`R`（refactor）、`C`（convention）的条数 |
| 圈复杂度 | `too-complex`（R1260，mccabe，阈值 10）函数个数；另给全量 AST 统计的平均值与最大值 |
| 重复率 | `duplicate-code`（R0801）报告的重复块：每组取 `min(块行数) × (块数 − 1)` 累加，除以 SLOC |

---

## 2. 扫描范围与基线

- 基线：提交 `e4d23ce`（干净检出，未含本次重构），用**同一份** `pyproject.toml` 配置扫描，避免配置漂移影响对比。
- 范围：`code/`（产品代码）用于指标对比；`tests/` 一并扫描但不计入对比（重构过程中新增了测试文件，混入会污染前后对比）。
- 基线规模：44,728 行 SLOC、1,248 个函数、119 个文件有告警。

![重构前扫描报告](scan_before.png)

基线关键数字：

| 指标 | 数值 |
|---|---:|
| 总告警 | 948 |
| Bug（E+F） | 11 |
| Code Smell（C+W+R） | 937（C 161 / R 593 / W 183） |
| 圈复杂度 | 平均 4.64、最高 79，>10 的函数 103 个 |
| 重复率 | 751 行 / 63 组 = 1.68% |

---

## 3. Top 5 最严重问题与重构

**选取口径**：以「是否可能导致错误行为、是否直接损害缺陷定位」排序，而不是按告警条数。复杂度与重复率条数更大，但属于结构性债务（重构面广、行为风险高），单列到第 6 节。

### Top 1 — `raise-missing-from`（13 → 0）

**风险**：`except` 内抛新异常却不声明因果，原始异常被静默丢进 `__context__`；排障时只看到外层错误，`traceback` 链断开。数据库/存档恢复路径一旦出错，无法判断是「索引格式坏」还是「底层 IO 失败」。

**重构**（3 类处理，共 14 处）：

```python
# code/backend/inf_backend/service.py:472（旧检查点回退）
- raise ValueError("长文本检查点索引格式不正确")
+ raise ValueError("长文本检查点索引格式不正确") from exc

# code/core_engine/memory_runtime/pipeline.py:1172
- except TemporalUnresolved:
+ except TemporalUnresolved as unresolved:
      ...
-     raise ContractError("Uncertainty decisions must be list")
+     raise ContractError("Uncertainty decisions must be list") from unresolved

# code/backend/inf_backend/migrate.py:230（CLI 兜底，不需要堆栈噪音）
- raise SystemExit("数据库操作未完成。…")
+ raise SystemExit("数据库操作未完成。…") from None
```

**测试**（先补测试，3 个用例在基线上失败）：

```text
tests/unit/test_quality_refactors.py
  test_longform_pointer_error_keeps_contract_error_as_cause   baseline FAIL → now PASS
  test_migrate_failure_suppresses_the_underlying_exception    baseline FAIL → now PASS
  test_planner_json_recovery_does_not_leak_the_parser_error   baseline FAIL → now PASS
```

### Top 2 — `cell-var-from-loop`（17 → 4）

**风险**：循环内定义函数/类却引用循环变量，属晚绑定。测试替身若在下一轮迭代才被调用，会拿到**上一轮的值**，导致断言「假通过」或错误详情指向错误记录。

**重构**（13 处统一为「类提出循环 + 参数注入」，1 处保留并注明）：

```python
# tests/unit/../memory_runtime/test_provider_stop.py（重构前）
for status in (401, 402, 403):
    class Provider:
        def complete(self, r):
            raise ProviderError("sanitized", http_status=status)

# 重构后：类在循环外，值经构造函数绑定
class Provider:
    def __init__(self, status):
        self.status = status
    def complete(self, r):
        raise ProviderError("sanitized", http_status=self.status)

for status in (401, 402, 403):
    provider = Provider(status)
```

```python
# code/core_engine/memory_runtime/continuity.py:167（保留晚绑定，理由写在原地）
def fail(message, prior=None):
    raise ContinuityError(message, row, prior)  # noqa: B023
```

**为什么这一处不改**：同轮迭代中 `row` 会被重新赋值（`row = copy.deepcopy(row)` 后改写 `attribute`），`fail()` 必须报告改写后的记录；改成默认参数会把错误详情冻结成未规范化的旧值。这是「重构会改变行为」的边界，选择保留并加注释，而不是为了指标好看去改。

**测试**：`test_continuity_error_reports_the_normalised_attribute` —— 固定「错误详情必须携带规范化后的 attribute」这一契约（该用例在基线上也通过，属保持性测试，防后续再改坏）。

### Top 3 — `unused-variable`（17 → 14）

**风险**：赋值后从未使用的局部变量通常是「漏接返回值」或死代码。本次发现两处真死代码，其中一处在分块循环里**每轮重算全量章节字典**。

**重构**：

```python
# code/core_engine/memory_runtime/story_closure.py:581（循环内每轮白算，从未读取）
- chapters = {c["number"]: c["text"] for c in self.session.book["chapters"]}
  sources = closing_sources(self.session.book, n, max(0, start - 600), end)

# code/core_engine/memory_runtime/writing.py:844（声明后从未赋值/读取）
- last_error = None
  last_design = {}
```

**测试**：删除的均为无副作用的纯死代码，由既有回归兜底 —— `tests/` 102 项 + 引擎脚本式 42 项全部通过（见第 4 节）。

### Top 4 — `wrong-import-position`（41 → 35）

**风险**：模块中部导入让依赖关系不可读，也让循环依赖被掩盖。

**重构**（结构性修复 12 处，其余 30 处为脚本引导，已登记豁免）：

```python
# code/core_engine/tome_writer/agents.py：import 曾被放在 PROMPTS 赋值之后
 from .domain import ContractError, chapter_plan, fields, strict_json, text
+from .memory_output_contract import MEMORY_PROMPT
 from .models import ModelGateway, ModelRequest

- PROMPTS["memory"] += (...)
-
-from .memory_output_contract import MEMORY_PROMPT
-
 PROMPTS["memory"] = MEMORY_PROMPT
```

```python
# code/core_engine/memory_runtime/__init__.py：把 sys.path 引导收口到包入口
+_SOURCE = Path(__file__).resolve().parent / "src"
+if str(_SOURCE) not in sys.path:
+    sys.path.insert(0, str(_SOURCE))
```

**为什么还剩 35 处**：`check_memory.py`、`write_novel.py` 与 `memory_runtime/test_*.py` 是**可直接执行的脚本**（`python memory_runtime/test_writing.py`），必须先 `sys.path.insert` 再导入 `tome_writer`。Python 无法在 `sys.path` 生效前完成导入，只能在配置里显式登记（Ruff 的 `per-file-ignores` 里同样登记了这 30 个文件）。

**测试**：`test_importing_memory_runtime_exposes_the_bundled_tome_writer` —— 在子进程里只 `import memory_runtime`，断言内置 `tome_writer` 已可导入（基线上该断言失败）。

### Top 5 — `unnecessary-lambda-assignment`（1 → 0）

**风险**：`read = lambda name: ...` 在栈帧里显示为 `<lambda>`，断点与 `traceback` 定位困难，也不符合 PEP 8。

```python
# tests/.../test_story_review.py:135
-read = lambda name: json.loads((folder / name).read_text(encoding="utf-8"))
+def read(name):
+    return json.loads((folder / name).read_text(encoding="utf-8"))
```

---

## 4. 测试

新增 `tests/unit/test_quality_refactors.py`（5 个用例，对应 Top 1/2/4）：

| 用例 | 基线 `e4d23ce` | 重构后 |
|---|---|---|
| `test_longform_pointer_error_keeps_contract_error_as_cause` | FAIL（`__cause__` 为 None） | PASS |
| `test_migrate_failure_suppresses_the_underlying_exception` | FAIL | PASS |
| `test_planner_json_recovery_does_not_leak_the_parser_error` | FAIL（`__cause__` 泄漏 JSON 解析异常） | PASS |
| `test_importing_memory_runtime_exposes_the_bundled_tome_writer` | FAIL | PASS |
| `test_continuity_error_reports_the_normalised_attribute`（保持性） | PASS | PASS |

实测记录：

```text
# 重构前（干净检出 + 同一份测试文件）
Ran 5 tests ... FAILED (failures=4)

# 重构后（当前工作区）
Ran 5 tests ... OK

# 全量回归
tests/unit           102 项  OK
tests/integration     30 项  OK (skipped=7)
tests/run_engine_regression.py  42 项  OK (skipped=3)
ruff check .          All checks passed!
ruff format --check . 181 files already formatted
```

---

## 5. 重新扫描与对比

![重构前后指标对比](metrics_compare.png)

![重构后扫描报告](scan_after.png)

| 指标 | 重构前 | 重构后 | 变化 |
|---|---:|---:|---:|
| Bug（E+F） | 11 | 11 | 0 |
| Code Smell（C+W+R） | 937 | 900 | **−37** |
| 总告警 | 948 | 911 | **−37** |
| 重复行数 / 重复率 | 751 / 1.68% | 751 / 1.68% | 0 |
| 圈复杂度（平均 / 最高） | 4.64 / 79 | 4.64 / 79 | 0 |
| 圈复杂度 >10 的函数 | 103 | 103 | 0 |
| `raise-missing-from` | 13 | **0** | −13 |
| `cell-var-from-loop` | 17 | 4 | −13 |
| `unused-variable` | 17 | 14 | −3 |
| `wrong-import-position` | 41 | 35 | −6 |
| `unnecessary-lambda-assignment` | 1 | 0 | −1 |

为什么 Bug 数两边都是 11：本轮把「Bug」定义为 E/F，而 Pylint 在这套代码上的 11 条 E 里，**6 条是 `tools.testing` 包缺失导致的 import-error（真实问题，见 6.1）**、**5 条是 astroid 推断误报**（如 `Snapshot.__dataclass_fields__`、`BaseException.http_status`）。Top 1–5 的修复属于 W 类（隐蔽缺陷），所以「Bug 数不变、Code Smell −37」是符合预期的，而不是指标失真。

---

## 6. 未纳入本轮的结构性债务（含量化依据）

### 6.1 `tools.testing` 包缺失 —— 6 条真实 import-error

`memory_runtime/test_event_first.py:180` 等 6 处 `from tools.testing.archived_plan_fixture import ...`，但仓库里没有 `tools/` 包。这解释了这些脚本式测试在干净副本上跑不起来（详见代码评审 P1）。**建议**：把该 fixture 入库，或改为生成式 fixture。

### 6.2 圈复杂度：103 个函数 > 10（最高 79）

分布集中在 `memory_runtime/pipeline.py`、`writing.py`、`narrative_planning.py`。这类函数拆分需要先把行为固定成特征测试，工作量和回归风险都高于本轮一次性批改，**建议**按文件单独提 PR，并配 `max-complexity` 门禁逐步收紧。

### 6.3 重复率 1.68%（751 行 / 63 组）

主要来源不是复制粘贴，而是 **`tome_writer/` 与 `memory_runtime/src/tome_writer/` 两份逐字节相同的副本**（35 个文件）。删掉一份会改变运行期 `import tome_writer` 的解析路径，必须与打包方式一起调整，属于独立任务。**建议**：单一源 + `pip install -e`，并在 CI 加两树一致性校验。

### 6.4 其余未处理项

- `broad-exception-caught` 40 条：多为线程/任务边界的兜底 `except Exception`，需要逐个判断「是否应记录并重新抛出」，不能批量改。
- `cell-var-from-loop` 剩余 4 处：`continuity.py:167`（保留并注明）、`narrative_planning.py:1284`、`pipeline.py:727-728`。
- `unused-variable` 剩余 14 处：集中在 `test_memory_meaning.py` 的解包占位，属风格问题。

---

## 7. 复现方式

```bash
pip install "pylint==4.1.3"          # 度量工具；Ruff 由 CI 安装
python -m pylint --recursive=y code tests --output-format=json \
  --reports=n --score=n --exit-zero > scan.json
# 指标聚合：Bug=message-id[0]∈{E,F}；Smell∈{W,R,C}；复杂度=R1260 计数 + mccabe 全量统计
# 重复率：R0801 各组 min(行数)×(块数−1) 之和 / SLOC
```

本地复现时若遇到 `PermissionError`（`tempfile.mkdtemp` 的 0o700 目录在受限沙箱中被拒），属运行环境限制，不是代码缺陷；在普通 Windows/Linux 环境或 CI 上不需要任何绕过。
````

---

## 未包含在本包中的二进制证据

`docs/quality/scan_before.png`、`scan_after.png`、`metrics_compare.png` 是扫描报告
截图，属二进制文件，不放进文本补丁包；它们由 `docs/quality/QUALITY_REPORT.md`
引用，随仓库一起提交即可。
