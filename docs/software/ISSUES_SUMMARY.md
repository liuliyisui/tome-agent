# 全生命周期主要问题与解决方法

本表汇总 Tome Agent 在分析、设计、开发、测试、部署运维阶段遇到的主要问题。每个问题都对应仓库中的实现、测试或文档记录。

| 问题类别 | 问题名称 | 发生原因 | 解决办法 |
| --- | --- | --- | --- |
| 分析 | 需求边界反复 | 长篇创作需求含糊，演示原型与真实生成容易混在一起 | 区分 `docs/software/prototype` 与正式服务；原型只作交互演示，不作为生成能力证据 |
| 设计 | 编排框架迁移 | LangGraph 迁移可能破坏已验证的事件推演、记忆和模型适配 | 节点内复用既有领域函数，只替换编排层；迁移后用回归测试验证 |
| 开发 | 模型调用失败 | 网络超时、响应截断、返回非法 JSON | 记录错误与用量；失败降级保留正文；区分请求失败、可能已计费、内容未审核 |
| 开发 | 长篇生成中断 | 一次成稿需要多次模型调用，耗时长 | 每个阶段保存原子检查点；恢复时识别待处理任务和损坏检查点 |
| 测试 | 文件与数据库双写 | 数据库记录与文件检查点不在同一事务 | 故障演练确认恢复行为；明确未覆盖边界，不承诺强一致 |
| 部署运维 | 旧版本无法续写 | 旧检查点的运行时哈希与新版本源码不一致 | 禁止手改哈希绕过；升级前保留旧代码与作品，新版本重新建立检查点 |
| 运维 | 成本不可预测 | token 计费随上下文和输出长度变化 | 生成前费用预估，生成后记录用量并由用户确认；不承诺固定价格 |

## 证据与维护

- 架构与能力边界：`docs/software/architecture.md`、`docs/software/LANGGRAPH_MIGRATION.md`
- 原型与正式服务边界：`docs/software/prototype/README.md`
- 失败处理、检查点与恢复：`code/backend/inf_backend/web.py`、`code/core_engine/memory_runtime/`
- 数据库与任务记录：`code/backend/inf_backend/schema.sql`
- 测试与故障演练：`tests/TEST_REPORT.md`、`tests/integration/`
- 部署与升级：`docs/software/DEPLOY.md`、`docs/software/WINDOWS_PORTABLE.md`、`docs/software/LINUX_HOSTED.md`
- 成本预估与用量：`code/backend/inf_backend/official_pricing.py`、`tome_usage` 表

维护方式：新问题先进入 GitHub Issue；解决后补充到本表，至少写清问题现象、发生原因、处理办法和对应证据。
