<div align="center">

# PRISM

### **P**ersistent **R**easoning & **I**ntelligent **S**elf-evolving **M**ulti-agent Framework

*The AI team that gets better every time you use it.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/Agents-20-blue)](#agent-library)
[![Evolution](https://img.shields.io/badge/Self--Evolving-Yes-green)](#evolution-layer)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple)](#mcp-integration)

</div>

---

## What is PRISM?

PRISM is a self-evolving multi-agent framework for AI-assisted software development and product delivery. It combines three ideas that have never been put together in a single open-source project:

**1. Living Agents** — Every agent in PRISM has a fixed identity and a growing memory. Unlike static prompt files that get stale, PRISM agents accumulate experience from every project they touch and apply that experience to the next one.

**2. Adaptive Orchestration (PRISM Flow)** — A quality-gated pipeline protocol that dynamically selects the right execution mode for each project. Not every project needs every phase. PRISM Flow knows the difference.

**3. Native Evolution Loop** — Self-improvement is not bolted on after the fact. Every agent file has an `## Evolution Integration` section. Every task generates telemetry. Every project feeds the distillation engine. The system compounds.

---

## How is PRISM different from agency-agents?

PRISM was inspired by [agency-agents](https://github.com/msitarzewski/agency-agents) and deeply respects its design philosophy. Here is where PRISM goes further:

| Feature | agency-agents | PRISM |
|---------|--------------|-------|
| Agent format | Static Markdown | Living Agent (static identity + growing memory) |
| Orchestration | Fixed 7-phase NEXUS | Adaptive PRISM Flow (4 execution modes) |
| Quality gate | Dev↔QA loop | Dev↔Critic loop + phase gates + escalation protocol |
| Self-improvement | None | Native 3-level evolution (L1/L2/L3) |
| Experience accumulation | None | MCP Experience Library (SQLite or PostgreSQL) |
| Agent relationships | Implicit | Explicit collaboration graph in frontmatter |
| Drift detection | None | Automated performance monitoring + alerts |
| Tool integration | convert.sh (10 platforms) | MCP-native (any MCP-compatible tool) |

---

## Quick Start

### 1. Pick your AI tool

PRISM works with any MCP-compatible AI tool. Recommended: Claude Code, Cursor, or Windsurf.

### 2. Install the Evolution MCP Server (optional but recommended)

```bash
# Clone the repo
git clone https://github.com/your-org/prism.git
cd prism

# Install MCP server dependencies
pip install openai sqlite3

# Add to your AI tool's MCP config (see integrations/ for tool-specific guides)
```

### 3. Start your first project

Open your AI tool and paste this prompt:

```
Activate the Conductor agent from PRISM. I want to [describe your project].
Use PRISM Flow to orchestrate the delivery.
```

The Conductor will:
1. Analyze your request and select the appropriate execution mode
2. Produce a Pipeline Initialization Report
3. Activate the right agents in the right sequence
4. Enforce quality gates at every phase transition
5. Report learnings to the Evolution Layer at completion

### 4. Read the QUICKSTART guide

See [QUICKSTART.md](QUICKSTART.md) for step-by-step examples with real projects.

---

## Agent Library

PRISM ships with 20 production-ready Living Agents across 6 divisions.

### Specialized Division — "Run the System"
| Agent | Superpower | Tier |
|-------|-----------|------|
| [Conductor](agents/specialized/conductor.md) | Pipeline orchestration, task assignment, phase gate management | Principal |
| [Critic](agents/specialized/critic.md) | Quality review, evidence-based assessment, default NEEDS WORK | Principal |
| [Planner](agents/specialized/planner.md) | Discovery, requirements clarity, scope definition | Principal |
| [Evolution Steward](agents/specialized/evolution-steward.md) | Agent performance monitoring, evolution trigger, L2/L3 review | Principal |
| [MCP Builder](agents/specialized/mcp-builder.md) | MCP server design and implementation | Senior |

### Engineering Division — "Build It Right"
| Agent | Superpower | Tier |
|-------|-----------|------|
| [Backend Architect](agents/engineering/backend-architect.md) | Scalable system design, APIs, databases, cloud | Senior |
| [Frontend Developer](agents/engineering/frontend-developer.md) | React/Vue, performance, responsive design | Senior |
| [DevOps Engineer](agents/engineering/devops-engineer.md) | CI/CD, containers, cloud deployment, monitoring | Senior |
| [Security Engineer](agents/engineering/security-engineer.md) | Security audit, vulnerability assessment, compliance | Principal |

### Product Division — "Build the Right Thing"
| Agent | Superpower | Tier |
|-------|-----------|------|
| [Product Strategist](agents/product/product-strategist.md) | Product positioning, user research, roadmap | Senior |
| [Sprint Planner](agents/product/sprint-planner.md) | Task decomposition, estimation, sprint scope | Mid |
| [Feedback Synthesizer](agents/product/feedback-synthesizer.md) | User feedback analysis, product improvement signals | Mid |

### Design Division — "Make It Beautiful"
| Agent | Superpower | Tier |
|-------|-----------|------|
| [UX Architect](agents/design/ux-architect.md) | Information architecture, user journeys, usability | Senior |
| [UI Designer](agents/design/ui-designer.md) | Visual design systems, components, prototypes | Mid |
| [Brand Guardian](agents/design/brand-guardian.md) | Brand consistency, visual identity, tone of voice | Senior |

### Growth Division — "Grow It"
| Agent | Superpower | Tier |
|-------|-----------|------|
| [Growth Strategist](agents/growth/growth-strategist.md) | Full-funnel growth strategy, A/B testing | Senior |
| [SEO Specialist](agents/growth/seo-specialist.md) | Technical SEO, keyword strategy, search ranking | Mid |
| [Content Creator](agents/growth/content-creator.md) | Blog posts, marketing copy, social content | Mid |

### Operations Division — "Keep It Running"
| Agent | Superpower | Tier |
|-------|-----------|------|
| [Analytics Reporter](agents/operations/analytics-reporter.md) | KPI tracking, dashboards, executive reporting | Mid |
| [Legal Compliance Checker](agents/operations/legal-compliance-checker.md) | GDPR, privacy policy, regulatory compliance | Senior |

---

## PRISM Flow

PRISM Flow is the adaptive orchestration protocol. It selects the right execution mode based on project scope and risk.

```
PRISM-Full    → 6 phases, 20-40 agents  → New product, high-stakes delivery
PRISM-Sprint  → 4 phases, 8-15 agents   → Feature addition, known scope
PRISM-Micro   → 2 phases, 3-6 agents    → Bug fix, small enhancement
PRISM-Explore → 2 phases, 3-5 agents    → Discovery, feasibility
```

Every mode enforces the same quality principles:
- **Evidence Over Claims**: No phase advances without documented proof
- **Context Continuity**: Every handoff carries full context
- **Critic Independence**: The Critic defaults to NEEDS WORK, always
- **Evolution Awareness**: Every execution generates learnings

See [core/PRISM-PROTOCOL.md](core/PRISM-PROTOCOL.md) for the complete protocol specification.

---

## Evolution Layer

The Evolution Layer is what makes PRISM a living system rather than a static library.

```
Project Execution
      ↓
Telemetry Collection  ← Agents report decisions + outcomes
      ↓
Distillation Engine   ← Extracts reusable principles
      ↓
Experience Library    ← Stores principles with quality scores
      ↓
Context Injection     ← Enriches agents at task start
      ↓
Better Execution      ← Higher quality, fewer retries
      ↓
[repeat]
```

### Three Evolution Levels

| Level | Trigger | Risk | Approval Required |
|-------|---------|------|------------------|
| **L1 Experience Injection** | Every task | Zero | None — fully automatic |
| **L2 Prompt Refinement** | First-pass rate < 65% | Low-Medium | Human review of PR |
| **L3 Agent Reconstruction** | First-pass rate < 50% for 30+ days | High | Expert review + A/B test |

### MCP Integration

The Experience Library is exposed as an MCP server. Any MCP-compatible tool can access it:

```bash
# Start the MCP server
python evolution/mcp-server/server.py

# Available tools:
# - recall_experience: Get relevant principles for current task
# - record_decision: Log important decisions
# - report_telemetry: Report task outcomes
# - get_agent_stats: View agent performance history
```

See [evolution/mcp-server/README.md](evolution/mcp-server/README.md) for setup instructions.

---

## Project Structure

```
prism/
├── core/                    # Framework specifications
│   ├── PRISM-PROTOCOL.md   # Orchestration protocol
│   ├── AGENT-SPEC.md       # Agent file specification
│   ├── EVOLUTION-SPEC.md   # Evolution mechanism spec
│   └── HANDOFF-SPEC.md     # Handoff protocol
│
├── agents/                  # Living Agent library
│   ├── engineering/         # Backend, Frontend, DevOps, Security
│   ├── product/             # Strategy, Planning, Feedback
│   ├── design/              # UX, UI, Brand
│   ├── growth/              # Growth, SEO, Content
│   ├── operations/          # Analytics, Legal
│   └── specialized/         # Conductor, Critic, Planner, Evolution Steward, MCP Builder
│
├── orchestration/           # Orchestration resources
│   ├── playbooks/           # Phase-by-phase execution guides
│   └── patterns/            # Reusable orchestration patterns
│
├── evolution/               # Evolution Layer
│   ├── mcp-server/          # MCP Experience Library server
│   ├── distillation/        # Distillation engine
│   ├── judge/               # LLM-as-Judge evaluator
│   └── telemetry/           # Telemetry collection utilities
│
├── integrations/            # Tool-specific setup guides
│   ├── claude-code/
│   ├── cursor/
│   └── windsurf/
│
└── examples/               # Example workflows
```

---

## Contributing

PRISM is an open-source project and welcomes contributions of all kinds:

- **New agents**: Follow the [Agent Specification](core/AGENT-SPEC.md) and submit a PR
- **Evolution improvements**: Propose changes to the distillation engine or judge
- **Orchestration patterns**: Add reusable patterns to `orchestration/patterns/`
- **Bug reports**: Use the GitHub issue templates

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**PRISM: 6 Divisions. 4 Execution Modes. One System That Learns.**

*From discovery to sustained operations — every agent knows their role, their history, and their next evolution.*

</div>
