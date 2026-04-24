# Projects

`projects/` 存放具体研究项目。每个项目使用稳定的 `lower-kebab-case` 目录名。

## 项目结构

```bash
projects/
└── <project-slug>/
    ├── README.md
    ├── planning/
    ├── notes/
    ├── data/
    │   ├── raw/
    │   ├── processed/
    │   └── metadata/
    ├── analysis/
    ├── writing/
    ├── outputs/
    └── archive/
```

## 项目 README 必备内容

- 研究问题：本项目试图回答什么。
- 当前状态：`idea`、`active`、`paused`、`writing`、`submitted`、`published`、`archived`。
- 背景与动机：为什么这个问题值得研究。
- 核心材料：关键文献、数据、案例、访谈、档案或理论资源。
- 当前结论：已经相对稳定的发现或判断。
- 下一步：最重要的 1 到 3 个行动。
- 相关路径：文献笔记、分析脚本、草稿、输出物的位置。

## 新建项目步骤

1. 创建 `projects/<project-slug>/`，项目名使用 `lower-kebab-case`。
2. 按上面的项目结构建立子目录。
3. 写项目 `README.md`，至少补全研究问题、当前状态、核心材料和下一步。
4. 在 `dashboard/projects.md` 添加项目索引。
5. 如项目有阅读计划，在 `dashboard/reading.md` 添加相关条目。

## 子目录语义

- `planning/`：研究设计、问题拆解、计划、会议纪要、任务清单。
- `notes/`：项目内的概念笔记、材料摘录、分析备忘和推理记录。
- `data/`：数据或材料；原始材料进入 `data/raw/`，不得覆盖。
- `analysis/`：代码、计算笔记、统计分析、图表生成过程。
- `writing/`：论文、报告、提纲、段落草稿、投稿材料。
- `outputs/`：导出的图表、表格、幻灯片、预印本、报告成品。
- `archive/`：过期方案、废弃草稿、历史版本和阶段归档。
