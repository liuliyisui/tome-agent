# memory_runtime 文件合并检查

本次检查范围为 `code/core_engine/memory_runtime`：35 个非测试 Python 模块、30 个回归测试，以及 `src/tome_writer` 中的 35 个 Python 文件。表中的合并候选仍需验证导入、旧检查点和回归测试；不代表已经合并。

| 模块 | 主要职责 | 初步判断 |
|---|---|---|
| `__init__` | 运行时导入路径 | 保留兼容入口 |
| `chapter_titles` | 标题生成与清理 | 独立职责，保留 |
| `closure_repair` | 结局问题修复 | 与 `story_closure` 紧密相关，可评估合并 |
| `completion` | 正文续写与输出处理 | 与长篇生成关联紧密，需单独验证 |
| `continuity` | 状态连续性 | 规模较大，不宜与其他大模块直接合并 |
| `engine` | 记忆阶段编排 | 独立入口，保留 |
| `event_contract` | 事件结构契约 | 与事件引用关联，合并前检查循环依赖 |
| `event_first` | 事件先行逻辑 | 规模较大，不宜直接并入其他模块 |
| `event_references` | 事件引用与目录 | 独立职责，保留 |
| `evidence_access` | 证据读取 | 体量适中，评估与相关证据模块归类 |
| `graph_runtime` | 状态图执行 | 独立职责，保留 |
| `identifiers` | 标识符生成 | 多个模块共享，保留独立入口 |
| `input_budget` | 输入大小限制 | 跨模块共享，保留独立入口 |
| `interface_contract` | 公开接口契约 | 被多个模块引用，保留 |
| `length_control` | 篇幅调整 | 与 `story_budget` 相关，可评估合并 |
| `meaning_organizer` | 记忆含义整理 | 规模较大，保留独立职责 |
| `narrative_planning` | 叙事规划 | 规模较大，不宜直接合并 |
| `narrative_repair` | 叙事规划修复 | 与 `narrative_planning` 紧密相关，可评估合并 |
| `numeric_grounding` | 数量来源与渲染 | 与正文渲染相关，但职责独立 |
| `pipeline` | 记忆流水线 | 规模较大，不宜直接合并 |
| `plan_repair` | 规划修复 | 被流程引用，需检查循环依赖 |
| `projection_grounding` | 投影证据校验 | 规模较大，保留独立职责 |
| `prose_memory` | 正文记忆覆盖 | 与正文相关，需验证旧数据契约 |
| `prose_rendering` | 正文引用渲染 | 独立职责，保留 |
| `recall_search` | 记忆检索 | 被流水线调用，保留独立职责 |
| `reference_choices` | 引用候选 | 规模较大，保留独立职责 |
| `semantics` | 语义检查 | 与流水线相关，需验证调用边界 |
| `stage_planning` | 阶段规划 | 与叙事规划相关，需检查循环依赖 |
| `state_recovery` | 状态恢复 | 被多个模块引用，保留独立职责 |
| `story_budget` | 章节及写作单元预算 | 与 `length_control` 相关，可评估合并 |
| `story_closure` | 故事结局 | 规模较大，直接合并前需验证 |
| `story_review` | 故事审核 | 独立职责，保留 |
| `time_calculation` | 时间计算 | 被多个模块引用，保留独立职责 |
| `writing` | 写作会话与生成编排 | 规模最大，不宜通过合并继续扩大 |
| `writing_units` | 写作单元 | 与阶段写作相关，需验证事件数据契约 |

30 个测试已归入 `regression_tests/`，其中 6 个已调整项目路径；旧导入路径和已审阅版本的检查点指纹有兼容处理。检查发现两套模型接口会因导入顺序产生不同行为，现已统一接口并为旧检查点增加受限的指纹兼容；重复实现已合并至 `code/core_engine/tome_writer`，原运行时位置保留兼容导入入口；旧检查点通过已审阅的整版本指纹进行兼容。

按 Python 语法树比较，顶层模块中未发现函数体完全相同的顶层函数或类方法（短小方法未纳入比较）。这不排除语义相近但实现不同的代码，也不证明任何候选已经完成安全审查。

运行模块参与检查点指纹。实施合并前应逐项保存旧版生成的检查点、保留旧导入入口，明确旧版本指纹与新版本的受限映射，并验证旧作品续写、篡改拒绝和完整回归。缺少的历史测试样本需要在结果中明确列出。

后续整理已将 34 个业务模块按写作流程、记忆处理、事件、规划与审核、辅助功能归类；`__init__.py` 保留在原位置，供兼容导入使用。
