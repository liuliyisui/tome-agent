# Backend

Windows 免安装版：运行 `build-windows.cmd` 构建包含 Python 运行时的 EXE 与 ZIP，使用说明见 `docs/software/WINDOWS_PORTABLE.md`。普通用户完整解压后双击 `TomeAgent.exe` 即可运行。

后端代码位于 `inf_backend/`，负责 `.env` 配置、作品元数据、DeepSeek 连接和作品数据目录。

首次打开页面时，若尚未设置 API Key，会弹出 DeepSeek 密钥配置窗口。页面保存到本机 `.env` 后立即生效，无需重启；已有环境变量或文件配置时不重复提示。初始化接口仅接受本机同源 JSON 请求，不回传密钥，也不能覆盖已配置的密钥。保存时只验证格式，实际认证在生成时进行。

运行 `run-web.cmd` 启动本地工作室。`service.generate` 通过 LangGraph 调用事件先行长文本流程，需配置 DeepSeek API 密钥。运行产物写入 `data/inf_books/<作品ID>/longform-runs/`，当前检查点由 `longform-current.json` 指向。

