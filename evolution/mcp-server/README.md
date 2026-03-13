# PRISM Evolution MCP Server

The Experience Library exposed as an MCP-compatible tool server. Works with Claude Code, Cursor, Windsurf, and any MCP-compatible AI tool.

## Quick Start (SQLite — zero config)

```bash
# Install dependencies
pip install mcp sqlite3

# Run the server
python server.py
```

## Configure in Claude Code

Add to `~/.claude/mcp_settings.json`:

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

## Configure in Cursor

Add to `.cursor/mcp.json` in your project root:

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

## Available Tools

| Tool | When to Call | Purpose |
|------|-------------|---------|
| `recall_experience` | Task start | Get relevant principles |
| `record_decision` | During task | Log important choices |
| `report_telemetry` | Task end | Report outcome metrics |
| `get_agent_stats` | Anytime | View agent performance |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PRISM_DB_PATH` | `~/.prism/evolution.db` | SQLite database path |
| `PRISM_MIN_CONFIDENCE` | `0.7` | Minimum principle confidence threshold |
| `PRISM_TOP_K` | `5` | Default number of principles to return |
