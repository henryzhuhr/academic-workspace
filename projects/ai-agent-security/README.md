# AI Agent Security

- 项目标识：`ai-agent-security`
- 启动日期：`2026-04-24`
- 迁移到 v2：`2026-07-19`
- 机器可读状态：[project.json](project.json)

## Research question

AI Agent 在具备规划、工具调用、记忆、权限委托和多步执行能力之后，会产生哪些不同于普通 LLM 应用的安全风险？这些风险应如何分类、评测和治理？

## Scope

### In scope

- Agent 的规划、工具调用、文件/网络/代码执行、记忆、权限委托和多代理协作。
- Prompt injection、goal hijacking、tool misuse、over-privilege、memory poisoning、供应链、意外代码执行、数据泄露和可观测性缺口。
- 风险分类、代表性文献、评测基准和治理框架。

### Out of scope

- 当前阶段不执行攻击实验或 benchmark 复现。
- 当前阶段不把研究地图直接转换为生产安全控制方案。
- 不在仓库内保存受版权限制的论文全文。

## Background and motivation

AI Agent 的安全问题不只来自模型输出错误，还来自模型可以把输出转化为行动：调用工具、访问文件、执行代码、读写记忆、与其他代理协作或代表用户完成任务。因此，安全边界从“提示词与回答”扩展到目标、权限、工具、环境、记忆、供应链和审计。

## Working assumptions

| Assumption | Why it matters | How to test or challenge it | Status |
| --- | --- | --- | --- |
| 模型输出触发外部行动是 Agent 风险相对普通 LLM 应用的主要放大器 | 决定风险分类是否需要同时覆盖模型与系统权限 | 对照 AgentDojo、Agent Security Bench 和 ToolEmu 的威胁场景 | `supported` |
| Prompt injection 的危害由工具权限、长期记忆和自动化循环进一步放大 | 决定防护重点不能只停留在输入过滤 | 比较不同权限与执行环境下的攻击结果 | `tentative` |
| 现有防护仍缺少统一、场景化的风险度量 | 决定后续是否需要建立跨基准评测维度 | 对齐现有 benchmark 的任务、威胁和成功指标 | `unverified` |

## Evidence map

| Claim or question | Evidence needed | Current source | Confidence | Next check |
| --- | --- | --- | --- | --- |
| Agent 行动能力扩大了安全边界 | 威胁模型与真实任务场景 | [Topic review](../../literature/topic-reviews/ai-agent-security.md) | `medium` | 对齐 OWASP 与 NIST 框架 |
| 现有 benchmark 覆盖范围不同 | 任务、攻击、指标和防御的横向表格 | [AgentDojo](../../literature/reading-notes/2024-arxiv-debenedetti-agentdojo.md)、[Agent Security Bench](../../literature/reading-notes/2024-arxiv-zhang-agent-security-bench.md) | `medium` | 补充统一 taxonomy |
| 工具模拟可以发现长尾风险 | ToolEmu 的方法与局限 | [ToolEmu note](../../literature/reading-notes/2023-arxiv-ruan-identifying-the-risks-of-lm-agents-with-an-lm-emulated-sandbox.md) | `medium` | 检查与其他 benchmark 的互补性 |

## Current understanding

### Relatively stable

- Agent 安全需要把 LLM 安全、应用安全、权限治理和运行时监控放在同一威胁模型中考察。
- Prompt injection 是重要入口风险，但实际影响受工具权限、执行环境和代理自治程度共同决定。

### Tentative

- 现有治理框架与学术 benchmark 之间可能缺少可直接映射的共同评测维度。
- 风险分类应同时表达攻击入口、被滥用能力、影响对象和控制阶段。

### Contradictions and unknowns

- 不同 benchmark 的攻击成功定义能否统一比较仍待验证。
- OWASP Agentic AI 与 NIST AI 600-1 对风险边界的重合和差异仍需系统整理。
- 多代理协作、长期记忆和技能供应链的公开实证材料仍不充分。

## Milestones

| Milestone | Exit criterion | Target | Status |
| --- | --- | --- | --- |
| Initial research map | 风险类别、代表文献和后续问题形成首版 | 2026-04-25 | `completed` |
| Framework alignment | OWASP、NIST 与学术 benchmark 建立映射 | _TBD_ | `active` |
| Review refresh | 更新 2026-04 综述并明确可验证研究缺口 | _TBD_ | `planned` |

## Next actions

1. 复核并更新现有主题综述的来源与结论。
2. 对齐 OWASP Agentic AI、NIST AI 600-1 与现有 benchmark 的分类维度。
3. 将 AgentDojo、Agent Security Bench 和 ToolEmu 整理为统一的攻击面与评测表。

## Research links

- Research plan: [planning/2026-04-24-research-plan.md](planning/2026-04-24-research-plan.md)
- Decisions: [planning/decision-log.md](planning/decision-log.md)
- Risk map: [notes/risk-map.md](notes/risk-map.md)
- Topic review: [../../literature/topic-reviews/ai-agent-security.md](../../literature/topic-reviews/ai-agent-security.md)
- Literature review draft: [writing/2026-04-24-ai-agent-security-literature-review.md](writing/2026-04-24-ai-agent-security-literature-review.md)
- Analysis and reproducibility: [analysis/README.md](analysis/README.md)
- Outputs: [outputs/README.md](outputs/README.md)

## Ethics, privacy, and constraints

- 当前材料以公开文献和公开框架为主，不包含实验参与者或生产系统敏感数据。
- 风险与攻击描述用于学术分析；转化为实验时必须先定义安全环境、授权范围和停止条件。
- 文献事实、页码和框架内容在引用前必须回到原始来源核验。
