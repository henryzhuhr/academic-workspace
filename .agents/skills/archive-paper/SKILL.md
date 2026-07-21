---
name: archive-paper
description: 将下载的学术论文 PDF 归档到工作区的外部文献库，并创建可追溯的 BibTeX、阅读笔记、校验和、阅读队列及课题关联记录。用户要求归档、入库、登记、编目或添加本地论文（包括 arXiv PDF）时使用。
---

# 论文入库

使用工作区命令执行确定性写入。PDF 元数据在与论文正文或权威来源核对前，一律视为待验证信息。

## 工作流程

1. 阅读 `AGENTS.md` 和 `literature/README.md`。
2. 检查 `test -L literature/files && test -e literature/files`。检查失败时停止，不创建 `literature/files`，也不复制 PDF。
3. 检查 PDF 元数据和文件名。只有文件名或用户明确提供时，才能推断 arXiv 编号。不得编造作者、标题、年份、 DOI、出版物或课题关联。
4. 从 `projects/*/project.json` 确认相关课题 ID。关联不明确时不要使用 `--project`。
5. 先预演操作：

   ```bash
   uv run scripts/workspace.py paper add "$PDF_PATH" --project <project-id> --dry-run
   ```

6. 检查候选标题、作者、目标路径、BibTeX key、笔记路径和 SHA-256。使用 `--title`、重复使用 `--author`、`--year`、`--arxiv`、`--doi`、`--url`、`--venue` 或 `--citation-key` 修正元数据。
7. 元数据可信后，使用相同命令并移除 `--dry-run`。
8. 运行 `uv run scripts/workspace.py check`，报告所有生成的记录以及仍标记为 `_TBD_` 的字段。

## 安全约束

- 保留源 PDF。命令只复制并校验文件；除非用户在校验后明确要求，否则不得删除 Downloads 中的副本。
- 全文只能通过外部 `literature/files` 软链接存储，不得把 PDF 提交到普通仓库目录。
- 保留 arXiv 的版本后缀，例如 `v1`；不同版本可以并存。
- 不覆盖目标文件，不重复登记 arXiv 论文，不复用冲突的 BibTeX key。
- 只有用户不希望加入阅读队列时才使用 `--no-queue`。
- 每个相关课题使用一次 `--project`；已知优先级时使用 `--priority high|medium|low`。

## 示例

归档一篇 arXiv 下载文件并关联一个课题：

```bash
uv run scripts/workspace.py paper add "$HOME/Downloads/2603.22853v1.pdf" \
  --project ai-agent-security \
  --priority high
```

写入前修正不完整的 PDF 元数据：

```bash
uv run scripts/workspace.py paper add "$PDF_PATH" \
  --title "Verified paper title" \
  --author "Family, Given" \
  --year 2026 \
  --dry-run
```
