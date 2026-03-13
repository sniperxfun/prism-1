# PRISM Evolution Specification v1.0

> The Evolution Layer is what separates PRISM from a static prompt library. Every project run teaches the system something. Every agent gets better over time. The team that uses PRISM for a year is categorically more capable than the team that just started.

---

## The Evolution Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRISM Evolution Loop                          │
│                                                                  │
│  Project Execution                                               │
│       ↓                                                          │
│  Telemetry Collection  ←── Agents report decisions + outcomes   │
│       ↓                                                          │
│  Distillation Engine   ←── Extracts reusable principles         │
│       ↓                                                          │
│  Experience Library    ←── Stores principles with quality scores │
│       ↓                                                          │
│  Context Injection     ←── Enriches agents at task start        │
│       ↓                                                          │
│  Better Execution      ←── Higher quality, fewer retries        │
│       ↓                                                          │
│  [repeat]                                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Evolution Levels

### L1 — Experience Injection (Automatic, Every Task)

**What it does**: Retrieves relevant principles from the Experience Library and injects them as soft context at the start of each task.

**Risk**: Zero — does not modify any agent file.

**Trigger**: Every task start.

**Mechanism**:
```
recall_experience(agent_slug, task_context) 
  → returns top-5 relevant principles
  → injected as "Relevant Experience" block in agent context
```

**Example injection**:
```markdown
## Relevant Experience (from Evolution Layer)

Based on 23 similar tasks, these principles have improved outcomes:

1. **[PostgreSQL + high-concurrency]** Use connection pooling (PgBouncer) from day one — retrofitting is painful. Confidence: 0.91
2. **[API design + versioning]** Version in the URL path (/v1/) not headers — easier to debug in logs. Confidence: 0.87
3. **[microservices + auth]** Implement auth as a sidecar, not embedded in each service. Confidence: 0.83

*These are suggestions, not rules. Use your judgment.*
```

---

### L2 — Prompt Refinement (Semi-automatic, Requires Human Approval)

**What it does**: Generates an improved version of an agent's prompt based on accumulated experience data.

**Risk**: Low-Medium — modifies agent files, but requires human approval.

**Trigger**: Agent's first-pass rate drops below 65% over 10+ tasks, OR accumulated experience suggests a systematic improvement.

**Process**:
1. Distillation Engine analyzes agent's execution history
2. Generates specific improvement proposals (not full rewrites)
3. LLM-as-Judge evaluates improvement on test cases (must show ≥ 5% improvement)
4. Creates a Pull Request with the proposed changes
5. Human reviewer approves/rejects/modifies
6. On merge: version bumped, evolution history updated

**What can be changed in L2**:
- ✅ Adding new best practices to Core Mission
- ✅ Updating Deliverables templates with better examples
- ✅ Refining acceptance criteria based on real failure patterns
- ✅ Adding new experience tags
- ❌ Cannot change Identity & Vibe (that's L3)
- ❌ Cannot change Critical Rules (that's L3)

---

### L3 — Agent Reconstruction (Manual, Expert Review Required)

**What it does**: Fundamentally redesigns an agent's identity, mission, or constraints.

**Risk**: High — changes the agent's core behavior.

**Trigger**: All of the following must be true:
- First-pass rate below 50% for 30+ consecutive days
- L1 and L2 interventions have not improved performance
- Root cause analysis identifies a fundamental design flaw

**Process**:
1. Evolution Layer flags agent for L3 review
2. Human expert conducts root cause analysis
3. New agent design proposed and documented
4. Community discussion period (for open source contributions)
5. A/B testing against old version on real tasks
6. Gradual rollout (10% → 50% → 100%)

---

## MCP Experience Library

The Experience Library is exposed as an MCP server, making it accessible to any MCP-compatible AI tool (Claude Code, Cursor, Windsurf, etc.).

### Available Tools

#### `recall_experience`
Retrieve relevant principles for the current task.

```typescript
recall_experience({
  agent: string,          // agent slug
  context: string,        // natural language description of current task
  top_k?: number,         // default: 5
  min_confidence?: number // default: 0.7
}) → {
  principles: Array<{
    text: string,
    confidence: number,
    source_count: number,  // how many projects contributed to this principle
    tags: string[]
  }>
}
```

#### `record_decision`
Log a significant decision for future distillation.

```typescript
record_decision({
  agent: string,
  decision: string,
  rationale: string,
  alternatives_considered?: string,
  outcome?: "pending" | "success" | "failure"  // update later
}) → { decision_id: string }
```

#### `report_telemetry`
Report task execution metrics.

```typescript
report_telemetry({
  agent: string,
  task_type: string,
  outcome: "pass" | "fail" | "partial",
  retry_count: number,
  failure_category?: "ambiguous_spec" | "implementation_error" | "context_loss" | "scope_creep" | "other",
  notes?: string
}) → { recorded: boolean }
```

#### `get_agent_stats`
View an agent's performance history.

```typescript
get_agent_stats({
  agent: string,
  days?: number  // default: 30
}) → {
  first_pass_rate: number,
  avg_retries: number,
  total_tasks: number,
  evolution_status: string,
  top_principles: Principle[]
}
```

---

## Drift Detection

The Evolution Layer continuously monitors for performance drift:

| Signal | Threshold | Response |
|--------|-----------|----------|
| First-pass rate drops > 10% (7-day window) | L1 alert | Auto-inject more context |
| First-pass rate drops > 20% (14-day window) | L2 alert | Trigger L2 review process |
| First-pass rate drops > 35% (30-day window) | L3 alert | Flag for expert review |
| Critic issues `BLOCKED` 3x in a row | Immediate | Human notification |

---

## Safety Constraints

The Evolution Layer operates within strict boundaries:

**Never auto-modify**:
- `## Critical Rules` sections
- Security-related constraints
- Legal compliance requirements
- The Critic's default `NEEDS WORK` stance

**Always require human approval**:
- Any L2 or L3 evolution
- Changes to agent tier or division
- Modifications to collaboration graph relationships

**Always maintain**:
- Full version history (Git-backed)
- Rollback capability to any previous version
- Audit log of all evolution events

---

## Getting Started with Evolution

### Minimal Setup (L1 only — no infrastructure required)

1. Install the PRISM MCP server (see `evolution/mcp-server/README.md`)
2. Add the MCP server to your AI tool's configuration
3. Agents will automatically use `recall_experience` at task start
4. Experience accumulates in a local SQLite database

### Full Setup (L1 + L2 + Drift Detection)

See `evolution/README.md` for the complete setup guide including:
- PostgreSQL for production-grade storage
- Chroma for semantic search
- EvidentlyAI for drift monitoring
- GitHub Actions for automated L2 PR creation
