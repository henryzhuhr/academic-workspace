# AI Agent Security

## Research Question

AI Agent 在具备规划、工具调用、记忆、权限委托和多步执行能力之后，会产生哪些不同于普通 LLM 应用的安全风险？这些风险应如何分类、评测和治理？

## Status

`active`

## Motivation

AI Agent 的安全问题不只来自模型输出错误，而来自模型可以把输出转化为行动：调用工具、访问文件、执行代码、读写记忆、与其他代理协作或代表用户完成任务。因此，安全边界从“提示词与回答”扩展到“目标、权限、工具、环境、记忆、供应链和审计”。

## Core Materials

- OWASP Agentic AI threats and mitigations.
- OWASP Top 10 for Agentic Applications 2026.
- OWASP Agentic Skills Top 10.
- NIST AI 600-1 Generative AI Profile.
- AgentDojo, Agent Security Bench, ToolEmu, prompt injection 等论文与基准。

## Current Working Claims

- Agent 安全的核心问题是“模型输出可以触发外部行动”，因此需要把 LLM 安全、应用安全、权限治理和运行时监控放在一起看。
- Prompt injection 仍是入口风险，但 agentic system 的放大器是工具权限、长期记忆、自动化循环和跨系统委托。
- 现有防护大多是局部措施，仍缺少统一的风险度量、场景化基准和可操作治理流程。

## Next Steps

1. 精读 AgentDojo、Agent Security Bench、ToolEmu，整理攻击面和评测维度。
2. 对齐 OWASP Agentic AI 与 NIST AI 600-1 的风险分类。
3. 扩展 `literature/topic-reviews/ai-agent-security.md`，形成可复用的相关工作地图。
4. 迭代 `reports/2026-04-24-ai-agent-security-literature-review.md`，逐步转为正式文献综述。

## Related Paths

- Topic review: `literature/topic-reviews/ai-agent-security.md`
- Reading queue: `dashboard/reading.md`
- Research plan: `projects/ai-agent-security/planning/2026-04-24-research-plan.md`
- Risk map: `projects/ai-agent-security/notes/risk-map.md`
- Report draft: `reports/2026-04-24-ai-agent-security-literature-review.md`
