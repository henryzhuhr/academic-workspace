# Literature

`literature/` 是跨项目共享的文献知识层，保存引用信息、阅读笔记、主题综述和外部全文库的稳定入口。项目通过相对链接引用这里的内容，不在各项目中复制同一份文献笔记。

## 结构

```text
literature/
├── bibliography.bib       # 全局 BibTeX 引用库
├── files -> <external>    # 指向仓库外全文库的本机软链接
├── reading-notes/         # 一篇文献一份可追溯笔记
├── topic-reviews/         # 跨文献综合、争议地图和阅读路线
├── authors/               # 作者、团队、学派与合作网络
└── venues/                # 期刊、会议、出版社与数据库信息
```

## 全文库

PDF、EPUB、HTML、补充材料和出版社下载文件不得进入 Git。`literature/files` 必须是指向仓库外文献库的软链接。

每次启动文献文件、BibTeX、文献笔记或文献报告任务时先检查：

```bash
test -L literature/files && test -e literature/files
```

通用配置：

```bash
EXTERNAL_LITERATURE_DIR="/path/to/external-literature-library"
mkdir -p "$EXTERNAL_LITERATURE_DIR"
ln -s "$EXTERNAL_LITERATURE_DIR" "literature/files"
```

如果软链接缺失或失效，不得创建普通 `files/` 目录或把全文下载到仓库。BibTeX 和笔记使用稳定的仓库相对路径 `literature/files/...`。

BibTeX 路径注释示例：

```bibtex
% local_file: literature/files/2026/author-short-title.pdf
@article{author2026short,
  title = {Short Title},
  author = {Author, Alice},
  year = {2026},
  doi = {10.xxxx/xxxxx}
}
```

## 阅读笔记

从 [reading-notes/template.md](reading-notes/template.md) 创建笔记，文件名优先使用稳定 BibTeX key；若尚无 key，使用 `lower-kebab-case` 临时名并在补全引用后统一更新链接。

笔记至少包含：

- 可验证的书目信息与本地文件路径；
- 一句话贡献、研究问题和语境；
- 关键主张、证据或方法及具体页码/位置；
- 方法限制、矛盾和待验证事项；
- 可复用洞见、关联项目 `id` 和后续行动。

摘要、作者、年份、DOI、页码和结论不得凭空补全。只有核对原始来源后，阅读状态才能标为 `verified`。

## 主题综述

从 [topic-reviews/template.md](topic-reviews/template.md) 开始，记录综述问题、检索范围、纳入标准、已知缺口、主张地图和更新日志。主题综述是跨文献综合，不是阅读笔记的拼接。
