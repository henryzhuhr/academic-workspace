# arXiv 论文检索方法

## 目的

使用 arXiv 官方 API 进行可复现的论文检索，保存结构化元数据和检索参数，再将人工筛选后的论文交给工作区的归档流程。该方法只负责发现和记录论文，不负责批量下载或重新分发全文。

官方参考：

- [arXiv API User's Manual](https://info.arxiv.org/help/api/user-manual.html)
- [Terms of Use for arXiv APIs](https://info.arxiv.org/help/api/tou.html)

## 输入与输出

输入：

- 一个原始 `search_query`，或若干字段条件；
- 可选的 arXiv 分类、排序方式、分页范围和结果数量。

输出：

- 标题、作者、摘要、分类、提交时间和更新时间；
- arXiv ID、版本、abstract URL 和 PDF URL；
- 查询字符串、分页参数、排序参数和检索时间；
- 可选的 JSON 检索记录。

全文 PDF 不由检索脚本下载。选定论文后，使用 `workspace.py paper add` 进行预演和归档。

## 查询设计

先把研究问题拆为三个维度，再组合查询：

```text
对象：LLM agent / autonomous agent / tool-using agent
问题：prompt injection / jailbreak / data poisoning
目标：security / defense / audit / benchmark
```

常用 API 字段：

| 字段 | 含义 | 示例 |
| --- | --- | --- |
| `all` | 所有可检索字段 | `all:"prompt injection"` |
| `ti` | 标题 | `ti:security` |
| `au` | 作者 | `au:Goodfellow` |
| `abs` | 摘要 | `abs:tool-use` |
| `cat` | arXiv 分类 | `cat:cs.AI` |

查询过宽时使用 `AND` 缩小范围，相关同义词使用 `OR` 扩展范围：

```text
all:"prompt injection" AND cat:cs.AI
all:("LLM agent" OR "autonomous agent") AND all:(security OR defense)
```

## 使用脚本

脚本入口：`scripts/arxiv_search.py`。所有 Python 命令使用 `uv run`。

按字段查询并保存检索记录：

```bash
uv run scripts/arxiv_search.py \
  --all '"prompt injection"' \
  --category cs.AI \
  --limit 20 \
  --sort-by submittedDate \
  --sort-order descending \
  --output literature/searches/2026-07-22-prompt-injection.json
```

直接传入原始 API 查询：

```bash
uv run scripts/arxiv_search.py \
  'all:"tool use" AND (all:security OR all:prompt-injection)' \
  --limit 20
```

仅查询指定标题或作者：

```bash
uv run scripts/arxiv_search.py --title 'prompt injection' --limit 10
uv run scripts/arxiv_search.py --author 'Russell' --limit 10
```

分页检索时脚本默认在请求之间等待 3 秒：

```bash
uv run scripts/arxiv_search.py \
  'cat:cs.AI AND all:agent' \
  --start 20 \
  --limit 20
```

## 筛选与归档

1. 查看 JSON 中的标题、摘要、分类和更新时间。
2. 以 arXiv ID 去重；`v1`、`v2` 是同一论文的不同版本，应保留版本信息。
3. 打开 abstract URL 核对元数据和论文版本。
4. 只下载需要阅读的论文。
5. 先预演归档：

   ```bash
   uv run scripts/workspace.py paper add \
     "$HOME/Downloads/<arxiv-id>.pdf" \
     --project <project-id> \
     --dry-run
   ```

6. 核对标题、作者、年份、目标路径和 BibTeX key 后，移除 `--dry-run` 正式归档。

正式归档后，统一索引位于 `literature/catalog.json`；BibTeX 仍用于引用，阅读笔记仍用于记录研究理解。不要手工在多个文件之间复制本地路径或 SHA-256。

## 合规与复现要求

- 使用官方 API，不批量抓取 HTML 页面。
- API 请求至少间隔 3 秒，保持单连接，不通过多台机器绕过限制。
- 相同查询应缓存 JSON 结果，避免重复访问。
- 元数据可以保存和共享；PDF 和源文件仅用于个人或研究用途，不对外重新分发，除非许可证或版权持有人明确允许。
- 检索记录应保留查询字符串、日期、分页、排序和 API 来源，便于复现。
