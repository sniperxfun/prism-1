"""
PRISM Distillation Engine

Analyzes accumulated decisions and telemetry to extract reusable principles.
Runs periodically (recommended: after every 10 completed projects, or weekly).

Usage:
  python distill.py                    # Distill all agents
  python distill.py --agent backend-architect  # Distill specific agent
  python distill.py --dry-run          # Preview without saving
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent to path for shared DB access
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-server"))
from server import get_db, add_principle

# ── LLM Client ────────────────────────────────────────────────────────────────

def call_llm(prompt: str, model: str = "gpt-4.1-mini") -> str:
    """Call the configured LLM for distillation."""
    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM call failed: {e}")
        return None


# ── Distillation Logic ────────────────────────────────────────────────────────

DISTILLATION_PROMPT = """You are a distillation engine for an AI agent framework. Your job is to analyze execution history and extract reusable principles.

## Agent: {agent_slug}

## Recent Decisions (last {n_decisions} decisions):
{decisions}

## Recent Telemetry (last {n_tasks} tasks):
- First-pass rate: {first_pass_rate:.0%}
- Average retries: {avg_retries:.1f}
- Failure categories: {failure_breakdown}

## Existing Principles (do not duplicate):
{existing_principles}

## Your Task:
Extract 3-5 NEW reusable principles from this data. Each principle should:
1. Be specific and actionable (not generic advice)
2. Be grounded in the actual decisions/outcomes above
3. Include relevant tags for retrieval
4. NOT duplicate existing principles

Return ONLY a JSON array in this exact format:
[
  {{
    "text": "Specific, actionable principle text",
    "tags": ["tag1", "tag2", "tag3"],
    "confidence": 0.75,
    "rationale": "Why this principle was extracted"
  }}
]

If there is insufficient data to extract meaningful principles, return an empty array: []
"""


def get_agent_decisions(conn, agent_slug: str, limit: int = 50) -> list:
    rows = conn.execute(
        """SELECT decision, rationale, alternatives, outcome
           FROM decisions WHERE agent_slug = ?
           ORDER BY created_at DESC LIMIT ?""",
        (agent_slug, limit)
    ).fetchall()
    return [dict(r) for r in rows]


def get_agent_telemetry_summary(conn, agent_slug: str, days: int = 30) -> dict:
    rows = conn.execute(
        """SELECT outcome, retry_count, failure_category
           FROM telemetry WHERE agent_slug = ?
           AND date(created_at) >= date('now', ?)
           ORDER BY created_at DESC""",
        (agent_slug, f"-{days} days")
    ).fetchall()

    if not rows:
        return {"first_pass_rate": None, "avg_retries": None, "failure_breakdown": {}}

    total = len(rows)
    first_pass = sum(1 for r in rows if r["retry_count"] == 0 and r["outcome"] == "pass")
    avg_retries = sum(r["retry_count"] for r in rows) / total

    failure_breakdown = {}
    for r in rows:
        if r["failure_category"]:
            failure_breakdown[r["failure_category"]] = failure_breakdown.get(r["failure_category"], 0) + 1

    return {
        "first_pass_rate": first_pass / total,
        "avg_retries": avg_retries,
        "failure_breakdown": failure_breakdown,
        "total_tasks": total
    }


def get_existing_principles(conn, agent_slug: str) -> list:
    rows = conn.execute(
        "SELECT text FROM principles WHERE agent_slug = ? ORDER BY confidence DESC",
        (agent_slug,)
    ).fetchall()
    return [r["text"] for r in rows]


def distill_agent(agent_slug: str, dry_run: bool = False, verbose: bool = False) -> dict:
    """Run distillation for a single agent."""
    conn = get_db()

    decisions = get_agent_decisions(conn, agent_slug)
    telemetry = get_agent_telemetry_summary(conn, agent_slug)
    existing = get_existing_principles(conn, agent_slug)

    if len(decisions) < 5:
        return {"agent": agent_slug, "status": "insufficient_data", "principles_added": 0}

    # Format decisions for prompt
    decisions_text = "\n".join([
        f"- Decision: {d['decision']}\n  Rationale: {d['rationale']}\n  Outcome: {d['outcome']}"
        for d in decisions[:20]
    ])

    existing_text = "\n".join([f"- {p}" for p in existing[:10]]) or "None yet"

    failure_breakdown = json.dumps(telemetry.get("failure_breakdown", {}))

    prompt = DISTILLATION_PROMPT.format(
        agent_slug=agent_slug,
        n_decisions=len(decisions),
        decisions=decisions_text,
        first_pass_rate=telemetry.get("first_pass_rate") or 0,
        avg_retries=telemetry.get("avg_retries") or 0,
        failure_breakdown=failure_breakdown,
        n_tasks=telemetry.get("total_tasks", 0),
        existing_principles=existing_text
    )

    if verbose:
        print(f"\n[{agent_slug}] Calling LLM for distillation...")

    response = call_llm(prompt)
    if not response:
        return {"agent": agent_slug, "status": "llm_error", "principles_added": 0}

    try:
        # Extract JSON from response
        start = response.find("[")
        end = response.rfind("]") + 1
        if start == -1 or end == 0:
            return {"agent": agent_slug, "status": "parse_error", "principles_added": 0}

        principles = json.loads(response[start:end])
    except json.JSONDecodeError:
        return {"agent": agent_slug, "status": "parse_error", "principles_added": 0}

    if not principles:
        return {"agent": agent_slug, "status": "no_new_principles", "principles_added": 0}

    added = 0
    for p in principles:
        if verbose:
            print(f"  + Principle (confidence={p.get('confidence', 0.5):.2f}): {p['text'][:80]}...")

        if not dry_run:
            add_principle(
                agent=agent_slug,
                text=p["text"],
                tags=p.get("tags", []),
                confidence=p.get("confidence", 0.5),
                source_count=len(decisions)
            )
        added += 1

    return {
        "agent": agent_slug,
        "status": "success",
        "principles_added": added,
        "dry_run": dry_run
    }


def distill_all(dry_run: bool = False, verbose: bool = False) -> list:
    """Run distillation for all agents with sufficient data."""
    conn = get_db()

    agents = conn.execute(
        "SELECT DISTINCT agent_slug FROM decisions GROUP BY agent_slug HAVING COUNT(*) >= 5"
    ).fetchall()

    results = []
    for row in agents:
        result = distill_agent(row["agent_slug"], dry_run=dry_run, verbose=verbose)
        results.append(result)
        print(f"[{result['agent']}] {result['status']} — {result['principles_added']} principles {'(dry run)' if dry_run else 'added'}")

    return results


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PRISM Distillation Engine")
    parser.add_argument("--agent", help="Distill specific agent (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print(f"PRISM Distillation Engine — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}\n")

    if args.agent:
        result = distill_agent(args.agent, dry_run=args.dry_run, verbose=args.verbose)
        print(json.dumps(result, indent=2))
    else:
        results = distill_all(dry_run=args.dry_run, verbose=args.verbose)
        total_added = sum(r["principles_added"] for r in results)
        print(f"\nDistillation complete: {total_added} principles added across {len(results)} agents")
