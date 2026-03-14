"""
PRISM Agent Loader

Parses Living Agent Markdown files, extracts YAML frontmatter metadata,
and provides a structured interface for agent discovery and activation.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AgentCollaborator:
    """A collaborator relationship for an agent."""
    slug: str
    relationship: str  # peer | upstream | downstream


@dataclass
class AgentEvolution:
    """Evolution metadata for an agent."""
    status: str = "active"
    generation: int = 1
    last_evolved: Optional[str] = None
    experience_tags: list[str] = field(default_factory=list)
    quality_score: Optional[float] = None
    first_pass_rate: Optional[float] = None


@dataclass
class Agent:
    """A PRISM Living Agent loaded from a Markdown file."""
    name: str
    slug: str
    version: str
    division: str
    tier: str  # principal | senior | mid | junior
    file_path: Path
    collaborates_with: list[AgentCollaborator] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)
    evolution: AgentEvolution = field(default_factory=AgentEvolution)
    content: str = ""

    @property
    def identity_section(self) -> str:
        """Extract the Identity & Vibe section."""
        return self._extract_section("Identity & Vibe")

    @property
    def core_mission_section(self) -> str:
        """Extract the Core Mission section."""
        return self._extract_section("Core Mission")

    @property
    def critical_rules_section(self) -> str:
        """Extract the Critical Rules section."""
        return self._extract_section("Critical Rules")

    def _extract_section(self, heading: str) -> str:
        pattern = rf"## {re.escape(heading)}\s*\n(.*?)(?=\n## |\Z)"
        match = re.search(pattern, self.content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def to_prompt(self, include_evolution: bool = True) -> str:
        """Generate the full activation prompt for this agent."""
        prompt = self.content
        if include_evolution and self.evolution.experience_tags:
            prompt += f"\n\n<!-- Evolution context: tags={self.evolution.experience_tags} -->"
        return prompt


def _parse_yaml_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from a Markdown file."""
    import yaml
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, text, re.DOTALL)
    if not match:
        return {}, text
    try:
        metadata = yaml.safe_load(match.group(1)) or {}
    except Exception:
        metadata = {}
    body = match.group(2)
    return metadata, body


def load_agent(file_path: Path) -> Agent:
    """Load a single agent from a Markdown file."""
    text = file_path.read_text(encoding="utf-8")
    meta, body = _parse_yaml_frontmatter(text)

    collaborators = []
    for c in meta.get("collaborates_with", []):
        if isinstance(c, dict):
            collaborators.append(AgentCollaborator(
                slug=c.get("slug", ""),
                relationship=c.get("relationship", "peer")
            ))

    evolution_data = meta.get("evolution", {})
    evolution = AgentEvolution(
        status=evolution_data.get("status", "active"),
        generation=evolution_data.get("generation", 1),
        last_evolved=evolution_data.get("last_evolved"),
        experience_tags=evolution_data.get("experience_tags", []),
        quality_score=evolution_data.get("performance", {}).get("quality_score") if isinstance(evolution_data.get("performance"), dict) else None,
        first_pass_rate=evolution_data.get("performance", {}).get("first_pass_rate") if isinstance(evolution_data.get("performance"), dict) else None,
    )

    return Agent(
        name=meta.get("name", file_path.stem),
        slug=meta.get("slug", file_path.stem),
        version=meta.get("version", "1.0.0"),
        division=meta.get("division", "unknown"),
        tier=meta.get("tier", "mid"),
        file_path=file_path,
        collaborates_with=collaborators,
        triggers=meta.get("triggers", []),
        evolution=evolution,
        content=body.strip(),
    )


def discover_agents(agents_dir: Path) -> list[Agent]:
    """Discover and load all agents from a directory tree."""
    agents = []
    if not agents_dir.exists():
        return agents
    for md_file in sorted(agents_dir.rglob("*.md")):
        if md_file.name.startswith("_") or md_file.name == "README.md":
            continue
        try:
            agent = load_agent(md_file)
            agents.append(agent)
        except Exception as e:
            print(f"Warning: Failed to load agent from {md_file}: {e}")
    return agents


def find_agent(agents: list[Agent], slug: str) -> Optional[Agent]:
    """Find an agent by slug."""
    for agent in agents:
        if agent.slug == slug:
            return agent
    return None


def agents_by_division(agents: list[Agent]) -> dict[str, list[Agent]]:
    """Group agents by division."""
    divisions: dict[str, list[Agent]] = {}
    for agent in agents:
        divisions.setdefault(agent.division, []).append(agent)
    return divisions


def build_collaboration_graph(agents: list[Agent]) -> dict[str, list[str]]:
    """Build a directed collaboration graph from agent metadata."""
    graph: dict[str, list[str]] = {}
    for agent in agents:
        graph[agent.slug] = [c.slug for c in agent.collaborates_with]
    return graph
