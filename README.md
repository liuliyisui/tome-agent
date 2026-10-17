# Tome Agent

面向长篇小说生成的写作助手。

通过分层规划、故事状态记忆和可恢复的逐章工具循环，把故事构想发展为连续章节。

## 当前交付

- DeepSeek真实接口适配器：.env配置、工具调用、推理内容回传、超时、用量与操作预算。
- 四阶段规划：前提→详细梗概→幕结构→冻结章节大纲。
- 逐章生成：read/search/correct/write/update→DONE。
- 三类叙事状态：人物、历史事件、未来义务。
- V4式事实账本：稳定属性、版本校验、来源引文、旧值及替换证据归档。
- 事务与恢复：依赖分组、pending修复、幂等收据、正式存档与失败工作副本。
- 全书调度：限定本次章节数、章间暂停、失败后显式恢复。
- 本地网页：创建作品、大纲编辑、续写、状态查看、Markdown与JSON导出。
- 依赖清单、完整锁定版本、Windows安装及启动脚本、自动测试工作流。

**已完成本地模拟验证，未发起真实付费生成。** 真实模型权限、连续长篇完成率和质量提升尚未验证。当前章节自动提交，作者逐条审核及编辑已提交正文后的记忆复核还未实现。

## 启动

需要Python 3.11或更高版本。

1. 双击setup.cmd安装依赖。
2. 在.env的DEEPSEEK_API_KEY=后填写密钥。
3. 双击start.cmd，打开显示的本地网页地址。
4. 新建作品，生成大纲，再选择作品逐章续写。

模型默认deepseek-flash；.env中空模型名也使用该默认值。依赖已安装在本机项目.venv，其他成员需运行setup.cmd。requirements.txt锁定直接依赖；requirements-lock.txt锁定完整解析结果。安装依赖仍需要网络，项目压缩包不是离线依赖安装包。

[问题定义与5W1H](docs/requirements/problem_definition.md) · [团队计划](docs/mgmt/TEAM_PLAN.md) · [Kanban](docs/mgmt/KANBAN.md) · [完整使用说明](docs/software/USER_GUIDE.md) · [架构对应说明](docs/algorithm/ARCHITECTURE.md) · [验证记录](docs/software/VALIDATION.md)

## 命令行

```powershell
.venv/Scripts/python.exe -m tome_agent check
.venv/Scripts/python.exe -m tome_agent demo-v4 --output data/v4-demo.json
.venv/Scripts/python.exe -m tome_agent plan --id my-novel --title 我的小说 --prompt-file story.txt --chapters 8 --target-units 10000 --allow-paid
.venv/Scripts/python.exe -m tome_agent generate --id my-novel --chapters 1 --allow-paid
.venv/Scripts/python.exe -m tome_agent export-v4 --input data/books/my-novel/book.json --output data/my-novel.md
.venv/Scripts/python.exe -m unittest discover -s tests -v
```

check和demo不联网。plan/generate产生模型费用，须显式添加--allow-paid；网页中需要主动确认。密钥不展示、不写入存档，.env、作品和运行数据已加入Git忽略规则。

## 目录

```text
setup.cmd / start.cmd        安装与启动
requirements*.txt            依赖及完整版本锁
code/frontend/app.py         本地网页工作台
code/backend/tome_backend/   DeepSeek适配、服务、检查点和存储
code/core_engine/tome_agent/ 规划、章节循环、记忆和全书调度
tests/unit/                  单元测试
tests/integration/           集成与页面测试
docs/requirements/           5W1H、产品描述与需求资料
docs/algorithm/              长文本生成算法说明
docs/software/               软件设计资料
docs/mgmt/                   团队计划、Kanban与缺陷流程
docs/retrospection/          迭代复盘
data/books/                  本地作品与过程记录（不提交）
```

第一轮简化框架domain.py/memory.py/pipeline.py及旧demo/export命令保留作历史实现；当前主流程使用Workspace、ChapterAgent和StoryRunner，两种存档不混用。

## 长文本验证计划

先验证约一万中文字、8–10章的完整创作，再测试更长篇幅。这是目标，不是已验证能力。使用同一DeepSeek模型、相同输入和大纲对比摘要续写与状态记忆续写，记录实际篇幅、完成率、明确跨章矛盾、情节完成度、重复停滞、耗时及token用量。未涉及目标事实不计为修复成功。

## 参考与原创边界

参考[NSTAgent](https://github.com/zhennan1/NstAgent)及本地INF writer的原版核心→method1→V2→V3→V4依赖链。未复制或导入其源码，不依赖参考文件运行，也不声称相关方法首次提出。工具和检查点使用Tome独立格式。

DeepSeek适配依据[官方首次调用说明](https://api-docs.deepseek.com/)和[工具调用文档](https://api-docs.deepseek.com/guides/tool_calls/)，核对日期2026-10-17。

格式正确和引文存在不等于语义正确，归档不自动证明旧值真实；工程测试不能替代长篇效果评测。更详细的接口差异、未移植优化及已知边界见架构说明。

