"""
Tests for Task Manager.
"""


from backend.workflows.task_manager import (
    TaskManager,
    TaskPriority,
    TaskStatus,
    WorkflowTask,
)


class TestWorkflowTask:
    """Test cases for WorkflowTask."""

    def test_task_creation(self):
        """Test creating a task."""
        task = WorkflowTask(
            name="Test Task",
            description="A test task",
            task_type="test",
            priority=TaskPriority.HIGH,
        )

        assert task.name == "Test Task"
        assert task.description == "A test task"
        assert task.task_type == "test"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.PENDING
        assert task.task_id is not None

    def test_task_to_dict(self):
        """Test converting task to dict."""
        task = WorkflowTask(name="Test Task", task_type="test")

        result = task.to_dict()

        assert result["name"] == "Test Task"
        assert result["task_type"] == "test"
        assert "task_id" in result


class TestTaskManager:
    """Test cases for TaskManager."""

    def setup_method(self):
        """Create fresh task manager for each test."""
        self.manager = TaskManager()

    def test_create_task(self):
        """Test creating a task."""
        task = self.manager.create_task(
            name="Test Task",
            description="A test task",
            task_type="test",
        )

        assert task.name == "Test Task"
        assert task in self.manager.get_pending_tasks()

    def test_assign_task(self):
        """Test assigning a task."""
        task = self.manager.create_task(name="Test Task", task_type="test")

        result = self.manager.assign_task(task.task_id, "agent-123")

        assert result is True
        assert task.status == TaskStatus.ASSIGNED
        assert task.assigned_to == "agent-123"

    def test_assign_nonexistent_task(self):
        """Test assigning non-existent task."""
        result = self.manager.assign_task("nonexistent", "agent-123")

        assert result is False

    def test_complete_task(self):
        """Test completing a task."""
        task = self.manager.create_task(name="Test Task", task_type="test")
        self.manager.assign_task(task.task_id, "agent-123")

        result = self.manager.complete_task(task.task_id, {"output": "success"})

        assert result is True
        assert task.status == TaskStatus.COMPLETED
        assert task.result == {"output": "success"}

    def test_fail_task(self):
        """Test failing a task."""
        task = self.manager.create_task(name="Test Task", task_type="test")
        self.manager.assign_task(task.task_id, "agent-123")

        result = self.manager.fail_task(task.task_id, "Something went wrong")

        assert result is True
        assert task.status == TaskStatus.FAILED
        assert task.error == "Something went wrong"

    def test_get_task(self):
        """Test getting a task."""
        task = self.manager.create_task(name="Test Task", task_type="test")

        retrieved = self.manager.get_task(task.task_id)

        assert retrieved is task

    def test_get_pending_tasks_priority_order(self):
        """Test that pending tasks are sorted by priority."""
        low_task = self.manager.create_task(
            name="Low Priority",
            task_type="test",
            priority=TaskPriority.LOW,
        )
        high_task = self.manager.create_task(
            name="High Priority",
            task_type="test",
            priority=TaskPriority.HIGH,
        )
        medium_task = self.manager.create_task(
            name="Medium Priority",
            task_type="test",
            priority=TaskPriority.MEDIUM,
        )

        pending = self.manager.get_pending_tasks()

        # Should be sorted high -> medium -> low
        assert pending[0] == high_task
        assert pending[1] == medium_task
        assert pending[2] == low_task

    def test_get_tasks_by_project(self):
        """Test getting tasks by project."""
        task1 = self.manager.create_task(
            name="Task 1",
            task_type="test",
            project_id="proj-1",
        )
        task2 = self.manager.create_task(
            name="Task 2",
            task_type="test",
            project_id="proj-1",
        )
        task3 = self.manager.create_task(
            name="Task 3",
            task_type="test",
            project_id="proj-2",
        )

        proj1_tasks = self.manager.get_tasks_by_project("proj-1")

        assert len(proj1_tasks) == 2
        assert task1 in proj1_tasks
        assert task2 in proj1_tasks
        assert task3 not in proj1_tasks

    def test_get_tasks_by_phase(self):
        """Test getting tasks by phase."""
        task1 = self.manager.create_task(
            name="Task 1",
            task_type="test",
            phase="requirements",
        )
        task2 = self.manager.create_task(
            name="Task 2",
            task_type="test",
            phase="requirements",
        )

        req_tasks = self.manager.get_tasks_by_phase("requirements")

        assert len(req_tasks) == 2
        assert task1 in req_tasks
        assert task2 in req_tasks

    def test_get_stats(self):
        """Test getting task statistics."""
        task1 = self.manager.create_task(name="Task 1", task_type="test")
        self.manager.create_task(name="Task 2", task_type="test")
        self.manager.assign_task(task1.task_id, "agent-1")
        self.manager.complete_task(task1.task_id, {})

        stats = self.manager.get_stats()

        assert stats["total"] == 2
        assert stats["completed"] == 1
        assert stats["pending"] == 1

    def test_assign_task_not_pending(self):
        """Test assigning a task that's not in pending state (covers lines 188-193)."""
        task = self.manager.create_task(name="Test Task", task_type="test")
        # First assignment succeeds
        self.manager.assign_task(task.task_id, "agent-1")
        assert task.status == TaskStatus.ASSIGNED

        # Second assignment should fail - task is no longer pending
        result = self.manager.assign_task(task.task_id, "agent-2")

        assert result is False
        assert task.assigned_to == "agent-1"  # Still assigned to first agent

    def test_complete_nonexistent_task(self):
        """Test completing a task that doesn't exist (covers line 228)."""
        result = self.manager.complete_task("nonexistent-id", {"output": "data"})

        assert result is False

    def test_fail_nonexistent_task(self):
        """Test failing a task that doesn't exist (covers line 258)."""
        result = self.manager.fail_task("nonexistent-id", "Some error")

        assert result is False

    def test_get_assigned_tasks_with_filter(self):
        """Test getting assigned tasks with agent filter (covers lines 298-304)."""
        task1 = self.manager.create_task(name="Task 1", task_type="test")
        task2 = self.manager.create_task(name="Task 2", task_type="test")
        task3 = self.manager.create_task(name="Task 3", task_type="test")

        self.manager.assign_task(task1.task_id, "agent-1")
        self.manager.assign_task(task2.task_id, "agent-1")
        self.manager.assign_task(task3.task_id, "agent-2")

        # Get all assigned tasks
        all_assigned = self.manager.get_assigned_tasks()
        assert len(all_assigned) == 3

        # Get tasks for specific agent
        agent1_tasks = self.manager.get_assigned_tasks(agent_id="agent-1")
        assert len(agent1_tasks) == 2
        assert all(t.assigned_to == "agent-1" for t in agent1_tasks)

        agent2_tasks = self.manager.get_assigned_tasks(agent_id="agent-2")
        assert len(agent2_tasks) == 1
        assert agent2_tasks[0].assigned_to == "agent-2"

    def test_get_next_pending_task_with_stale_entries(self):
        """Test get_next_pending_task cleans up stale queue entries (covers lines 329-336)."""
        task1 = self.manager.create_task(name="Task 1", task_type="test", priority=TaskPriority.LOW)
        task2 = self.manager.create_task(name="Task 2", task_type="test", priority=TaskPriority.HIGH)

        # Assign task2 - this removes it from pending queue
        self.manager.assign_task(task2.task_id, "agent-1")

        # Manually add stale entry to pending queue to simulate corruption
        self.manager._pending_queue.insert(0, "invalid-task-id")

        # get_next_pending_task should skip invalid entry and return task1
        next_task = self.manager.get_next_pending_task()

        assert next_task == task1
        assert "invalid-task-id" not in self.manager._pending_queue

    def test_get_next_pending_task_empty_after_cleanup(self):
        """Test get_next_pending_task returns None when all entries are invalid."""
        # Create and assign a task
        task = self.manager.create_task(name="Task", task_type="test")
        self.manager.assign_task(task.task_id, "agent-1")

        # Manually add only invalid entries
        self.manager._pending_queue = ["invalid-1", "invalid-2"]

        next_task = self.manager.get_next_pending_task()

        assert next_task is None
        assert len(self.manager._pending_queue) == 0
