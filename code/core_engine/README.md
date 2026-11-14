# Core Engine

这里保存基于 F 盘 `transfer_and_closure_20261028` 引擎和 LangGraph 编排合并的长文本运行代码。

- `tome_writer/`：模型适配、基础角色、契约、事务和版本化事实。
- `memory_runtime/`：事件先行、三层记忆、连续性、篇幅和输入预算控制。
- `memory_runtime/writing_flow/graph_runtime.py`：实际写作入口的 LangGraph 状态图、重规划条件边和待处理任务恢复入口。
- `write_novel.py`、`user_runtime.py`、`check_memory.py`：稳定版运行入口及检查工具。
- `stable_release_manifest.json`：稳定版文件哈希和真实测试摘要。

后端默认从这里导入 `WritingSession`。发布清单记录上游文件哈希；本仓库的标题修正使部分文件与清单不同。

后端与命令行均调用 `WritingSession.write_next()`，实际执行 `session.graph.invoke()`。基础 `Coordinator` 的两个可导入副本也采用 LangGraph，审核拒绝走独立分支，不提交正式状态。

单独使用命令行前安装 `python -m pip install -r requirements.txt`；网页后端的依赖文件也包含相同的 LangGraph 版本。当前固定 `langgraph==1.2.17`。

发布清单记录各上游版本，不能用于证明当前合并版本逐字节一致。恢复采用应用自己的完整性检查点，未接入 LangGraph checkpointer；旧运行时存档不能直接续写。详见 `../../docs/software/LANGGRAPH_MIGRATION.md`。

