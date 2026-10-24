# 使用说明

## 环境准备

安装 Python 3.11 或更高版本。在仓库根目录运行：

```powershell
code\backend\setup.cmd
```

INF 当前只使用 Python 标准库，因此无需下载第三方包。脚本会在 `code/backend/.venv` 创建独立环境，并在缺少配置时复制 `.env.example`。

## 启动网页

运行 `code\backend\run-web.cmd`，打开 http://127.0.0.1:8765。创建作品并配置文风，生成前会显示 token 和费用预估，确认后才调用模型。

## DeepSeek 配置

打开 `code/backend/.env`，填写：

```text
DEEPSEEK_API_KEY=你的密钥
```

其他可选配置见 `.env.example`。默认模型为 `deepseek-chat`，接口限定为 DeepSeek 官方 `chat/completions` 地址。`.env` 已被 Git 忽略，不能上传或发到群聊。

网页已接入事件先行和三层记忆引擎。真实生成需配置密钥；先生成首章并人工确认后，可批量续写。

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

