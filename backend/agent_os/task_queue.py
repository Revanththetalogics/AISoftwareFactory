"""
Task queue for AgentOS.

This module provides Redis-based task queue management for distributed task processing.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.core.logging import get_logger
from backend.models.task import Task, TaskStatus, TaskPriority

logger = get_logger(__name__)


class TaskQueue:
    """
    Task queue for agent task distribution.
    
    Provides queue management with support for priority queues,
    dead letter queues, and separate queues for different agent types.
    """
    
    def __init__(self, redis_client=None):
        """
        Initialize the task queue.
        
        Args:
            redis_client: Optional Redis client for persistence
        """
        self._redis = redis_client
        self._queues: Dict[str, List[Task]] = {
            "default": [],
            "high_priority": [],
            "langgraph": [],
            "crewai": [],
            "dead_letter": []
        }
        self._logger = get_logger(__name__)
    
    async def enqueue(
        self,
        task: Task,
        queue_name: str = "default"
    ) -> str:
        """
        Add a task to the queue.
        
        Args:
            task: Task to enqueue
            queue_name: Queue to add to
            
        Returns:
            Task ID
        """
        if queue_name not in self._queues:
            queue_name = "default"
        
        task.status = TaskStatus.QUEUED
        self._queues[queue_name].append(task)
        
        # Sort by priority
        self._queues[queue_name].sort(key=lambda t: t.priority.value)
        
        self._logger.info(
            "Task enqueued",
            task_id=task.task_id,
            queue=queue_name,
            priority=task.priority.name
        )
        
        return task.task_id
    
    async def dequeue(
        self,
        queue_name: str = "default"
    ) -> Optional[Task]:
        """
        Get the next task from the queue.
        
        Args:
            queue_name: Queue to dequeue from
            
        Returns:
            Next task or None if queue is empty
        """
        if queue_name not in self._queues:
            return None
        
        queue = self._queues[queue_name]
        if not queue:
            return None
        
        # Get highest priority task
        task = queue.pop(0)
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        
        self._logger.info(
            "Task dequeued",
            task_id=task.task_id,
            queue=queue_name
        )
        
        return task
    
    async def complete_task(
        self,
        task: Task,
        success: bool = True
    ):
        """
        Mark a task as complete.
        
        Args:
            task: Task to complete
            success: Whether task succeeded
        """
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        task.completed_at = datetime.utcnow()
        
        self._logger.info(
            "Task completed",
            task_id=task.task_id,
            success=success
        )
    
    async def move_to_dead_letter(self, task: Task):
        """
        Move a failed task to dead letter queue.
        
        Args:
            task: Task to move
        """
        task.status = TaskStatus.FAILED
        self._queues["dead_letter"].append(task)
        
        self._logger.warning(
            "Task moved to dead letter queue",
            task_id=task.task_id
        )
    
    def get_queue_length(self, queue_name: str = "default") -> int:
        """
        Get the length of a queue.
        
        Args:
            queue_name: Queue name
            
        Returns:
            Number of tasks in queue
        """
        return len(self._queues.get(queue_name, []))
    
    def get_all_queues_status(self) -> Dict[str, int]:
        """
        Get status of all queues.
        
        Returns:
            Dictionary of queue names and lengths
        """
        return {name: len(queue) for name, queue in self._queues.items()}
