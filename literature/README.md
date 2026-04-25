# Literature

`literature/` 保存文献笔记、主题综述、引用信息、阅读路线和本地文献文件的软链接入口。论文 PDF、EPUB、HTML、补充材料等全文文件不进入 git 仓库。

## 目录结构

```bash
literature/
├── README.md                 # 本目录规范
├── bibliography.bib          # 全局 BibTeX 引用库
├── files -> <external-library> # 指向仓库外文献文件库的软链接
├── reading-notes/            # 单篇文献阅读笔记
├── topic-reviews/            # 按主题整理的综述和文献脉络
├── authors/                  # 按作者或研究团队整理的资料
└── venues/                   # 按期刊、会议、出版社或资料来源整理的信息
```

## 子目录用途

- `bibliography.bib`：集中维护引用条目和本地文献文件路径注释。
- `files`：仓库内稳定入口，实际指向仓库外文献文件库。
- `reading-notes/`：一篇文献一份笔记，记录摘要、观点、方法、证据和可引用位置。
- `topic-reviews/`：跨文献的主题综述、概念谱系、争议地图和阅读路线。
- `authors/`：重要作者、研究团队、学派或合作网络的长期资料。
- `venues/`：期刊、会议、出版社、数据库或档案来源的投稿、检索和质量信息。

## 文献文件软链接

PDF、EPUB、HTML、补充材料等文献文件可以下载，但实际文件必须存放在仓库外。`literature/files` 是仓库内的稳定入口，具体指向哪里由本机决定。

通用配置方式：

```bash
EXTERNAL_LITERATURE_DIR="/path/to/external-literature-library"
mkdir -p "$EXTERNAL_LITERATURE_DIR"
ln -s "$EXTERNAL_LITERATURE_DIR" "literature/files"
```

> 如果希望在 macOS 上用 iCloud Drive 同步论文，可以把目标路径换成：
>
> ```bash
> mkdir -p "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Research/Literature"
> ln -s "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Research/Literature" "literature/files"
> ```

规则：

- `literature/files` 必须是指向仓库外文献库的软链接，不应是普通 git 目录。
- 克隆仓库、换电脑或执行任何文献相关任务时，先检查 `literature/files` 是否存在且有效：`test -L literature/files && test -e literature/files`。
- 如果 `literature/files` 缺失或失效，AI 助手必须提醒用户配置软链接；在配置完成前不要下载文献文件或创建普通 `files/` 目录。
- 若当前环境无法直接写入 `literature/files`，临时下载缓冲统一放入 `tmp/session-<YYYYMMDDHHMMSS>/literature/files/`，待用户移动到外部文献库后再清理。
- PDF、EPUB、HTML、补充材料、出版社下载文件等全文材料只通过 `literature/files/` 访问。
- `bibliography.bib` 和文献笔记中优先使用仓库相对路径 `literature/files/...`。

## 文献文件命名

文献文件名使用统一规则：

```text
<year>-<venue>-<first_author>-<short_title>.<ext>
```

示例：

```text
2024-NeurIPS-debenedetti-agentdojo.pdf
2024-arXiv-zhang-agent_security_bench.pdf
2025-OWASP-owasp-agentic_ai_threats.html
2024-Transactions_on_Machine_Learning_Research-wang-tool_safety_eval.pdf
```

字段规则：

- `year`：4 位数字。
- `venue`：按常见写法保留大小写；多个单词使用 `snake_case`。
- `first_author`：使用 `snake_case`。
- `short_title`：使用 `snake_case`，只保留核心词。
- 字段之间统一用 `-` 分隔；字段内部如需多词，统一用 `_`。
- `ext`：保留真实文件格式，例如 `pdf`、`epub`、`html`、`mobi`。

多文件材料建议使用同名目录：

```text
literature/files/papers/2024/2024-NeurIPS-debenedetti-agentdojo/
├── paper.pdf
├── supplement.pdf
└── appendix.pdf
```

若只有单个全文文件，可直接使用文件名：

```text
literature/files/papers/2024/2024-NeurIPS-debenedetti-agentdojo.pdf
```

## BibTeX Key 规则

`bibliography.bib` 中的 BibTeX key 默认与文献文件 stem 保持一致：

```text
<year>-<venue>-<first_author>-<short_title>
```

这样文件名、BibTeX key、阅读笔记和后续脚本都可以共用同一个稳定标识。

## Venue 写法表

为了避免同一 venue 混用不同写法，使用固定写法表。下面是当前建议的常用写法：

| Venue | Recommended Form |
| --- | --- |
| arXiv | `arXiv` |
| NeurIPS | `NeurIPS` |
| ICML | `ICML` |
| ICLR | `ICLR` |
| ACL | `ACL` |
| EMNLP | `EMNLP` |
| NAACL | `NAACL` |
| CVPR | `CVPR` |
| ICCV | `ICCV` |
| ECCV | `ECCV` |
| KDD | `KDD` |
| WWW | `WWW` |
| USENIX Security | `USENIX_Security` |
| IEEE S&P | `IEEE_SP` |
| CCS | `CCS` |
| NDSS | `NDSS` |
| TMLR | `Transactions_on_Machine_Learning_Research` |
| JMLR | `JMLR` |
| Nature | `Nature` |
| Science | `Science` |
| OWASP | `OWASP` |
| NIST | `NIST` |
| Technical report | `Tech_Report` |
| Web resource | `Web` |

BibTeX 路径注释格式：

```bibtex
% local_file: literature/files/papers/2024/2024-NeurIPS-debenedetti-agentdojo.pdf
@misc{2024-NeurIPS-debenedetti-agentdojo,
  title = {Short Title},
  author = {Author, Alice},
  year = {2026},
  doi = {10.xxxx/xxxxx}
}
```

## 文献笔记

文献笔记建议包含：

- 基本信息：标题、作者、年份、来源、DOI/URL、BibTeX key。
- 本地文件：如已下载全文或补充材料，记录 `literature/files/...` 路径。
- 一句话摘要：这篇文献解决什么问题，核心贡献是什么。
- 关键观点：可复用的概念、论点、结论或反例。
- 方法与证据：数据、模型、实验、论证方式和局限。
- 可引用内容：适合未来写作引用的结论，必须标明页码或位置。
- 关联项目：与哪些项目、问题、写作段落有关。
- 后续动作：需要精读、复查、复现、比较或引用的位置。
