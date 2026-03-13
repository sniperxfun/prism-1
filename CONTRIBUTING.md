# Contributing to PRISM

Thank you for your interest in contributing to PRISM. This guide covers everything you need to know to contribute effectively.

---

## Types of Contributions

### New Agents
The most valuable contribution. Add a new Living Agent to the library.

**Requirements:**
- Follow the [Agent Specification](core/AGENT-SPEC.md) exactly
- Include all required sections: Identity & Vibe, Core Mission, Critical Rules, Deliverables, Evolution Integration
- Agent must have a distinct, non-overlapping specialty from existing agents
- Include at least 3 activation triggers in frontmatter
- Include at least 2 collaboration relationships in frontmatter

**Process:**
1. Fork the repo
2. Create `agents/{division}/{division}-{role}.md`
3. Ensure frontmatter is valid YAML
4. Submit PR with a brief description of the agent's unique value

### Evolution Improvements
Improvements to the distillation engine, LLM-as-Judge, or MCP server.

**Requirements:**
- All changes must be backward compatible with existing SQLite databases
- Include tests for new functionality
- Document any new environment variables or configuration options

### Orchestration Patterns
Reusable patterns for the `orchestration/patterns/` directory.

**Format:**
```markdown
# Pattern: [Name]

## When to Use
[Specific scenario where this pattern applies]

## Agent Activation Sequence
[Ordered list of agents and their roles]

## Quality Gates
[Specific gate criteria for this pattern]

## Example
[Concrete example of this pattern in action]
```

### Bug Reports
Use the GitHub issue template. Include:
- Which agent or component is affected
- Expected behavior
- Actual behavior
- Steps to reproduce

---

## Agent Quality Standards

All contributed agents must meet these standards:

**Identity & Vibe**: The agent must have a distinct, memorable personality. Avoid generic descriptions like "helpful assistant." Give the agent a worldview, a communication style, and something they care deeply about.

**Critical Rules**: Rules must be genuinely constraining. "Be helpful" is not a rule. "NEVER approve a deployment without a rollback procedure" is a rule. Each rule should prevent a specific, realistic failure mode.

**Deliverables**: Templates must be complete and immediately usable. Include realistic placeholder values, not just `[placeholder]`. The template should demonstrate what a good output looks like.

**Evolution Integration**: The three MCP tool calls (recall_experience, record_decision, report_telemetry) must be present with correct syntax. The agent slug in tool calls must match the frontmatter slug exactly.

---

## Code Style

For Python files in `evolution/`:
- Follow PEP 8
- Type hints required for all function signatures
- Docstrings required for all public functions
- No external dependencies beyond `openai` and `sqlite3` for the core MCP server

---

## Pull Request Process

1. Ensure your contribution follows all requirements above
2. Update relevant documentation if needed
3. PRs for new agents require no tests — quality is assessed by human review
4. PRs for evolution code require passing tests
5. All PRs require at least one approving review

---

## Code of Conduct

Be direct, be honest, be constructive. The same standards the Critic applies to agent outputs apply to contributions to this project.
