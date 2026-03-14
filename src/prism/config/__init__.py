"""
PRISM Configuration System

Manages project-level and global configuration for PRISM.
Configuration is stored in YAML files and can be overridden via environment variables.
"""

import os
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ── Default Paths ────────────────────────────────────────────────────────────

PRISM_HOME = Path(os.environ.get("PRISM_HOME", "~/.prism")).expanduser()
PRISM_DB_PATH = PRISM_HOME / "evolution.db"
PRISM_CONFIG_PATH = PRISM_HOME / "config.json"
PRISM_LOGS_PATH = PRISM_HOME / "logs"


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    temperature: float = 0.3
    max_tokens: int = 4096
    api_key: Optional[str] = None
    base_url: Optional[str] = None

    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.environ.get("OPENAI_API_KEY")
        if self.base_url is None:
            self.base_url = os.environ.get("OPENAI_BASE_URL")


@dataclass
class EvolutionConfig:
    """Evolution layer configuration."""
    db_path: str = str(PRISM_DB_PATH)
    distillation_threshold: int = 10  # Min decisions before distillation
    l2_trigger_threshold: float = 0.65  # First-pass rate below this triggers L2
    l3_trigger_threshold: float = 0.50  # First-pass rate below this triggers L3
    l3_min_days: int = 30  # Minimum days below threshold for L3
    ema_alpha: float = 0.1  # Exponential moving average alpha


@dataclass
class FlowConfig:
    """PRISM Flow orchestration configuration."""
    default_mode: str = "auto"  # auto | full | sprint | micro | explore
    max_retries: int = 3
    critic_default: str = "NEEDS_WORK"
    require_security_phase: bool = True
    parallel_agents: bool = False


@dataclass
class MCPConfig:
    """MCP server configuration."""
    host: str = "127.0.0.1"
    port: int = 3100
    transport: str = "stdio"  # stdio | sse


@dataclass
class PrismConfig:
    """Root PRISM configuration."""
    project_name: str = "prism-project"
    agents_dir: str = "agents"
    llm: LLMConfig = field(default_factory=LLMConfig)
    evolution: EvolutionConfig = field(default_factory=EvolutionConfig)
    flow: FlowConfig = field(default_factory=FlowConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)

    def save(self, path: Optional[Path] = None):
        """Save configuration to JSON file."""
        path = path or PRISM_CONFIG_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "PrismConfig":
        """Load configuration from JSON file."""
        path = path or PRISM_CONFIG_PATH
        if not path.exists():
            return cls()
        with open(path) as f:
            data = json.load(f)
        return cls(
            project_name=data.get("project_name", "prism-project"),
            agents_dir=data.get("agents_dir", "agents"),
            llm=LLMConfig(**data.get("llm", {})),
            evolution=EvolutionConfig(**data.get("evolution", {})),
            flow=FlowConfig(**data.get("flow", {})),
            mcp=MCPConfig(**data.get("mcp", {})),
        )

    @classmethod
    def from_project(cls, project_dir: Path) -> "PrismConfig":
        """Load configuration from a project directory's prism.json."""
        config_path = project_dir / "prism.json"
        if config_path.exists():
            return cls.load(config_path)
        return cls.load()


def ensure_prism_home():
    """Ensure PRISM home directory exists with proper structure."""
    PRISM_HOME.mkdir(parents=True, exist_ok=True)
    PRISM_LOGS_PATH.mkdir(parents=True, exist_ok=True)
    if not PRISM_CONFIG_PATH.exists():
        PrismConfig().save()
