# AI Agent Security Risk Map

## Risk Categories

| Category | Core Question | Representative Sources | Current Notes |
| --- | --- | --- | --- |
| Goal / instruction hijacking | 外部内容如何改变 agent 的目标或指令优先级？ | OWASP Agentic AI, AgentDojo, prompt injection papers | 从单轮 prompt injection 扩展到多步任务劫持。 |
| Tool misuse | Agent 如何被诱导调用错误工具、错误参数或危险动作？ | AgentDojo, ASB, ToolEmu | 关键在工具权限、调用前验证和结果解释。 |
| Over-privileged agents | Agent 是否拥有超过任务所需的文件、网络、shell、API 权限？ | OWASP Agentic AI, OWASP Agentic Skills | Least privilege / least agency 是核心控制原则。 |
| Memory / context poisoning | 攻击者能否污染长期记忆、RAG 语料或历史上下文？ | ASB, OWASP Agentic AI | 需要区分短期上下文、长期记忆和检索索引。 |
| Agentic supply chain | 技能、工具、插件、MCP server、配置文件是否可被投毒？ | OWASP Agentic Skills Top 10 | Skills 和工具描述本身应视为执行层供应链。 |
| Unexpected code execution | Agent 是否能把自然语言任务转化为未审计代码执行？ | OWASP Agentic AI, Agentic Skills | 重点关注 shell、browser automation、CI/CD、IDE agent。 |
| Data leakage | Agent 在读取工具结果或文件时是否泄露凭证、隐私或商业信息？ | NIST AI 600-1, ToolEmu | 需要结合数据分类、输出过滤和审计。 |
| Multi-agent failures | 多代理协作是否引入错误传播、权限扩散和责任不清？ | OWASP Agentic AI | 目前文献仍偏早期，需要重点补充。 |
| Evaluation gap | 现有 benchmark 是否能覆盖真实 agent 场景？ | AgentDojo, ASB, ToolEmu | 评测应同时度量任务成功率和攻击成功率。 |

## Working Taxonomy

AI Agent 安全可按三层组织：

1. 输入层：prompt injection、数据投毒、恶意网页/邮件/文档。
2. 决策层：目标劫持、规划偏移、记忆污染、多代理错误传播。
3. 执行层：工具误用、权限滥用、代码执行、供应链投毒、数据泄露。

## Open Questions

- 如何定义 agent 的“最小权限”和“最小自主性”？
- 现有 prompt injection 防护能否迁移到带工具调用的 agent？
- Agent benchmark 应该如何同时评估 utility、security、cost 和 human oversight？
- 长期记忆是否需要类似数据库安全中的访问控制、完整性校验和审计机制？
- 多代理系统中的责任边界如何定义？
