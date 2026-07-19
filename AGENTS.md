# AGENTS.md

本文件是 `academic-workspace` 的全局入口规范，面向本人和所有 AI 助手。工作区采用“Markdown 知识 + JSON 元数据 + 外部大文件”的多课题研究模型。

## 启动顺序

处理任务前必须依次读取：

1. 本文件。
2. 任务涉及顶层目录的 `README.md`。
3. 具体项目或材料目录中的局部说明。

涉及目录结构、元数据、Schema、工作区 CLI 或跨目录规则时，还必须阅读 `ARCHITECTURE.md`。

局部规则应写在最接近材料的 `README.md` 中；不要把目录细则继续堆入本文件。

## 目录职责

```text
inbox/       临时捕获，定期清空
dashboard/   全局组合视图、阅读队列和周期复盘
projects/    具体研究课题；每个课题是独立研究单元
literature/  跨课题共享的文献引用、笔记和综述
methods/     可复用的方法、协议和研究规范
assets/      非项目专属的通用素材
reports/     跨项目或按需生成的总结报告
archive/     非项目专属的历史材料
schemas/     机器可读元数据 Schema
scripts/     工作区初始化、校验和索引工具
tests/       工作区工具的隔离回归测试
pyproject.toml / uv.lock  Python 环境和锁文件
package.json / package-lock.json  可选 Node 工具环境和锁文件
tmp/         单次会话临时文件，Git 忽略
```

## 核心原则

- 知识优先：重要判断、来源、假设、限制和下一步必须写入 Markdown。
- 单一来源：项目研究内容以项目 README 为入口；项目状态以 `project.json` 为唯一机器可读来源。
- 可追溯：结论必须能回到文献、数据、代码、运行记录、实验记录或明确推理。
- 原始材料只读：原始数据、访谈、档案、截图和不可再生文件不得覆盖。
- 共享不复制：跨课题文献、方法和通用素材只保留一份，项目通过相对链接引用。
- 稳定路径：项目完成后保留在 `projects/<slug>/` 并更新状态，不因归档而移动整个项目。
- 环境统一：所有工作区 Python 命令通过 `uv run` 执行；CLI 本身只使用 Python 标准库。
- 工具分层：根 npm 包只承载 Agent 插件、Markdown lint 等可选仓库工具，不定义研究项目运行环境。

## 项目规则

- 新项目必须通过 `uv run scripts/workspace.py new <slug>` 或等价地复制 `projects/_template/` 创建。
- 项目目录名和 `project.json.id` 必须一致，并使用 `lower-kebab-case`。
- `project.json` 必须符合 `schemas/project.schema.json`；不要在 dashboard 中另建一份项目状态。
- 项目 README 必须记录研究问题、范围、当前判断、证据、限制和下一步。
- `data/raw/` 默认不进入 Git；项目的数据登记表必须说明来源、许可、敏感等级、位置和校验信息。
- 计算型研究必须记录环境、入口、输入、输出和关键运行参数；非计算型项目可在分析说明中标注不适用。

## 文献规则

- 启动文献文件、BibTeX、文献笔记或文献报告任务时，先检查 `test -L literature/files && test -e literature/files`。
- 全文 PDF、EPUB、HTML、补充材料和出版社下载文件只通过 `literature/files/` 访问，不进入普通仓库目录。
- 如果软链接缺失或失效，不得下载文献文件或创建普通 `literature/files/` 目录；应持续提醒用户配置仓库外文献库。
- 不得编造作者、题名、年份、DOI、页码、来源、数据或实验结果；不确定内容必须标注“待验证”。

## 输出与归档

- 项目专属论文、图表、幻灯片和交付物放入项目 `outputs/`；其源稿放在 `writing/` 或 `analysis/`。
- 跨项目总结、阶段汇总和按需报告放在 `reports/`；PDF、DOCX 等导出文件放在 `reports/dist/`。
- 项目内部旧方案和历史版本进入项目 `archive/`；顶层 `archive/` 只存放不属于某个项目的历史材料。
- 不进行大规模删除、重命名、移动或格式化，除非用户明确授权。

## Git 与临时文件

- 所有长期课题应在同一主工作分支共存；不要长期“一课题一分支”。
- 分支仅用于短期变更，完成后合并回主工作分支。
- 提交信息统一使用“Emoji + Conventional Commits 类型 + 中文描述”，必要时可增加作用域，例如 `✨ feat(projects): 新增课题模板`、`📝 docs: 更新工作区说明`。
- 常用类型与 Emoji：`✨ feat`、`🐛 fix`、`📝 docs`、`♻️ refactor`、`✅ test`、`🔧 chore`、`👷 ci`、`📦 build`。
- 用户已有或未提交的修改必须保留；不得覆盖不可再生材料。
- 临时会话文件统一放入 `tmp/session-<YYYYMMDDHHMMSS>/`，完成后删除。
- 脚本引用用户家目录时使用 `$HOME`，不得写死 `/Users/<name>`。
- Python 依赖通过 `uv add`/`uv remove` 管理并提交 `uv.lock`；Node 工具依赖通过 npm 管理并提交 `package-lock.json`。

## 命名与维护

- 日期使用 `YYYY-MM-DD`；目录和机器可读文件使用 `lower-kebab-case`。
- 日志、周报和会议纪要以日期开头；对外输出标明日期或版本。
- 修改目录规则时优先更新该目录的 `README.md`；只有跨目录规则才更新本文件。
- 结构变更后运行 `uv run scripts/workspace.py check` 和 `uv run python -m unittest discover -s tests -v`；项目状态变更后运行 `uv run scripts/workspace.py dashboard`。
