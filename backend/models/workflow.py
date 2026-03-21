"""
Workflow data models for AI Software Factory.

This module defines Pydantic models for workflow management, including
workflow definitions, steps, triggers, and execution state.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class WorkflowStatus(StrEnum):
    """Status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowTrigger(StrEnum):
    """Types of workflow triggers."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    WEBHOOK = "webhook"
    EVENT = "event"


class WorkflowStep(BaseModel):
    """
    A single step in a workflow.

    Attributes:
        step_id: Unique identifier for the step
        name: Human-readable name
        description: Detailed description
        agent_role: Role of agent to execute this step
        crew_type: Type of crew to use
        dependencies: List of step IDs that must complete before this step
        config: Step-specific configuration
        timeout_seconds: Maximum execution time
        retry_count: Number of retry attempts
    """
    step_id: str = Field(..., description="Unique step identifier")
    name: str = Field(..., description="Step name")
    description: str = Field(default="", description="Step description")
    agent_role: str | None = Field(default=None, description="Agent role for execution")
    crew_type: str | None = Field(default=None, description="Crew type to use")
    dependencies: list[str] = Field(default_factory=list, description="Dependent step IDs")
    config: dict[str, Any] = Field(default_factory=dict, description="Step configuration")
    timeout_seconds: int = Field(default=300, description="Execution timeout")
    retry_count: int = Field(default=3, description="Retry attempts")


class Workflow(BaseModel):
    """
    Workflow definition and execution state.

    Attributes:
        workflow_id: Unique identifier
        name: Workflow name
        description: Workflow description
        version: Workflow version
        status: Current execution status
        trigger: How the workflow was triggered
        project_id: Associated project ID
        steps: List of workflow steps
        current_step_id: Currently executing step
        completed_steps: List of completed step IDs
        failed_steps: List of failed step IDs
        context: Workflow execution context/data
        started_at: When workflow started
        completed_at: When workflow completed
        created_by: User who created the workflow
        metadata: Additional metadata
    """
    workflow_id: str = Field(..., description="Unique workflow identifier")
    name: str = Field(..., description="Workflow name")
    description: str = Field(default="", description="Workflow description")
    version: str = Field(default="1.0.0", description="Workflow version")
    status: WorkflowStatus = Field(default=WorkflowStatus.PENDING, description="Current status")
    trigger: WorkflowTrigger = Field(default=WorkflowTrigger.MANUAL, description="Trigger type")
    project_id: str | None = Field(default=None, description="Associated project ID")
    steps: list[WorkflowStep] = Field(default_factory=list, description="Workflow steps")
    current_step_id: str | None = Field(default=None, description="Current step ID")
    completed_steps: list[str] = Field(default_factory=list, description="Completed step IDs")
    failed_steps: list[str] = Field(default_factory=list, description="Failed step IDs")
    context: dict[str, Any] = Field(default_factory=dict, description="Execution context")
    started_at: datetime | None = Field(default=None, description="Start timestamp")
    completed_at: datetime | None = Field(default=None, description="Completion timestamp")
    created_by: str | None = Field(default=None, description="Creator user ID")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def is_complete(self) -> bool:
        """Check if workflow is complete."""
        return self.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]

    def can_execute(self) -> bool:
        """Check if workflow can be executed."""
        return self.status in [WorkflowStatus.PENDING, WorkflowStatus.PAUSED]

    def get_next_steps(self) -> list[WorkflowStep]:
        """Get steps that are ready to execute (dependencies met)."""
        ready = []
        for step in self.steps:
            if step.step_id in self.completed_steps or step.step_id in self.failed_steps:
                continue
            if all(dep in self.completed_steps for dep in step.dependencies):
                ready.append(step)
        return ready

    def get_progress_percent(self) -> float:
        """Calculate workflow completion percentage."""
        if not self.steps:
            return 0.0
        return (len(self.completed_steps) / len(self.steps)) * 100
