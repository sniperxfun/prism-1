# Example: SaaS MVP with PRISM-Sprint

This example shows a complete PRISM-Sprint pipeline for building a task management SaaS MVP.

## Project Brief

**Goal**: Build a minimal viable product for a team task management tool
**Mode**: PRISM-Sprint (Phases 2–5)
**Timeline**: 2 weeks
**Stack**: Next.js frontend, Node.js/Express backend, PostgreSQL

---

## Activation Prompt

```
Activate the Conductor from agents/specialized/conductor.md.

Project: Build a task management SaaS MVP. Core features:
- User authentication (email/password + Google OAuth)
- Create/edit/delete tasks with title, description, due date, assignee
- Task status: Todo, In Progress, Done
- Team workspaces (invite members by email)
- Basic dashboard showing tasks assigned to me

Stack: Next.js 14 (App Router), Node.js/Express, PostgreSQL, Prisma ORM
Timeline: 2 weeks
Mode: PRISM-Sprint
```

---

## What Happens Next

### Phase 2: Scaffold

The Conductor activates:
- **Backend Architect** → Database schema + API contract
- **DevOps Engineer** → CI/CD pipeline + Docker setup
- **Security Engineer** → Auth architecture review

**Gate**: Critic validates that the repo is runnable in < 5 minutes and the API contract is complete.

### Phase 3: Build

The Conductor runs the Build Loop for each task:

**Task 1**: Backend Architect implements auth endpoints
→ Critic reviews → PASS

**Task 2**: Frontend Developer implements auth UI
→ Critic reviews → NEEDS WORK (missing loading states)
→ Frontend Developer revises → PASS

**Task 3**: Backend Architect implements task CRUD
→ Critic reviews → PASS

**Task 4**: Frontend Developer implements task board
→ Critic reviews → PASS

**Task 5**: Backend Architect implements workspace/team features
→ Critic reviews → NEEDS WORK (missing email validation)
→ Backend Architect revises → PASS

**Gate**: All tasks PASS. Zero P0 issues.

### Phase 4: Harden

- **Security Engineer** → Auth security audit (JWT expiry, CSRF, SQL injection)
- **DevOps Engineer** → Performance baseline, monitoring setup
- **Critic** → Final integration review

**Gate**: Critic certifies READY (not just NEEDS WORK).

### Phase 5: Launch

- **DevOps Engineer** → Deployment runbook + rollback procedure
- **Conductor** → Launch checklist verification

---

## Evolution Telemetry Generated

After this project, the Evolution Layer records:

```
backend-architect: 3 tasks, 100% first-pass rate
  → Principle extracted: "For multi-tenant SaaS, always implement row-level security 
    at the database level, not just application level"

frontend-developer: 2 tasks, 50% first-pass rate  
  → Pattern noted: Loading states are a recurring miss
  → L1 context injection added for future tasks

security-engineer: 1 task, 100% first-pass rate
  → Principle extracted: "JWT refresh token rotation should be implemented 
    from day one — retrofitting is a security risk"
```

The next time these agents work on a SaaS project, they'll have these principles injected automatically.
