# Scripts

`workspace.py` 是工作区的统一入口，由 uv 提供锁定的 Python 3.9+ 环境和 PDF 元数据依赖。不要使用裸 `python3` 执行工作区命令。

工作区的 `*.json` 文件保持严格 JSON，因此天然兼容 JSONC。Python 工具通过 `scripts/jsonc.py` 读取元数据，允许 `//`、`/* ... */` 注释和尾逗号；写入时仍输出严格 JSON。

```bash
uv run scripts/workspace.py new <slug> [options]
uv run scripts/workspace.py check
uv run scripts/workspace.py dashboard
uv run scripts/workspace.py paper add <pdf> [options]
uv run scripts/arxiv_search.py "<query>" [options]
```

- `new`：从 `projects/_template/` 原子化创建项目，写入元数据并更新 dashboard。
- `check`：只读检查目录、JSON、项目字段、交叉引用、本地 Markdown 链接、文献软链接和 dashboard 漂移。
- `dashboard`：从项目元数据重建 `dashboard/projects.md`。
- `paper add`：校验并复制 PDF 到仓库外全文库，更新 `literature/catalog.json`，并生成 BibTeX、SHA-256、阅读笔记、阅读队列和可选课题关联；先使用 `--dry-run` 预演。
- `arxiv_search.py`：调用 arXiv 官方 API 搜索并保存可复现的 JSON 元数据；不自动下载或重新分发 PDF。

示例：

```bash
uv run scripts/arxiv_search.py \
  --all '"prompt injection"' \
  --category cs.AI \
  --limit 20 \
  --sort-by submittedDate \
  --output literature/searches/2026-07-22-prompt-injection.json
```

原始 API 查询也可以直接作为位置参数传入：

```bash
uv run scripts/arxiv_search.py \
  'all:"tool use" AND (all:security OR all:prompt-injection)' \
  --limit 20
```

除 `paper add` 外，工作区工具不得读取或修改 `literature/files` 指向的外部全文库。`paper add` 只在软链接有效且目标位于仓库外时工作，不覆盖不同内容的同名文件，不删除源文件，并在写入失败时回滚本次新增内容。
