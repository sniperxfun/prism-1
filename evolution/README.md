# PRISM Evolution Layer

The Evolution Layer is the self-improvement engine of PRISM. It consists of four components that work together to make agents better over time.

## Components

### MCP Server (`mcp-server/`)
Exposes the Experience Library as MCP tools. Agents call these tools automatically during task execution to recall relevant principles and log decisions.

**Setup**: See [mcp-server/README.md](mcp-server/README.md)

### Distillation Engine (`distillation/`)
Analyzes accumulated decisions and telemetry to extract reusable principles. Run periodically (weekly or after every 10 projects).

```bash
python distillation/distill.py --verbose
```

### LLM-as-Judge (`judge/`)
Evaluates proposed L2 prompt improvements against a test suite. Used to gate L2 pull requests — a proposed improvement must show ≥ 5% quality improvement to be approved.

```bash
python judge/judge.py --agent backend-architect \
  --old agents/engineering/backend-architect.md \
  --new proposed/backend-architect-v2.md \
  --test-suite judge/tests/backend-architect.json
```

### Telemetry (`telemetry/`)
Utilities for viewing and analyzing agent performance data.

```bash
# View all agent stats
python telemetry/stats.py

# View specific agent
python telemetry/stats.py --agent backend-architect --days 30
```

## Evolution Levels

| Level | What Changes | Trigger | Approval |
|-------|-------------|---------|---------|
| L1 | Runtime context only | Every task | None |
| L2 | Agent prompt file | First-pass rate < 65% | Human review |
| L3 | Agent identity/mission | First-pass rate < 50% for 30 days | Expert review |

## Data Storage

By default, all evolution data is stored in `~/.prism/evolution.db` (SQLite).

For team use, configure PostgreSQL:
```bash
export PRISM_DB_URL="postgresql://user:pass@host/prism_evolution"
python mcp-server/server.py --backend postgres
```
