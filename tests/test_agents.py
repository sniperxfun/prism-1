"""Tests for the PRISM Agent loader."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prism.agents import (
    load_agent, discover_agents, find_agent,
    agents_by_division, build_collaboration_graph, Agent
)


SAMPLE_AGENT_MD = """---
name: "Test Agent"
slug: "test-agent"
version: "1.0.0"
division: engineering
tier: senior
collaborates_with:
  - slug: critic
    relationship: peer
  - slug: backend-architect
    relationship: downstream
triggers:
  - "test trigger"
  - "sample task"
evolution:
  status: active
  generation: 1
  last_evolved: null
  experience_tags: ["testing", "quality"]
  performance:
    quality_score: 0.85
    first_pass_rate: 0.72
    last_updated: null
---

# Test Agent

You are **Test Agent**, a sample agent for testing the PRISM framework.

## Identity & Vibe

**Personality**: Methodical, thorough, detail-oriented
**Voice**: Clear and precise

## Core Mission

### Primary Task
Test things thoroughly and report results accurately.

## Critical Rules

**NEVER skip a test case.** Every edge case matters.

**ALWAYS report failures immediately.** Silence is not golden.

## Evolution Integration

### Experience Recall
```
recall_experience({ agent: "test-agent", context: "testing" })
```
"""


def test_load_agent():
    """Test loading a single agent from Markdown."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(SAMPLE_AGENT_MD)
        f.flush()
        agent = load_agent(Path(f.name))

    assert agent.name == "Test Agent"
    assert agent.slug == "test-agent"
    assert agent.version == "1.0.0"
    assert agent.division == "engineering"
    assert agent.tier == "senior"
    assert len(agent.collaborates_with) == 2
    assert agent.collaborates_with[0].slug == "critic"
    assert agent.collaborates_with[0].relationship == "peer"
    assert len(agent.triggers) == 2
    assert agent.evolution.status == "active"
    assert agent.evolution.generation == 1
    assert agent.evolution.quality_score == 0.85
    assert agent.evolution.first_pass_rate == 0.72
    print("  ✓ test_load_agent passed")


def test_agent_sections():
    """Test extracting sections from agent content."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(SAMPLE_AGENT_MD)
        f.flush()
        agent = load_agent(Path(f.name))

    identity = agent.identity_section
    assert "Methodical" in identity
    assert "thorough" in identity

    mission = agent.core_mission_section
    assert "Primary Task" in mission

    rules = agent.critical_rules_section
    assert "NEVER skip" in rules
    print("  ✓ test_agent_sections passed")


def test_discover_agents():
    """Test discovering agents from a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        agents_dir = Path(tmpdir) / "agents" / "engineering"
        agents_dir.mkdir(parents=True)

        (agents_dir / "agent-a.md").write_text(SAMPLE_AGENT_MD)
        (agents_dir / "agent-b.md").write_text(
            SAMPLE_AGENT_MD.replace("test-agent", "agent-b").replace("Test Agent", "Agent B")
        )
        (agents_dir / "README.md").write_text("# README\nThis should be skipped.")

        agents = discover_agents(Path(tmpdir) / "agents")
        assert len(agents) == 2
        slugs = {a.slug for a in agents}
        assert "test-agent" in slugs or "agent-b" in slugs
    print("  ✓ test_discover_agents passed")


def test_find_agent():
    """Test finding an agent by slug."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(SAMPLE_AGENT_MD)
        f.flush()
        agent = load_agent(Path(f.name))

    agents = [agent]
    found = find_agent(agents, "test-agent")
    assert found is not None
    assert found.slug == "test-agent"

    not_found = find_agent(agents, "nonexistent")
    assert not_found is None
    print("  ✓ test_find_agent passed")


def test_collaboration_graph():
    """Test building the collaboration graph."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(SAMPLE_AGENT_MD)
        f.flush()
        agent = load_agent(Path(f.name))

    graph = build_collaboration_graph([agent])
    assert "test-agent" in graph
    assert "critic" in graph["test-agent"]
    assert "backend-architect" in graph["test-agent"]
    print("  ✓ test_collaboration_graph passed")


def test_agents_by_division():
    """Test grouping agents by division."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(SAMPLE_AGENT_MD)
        f.flush()
        agent = load_agent(Path(f.name))

    divisions = agents_by_division([agent])
    assert "engineering" in divisions
    assert len(divisions["engineering"]) == 1
    print("  ✓ test_agents_by_division passed")


if __name__ == "__main__":
    print("\n=== PRISM Agent Loader Tests ===\n")
    test_load_agent()
    test_agent_sections()
    test_discover_agents()
    test_find_agent()
    test_collaboration_graph()
    test_agents_by_division()
    print("\n  All agent tests passed! ✓\n")
