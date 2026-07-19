# Projects

`projects/` 保存所有长期研究课题。每个课题都是自包含的研究单元，同时通过链接复用 `literature/`、`methods/` 和 `assets/` 中的共享知识。

`_template/` 是保留目录，不是研究项目，也是 `lower-kebab-case` 命名规则的唯一例外。

## 创建项目

```bash
uv run scripts/workspace.py new project-slug --title "Project Title"
```

可选参数包括 `--area`、`--owner`、`--status` 和 `--data-classification`。工具会复制项目模板、写入日期和元数据、校验项目，并更新项目 dashboard。

## 标准结构

```text
projects/<project-slug>/
├── project.json          # 机器可读状态；dashboard 的唯一数据源
├── README.md             # 研究问题、判断、证据、限制和下一步
├── .gitignore            # 本项目的数据与运行产物策略
├── planning/             # 设计、计划、会议与决策记录
├── notes/                # 项目专属的研究备忘
├── data/
│   ├── README.md         # 数据登记表与数据治理说明
│   ├── raw/              # 只读原始数据，默认不进入 Git
│   ├── processed/        # 可再生的处理数据，默认不进入 Git
│   └── metadata/         # 字典、清单、校验值、许可和来源
├── analysis/             # 代码、计算笔记和复现入口
│   └── runs/             # 关键运行记录，载荷默认不进入 Git
├── writing/              # 论文、报告和投稿源稿
├── outputs/              # 项目正式交付物及其产物清单
└── archive/              # 项目内部的旧方案和历史版本
```

并非所有课题都需要相同工具链。目录提供稳定语义，具体项目可在自己的 README 中增加更细的结构，但不得改变原始材料只读、状态单一来源和结果可追溯三项原则。

## 项目元数据

`project.json` 必须符合 `schemas/project.schema.json`。关键字段包括：

- `id`：稳定项目标识，必须等于目录名。
- `status`：`idea`、`active`、`paused`、`writing`、`submitted`、`published` 或 `archived`。
- `area`、`tags`：用于跨项目聚合，不代替研究内容。
- `summary`、`nextAction`：用于 dashboard 的简短组合视图。
- `updated`、`nextReview`：用于识别失去维护的项目。
- `relatedProjects`：只填写其他项目的稳定 `id`。
- `dataClassification`：`public`、`internal`、`sensitive` 或 `restricted`。

项目 README 仍是面向人的主入口。元数据只保存状态，不承载复杂论证。

## 状态与复盘

- `idea`：问题仍在形成，尚未投入稳定资源。
- `active`：正在收集、分析或验证材料。
- `paused`：保留价值，但当前不安排行动。
- `writing`：主要工作已转向写作与整合。
- `submitted`：已提交，等待反馈或处理修订。
- `published`：正式输出已完成，仍可能维护衍生工作。
- `archived`：不再活跃；项目保留原路径，不整体移动。

`active` 和 `writing` 项目必须填写 `nextAction` 与 `nextReview`。每次重要判断变化后更新 `updated`，并在 `planning/decision-log.md` 留下原因。

## 数据与复现

- 数据登记遵守 [methods/data-management.md](../methods/data-management.md)。
- 计算与分析遵守 [methods/reproducibility.md](../methods/reproducibility.md)。
- 项目默认忽略 `data/raw/`、`data/processed/` 和 `analysis/runs/` 中的载荷，但保留各目录 README。若确需跟踪小型公开数据，应在项目 `.gitignore` 中显式调整并记录理由。
- 密钥、令牌、个人身份信息和受限材料不得进入 Git。

## Dashboard

不要手工复制项目状态到 `dashboard/projects.md`。修改 `project.json` 后运行：

```bash
uv run scripts/workspace.py dashboard
uv run scripts/workspace.py check
```
