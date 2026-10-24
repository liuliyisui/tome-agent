# 五万字稳定版本 · 2026-10-23

> 历史版本记录。当前已升级到 tested-c-20261024，见 ENGINE_UPDATE_20261024.md。

本版本对应ar真实测试：25章50107汉字，固定源码连续运行，无人工续跑。4处异常降级未阻断生成；正文记忆齐全，3章结构化状态未补齐。不包含此后尚未验证的意图编号及五次重试改动。

现有.env、novel_config.json及runs不覆盖。使用原配置照常运行write_novel.py；执行五万字配置：

    python -X utf8 -B write_novel.py --config novel_config_50000.json

运行会调用模型并产生费用。字数是目标，不保证精确相等；小说内容质量未认证。verification保存只读核对结果，不附带已完成作品。旧程序备份在history。
