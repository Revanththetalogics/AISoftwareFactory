"""
API Request/Response Models for AI Software Factory.

This module defines Pydantic models for API validation and serialization.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectStatus(str, Enum):
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
    requirements: Optional[str] = Field(None, description="Project requirements")
    tech_stack: Optional[Dict[str, Any]] = Field(None, description="Technology stack preferences")


class ProjectUpdate(BaseModel):
    """Request model for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    requirements: Optional[str] = None
    status: Optional[ProjectStatus] = None
    tech_stack: Optional[Dict[str, Any]] = None


class ProjectResponse(BaseModel):
    """Response model for project data."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    requirements: Optional[str] = None
    status: ProjectStatus
    tech_stack: Optional[Dict[str, Any]] = None
    current_phase: Optional[str] = None
    progress_percent: int = Field(0, ge=0, le=100)
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


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
    phase: Optional[str] = Field(None, description="Specific phase to execute")
    context: Optional[Dict[str, Any]] = Field(None, description="Execution context")
    async_execution: bool = Field(True, description="Execute asynchronously")


class WorkflowStatusResponse(BaseModel):
    """Response model for workflow status."""
    model_config = ConfigDict(from_attributes=True)

    workflow_id: str
    project_id: str
    status: str
    current_phase: Optional[str] = None
    progress_percent: int = Field(0, ge=0, le=100)
    steps_completed: int = 0
    steps_total: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    logs: List[str] = Field(default_factory=list)


class AgentResponse(BaseModel):
    """Response model for agent data."""
    model_config = ConfigDict(from_attributes=True)

    agent_id: str
    name: str
    role: str
    capabilities: List[str]
    status: str
    current_task: Optional[str] = None
    last_active: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentTaskRequest(BaseModel):
    """Request model for assigning a task to an agent."""
    task_type: str
    description: str
    context: Optional[Dict[str, Any]] = None
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
    config: Optional[Dict[str, Any]] = None


class DeploymentResponse(BaseModel):
    """Response model for deployment data."""
    model_config = ConfigDict(from_attributes=True)

    deployment_id: str
    project_id: str
    environment: str
    version: str
    status: str
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    url: Optional[str] = None


class CodeGenerationRequest(BaseModel):
    """Request model for code generation."""
    project_id: str
    component_type: str
    specifications: Dict[str, Any]
    language: str = "python"
    framework: Optional[str] = None


class CodeGenerationResponse(BaseModel):
    """Response model for generated code."""
    generation_id: str
    project_id: str
    files: List[Dict[str, str]]
    language: str
    quality_score: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)


class WebSocketMessage(BaseModel):
    """Model for WebSocket messages."""
    type: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    timestamp: datetime
    components: Dict[str, str]
    uptime_seconds: float
