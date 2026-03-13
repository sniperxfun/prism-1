# PRISM Agent Specification v1.0

> Every agent in PRISM is a **Living Agent** — it has a fixed identity, a growing memory, and the capacity to evolve. Unlike static prompt files, a Living Agent improves with every project it touches.

---

## Agent File Structure

Every PRISM agent is a single Markdown file with a YAML frontmatter block followed by structured sections.

### Frontmatter Schema

```yaml
---
# ── Identity (immutable) ──────────────────────────────────────────
name: "Human-readable agent name"
slug: "kebab-case-unique-identifier"
version: "1.0.0"           # semver, bumped on each evolution
division: engineering       # engineering | product | design | growth | operations | specialized
tier: senior                # junior | mid | senior | principal

# ── Collaboration Graph ───────────────────────────────────────────
collaborates_with:
  - slug: frontend-developer
    relationship: peer        # peer | upstream | downstream | reviewer
  - slug: critic
    relationship: reviewer

# ── Activation Triggers ───────────────────────────────────────────
triggers:
  - "backend architecture"
  - "API design"
  - "database schema"

# ── Evolution State (managed by Evolution Layer) ──────────────────
evolution:
  status: active             # dormant | active | evolving
  generation: 1              # increments on each L2/L3 evolution
  last_evolved: null         # ISO 8601 date
  experience_tags: []        # populated by distillation engine
  performance:
    quality_score: null      # 0.0–1.0, rolling average
    first_pass_rate: null    # % of tasks passing QA on first attempt
    last_updated: null
---
```

### Required Sections

Every agent file MUST contain these sections in order:

```markdown
## Identity & Vibe
## Core Mission
## Critical Rules
## Deliverables
## Evolution Integration
```

### Section Specifications

#### `## Identity & Vibe`
Define who this agent IS — personality, worldview, communication style. This is the agent's "genetic code" and should rarely change.

```markdown
## Identity & Vibe

You are **[Name]**, [one-sentence character description].

**Personality**: [3–5 adjectives that define how this agent thinks and communicates]
**Worldview**: [The lens through which this agent sees every problem]
**Voice**: [How this agent communicates — formal/casual, terse/verbose, etc.]
**Memory**: You remember [what persistent knowledge this agent carries]
```

#### `## Core Mission`
Define what this agent DOES — the specific outcomes it produces. Be concrete, not aspirational.

#### `## Critical Rules`
Non-negotiable constraints. These CANNOT be overridden by dynamic context injection. Written as hard stops, not guidelines.

#### `## Deliverables`
Structured output templates. Every deliverable must have:
- A clear name
- A Markdown template
- Explicit acceptance criteria

#### `## Evolution Integration`
**This section is unique to PRISM.** It defines how this agent participates in the evolution loop.

```markdown
## Evolution Integration

### Experience Recall
At the start of each task, use the `recall_experience` MCP tool:
```
recall_experience({
  agent: "your-slug",
  context: "[brief description of current task]",
  top_k: 5
})
```
Apply retrieved principles as **soft guidance** — they inform your judgment, they don't override it.

### Decision Logging
When you make a significant decision (architecture choice, technology selection, approach tradeoff), log it:
```
record_decision({
  agent: "your-slug",
  decision: "[what you decided]",
  rationale: "[why]",
  alternatives_considered: "[what else you considered]"
})
```

### Task Telemetry
When you complete a task, report:
```
report_telemetry({
  agent: "your-slug",
  task_type: "[category of task]",
  outcome: "pass | fail | partial",
  retry_count: 0,
  notes: "[anything notable about this execution]"
})
```
```

---

## Agent Tiers

| Tier | Scope | Autonomy | Typical Role |
|------|-------|----------|-------------|
| **junior** | Single, well-defined tasks | Low — needs explicit instructions | Specialist executor |
| **mid** | Multi-step tasks within a domain | Medium — handles ambiguity within domain | Domain contributor |
| **senior** | Cross-domain tasks, architectural decisions | High — can challenge requirements | Domain lead |
| **principal** | System-wide concerns, strategic decisions | Full — can redefine scope | Cross-domain authority |

---

## Division Structure

| Division | Purpose | Key Agents |
|----------|---------|-----------|
| **engineering** | Build and maintain technical systems | Backend Architect, Frontend Developer, DevOps Engineer, Security Engineer |
| **product** | Define what to build and why | Product Strategist, Sprint Planner, Feedback Synthesizer |
| **design** | Define how it looks and feels | UX Architect, UI Designer, Brand Guardian |
| **growth** | Acquire and retain users | Growth Strategist, SEO Specialist, Content Creator |
| **operations** | Keep everything running | Analytics Reporter, Finance Tracker, Legal Compliance |
| **specialized** | Cross-cutting concerns | Conductor, Critic, Planner, MCP Builder |

---

## Naming Convention

Agent files follow this pattern: `{division}-{role}.md`

Examples:
- `engineering-backend-architect.md`
- `product-sprint-planner.md`
- `design-ux-architect.md`
- `growth-seo-specialist.md`
