# 使用说明

## 环境准备

安装 Python 3.11 或更高版本。在仓库根目录运行：

```powershell
code\backend\setup.cmd
```

脚本会在 `code/backend/.venv` 创建独立环境，安装包括 LangGraph 与 Psycopg 的依赖，并在缺少配置时复制 `.env.example`。数据库初始化及旧作品导入见 [PostgreSQL 说明](POSTGRESQL.md)。

## 启动网页

运行 `code\backend\run-web.cmd`，打开 http://127.0.0.1:8765。创建作品并配置文风，生成前会显示 token 和费用预估，确认后才调用模型。

## 模型服务配置

在网页「设置 → 配置模型服务」中可选择 DeepSeek、OpenAI 或其他 OpenAI Chat Completions 兼容服务。填写模型名称和对应 API Key；选择「自定义」时，填写服务商提供的 HTTPS Base URL（如 https://api.example.com/v1），系统会补上 /chat/completions。也可以直接填写完整接口地址。保存只检查格式，不会测试密钥或模型是否可用。兼容服务须支持 JSON 对象输出和用量返回。

新作品使用当前配置；已有作品继续使用其绑定的服务与模型。同一接口的密钥更新后，其作品使用更新的密钥。非 DeepSeek 模型的价格无法自动核验，生成前请向服务商确认，费用以实际账单为准。

原有 DeepSeek `.env` 配置仍可使用：

打开 `code/backend/.env`，填写：

```text
DEEPSEEK_API_KEY=你的密钥
```

其他可选配置见 `.env.example`。默认模型为 `deepseek-chat`。`.env` 已被 Git 忽略，不能上传或发到群聊。

网页已接入事件先行和三层记忆引擎。真实生成需配置密钥；先生成首章并人工确认后，可批量续写。

## 自动测试

```powershell
$env:PYTHONPATH="$PWD\code\core_engine;$PWD\code\backend"
code\backend\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

测试数据写入 `code/backend/data/`，不会进入 Git。

## 存档规则

- 每本作品存放在 `code/backend/data/inf_books/<作品ID>/`。
- 作品与章节记录由 PostgreSQL 管理，引擎完整阶段状态仍保存在本地检查点 JSON 中。
- 每章成功后快照版本加一；同一请求 ID 可安全重复调用。
- 同一作品同时只能有一个写入操作。
- 基础严格事务入口审核拒绝时不提交候选章节；实际长篇入口会保留未审核草稿并记录待处理任务，两种策略不可混淆。
- 升级后的运行时指纹不同，旧版检查点不能直接续写；恢复范围见 [LangGraph 迁移说明](LANGGRAPH_MIGRATION.md)。

