# PRISM × Claude Code Integration

## Setup (5 minutes)

### 1. Add MCP Server

Edit `~/.claude/mcp_settings.json`:

```json
{
  "mcpServers": {
    "prism-evolution": {
      "command": "python",
      "args": ["/path/to/prism/evolution/mcp-server/server.py"],
      "env": {
        "PRISM_DB_PATH": "~/.prism/evolution.db"
      }
    }
  }
}
```

### 2. Add PRISM to your project

```bash
# Option A: Clone into your project
git submodule add https://github.com/prism-agentic/prism.git .prism

# Option B: Clone separately and reference by path
git clone https://github.com/prism-agentic/prism.git ~/prism
```

### 3. Create a CLAUDE.md in your project root

```markdown
# PRISM Agent Framework

This project uses PRISM agents for AI-assisted development.
Agent files are located in `.prism/agents/` (or `~/prism/agents/`).

## Activating Agents
To activate an agent: "Read [agent-file-path] and adopt that agent's identity."

## Starting a PRISM Flow
To start a pipeline: "Activate the Conductor from .prism/agents/specialized/conductor.md. 
Project: [description]. Use PRISM-[Full/Sprint/Micro/Explore] mode."
```

## Usage Examples

### Start a PRISM-Sprint pipeline
```
Activate the Conductor from .prism/agents/specialized/conductor.md.
I need to add Stripe payment integration to our Next.js SaaS app.
Use PRISM-Sprint mode. We have 1 week.
```

### Direct agent activation
```
Read .prism/agents/engineering/backend-architect.md and adopt that identity.
Design the database schema for: [requirements]
```

### Run quality review
```
Read .prism/agents/specialized/critic.md and adopt that identity.
Review the following implementation: [paste code/design]
Default to NEEDS WORK. Provide evidence-based assessment.
```

## Tips

- Reference agent files by path — Claude Code reads them automatically
- The Evolution MCP tools (`recall_experience`, `record_decision`, `report_telemetry`) 
  are called automatically by agents when the MCP server is configured
- Use `/clear` between major phase transitions to keep context focused
