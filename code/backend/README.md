# Backend

后端代码位于 `inf_backend/`，负责 `.env` 配置、作品元数据、DeepSeek 连接和作品数据目录。

`service.generate` 默认调用稳定版的事件先行长文本流程；`generate_legacy` 只用于保留旧离线演示的回归验证。运行产物写入 `data/inf_books/<作品ID>/longform-runs/`，当前检查点由 `longform-current.json` 指向。

