# Prompt Injection attack against LLM-integrated Applications

- File: `literature/files/papers/2023/2023-arXiv-liu-prompt_injection_attack_against_llm_integrated_applications.pdf`
- Citation key: `liu2023promptInjection`
- Venue status: arXiv preprint
- Reading status: full-text first pass
- Related project: `projects/ai-agent-security/`

## Core Question

现实中的黑盒 LLM-integrated applications 是否容易被 prompt injection 利用？如果已有启发式攻击不够稳定，如何系统化构造更强的黑盒注入方法？

## Main Contribution

- 先对真实商业应用中的 prompt injection 可利用性做 pilot study。
- 发现已有启发式攻击在真实应用里并不稳定，因为应用会对 prompt 的拼接方式、输入输出格式和多步工作流做额外约束。
- 基于这一观察提出 `HOUYI`，把 prompt injection 拆成 framework、separator、disruptor 三部分进行生成。
- 在 36 个真实 LLM-integrated applications 上测试，报告 31 个存在可利用性。

## Threat Model and Setup

- 黑盒威胁模型：攻击者不知道应用内部 prompt、系统结构和底层模型。
- 攻击目标是让应用输出偏离预期功能，或者泄露 prompt、滥用底层 LLM 计算资源等。
- 论文关注的对象主要还是 LLM 应用，不是具备复杂工具自治的 agent，但它提供了后续 agent hijacking 的基础攻击语言。

## Key Findings

- 论文报告 `HOUYI` 在 36 个真实应用上的总体攻击成功率为 `86.1%`。
- 作者声称识别出 31 个可被 prompt injection 利用的应用。
- 重要启发不是某个具体 payload，而是：成功攻击依赖于让模型把恶意载荷解释成“应执行的问题/命令”，而不是普通数据。
- 论文还说明，一些常见防御能挡住传统注入，但仍可能被更系统化的 payload generation 绕过。

## Why It Matters

- 这篇论文不是 agent benchmark，但它构成了 agent prompt injection 研究的直接前史。
- 它帮助解释为什么 agent 场景中的“instructions vs data indistinguishability”会成为根本问题。
- 对本项目来说，它适合放在 related work 的起点位置，用来承接 `AgentDojo` 对 indirect prompt injection 的 agent 化扩展。

## Limits

- 研究对象主要是 2023 年前后的应用形态，和当前 agent framework 仍有代际差异。
- 论文重点是黑盒攻击构造，不提供 agent 级别的权限、记忆或工具治理框架。
- 一些成功判定更偏“能否劫持输出”，与真实高后果行动之间还有距离。

## Relevance to AI Agent Security

- 适合作为 prompt injection 基础文献。
- 可用来支撑一个判断：agent 安全中的 goal hijacking 并不是突然出现的新问题，而是 prompt injection 在工具化、自治化系统中的升级版。
