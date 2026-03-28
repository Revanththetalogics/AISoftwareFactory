"""
API Request/Response Models for AI Software Factory.

This module defines Pydantic models for API validation and serialization.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    data: Any = None
    message: str | None = None
    error: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProjectStatus(StrEnum):
    """Project status values."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ProjectCreate(BaseModel):
    """Request model for creating a project."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "My SaaS App",
            "description": "A revolutionary SaaS application",
            "requirements": "User authentication, dashboard, API",
        }
    })

    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: str = Field(..., min_length=1, description="Project description")
    requirements: str | None = Field(None, description="Project requirements")
    tech_stack: dict[str, Any] | None = Field(None, description="Technology stack preferences")


class ProjectUpdate(BaseModel):
    """Request model for updating a project."""
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    requirements: str | None = None
    status: ProjectStatus | None = None
    tech_stack: dict[str, Any] | None = None


class ProjectResponse(BaseModel):
    """Response model for project data."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    requirements: str | None = None
    status: ProjectStatus
    tech_stack: dict[str, Any] | None = None
    current_phase: str | None = None
    progress_percent: int = Field(0, ge=0, le=100)
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowExecuteRequest(BaseModel):
    """Request model for executing a workflow."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "project_id": "proj-123",
            "phase": "implementation",
            "context": {"priority": "high"},
        }
    })

    project_id: str = Field(..., description="Project ID")
    phase: str | None = Field(None, description="Specific phase to execute")
    context: dict[str, Any] | None = Field(None, description="Execution context")
    async_execution: bool = Field(True, description="Execute asynchronously")


class WorkflowStatusResponse(BaseModel):
    """Response model for workflow status."""
    model_config = ConfigDict(from_attributes=True)

    workflow_id: str
    project_id: str
    status: str
    current_phase: str | None = None
    progress_percent: int = Field(0, ge=0, le=100)
    steps_completed: int = 0
    steps_total: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    logs: list[str] = Field(default_factory=list)


class AgentResponse(BaseModel):
    """Response model for agent data."""
    model_config = ConfigDict(from_attributes=True)

    agent_id: str
    name: str
    role: str
    capabilities: list[str]
    status: str
    current_task: str | None = None
    last_active: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentTaskRequest(BaseModel):
    """Request model for assigning a task to an agent."""
    task_type: str
    description: str
    context: dict[str, Any] | None = None
    priority: str = "medium"


class TaskAssignmentResponse(BaseModel):
    """Response model for task assignment to an agent."""
    model_config = ConfigDict(from_attributes=True)

    task_id: str
    agent_id: str
    status: str
    message: str


class DeploymentRequest(BaseModel):
    """Request model for creating a deployment."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "project_id": "proj-123",
            "environment": "staging",
            "version": "1.0.0",
        }
    })

    project_id: str
    environment: str = Field(..., pattern="^(dev|staging|production)$")
    version: str
    config: dict[str, Any] | None = None


class DeploymentResponse(BaseModel):
    """Response model for deployment data."""
    model_config = ConfigDict(from_attributes=True)

    deployment_id: str
    project_id: str
    environment: str
    version: str
    status: str
    steps: list[dict[str, Any]] = Field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    url: str | None = None


class CodeGenerationRequest(BaseModel):
    """Request model for code generation."""
    project_id: str
    component_type: str
    specifications: dict[str, Any]
    language: str = "python"
    framework: str | None = None


class CodeGenerationResponse(BaseModel):
    """Response model for generated code."""
    generation_id: str
    project_id: str
    files: list[dict[str, str]]
    language: str
    quality_score: float | None = None
    warnings: list[str] = Field(default_factory=list)


class WebSocketMessage(BaseModel):
    """Model for WebSocket messages."""
    type: str
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    timestamp: datetime
    components: dict[str, str]
    uptime_seconds: float


class QuickStartRequest(BaseModel):
    """Request model for single-prompt SaaS creation."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "idea": "A SaaS platform for managing freelance projects with time tracking and invoicing",
            "template": "saas_starter",
            "tech_stack": {"frontend": "nextjs", "backend": "fastapi"}
        }
    })

    idea: str = Field(..., min_length=10, description="Your SaaS idea/prompt")
    template: str | None = Field(None, description="Optional template to use")
    tech_stack: dict[str, Any] | None = Field(None, description="Technology stack preferences")


class QuickStartResponse(BaseModel):
    """Response model for QuickStart endpoint."""
    model_config = ConfigDict(from_attributes=True)

    project_id: str
    workflow_id: str
    message: str
    status: str
