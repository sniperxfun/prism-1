# PRISM × Cursor Integration

## Setup (5 minutes)

### 1. Add MCP Server

Create `.cursor/mcp.json` in your project root:

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

### 2. Add PRISM Rules

Create `.cursor/rules/prism.mdc`:

```markdown
---
description: PRISM Agent Framework activation rules
globs: ["**/*"]
alwaysApply: false
---

# PRISM Agent Framework

When the user says "activate [agent-name]", find and read the corresponding 
agent file from the `agents/` directory and fully adopt that agent's identity,
personality, Critical Rules, and operating procedures.

When the user says "start PRISM [mode]", activate the Conductor agent and 
begin a PRISM Flow pipeline in the specified mode.

Available agents are in the `agents/` directory organized by division.
```

### 3. Reference agents in Cursor Chat

```
@agents/specialized/conductor.md 
Start a PRISM-Sprint pipeline. Project: [description]
```

## Tips

- Use `@` file references to include agent files in Cursor Chat context
- The MCP server enables automatic experience recall and telemetry
- Add frequently used agents to Cursor's "Always include" rules for persistent activation
