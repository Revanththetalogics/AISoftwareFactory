"""
Task data models for AI Software Factory.

This module defines Pydantic models for task management, including
task definitions, status tracking, and execution results.
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    """Status of a task execution."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(int, Enum):
    """Priority levels for tasks."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class TaskResult(BaseModel):
    """
    Result of a task execution.

    Attributes:
        success: Whether the task succeeded
        output: Task output data
        error: Error message if failed
        logs: Execution logs
        artifacts: Generated artifacts
        metrics: Performance metrics
        started_at: When execution started
        completed_at: When execution completed
    """

    success: bool = Field(..., description="Whether task succeeded")
    output: dict[str, Any] = Field(default_factory=dict, description="Task output")
    error: str | None = Field(default=None, description="Error message")
    logs: list[str] = Field(default_factory=list, description="Execution logs")
    artifacts: list[dict[str, Any]] = Field(default_factory=list, description="Generated artifacts")
    metrics: dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    started_at: datetime | None = Field(default=None, description="Start timestamp")
    completed_at: datetime | None = Field(default=None, description="Completion timestamp")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Task(BaseModel):
    """
    Task definition and execution state.

    Attributes:
        task_id: Unique identifier
        name: Task name
        description: Task description
        status: Current execution status
        priority: Task priority level
        project_id: Associated project ID
        workflow_id: Parent workflow ID
        step_id: Workflow step ID
        agent_id: Assigned agent ID
        crew_type: Crew type for execution
        input_data: Input parameters
        result: Execution result
        dependencies: Task IDs that must complete first
        retry_count: Current retry attempt
        max_retries: Maximum retry attempts
        timeout_seconds: Execution timeout
        scheduled_at: When to execute
        started_at: When execution started
        completed_at: When execution completed
        created_by: User who created the task
        metadata: Additional metadata
    """

    task_id: str = Field(..., description="Unique task identifier")
    name: str = Field(..., description="Task name")
    description: str = Field(default="", description="Task description")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    project_id: str | None = Field(default=None, description="Associated project ID")
    workflow_id: str | None = Field(default=None, description="Parent workflow ID")
    step_id: str | None = Field(default=None, description="Workflow step ID")
    agent_id: str | None = Field(default=None, description="Assigned agent ID")
    crew_type: str | None = Field(default=None, description="Crew type for execution")
    input_data: dict[str, Any] = Field(default_factory=dict, description="Input parameters")
    result: TaskResult | None = Field(default=None, description="Execution result")
    dependencies: list[str] = Field(default_factory=list, description="Dependent task IDs")
    retry_count: int = Field(default=0, description="Current retry attempt")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout_seconds: int = Field(default=300, description="Execution timeout")
    scheduled_at: datetime | None = Field(default=None, description="Scheduled timestamp")
    started_at: datetime | None = Field(default=None, description="Start timestamp")
    completed_at: datetime | None = Field(default=None, description="Completion timestamp")
    created_by: str | None = Field(default=None, description="Creator user ID")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def is_complete(self) -> bool:
        """Check if task is complete."""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]

    def can_execute(self) -> bool:
        """Check if task can be executed."""
        return self.status in [TaskStatus.PENDING, TaskStatus.QUEUED]

    def should_retry(self) -> bool:
        """Check if task should be retried."""
        if self.status != TaskStatus.FAILED:
            return False
        return self.retry_count < self.max_retries

    def get_duration_seconds(self) -> float | None:
        """Calculate task execution duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
