# 单元测试目录

本目录保存框架、写作引擎、模型适配器与作品输入校验的单元测试。

测试用例文档见本目录 [TEST_CASES.md](TEST_CASES.md)：

- `test_book_input_validation.py`：作品输入校验（等价类 + 边界值）
- `test_length_control.py`：章节长度控制
- `test_domain_support_contract.py`：证据绑定与支持审核

集成与 E2E 用例见 [../integration/TEST_CASES.md](../integration/TEST_CASES.md)。
