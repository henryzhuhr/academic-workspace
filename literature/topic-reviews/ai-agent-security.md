# AI Agent Security Topic Review

## Scope

本主题综述关注 AI Agent 的安全性，尤其是 LLM-based agents 在规划、工具调用、记忆、权限委托和多步执行过程中产生的新风险。

## Source Policy

- 当前已完成首批核心论文全文首轮精读。
- 本页记录主题脉络、关键论文定位、阅读优先级和综合判断。
- 单篇精读笔记后续放入 `literature/reading-notes/`。

## Reading Clusters

| Cluster | Key Question | Initial Sources |
| --- | --- | --- |
| Agent-specific threat model | Agentic AI 相比普通 LLM app 多了哪些攻击面？ | OWASP Agentic AI Threats and Mitigations, OWASP Top 10 for Agentic Applications |
| Prompt injection and goal hijacking | 不可信数据如何改变 agent 的目标和行动？ | AgentDojo, Prompt Injection attack against LLM-integrated Applications |
| Tool-use safety | 工具调用如何引入高后果风险？ | ToolEmu, AgentDojo, ASB |
| Benchmark and evaluation | 如何系统评估 agent 攻防？ | Agent Security Bench, AgentDojo, ToolEmu |
| Governance and risk management | 组织如何管理 GenAI / Agent 风险？ | NIST AI 600-1, OWASP Agentic AI resources |
| Agent skill / tool supply chain | 技能、工具、插件和配置如何成为供应链风险？ | OWASP Agentic Skills Top 10 |

## Initial Source List

- `owasp2025agenticThreats`: OWASP Agentic AI Threats and Mitigations, 2025. https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/
- `owasp2026agenticTop10`: OWASP Top 10 for Agentic Applications 2026, 2025. https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- `owasp2026agenticSkills`: OWASP Agentic Skills Top 10, 2026. https://owasp.org/www-project-agentic-skills-top-10/
- `nist2024genaiProfile`: NIST AI 600-1 Generative AI Profile, 2024. https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- `debenedetti2024agentdojo`: AgentDojo, 2024. https://arxiv.org/abs/2406.13352
- `zhang2024asb`: Agent Security Bench, 2024. https://arxiv.org/abs/2410.02644
- `ruan2023toolemu`: ToolEmu, 2023. https://arxiv.org/abs/2309.15817
- `liu2023promptInjection`: Prompt Injection attack against LLM-integrated Applications, 2023. https://arxiv.org/abs/2306.05499

## Full-Text Notes Linked

- `literature/reading-notes/2024-arxiv-debenedetti-agentdojo.md`
- `literature/reading-notes/2024-arxiv-zhang-agent-security-bench.md`
- `literature/reading-notes/2023-arxiv-ruan-identifying-the-risks-of-lm-agents-with-an-lm-emulated-sandbox.md`
- `literature/reading-notes/2023-arxiv-liu-prompt-injection-attack-against-llm-integrated-applications.md`

## Current Synthesis

AI Agent 安全问题的关键，不是单点的模型输出失误，而是语言模型输出会被接到工具、记忆、权限和环境之上，最终转化为外部行动。现有核心文献大致可分成三条路线：

1. `Prompt injection / goal hijacking` 路线  
   代表文献是 `liu2023promptInjection`。这条路线解释了为什么 LLM 难以稳定区分“数据”和“指令”，并给后续 agent hijacking 提供了基础攻击语言。

2. `Dynamic benchmark / adversarial environment` 路线  
   代表文献是 `debenedetti2024agentdojo`。这条路线把注入风险放进带工具、带状态、带环境转移的 agent 场景中，强调 utility-security tradeoff 和环境级评测。

3. `Broad agent attack surface / unified benchmark` 路线  
   代表文献是 `zhang2024asb`。这条路线把攻击面扩展到 system prompt、memory retrieval、planning、tool usage 等多个运行阶段，试图给 agent security 建立统一 taxonomy。

此外，`ruan2023toolemu` 所代表的路线并不把安全仅仅理解为“对抗攻击”，而是强调高后果工具执行中的长尾失败发现。这对 agent safety 很关键，因为真实风险常常来自歧义任务、错误假设和过度自主性，而不只是恶意注入。

## Working Comparison

| Work | Best use in this project | Main focus | Main limit |
| --- | --- | --- | --- |
| `liu2023promptInjection` | 解释 prompt injection 基础机制 | 黑盒注入攻击 | 不是完整 agent 场景 |
| `debenedetti2024agentdojo` | 分析 tool-calling agent 的动态注入风险 | 动态环境 benchmark | 主要聚焦 indirect prompt injection |
| `zhang2024asb` | 搭 threat taxonomy 和评测框架 | 多攻击面统一 benchmark | 指标聚合较强，异质攻击被统一比较 |
| `ruan2023toolemu` | 补工具执行与高后果误操作风险 | LM-emulated sandbox | 仿真真实性仍有限 |

## Current Working Claims

- Prompt injection 是 agent 安全的重要入口，但不是全部问题；真正的风险放大器是工具权限、长期记忆、自动化循环和跨系统委托。
- 不能把 agent security 只建模为“攻击成功率”；至少还需要同时看 utility、拒绝策略、误报代价和高后果风险。
- `AgentDojo`、`ASB`、`ToolEmu` 分别对应三种不同研究目标：动态对抗评测、统一安全基准、长尾风险发现。三者互补，不应混为一个问题。
- 现有研究仍缺少一个把 prompt injection、memory poisoning、tool privilege 和 governance control 串起来的端到端框架。

## Next Reading Order

1. OWASP Agentic AI Threats and Mitigations: 把论文中的攻击面映射到工程控制点。
2. OWASP Top 10 for Agentic Applications 2026: 对齐 agentic application 风险语言。
3. NIST AI 600-1: 将技术风险转换为治理和风险管理语汇。
4. 检索 memory poisoning、multi-agent security、MCP/tool supply chain 的 2025-2026 新论文。
