# 架构说明：以 INF writer V4 完整运行链为基础

本项目独立实现对应模块，不复制或导入 NSTAgent 源码。参考范围为原版 agent_core 与 method1 → method1_v2 → method1_v3 → method1_v4 的依赖链，而非只参考 V4 的三个文件。本轮只读取参考项目，不执行其中的任务、历史实验或付费请求。

## 架构对应表

| 参考架构职责 | Tome Agent 实现 | 当前边界 |
|---|---|---|
| 前提、梗概、幕结构、冻结章节大纲 | planning.OutlinePlanner | 四阶段模型协议、缓存与指纹；仅模拟响应验证 |
| 全书顺序生成、章节检查点 | runner.StoryRunner | 显式章节上限，章间暂停，拒绝配置错配 |
| 工具调用章节循环 | agent.ChapterAgent | read/search/correct/write/update 与严格 DONE 完成门 |
| 人物、过去事件、未来义务 | state.NarrativeState | 三类叙事记录，义务保留解决记录 |
| 有来源和版本的事实账本 | submissions.apply_entry | store/update/retire、来源哈希、时锚保护 |
| 单次填写候选 | tools.chapter_tools / entry_errors | 一份entry生成写入与审计 |
| 依赖组与保守资源归并 | submissions.components / submit_groups | 显式依赖、同主体、同事件/任务键合并 |
| pending、收据、幂等 | NarrativeState | 空提交不清pending；成功同ID不可改写 |
| V4自动归档与替换证据 | submissions.apply_entry | 更新当前值，同时保留旧值及替换来源 |
| 按属性历史查询 | submissions.attribute_history | 本地只读，核原来源及替换来源；与V4一样未暴露为模型工具 |
| 整章事务、失败工作副本 | agent + checkpoints | 全部完成才替换正式检查点；失败另存attempt |

## 生成与提交顺序

1. OutlinePlanner生成premise、synopsis、acts、chapters，检查章节数并分配目标篇幅。缓存绑定输入、配置及内容指纹。
2. StoryRunner读取正式检查点，核对输入/大纲/配置，逐章运行；不并发生成同一作品。
3. ChapterAgent复制工作区，只向模型提供当前叙事状态、有效事实与冻结大纲。历史与审计不自动注入提示。
4. 模型按需read/search；write接受符合长度范围的完整正文。长度按CJK单字与ASCII词计数，不等于token。
5. update从当前接受正文提出单份entries及叙事操作；校验候选、版本、引文、认知归属与时间锚。omit/defer只审计。
6. 依赖连通分量整体成功或回滚，无关成功只在本章暂存。失败pending必须以原ID修复；成功收据绑定完整提案和正文。
7. write成功、update成功、pending为空、明确DONE、来源核验及事实容量检查通过后，才更新正式检查点。

## 工具与接口差异

章节编号从1开始；事件与任务用稳定字符串key；correct使用唯一精确文本替换。所有工具schema见tools.py。不能直接导入NSTAgent检查点或V4工具参数。第一轮简化模型schema_version=1不自动迁移到新workspace检查点schema_version=2。

## 修改、失败与恢复

correct允许修改未绑定来源的工作正文；若对应章节已有成功组收据则拒绝修改，要求显式记忆复核。尚未实现作者编辑后的自动失效传播。正式作品只在整章成功后变化。

每个完整工具轮次后，<checkpoint>.attempt.json保存工作区、草稿、pending、消息、反馈、用量与轮次。StoryRunner的resume_attempt=True可显式继续匹配正式基准hash的工作副本。已消耗轮次不重置；增加上限必须由调用者明确配置。过期或READY_TO_COMMIT的attempt不是正式成果，正式检查点始终权威。

Model协议注入模型传输；providers/deepseek.py使用OpenAI兼容SDK接入DeepSeek，保留reasoning_content、工具参数及用量。默认关闭SDK重试，应用层不自动重试或换算费用。service.py提供.env读取、显式付费入口、操作预算及同作品进程锁；Streamlit工作台与CLI共用该服务。尚未进行真实在线生成。

## 边界

- 已按完整架构职责搭建，不声称逐行复现NSTAgent或移植其全部生产优化。
- 检索目前为确定性子串匹配，未实现原版FTS、语义检索及查询改写。
- 长度控制为上下界，未移植动态token分配、拒绝历史压缩、近期失败自适应。
- 活跃事实保持12000 UTF-8字节上限，超限报错，不静默裁剪；消息和磁盘历史仍增长。
- service.py用作品锁拒绝并发写入；底层ChapterAgent仍要求调用者避免并发。规划中途恢复和网络调用期间取消尚未实现。
- 引文存在与schema正确不证明语义正确；漏选、误认主体、错误计数仍需评阅。
- 归档是记录版本，不证明旧值真实成立；替换章节不是故事日期。
- 工程测试不证明更少矛盾、更好的小说或更低费用。

