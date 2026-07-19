# Agent Security Bench (ASB)

- File: `literature/files/papers/2024/2024-arXiv-zhang-agent_security_bench.pdf`
- Citation key: `zhang2024asb`
- Venue status: ICLR 2025 conference paper
- Reading status: full-text first pass
- Related project: `projects/ai-agent-security/`

## Core Question

能否用统一框架同时形式化和评测 LLM-based agent 在 system prompt、user prompt、memory retrieval、tool usage 等多个运行阶段上的攻击与防御？

## Main Contribution

- 提出 `ASB`，试图把 agent 安全问题从单一的 indirect prompt injection 扩展为多阶段攻击面框架。
- 覆盖 10 个场景、10 个 agent、400+ tools、27 类攻击/防御方法和 7 个评测指标。
- 明确纳入五类攻击：
  - Direct Prompt Injection
  - Indirect Prompt Injection
  - Memory Poisoning
  - Plan-of-Thought Backdoor
  - Mixed Attacks
- 提出 `NRP` 指标，试图同时考虑正常任务性能和攻击下韧性。

## Threat Model and Setup

- 论文把 agent 运行过程分解成 system prompt、user instruction、memory retrieval、planning、tool execution 五个环节。
- 不同攻击类型分别映射到这些环节上的可利用点。
- 评测指标除了攻击成功率，还包括 refusal rate、PNA、BP、FPR/FNR 和 `NRP = PNA x (1 - ASR)`。

## Key Findings

- 平均来看，`Mixed Attack` 最强，平均 ASR 达到 `84.30%`。
- `Memory Poisoning` 的平均 ASR 最低，为 `7.92%`，说明该方向目前 benchmark 下更难稳定触发，或者现有实现较弱。
- GPT-4o 在文中对多类攻击表现出较高脆弱性，其中 PoT backdoor 条件下的 ASR 被报告为 `100%`。
- 作者强调 agent backbone 的通用能力与 agent security 并不是单调正相关：能力更强的模型有时更容易执行攻击目标，但 refusal 机制又会把 ASR 拉下来。

## Why It Matters

- `ASB` 的价值不在于单一数字，而在于把 agent 安全问题组织成一个跨运行阶段的 taxonomy。
- 对本项目来说，这篇论文最有用的地方是它把“攻击面”从 prompt 输入扩展到 memory、planning、tool 和 hidden system behavior。
- `NRP` 提供了一个有启发性的思路：科研和工程都不该只优化 utility 或只优化 safety。

## Limits

- 论文把很多异质攻击统一进同一个 benchmark，但不同攻击的现实性和可复现性并不完全等价。
- `NRP` 简洁，但仍是乘积式聚合指标，会掩盖不同风险类型之间的差异。
- 某些 attack/defense 结果对具体 agent 框架、prompt 设计和 refusal 策略较敏感。

## Relevance to AI Agent Security

- 适合作为本项目 threat taxonomy 的骨架文献。
- 在 related work 中，可将其定位为“统一多攻击面 benchmark”，区别于 `AgentDojo` 的动态注入环境和 `ToolEmu` 的风险发现框架。
- 后续如果要设计自己的 agent 安全评测方案，`ASB` 是最直接的参照系之一。
