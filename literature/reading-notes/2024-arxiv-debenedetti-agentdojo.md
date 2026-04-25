# AgentDojo

- File: `literature/files/papers/2024/2024-arXiv-debenedetti-agentdojo.pdf`
- Citation key: `debenedetti2024agentdojo`
- Venue status: NeurIPS 2024 Datasets and Benchmarks Track
- Reading status: full-text first pass
- Related project: `projects/ai-agent-security/`

## Core Question

如何在动态、带工具调用、且包含不可信外部数据的环境中评测 LLM agent 的 prompt injection 攻击与防御？

## Main Contribution

- 提出 `AgentDojo`，一个面向 tool-calling agent 的动态评测环境，而不是静态数据集。
- 给出 97 个现实任务、629 个安全测试用例，覆盖 workspace、Slack、travel、e-banking 等状态化场景。
- 用环境状态上的确定性检查函数评估 utility 和 security，而不是依赖另一个 LLM 充当评审。
- 将攻击、防御和新任务扩展视为 benchmark 的一等对象，强调 benchmark 需要随攻击共同演化。

## Threat Model and Setup

- 攻击入口主要是工具返回的不可信文本数据。
- 攻击目标是诱导 agent 在执行原始任务时额外完成攻击者目标。
- 评测区分三类核心指标：
  - `Benign Utility`
  - `Utility Under Attack`
  - `Targeted Attack Success Rate`

## Key Findings

- 当前模型在 benign 条件下也很难把任务做好；论文摘要报告多数模型在无攻击时都无法稳定解决全部任务。
- 论文首页明确给出：当前模型在无攻击时对该套任务的完成率不到 `66%`。
- 攻击对最强基线 agent 的成功率低于 `25%`，说明攻击并不是“随便一打就中”，但这是建立在 agent 本身 utility 不高的前提下。
- 加入现有 prompt injection defense 后，攻击成功率可降到 `8%` 左右，但 utility 仍明显下降。
- 文中观察到一个重要现象：能力更强的模型往往更容易被 targeted attack 成功，因为它们更有能力完成攻击者要求的恶意动作。

## Why It Matters

- 这篇论文把“agent 安全评测”从单轮 prompt 注入，推进到带状态、带工具、多步执行的环境里。
- 它比单纯的 prompt injection benchmark 更接近真实 agent 工作流。
- 它强调 security evaluation 不能脱离 utility；否则“什么都不做”的 agent 会看起来最安全。

## Limits

- 威胁模型仍以 prompt injection 为中心，对 memory poisoning、backdoor、skill/tool supply chain 还没有系统覆盖。
- 工具过滤等防御在任务可预先规划时有效，但对开放式任务未必成立。
- benchmark 仍是研究者构造的环境，和真实生产系统之间还有部署差距。

## Relevance to AI Agent Security

- 可作为“tool-use + indirect prompt injection”方向的基线论文。
- 适合为本项目的 `tool misuse`、`goal hijacking`、`evaluation gap` 三个子问题提供共同坐标系。
- 后续写 related work 时，可将其定位为“动态环境 benchmark”，与 `ToolEmu` 的“LM 仿真 sandbox”路线和 `ASB` 的“多攻击面统一基准”路线做对照。
