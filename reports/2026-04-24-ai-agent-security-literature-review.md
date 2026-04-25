# AI Agent 安全性文献综述

Date: 2026-04-24
Project: `ai-agent-security`
Format: Markdown draft

## 信息来源

本报告读取了以下仓库文件：

- `AGENTS.md`
- `literature/README.md`
- `projects/README.md`
- `reports/README.md`
- `projects/ai-agent-security/README.md`
- `projects/ai-agent-security/notes/risk-map.md`
- `literature/topic-reviews/ai-agent-security.md`

本报告引用了以下外部来源：

- OWASP Agentic AI Threats and Mitigations: https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/
- OWASP Top 10 for Agentic Applications for 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- OWASP Agentic Skills Top 10: https://owasp.org/www-project-agentic-skills-top-10/
- NIST AI 600-1 Generative AI Profile: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- AgentDojo: https://arxiv.org/abs/2406.13352
- Agent Security Bench: https://arxiv.org/abs/2410.02644
- ToolEmu: https://arxiv.org/abs/2309.15817
- Prompt Injection attack against LLM-integrated Applications: https://arxiv.org/abs/2306.05499

本报告已完成对 4 篇核心论文的全文首轮精读，并结合 OWASP / NIST 文档做结构化综述。

## 1. 研究问题与综述范围

本文关注的问题是：当大型语言模型被包装成具备规划、工具调用、记忆、权限委托和多步执行能力的 agent 之后，安全问题究竟发生了什么变化？这一问题至少包含四个子问题：

1. 风险边界如何从“文本生成错误”扩展为“高后果行动错误”。
2. 现有研究如何刻画 agent 的主要攻击面。
3. benchmark 如何同时衡量 utility 与 security。
4. 现有工作在哪些方面仍不足以支撑真实 agent 系统的安全治理。

AI Agent 与普通 LLM 应用的关键差别在于：模型输出不再停留在文本层，而可能进一步触发网页操作、API 调用、代码执行、文件改写、记忆写入和跨系统委托。因此，agent 安全的核心问题不是“模型会不会答错”，而是“错误、恶意或被污染的模型决策是否会变成真实行动”。这一变化使风险边界从 prompt/response 对扩展到目标、权限、工具、环境、记忆、供应链与审计。

本文当前的核心文献包括四篇：`AgentDojo`、`ASB`、`ToolEmu` 和 `Prompt Injection attack against LLM-integrated Applications`。其中最后一篇严格来说还不是完整的 agent 论文，但它提供了理解后续 goal hijacking 的基础攻击视角。

## 2. 文献脉络：从 prompt injection 到 agent security

### 2.1 Prompt Injection 是前史，不是全部问题

`Liu et al. (2023)` 研究的是黑盒 `LLM-integrated applications` 的 prompt injection。它的重要性不在于给出了某个永远有效的 payload，而在于指出：应用是否可被注入，取决于模型如何把输入解释为“数据”还是“应执行的请求”。作者通过 pilot study 先证明，早期启发式攻击在真实系统里并不总有效，随后提出 `HOUYI`，将 payload 拆成 framework、separator 和 disruptor 三个部分，在 36 个真实应用上报告了 31 个可利用目标和 `86.1%` 的总体成功率。

对 AI Agent 安全研究来说，这篇论文的价值是奠定了一个根本判断：`instructions vs data indistinguishability` 不是 agent 独有问题，而是 LLM 系统的基础脆弱性。agent 场景的变化在于，一旦注入成功，被劫持的不再只是回答内容，而是后续的计划、工具选择和真实执行路径。

### 2.2 AgentDojo：把注入风险放进动态工具环境

`Debenedetti et al. (2024)` 的 `AgentDojo` 将 prompt injection 风险推进到更贴近 agent 的设置中。与仅评测单轮输入输出的工作不同，AgentDojo 构造了带状态、带工具、带环境转移的动态 benchmark，并明确要求同时评估用户任务完成度和攻击者目标达成度。论文构造了 `97` 个现实任务、`629` 个安全测试用例，并用环境状态上的确定性检查函数来衡量：

- benign utility
- utility under attack
- targeted attack success rate

这一步很关键，因为 agent security 不能只看攻击是否成功。如果一个模型什么都做不好，它当然也不容易完成攻击者目标。AgentDojo 的一个重要观察正来自这里：在该 benchmark 上，多数模型在无攻击条件下完成率也不足 `66%`；同时，对最强模型的 targeted attack success rate 也低于 `25%`。这意味着低攻击成功率并不必然意味着安全，也可能意味着 agent 本身 utility 很差。

AgentDojo 还表明，一些防御能把攻击成功率进一步压低到 `8%` 左右，但通常需要付出明显 utility 代价。对本项目而言，这篇论文最重要的启发是：`agent security evaluation 必须内生地处理 utility-security tradeoff`，否则结论很容易失真。

### 2.3 ToolEmu：安全不只等于“对抗攻击”

`Ruan et al. (2023/2024)` 的 `ToolEmu` 提供了另一条路线。它关注的不是 prompt injection，而是高后果工具执行中的失败发现问题。论文的核心威胁模型是：用户指令存在歧义或遗漏关键约束，agent 却在高风险工具上过度自主地补全、推断并执行，从而造成财务、隐私、物理或系统后果。

为了解决真实沙箱难以大规模搭建的问题，ToolEmu 用 LM 来模拟工具执行和环境状态，并配套自动 safety/helpfulness evaluator。其核心贡献不是证明 LM 仿真完全等价于真实环境，而是证明这种方法足够便宜，且在风险发现上足够有用。论文报告：

- 被 ToolEmu 识别出的失败中，约 `68.8%` 经人工验证为真实且有风险的失败；
- 最安全的 GPT-4 Safety agent 仍在 `23.9%` 的测试用例中失败；
- terminal 场景中，作者人工复现实验表明多数严重失败可以在真实 bash 中复现。

这篇论文对 agent security 研究的真正贡献，是把问题从“恶意攻击者能否攻破系统”扩展到“正常任务下 agent 是否会以危险方式误执行”。如果只盯着 prompt injection，就会漏掉这部分真实风险。

### 2.4 ASB：把多攻击面放进统一基准

`Zhang et al. (2024/2025)` 的 `Agent Security Bench (ASB)` 试图把 agent security 统一成跨运行阶段的 benchmark。论文将 agent 流程分成 system prompt、user prompt、memory retrieval、planning 和 tool usage 等环节，并在此基础上纳入五类攻击：

- Direct Prompt Injection
- Indirect Prompt Injection
- Memory Poisoning
- Plan-of-Thought Backdoor
- Mixed Attacks

ASB 覆盖 10 个场景、10 个 agents、400+ tools、27 类 attack/defense 方法和 7 个指标。它的重要性在于：相比只研究 indirect prompt injection 的工作，它把 memory、system prompt 和 planning 也纳入攻击面，试图形成一个更完整的 taxonomy。

结果上，ASB 报告 `Mixed Attack` 平均 ASR 达到 `84.30%`，而 `Memory Poisoning` 的平均 ASR 仅 `7.92%`。这至少说明两件事：第一，不同攻击类型的强度与成熟度差异很大；第二，把它们都放到“agent security”名下是合理的，但不能轻率地把单一数字当作统一结论。论文提出的 `NRP = PNA x (1 - ASR)` 则是一个值得保留的思路：选 agent backbone 时，不能只看 leaderboard 能力，也不能只看攻击成功率，而要看综合韧性。

## 3. 风险分类：当前可用的分析框架

结合这四篇论文和 OWASP / NIST 文档，当前较稳妥的分类方式至少应包含以下六类。

### 3.1 Goal Hijacking / Instruction Override

攻击者通过网页、邮件、文档、工具返回值或上下文内容插入新的指令，改变 agent 的优先级、目标排序或执行顺序。这是从 prompt injection 到 agent hijacking 的直接延伸。`Liu et al.` 提供了基础攻击语言，`AgentDojo` 则把它放进真实工具环境中验证后果。

### 3.2 Tool Misuse and Unsafe Execution

即便没有显式恶意输入，agent 也可能错误选择工具、填错参数、对模糊指令做危险假设，或者把低置信度推断直接转化为高后果动作。`ToolEmu` 说明，这类风险在高风险工具场景中并不少见，且不能简单归结为 prompt injection。

### 3.3 Over-Privilege and Action Amplification

同一段错误 reasoning，在普通聊天系统里可能只是一个错误答案，在拥有支付、发信、执行代码、操作浏览器权限的 agent 中却会被放大成真实损害。OWASP 的很多风险条目实质上都与这种“权限放大器”有关。

### 3.4 Memory and Context Poisoning

长期记忆、RAG 数据库、历史任务计划和偏好记录都可能在跨任务尺度上污染 agent 的后续行为。ASB 已经把 memory poisoning 明确纳入 benchmark，但该方向的现实攻击和防御研究仍明显不够成熟。

### 3.5 Hidden Planning and System-Level Manipulation

ASB 的 PoT backdoor 提醒我们：agent 安全不仅关乎外部输入，还关乎内部 planning scaffold、system prompt 和隐藏执行逻辑。随着 agent framework 越来越复杂，这类风险的重要性会上升。

### 3.6 Evaluation and Governance Gap

真实系统中，最难的问题常常不是“有没有一个攻击样本能打中”，而是“组织能否系统性地知道哪里会出问题、什么时候必须人工确认、怎么记录和追责”。这就是为什么 OWASP 和 NIST 文档仍然重要：它们补足了 benchmark 论文很少处理的治理层语言。

## 4. 评测方法比较：三类研究目标，不应混为一谈

当前文献至少对应三种不同的评测目标。

### 4.1 动态对抗评测

以 `AgentDojo` 为代表。目标是评估在不可信工具数据和真实任务压力下，agent 是否既完成用户目标又抵抗攻击者目标。

### 4.2 统一多攻击面基准

以 `ASB` 为代表。目标是用单一框架对 system prompt、memory、tool、planning 等多个阶段的攻防进行统一整理和比较。

### 4.3 长尾风险发现

以 `ToolEmu` 为代表。目标不是证明某类攻击更强，而是尽可能低成本地发现“真实部署时会出事的失败模式”。

这三种目标互相重叠，但并不等价。后续写 survey 时，应避免把它们都笼统称为“benchmark 工作”，否则会掩盖不同方法真正回答的问题。

## 5. 当前研究空白

- Agent 安全缺少统一的“权限-行动-风险”度量框架。
- 许多防护仍集中在 prompt 层，而对工具权限、记忆、系统 scaffold 和 skill/tool supply chain 处理不足。
- benchmark 经常只评估攻击成功率，却缺少对误拒、确认疲劳、审计可用性和恢复机制的系统度量。
- memory poisoning、多 agent 协作安全、MCP/tool supply chain 等方向仍明显欠缺成熟 benchmark。
- 现有工作虽强调 human-in-the-loop，但极少回答“哪些动作必须确认、确认粒度是什么、确认成本如何优化”。

## 6. 结论

当前文献已经足以支持一个明确判断：AI Agent 安全不是简单的“LLM 安全 + 插件安全”。它是一个由 prompt/data 边界模糊、工具执行、高权限放大、记忆污染、系统隐藏逻辑和治理缺口共同构成的复合问题。`Prompt Injection` 解释了起点，`AgentDojo` 解释了动态工具环境中的注入后果，`ToolEmu` 解释了高后果误执行与长尾风险，`ASB` 则尝试把多攻击面统一进一个 benchmark 视角。

如果要继续推进本项目，更有价值的方向不是再多收集几篇相似 benchmark，而是补上三块：`memory poisoning`、`multi-agent / MCP tool chain` 和 `governance / approval design`。这三块决定了这份综述能否从“已有论文总结”真正升级成可用于后续研究设计的 related work 基础。

## 7. 下一步阅读计划

1. 精读 OWASP Agentic AI 与 Agentic Skills，把风险项映射到本文六类风险框架。
2. 阅读 NIST AI 600-1，把技术风险翻译成治理和组织控制语言。
3. 检索 2025-2026 年的 memory poisoning、multi-agent security、MCP/tool supply chain 论文。
4. 形成正式 related work 结构，准备从 Markdown 综述转为论文式 survey 草稿。

## 8. 当前待验证事项

- OWASP Top 10 for Agentic Applications 的最终条目和发布时间需要在后续阅读中逐项核对。
- `ASB` 的 BibTeX 作者与会议信息需要再校对一次。
- 是否存在 2025-2026 年更新的 agent memory poisoning、多代理安全和 MCP / tool supply chain 专项论文，需要进一步检索。

## 9. 工作流状态

- Project: `projects/ai-agent-security/`
- Topic review: `literature/topic-reviews/ai-agent-security.md`
- Reading notes:
  - `literature/reading-notes/2024-arxiv-debenedetti-agentdojo.md`
  - `literature/reading-notes/2024-arxiv-zhang-agent-security-bench.md`
  - `literature/reading-notes/2023-arxiv-ruan-identifying-the-risks-of-lm-agents-with-an-lm-emulated-sandbox.md`
  - `literature/reading-notes/2023-arxiv-liu-prompt-injection-attack-against-llm-integrated-applications.md`
- Reading queue: `dashboard/reading.md`
- BibTeX: `literature/bibliography.bib`
- Report draft: `reports/2026-04-24-ai-agent-security-literature-review.md`
- Local literature files: available through `literature/files`
