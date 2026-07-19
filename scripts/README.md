# Scripts

`workspace.py` 是工作区的统一入口，由 uv 提供 Python 3.9+ 环境，脚本本身只依赖标准库。不要使用裸 `python3` 执行工作区命令。

```bash
uv run scripts/workspace.py new <slug> [options]
uv run scripts/workspace.py check
uv run scripts/workspace.py dashboard
```

- `new`：从 `projects/_template/` 原子化创建项目，写入元数据并更新 dashboard。
- `check`：只读检查目录、JSON、项目字段、交叉引用、本地 Markdown 链接、文献软链接和 dashboard 漂移。
- `dashboard`：从项目元数据重建 `dashboard/projects.md`。

工具不得读取或修改 `literature/files` 指向的外部全文库。
