"""
Worker pool for AgentOS.

This module provides worker process management with dynamic scaling
and health monitoring.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Worker:
    """A worker process."""

    worker_id: str
    name: str
    status: str = "idle"  # idle, busy, unhealthy
    current_task: str | None = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    total_tasks: int = 0
    failed_tasks: int = 0


class WorkerPool:
    """
    Worker pool for agent task execution.

    Provides dynamic worker scaling, health monitoring, and
    graceful shutdown capabilities.
    """

    def __init__(self, min_workers: int = 2, max_workers: int = 10):
        """
        Initialize the worker pool.

        Args:
            min_workers: Minimum number of workers
            max_workers: Maximum number of workers
        """
        self._min_workers = min_workers
        self._max_workers = max_workers
        self._workers: dict[str, Worker] = {}
        self._running = False
        self._logger = get_logger(__name__)

        # Initialize minimum workers
        for i in range(min_workers):
            self._create_worker(f"worker-{i + 1}")

    def _create_worker(self, name: str) -> Worker:
        """Create a new worker."""
        worker = Worker(worker_id=str(uuid4()), name=name)
        self._workers[worker.worker_id] = worker
        self._logger.info("Worker created", worker_id=worker.worker_id, name=name)
        return worker

    async def scale_up(self, count: int = 1) -> list[Worker]:
        """
        Scale up the worker pool.

        Args:
            count: Number of workers to add

        Returns:
            List of new workers
        """
        new_workers = []
        current_count = len(self._workers)

        for i in range(count):
            if current_count + i >= self._max_workers:
                break
            worker = self._create_worker(f"worker-{current_count + i + 1}")
            new_workers.append(worker)

        self._logger.info("Worker pool scaled up", added=len(new_workers), total=len(self._workers))
        return new_workers

    async def scale_down(self, count: int = 1) -> int:
        """
        Scale down the worker pool.

        Args:
            count: Number of workers to remove

        Returns:
            Number of workers removed
        """
        removed = 0
        idle_workers = [w for w in self._workers.values() if w.status == "idle"]

        for worker in idle_workers[:count]:
            if len(self._workers) <= self._min_workers:
                break
            del self._workers[worker.worker_id]
            removed += 1

        self._logger.info("Worker pool scaled down", removed=removed, total=len(self._workers))
        return removed

    def get_available_worker(self) -> Worker | None:
        """
        Get an available (idle) worker.

        Returns:
            Available worker or None
        """
        for worker in self._workers.values():
            if worker.status == "idle":
                return worker
        return None

    def assign_task(self, worker_id: str, task_id: str) -> bool:
        """
        Assign a task to a worker.

        Args:
            worker_id: Worker ID
            task_id: Task ID

        Returns:
            True if assigned, False otherwise
        """
        worker = self._workers.get(worker_id)
        if not worker or worker.status != "idle":
            return False

        worker.status = "busy"
        worker.current_task = task_id
        return True

    def release_worker(self, worker_id: str, success: bool = True):
        """
        Release a worker from its task.

        Args:
            worker_id: Worker ID
            success: Whether task succeeded
        """
        worker = self._workers.get(worker_id)
        if worker:
            worker.status = "idle"
            worker.current_task = None
            worker.total_tasks += 1
            if not success:
                worker.failed_tasks += 1

    def get_pool_status(self) -> dict[str, Any]:
        """
        Get worker pool status.

        Returns:
            Pool status dictionary
        """
        status = {
            "total_workers": len(self._workers),
            "idle_workers": sum(1 for w in self._workers.values() if w.status == "idle"),
            "busy_workers": sum(1 for w in self._workers.values() if w.status == "busy"),
            "unhealthy_workers": sum(1 for w in self._workers.values() if w.status == "unhealthy"),
            "min_workers": self._min_workers,
            "max_workers": self._max_workers,
        }
        return status

    async def shutdown(self):
        """Shutdown the worker pool gracefully."""
        self._logger.info("Worker pool shutting down")

        # Wait for busy workers to complete
        while any(w.status == "busy" for w in self._workers.values()):
            await asyncio.sleep(1)

        self._workers.clear()
        self._logger.info("Worker pool shutdown complete")
