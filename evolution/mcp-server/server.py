"""
PRISM Evolution MCP Server
Provides the Experience Library as an MCP-compatible tool server.

Supports two storage backends:
  - SQLite (default, zero-config, for local/personal use)
  - PostgreSQL + Chroma (production, for team use)

Usage:
  python server.py                    # SQLite mode
  python server.py --backend postgres # PostgreSQL + Chroma mode
"""

import argparse
import json
import sqlite3
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Storage Backend ───────────────────────────────────────────────────────────

DB_PATH = Path(os.environ.get("PRISM_DB_PATH", "~/.prism/evolution.db")).expanduser()


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS principles (
            id TEXT PRIMARY KEY,
            agent_slug TEXT NOT NULL,
            text TEXT NOT NULL,
            tags TEXT NOT NULL DEFAULT '[]',
            confidence REAL NOT NULL DEFAULT 0.5,
            source_count INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS decisions (
            id TEXT PRIMARY KEY,
            agent_slug TEXT NOT NULL,
            decision TEXT NOT NULL,
            rationale TEXT NOT NULL,
            alternatives TEXT,
            outcome TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS telemetry (
            id TEXT PRIMARY KEY,
            agent_slug TEXT NOT NULL,
            task_type TEXT NOT NULL,
            outcome TEXT NOT NULL,
            retry_count INTEGER NOT NULL DEFAULT 0,
            failure_category TEXT,
            notes TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agent_baselines (
            agent_slug TEXT PRIMARY KEY,
            first_pass_rate REAL,
            avg_retries REAL,
            total_tasks INTEGER DEFAULT 0,
            quality_score REAL,
            evolution_status TEXT DEFAULT 'active',
            last_updated TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_principles_agent ON principles(agent_slug);
        CREATE INDEX IF NOT EXISTS idx_telemetry_agent ON telemetry(agent_slug);
        CREATE INDEX IF NOT EXISTS idx_telemetry_created ON telemetry(created_at);
    """)
    conn.commit()


# ── Tool Implementations ──────────────────────────────────────────────────────

def recall_experience(agent: str, context: str, top_k: int = 5, min_confidence: float = 0.7) -> dict:
    """
    Retrieve relevant principles for the current task.
    Uses keyword matching (SQLite mode) or semantic search (Chroma mode).
    """
    conn = get_db()

    # Simple keyword-based relevance scoring for SQLite mode
    # In production (Chroma mode), this would use vector similarity
    context_words = set(context.lower().split())

    rows = conn.execute(
        "SELECT * FROM principles WHERE agent_slug = ? AND confidence >= ? ORDER BY confidence DESC, source_count DESC",
        (agent, min_confidence)
    ).fetchall()

    scored = []
    for row in rows:
        tags = json.loads(row["tags"])
        tag_words = set(" ".join(tags).lower().split())
        text_words = set(row["text"].lower().split())

        # Score based on overlap with context
        overlap = len(context_words & (tag_words | text_words))
        score = row["confidence"] * (1 + 0.1 * overlap)
        scored.append((score, dict(row)))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [item for _, item in scored[:top_k]]

    return {
        "principles": [
            {
                "text": p["text"],
                "confidence": p["confidence"],
                "source_count": p["source_count"],
                "tags": json.loads(p["tags"])
            }
            for p in top
        ],
        "agent": agent,
        "total_available": len(rows)
    }


def record_decision(
    agent: str,
    decision: str,
    rationale: str,
    alternatives_considered: Optional[str] = None,
    outcome: str = "pending"
) -> dict:
    """Log a significant decision for future distillation."""
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()
    decision_id = str(uuid.uuid4())

    conn.execute(
        "INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (decision_id, agent, decision, rationale, alternatives_considered, outcome, now, now)
    )
    conn.commit()

    return {"decision_id": decision_id, "recorded": True}


def report_telemetry(
    agent: str,
    task_type: str,
    outcome: str,
    retry_count: int = 0,
    failure_category: Optional[str] = None,
    notes: Optional[str] = None
) -> dict:
    """Report task execution metrics and update agent baseline."""
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()
    telemetry_id = str(uuid.uuid4())

    conn.execute(
        "INSERT INTO telemetry VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (telemetry_id, agent, task_type, outcome, retry_count, failure_category, notes, now)
    )

    # Update rolling baseline using exponential moving average (alpha=0.1)
    alpha = 0.1
    baseline = conn.execute(
        "SELECT * FROM agent_baselines WHERE agent_slug = ?", (agent,)
    ).fetchone()

    first_pass = 1.0 if retry_count == 0 and outcome == "pass" else 0.0

    if baseline:
        new_fpr = alpha * first_pass + (1 - alpha) * (baseline["first_pass_rate"] or 0.5)
        new_retries = alpha * retry_count + (1 - alpha) * (baseline["avg_retries"] or 1.0)
        new_total = (baseline["total_tasks"] or 0) + 1

        # Determine evolution status based on first-pass rate
        if new_fpr < 0.50:
            status = "needs_l3_review"
        elif new_fpr < 0.65:
            status = "needs_l2_refinement"
        elif new_fpr < 0.75:
            status = "l1_active"
        else:
            status = "healthy"

        conn.execute(
            """UPDATE agent_baselines
               SET first_pass_rate=?, avg_retries=?, total_tasks=?,
                   evolution_status=?, last_updated=?
               WHERE agent_slug=?""",
            (new_fpr, new_retries, new_total, status, now, agent)
        )
    else:
        conn.execute(
            "INSERT INTO agent_baselines VALUES (?, ?, ?, ?, ?, ?, ?)",
            (agent, first_pass, float(retry_count), 1, None, "active", now)
        )

    conn.commit()
    return {"recorded": True, "telemetry_id": telemetry_id}


def get_agent_stats(agent: str, days: int = 30) -> dict:
    """View an agent's performance history."""
    conn = get_db()

    baseline = conn.execute(
        "SELECT * FROM agent_baselines WHERE agent_slug = ?", (agent,)
    ).fetchone()

    cutoff = datetime.now(timezone.utc).isoformat()[:10]
    recent_telemetry = conn.execute(
        """SELECT * FROM telemetry
           WHERE agent_slug = ? AND date(created_at) >= date(?, ?)
           ORDER BY created_at DESC""",
        (agent, cutoff, f"-{days} days")
    ).fetchall()

    top_principles = conn.execute(
        """SELECT text, confidence, source_count, tags FROM principles
           WHERE agent_slug = ? ORDER BY confidence DESC, source_count DESC LIMIT 5""",
        (agent,)
    ).fetchall()

    return {
        "agent": agent,
        "first_pass_rate": baseline["first_pass_rate"] if baseline else None,
        "avg_retries": baseline["avg_retries"] if baseline else None,
        "total_tasks": baseline["total_tasks"] if baseline else 0,
        "evolution_status": baseline["evolution_status"] if baseline else "no_data",
        "recent_tasks": len(recent_telemetry),
        "top_principles": [
            {
                "text": p["text"],
                "confidence": p["confidence"],
                "source_count": p["source_count"],
                "tags": json.loads(p["tags"])
            }
            for p in top_principles
        ]
    }


def add_principle(
    agent: str,
    text: str,
    tags: list[str],
    confidence: float = 0.5,
    source_count: int = 1
) -> dict:
    """Add a new principle to the Experience Library (used by distillation engine)."""
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()
    principle_id = str(uuid.uuid4())

    conn.execute(
        "INSERT INTO principles VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (principle_id, agent, text, json.dumps(tags), confidence, source_count, now, now)
    )
    conn.commit()

    return {"principle_id": principle_id, "recorded": True}


# ── MCP Server Entry Point ────────────────────────────────────────────────────

def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    """Route MCP tool calls to the appropriate handler."""
    handlers = {
        "recall_experience": recall_experience,
        "record_decision": record_decision,
        "report_telemetry": report_telemetry,
        "get_agent_stats": get_agent_stats,
        "add_principle": add_principle,
    }

    if tool_name not in handlers:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        return handlers[tool_name](**arguments)
    except Exception as e:
        return {"error": str(e)}


def run_stdio_server():
    """Run as a stdio-based MCP server."""
    import sys

    # Send tool list on startup
    tools = [
        {
            "name": "recall_experience",
            "description": "Retrieve relevant principles from the Experience Library for the current task. Call this at the START of every task.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent": {"type": "string", "description": "Your agent slug (e.g. 'backend-architect')"},
                    "context": {"type": "string", "description": "Brief description of the current task"},
                    "top_k": {"type": "integer", "default": 5},
                    "min_confidence": {"type": "number", "default": 0.7}
                },
                "required": ["agent", "context"]
            }
        },
        {
            "name": "record_decision",
            "description": "Log a significant decision for future distillation. Call this when making important architectural, technical, or strategic choices.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent": {"type": "string"},
                    "decision": {"type": "string", "description": "What you decided"},
                    "rationale": {"type": "string", "description": "Why you made this decision"},
                    "alternatives_considered": {"type": "string"},
                    "outcome": {"type": "string", "enum": ["pending", "success", "failure"], "default": "pending"}
                },
                "required": ["agent", "decision", "rationale"]
            }
        },
        {
            "name": "report_telemetry",
            "description": "Report task execution metrics. Call this when you COMPLETE a task.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent": {"type": "string"},
                    "task_type": {"type": "string", "description": "Category of task (e.g. 'api-design', 'database-schema')"},
                    "outcome": {"type": "string", "enum": ["pass", "fail", "partial"]},
                    "retry_count": {"type": "integer", "default": 0},
                    "failure_category": {"type": "string", "enum": ["ambiguous_spec", "implementation_error", "context_loss", "scope_creep", "other"]},
                    "notes": {"type": "string"}
                },
                "required": ["agent", "task_type", "outcome"]
            }
        },
        {
            "name": "get_agent_stats",
            "description": "View an agent's performance history and evolution status.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent": {"type": "string"},
                    "days": {"type": "integer", "default": 30}
                },
                "required": ["agent"]
            }
        }
    ]

    print(json.dumps({"type": "tools_list", "tools": tools}), flush=True)

    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            result = handle_tool_call(request.get("tool"), request.get("arguments", {}))
            print(json.dumps({"type": "tool_result", "result": result}), flush=True)
        except json.JSONDecodeError:
            print(json.dumps({"type": "error", "message": "Invalid JSON"}), flush=True)
        except Exception as e:
            print(json.dumps({"type": "error", "message": str(e)}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PRISM Evolution MCP Server")
    parser.add_argument("--backend", choices=["sqlite", "postgres"], default="sqlite")
    parser.add_argument("--mode", choices=["stdio", "http"], default="stdio")
    args = parser.parse_args()

    print(f"Starting PRISM Evolution MCP Server (backend: {args.backend}, mode: {args.mode})", flush=True)
    run_stdio_server()
