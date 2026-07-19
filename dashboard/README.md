# Dashboard

`dashboard/` 是多课题工作区的组合管理层，只保存索引、优先级、复盘和近期行动，不承载详细研究内容。

## 内容

- `projects.md`：由所有项目的 `project.json` 自动生成；不要手工编辑项目行。
- `reading.md`：跨课题阅读队列，链接到文献笔记或待处理来源。
- `weekly/`：每周计划、复盘和会议准备。
- `yearly/`：年度目标、季度检查和阶段总结。

## 维护节奏

- 每周：清理 inbox，检查活跃项目的下一步和复盘日期，整理阅读队列。
- 每月：检查暂停项目、跨项目依赖和方法复用机会。
- 每季度：复核课题组合，明确继续、暂停、合并或结束的项目。

项目的事实来源始终是 `projects/<slug>/project.json` 和项目 README。更新项目元数据后运行：

```bash
uv run scripts/workspace.py dashboard
```

生成总结报告时可从 dashboard 获取当前组合状态，但报告文件写入 `reports/`。
