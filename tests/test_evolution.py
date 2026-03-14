"""Tests for the PRISM Evolution layer."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prism.evolution import ExperienceLibrary, DriftDetector


def _make_library():
    """Create a temporary ExperienceLibrary for testing."""
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / "test_evolution.db"
    return ExperienceLibrary(db_path=db_path)


def test_add_and_recall_principle():
    """Test adding and recalling principles."""
    lib = _make_library()

    pid = lib.add_principle(
        agent="backend-architect",
        text="Always use connection pooling for database connections in high-traffic services",
        tags=["database", "performance", "connection-pooling"],
        confidence=0.85,
    )
    assert pid is not None

    principles = lib.recall(
        agent="backend-architect",
        context="database connection performance optimization",
        min_confidence=0.5,
    )
    assert len(principles) == 1
    assert "connection pooling" in principles[0]["text"]
    assert principles[0]["confidence"] == 0.85

    lib.close()
    print("  ✓ test_add_and_recall_principle passed")


def test_recall_filters_by_confidence():
    """Test that recall respects minimum confidence threshold."""
    lib = _make_library()

    lib.add_principle("test-agent", "Low confidence principle", ["test"], confidence=0.3)
    lib.add_principle("test-agent", "High confidence principle", ["test"], confidence=0.9)

    high_only = lib.recall("test-agent", "test", min_confidence=0.7)
    assert len(high_only) == 1
    assert "High confidence" in high_only[0]["text"]

    all_principles = lib.recall("test-agent", "test", min_confidence=0.1)
    assert len(all_principles) == 2

    lib.close()
    print("  ✓ test_recall_filters_by_confidence passed")


def test_record_decision():
    """Test recording decisions."""
    lib = _make_library()

    did = lib.record_decision(
        agent="conductor",
        decision="Selected PRISM-Sprint over PRISM-Full",
        rationale="Well-defined scope, 2-week timeline",
        alternatives="PRISM-Full would add 1 week",
        outcome="success",
    )
    assert did is not None

    stats = lib.get_agent_stats("conductor")
    assert stats["total_decisions"] == 1

    lib.close()
    print("  ✓ test_record_decision passed")


def test_report_telemetry():
    """Test reporting telemetry and baseline updates."""
    lib = _make_library()

    # First report — creates baseline
    tid = lib.report_telemetry(
        agent="frontend-developer",
        task_type="component-build",
        outcome="pass",
        retry_count=0,
    )
    assert tid is not None

    stats = lib.get_agent_stats("frontend-developer")
    assert stats["total_tasks"] == 1
    assert stats["evolution_status"] == "active"

    # Report several more to build up baseline
    for i in range(10):
        lib.report_telemetry(
            agent="frontend-developer",
            task_type="component-build",
            outcome="pass",
            retry_count=0,
        )

    stats = lib.get_agent_stats("frontend-developer")
    assert stats["total_tasks"] == 11
    assert stats["first_pass_rate"] is not None
    assert stats["first_pass_rate"] > 0.5  # Should be trending toward 1.0

    lib.close()
    print("  ✓ test_report_telemetry passed")


def test_telemetry_triggers_evolution_status():
    """Test that poor performance triggers evolution status changes."""
    lib = _make_library()

    # Report many failures to drive first_pass_rate down
    for i in range(20):
        lib.report_telemetry(
            agent="struggling-agent",
            task_type="complex-task",
            outcome="fail",
            retry_count=3,
            failure_category="logic_error",
        )

    stats = lib.get_agent_stats("struggling-agent")
    assert stats["evolution_status"] in ("needs_l2_refinement", "needs_l3_review")

    lib.close()
    print("  ✓ test_telemetry_triggers_evolution_status passed")


def test_drift_detector():
    """Test the drift detection system."""
    lib = _make_library()

    # Create a healthy agent
    for _ in range(10):
        lib.report_telemetry("healthy-agent", "task", "pass", retry_count=0)

    # Create a struggling agent
    for _ in range(10):
        lib.report_telemetry("bad-agent", "task", "fail", retry_count=3)

    detector = DriftDetector(lib)
    alerts = detector.check_all()

    # Should have alert for bad-agent but not healthy-agent
    alert_slugs = {a.agent_slug for a in alerts}
    assert "bad-agent" in alert_slugs
    assert "healthy-agent" not in alert_slugs

    lib.close()
    print("  ✓ test_drift_detector passed")


def test_agent_stats():
    """Test comprehensive agent stats retrieval."""
    lib = _make_library()

    lib.add_principle("stats-agent", "Test principle", ["test"], confidence=0.8)
    lib.record_decision("stats-agent", "Test decision", "Test rationale")
    lib.report_telemetry("stats-agent", "test-task", "pass")

    stats = lib.get_agent_stats("stats-agent")
    assert stats["agent"] == "stats-agent"
    assert stats["total_principles"] == 1
    assert stats["total_decisions"] == 1
    assert stats["total_tasks"] == 1

    lib.close()
    print("  ✓ test_agent_stats passed")


if __name__ == "__main__":
    print("\n=== PRISM Evolution Layer Tests ===\n")
    test_add_and_recall_principle()
    test_recall_filters_by_confidence()
    test_record_decision()
    test_report_telemetry()
    test_telemetry_triggers_evolution_status()
    test_drift_detector()
    test_agent_stats()
    print("\n  All evolution tests passed! ✓\n")
