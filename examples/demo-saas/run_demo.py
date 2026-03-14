#!/usr/bin/env python3
"""
PRISM Demo — SaaS MVP Pipeline Simulation

Demonstrates the full PRISM Flow lifecycle:
1. Load agents from the agent library
2. Create a pipeline with automatic mode selection
3. Assign tasks to agents across phases
4. Simulate critic reviews with pass/fail outcomes
5. Advance through quality gates
6. Report telemetry to the evolution layer
7. Run drift detection

Usage:
  cd examples/demo-saas
  python run_demo.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from prism import __version__
from prism.agents import discover_agents, find_agent, agents_by_division
from prism.flow import FlowEngine, ExecutionMode, Task, CriticVerdict
from prism.evolution import ExperienceLibrary, DriftDetector
from prism.config import PrismConfig

# ── Formatting ───────────────────────────────────────────────────────────────

def header(text: str):
    print(f"\n{'='*60}")
    print(f"  PRISM v{__version__} | {text}")
    print(f"{'='*60}\n")

def step(n: int, text: str):
    print(f"  [{n}] {text}")

def ok(text: str):
    print(f"      ✓ {text}")

def info(text: str):
    print(f"      → {text}")


# ── Demo ─────────────────────────────────────────────────────────────────────

def main():
    header("SaaS MVP Pipeline Demo")

    # Step 1: Load agents
    step(1, "Loading agent library...")
    agents_dir = Path(__file__).parent.parent.parent / "agents"
    agents = discover_agents(agents_dir)
    divisions = agents_by_division(agents)
    ok(f"Loaded {len(agents)} agents across {len(divisions)} divisions")
    for div, div_agents in sorted(divisions.items()):
        info(f"{div}: {', '.join(a.slug for a in div_agents)}")

    # Step 2: Initialize evolution library
    step(2, "Initializing evolution library (in-memory)...")
    import tempfile
    db_path = Path(tempfile.mkdtemp()) / "demo_evolution.db"
    library = ExperienceLibrary(db_path=db_path)
    ok("Evolution library ready")

    # Seed some principles
    library.add_principle(
        "backend-architect",
        "Always use connection pooling for PostgreSQL in high-traffic services",
        ["database", "performance", "postgresql"],
        confidence=0.9,
    )
    library.add_principle(
        "frontend-developer",
        "Use React Server Components for data-heavy pages to reduce client bundle size",
        ["react", "performance", "ssr"],
        confidence=0.85,
    )
    library.add_principle(
        "security-engineer",
        "Implement rate limiting on all authentication endpoints from day one",
        ["security", "auth", "rate-limiting"],
        confidence=0.95,
    )
    ok("Seeded 3 experience principles")

    # Step 3: Recall experience
    step(3, "Recalling experience for backend-architect...")
    principles = library.recall(
        agent="backend-architect",
        context="Design a REST API with PostgreSQL database for a SaaS product",
        min_confidence=0.5,
    )
    for p in principles:
        info(f"[{p['confidence']:.0%}] {p['text'][:70]}...")

    # Step 4: Create pipeline
    step(4, "Creating pipeline with automatic mode selection...")
    engine = FlowEngine(agents)
    pipeline = engine.create_pipeline(
        project_name="TaskFlow SaaS MVP",
        description="Build a new SaaS MVP for project management with real-time collaboration",
    )
    ok(f"Pipeline {pipeline.id} created in PRISM-{pipeline.mode.value.capitalize()} mode")
    ok(f"{len(pipeline.phases)} phases planned")

    # Step 5: Assign tasks to Phase 0 (Discover)
    step(5, "Assigning tasks to Phase 0 (Discover)...")
    discover_tasks = [
        Task(
            id="T-001", phase_id=0, agent_slug="planner",
            description="Conduct stakeholder analysis and define project scope",
            acceptance_criteria=["Stakeholder map", "Scope document", "Risk assessment"],
        ),
        Task(
            id="T-002", phase_id=0, agent_slug="product-strategist",
            description="Define product positioning and competitive analysis",
            acceptance_criteria=["Positioning statement", "Competitor matrix", "Value proposition"],
        ),
    ]
    for task in discover_tasks:
        pipeline = engine.add_task(pipeline, 0, task)
        ok(f"Task {task.id} → {task.agent_slug}: {task.description[:50]}...")

    # Step 6: Simulate critic reviews
    step(6, "Simulating critic reviews...")

    # T-001: Pass on first try
    pipeline = engine.submit_review(pipeline, "T-001", CriticVerdict.PASS)
    ok("T-001: PASS (first attempt)")
    library.report_telemetry("planner", "stakeholder-analysis", "pass", retry_count=0)

    # T-002: Needs work, then passes
    pipeline = engine.submit_review(pipeline, "T-002", CriticVerdict.NEEDS_WORK,
                                     "Missing competitive pricing analysis")
    info("T-002: NEEDS_WORK — Missing competitive pricing analysis")
    pipeline = engine.submit_review(pipeline, "T-002", CriticVerdict.PASS)
    ok("T-002: PASS (second attempt)")
    library.report_telemetry("product-strategist", "competitive-analysis", "pass", retry_count=1)

    # Step 7: Advance phase
    step(7, "Attempting phase advancement...")
    pipeline, advanced = engine.try_advance_phase(pipeline)
    if advanced:
        ok(f"Phase 0 gate PASSED → Now in Phase {pipeline.current_phase_id}: {pipeline.current_phase.name}")
    else:
        info("Phase gate not yet passed")

    # Step 8: Continue through remaining phases (simulated)
    step(8, "Simulating remaining phases...")

    remaining_phases = [p for p in pipeline.phases if p.id > 0]
    for phase in remaining_phases:
        # Add a representative task
        task = Task(
            id=f"T-{phase.id}00",
            phase_id=phase.id,
            agent_slug="conductor",
            description=f"Complete {phase.name} phase deliverables",
        )
        pipeline = engine.add_task(pipeline, phase.id, task)
        pipeline = engine.submit_review(pipeline, task.id, CriticVerdict.PASS)
        library.report_telemetry("conductor", f"phase-{phase.id}", "pass", retry_count=0)
        pipeline, advanced = engine.try_advance_phase(pipeline)
        ok(f"Phase {phase.id} ({phase.name}): PASSED")

    ok(f"Pipeline status: {pipeline.status}")
    ok(f"Progress: {pipeline.progress_pct:.0f}%")

    # Step 9: Generate report
    step(9, "Generating pipeline report...")
    report = engine.generate_report(pipeline)
    print()
    for line in report.split("\n"):
        print(f"      {line}")
    print()

    # Step 10: Run drift detection
    step(10, "Running drift detection...")
    detector = DriftDetector(library)
    alerts = detector.check_all()
    if alerts:
        for alert in alerts:
            info(f"⚠ {alert.agent_slug}: {alert.metric} = {alert.current_value:.2f} ({alert.severity})")
    else:
        ok("All agents performing within thresholds")

    # Step 11: Show evolution stats
    step(11, "Evolution statistics...")
    all_stats = library.get_all_agent_stats()
    for s in all_stats:
        fpr = f"{s['first_pass_rate']:.0%}" if s.get('first_pass_rate') is not None else "-"
        info(f"{s['agent_slug']}: {s.get('total_tasks', 0)} tasks, FPR={fpr}, status={s.get('evolution_status', 'unknown')}")

    library.close()

    header("Demo Complete")
    print("  This demo showed the full PRISM lifecycle:")
    print("  • Agent discovery and loading from Markdown files")
    print("  • Automatic execution mode classification")
    print("  • Pipeline creation with quality-gated phases")
    print("  • Critic review loop with retry tracking")
    print("  • Phase advancement through quality gates")
    print("  • Telemetry reporting to the evolution layer")
    print("  • Drift detection for agent performance monitoring")
    print()
    print("  To use PRISM in your own projects:")
    print("  1. pip install prism-agentic")
    print("  2. prism init my-project")
    print("  3. Configure your AI tool's MCP settings")
    print("  4. Start building with living agents!")
    print()


if __name__ == "__main__":
    main()
