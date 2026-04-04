"""
Comprehensive tests for model methods with full coverage.

Covers uncovered lines in:
- backend/models/workflow.py (lines 105, 109, 113-119, 123-125)
- backend/models/task.py (lines 121, 129, 133-135, 139-141)
"""

from datetime import datetime

from backend.models.task import Task, TaskPriority, TaskStatus
from backend.models.workflow import Workflow, WorkflowStatus, WorkflowStep


class TestWorkflowMethods:
    """Tests for Workflow model methods."""

    # ===========================================================================
    # is_complete() tests - covers line 105
    # ===========================================================================

    def test_is_complete_when_completed(self):
        """Test is_complete returns True for COMPLETED status."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", status=WorkflowStatus.COMPLETED)

        assert workflow.is_complete() is True

    def test_is_complete_when_failed(self):
        """Test is_complete returns True for FAILED status."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", status=WorkflowStatus.FAILED)

        assert workflow.is_complete() is True

    def test_is_complete_when_cancelled(self):
        """Test is_complete returns True for CANCELLED status."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", status=WorkflowStatus.CANCELLED)

        assert workflow.is_complete() is True

    def test_is_complete_when_running(self):
        """Test is_complete returns False for RUNNING status."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", status=WorkflowStatus.RUNNING)

        assert workflow.is_complete() is False

    def test_is_complete_when_pending(self):
        """Test is_complete returns False for PENDING status."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", status=WorkflowStatus.PENDING)

        assert workflow.is_complete() is False

    def test_is_complete_when_paused(self):
        """Test is_complete returns False for PAUSED status."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", status=WorkflowStatus.PAUSED)

        assert workflow.is_complete() is False

    # ===========================================================================
    # can_execute() tests - covers line 109
    # ===========================================================================

    def test_can_execute_when_pending(self):
        """Test can_execute returns True for PENDING status."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", status=WorkflowStatus.PENDING)

        assert workflow.can_execute() is True

    def test_can_execute_when_paused(self):
        """Test can_execute returns True for PAUSED status."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", status=WorkflowStatus.PAUSED)

        assert workflow.can_execute() is True

    def test_can_execute_when_running(self):
        """Test can_execute returns False for RUNNING status."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", status=WorkflowStatus.RUNNING)

        assert workflow.can_execute() is False

    def test_can_execute_when_completed(self):
        """Test can_execute returns False for COMPLETED status."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", status=WorkflowStatus.COMPLETED)

        assert workflow.can_execute() is False

    def test_can_execute_when_failed(self):
        """Test can_execute returns False for FAILED status."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", status=WorkflowStatus.FAILED)

        assert workflow.can_execute() is False

    def test_can_execute_when_cancelled(self):
        """Test can_execute returns False for CANCELLED status."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", status=WorkflowStatus.CANCELLED)

        assert workflow.can_execute() is False

    # ===========================================================================
    # get_next_steps() tests - covers lines 113-119
    # ===========================================================================

    def test_get_next_steps_no_steps(self):
        """Test get_next_steps with no steps."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", steps=[])

        result = workflow.get_next_steps()
        assert result == []

    def test_get_next_steps_no_dependencies(self):
        """Test get_next_steps when steps have no dependencies."""
        steps = [
            WorkflowStep(step_id="step1", name="Step 1"),
            WorkflowStep(step_id="step2", name="Step 2"),
        ]

        workflow = Workflow(
            workflow_id="wf-123", name="Test Workflow", steps=steps, completed_steps=[], failed_steps=[]
        )

        result = workflow.get_next_steps()

        assert len(result) == 2
        assert result[0].step_id == "step1"
        assert result[1].step_id == "step2"

    def test_get_next_steps_with_dependencies(self):
        """Test get_next_steps with dependencies."""
        steps = [
            WorkflowStep(step_id="step1", name="Step 1"),
            WorkflowStep(step_id="step2", name="Step 2", dependencies=["step1"]),
            WorkflowStep(step_id="step3", name="Step 3", dependencies=["step1", "step2"]),
        ]

        workflow = Workflow(
            workflow_id="wf-123", name="Test Workflow", steps=steps, completed_steps=[], failed_steps=[]
        )

        # Only step1 should be ready (no dependencies)
        result = workflow.get_next_steps()

        assert len(result) == 1
        assert result[0].step_id == "step1"

    def test_get_next_steps_after_some_completed(self):
        """Test get_next_steps after completing some steps."""
        steps = [
            WorkflowStep(step_id="step1", name="Step 1"),
            WorkflowStep(step_id="step2", name="Step 2", dependencies=["step1"]),
            WorkflowStep(step_id="step3", name="Step 3", dependencies=["step1", "step2"]),
        ]

        workflow = Workflow(
            workflow_id="wf-123", name="Test Workflow", steps=steps, completed_steps=["step1"], failed_steps=[]
        )

        # step2 should be ready now (step1 is completed)
        result = workflow.get_next_steps()

        assert len(result) == 1
        assert result[0].step_id == "step2"

    def test_get_next_steps_skip_failed(self):
        """Test get_next_steps skips failed steps."""
        steps = [
            WorkflowStep(step_id="step1", name="Step 1"),
            WorkflowStep(step_id="step2", name="Step 2"),
        ]

        workflow = Workflow(
            workflow_id="wf-123", name="Test Workflow", steps=steps, completed_steps=[], failed_steps=["step1"]
        )

        # step1 is failed, only step2 should be ready
        result = workflow.get_next_steps()

        assert len(result) == 1
        assert result[0].step_id == "step2"

    def test_get_next_steps_skip_completed(self):
        """Test get_next_steps skips completed steps."""
        steps = [
            WorkflowStep(step_id="step1", name="Step 1"),
            WorkflowStep(step_id="step2", name="Step 2"),
        ]

        workflow = Workflow(
            workflow_id="wf-123", name="Test Workflow", steps=steps, completed_steps=["step1"], failed_steps=[]
        )

        result = workflow.get_next_steps()

        assert len(result) == 1
        assert result[0].step_id == "step2"

    def test_get_next_steps_all_completed(self):
        """Test get_next_steps when all steps are complete."""
        steps = [
            WorkflowStep(step_id="step1", name="Step 1"),
            WorkflowStep(step_id="step2", name="Step 2"),
        ]

        workflow = Workflow(
            workflow_id="wf-123", name="Test Workflow", steps=steps, completed_steps=["step1", "step2"], failed_steps=[]
        )

        result = workflow.get_next_steps()
        assert result == []

    def test_get_next_steps_dependencies_not_met(self):
        """Test get_next_steps when dependencies not met."""
        steps = [
            WorkflowStep(step_id="step1", name="Step 1"),
            WorkflowStep(step_id="step2", name="Step 2", dependencies=["step1"]),
        ]

        workflow = Workflow(
            workflow_id="wf-123",
            name="Test Workflow",
            steps=steps,
            completed_steps=[],
            failed_steps=["step1"],  # step1 failed
        )

        # step2 depends on step1, but step1 failed, so step2 can't run
        # Only step2 is not in completed/failed, but its deps not in completed
        result = workflow.get_next_steps()
        assert result == []

    # ===========================================================================
    # get_progress_percent() tests - covers lines 123-125
    # ===========================================================================

    def test_get_progress_percent_no_steps(self):
        """Test get_progress_percent with no steps."""
        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", steps=[])

        result = workflow.get_progress_percent()
        assert result == 0.0

    def test_get_progress_percent_no_completed(self):
        """Test get_progress_percent with no completed steps."""
        steps = [
            WorkflowStep(step_id="step1", name="Step 1"),
            WorkflowStep(step_id="step2", name="Step 2"),
        ]

        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", steps=steps, completed_steps=[])

        result = workflow.get_progress_percent()
        assert result == 0.0

    def test_get_progress_percent_half_completed(self):
        """Test get_progress_percent with half steps completed."""
        steps = [
            WorkflowStep(step_id="step1", name="Step 1"),
            WorkflowStep(step_id="step2", name="Step 2"),
        ]

        workflow = Workflow(workflow_id="wf-123", name="Test Workflow", steps=steps, completed_steps=["step1"])

        result = workflow.get_progress_percent()
        assert result == 50.0

    def test_get_progress_percent_all_completed(self):
        """Test get_progress_percent with all steps completed."""
        steps = [
            WorkflowStep(step_id="step1", name="Step 1"),
            WorkflowStep(step_id="step2", name="Step 2"),
            WorkflowStep(step_id="step3", name="Step 3"),
        ]

        workflow = Workflow(
            workflow_id="wf-123", name="Test Workflow", steps=steps, completed_steps=["step1", "step2", "step3"]
        )

        result = workflow.get_progress_percent()
        assert result == 100.0

    def test_get_progress_percent_partial(self):
        """Test get_progress_percent with partial completion."""
        steps = [
            WorkflowStep(step_id=f"step{i}", name=f"Step {i}")
            for i in range(1, 5)  # 4 steps
        ]

        workflow = Workflow(
            workflow_id="wf-123",
            name="Test Workflow",
            steps=steps,
            completed_steps=["step1"],  # 1 of 4 completed
        )

        result = workflow.get_progress_percent()
        assert result == 25.0


class TestTaskMethods:
    """Tests for Task model methods."""

    # ===========================================================================
    # is_complete() tests - covers line 121
    # ===========================================================================

    def test_is_complete_when_completed(self):
        """Test is_complete returns True for COMPLETED status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.COMPLETED)

        assert task.is_complete() is True

    def test_is_complete_when_failed(self):
        """Test is_complete returns True for FAILED status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.FAILED)

        assert task.is_complete() is True

    def test_is_complete_when_cancelled(self):
        """Test is_complete returns True for CANCELLED status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.CANCELLED)

        assert task.is_complete() is True

    def test_is_complete_when_running(self):
        """Test is_complete returns False for RUNNING status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.RUNNING)

        assert task.is_complete() is False

    def test_is_complete_when_pending(self):
        """Test is_complete returns False for PENDING status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.PENDING)

        assert task.is_complete() is False

    def test_is_complete_when_queued(self):
        """Test is_complete returns False for QUEUED status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.QUEUED)

        assert task.is_complete() is False

    def test_is_complete_when_paused(self):
        """Test is_complete returns False for PAUSED status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.PAUSED)

        assert task.is_complete() is False

    def test_is_complete_when_retrying(self):
        """Test is_complete returns False for RETRYING status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.RETRYING)

        assert task.is_complete() is False

    # ===========================================================================
    # can_execute() tests - covers line 129
    # ===========================================================================

    def test_can_execute_when_pending(self):
        """Test can_execute returns True for PENDING status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.PENDING)

        assert task.can_execute() is True

    def test_can_execute_when_queued(self):
        """Test can_execute returns True for QUEUED status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.QUEUED)

        assert task.can_execute() is True

    def test_can_execute_when_running(self):
        """Test can_execute returns False for RUNNING status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.RUNNING)

        assert task.can_execute() is False

    def test_can_execute_when_completed(self):
        """Test can_execute returns False for COMPLETED status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.COMPLETED)

        assert task.can_execute() is False

    def test_can_execute_when_failed(self):
        """Test can_execute returns False for FAILED status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.FAILED)

        assert task.can_execute() is False

    def test_can_execute_when_paused(self):
        """Test can_execute returns False for PAUSED status."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.PAUSED)

        assert task.can_execute() is False

    # ===========================================================================
    # should_retry() tests - covers lines 133-135
    # ===========================================================================

    def test_should_retry_when_not_failed(self):
        """Test should_retry returns False when status is not FAILED."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.RUNNING, retry_count=0, max_retries=3)

        assert task.should_retry() is False

    def test_should_retry_when_failed_with_retries_left(self):
        """Test should_retry returns True when failed with retries remaining."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.FAILED, retry_count=1, max_retries=3)

        assert task.should_retry() is True

    def test_should_retry_when_failed_no_retries_left(self):
        """Test should_retry returns False when retries exhausted."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.FAILED, retry_count=3, max_retries=3)

        assert task.should_retry() is False

    def test_should_retry_when_failed_exceeded_retries(self):
        """Test should_retry returns False when retry count exceeds max."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.FAILED, retry_count=5, max_retries=3)

        assert task.should_retry() is False

    def test_should_retry_zero_max_retries(self):
        """Test should_retry with zero max retries."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.FAILED, retry_count=0, max_retries=0)

        assert task.should_retry() is False

    def test_should_retry_first_failure(self):
        """Test should_retry on first failure."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.FAILED, retry_count=0, max_retries=3)

        assert task.should_retry() is True

    def test_should_retry_when_completed(self):
        """Test should_retry returns False for completed task."""
        task = Task(task_id="task-123", name="Test Task", status=TaskStatus.COMPLETED, retry_count=0, max_retries=3)

        assert task.should_retry() is False

    # ===========================================================================
    # get_duration_seconds() tests - covers lines 139-141
    # ===========================================================================

    def test_get_duration_seconds_both_timestamps(self):
        """Test get_duration_seconds with both timestamps."""
        started = datetime(2024, 1, 15, 10, 0, 0)
        completed = datetime(2024, 1, 15, 10, 5, 30)

        task = Task(task_id="task-123", name="Test Task", started_at=started, completed_at=completed)

        result = task.get_duration_seconds()

        assert result == 330.0  # 5 minutes 30 seconds

    def test_get_duration_seconds_no_started_at(self):
        """Test get_duration_seconds with no started_at."""
        task = Task(task_id="task-123", name="Test Task", started_at=None, completed_at=datetime.now())

        result = task.get_duration_seconds()
        assert result is None

    def test_get_duration_seconds_no_completed_at(self):
        """Test get_duration_seconds with no completed_at."""
        task = Task(task_id="task-123", name="Test Task", started_at=datetime.now(), completed_at=None)

        result = task.get_duration_seconds()
        assert result is None

    def test_get_duration_seconds_neither_timestamp(self):
        """Test get_duration_seconds with neither timestamp."""
        task = Task(task_id="task-123", name="Test Task", started_at=None, completed_at=None)

        result = task.get_duration_seconds()
        assert result is None

    def test_get_duration_seconds_short_duration(self):
        """Test get_duration_seconds for short duration."""
        started = datetime(2024, 1, 15, 10, 0, 0)
        completed = datetime(2024, 1, 15, 10, 0, 1)

        task = Task(task_id="task-123", name="Test Task", started_at=started, completed_at=completed)

        result = task.get_duration_seconds()
        assert result == 1.0

    def test_get_duration_seconds_long_duration(self):
        """Test get_duration_seconds for long duration."""
        started = datetime(2024, 1, 15, 10, 0, 0)
        completed = datetime(2024, 1, 16, 10, 0, 0)  # 24 hours later

        task = Task(task_id="task-123", name="Test Task", started_at=started, completed_at=completed)

        result = task.get_duration_seconds()
        assert result == 86400.0  # 24 hours in seconds

    def test_get_duration_seconds_with_microseconds(self):
        """Test get_duration_seconds preserves precision."""
        started = datetime(2024, 1, 15, 10, 0, 0, 0)
        completed = datetime(2024, 1, 15, 10, 0, 0, 500000)  # 0.5 seconds

        task = Task(task_id="task-123", name="Test Task", started_at=started, completed_at=completed)

        result = task.get_duration_seconds()
        assert result == 0.5


class TestWorkflowStep:
    """Tests for WorkflowStep model."""

    def test_workflow_step_creation_minimal(self):
        """Test WorkflowStep creation with minimal fields."""
        step = WorkflowStep(step_id="step-123", name="Test Step")

        assert step.step_id == "step-123"
        assert step.name == "Test Step"
        assert step.description == ""
        assert step.agent_role is None
        assert step.crew_type is None
        assert step.dependencies == []
        assert step.config == {}
        assert step.timeout_seconds == 300
        assert step.retry_count == 3

    def test_workflow_step_creation_full(self):
        """Test WorkflowStep creation with all fields."""
        step = WorkflowStep(
            step_id="step-123",
            name="Test Step",
            description="A test step",
            agent_role="backend_engineer",
            crew_type="development",
            dependencies=["step-100", "step-101"],
            config={"key": "value"},
            timeout_seconds=600,
            retry_count=5,
        )

        assert step.step_id == "step-123"
        assert step.description == "A test step"
        assert step.agent_role == "backend_engineer"
        assert step.crew_type == "development"
        assert step.dependencies == ["step-100", "step-101"]
        assert step.config == {"key": "value"}
        assert step.timeout_seconds == 600
        assert step.retry_count == 5


class TestWorkflowStatusEnum:
    """Tests for WorkflowStatus enum."""

    def test_all_workflow_statuses(self):
        """Test all workflow status values."""
        assert WorkflowStatus.PENDING.value == "pending"
        assert WorkflowStatus.RUNNING.value == "running"
        assert WorkflowStatus.PAUSED.value == "paused"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.FAILED.value == "failed"
        assert WorkflowStatus.CANCELLED.value == "cancelled"


class TestTaskStatusEnum:
    """Tests for TaskStatus enum."""

    def test_all_task_statuses(self):
        """Test all task status values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.QUEUED.value == "queued"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.PAUSED.value == "paused"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"
        assert TaskStatus.RETRYING.value == "retrying"


class TestTaskPriorityEnum:
    """Tests for TaskPriority enum."""

    def test_all_task_priorities(self):
        """Test all task priority values."""
        assert TaskPriority.CRITICAL.value == 1
        assert TaskPriority.HIGH.value == 2
        assert TaskPriority.MEDIUM.value == 3
        assert TaskPriority.LOW.value == 4
        assert TaskPriority.BACKGROUND.value == 5

    def test_priority_ordering(self):
        """Test that priorities are correctly ordered."""
        assert TaskPriority.CRITICAL.value < TaskPriority.HIGH.value
        assert TaskPriority.HIGH.value < TaskPriority.MEDIUM.value
        assert TaskPriority.MEDIUM.value < TaskPriority.LOW.value
        assert TaskPriority.LOW.value < TaskPriority.BACKGROUND.value
