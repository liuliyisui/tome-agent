# 使用说明

## Windows启动

1. 安装Python 3.11或更高版本，并在安装时勾选加入PATH。
2. 双击setup.cmd，下载依赖到项目.venv。此步骤需要网络，不调用模型。
3. 用文本编辑器打开项目根目录.env，填写DEEPSEEK_API_KEY；空模型名自动使用deepseek-flash。
4. 双击start.cmd，打开终端提示的本地地址，通常为http://127.0.0.1:8501。
5. 新建作品，填写故事要求和篇幅，确认费用后生成大纲。
6. 左侧选择作品，开始写作前可在大纲页修改JSON并保存。
7. 在续写页确认费用，先生成1章检查效果，再增加章节数。
8. 在故事记忆页查看当前状态与历史，在导出页下载Markdown和作品JSON。

默认只监听本机，不用于公开部署。关闭窗口不会保证取消已发送请求；暂停采用每次生成1章的方式。不要把API密钥发到群聊或上传GitHub。

## 配置

系统环境变量优先于.env。配置文件以UTF-8保存。

| 配置项 | 默认 | 含义 |
|---|---|---|
| DEEPSEEK_API_KEY | 空 | 必填，本地保存 |
| DEEPSEEK_MODEL | deepseek-flash | 模型名称 |
| DEEPSEEK_BASE_URL | https://api.deepseek.com | 官方接口 |
| DEEPSEEK_THINKING | false | true启用思考模式 |
| DEEPSEEK_MAX_TOKENS | 8192 | 单请求输出上限 |
| DEEPSEEK_TIMEOUT | 180 | 网络超时秒数 |
| TOME_MAX_REQUESTS | 100 | 每次操作请求上限 |
| TOME_MAX_TOTAL_TOKENS | 300000 | 每次操作token软上限 |

预算针对一次大纲/续写操作，不是账户或整本书累计费用。token总量在响应后获得，单次响应可能超预算；不能作为严格扣费上限。没有自动重试，也不自动换算金额。思考模式消耗的输出预算可能影响正文与工具参数长度。

作品配置绑定模型、接口、思考模式和max_tokens。续写时保持一致；轮次、超时与操作预算可显式调整。

## 命令行

在项目目录运行（非Windows环境将.venv/Scripts/python.exe换为.venv/bin/python）：

```powershell
.venv/Scripts/python.exe -m tome_agent check
.venv/Scripts/python.exe -m tome_agent demo-v4 --output data/v4-demo.json
.venv/Scripts/python.exe -m tome_agent plan --id my-novel --title 我的小说 --prompt-file story.txt --chapters 8 --target-units 10000 --allow-paid
.venv/Scripts/python.exe -m tome_agent generate --id my-novel --chapters 1 --allow-paid
.venv/Scripts/python.exe -m tome_agent generate --id my-novel --chapters 1 --resume-attempt --max-turns 40 --allow-paid
.venv/Scripts/python.exe -m tome_agent export-v4 --input data/books/my-novel/book.json --output data/my-novel.md
```

check不联网且不展示密钥；demo-v4只调用模拟模型。plan/generate真实调用模型，必须显式allow-paid。

## 存档与故障

- 正式存档：data/books/作品ID/book.json。每章成功后保存。
- 失败工作副本：book.json.attempt.json，包括工具消息、pending和已用轮次。
- 用量：planning-usage.json、generation-usage.json记录最近一次相应操作；正文工具轨迹在attempt中。不是累计账单。
- 网络失败后打开同一作品并勾选恢复工作副本。恢复要求基准一致；预算耗尽时增加轮次需要你明确设置。
- 作品锁operation.lock阻止应用同时写同一作品。若进程崩溃，确认无运行任务后可手动删除该锁。
- 模型完成后仍无法提交时检查pending、引文和工具反馈，不能手动清pending伪装成功。
- 当前页面不支持直接编辑已提交章节；它们绑定记忆来源。需要更改时另建作品或开发显式复核流程。

## 交付边界

本版本实现真实DeepSeek适配器与本地工作台，已用模拟HTTP和Streamlit测试工具验证。未使用真实密钥进行在线生成，模型权限、余额、提供商实时行为及长篇质量仍需用户实际验证。自动提交通过结构校验的章节，不包含人工逐条记忆审核模式。

正文会发送至模型提供商；不在请求中包含本机API密钥以外的配置内容。系统不自动上传INF writer材料。作品与过程记录默认在Git忽略范围内。
