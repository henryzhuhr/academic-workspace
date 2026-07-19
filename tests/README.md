# Tests

本目录使用 Python 标准库 `unittest` 对工作区 CLI 做隔离回归测试。测试在系统临时目录复制最小工作区，不修改真实项目或外部文献库。

```bash
uv run python -m unittest discover -s tests -v
```
