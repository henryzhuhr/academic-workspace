# zhang2026agentAuditSecurityAnalysis — Agent Audit: A Security Analysis System for LLM Agent Applications

## Bibliographic record

| Field | Value |
| --- | --- |
| BibTeX key | `zhang2026agentAuditSecurityAnalysis` |
| Authors | Haiyue Zhang; Yi Nian; Yue Zhao |
| Year | 2026 |
| Venue | arXiv preprint |
| DOI / URL | https://arxiv.org/abs/2603.22853v1 |
| Local file | `literature/files/papers/2026/2026-arxiv-zhang-agent-audit-security-analysis-2603.22853v1.pdf` |
| SHA-256 | `9be692858841bc07eb38c75a93828b87e7880bd8042bb7e5fd9fa1a2c7de9ddf` |
| PDF pages | 5 |
| Reading status | `read` |
| Updated | 2026-07-22 |

## One-sentence contribution

提出 Agent Audit——首个面向 LLM Agent 应用的静态安全分析系统，通过 agent-aware 的多扫描器管道（AST 污点分析 + 凭证检测 + MCP 配置解析 + 权限风险检查）检测工具函数、提示构造和部署配置三层攻击面，在 42 个漏洞 benchmark 上达到 95.24% recall（4× 优于 Semgrep），并已开源。

## Research question and context

How should developers audit the security of an LLM agent before deployment? 现有 SAST 工具（Bandit, Semgrep）无法覆盖 agent 特有的攻击面：
- `@tool` 装饰的函数形成执行边界，处理 LLM 生成的可疑输入
- 提示词拼接中的注入风险（f-string, .format(), +=）
- MCP 部署配置中的过度权限、未验证第三方服务器、凭据泄露
- 这些威胁已出现在实际 CVE 中（CVE-2023-29374, CVE-2023-36258）

## Claims and evidence

| Claim | Evidence or method | Location | Confidence / limitation |
| --- | --- | --- | --- |
| Agent Audit 在 AVB 上达 95.24% recall | 42 个标注漏洞中检测出 40 个 | §3.2, Table 2 | 2 个 FN 在 TS/MD 非 Python 样本中； intra-procedural 仅限 |
| 4.0× recall 优势对比 Semgrep | Semgrep 仅 23.8% recall (10/42) | §3.2, Table 2 | Semgrep 100% precision 但因检测极少（10 TP） |
| 30 个漏洞为 Agent Audit 独家检测 | 对比 Semgrep 0 个独家检测 | §3.2 | MCP 配置漏洞（10/42）、凭据（12/42）、agent 特有模式 |
| MCP 配置漏洞覆盖率 100% | 10/10 oracle entries | §3.2 | 纯静态分析，不执行运行时检测 |
| 子秒级扫描 | 22,009 行 / 0.87 秒 (25K lines/sec) | §3.2 | 线性扩展，全测试套件 1.27s |
| 57 条规则覆盖全部 10 个 OWASP ASI 类别 | 规则分布：ASI-04 Supply Chain 最多(10), ASI-02 Tool Misuse(9), ASI-03 Identity/Priv(9) | §2.1, Figure 2 | 4 条额外 cross-cutting 规则 |

## Methods

1. **Multi-scanner pipeline** — 4 个扫描器并行运行：PythonScanner (AST + taint), SecretScanner (regex + semantic), MCPConfigScanner (JSON/YAML 结构化解析), PrivilegeScanner (AST + regex)
2. **Agent-aware 代码分析** — 识别 12 种 `@tool` 装饰器模式（LangChain, CrewAI, 自定义），工具函数内发现 base confidence 0.90 vs 普通函数 0.55；四阶段 taint pipeline（source 分类 → 数据流图 → 消毒检测 → sink 可达性）
3. **Confidence tiering** — BLOCK (≥0.92) / WARN (≥0.60) / INFO (≥0.30) / SUPPRESSED (<0.30)，20+ 假阳抑制机制
4. **Agent-Vuln-Bench (AVB)** — 22 样本 / 42 漏洞，分三组：Injection/RCE (Set A) / MCP (Set B) / Data/Auth (Set C)

## Limitations and contradictions

- **Intra-procedural only** — 不追踪跨函数数据流
- **Python 为主** — TypeScript/JS 仅正则级别扫描
- **不执行运行时** — 不模拟 prompt injection payloads
- **置信度经验校准** — 非形式化模型推导
- **6 个 FP** — precision 86.96%，来自 MCP 配置启发式过检测安全模式

## Reusable insights

- Agent 安全分析需要三层覆盖：代码（tool 函数）→ 提示词（构造路径）→ 配置（MCP 部署）。缺少任何一层都会遗漏关键攻击面。
- `@tool` 边界作为 confidence boosting 信号是个有效设计：工具函数处理 LLM 生成输入，风险天然更高。
- MCP 配置应被视为攻击面而非透明数据——跨服务器 tool shadowing、description poisoning 等供给链攻击是新兴威胁。
- 57 规则映射到 10 个 OWASP ASI 类别的设计模式可复用于其他 agent 安全工具。

## Related projects and topics

- Project IDs: `ai-agent-security`
- Topic reviews: LLM Agent Security, Static Analysis for AI Systems, MCP Security

## Follow-up

- [x] 核实书目信息、核心主张、方法、限制和对应页码
- [ ] 评估 Agent Audit 规则能否直接引入项目 CI 流程
- [ ] 对比其 MCP 配置分析与 MCP Checkpoint (aira-security) 的关系
- [ ] 关注后续是否加入 inter-procedural taint 和学习型检测
