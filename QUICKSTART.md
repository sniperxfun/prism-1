# PRISM Quick Start Guide

Get your first PRISM-powered project running in under 10 minutes.

---

## Step 1: Choose Your Setup

### Minimal Setup (No Installation)
Use PRISM agents directly as prompts in any AI tool. No MCP server required. You get the full agent library and PRISM Flow orchestration — but without the Evolution Layer (agents won't accumulate experience across sessions).

**Best for**: Trying PRISM, solo projects, quick tasks.

### Full Setup (With Evolution)
Install the MCP server to enable the Evolution Layer. Agents accumulate experience, performance is tracked, and the system improves over time.

**Best for**: Team use, ongoing projects, production workflows.

---

## Step 2: Minimal Setup (5 minutes)

### Option A: Claude Code

1. Clone the repo or download the `agents/` folder
2. In Claude Code, reference an agent file directly:

```
Read the file agents/specialized/conductor.md and adopt that agent's identity.
Then help me: [your project description]
```

### Option B: Cursor

Add to `.cursor/rules` in your project:

```
When I say "activate [agent-name]", read the corresponding file from the prism/agents/ 
directory and adopt that agent's identity, personality, and operating procedures.
```

### Option C: Any AI Tool

Copy the contents of any agent file and paste it as a system prompt. The agent's YAML frontmatter and all sections work as a complete system prompt.

---

## Step 3: Full Setup with Evolution (10 minutes)

### Install the MCP Server

```bash
# Clone PRISM
git clone https://github.com/your-org/prism.git
cd prism

# Install Python dependencies
pip install openai

# Test the server
python evolution/mcp-server/server.py --help
```

### Configure Claude Code

Add to `~/.claude/mcp_settings.json`:

```json
{
  "mcpServers": {
    "prism-evolution": {
      "command": "python",
      "args": ["/absolute/path/to/prism/evolution/mcp-server/server.py"],
      "env": {
        "PRISM_DB_PATH": "~/.prism/evolution.db"
      }
    }
  }
}
```

### Configure Cursor

Create `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "prism-evolution": {
      "command": "python",
      "args": ["./evolution/mcp-server/server.py"]
    }
  }
}
```

---

## Step 4: Your First Project

### Example 1: PRISM-Micro (Bug Fix)

```
Activate the Conductor agent from agents/specialized/conductor.md.

Project: Fix the authentication bug in our Express.js API where JWT tokens 
are not being properly validated on the /admin routes.

Use PRISM-Micro mode.
```

The Conductor will:
1. Confirm PRISM-Micro mode (Phases 3–4 only)
2. Activate Backend Architect for the fix
3. Activate Critic for review
4. Activate Security Engineer for auth-specific validation

### Example 2: PRISM-Sprint (New Feature)

```
Activate the Conductor agent from agents/specialized/conductor.md.

Project: Add a user notification system to our SaaS app. Users should receive 
email and in-app notifications for key events (new comment, mention, deadline).
We have a React frontend and Node.js backend.

Use PRISM-Sprint mode. Timeline: 2 weeks.
```

### Example 3: PRISM-Full (New Product)

```
Activate the Conductor agent from agents/specialized/conductor.md.

Project: Build an AI-powered code review tool for GitHub PRs. It should 
automatically review PRs, suggest improvements, and learn from accepted/rejected 
suggestions over time.

Use PRISM-Full mode. Start with Phase 0 Discovery.
```

---

## Step 5: Understanding the Quality Gates

Every PRISM Flow pipeline enforces quality gates between phases. Here is what to expect:

**When the Critic says NEEDS WORK:**
This is normal and expected. The Critic defaults to finding issues. Provide the specific feedback to the implementing agent and retry. Maximum 3 retries before escalation.

**When the Critic says BLOCKED:**
A fundamental issue was found that cannot be fixed by revision. The Conductor will flag this for human review. Do not bypass the gate — investigate the root cause.

**When a phase gate PASSES:**
The Conductor will summarize what was completed, what evidence was provided, and what the next phase will focus on. Review the summary before proceeding.

---

## Step 6: Running the Distillation Engine

After completing several projects, run the distillation engine to extract principles:

```bash
# Distill all agents (requires 5+ decisions per agent)
python evolution/distillation/distill.py

# Distill a specific agent
python evolution/distillation/distill.py --agent backend-architect

# Preview without saving
python evolution/distillation/distill.py --dry-run --verbose
```

---

## Common Patterns

### Activating Multiple Agents Directly

For PRISM-Micro tasks, you can skip the Conductor and activate agents directly:

```
Activate the Backend Architect from agents/engineering/backend-architect.md.
Task: Design the database schema for a multi-tenant SaaS application with 
the following requirements: [requirements]
```

Then:
```
Activate the Critic from agents/specialized/critic.md.
Review the Backend Architect's database schema design above. Apply your 
standard quality assessment. Default to NEEDS WORK.
```

### Using the Handoff Protocol

When passing work between agents, use the handoff format from `core/PRISM-PROTOCOL.md`:

```
# Handoff: Backend Architect → Frontend Developer

## Context Summary
**Project**: [Name]
**Phase**: 3 — Build
**Task**: API contract definition
**Status**: PASS

## What Was Done
[Summary]

## What You Need to Know
[Critical context]

## Acceptance Criteria for Your Task
[Explicit criteria]
```

---

## Troubleshooting

**Agent seems to ignore its Critical Rules**
Ensure the full agent file content (including frontmatter) is included in the system prompt. Some tools truncate long system prompts — check your tool's context limits.

**Evolution Layer not recording data**
Verify the MCP server is running and properly configured. Check `~/.prism/evolution.db` exists after the first task.

**Critic is too harsh / blocking everything**
This is by design. The Critic's default is NEEDS WORK. If you believe a NEEDS WORK verdict is incorrect, provide specific counter-evidence rather than asking the Critic to reconsider.

**Conductor is not activating the right agents**
Ensure you have specified the execution mode (PRISM-Full/Sprint/Micro/Explore). If unspecified, the Conductor defaults to PRISM-Sprint.

---

## Next Steps

- Read [core/PRISM-PROTOCOL.md](core/PRISM-PROTOCOL.md) for the complete orchestration protocol
- Read [core/EVOLUTION-SPEC.md](core/EVOLUTION-SPEC.md) to understand the evolution mechanism
- Browse [agents/](agents/) to see all available agents
- See [examples/](examples/) for complete worked examples
- Read [CONTRIBUTING.md](CONTRIBUTING.md) to add your own agents
