"""
PRISM CLI — Main entry point.

Provides a rich command-line interface for managing PRISM projects,
agents, pipelines, and the evolution layer.
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from .. import __version__, PROJECT_ROOT
from ..config import PrismConfig, ensure_prism_home, PRISM_HOME
from ..agents import discover_agents, find_agent, agents_by_division, build_collaboration_graph
from ..flow import FlowEngine, ExecutionMode, Pipeline, Task, TaskStatus
from ..evolution import ExperienceLibrary, DriftDetector


# ── Formatting Helpers ───────────────────────────────────────────────────────

COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "red": "\033[31m",
    "white": "\033[37m",
}

def c(text: str, color: str) -> str:
    """Colorize text for terminal output."""
    if not sys.stdout.isatty():
        return text
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def print_header(text: str):
    print(f"\n{c('PRISM', 'cyan')} {c('|', 'dim')} {c(text, 'bold')}")
    print(c("─" * 60, "dim"))


def print_table(headers: list[str], rows: list[list[str]]):
    """Print a simple ASCII table."""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    header_line = " │ ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    separator = "─┼─".join("─" * w for w in widths)
    print(f" {header_line}")
    print(f" {separator}")
    for row in rows:
        line = " │ ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
        print(f" {line}")


# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_version(args):
    """Show version information."""
    print(f"{c('PRISM', 'cyan')} v{__version__}")
    print(f"Persistent Reasoning & Intelligent Self-evolving Multi-agent Framework")
    print(f"Home: {PRISM_HOME}")


def cmd_init(args):
    """Initialize a new PRISM project."""
    project_name = args.name or "my-prism-project"
    target_dir = Path.cwd() / project_name

    if target_dir.exists():
        print(f"{c('Error:', 'red')} Directory '{project_name}' already exists.")
        sys.exit(1)

    print_header(f"Initializing project: {project_name}")

    # Create project structure
    target_dir.mkdir(parents=True)

    # Copy agent files
    source_agents = PROJECT_ROOT / "agents"
    if source_agents.exists():
        shutil.copytree(source_agents, target_dir / "agents")
        agent_count = len(list((target_dir / "agents").rglob("*.md")))
        print(f"  {c('✓', 'green')} Copied {agent_count} agents")
    else:
        (target_dir / "agents").mkdir()
        print(f"  {c('!', 'yellow')} No agent templates found, created empty agents/")

    # Copy core specs
    source_core = PROJECT_ROOT / "core"
    if source_core.exists():
        shutil.copytree(source_core, target_dir / "core")
        print(f"  {c('✓', 'green')} Copied core specifications")

    # Copy evolution layer
    source_evo = PROJECT_ROOT / "evolution"
    if source_evo.exists():
        shutil.copytree(source_evo, target_dir / "evolution",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        print(f"  {c('✓', 'green')} Copied evolution layer")

    # Create project config
    config = PrismConfig(project_name=project_name)
    config.save(target_dir / "prism.json")
    print(f"  {c('✓', 'green')} Created prism.json")

    # Create .prism directory for local state
    (target_dir / ".prism").mkdir()
    print(f"  {c('✓', 'green')} Created .prism/ for local state")

    # Ensure global PRISM home
    ensure_prism_home()

    print(f"\n{c('Done!', 'green')} Project initialized at {target_dir}")
    print(f"\nNext steps:")
    print(f"  cd {project_name}")
    print(f"  prism agents              # List available agents")
    print(f"  prism flow start \"...\"    # Start a pipeline")


def cmd_agents(args):
    """List all available agents."""
    agents_dir = _find_agents_dir()
    agents = discover_agents(agents_dir)

    if not agents:
        print(f"{c('No agents found.', 'yellow')} Run 'prism init' first.")
        return

    print_header(f"Agent Library ({len(agents)} agents)")

    divisions = agents_by_division(agents)
    for div_name, div_agents in sorted(divisions.items()):
        print(f"\n  {c(div_name.upper(), 'magenta')} Division ({len(div_agents)} agents)")
        rows = []
        for agent in sorted(div_agents, key=lambda a: a.name):
            tier_color = {"principal": "red", "senior": "yellow", "mid": "green", "junior": "blue"}.get(agent.tier, "white")
            status = agent.evolution.status
            rows.append([agent.slug, agent.name, c(agent.tier, tier_color), status])
        print_table(["Slug", "Name", "Tier", "Evolution"], rows)


def cmd_agent_detail(args):
    """Show detailed information about a specific agent."""
    agents_dir = _find_agents_dir()
    agents = discover_agents(agents_dir)
    agent = find_agent(agents, args.slug)

    if not agent:
        print(f"{c('Error:', 'red')} Agent '{args.slug}' not found.")
        available = [a.slug for a in agents]
        print(f"Available agents: {', '.join(available)}")
        sys.exit(1)

    print_header(f"Agent: {agent.name}")
    print(f"  {c('Slug:', 'dim')}      {agent.slug}")
    print(f"  {c('Version:', 'dim')}   {agent.version}")
    print(f"  {c('Division:', 'dim')}  {agent.division}")
    print(f"  {c('Tier:', 'dim')}      {agent.tier}")
    print(f"  {c('File:', 'dim')}      {agent.file_path}")

    if agent.triggers:
        print(f"  {c('Triggers:', 'dim')}  {', '.join(agent.triggers)}")

    if agent.collaborates_with:
        print(f"\n  {c('Collaborators:', 'bold')}")
        for collab in agent.collaborates_with:
            arrow = {"peer": "↔", "upstream": "←", "downstream": "→"}.get(collab.relationship, "-")
            print(f"    {arrow} {collab.slug} ({collab.relationship})")

    print(f"\n  {c('Evolution:', 'bold')}")
    print(f"    Status: {agent.evolution.status}")
    print(f"    Generation: {agent.evolution.generation}")
    if agent.evolution.first_pass_rate is not None:
        print(f"    First-pass rate: {agent.evolution.first_pass_rate:.0%}")


def cmd_flow_start(args):
    """Start a new PRISM Flow pipeline."""
    agents_dir = _find_agents_dir()
    agents = discover_agents(agents_dir)

    engine = FlowEngine(agents)
    mode = None
    if args.mode:
        mode = ExecutionMode(args.mode)

    pipeline = engine.create_pipeline(
        project_name=args.project or "unnamed",
        description=args.description,
        mode=mode,
    )

    # Save pipeline state
    state_dir = _find_state_dir()
    pipeline.save(state_dir / f"{pipeline.id}.json")

    print_header(f"Pipeline Created")
    print(f"  {c('ID:', 'dim')}       {pipeline.id}")
    print(f"  {c('Project:', 'dim')}  {pipeline.project_name}")
    print(f"  {c('Mode:', 'dim')}     PRISM-{pipeline.mode.value.capitalize()}")
    print(f"  {c('Phases:', 'dim')}   {len(pipeline.phases)}")
    print()

    for phase in pipeline.phases:
        status_icon = "●" if phase.status.value == "active" else "○"
        print(f"  {status_icon} Phase {phase.id}: {phase.name} — {phase.description}")

    print(f"\n  Pipeline state saved to: {state_dir / f'{pipeline.id}.json'}")


def cmd_flow_status(args):
    """Show current pipeline status."""
    state_dir = _find_state_dir()
    pipelines = list(state_dir.glob("pipe-*.json"))

    if not pipelines:
        print(f"{c('No active pipelines.', 'yellow')} Run 'prism flow start' first.")
        return

    # Load most recent pipeline
    latest = max(pipelines, key=lambda p: p.stat().st_mtime)
    pipeline = Pipeline.load(latest)

    agents_dir = _find_agents_dir()
    agents = discover_agents(agents_dir)
    engine = FlowEngine(agents)

    report = engine.generate_report(pipeline)
    print(report)


def cmd_evolve_stats(args):
    """Show evolution statistics."""
    library = ExperienceLibrary()

    print_header("Evolution Statistics")

    stats = library.get_all_agent_stats()
    if not stats:
        print(f"  {c('No evolution data yet.', 'yellow')} Run some pipelines first.")
        return

    rows = []
    for s in stats:
        fpr = f"{s['first_pass_rate']:.0%}" if s.get("first_pass_rate") is not None else "-"
        retries = f"{s['avg_retries']:.1f}" if s.get("avg_retries") is not None else "-"
        total = str(s.get("total_tasks", 0))
        status = s.get("evolution_status", "unknown")
        status_color = {
            "healthy": "green", "l1_active": "blue",
            "needs_l2_refinement": "yellow", "needs_l3_review": "red"
        }.get(status, "white")
        rows.append([s["agent_slug"], fpr, retries, total, c(status, status_color)])

    print_table(["Agent", "FPR", "Avg Retries", "Tasks", "Status"], rows)


def cmd_evolve_drift(args):
    """Check for performance drift."""
    library = ExperienceLibrary()
    detector = DriftDetector(library)
    alerts = detector.check_all()

    print_header("Drift Detection")

    if not alerts:
        print(f"  {c('✓ All agents performing within thresholds.', 'green')}")
        return

    for alert in alerts:
        icon = "⚠" if alert.severity == "warning" else "✖"
        color = "yellow" if alert.severity == "warning" else "red"
        print(f"  {c(icon, color)} {c(alert.agent_slug, 'bold')}: "
              f"{alert.metric} = {alert.current_value:.2f} "
              f"(threshold: {alert.threshold:.2f})")
        print(f"    → {alert.recommended_action}")


def cmd_evolve_distill(args):
    """Run the distillation engine."""
    print_header("Distillation Engine")
    print(f"  Running distillation{'  (dry run)' if args.dry_run else ''}...")

    # Import and run the distillation engine
    sys.path.insert(0, str(PROJECT_ROOT / "evolution" / "distillation"))
    try:
        from distill import distill_all, distill_agent
        if args.agent:
            result = distill_agent(args.agent, dry_run=args.dry_run, verbose=True)
            print(f"\n  Result: {json.dumps(result, indent=2)}")
        else:
            results = distill_all(dry_run=args.dry_run, verbose=True)
            total = sum(r["principles_added"] for r in results)
            print(f"\n  {c('Done:', 'green')} {total} principles extracted from {len(results)} agents")
    except ImportError:
        print(f"  {c('Error:', 'red')} Distillation engine not found. Ensure evolution/ directory exists.")


def cmd_graph(args):
    """Show agent collaboration graph."""
    agents_dir = _find_agents_dir()
    agents = discover_agents(agents_dir)
    graph = build_collaboration_graph(agents)

    print_header("Agent Collaboration Graph")
    for slug, collaborators in sorted(graph.items()):
        if collaborators:
            targets = ", ".join(collaborators)
            print(f"  {c(slug, 'cyan')} → {targets}")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _find_agents_dir() -> Path:
    """Find the agents directory, checking CWD first, then project root."""
    cwd_agents = Path.cwd() / "agents"
    if cwd_agents.exists():
        return cwd_agents
    root_agents = PROJECT_ROOT / "agents"
    if root_agents.exists():
        return root_agents
    return cwd_agents  # Will produce empty list


def _find_state_dir() -> Path:
    """Find or create the state directory for pipeline files."""
    cwd_state = Path.cwd() / ".prism"
    if cwd_state.exists():
        return cwd_state
    global_state = PRISM_HOME / "pipelines"
    global_state.mkdir(parents=True, exist_ok=True)
    return global_state


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="prism",
        description="PRISM — Persistent Reasoning & Intelligent Self-evolving Multi-agent Framework",
    )
    parser.add_argument("--version", action="store_true", help="Show version")
    subparsers = parser.add_subparsers(dest="command")

    # version
    sub_version = subparsers.add_parser("version", help="Show version info")
    sub_version.set_defaults(func=cmd_version)

    # init
    sub_init = subparsers.add_parser("init", help="Initialize a new PRISM project")
    sub_init.add_argument("name", nargs="?", default=None, help="Project name")
    sub_init.set_defaults(func=cmd_init)

    # agents
    sub_agents = subparsers.add_parser("agents", help="List all agents")
    sub_agents.set_defaults(func=cmd_agents)

    # agent <slug>
    sub_agent = subparsers.add_parser("agent", help="Show agent details")
    sub_agent.add_argument("slug", help="Agent slug")
    sub_agent.set_defaults(func=cmd_agent_detail)

    # graph
    sub_graph = subparsers.add_parser("graph", help="Show agent collaboration graph")
    sub_graph.set_defaults(func=cmd_graph)

    # flow
    sub_flow = subparsers.add_parser("flow", help="Pipeline management")
    flow_sub = sub_flow.add_subparsers(dest="flow_command")

    flow_start = flow_sub.add_parser("start", help="Start a new pipeline")
    flow_start.add_argument("description", help="Project description")
    flow_start.add_argument("--project", "-p", help="Project name")
    flow_start.add_argument("--mode", "-m", choices=["full", "sprint", "micro", "explore"],
                            help="Force execution mode")
    flow_start.set_defaults(func=cmd_flow_start)

    flow_status = flow_sub.add_parser("status", help="Show pipeline status")
    flow_status.set_defaults(func=cmd_flow_status)

    # evolve
    sub_evolve = subparsers.add_parser("evolve", help="Evolution layer management")
    evolve_sub = sub_evolve.add_subparsers(dest="evolve_command")

    evolve_stats = evolve_sub.add_parser("stats", help="Show evolution statistics")
    evolve_stats.set_defaults(func=cmd_evolve_stats)

    evolve_drift = evolve_sub.add_parser("drift", help="Check for performance drift")
    evolve_drift.set_defaults(func=cmd_evolve_drift)

    evolve_distill = evolve_sub.add_parser("distill", help="Run distillation engine")
    evolve_distill.add_argument("--agent", help="Distill specific agent")
    evolve_distill.add_argument("--dry-run", action="store_true", help="Preview only")
    evolve_distill.set_defaults(func=cmd_evolve_distill)

    args = parser.parse_args()

    if args.version:
        cmd_version(args)
        return

    if not args.command:
        parser.print_help()
        return

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
