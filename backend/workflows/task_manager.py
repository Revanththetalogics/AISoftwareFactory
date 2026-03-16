"""
Task Manager for Workflow Engine.

This module provides task queue management, task assignment, and status tracking
for workflow tasks.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.core.logging import get_logger

logger = get_logger(__name__)


class TaskPriority(int, Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowTask:
    """
    Task definition for workflow execution.
    
    Attributes:
        task_id: Unique task identifier
        name: Task name
        description: Task description
        task_type: Type of task
        priority: Task priority
        status: Current status
        assigned_to: ID of assigned agent
        project_id: Associated project ID
        phase: Workflow phase
        context: Task context data
        created_at: Creation timestamp
        started_at: Start timestamp
        completed_at: Completion timestamp
        result: Task result
        error: Error message if failed
    """
    task_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    task_type: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    project_id: Optional[str] = None
    phase: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type,
            "priority": self.priority.value,
            "status": self.status.value,
            "assigned_to": self.assigned_to,
            "project_id": self.project_id,
            "phase": self.phase,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
        }


class TaskManager:
    """
    Manager for workflow tasks.
    
    This class provides:
    - Task queue management
    - Task assignment to agents
    - Task status tracking
    - Priority-based scheduling
    
    Example:
        >>> manager = TaskManager()
        >>> task = manager.create_task(
        ...     name="Design API",
        ...     task_type="api_design",
        ...     priority=TaskPriority.HIGH,
        ... )
        >>> manager.assign_task(task.task_id, "agent-123")
    """
    
    def __init__(self):
        """Initialize the task manager."""
        self._tasks: Dict[str, WorkflowTask] = {}
        self._pending_queue: List[str] = []
        self._assigned_tasks: Dict[str, str] = {}  # task_id -> agent_id
        self._logger = get_logger(__name__)
    
    def create_task(
        self,
        name: str,
        description: str = "",
        task_type: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        project_id: Optional[str] = None,
        phase: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> WorkflowTask:
        """
        Create a new task.
        
        Args:
            name: Task name
            description: Task description
            task_type: Type of task
            priority: Task priority
            project_id: Associated project ID
            phase: Workflow phase
            context: Task context
            
        Returns:
            Created task
        """
        task = WorkflowTask(
            name=name,
            description=description,
            task_type=task_type,
            priority=priority,
            project_id=project_id,
            phase=phase,
            context=context or {},
        )
        
        self._tasks[task.task_id] = task
        self._pending_queue.append(task.task_id)
        self._sort_pending_queue()
        
        self._logger.info(
            "Task created",
            task_id=task.task_id,
            name=task.name,
            priority=task.priority.value,
        )
        
        return task
    
    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """
        Assign a task to an agent.
        
        Args:
            task_id: Task ID
            agent_id: Agent ID
            
        Returns:
            True if assignment successful
        """
        task = self._tasks.get(task_id)
        if not task:
            self._logger.error("Task not found", task_id=task_id)
            return False
        
        if task.status != TaskStatus.PENDING:
            self._logger.warning(
                "Task not in pending state",
                task_id=task_id,
                status=task.status.value,
            )
            return False
        
        task.assigned_to = agent_id
        task.status = TaskStatus.ASSIGNED
        task.started_at = datetime.now()
        
        self._assigned_tasks[task_id] = agent_id
        if task_id in self._pending_queue:
            self._pending_queue.remove(task_id)
        
        self._logger.info(
            "Task assigned",
            task_id=task_id,
            agent_id=agent_id,
        )
        
        return True
    
    def complete_task(
        self,
        task_id: str,
        result: Dict[str, Any],
    ) -> bool:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task ID
            result: Task result
            
        Returns:
            True if successful
        """
        task = self._tasks.get(task_id)
        if not task:
            return False
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.result = result
        
        if task_id in self._assigned_tasks:
            del self._assigned_tasks[task_id]
        
        self._logger.info(
            "Task completed",
            task_id=task_id,
            task_name=task.name,
        )
        
        return True
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """
        Mark a task as failed.
        
        Args:
            task_id: Task ID
            error: Error message
            
        Returns:
            True if successful
        """
        task = self._tasks.get(task_id)
        if not task:
            return False
        
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.now()
        task.error = error
        
        if task_id in self._assigned_tasks:
            del self._assigned_tasks[task_id]
        
        self._logger.error(
            "Task failed",
            task_id=task_id,
            task_name=task.name,
            error=error,
        )
        
        return True
    
    def get_task(self, task_id: str) -> Optional[WorkflowTask]:
        """Get a task by ID."""
        return self._tasks.get(task_id)
    
    def get_pending_tasks(self) -> List[WorkflowTask]:
        """Get all pending tasks sorted by priority."""
        return [
            self._tasks[task_id]
            for task_id in self._pending_queue
            if task_id in self._tasks
        ]
    
    def get_assigned_tasks(self, agent_id: Optional[str] = None) -> List[WorkflowTask]:
        """
        Get assigned tasks.
        
        Args:
            agent_id: Filter by agent ID (optional)
            
        Returns:
            List of assigned tasks
        """
        tasks = []
        for task_id, assigned_agent_id in self._assigned_tasks.items():
            if agent_id is None or assigned_agent_id == agent_id:
                task = self._tasks.get(task_id)
                if task:
                    tasks.append(task)
        return tasks
    
    def get_tasks_by_project(self, project_id: str) -> List[WorkflowTask]:
        """Get all tasks for a project."""
        return [
            task for task in self._tasks.values()
            if task.project_id == project_id
        ]
    
    def get_tasks_by_phase(self, phase: str) -> List[WorkflowTask]:
        """Get all tasks for a phase."""
        return [
            task for task in self._tasks.values()
            if task.phase == phase
        ]
    
    def _sort_pending_queue(self) -> None:
        """Sort pending queue by priority (highest first)."""
        self._pending_queue.sort(
            key=lambda task_id: self._tasks[task_id].priority.value,
            reverse=True,
        )
    
    def get_next_pending_task(self) -> Optional[WorkflowTask]:
        """Get the next pending task (highest priority)."""
        while self._pending_queue:
            task_id = self._pending_queue[0]
            task = self._tasks.get(task_id)
            if task and task.status == TaskStatus.PENDING:
                return task
            # Remove invalid entries
            self._pending_queue.pop(0)
        return None
    
    def get_stats(self) -> Dict[str, int]:
        """Get task statistics."""
        stats = {
            "total": len(self._tasks),
            "pending": 0,
            "assigned": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }
        
        for task in self._tasks.values():
            stats[task.status.value] += 1
        
        return stats
