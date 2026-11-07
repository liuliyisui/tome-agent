# Core Engine

这里保存基于 F 盘 `transfer_and_closure_20261028` 的长文本运行代码，并合入章节标题清理修改。

- `inf_writer/`：模型适配、基础角色、契约、事务和版本化事实。
- `memory_runtime/`：事件先行、三层记忆、连续性、篇幅和输入预算控制。
- `write_novel.py`、`user_runtime.py`、`check_memory.py`：稳定版运行入口及检查工具。
- `stable_release_manifest.json`：稳定版文件哈希和真实测试摘要。

后端默认从这里导入 `WritingSession`。发布清单记录上游文件哈希；本仓库的标题修正使部分文件与清单不同。

