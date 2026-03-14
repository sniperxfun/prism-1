"""
PRISM Flow — Adaptive Orchestration Engine

Implements the four execution modes (Full, Sprint, Micro, Explore) and
manages phase transitions, quality gates, and agent activation sequences.
"""

import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

from ..agents import Agent, find_agent


# ── Execution Modes ──────────────────────────────────────────────────────────

class ExecutionMode(str, Enum):
    FULL = "full"        # 6 phases, 20-40 agents
    SPRINT = "sprint"    # 4 phases, 8-15 agents
    MICRO = "micro"      # 2 phases, 3-6 agents
    EXPLORE = "explore"  # 2 phases, 3-5 agents


class PhaseStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PASSED = "passed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    PASSED = "passed"
    NEEDS_WORK = "needs_work"
    BLOCKED = "blocked"


class CriticVerdict(str, Enum):
    PASS = "PASS"
    NEEDS_WORK = "NEEDS_WORK"
    BLOCKED = "BLOCKED"


# ── Phase Definitions ────────────────────────────────────────────────────────

PHASE_DEFINITIONS = {
    0: {"name": "Discover", "description": "Requirements gathering, stakeholder analysis, feasibility"},
    1: {"name": "Strategize", "description": "Architecture, tech stack, project plan, risk assessment"},
    2: {"name": "Scaffold", "description": "Project setup, CI/CD, base infrastructure"},
    3: {"name": "Build", "description": "Core implementation, feature development"},
    4: {"name": "Harden", "description": "Security audit, performance optimization, testing"},
    5: {"name": "Launch", "description": "Deployment, monitoring, documentation, handoff"},
}

MODE_PHASES = {
    ExecutionMode.FULL: [0, 1, 2, 3, 4, 5],
    ExecutionMode.SPRINT: [1, 2, 3, 4],
    ExecutionMode.MICRO: [3, 4],
    ExecutionMode.EXPLORE: [0, 1],
}

MODE_AGENT_RANGE = {
    ExecutionMode.FULL: (20, 40),
    ExecutionMode.SPRINT: (8, 15),
    ExecutionMode.MICRO: (3, 6),
    ExecutionMode.EXPLORE: (3, 5),
}


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class Task:
    """A unit of work assigned to an agent within a phase."""
    id: str
    phase_id: int
    agent_slug: str
    description: str
    acceptance_criteria: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    critic_feedback: list[str] = field(default_factory=list)
    handoff_to: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    @property
    def is_terminal(self) -> bool:
        return self.status in (TaskStatus.PASSED, TaskStatus.BLOCKED)


@dataclass
class Phase:
    """A phase in the PRISM Flow pipeline."""
    id: int
    name: str
    description: str
    status: PhaseStatus = PhaseStatus.PENDING
    tasks: list[Task] = field(default_factory=list)
    gate_passed: bool = False
    gate_evidence: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    @property
    def all_tasks_complete(self) -> bool:
        return all(t.is_terminal for t in self.tasks) if self.tasks else False

    @property
    def has_blocked_tasks(self) -> bool:
        return any(t.status == TaskStatus.BLOCKED for t in self.tasks)


@dataclass
class Risk:
    """A risk entry in the pipeline risk register."""
    id: str
    description: str
    severity: str  # P0 | P1 | P2 | P3
    probability: str  # high | medium | low
    mitigation: str
    status: str = "open"  # open | mitigated | accepted | closed


@dataclass
class Pipeline:
    """A complete PRISM Flow pipeline instance."""
    id: str
    project_name: str
    mode: ExecutionMode
    phases: list[Phase] = field(default_factory=list)
    risks: list[Risk] = field(default_factory=list)
    agent_roster: dict[str, str] = field(default_factory=dict)  # slug -> role
    success_metrics: list[str] = field(default_factory=list)
    current_phase_id: int = 0
    status: str = "initialized"  # initialized | running | completed | failed | aborted
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None

    @property
    def current_phase(self) -> Optional[Phase]:
        for phase in self.phases:
            if phase.id == self.current_phase_id:
                return phase
        return None

    @property
    def progress_pct(self) -> float:
        if not self.phases:
            return 0.0
        passed = sum(1 for p in self.phases if p.status == PhaseStatus.PASSED)
        return (passed / len(self.phases)) * 100

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: Path):
        """Save pipeline state to JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    @classmethod
    def load(cls, path: Path) -> "Pipeline":
        """Load pipeline state from JSON."""
        with open(path) as f:
            data = json.load(f)
        pipeline = cls(
            id=data["id"],
            project_name=data["project_name"],
            mode=ExecutionMode(data["mode"]),
            status=data.get("status", "initialized"),
            current_phase_id=data.get("current_phase_id", 0),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at"),
            success_metrics=data.get("success_metrics", []),
            agent_roster=data.get("agent_roster", {}),
        )
        for pd in data.get("phases", []):
            tasks = [Task(**t) for t in pd.get("tasks", [])]
            phase = Phase(
                id=pd["id"], name=pd["name"], description=pd["description"],
                status=PhaseStatus(pd.get("status", "pending")),
                tasks=tasks, gate_passed=pd.get("gate_passed", False),
                gate_evidence=pd.get("gate_evidence"),
                started_at=pd.get("started_at"), completed_at=pd.get("completed_at"),
            )
            pipeline.phases.append(phase)
        for rd in data.get("risks", []):
            pipeline.risks.append(Risk(**rd))
        return pipeline


# ── Flow Engine ──────────────────────────────────────────────────────────────

class FlowEngine:
    """
    The PRISM Flow orchestration engine.

    Manages pipeline lifecycle: initialization, phase transitions,
    task assignment, quality gates, and evolution reporting.
    """

    def __init__(self, agents: list[Agent], config: Optional[dict] = None):
        self.agents = agents
        self.config = config or {}
        self.max_retries = self.config.get("max_retries", 3)

    def classify_mode(self, description: str, scope_hint: Optional[str] = None) -> ExecutionMode:
        """
        Classify the appropriate execution mode based on project description.

        Uses keyword heuristics; in production, the Conductor agent would
        make this decision with LLM reasoning.
        """
        desc_lower = description.lower()

        # Explicit hints
        if scope_hint:
            hint = scope_hint.lower()
            if hint in ("full", "sprint", "micro", "explore"):
                return ExecutionMode(hint)

        # Keyword-based classification
        explore_keywords = ["research", "feasibility", "explore", "investigate", "poc", "prototype", "spike"]
        micro_keywords = ["bug", "fix", "patch", "hotfix", "typo", "small", "minor", "tweak"]
        sprint_keywords = ["feature", "add", "implement", "update", "improve", "enhance", "refactor"]
        full_keywords = ["new product", "mvp", "launch", "platform", "rebuild", "rewrite", "migration"]

        if any(kw in desc_lower for kw in full_keywords):
            return ExecutionMode.FULL
        if any(kw in desc_lower for kw in explore_keywords):
            return ExecutionMode.EXPLORE
        if any(kw in desc_lower for kw in micro_keywords):
            return ExecutionMode.MICRO
        if any(kw in desc_lower for kw in sprint_keywords):
            return ExecutionMode.SPRINT

        return ExecutionMode.SPRINT  # Default

    def create_pipeline(
        self,
        project_name: str,
        description: str,
        mode: Optional[ExecutionMode] = None,
    ) -> Pipeline:
        """Create and initialize a new pipeline."""
        import uuid

        if mode is None:
            mode = self.classify_mode(description)

        pipeline_id = f"pipe-{uuid.uuid4().hex[:8]}"
        pipeline = Pipeline(
            id=pipeline_id,
            project_name=project_name,
            mode=mode,
        )

        # Create phases based on mode
        phase_ids = MODE_PHASES[mode]
        for pid in phase_ids:
            phase_def = PHASE_DEFINITIONS[pid]
            phase = Phase(
                id=pid,
                name=phase_def["name"],
                description=phase_def["description"],
            )
            pipeline.phases.append(phase)

        # Set initial phase
        if pipeline.phases:
            pipeline.current_phase_id = pipeline.phases[0].id
            pipeline.phases[0].status = PhaseStatus.ACTIVE
            pipeline.phases[0].started_at = datetime.now(timezone.utc).isoformat()

        pipeline.status = "running"
        return pipeline

    def add_task(self, pipeline: Pipeline, phase_id: int, task: Task) -> Pipeline:
        """Add a task to a phase in the pipeline."""
        for phase in pipeline.phases:
            if phase.id == phase_id:
                phase.tasks.append(task)
                break
        return pipeline

    def submit_review(
        self,
        pipeline: Pipeline,
        task_id: str,
        verdict: CriticVerdict,
        feedback: str = "",
    ) -> Pipeline:
        """Submit a critic review for a task."""
        for phase in pipeline.phases:
            for task in phase.tasks:
                if task.id == task_id:
                    if verdict == CriticVerdict.PASS:
                        task.status = TaskStatus.PASSED
                        task.completed_at = datetime.now(timezone.utc).isoformat()
                    elif verdict == CriticVerdict.NEEDS_WORK:
                        task.retry_count += 1
                        task.critic_feedback.append(feedback)
                        if task.retry_count >= task.max_retries:
                            task.status = TaskStatus.BLOCKED
                        else:
                            task.status = TaskStatus.NEEDS_WORK
                    elif verdict == CriticVerdict.BLOCKED:
                        task.status = TaskStatus.BLOCKED
                    break
        return pipeline

    def try_advance_phase(self, pipeline: Pipeline) -> tuple[Pipeline, bool]:
        """
        Attempt to advance to the next phase.
        Returns (pipeline, advanced: bool).
        """
        current = pipeline.current_phase
        if current is None:
            return pipeline, False

        if not current.all_tasks_complete:
            return pipeline, False

        if current.has_blocked_tasks:
            current.status = PhaseStatus.BLOCKED
            return pipeline, False

        # Gate passed
        current.status = PhaseStatus.PASSED
        current.gate_passed = True
        current.completed_at = datetime.now(timezone.utc).isoformat()

        # Find next phase
        phase_ids = [p.id for p in pipeline.phases]
        current_idx = phase_ids.index(current.id)
        if current_idx + 1 < len(phase_ids):
            next_phase = pipeline.phases[current_idx + 1]
            next_phase.status = PhaseStatus.ACTIVE
            next_phase.started_at = datetime.now(timezone.utc).isoformat()
            pipeline.current_phase_id = next_phase.id
            return pipeline, True
        else:
            # Pipeline complete
            pipeline.status = "completed"
            pipeline.completed_at = datetime.now(timezone.utc).isoformat()
            return pipeline, True

    def generate_report(self, pipeline: Pipeline) -> str:
        """Generate a Pipeline Status Report in Markdown."""
        lines = [
            f"# Pipeline Status Report",
            f"",
            f"**Project**: {pipeline.project_name}",
            f"**Pipeline ID**: {pipeline.id}",
            f"**Mode**: PRISM-{pipeline.mode.value.capitalize()}",
            f"**Status**: {pipeline.status}",
            f"**Progress**: {pipeline.progress_pct:.0f}%",
            f"**Created**: {pipeline.created_at}",
            f"",
            f"## Phases",
            f"",
            f"| Phase | Name | Status | Tasks | Gate |",
            f"|-------|------|--------|-------|------|",
        ]

        for phase in pipeline.phases:
            total = len(phase.tasks)
            passed = sum(1 for t in phase.tasks if t.status == TaskStatus.PASSED)
            gate = "PASSED" if phase.gate_passed else "-"
            lines.append(
                f"| {phase.id} | {phase.name} | {phase.status.value} | {passed}/{total} | {gate} |"
            )

        if pipeline.risks:
            lines.extend([
                f"",
                f"## Risk Register",
                f"",
                f"| Risk | Severity | Status |",
                f"|------|----------|--------|",
            ])
            for risk in pipeline.risks:
                lines.append(f"| {risk.description} | {risk.severity} | {risk.status} |")

        return "\n".join(lines)
