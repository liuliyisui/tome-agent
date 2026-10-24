# Core Engine

这里保存 F 盘 `stable-ar-20261023` 的稳定长文本运行代码。

- `inf_writer/`：模型适配、基础角色、契约、事务和版本化事实。
- `memory_runtime/`：事件先行、三层记忆、连续性、篇幅和输入预算控制。
- `write_novel.py`、`user_runtime.py`、`check_memory.py`：稳定版运行入口及检查工具。
- `stable_release_manifest.json`：稳定版文件哈希和真实测试摘要。

后端默认从这里导入 `WritingSession`。代码打包位置改变之外，发布清单覆盖的稳定版文件保持原样。

