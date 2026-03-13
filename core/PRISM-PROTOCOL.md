# PRISM Flow Protocol v1.0

> **PRISM Flow** is the adaptive orchestration protocol at the heart of PRISM. Unlike fixed pipelines, PRISM Flow dynamically selects the right execution pattern based on project characteristics — then learns from every run to get better at that selection.

---

## Core Principles

**1. Evidence Over Claims**
No phase advances without documented evidence. "It works" is not evidence. A passing test suite, a screenshot, a benchmark result — those are evidence.

**2. Context Continuity**
Every handoff carries the full context needed for the next agent to succeed without asking clarifying questions. A handoff that requires follow-up questions has failed.

**3. Critic Independence**
The Critic agent is structurally independent from the agents it reviews. It defaults to `NEEDS WORK`. It cannot be overridden by the Conductor. Its default is pessimism, not optimism.

**4. Evolution Awareness**
Every execution is a learning opportunity. The Conductor reports telemetry after every project. Agents log decisions. The Evolution Layer distills patterns. The system gets better.

**5. Adaptive Depth**
Not every project needs every phase. PRISM Flow selects the appropriate execution mode based on project scope, risk, and time constraints.

---

## Execution Modes

| Mode | Phases | Agents | Use When |
|------|--------|--------|----------|
| **PRISM-Full** | All 6 phases | 20–40 agents | New product, major feature, high-stakes delivery |
| **PRISM-Sprint** | Phases 2–5 | 8–15 agents | Feature addition, known scope, 1–2 week timeline |
| **PRISM-Micro** | Phases 3–4 | 3–6 agents | Bug fix, small enhancement, single-domain task |
| **PRISM-Explore** | Phases 0–1 | 3–5 agents | Discovery, research, feasibility assessment |

---

## Phase Definitions

### Phase 0 — DISCOVER
**Purpose**: Understand the problem space before committing to a solution.
**Gate**: Planner approves discovery completeness.
**Key Agents**: Planner, Product Strategist, UX Researcher

**Outputs Required**:
- Problem statement (validated with evidence)
- User/stakeholder map
- Constraint inventory (technical, business, time)
- Success metrics (measurable, not aspirational)
- Go/No-Go recommendation

**Gate Criteria**: Can we clearly state what success looks like and why this is worth building?

---

### Phase 1 — STRATEGIZE
**Purpose**: Decide the approach before writing a line of code.
**Gate**: Conductor + Critic approve strategy.
**Key Agents**: Product Strategist, Backend Architect, UX Architect, Security Engineer

**Outputs Required**:
- Technical architecture decision record (ADR)
- Risk register (P0–P3 classification)
- Agent activation plan (which agents, in what order)
- Definition of Done for each deliverable

**Gate Criteria**: Does the strategy address all P0 risks? Is the architecture decision defensible?

---

### Phase 2 — SCAFFOLD
**Purpose**: Establish the foundation everything else builds on.
**Gate**: Critic validates foundation integrity.
**Key Agents**: Backend Architect, Frontend Developer, DevOps Engineer

**Outputs Required**:
- Repository structure + CI/CD pipeline
- Core data models and API contracts
- Development environment (reproducible in < 5 minutes)
- Security baseline (auth, secrets management, dependency scanning)

**Gate Criteria**: Can a new engineer clone the repo and run the project in under 5 minutes?

---

### Phase 3 — BUILD
**Purpose**: Implement the solution, task by task, with continuous QA.
**Gate**: Each task passes Critic review before the next begins.
**Key Agents**: Domain specialists + Critic (per task)

**The Build Loop** (per task):
```
1. Conductor assigns task to appropriate agent
2. Agent implements and submits deliverable
3. Critic reviews against acceptance criteria
4. IF PASS → log telemetry → next task
5. IF FAIL → agent revises with Critic feedback → retry (max 3)
6. IF 3 FAILS → escalate to Conductor → human review flag
```

**Gate Criteria**: All tasks PASS Critic review. Zero P0 issues open.

---

### Phase 4 — HARDEN
**Purpose**: Stress-test the system before it meets real users.
**Gate**: Critic certifies production readiness.
**Key Agents**: Security Engineer, Performance Benchmarker, Accessibility Auditor, Critic

**Outputs Required**:
- Security audit report (no P0/P1 vulnerabilities)
- Performance benchmark (meets defined SLAs)
- Accessibility audit (WCAG 2.1 AA minimum)
- Disaster recovery test results

**Gate Criteria**: System survives adversarial testing. Critic certifies `READY` (not just `NEEDS WORK`).

---

### Phase 5 — LAUNCH
**Purpose**: Ship with confidence and a rollback plan.
**Gate**: Conductor confirms launch checklist complete.
**Key Agents**: DevOps Engineer, Conductor

**Outputs Required**:
- Deployment runbook (step-by-step, tested)
- Rollback procedure (tested, < 5 min execution)
- Monitoring dashboard (key metrics visible)
- Launch communication (internal + external)

---

### Phase 6 — OPERATE
**Purpose**: Keep the system healthy and capture learnings for evolution.
**Gate**: Continuous (no single gate — ongoing monitoring)
**Key Agents**: Analytics Reporter, Infrastructure Maintainer, Conductor (evolution reporting)

**Ongoing Responsibilities**:
- Monitor performance against Phase 0 success metrics
- Capture user feedback and route to Product Strategist
- Detect drift (performance degradation, changing requirements)
- **Trigger Evolution Layer**: After each project, Conductor submits pipeline telemetry

---

## Handoff Protocol

Every handoff between agents MUST use this structure:

```markdown
# Handoff: [From Agent] → [To Agent]

## Context Summary
**Project**: [Name]
**Phase**: [Current phase]
**Task**: [What was just completed]
**Status**: PASS | FAIL | PARTIAL

## What Was Done
[Concise summary of work completed — facts only, no spin]

## Key Decisions Made
| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| [Decision] | [Why] | [What else was considered] |

## What You Need to Know
[Critical context the next agent needs — don't make them ask]

## Acceptance Criteria for Your Task
[Explicit, measurable criteria — not "make it good"]

## Known Issues / Risks
[Anything that might affect the next agent's work]

## Evolution Telemetry
**Task Type**: [category]
**Retry Count**: [N]
**Failure Category** (if applicable): [ambiguous_spec | implementation_error | context_loss | scope_creep]
**Notable Patterns**: [anything worth distilling for future runs]
```

---

## Quality Gate Verdicts

The Critic issues one of three verdicts:

| Verdict | Meaning | Next Action |
|---------|---------|------------|
| `PASS` | Meets all acceptance criteria with evidence | Proceed to next task/phase |
| `NEEDS WORK` | Gaps identified — specific fixes required | Return to implementing agent with feedback |
| `BLOCKED` | Fundamental issue that cannot be fixed by revision | Escalate to Conductor — may require phase rollback |

**Default verdict is `NEEDS WORK`.** The Critic must provide specific, evidence-based justification to issue a `PASS`.

---

## Evolution Reporting

At the end of every project (Phase 6 or earlier termination), the Conductor submits a pipeline report to the Evolution Layer:

```markdown
# PRISM Pipeline Evolution Report

## Project Summary
**Mode**: [Full/Sprint/Micro/Explore]
**Duration**: [Actual vs. estimated]
**Final Status**: [SHIPPED / CANCELLED / PAUSED]

## Agent Performance
| Agent | Tasks | First-Pass Rate | Avg Retries | Notable |
|-------|-------|----------------|-------------|---------|
| [slug] | [N] | [%] | [N] | [notes] |

## Bottlenecks Identified
[Agents or phases with highest retry rates or longest durations]

## Patterns Worth Distilling
[Specific decisions or approaches that worked exceptionally well or poorly]

## Recommended Evolution Actions
- [ ] [Agent slug]: [specific improvement suggestion]
- [ ] [Agent slug]: [specific improvement suggestion]
```

---

## Collaboration Graph

PRISM makes agent relationships explicit. The Conductor uses this graph to route tasks and resolve conflicts.

```
Conductor (orchestrates all)
    ├── Planner (upstream of all phases)
    ├── Critic (reviewer of all agents)
    │
    ├── Engineering Division
    │   ├── Backend Architect → Frontend Developer (API contracts)
    │   ├── Backend Architect → DevOps Engineer (deployment specs)
    │   └── Security Engineer → all (security review)
    │
    ├── Product Division
    │   ├── Product Strategist → Backend Architect (requirements)
    │   └── Sprint Planner → Conductor (task sequencing)
    │
    └── Design Division
        ├── UX Architect → Frontend Developer (design specs)
        └── Brand Guardian → UI Designer (brand compliance)
```
