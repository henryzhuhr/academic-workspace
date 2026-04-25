# AGENTS.md

本文件是 `academic-workspace` 的入口规范，面向本人和所有 AI 助手。仓库定位为长期、多课题、知识库优先的科研工作区。

## 工作方式

AI 助手处理任务前必须先读：

1. 本文件。
2. 任务涉及目录下的 `README.md`。
3. 具体项目或材料目录中的局部说明。

如果目录存在 `README.md`，该文件就是该目录的本地规范；不要把目录细则继续堆进本文件。

## 目录索引

```bash
.
├── inbox/       # 临时收集和待整理材料，见 inbox/README.md
├── dashboard/   # 工作区总览、计划、复盘和索引，见 dashboard/README.md
├── literature/  # 文献笔记、BibTeX 和外部文献文件入口，见 literature/README.md
├── projects/    # 具体研究项目，见 projects/README.md
├── methods/     # 方法、协议和可复用研究规范，见 methods/README.md
├── assets/      # 通用图片、图表和演示素材，见 assets/README.md
├── reports/     # 按需生成的总结性报告，见 reports/README.md
├── tmp/         # 单次会话的临时缓存与脚本，git 忽略
└── archive/     # 已完成、暂停或废弃内容归档，见 archive/README.md
```

## 全局原则

- 知识优先：Markdown 是默认知识载体，重要判断、来源、假设和下一步必须写下来。
- 可追溯：研究结论应能追溯到文献、笔记、数据、代码、实验记录或明确的推理过程。
- 原始材料只读：原始数据、文献文件、访谈记录、截图和不可再生文件不得被覆盖。
- 少搬动：优先在既有结构中补充内容，避免无必要的重命名和批量移动。
- 轻工具依赖：可使用 Zotero、Obsidian、LaTeX、Python、R、Quarto、Makefile 等工具，但仓库规范不绑定具体工具链。

## 命名约定

- 日期使用 `YYYY-MM-DD`。
- 项目、文件夹和机器可读文件使用 `lower-kebab-case`。
- 日志、周报和会议纪要建议以日期开头，例如 `2026-04-24-weekly-review.md`。
- 对外输出文件应标明版本或日期，例如 `paper-draft-2026-04-24.pdf`。
- 脚本中引用用户家目录时统一使用 `$HOME`，不要写死 `/Users/<name>` 绝对路径。

## AI 助手约束

- 不得编造文献、DOI、作者、页码、数据来源或实验结果。
- 不确定的事实必须标记为待验证，或请求联网/用户确认。
- 不把论文 PDF、EPUB、HTML、补充材料或出版社全文下载到普通仓库目录；全文材料必须通过 `literature/files/` 软链接进入仓库外文献库。
- 每次启动文献文件、BibTeX、文献笔记或文献报告相关任务时，必须检查 `literature/files` 是否存在且为有效软链接；缺失或失效时，持续提醒用户先创建软链接。
- 用户要求“总结”“报告”“汇总”“给我看整体情况”时，优先产出到 `reports/`；源稿放 `reports/`，导出的 PDF/DOCX 等成品放 `reports/dist/`；如果未指定格式，先询问要 Markdown、PDF、LaTeX 还是 DOCX。
- 不进行大规模删除、重命名、移动或格式化，除非用户明确要求。
- 修改目录规则时，优先更新该目录的 `README.md`；只有影响全仓库的规则才写入本文件。

## 强制检查项

- 文献库软链接：涉及 `literature/`、文献文件、BibTeX、文献笔记或文献报告时，先执行等价于 `test -L literature/files && test -e literature/files` 的检查。
- 若 `literature/files` 缺失或不是有效软链接，不要下载文献文件，不要创建普通目录，必须提醒用户配置仓库外文献库软链接。

## 维护规则

- 目录规则放在对应目录的 `README.md`。
- 本仓库本身作为科研工作区模板；fork、clone 或新分支应直接沿用当前目录结构。
- 具体项目可以在自己的 `README.md` 中补充局部规则。
- 当局部规则与本文件冲突时，优先遵守更具体、更新且明确说明原因的项目规则。
- 有 `README.md` 的目录不需要 `.gitkeep`；空目录如果需要被 git 跟踪，则保留 `.gitkeep`。
- 临时会话文件统一放入 `tmp/session-<YYYYMMDDHHMMSS>/`；该目录用于下载缓冲、一次性脚本和处理中间文件，完成后应删除。
