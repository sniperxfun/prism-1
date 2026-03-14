"""
PRISM Evolution Layer

Provides the self-improvement infrastructure: experience library,
distillation engine, drift detection, and agent performance monitoring.
"""

import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..config import EvolutionConfig, PRISM_DB_PATH


# ── Experience Library ───────────────────────────────────────────────────────

class ExperienceLibrary:
    """
    Persistent storage for agent principles, decisions, and telemetry.
    Supports SQLite (local) backend. Production deployments can extend
    with PostgreSQL + vector search.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or PRISM_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None
        self._init_schema()

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_schema(self):
        self.conn.executescript("""
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
        self.conn.commit()

    def recall(self, agent: str, context: str, top_k: int = 5, min_confidence: float = 0.7) -> list[dict]:
        """Retrieve relevant principles for a task context."""
        context_words = set(context.lower().split())
        rows = self.conn.execute(
            "SELECT * FROM principles WHERE agent_slug = ? AND confidence >= ? ORDER BY confidence DESC",
            (agent, min_confidence)
        ).fetchall()

        scored = []
        for row in rows:
            tags = json.loads(row["tags"])
            tag_words = set(" ".join(tags).lower().split())
            text_words = set(row["text"].lower().split())
            overlap = len(context_words & (tag_words | text_words))
            score = row["confidence"] * (1 + 0.1 * overlap)
            scored.append((score, dict(row)))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"text": p["text"], "confidence": p["confidence"], "tags": json.loads(p["tags"])}
            for _, p in scored[:top_k]
        ]

    def record_decision(self, agent: str, decision: str, rationale: str,
                        alternatives: Optional[str] = None, outcome: str = "pending") -> str:
        """Log a significant decision."""
        now = datetime.now(timezone.utc).isoformat()
        decision_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (decision_id, agent, decision, rationale, alternatives, outcome, now, now)
        )
        self.conn.commit()
        return decision_id

    def report_telemetry(self, agent: str, task_type: str, outcome: str,
                         retry_count: int = 0, failure_category: Optional[str] = None,
                         notes: Optional[str] = None, config: Optional[EvolutionConfig] = None) -> str:
        """Report task execution metrics and update agent baseline."""
        cfg = config or EvolutionConfig()
        now = datetime.now(timezone.utc).isoformat()
        telemetry_id = str(uuid.uuid4())

        self.conn.execute(
            "INSERT INTO telemetry VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (telemetry_id, agent, task_type, outcome, retry_count, failure_category, notes, now)
        )

        alpha = cfg.ema_alpha
        baseline = self.conn.execute(
            "SELECT * FROM agent_baselines WHERE agent_slug = ?", (agent,)
        ).fetchone()

        first_pass = 1.0 if retry_count == 0 and outcome == "pass" else 0.0

        if baseline:
            new_fpr = alpha * first_pass + (1 - alpha) * (baseline["first_pass_rate"] or 0.5)
            new_retries = alpha * retry_count + (1 - alpha) * (baseline["avg_retries"] or 1.0)
            new_total = (baseline["total_tasks"] or 0) + 1

            if new_fpr < cfg.l3_trigger_threshold:
                status = "needs_l3_review"
            elif new_fpr < cfg.l2_trigger_threshold:
                status = "needs_l2_refinement"
            elif new_fpr < 0.75:
                status = "l1_active"
            else:
                status = "healthy"

            self.conn.execute(
                """UPDATE agent_baselines
                   SET first_pass_rate=?, avg_retries=?, total_tasks=?,
                       evolution_status=?, last_updated=?
                   WHERE agent_slug=?""",
                (new_fpr, new_retries, new_total, status, now, agent)
            )
        else:
            self.conn.execute(
                "INSERT INTO agent_baselines VALUES (?, ?, ?, ?, ?, ?, ?)",
                (agent, first_pass, float(retry_count), 1, None, "active", now)
            )

        self.conn.commit()
        return telemetry_id

    def add_principle(self, agent: str, text: str, tags: list[str],
                      confidence: float = 0.5, source_count: int = 1) -> str:
        """Add a new principle to the library."""
        now = datetime.now(timezone.utc).isoformat()
        principle_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO principles VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (principle_id, agent, text, json.dumps(tags), confidence, source_count, now, now)
        )
        self.conn.commit()
        return principle_id

    def get_agent_stats(self, agent: str) -> dict:
        """Get performance statistics for an agent."""
        baseline = self.conn.execute(
            "SELECT * FROM agent_baselines WHERE agent_slug = ?", (agent,)
        ).fetchone()

        principles = self.conn.execute(
            "SELECT COUNT(*) as cnt FROM principles WHERE agent_slug = ?", (agent,)
        ).fetchone()

        decisions = self.conn.execute(
            "SELECT COUNT(*) as cnt FROM decisions WHERE agent_slug = ?", (agent,)
        ).fetchone()

        return {
            "agent": agent,
            "first_pass_rate": baseline["first_pass_rate"] if baseline else None,
            "avg_retries": baseline["avg_retries"] if baseline else None,
            "total_tasks": baseline["total_tasks"] if baseline else 0,
            "evolution_status": baseline["evolution_status"] if baseline else "no_data",
            "total_principles": principles["cnt"],
            "total_decisions": decisions["cnt"],
        }

    def get_all_agent_stats(self) -> list[dict]:
        """Get performance statistics for all agents."""
        rows = self.conn.execute("SELECT * FROM agent_baselines ORDER BY agent_slug").fetchall()
        return [dict(r) for r in rows]

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None


# ── Drift Detector ───────────────────────────────────────────────────────────

@dataclass
class DriftAlert:
    """An alert generated when agent performance drifts below thresholds."""
    agent_slug: str
    metric: str
    current_value: float
    threshold: float
    recommended_action: str
    severity: str  # warning | critical


class DriftDetector:
    """Monitors agent performance and generates drift alerts."""

    def __init__(self, library: ExperienceLibrary, config: Optional[EvolutionConfig] = None):
        self.library = library
        self.config = config or EvolutionConfig()

    def check_all(self) -> list[DriftAlert]:
        """Check all agents for performance drift."""
        alerts = []
        stats = self.library.get_all_agent_stats()

        for agent_stat in stats:
            fpr = agent_stat.get("first_pass_rate")
            if fpr is None:
                continue

            total = agent_stat.get("total_tasks", 0)
            if total < 5:
                continue  # Not enough data

            slug = agent_stat["agent_slug"]

            if fpr < self.config.l3_trigger_threshold:
                alerts.append(DriftAlert(
                    agent_slug=slug,
                    metric="first_pass_rate",
                    current_value=fpr,
                    threshold=self.config.l3_trigger_threshold,
                    recommended_action="L3 Agent Reconstruction recommended",
                    severity="critical",
                ))
            elif fpr < self.config.l2_trigger_threshold:
                alerts.append(DriftAlert(
                    agent_slug=slug,
                    metric="first_pass_rate",
                    current_value=fpr,
                    threshold=self.config.l2_trigger_threshold,
                    recommended_action="L2 Prompt Refinement recommended",
                    severity="warning",
                ))

        return alerts
