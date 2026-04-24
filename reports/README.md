# Reports

`reports/` 存放按用户要求生成的总结性报告，用来避免用户必须逐个目录阅读材料。

## 使用场景

- 汇总整个工作区当前状态。
- 汇总某个项目、主题、文献群或时间段的进展。
- 把分散在 `dashboard/`、`literature/`、`projects/`、`methods/` 中的信息整理成可阅读报告。
- 生成给导师、合作者、会议或个人复盘使用的材料。

## 格式规则

- 用户指定格式时，按用户要求生成，例如 Markdown、PDF、LaTeX、DOCX。
- 用户未指定格式时，AI 助手必须先询问目标格式。
- Markdown、LaTeX 等源稿放在 `reports/`。
- PDF、DOCX 等导出成品放在 `reports/dist/`。
- 默认不把报告内容反写回源目录；源目录仍保存原始笔记、项目状态和研究材料。

## 命名规则

报告文件名建议包含日期、主题和格式用途：

```bash
reports/
├── 2026-04-24-workspace-summary.md
├── 2026-04-24-literature-review-draft.tex
└── dist/
    ├── 2026-04-24-project-progress.pdf
    └── 2026-04-24-meeting-brief.docx
```

## 生成要求

- 报告必须说明信息来源，至少列出读取过的关键目录或文件。
- 对不确定内容标注“待验证”，不要把推断写成事实。
- 涉及文献时不得编造作者、年份、DOI、页码或结论。
- 涉及文献全文或补充材料时遵守 `literature/README.md` 的软链接规则。
- 报告可以综合和压缩信息，但不应替代源目录中的原始记录。
