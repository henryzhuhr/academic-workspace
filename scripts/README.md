# Scripts

`workspace.py` 是工作区的统一入口，由 uv 提供锁定的 Python 3.9+ 环境和 PDF 元数据依赖。不要使用裸 `python3` 执行工作区命令。

```bash
uv run scripts/workspace.py new <slug> [options]
uv run scripts/workspace.py check
uv run scripts/workspace.py dashboard
uv run scripts/workspace.py paper add <pdf> [options]
```

- `new`：从 `projects/_template/` 原子化创建项目，写入元数据并更新 dashboard。
- `check`：只读检查目录、JSON、项目字段、交叉引用、本地 Markdown 链接、文献软链接和 dashboard 漂移。
- `dashboard`：从项目元数据重建 `dashboard/projects.md`。
- `paper add`：校验并复制 PDF 到仓库外全文库，生成 BibTeX、SHA-256、阅读笔记、阅读队列和可选课题关联；先使用 `--dry-run` 预演。

除 `paper add` 外，工作区工具不得读取或修改 `literature/files` 指向的外部全文库。`paper add` 只在软链接有效且目标位于仓库外时工作，不覆盖不同内容的同名文件，不删除源文件，并在写入失败时回滚本次新增内容。
