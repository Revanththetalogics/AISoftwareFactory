"""
Task scheduler for AgentOS.

This module provides scheduling capabilities for agent tasks with support for
cron-like scheduling, priority-based execution, and dependency resolution.
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ScheduledTask:
    """A scheduled task with metadata."""
    task_id: str
    name: str
    scheduled_at: datetime
    priority: int
    execute: Callable
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class Scheduler:
    """
    Task scheduler for agent execution.

    Provides cron-like scheduling, priority-based execution, and
    dependency resolution for tasks.
    """

    def __init__(self):
        """Initialize the scheduler."""
        self._scheduled_tasks: dict[str, ScheduledTask] = {}
        self._running = False
        self._task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._logger = get_logger(__name__)

    async def schedule_task(
        self,
        name: str,
        execute: Callable,
        scheduled_at: datetime | None = None,
        priority: int = 5,
        dependencies: list[str] | None = None,
        metadata: dict[str, Any] | None = None
    ) -> str:
        """
        Schedule a task for execution.

        Args:
            name: Task name
            execute: Function to execute
            scheduled_at: When to execute (None for immediate)
            priority: Priority (1-10, lower is higher)
            dependencies: Task IDs that must complete first
            metadata: Additional metadata

        Returns:
            Task ID
        """
        task_id = str(uuid4())

        task = ScheduledTask(
            task_id=task_id,
            name=name,
            scheduled_at=scheduled_at or datetime.utcnow(),
            priority=priority,
            execute=execute,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )

        self._scheduled_tasks[task_id] = task
        await self._task_queue.put((priority, scheduled_at or datetime.utcnow(), task_id))

        self._logger.info("Task scheduled", task_id=task_id, name=name)
        return task_id

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a scheduled task.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if cancelled, False if not found
        """
        if task_id in self._scheduled_tasks:
            del self._scheduled_tasks[task_id]
            self._logger.info("Task cancelled", task_id=task_id)
            return True
        return False

    async def get_ready_tasks(self) -> list[ScheduledTask]:
        """
        Get tasks that are ready to execute.

        Returns:
            List of ready tasks
        """
        now = datetime.utcnow()
        ready = []

        for task in self._scheduled_tasks.values():
            if task.scheduled_at <= now:
                # Check dependencies
                deps_met = all(
                    dep not in self._scheduled_tasks
                    for dep in task.dependencies
                )
                if deps_met:
                    ready.append(task)

        return sorted(ready, key=lambda t: t.priority)

    async def start(self):
        """Start the scheduler."""
        self._running = True
        self._logger.info("Scheduler started")

        while self._running:
            try:
                ready_tasks = await self.get_ready_tasks()

                for task in ready_tasks:
                    try:
                        await task.execute()
                        await self.cancel_task(task.task_id)
                    except Exception as e:
                        self._logger.error(
                            "Task execution failed",
                            task_id=task.task_id,
                            error=str(e)
                        )

                await asyncio.sleep(1)
            except Exception as e:
                self._logger.error("Scheduler error", error=str(e))
                await asyncio.sleep(5)

    def stop(self):
        """Stop the scheduler."""
        self._running = False
        self._logger.info("Scheduler stopped")
