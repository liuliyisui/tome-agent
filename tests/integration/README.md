# 集成测试目录

本目录保存端到端、页面、作品标识和长文写作流程的集成测试。

测试用例文档见 [../TEST_CASES.md](../TEST_CASES.md)，其中 §3–§4 为集成测试与 E2E 用例：

- `test_story_flow_e2e.py`：创建作品 → 生成章节 → 导出 Markdown（场景法）
- `test_service.py`：应用服务、失败保留与检查点
- `test_web.py`：Web API 契约
