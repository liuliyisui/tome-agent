# 代码质量

项目使用 `code/backend/pyproject.toml` 中的 Ruff 规则检查 Python 代码和格式。仓库根目录执行：

```powershell
code\backend\.venv\Scripts\python.exe -m ruff check --config code/backend/pyproject.toml --no-cache .
code\backend\.venv\Scripts\python.exe -m ruff format --config code/backend/pyproject.toml --no-cache --check .
```

历史检查记录、规则配置与修复说明见 [CODE_QUALITY_FIXES.md](CODE_QUALITY_FIXES.md) 和 [quality/QUALITY_REPORT.md](quality/QUALITY_REPORT.md)。测试范围、测试命令和覆盖率口径见 [测试用例总览](../../tests/TEST_CASES.md)。历史结果仅对应记录中说明的代码版本，当前结果应以重新运行的检查为准。
