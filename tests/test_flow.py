"""Tests for the PRISM Flow orchestration engine."""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prism.flow import (
    FlowEngine, ExecutionMode, Pipeline, Phase, Task,
    TaskStatus, PhaseStatus, CriticVerdict,
    PHASE_DEFINITIONS, MODE_PHASES,
)


def test_classify_mode():
    """Test automatic execution mode classification."""
    engine = FlowEngine(agents=[])

    assert engine.classify_mode("Build a new product MVP for our startup") == ExecutionMode.FULL
    assert engine.classify_mode("Research feasibility of WebRTC integration") == ExecutionMode.EXPLORE
    assert engine.classify_mode("Fix the login bug on mobile") == ExecutionMode.MICRO
    assert engine.classify_mode("Add user profile feature") == ExecutionMode.SPRINT

    # Explicit hint overrides
    assert engine.classify_mode("Something", scope_hint="full") == ExecutionMode.FULL
    assert engine.classify_mode("Something", scope_hint="micro") == ExecutionMode.MICRO
    print("  ✓ test_classify_mode passed")


def test_create_pipeline():
    """Test pipeline creation."""
    engine = FlowEngine(agents=[])

    pipeline = engine.create_pipeline(
        project_name="test-project",
        description="Build a new SaaS MVP",
        mode=ExecutionMode.FULL,
    )

    assert pipeline.project_name == "test-project"
    assert pipeline.mode == ExecutionMode.FULL
    assert len(pipeline.phases) == 6
    assert pipeline.phases[0].status == PhaseStatus.ACTIVE
    assert pipeline.status == "running"
    assert pipeline.progress_pct == 0.0
    print("  ✓ test_create_pipeline passed")


def test_pipeline_sprint_mode():
    """Test sprint mode has correct phases."""
    engine = FlowEngine(agents=[])
    pipeline = engine.create_pipeline("sprint-test", "Add a new feature", mode=ExecutionMode.SPRINT)

    assert len(pipeline.phases) == 4
    phase_ids = [p.id for p in pipeline.phases]
    assert phase_ids == [1, 2, 3, 4]
    print("  ✓ test_pipeline_sprint_mode passed")


def test_pipeline_micro_mode():
    """Test micro mode has correct phases."""
    engine = FlowEngine(agents=[])
    pipeline = engine.create_pipeline("micro-test", "Fix a bug", mode=ExecutionMode.MICRO)

    assert len(pipeline.phases) == 2
    phase_ids = [p.id for p in pipeline.phases]
    assert phase_ids == [3, 4]
    print("  ✓ test_pipeline_micro_mode passed")


def test_add_task():
    """Test adding tasks to a pipeline."""
    engine = FlowEngine(agents=[])
    pipeline = engine.create_pipeline("task-test", "Test project", mode=ExecutionMode.MICRO)

    task = Task(
        id="T-001",
        phase_id=3,
        agent_slug="backend-architect",
        description="Design the API schema",
        acceptance_criteria=["OpenAPI spec generated", "All endpoints documented"],
    )
    pipeline = engine.add_task(pipeline, 3, task)

    assert len(pipeline.phases[0].tasks) == 1
    assert pipeline.phases[0].tasks[0].id == "T-001"
    print("  ✓ test_add_task passed")


def test_submit_review_pass():
    """Test submitting a passing review."""
    engine = FlowEngine(agents=[])
    pipeline = engine.create_pipeline("review-test", "Test", mode=ExecutionMode.MICRO)

    task = Task(id="T-001", phase_id=3, agent_slug="test", description="Test task")
    task.status = TaskStatus.REVIEW
    pipeline = engine.add_task(pipeline, 3, task)

    pipeline = engine.submit_review(pipeline, "T-001", CriticVerdict.PASS)
    assert pipeline.phases[0].tasks[0].status == TaskStatus.PASSED
    assert pipeline.phases[0].tasks[0].completed_at is not None
    print("  ✓ test_submit_review_pass passed")


def test_submit_review_needs_work():
    """Test submitting a NEEDS_WORK review with retry tracking."""
    engine = FlowEngine(agents=[])
    pipeline = engine.create_pipeline("retry-test", "Test", mode=ExecutionMode.MICRO)

    task = Task(id="T-001", phase_id=3, agent_slug="test", description="Test task")
    pipeline = engine.add_task(pipeline, 3, task)

    # First retry
    pipeline = engine.submit_review(pipeline, "T-001", CriticVerdict.NEEDS_WORK, "Fix error handling")
    assert pipeline.phases[0].tasks[0].status == TaskStatus.NEEDS_WORK
    assert pipeline.phases[0].tasks[0].retry_count == 1
    assert len(pipeline.phases[0].tasks[0].critic_feedback) == 1

    # Second retry
    pipeline = engine.submit_review(pipeline, "T-001", CriticVerdict.NEEDS_WORK, "Still broken")
    assert pipeline.phases[0].tasks[0].retry_count == 2

    # Third retry → BLOCKED
    pipeline = engine.submit_review(pipeline, "T-001", CriticVerdict.NEEDS_WORK, "Cannot fix")
    assert pipeline.phases[0].tasks[0].status == TaskStatus.BLOCKED
    assert pipeline.phases[0].tasks[0].retry_count == 3
    print("  ✓ test_submit_review_needs_work passed")


def test_phase_advance():
    """Test phase advancement after all tasks pass."""
    engine = FlowEngine(agents=[])
    pipeline = engine.create_pipeline("advance-test", "Test", mode=ExecutionMode.MICRO)

    task1 = Task(id="T-001", phase_id=3, agent_slug="test", description="Task 1")
    task2 = Task(id="T-002", phase_id=3, agent_slug="test", description="Task 2")
    pipeline = engine.add_task(pipeline, 3, task1)
    pipeline = engine.add_task(pipeline, 3, task2)

    # Pass both tasks
    pipeline = engine.submit_review(pipeline, "T-001", CriticVerdict.PASS)
    pipeline = engine.submit_review(pipeline, "T-002", CriticVerdict.PASS)

    # Try to advance
    pipeline, advanced = engine.try_advance_phase(pipeline)
    assert advanced is True
    assert pipeline.phases[0].status == PhaseStatus.PASSED
    assert pipeline.phases[0].gate_passed is True
    assert pipeline.phases[1].status == PhaseStatus.ACTIVE
    assert pipeline.current_phase_id == 4
    print("  ✓ test_phase_advance passed")


def test_pipeline_completion():
    """Test full pipeline completion."""
    engine = FlowEngine(agents=[])
    pipeline = engine.create_pipeline("complete-test", "Test", mode=ExecutionMode.MICRO)

    # Phase 3
    task1 = Task(id="T-001", phase_id=3, agent_slug="test", description="Build")
    pipeline = engine.add_task(pipeline, 3, task1)
    pipeline = engine.submit_review(pipeline, "T-001", CriticVerdict.PASS)
    pipeline, _ = engine.try_advance_phase(pipeline)

    # Phase 4
    task2 = Task(id="T-002", phase_id=4, agent_slug="test", description="Harden")
    pipeline = engine.add_task(pipeline, 4, task2)
    pipeline = engine.submit_review(pipeline, "T-002", CriticVerdict.PASS)
    pipeline, advanced = engine.try_advance_phase(pipeline)

    assert advanced is True
    assert pipeline.status == "completed"
    assert pipeline.completed_at is not None
    assert pipeline.progress_pct == 100.0
    print("  ✓ test_pipeline_completion passed")


def test_pipeline_serialization():
    """Test saving and loading pipeline state."""
    engine = FlowEngine(agents=[])
    pipeline = engine.create_pipeline("serial-test", "Test", mode=ExecutionMode.SPRINT)

    task = Task(id="T-001", phase_id=1, agent_slug="test", description="Test")
    pipeline = engine.add_task(pipeline, 1, task)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        pipeline.save(Path(f.name))
        loaded = Pipeline.load(Path(f.name))

    assert loaded.id == pipeline.id
    assert loaded.project_name == pipeline.project_name
    assert loaded.mode == pipeline.mode
    assert len(loaded.phases) == len(pipeline.phases)
    assert len(loaded.phases[0].tasks) == 1
    assert loaded.phases[0].tasks[0].id == "T-001"
    print("  ✓ test_pipeline_serialization passed")


def test_generate_report():
    """Test pipeline report generation."""
    engine = FlowEngine(agents=[])
    pipeline = engine.create_pipeline("report-test", "Test", mode=ExecutionMode.MICRO)

    task = Task(id="T-001", phase_id=3, agent_slug="test", description="Build")
    pipeline = engine.add_task(pipeline, 3, task)

    report = engine.generate_report(pipeline)
    assert "Pipeline Status Report" in report
    assert "report-test" in report
    assert "PRISM-Micro" in report
    assert "Build" in report
    print("  ✓ test_generate_report passed")


if __name__ == "__main__":
    print("\n=== PRISM Flow Engine Tests ===\n")
    test_classify_mode()
    test_create_pipeline()
    test_pipeline_sprint_mode()
    test_pipeline_micro_mode()
    test_add_task()
    test_submit_review_pass()
    test_submit_review_needs_work()
    test_phase_advance()
    test_pipeline_completion()
    test_pipeline_serialization()
    test_generate_report()
    print("\n  All flow tests passed! ✓\n")
