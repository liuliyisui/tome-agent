# 使用说明

## 环境准备

安装 Python 3.11 或更高版本。在仓库根目录运行：

```powershell
code\backend\setup.cmd
```

INF 当前只使用 Python 标准库，因此无需下载第三方包。脚本会在 `code/backend/.venv` 创建独立环境，并在缺少配置时复制 `.env.example`。

## 离线演示

```powershell
code\backend\run-demo.cmd
```

演示使用固定响应依次运行 planner、writer、memory、reviewer，生成两章并验证事实版本变化。它不会联网，也不会消耗 DeepSeek 额度。结果位于 `code/backend/data/runs/`。

## DeepSeek 配置

打开 `code/backend/.env`，填写：

```text
DEEPSEEK_API_KEY=你的密钥
```

其他可选配置见 `.env.example`。默认模型为 `deepseek-chat`，接口限定为 DeepSeek 官方 `chat/completions` 地址。`.env` 已被 Git 忽略，不能上传或发到群聊。

当前版本已提供后端服务函数，但尚未重新接入图形前端。真实生成入口留到后续前端开发时再接入；目前只运行离线演示和测试，不会误用模型额度。

## 自动测试

```powershell
$env:PYTHONPATH="$PWD\code\core_engine;$PWD\code\backend"
code\backend\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

测试数据写入 `code/backend/data/`，不会进入 Git。

## 存档规则

- 每本作品存放在 `code/backend/data/inf_books/<作品ID>/`。
- 正式章节、计划和事实记忆保存在检查点 JSON 中。
- 每章成功后快照版本加一；同一请求 ID 可安全重复调用。
- 同一作品同时只能有一个写入操作。
- 审核拒绝、输出格式错误、预算耗尽或存档冲突都不会部分提交正式章节。

