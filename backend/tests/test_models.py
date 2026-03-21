"""
Tests for data models.
"""


from backend.models.task import Task, TaskPriority, TaskStatus
from backend.models.workflow import Workflow, WorkflowStatus


class TestWorkflow:
    """Tests for Workflow model."""

    def test_workflow_creation(self):
        """Test workflow creation."""
        workflow = Workflow(
            workflow_id="wf-123",
            name="Test Workflow",
            description="A test workflow"
        )

        assert workflow.name == "Test Workflow"
        assert workflow.status == WorkflowStatus.PENDING
        assert workflow.workflow_id == "wf-123"

    def test_workflow_to_dict(self):
        """Test workflow serialization."""
        workflow = Workflow(
            workflow_id="wf-123",
            name="Test Workflow",
            description="A test workflow"
        )

        data = workflow.model_dump()

        assert data["name"] == "Test Workflow"
        assert data["status"] == "pending"
        assert data["workflow_id"] == "wf-123"

    def test_workflow_status_transition(self):
        """Test workflow status transitions."""
        workflow = Workflow(workflow_id="wf-123", name="Test")

        assert workflow.status == WorkflowStatus.PENDING

        workflow.status = WorkflowStatus.RUNNING
        assert workflow.status == WorkflowStatus.RUNNING

        workflow.status = WorkflowStatus.COMPLETED
        assert workflow.status == WorkflowStatus.COMPLETED


class TestTask:
    """Tests for Task model."""

    def test_task_creation(self):
        """Test task creation."""
        task = Task(
            task_id="task-123",
            name="Test Task",
            description="A test task"
        )

        assert task.name == "Test Task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM
        assert task.task_id == "task-123"

    def test_task_priority_levels(self):
        """Test task priority levels."""
        low = Task(task_id="t1", name="Low", priority=TaskPriority.LOW)
        medium = Task(task_id="t2", name="Medium", priority=TaskPriority.MEDIUM)
        high = Task(task_id="t3", name="High", priority=TaskPriority.HIGH)
        critical = Task(task_id="t4", name="Critical", priority=TaskPriority.CRITICAL)

        assert low.priority.value == 4
        assert medium.priority.value == 3
        assert high.priority.value == 2
        assert critical.priority.value == 1

    def test_task_status_progression(self):
        """Test task status progression."""
        task = Task(task_id="task-123", name="Test")

        assert task.status == TaskStatus.PENDING

        task.status = TaskStatus.QUEUED
        assert task.status == TaskStatus.QUEUED

        task.status = TaskStatus.RUNNING
        assert task.status == TaskStatus.RUNNING

        task.status = TaskStatus.COMPLETED
        assert task.status == TaskStatus.COMPLETED

    def test_task_to_dict(self):
        """Test task serialization."""
        task = Task(
            task_id="task-123",
            name="Test Task",
            description="A test task",
            priority=TaskPriority.HIGH
        )

        data = task.model_dump()

        assert data["name"] == "Test Task"
        assert data["priority"] == TaskPriority.HIGH
        assert data["status"] == TaskStatus.PENDING
