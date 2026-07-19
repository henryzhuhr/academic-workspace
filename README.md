# Academic Workspace v2

一个面向长期、多课题并行研究的工作区。它把研究知识、机器可读状态和大体量原始材料分开管理：Markdown 保存可阅读、可追溯的研究内容，JSON 保存可校验的项目元数据，原始文件按数据策略决定是否进入 Git。

系统边界、权威来源和演进规则见 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 工作模型

```text
inbox ──整理──> literature / methods / projects
                         │
                         ├──> dashboard（组合视图）
                         └──> reports（跨项目总结）
projects/<slug> ────────> outputs（项目正式产物）
```

- `projects/<slug>/README.md` 是课题的研究入口。
- `projects/<slug>/project.json` 是课题状态的唯一机器可读来源。
- `dashboard/projects.md` 由项目元数据生成，不手工维护项目状态。
- `literature/` 和 `methods/` 是跨课题共享知识层；项目通过链接引用，不复制同一份知识。
- 大型、敏感或不可再生材料默认不进入 Git；仓库保存元数据、路径映射和处理过程。

## 目录

```text
.
├── ARCHITECTURE.md # 系统设计、不变量与演进协议
├── pyproject.toml  # uv 管理的 Python 环境
├── uv.lock         # Python 环境锁文件
├── package.json    # 可选的 Agent / Markdown / Node 工具层
├── workspace.json  # 工作区配置
├── inbox/          # 尚未归位的临时材料
├── dashboard/      # 项目组合、阅读队列与周期复盘
├── projects/       # 具体研究课题及项目模板
├── literature/     # 文献库、阅读笔记和主题综述
├── methods/        # 跨课题复用的方法与研究规范
├── assets/         # 非项目专属的通用素材
├── reports/        # 跨项目或按需生成的总结报告
├── archive/        # 非项目专属的历史材料
├── schemas/        # 工作区和项目元数据 Schema
├── scripts/        # 无第三方依赖的工作区工具
└── tests/          # 工作区工具的隔离回归测试
```

## 快速开始

核心环境要求：uv；工作区 Python 版本为 3.9 或更高。Node.js/npm 仅用于可选的 Agent 插件、Markdown lint 等仓库工具。

```bash
# 检查工作区结构和元数据
uv run scripts/workspace.py check

# 创建新课题
uv run scripts/workspace.py new my-research-topic --title "My Research Topic"

# 根据所有 project.json 重建项目总览
uv run scripts/workspace.py dashboard

# 运行工作区工具测试
uv run python -m unittest discover -s tests -v
```

也可以通过 npm 的便捷入口运行 `npm run check`、`npm run dashboard` 和 `npm test`。根 npm 包设置为 `private`，只承载工作区工具，不发布到 registry。

新项目创建后，先完成项目 README 中的研究问题、边界、证据和下一步，再开始导入材料。

## Git 策略

所有长期课题共存在同一个主工作分支中。不要用长期分支隔离不同课题，否则全局索引、共享文献和方法会彼此分叉。分支仅用于短期修改、实验性重构或协作审阅，完成后合并回主工作分支。

## AI 协作

AI 助手先读 [AGENTS.md](AGENTS.md)，再读任务涉及目录及具体项目的局部说明。仓库内的 `.agents/skills/` 是有意版本化的工作区工具能力，`.claude/skills` 仅作为兼容入口。
