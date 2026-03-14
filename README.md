<div align="center">

# PRISM

### **P**ersistent **R**easoning & **I**ntelligent **S**elf-evolving **M**ulti-agent Framework

### 持久推理与智能自进化多智能体框架

*The AI team that gets better every time you use it.*

*越用越强的 AI 智能体团队。*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/Agents-20-blue)](#agent-library--智能体库)
[![Evolution](https://img.shields.io/badge/Self--Evolving-Yes-green)](#evolution-layer--进化层)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple)](#mcp-integration)

[English](#what-is-prism) | [中文](#什么是-prism)

</div>

---

## What is PRISM?

PRISM is a self-evolving multi-agent framework for AI-assisted software development and product delivery. It combines three ideas that have never been put together in a single open-source project:

**1. Living Agents** — Every agent in PRISM has a fixed identity and a growing memory. Unlike static prompt files that get stale, PRISM agents accumulate experience from every project they touch and apply that experience to the next one.

**2. Adaptive Orchestration (PRISM Flow)** — A quality-gated pipeline protocol that dynamically selects the right execution mode for each project. Not every project needs every phase. PRISM Flow knows the difference.

**3. Native Evolution Loop** — Self-improvement is not bolted on after the fact. Every agent file has an `## Evolution Integration` section. Every task generates telemetry. Every project feeds the distillation engine. The system compounds.

---

## 什么是 PRISM？

PRISM 是一个面向 AI 辅助软件开发与产品交付的**自进化多智能体框架**。它将三个从未在同一个开源项目中结合过的理念融为一体：

**1. 活的智能体（Living Agents）** — PRISM 中的每个智能体都拥有固定身份和成长记忆。与会逐渐过时的静态提示词文件不同，PRISM 智能体从每个项目中积累经验，并将这些经验应用到下一个项目中。

**2. 自适应编排（PRISM Flow）** — 一套带质量门控的流水线协议，根据项目规模和风险动态选择最合适的执行模式。不是每个项目都需要走完所有阶段，PRISM Flow 能自动判断。

**3. 原生进化循环（Native Evolution Loop）** — 自我改进不是事后叠加的功能。每个智能体文件都内置 `## Evolution Integration` 章节，每次任务都生成遥测数据，每个项目都喂入蒸馏引擎。系统持续复利增长。

---

## How is PRISM different? | PRISM 有何不同？

PRISM was inspired by [agency-agents](https://github.com/msitarzewski/agency-agents) and deeply respects its design philosophy. Here is where PRISM goes further:

PRISM 受 [agency-agents](https://github.com/msitarzewski/agency-agents) 启发，并深度尊重其设计哲学。以下是 PRISM 的进一步突破：

| Feature 特性 | agency-agents | PRISM |
|-------------|--------------|-------|
| Agent format 智能体格式 | Static Markdown 静态 Markdown | Living Agent 活的智能体（固定身份 + 成长记忆） |
| Orchestration 编排 | Fixed 7-phase NEXUS 固定 7 阶段 | Adaptive PRISM Flow 自适应（4 种执行模式） |
| Quality gate 质量门控 | Dev↔QA loop | Dev↔Critic loop + phase gates + escalation 阶段门控 + 升级协议 |
| Self-improvement 自我改进 | None 无 | Native 3-level evolution 原生三级进化（L1/L2/L3） |
| Experience 经验积累 | None 无 | MCP Experience Library 经验库（SQLite/PostgreSQL） |
| Agent relationships 智能体关系 | Implicit 隐式 | Explicit collaboration graph 显式协作图谱 |
| Drift detection 漂移检测 | None 无 | Automated monitoring 自动性能监控 + 告警 |
| Tool integration 工具集成 | convert.sh (10 platforms) | MCP-native 原生 MCP 集成 |

---

## Quick Start | 快速上手

### 1. Pick your AI tool | 选择你的 AI 工具

PRISM works with any MCP-compatible AI tool. Recommended: Claude Code, Cursor, or Windsurf.

PRISM 兼容任何支持 MCP 的 AI 工具，推荐：Claude Code、Cursor 或 Windsurf。

### 2. Install the Evolution MCP Server (optional) | 安装进化层 MCP 服务器（可选）

```bash
# Clone the repo | 克隆仓库
git clone https://github.com/prism-agentic/prism.git
cd prism

# Install dependencies | 安装依赖
pip install openai

# Add to your AI tool's MCP config | 添加到你的 AI 工具 MCP 配置
# See integrations/ for tool-specific guides | 参见 integrations/ 目录获取各工具配置指南
```

### 3. Start your first project | 启动你的第一个项目

Open your AI tool and paste this prompt:

打开你的 AI 工具，粘贴以下提示词：

```
Activate the Conductor agent from agents/specialized/conductor.md.
I want to [describe your project].
Use PRISM Flow to orchestrate the delivery.
```

The Conductor will | Conductor 将会：
1. Analyze your request and select the appropriate execution mode | 分析需求并选择执行模式
2. Produce a Pipeline Initialization Report | 生成流水线初始化报告
3. Activate the right agents in the right sequence | 按正确顺序激活合适的智能体
4. Enforce quality gates at every phase transition | 在每个阶段转换时执行质量门控
5. Report learnings to the Evolution Layer at completion | 完成后向进化层报告学习成果

See [QUICKSTART.md](QUICKSTART.md) for step-by-step examples | 参见 [QUICKSTART.md](QUICKSTART.md) 获取详细示例。

---

## Agent Library | 智能体库

PRISM ships with 20 production-ready Living Agents across 6 divisions.

PRISM 内置 20 个生产就绪的 Living Agent，覆盖 6 大部门。

### Specialized Division 专项部门 — "Run the System 运行系统"

| Agent 智能体 | Superpower 超能力 | Tier 层级 |
|-------------|-----------------|----------|
| [Conductor](agents/specialized/conductor.md) | Pipeline orchestration 流水线编排 | Principal |
| [Critic](agents/specialized/critic.md) | Quality review, default NEEDS WORK 质量审查 | Principal |
| [Planner](agents/specialized/planner.md) | Discovery, requirements clarity 需求发现 | Principal |
| [Evolution Steward](agents/specialized/evolution-steward.md) | Agent performance monitoring 性能监控 | Principal |
| [MCP Builder](agents/specialized/mcp-builder.md) | MCP server design MCP 服务器设计 | Senior |

### Engineering Division 工程部门 — "Build It Right 正确构建"

| Agent 智能体 | Superpower 超能力 | Tier 层级 |
|-------------|-----------------|----------|
| [Backend Architect](agents/engineering/backend-architect.md) | System design, APIs, databases 系统设计 | Senior |
| [Frontend Developer](agents/engineering/frontend-developer.md) | React/Vue, performance 前端开发 | Senior |
| [DevOps Engineer](agents/engineering/devops-engineer.md) | CI/CD, containers, monitoring 运维 | Senior |
| [Security Engineer](agents/engineering/security-engineer.md) | Security audit, compliance 安全审计 | Principal |

### Product Division 产品部门 — "Build the Right Thing 构建正确的东西"

| Agent 智能体 | Superpower 超能力 | Tier 层级 |
|-------------|-----------------|----------|
| [Product Strategist](agents/product/product-strategist.md) | Product positioning, roadmap 产品定位 | Senior |
| [Sprint Planner](agents/product/sprint-planner.md) | Task decomposition, estimation 任务拆解 | Mid |
| [Feedback Synthesizer](agents/product/feedback-synthesizer.md) | User feedback analysis 用户反馈分析 | Mid |

### Design Division 设计部门 — "Make It Beautiful 让它更美"

| Agent 智能体 | Superpower 超能力 | Tier 层级 |
|-------------|-----------------|----------|
| [UX Architect](agents/design/ux-architect.md) | Information architecture, usability 信息架构 | Senior |
| [UI Designer](agents/design/ui-designer.md) | Visual design systems 视觉设计 | Mid |
| [Brand Guardian](agents/design/brand-guardian.md) | Brand consistency 品牌一致性 | Senior |

### Growth Division 增长部门 — "Grow It 驱动增长"

| Agent 智能体 | Superpower 超能力 | Tier 层级 |
|-------------|-----------------|----------|
| [Growth Strategist](agents/growth/growth-strategist.md) | Full-funnel growth 全漏斗增长 | Senior |
| [SEO Specialist](agents/growth/seo-specialist.md) | Technical SEO, keyword strategy SEO 优化 | Mid |
| [Content Creator](agents/growth/content-creator.md) | Blog posts, marketing copy 内容创作 | Mid |

### Operations Division 运营部门 — "Keep It Running 持续运行"

| Agent 智能体 | Superpower 超能力 | Tier 层级 |
|-------------|-----------------|----------|
| [Analytics Reporter](agents/operations/analytics-reporter.md) | KPI tracking, dashboards 数据分析 | Mid |
| [Legal Compliance Checker](agents/operations/legal-compliance-checker.md) | GDPR, privacy, regulatory 合规审查 | Senior |

---

## PRISM Flow | PRISM 编排协议

PRISM Flow is the adaptive orchestration protocol. It selects the right execution mode based on project scope and risk.

PRISM Flow 是自适应编排协议，根据项目规模和风险自动选择最合适的执行模式。

```
PRISM-Full    → 6 phases, 20-40 agents  → New product 新产品, high-stakes delivery 高风险交付
PRISM-Sprint  → 4 phases, 8-15 agents   → Feature addition 功能迭代, known scope 明确范围
PRISM-Micro   → 2 phases, 3-6 agents    → Bug fix 缺陷修复, small enhancement 小优化
PRISM-Explore → 2 phases, 3-5 agents    → Discovery 探索, feasibility 可行性验证
```

Every mode enforces the same quality principles | 所有模式遵循相同的质量原则：

- **Evidence Over Claims 证据优先**：No phase advances without documented proof 无证据不推进
- **Context Continuity 上下文连续性**：Every handoff carries full context 每次交接携带完整上下文
- **Critic Independence 审查独立性**：The Critic defaults to NEEDS WORK 审查者默认"需改进"
- **Evolution Awareness 进化感知**：Every execution generates learnings 每次执行产生学习成果

See [core/PRISM-PROTOCOL.md](core/PRISM-PROTOCOL.md) for the complete specification | 参见完整规范。

---

## Evolution Layer | 进化层

The Evolution Layer is what makes PRISM a living system rather than a static library.

进化层是让 PRISM 成为活系统而非静态库的关键。

```
Project Execution 项目执行
      ↓
Telemetry Collection 遥测收集  ← Agents report decisions + outcomes 智能体报告决策与结果
      ↓
Distillation Engine 蒸馏引擎   ← Extracts reusable principles 提取可复用原则
      ↓
Experience Library 经验库      ← Stores principles with quality scores 存储带质量评分的原则
      ↓
Context Injection 上下文注入   ← Enriches agents at task start 任务开始时增强智能体
      ↓
Better Execution 更好的执行    ← Higher quality, fewer retries 更高质量，更少重试
      ↓
[repeat 循环]
```

### Three Evolution Levels | 三级进化机制

| Level 级别 | Trigger 触发条件 | Risk 风险 | Approval 审批 |
|-----------|-----------------|----------|--------------|
| **L1 Experience Injection 经验注入** | Every task 每次任务 | Zero 零 | None 无需审批 |
| **L2 Prompt Refinement 提示词优化** | First-pass rate < 65% 首次通过率 < 65% | Low-Medium 低中 | Human review 人工审查 |
| **L3 Agent Reconstruction 智能体重构** | First-pass rate < 50% for 30+ days 持续30天 < 50% | High 高 | Expert review + A/B test 专家审查 + A/B 测试 |

### MCP Integration | MCP 集成

The Experience Library is exposed as an MCP server:

经验库通过 MCP 服务器对外暴露：

```bash
# Start the MCP server | 启动 MCP 服务器
python evolution/mcp-server/server.py

# Available tools | 可用工具:
# - recall_experience: Get relevant principles 获取相关经验原则
# - record_decision: Log important decisions 记录重要决策
# - report_telemetry: Report task outcomes 报告任务结果
# - get_agent_stats: View agent performance 查看智能体性能
```

See [evolution/mcp-server/README.md](evolution/mcp-server/README.md) for setup | 参见配置指南。

---

## Project Structure | 项目结构

```
prism/
├── core/                    # Framework specs 框架规范
│   ├── PRISM-PROTOCOL.md   # Orchestration protocol 编排协议
│   ├── AGENT-SPEC.md       # Agent file spec 智能体规范
│   └── EVOLUTION-SPEC.md   # Evolution mechanism 进化机制规范
│
├── agents/                  # Living Agent library 智能体库
│   ├── engineering/         # Backend, Frontend, DevOps, Security 工程部门
│   ├── product/             # Strategy, Planning, Feedback 产品部门
│   ├── design/              # UX, UI, Brand 设计部门
│   ├── growth/              # Growth, SEO, Content 增长部门
│   ├── operations/          # Analytics, Legal 运营部门
│   └── specialized/         # Conductor, Critic, Planner, Evolution Steward, MCP Builder 专项部门
│
├── evolution/               # Evolution Layer 进化层
│   ├── mcp-server/          # MCP Experience Library server 经验库服务器
│   ├── distillation/        # Distillation engine 蒸馏引擎
│   └── judge/               # LLM-as-Judge evaluator 评估器
│
├── integrations/            # Tool-specific setup guides 工具集成指南
│   ├── claude-code/
│   └── cursor/
│
└── examples/                # Example workflows 示例工作流
```

---

## Contributing | 贡献指南

PRISM is an open-source project and welcomes contributions of all kinds:

PRISM 是一个开源项目，欢迎各种形式的贡献：

- **New agents 新智能体**: Follow the [Agent Specification](core/AGENT-SPEC.md) and submit a PR | 遵循智能体规范并提交 PR
- **Evolution improvements 进化层改进**: Propose changes to the distillation engine or judge | 改进蒸馏引擎或评估器
- **Orchestration patterns 编排模式**: Add reusable patterns | 添加可复用的编排模式
- **Bug reports 缺陷报告**: Use the GitHub issue templates | 使用 Issue 模板

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines | 参见贡献指南。

---

## License | 许可证

MIT License — see [LICENSE](LICENSE) for details.

MIT 许可证 — 详见 [LICENSE](LICENSE)。

---

<div align="center">

**6 Divisions · 4 Execution Modes · 1 System That Learns**

**6 大部门 · 4 种执行模式 · 1 个持续进化的系统**

*From discovery to sustained operations — every agent knows their role, their history, and their next evolution.*

*从需求发现到持续运营——每个智能体都清楚自己的角色、历史和下一次进化方向。*

</div>
