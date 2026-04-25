# Academic Workspace

这是一个长期、多课题、知识库优先的科研工作区模板。它适合 fork、clone 或在新分支上启动新的研究工作流。

## 快速开始

1. 阅读 [AGENTS.md](AGENTS.md)，了解全局规则和 AI 助手协作方式。
2. 按任务进入对应目录，并阅读该目录的 `README.md`。
3. 在 `dashboard/projects.md` 维护项目索引，在 `dashboard/reading.md` 维护阅读队列。
4. 新课题放入 `projects/<project-slug>/`，文献笔记放入 `literature/`，总结性报告放入 `reports/`。
5. 如需管理论文全文或补充材料，先按 [literature/README.md](literature/README.md) 创建 `literature/files` 软链接。

## 目录概览

```bash
.
├── inbox/       # 临时收集和待整理材料
├── dashboard/   # 工作区总览、计划、复盘和索引
├── literature/  # 文献笔记、BibTeX 和外部文献文件入口
├── projects/    # 具体研究项目
├── methods/     # 方法、协议和可复用研究规范
├── assets/      # 通用图片、图表和演示素材
├── reports/     # 按需生成的总结性报告
├── tmp/         # 单次会话的临时缓存与脚本，git 忽略
└── archive/     # 已完成、暂停或废弃内容归档
```

## 关键约定

- 仓库内保存笔记、索引、代码、报告和可追溯记录。
- 论文 PDF、EPUB、HTML、补充材料等文献文件不进入 git；通过 `literature/files` 软链接指向仓库外文献库。
- 报告源稿放在 `reports/`，导出的 PDF/DOCX 等成品放在 `reports/dist/`。
- 一次性下载、临时脚本和处理中间文件放在 `tmp/session-<YYYYMMDDHHMMSS>/`，任务完成后删除整个 session 目录。
