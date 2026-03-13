"""Validate PRISM agent file frontmatter against the Agent Specification."""

import sys
import yaml
from pathlib import Path

REQUIRED_FIELDS = ["name", "slug", "version", "division", "tier", "triggers", "evolution"]
VALID_DIVISIONS = ["engineering", "product", "design", "growth", "operations", "specialized"]
VALID_TIERS = ["junior", "mid", "senior", "principal"]
REQUIRED_SECTIONS = [
    "## Identity & Vibe",
    "## Core Mission",
    "## Critical Rules",
    "## Deliverables",
    "## Evolution Integration"
]

errors = []
warnings = []

agent_files = list(Path("agents").rglob("*.md"))
print(f"Validating {len(agent_files)} agent files...")

for path in agent_files:
    content = path.read_text()

    # Extract frontmatter
    if not content.startswith("---"):
        errors.append(f"{path}: Missing YAML frontmatter")
        continue

    try:
        end = content.index("---", 3)
        fm = yaml.safe_load(content[3:end])
    except Exception as e:
        errors.append(f"{path}: Invalid YAML frontmatter: {e}")
        continue

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"{path}: Missing required field '{field}'")

    # Check valid values
    if fm.get("division") not in VALID_DIVISIONS:
        errors.append(f"{path}: Invalid division '{fm.get('division')}'. Must be one of: {VALID_DIVISIONS}")

    if fm.get("tier") not in VALID_TIERS:
        errors.append(f"{path}: Invalid tier '{fm.get('tier')}'. Must be one of: {VALID_TIERS}")

    if not isinstance(fm.get("triggers"), list) or len(fm.get("triggers", [])) < 2:
        errors.append(f"{path}: 'triggers' must be a list with at least 2 items")

    # Check required sections
    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"{path}: Missing required section '{section}'")

    # Check Evolution Integration has MCP tool calls
    if "## Evolution Integration" in content:
        evo_section = content.split("## Evolution Integration")[1]
        if "recall_experience" not in evo_section:
            warnings.append(f"{path}: Evolution Integration missing 'recall_experience' call")
        if "report_telemetry" not in evo_section:
            warnings.append(f"{path}: Evolution Integration missing 'report_telemetry' call")

if warnings:
    print(f"\n⚠️  {len(warnings)} warnings:")
    for w in warnings:
        print(f"  {w}")

if errors:
    print(f"\n❌ {len(errors)} errors:")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print(f"\n✅ All {len(agent_files)} agent files are valid!")
