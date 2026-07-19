# Schemas

本目录保存工作区机器可读配置的 JSON Schema：

- `workspace.schema.json`：根目录 `workspace.json` 的结构。
- `project.schema.json`：每个项目 `project.json` 的结构。

Schema 为编辑器提供提示，`scripts/workspace.py check` 负责无需第三方依赖的运行时校验。新增或修改元数据字段时，必须同步更新 Schema、CLI、项目模板和相关 README。

