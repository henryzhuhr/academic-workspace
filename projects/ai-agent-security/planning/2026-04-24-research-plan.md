# AI Agent Security Research Plan

Date: 2026-04-24

## Goal

建立 AI Agent 安全性的第一版研究地图，明确核心风险类型、代表性文献、评测基准和可继续推进的研究问题。

## Scope

- Agent 能力：规划、工具调用、文件/网络/代码执行、记忆、权限委托、多代理协作。
- 风险类型：prompt injection、goal hijacking、tool misuse、over-privilege、memory poisoning、supply chain、unexpected code execution、data leakage、observability gap。
- 产物形态：Markdown 文献综述初稿，后续可导出 PDF/DOCX 或转为论文相关工作。

## Out of Scope

- 本轮不下载论文全文，因为 `literature/files` 软链接尚未配置。
- 本轮不做实验复现，只记录后续可能复现的 benchmark 和代码仓库。
- 本轮不直接给出工程安全方案，只建立学术调研框架。

## Workflow

1. 在 `dashboard/reading.md` 建立第一批阅读队列。
2. 在 `literature/topic-reviews/ai-agent-security.md` 建立主题综述入口。
3. 在 `projects/ai-agent-security/notes/risk-map.md` 维护风险地图。
4. 在 `projects/ai-agent-security/writing/2026-04-24-ai-agent-security-literature-review.md` 产出第一版综述。
5. 后续每精读一篇文献，再补充 `literature/reading-notes/` 中的单篇笔记。

## Acceptance Criteria

- 能用 5-8 个风险类别解释 AI Agent 安全问题的主干。
- 每个风险类别至少关联 1 个权威来源或代表性论文。
- 能明确下一轮精读顺序和待验证问题。
