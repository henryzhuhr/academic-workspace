# ToolEmu

- File: `literature/files/papers/2023/2023-arXiv-ruan-identifying_the_risks_of_lm_agents_with_an_lm_emulated_sandbox.pdf`
- Citation key: `ruan2023toolemu`
- Venue status: ICLR 2024 conference paper
- Reading status: full-text first pass
- Related project: `projects/ai-agent-security/`

## Core Question

在真实工具和真实沙箱难以大规模搭建的情况下，能否用 LM 模拟工具执行环境，从而更快发现 LM agent 的高风险失败模式？

## Main Contribution

- 提出 `ToolEmu`，用 LM 模拟工具执行与环境状态，而不是为每种工具单独实现真实 sandbox。
- 同时设计了自动 safety evaluator 与 helpfulness evaluator，用于大规模风险评估。
- 构造了 36 个高风险工具包、144 个测试用例、9 类风险类型的基准。
- 引入 adversarial emulator，用于自动生成更容易诱发失败的场景。

## Threat Model and Setup

- 核心威胁模型不是 prompt injection，而是“用户指令存在歧义或遗漏关键约束，agent 在高风险工具上擅自执行”。
- 关注的失败模式包括误解指令、擅自补全缺失信息、错误执行、忽略风险后果等。
- 通过仿真环境降低测试成本，强调 long-tail risk discovery。

## Key Findings

- 论文报告：通过 ToolEmu 识别出的失败中，约 `68.8%` 被人工验证为真实且有风险的失败。
- 最安全的 GPT-4 Safety agent 仍在 `23.9%` 的测试用例中出现失败。
- 仿真环境在不少情况下足够接近真实环境；作者对 terminal 场景的复现实验显示，多数严重失败可以在真实 bash 中复现。
- adversarial emulator 能发现更多 true failures，但会略微牺牲仿真精度。

## Why It Matters

- 这篇论文提醒我们，agent 安全不只来自“恶意输入”，还来自正常任务中的高后果误执行。
- 它把 agent safety 直接连到风险发现流程，而不是只连到攻击 benchmark。
- 对工程侧很重要的一点是：低成本模拟环境也许足够支持红队和回归测试，而不必每次都接真实工具链。

## Limits

- LM 模拟环境本身可能带来误差，尤其在复杂工具语义和物理世界后果上。
- 其 threat model 更像 high-stakes misuse / underspecification，不完全等同于 adversarial compromise。
- 自动 evaluator 与人工判断仍存在偏差，论文也承认 agreement 只是接近人类标注的一般水平。

## Relevance to AI Agent Security

- `ToolEmu` 为“高后果工具执行风险”提供了一个独立于 prompt injection 的研究入口。
- 它补足了 `AgentDojo` 和 `ASB` 偏攻击者中心的视角，强调了 capability failure 和 safety failure 的交叠地带。
- 本项目后续可以把它放在 “tool misuse / unsafe autonomy / evaluation methodology” 小节中讨论。
