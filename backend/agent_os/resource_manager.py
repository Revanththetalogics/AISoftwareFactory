"""
Resource manager for AgentOS.

This module provides resource allocation and management for agent execution.
"""

from dataclasses import dataclass
from typing import Any, Dict

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ResourceAllocation:
    """Resource allocation for a task."""
    cpu_cores: float
    memory_mb: int
    gpu_count: int = 0
    storage_mb: int = 0


class ResourceManager:
    """
    Resource manager for agent execution.

    Provides resource allocation, monitoring, and limits enforcement.
    """

    def __init__(self):
        """Initialize the resource manager."""
        self._total_resources = ResourceAllocation(
            cpu_cores=8.0,
            memory_mb=16384,
            gpu_count=1,
            storage_mb=102400
        )
        self._allocated: Dict[str, ResourceAllocation] = {}
        self._logger = get_logger(__name__)

    def allocate(
        self,
        task_id: str,
        cpu_cores: float = 1.0,
        memory_mb: int = 512,
        gpu_count: int = 0,
        storage_mb: int = 1024
    ) -> bool:
        """
        Allocate resources for a task.

        Args:
            task_id: Task ID
            cpu_cores: CPU cores needed
            memory_mb: Memory needed in MB
            gpu_count: GPUs needed
            storage_mb: Storage needed in MB

        Returns:
            True if allocated, False if insufficient resources
        """
        available = self.get_available_resources()

        if (cpu_cores > available.cpu_cores or
            memory_mb > available.memory_mb or
            gpu_count > available.gpu_count or
            storage_mb > available.storage_mb):
            self._logger.warning(
                "Insufficient resources",
                task_id=task_id,
                requested={"cpu": cpu_cores, "memory": memory_mb}
            )
            return False

        self._allocated[task_id] = ResourceAllocation(
            cpu_cores=cpu_cores,
            memory_mb=memory_mb,
            gpu_count=gpu_count,
            storage_mb=storage_mb
        )

        self._logger.info("Resources allocated", task_id=task_id)
        return True

    def release(self, task_id: str) -> bool:
        """
        Release resources for a task.

        Args:
            task_id: Task ID

        Returns:
            True if released, False if not found
        """
        if task_id in self._allocated:
            del self._allocated[task_id]
            self._logger.info("Resources released", task_id=task_id)
            return True
        return False

    def get_available_resources(self) -> ResourceAllocation:
        """
        Get available resources.

        Returns:
            Available resource allocation
        """
        used_cpu = sum(r.cpu_cores for r in self._allocated.values())
        used_memory = sum(r.memory_mb for r in self._allocated.values())
        used_gpu = sum(r.gpu_count for r in self._allocated.values())
        used_storage = sum(r.storage_mb for r in self._allocated.values())

        return ResourceAllocation(
            cpu_cores=self._total_resources.cpu_cores - used_cpu,
            memory_mb=self._total_resources.memory_mb - used_memory,
            gpu_count=self._total_resources.gpu_count - used_gpu,
            storage_mb=self._total_resources.storage_mb - used_storage
        )

    def get_status(self) -> Dict[str, Any]:
        """
        Get resource status.

        Returns:
            Resource status dictionary
        """
        available = self.get_available_resources()
        return {
            "total": {
                "cpu_cores": self._total_resources.cpu_cores,
                "memory_mb": self._total_resources.memory_mb,
                "gpu_count": self._total_resources.gpu_count,
                "storage_mb": self._total_resources.storage_mb
            },
            "available": {
                "cpu_cores": available.cpu_cores,
                "memory_mb": available.memory_mb,
                "gpu_count": available.gpu_count,
                "storage_mb": available.storage_mb
            },
            "allocated_tasks": len(self._allocated)
        }
