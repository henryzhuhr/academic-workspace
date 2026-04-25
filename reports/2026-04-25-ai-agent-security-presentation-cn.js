const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "OpenAI Codex";
pptx.company = "academic-workspace";
pptx.subject = "AI Agent 安全性调研";
pptx.title = "AI Agent 安全性调研";
pptx.lang = "zh-CN";
pptx.theme = {
  headFontFace: "PingFang SC",
  bodyFontFace: "PingFang SC",
  lang: "zh-CN"
};

const C = {
  ink: "102A43",
  navy: "12355B",
  blue: "2D6A8D",
  teal: "0E7490",
  mint: "CFE8EF",
  cream: "F7F4EA",
  sand: "E7E3D4",
  red: "A63D40",
  gold: "C48A3A",
  white: "FFFFFF",
  slate: "5B7083",
  pale: "EEF4F7",
  line: "D8E2E8"
};

function addTitle(slide, title, subtitle) {
  slide.addText(title, {
    x: 0.6, y: 0.35, w: 8.8, h: 0.55,
    fontFace: "PingFang SC", fontSize: 28, bold: true, color: C.ink, margin: 0
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.6, y: 0.92, w: 8.8, h: 0.3,
      fontFace: "PingFang SC", fontSize: 11, color: C.slate, margin: 0
    });
  }
}

function addFooter(slide, page, label) {
  slide.addShape(pptx.ShapeType.line, {
    x: 0.6, y: 7.0, w: 12.0, h: 0,
    line: { color: C.line, width: 1 }
  });
  slide.addText(label, {
    x: 0.62, y: 7.07, w: 4.0, h: 0.18,
    fontSize: 9, color: C.slate, margin: 0
  });
  slide.addText(String(page).padStart(2, "0"), {
    x: 12.15, y: 7.04, w: 0.45, h: 0.2,
    fontSize: 10, bold: true, color: C.ink, align: "right", margin: 0
  });
}

function addCard(slide, x, y, w, h, fill, line = C.line) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.06,
    fill: { color: fill },
    line: { color: line, width: 1 }
  });
}

// Slide 1
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  s.addShape(pptx.ShapeType.rect, {
    x: 8.6, y: 0, w: 4.7, h: 7.5,
    fill: { color: "0F2743" },
    line: { color: "0F2743", width: 0 }
  });
  s.addShape(pptx.ShapeType.rect, {
    x: 8.95, y: 0.65, w: 3.95, h: 1.25,
    fill: { color: C.red, transparency: 8 },
    line: { color: C.red, width: 0 }
  });
  s.addText("AI Agent 安全性调研", {
    x: 0.7, y: 1.1, w: 6.7, h: 0.9,
    fontFace: "PingFang SC", fontSize: 28, bold: true, color: C.white, margin: 0
  });
  s.addText("从 Prompt Injection 到工具执行、记忆污染与统一评测", {
    x: 0.7, y: 2.0, w: 6.8, h: 0.48,
    fontFace: "PingFang SC", fontSize: 16, color: "DCE7F1", margin: 0
  });
  s.addText("基于 4 篇核心论文全文首轮精读 + OWASP / NIST 治理框架整理", {
    x: 0.7, y: 2.55, w: 6.8, h: 0.34,
    fontFace: "PingFang SC", fontSize: 11, color: "B8C9D9", margin: 0
  });
  addCard(s, 0.75, 4.15, 2.15, 1.1, "20456E", "2D6A8D");
  addCard(s, 3.05, 4.15, 2.15, 1.1, "20456E", "2D6A8D");
  addCard(s, 5.35, 4.15, 2.15, 1.1, "20456E", "2D6A8D");
  s.addText("4\n核心论文", {
    x: 1.05, y: 4.35, w: 1.55, h: 0.62, fontSize: 22, bold: true,
    color: C.white, align: "center", valign: "mid", breakLine: true, margin: 0
  });
  s.addText("6\n风险类别", {
    x: 3.35, y: 4.35, w: 1.55, h: 0.62, fontSize: 22, bold: true,
    color: C.white, align: "center", valign: "mid", breakLine: true, margin: 0
  });
  s.addText("3\n类评测目标", {
    x: 5.6, y: 4.35, w: 1.7, h: 0.62, fontSize: 22, bold: true,
    color: C.white, align: "center", valign: "mid", breakLine: true, margin: 0
  });
  s.addText("研究工作流输出", {
    x: 9.25, y: 0.95, w: 2.9, h: 0.25, fontSize: 12, color: C.white, bold: true, margin: 0
  });
  const outputs = [
    "IEEE 英文论文版 PDF",
    "中文汇报 PPTX",
    "单篇论文阅读笔记",
    "主题综述与后续选题入口"
  ];
  outputs.forEach((t, i) => {
    addCard(s, 9.25, 1.45 + i * 1.02, 3.0, 0.72, "17314F", "2B5278");
    s.addText(t, {
      x: 9.5, y: 1.66 + i * 1.02, w: 2.45, h: 0.18,
      fontSize: 12, color: "E5EEF5", margin: 0
    });
  });
  s.addText("academic-workspace / ai-agent-security", {
    x: 0.75, y: 6.7, w: 4.2, h: 0.2,
    fontSize: 10, color: "B8C9D9", margin: 0
  });
}

// Slide 2
{
  const s = pptx.addSlide();
  s.background = { color: C.cream };
  addTitle(s, "为什么 Agent 安全问题比普通 LLM 安全更难", "核心变化不在“会不会答错”，而在“会不会把错误变成外部行动”");
  const left = [
    "输出会触发工具、代码、浏览器、文件和跨系统操作",
    "错误 reasoning 会被权限放大为真实损害",
    "长期记忆和工作流状态会把风险跨任务传播",
    "隐藏 system prompt、planning scaffold 与 tool schema 也成为攻击面"
  ];
  addCard(s, 0.7, 1.5, 5.6, 4.75, "FFFDFC", "DCCFB8");
  s.addText("结构性变化", {
    x: 0.95, y: 1.78, w: 2.0, h: 0.22, fontSize: 15, bold: true, color: C.ink, margin: 0
  });
  left.forEach((t, i) => {
    s.addShape(pptx.ShapeType.ellipse, {
      x: 0.98, y: 2.18 + i * 0.82, w: 0.22, h: 0.22,
      fill: { color: i % 2 === 0 ? C.red : C.gold }, line: { color: "FFFFFF", width: 0.8 }
    });
    s.addText(t, {
      x: 1.35, y: 2.14 + i * 0.82, w: 4.55, h: 0.36,
      fontSize: 13, color: C.ink, margin: 0
    });
  });
  addCard(s, 6.55, 1.5, 6.0, 4.75, "F8FBFD", "D8E2E8");
  s.addText("论文中的高信号数字", {
    x: 6.82, y: 1.78, w: 2.6, h: 0.22, fontSize: 15, bold: true, color: C.ink, margin: 0
  });
  const stats = [
    ["86.1%", "HOUYI 在 36 个真实应用上的总体攻击成功率"],
    ["23.9%", "ToolEmu 中最安全 GPT-4 Safety agent 的失败比例"],
    ["84.30%", "ASB 中 Mixed Attack 的平均 ASR"],
    ["97 / 629", "AgentDojo 的现实任务数 / 安全测试数"]
  ];
  stats.forEach((it, i) => {
    const y = 2.15 + i * 0.82;
    s.addText(it[0], {
      x: 6.9, y, w: 1.45, h: 0.3, fontSize: 22, bold: true,
      color: i < 2 ? C.red : C.blue, margin: 0
    });
    s.addText(it[1], {
      x: 8.1, y: y + 0.04, w: 4.15, h: 0.28, fontSize: 12,
      color: C.ink, margin: 0
    });
  });
  addFooter(s, 2, "问题定义");
}

// Slide 3
{
  const s = pptx.addSlide();
  s.background = { color: C.white };
  addTitle(s, "核心文献地图", "这 4 篇论文不是同一个问题的重复版本，而是三类不同研究目标");
  const xs = [0.7, 3.95, 7.2, 10.45];
  const titles = ["Prompt Injection", "ToolEmu", "AgentDojo", "ASB"];
  const subtitles = [
    "黑盒应用注入",
    "长尾风险发现",
    "动态对抗环境",
    "统一多攻击面基准"
  ];
  const descs = [
    "解释 instructions / data 边界为什么会失效，是后续 agent hijacking 的前史。",
    "关注高后果工具误执行，不要求必须存在攻击者。",
    "在状态化工具环境里同时评估 utility 与 targeted attack。",
    "把 system prompt、memory、planning、tool 等阶段统一进 benchmark。"
  ];
  xs.forEach((x, i) => {
    addCard(s, x, 1.65, 2.65, 4.7, i === 0 ? "FDF4F4" : i === 1 ? "F4FBFC" : i === 2 ? "F4F7FB" : "F7F4FC", "D8E2E8");
    s.addText(titles[i], {
      x: x + 0.18, y: 1.95, w: 2.1, h: 0.24, fontSize: 16, bold: true, color: C.ink, margin: 0
    });
    s.addText(subtitles[i], {
      x: x + 0.18, y: 2.25, w: 1.8, h: 0.18, fontSize: 10, color: C.slate, margin: 0
    });
    s.addText(descs[i], {
      x: x + 0.18, y: 2.75, w: 2.22, h: 1.1, fontSize: 11.5, color: C.ink, margin: 0
    });
    s.addShape(pptx.ShapeType.rect, {
      x: x + 0.18, y: 4.35, w: 2.1, h: 0.05,
      fill: { color: i === 0 ? C.red : i === 1 ? C.teal : i === 2 ? C.blue : "6D4C9C" },
      line: { color: i === 0 ? C.red : i === 1 ? C.teal : i === 2 ? C.blue : "6D4C9C", width: 0 }
    });
    s.addText(i === 0 ? "回答：如何注入" : i === 1 ? "回答：如何发现危险失败" : i === 2 ? "回答：如何在动态环境测攻防" : "回答：如何统一 attack surface", {
      x: x + 0.18, y: 4.55, w: 2.2, h: 0.45, fontSize: 10.5, color: C.ink, margin: 0
    });
  });
  addFooter(s, 3, "文献脉络");
}

// Slide 4
{
  const s = pptx.addSlide();
  s.background = { color: C.pale };
  addTitle(s, "当前可用的 6 类风险框架", "建议把技术风险和治理风险放在同一张图里，而不是只盯 Prompt Injection");
  const items = [
    ["1", "Goal Hijacking", "恶意内容改变目标、优先级与执行顺序。"],
    ["2", "Tool Misuse", "错误工具、错误参数、危险假设与过度自主执行。"],
    ["3", "Privilege Amplification", "同样的推理错误在高权限环境中被放大。"],
    ["4", "Memory Poisoning", "长期记忆、RAG 与历史计划污染后续任务。"],
    ["5", "Hidden Planning", "system prompt、planning scaffold 与 PoT backdoor。"],
    ["6", "Governance Gap", "审批、审计、回滚、追责与恢复机制不足。"]
  ];
  items.forEach((it, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.7 + col * 6.15;
    const y = 1.55 + row * 1.62;
    addCard(s, x, y, 5.75, 1.25, C.white, "D8E2E8");
    s.addText(it[0], {
      x: x + 0.22, y: y + 0.2, w: 0.55, h: 0.34, fontSize: 22,
      bold: true, color: i < 2 ? C.red : i < 4 ? C.blue : C.teal, margin: 0
    });
    s.addText(it[1], {
      x: x + 0.88, y: y + 0.17, w: 2.9, h: 0.24, fontSize: 14, bold: true, color: C.ink, margin: 0
    });
    s.addText(it[2], {
      x: x + 0.88, y: y + 0.5, w: 4.45, h: 0.38, fontSize: 11.5, color: C.slate, margin: 0
    });
  });
  addFooter(s, 4, "风险分类");
}

// Slide 5
{
  const s = pptx.addSlide();
  s.background = { color: C.white };
  addTitle(s, "三类评测目标：不要混成一个“benchmark”问题", "同样都在测 agent security，但回答的问题并不相同");
  addCard(s, 0.7, 1.7, 3.9, 4.5, "F4FBFC", "CFE8EF");
  addCard(s, 4.75, 1.7, 3.9, 4.5, "F4F7FB", "D9E6F2");
  addCard(s, 8.8, 1.7, 3.9, 4.5, "F7F4FC", "E2D9F2");
  const cols = [
    ["长尾风险发现", "ToolEmu", ["目标：尽可能低成本找到会出事的失败模式", "适合：高后果工具、歧义指令、误操作场景", "不足：LM 仿真与真实环境仍有差距"]],
    ["动态对抗评测", "AgentDojo", ["目标：在状态化工具环境里同时看 utility 与 attack", "适合：tool output 注入、环境转移、对抗评测", "不足：攻击面仍偏 prompt injection"]],
    ["统一多攻击面", "ASB", ["目标：把 system prompt / memory / planning / tool 放进统一 benchmark", "适合：建立 taxonomy 与跨攻击面讨论", "不足：异质攻击被同一套指标聚合"]]
  ];
  cols.forEach((c, i) => {
    const x = 0.95 + i * 4.05;
    s.addText(c[0], {
      x, y: 2.0, w: 2.5, h: 0.25, fontSize: 16, bold: true, color: C.ink, margin: 0
    });
    s.addText(c[1], {
      x, y: 2.34, w: 1.7, h: 0.2, fontSize: 11, color: C.slate, margin: 0
    });
    c[2].forEach((t, idx) => {
      s.addShape(pptx.ShapeType.ellipse, {
        x, y: 2.82 + idx * 0.86, w: 0.18, h: 0.18,
        fill: { color: i === 0 ? C.teal : i === 1 ? C.blue : "6D4C9C" },
        line: { color: "FFFFFF", width: 0.5 }
      });
      s.addText(t, {
        x: x + 0.28, y: 2.78 + idx * 0.86, w: 2.95, h: 0.46, fontSize: 11.2,
        color: C.ink, margin: 0
      });
    });
  });
  addFooter(s, 5, "评测方法");
}

// Slide 6
{
  const s = pptx.addSlide();
  s.background = { color: C.cream };
  addTitle(s, "当前最值得继续补的 4 个缺口", "下一批阅读不应继续重复 benchmark，而应补机制与治理空白");
  const gaps = [
    ["Memory Poisoning", "现有工作已纳入 benchmark，但真实部署攻击与防御仍不成熟。", C.red],
    ["Multi-Agent / MCP Tool Chain", "多代理协作、工具协议与 skill / plugin 供应链风险研究不足。", C.blue],
    ["Approval Design", "什么时候需要人工确认、确认粒度是什么、如何降低确认疲劳，仍缺研究。", C.teal],
    ["Audit / Recovery", "回滚、追责、事后分析与组织级恢复机制，尚未进入主流指标。", C.gold]
  ];
  gaps.forEach((g, i) => {
    const x = i < 2 ? 0.75 : 6.55;
    const y = i % 2 === 0 ? 1.75 : 3.85;
    addCard(s, x, y, 5.45, 1.6, "FFFDFC", "DCCFB8");
    s.addShape(pptx.ShapeType.rect, {
      x: x + 0.2, y: y + 0.22, w: 0.15, h: 1.15, fill: { color: g[2] }, line: { color: g[2], width: 0 }
    });
    s.addText(g[0], {
      x: x + 0.5, y: y + 0.26, w: 3.2, h: 0.24, fontSize: 15, bold: true, color: C.ink, margin: 0
    });
    s.addText(g[1], {
      x: x + 0.5, y: y + 0.62, w: 4.55, h: 0.5, fontSize: 11.4, color: C.slate, margin: 0
    });
  });
  addFooter(s, 6, "研究缺口");
}

// Slide 7
{
  const s = pptx.addSlide();
  s.background = { color: C.white };
  addTitle(s, "建议的后续研究推进顺序", "按照“先补框架、再补机制、最后做方案”的顺序推进更稳");
  const steps = [
    ["01", "对齐治理框架", "用 OWASP / NIST 把技术风险映射到组织控制语言。"],
    ["02", "补 2025-2026 新论文", "重点补 memory poisoning、multi-agent、MCP / tool chain。"],
    ["03", "重写 related work", "把 4 篇核心论文改成投稿式英文 related work。"],
    ["04", "提出自己的评测或治理方案", "在权限、审批、记忆与审计之间选一个明确切口。"]
  ];
  s.addShape(pptx.ShapeType.line, {
    x: 1.2, y: 4.18, w: 10.6, h: 0, line: { color: C.line, width: 2 }
  });
  steps.forEach((st, i) => {
    const x = 0.9 + i * 3.0;
    s.addShape(pptx.ShapeType.ellipse, {
      x: x + 0.65, y: 3.78, w: 0.58, h: 0.58,
      fill: { color: i === 0 ? C.red : i === 1 ? C.blue : i === 2 ? C.teal : C.gold },
      line: { color: C.white, width: 1 }
    });
    addCard(s, x, 1.75, 2.35, 1.7, "F8FBFD", "D8E2E8");
    s.addText(st[0], {
      x: x + 0.18, y: 1.95, w: 0.5, h: 0.22, fontSize: 15, bold: true, color: C.slate, margin: 0
    });
    s.addText(st[1], {
      x: x + 0.18, y: 2.25, w: 1.95, h: 0.24, fontSize: 13, bold: true, color: C.ink, margin: 0
    });
    s.addText(st[2], {
      x: x + 0.18, y: 2.65, w: 1.95, h: 0.45, fontSize: 10.8, color: C.slate, margin: 0
    });
  });
  addFooter(s, 7, "推进顺序");
}

// Slide 8
{
  const s = pptx.addSlide();
  s.background = { color: C.ink };
  s.addText("结论", {
    x: 0.75, y: 0.85, w: 1.2, h: 0.35, fontSize: 24, bold: true, color: C.white, margin: 0
  });
  s.addText("AI Agent 安全不是单一 benchmark 问题，而是由权限、工具、记忆、执行与治理共同构成的系统问题。", {
    x: 0.75, y: 1.45, w: 9.2, h: 0.42, fontSize: 16, color: "DCE7F1", margin: 0
  });
  const points = [
    "Prompt Injection 解释起点，但不足以覆盖全部 agent 风险。",
    "ToolEmu、AgentDojo、ASB 分别回答长尾失败、动态攻防、多攻击面统一三个问题。",
    "下一步最该补的是 memory poisoning、multi-agent / MCP tool chain 与 approval design。",
    "研究输出已经具备：英文 IEEE 论文稿 + 中文汇报 PPTX + 阅读笔记与主题综述。"
  ];
  points.forEach((t, i) => {
    s.addShape(pptx.ShapeType.rect, {
      x: 0.82, y: 2.3 + i * 0.88, w: 0.16, h: 0.16,
      fill: { color: i % 2 === 0 ? C.red : C.gold }, line: { color: i % 2 === 0 ? C.red : C.gold, width: 0 }
    });
    s.addText(t, {
      x: 1.15, y: 2.19 + i * 0.88, w: 8.9, h: 0.34, fontSize: 13.5, color: C.white, margin: 0
    });
  });
  s.addText("academic-workspace / reports", {
    x: 0.78, y: 6.86, w: 2.6, h: 0.18, fontSize: 10, color: "AFC4D6", margin: 0
  });
  s.addText("08", {
    x: 12.1, y: 6.84, w: 0.35, h: 0.18, fontSize: 10, bold: true, color: C.white, align: "right", margin: 0
  });
}

pptx.writeFile({ fileName: "reports/2026-04-25-ai-agent-security-presentation-cn.pptx" });
