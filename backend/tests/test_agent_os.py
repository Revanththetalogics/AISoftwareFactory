"""
Tests for AgentOS components.
"""


import pytest

from backend.agent_os.resource_manager import ResourceManager
from backend.agent_os.scheduler import Scheduler
from backend.agent_os.task_queue import TaskQueue
from backend.agent_os.worker_pool import WorkerPool
from backend.models.task import Task, TaskPriority


class TestScheduler:
    """Tests for Scheduler."""

    @pytest.mark.asyncio
    async def test_schedule_task(self):
        """Test scheduling a task."""
        scheduler = Scheduler()

        async def dummy_task():
            return "done"

        task_id = await scheduler.schedule_task(
            name="test_task",
            execute=dummy_task
        )

        assert task_id is not None
        assert task_id in scheduler._scheduled_tasks

    @pytest.mark.asyncio
    async def test_cancel_task(self):
        """Test canceling a task."""
        scheduler = Scheduler()

        async def dummy_task():
            return "done"

        task_id = await scheduler.schedule_task(
            name="test_task",
            execute=dummy_task
        )

        result = await scheduler.cancel_task(task_id)
        assert result is True
        assert task_id not in scheduler._scheduled_tasks


class TestTaskQueue:
    """Tests for TaskQueue."""

    @pytest.mark.asyncio
    async def test_enqueue_task(self):
        """Test enqueueing a task."""
        queue = TaskQueue()
        task = Task(task_id="task-123", name="Test Task", priority=TaskPriority.HIGH)

        task_id = await queue.enqueue(task)

        assert task_id is not None
        assert queue.get_queue_length() == 1

    @pytest.mark.asyncio
    async def test_dequeue_task(self):
        """Test dequeuing a task."""
        queue = TaskQueue()
        task = Task(task_id="task-123", name="Test Task", priority=TaskPriority.HIGH)

        await queue.enqueue(task)
        dequeued = await queue.dequeue()

        assert dequeued is not None
        assert dequeued.name == "Test Task"
        assert queue.get_queue_length() == 0


class TestWorkerPool:
    """Tests for WorkerPool."""

    def test_worker_pool_initialization(self):
        """Test worker pool initialization."""
        pool = WorkerPool(min_workers=2, max_workers=5)

        status = pool.get_pool_status()

        assert status["total_workers"] == 2
        assert status["min_workers"] == 2
        assert status["max_workers"] == 5

    @pytest.mark.asyncio
    async def test_scale_up(self):
        """Test scaling up workers."""
        pool = WorkerPool(min_workers=2, max_workers=5)

        new_workers = await pool.scale_up(2)

        assert len(new_workers) == 2
        assert pool.get_pool_status()["total_workers"] == 4


class TestResourceManager:
    """Tests for ResourceManager."""

    def test_resource_allocation(self):
        """Test resource allocation."""
        manager = ResourceManager()

        result = manager.allocate(
            task_id="task1",
            cpu_cores=2.0,
            memory_mb=1024
        )

        assert result is True

        status = manager.get_status()
        assert status["allocated_tasks"] == 1

    def test_resource_release(self):
        """Test resource release."""
        manager = ResourceManager()

        manager.allocate(task_id="task1", cpu_cores=2.0, memory_mb=1024)
        result = manager.release("task1")

        assert result is True
        assert manager.get_status()["allocated_tasks"] == 0

    def test_insufficient_resources(self):
        """Test allocation with insufficient resources."""
        manager = ResourceManager()

        # Try to allocate more than available
        result = manager.allocate(
            task_id="task1",
            cpu_cores=100.0  # More than total
        )

        assert result is False
