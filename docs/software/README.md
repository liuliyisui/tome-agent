# 软件设计资料

本目录保存使用说明、验证记录和发布材料。项目包含 Vue 前端、Python 服务层、INF 创作引擎和 DeepSeek 接口；存储与部署配置请参阅相应使用说明。

核心技术选型及未来一周自学计划见 [技术方案调研报告](architecture.md)。当前编排已迁移到 LangGraph，具体实现与存档边界见 [迁移说明](LANGGRAPH_MIGRATION.md)。

原型展示见 [AI 交互原型与演示步骤](prototype/README.md)，打开 [原型页面](prototype/index.html) 即可体验，无需安装依赖或配置 API Key。

设计详情见[系统架构](../algorithm/ARCHITECTURE.md)和[使用说明](USER_GUIDE.md)。

Python 代码质量规范与整改记录见[代码质量整改清单](CODE_QUALITY_FIXES.md)（Ruff + Pylance 方案，含配置文件说明与逐条修改对照）。

整改后的复审意见（含优先级排序的遗留问题）见[代码评审报告](CODE_REVIEW_20261107.md)。

首轮缺陷测试的检查表、执行记录与缺陷清单见[测试检查表](QA_DEFECT_TEST_ROUND1.md)。

