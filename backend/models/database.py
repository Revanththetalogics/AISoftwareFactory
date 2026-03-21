"""
Database Models for AI Software Factory.

This module defines SQLAlchemy models for core entities including:
- Users
- Projects
- Workflows
- Tasks
- Agents
"""

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db.base import Base
from backend.models.task import TaskPriority, TaskStatus
from backend.models.workflow import WorkflowStatus, WorkflowTrigger


class DBUser(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_superuser = Column(Boolean, default=False, nullable=False)
    permissions = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True))

    # Relationships
    projects = relationship("DBProject", back_populates="owner")
    workflows = relationship("DBWorkflow", back_populates="created_by_user")
    tasks = relationship("DBTask", back_populates="created_by_user")

    __table_args__ = (
        Index('idx_users_username', 'username'),
        Index('idx_users_email', 'email'),
        Index('idx_users_active', 'is_active'),
    )


class DBProject(Base):
    """Project model representing a software development project."""
    __tablename__ = "projects"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    requirements = Column(Text)
    status = Column(String(20), default="draft", nullable=False)
    tech_stack = Column(JSON)
    current_phase = Column(String(50))
    progress_percent = Column(Integer, default=0)
    extra_metadata = Column(JSON, default=dict)  # Renamed from 'metadata'
    owner_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    owner = relationship("DBUser", back_populates="projects")
    workflows = relationship("DBWorkflow", back_populates="project")
    tasks = relationship("DBTask", back_populates="project")

    __table_args__ = (
        Index('idx_projects_owner', 'owner_id'),
        Index('idx_projects_status', 'status'),
        Index('idx_projects_created', 'created_at'),
        Index('idx_projects_name_trgm', 'name', postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'}),  # For text search
    )


class DBWorkflow(Base):
    """Workflow model representing an automated process."""
    __tablename__ = "workflows"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    version = Column(String(20), default="1.0.0")
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.PENDING, nullable=False)
    trigger = Column(Enum(WorkflowTrigger), default=WorkflowTrigger.MANUAL, nullable=False)
    project_id = Column(String(50), ForeignKey("projects.id"), nullable=False)
    steps = Column(JSON, default=list)  # Store steps as JSON for flexibility
    current_step_id = Column(String(50))
    completed_steps = Column(JSON, default=list)
    failed_steps = Column(JSON, default=list)
    context = Column(JSON, default=dict)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_by = Column(String(50), ForeignKey("users.id"))
    extra_metadata = Column(JSON, default=dict)  # Renamed from 'metadata'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("DBProject", back_populates="workflows")
    created_by_user = relationship("DBUser", back_populates="workflows")
    tasks = relationship("DBTask", back_populates="workflow")

    __table_args__ = (
        Index('idx_workflows_project', 'project_id'),
        Index('idx_workflows_status', 'status'),
        Index('idx_workflows_created_by', 'created_by'),
        Index('idx_workflows_created', 'created_at'),
    )


class DBTask(Base):
    """Task model representing a unit of work."""
    __tablename__ = "tasks"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    project_id = Column(String(50), ForeignKey("projects.id"))
    workflow_id = Column(String(50), ForeignKey("workflows.id"))
    step_id = Column(String(50))
    agent_id = Column(String(50))
    crew_type = Column(String(50))
    input_data = Column(JSON, default=dict)
    result = Column(JSON)  # Store TaskResult as JSON
    dependencies = Column(JSON, default=list)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=300)
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_by = Column(String(50), ForeignKey("users.id"))
    extra_metadata = Column(JSON, default=dict)  # Renamed from 'metadata'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("DBProject", back_populates="tasks")
    workflow = relationship("DBWorkflow", back_populates="tasks")
    created_by_user = relationship("DBUser", back_populates="tasks")

    __table_args__ = (
        Index('idx_tasks_project', 'project_id'),
        Index('idx_tasks_workflow', 'workflow_id'),
        Index('idx_tasks_status', 'status'),
        Index('idx_tasks_priority', 'priority'),
        Index('idx_tasks_created_by', 'created_by'),
        Index('idx_tasks_scheduled', 'scheduled_at'),
        Index('idx_tasks_created', 'created_at'),
    )


class DBAgent(Base):
    """Agent model representing an AI agent."""
    __tablename__ = "agents"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    description = Column(Text)
    capabilities = Column(JSON, default=list)
    status = Column(String(20), default="idle", nullable=False)
    current_task_id = Column(String(50))
    last_active = Column(DateTime(timezone=True))
    config = Column(JSON, default=dict)
    extra_metadata = Column(JSON, default=dict)  # Renamed from 'metadata'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_agents_role', 'role'),
        Index('idx_agents_status', 'status'),
        Index('idx_agents_current_task', 'current_task_id'),
    )


class DBDeployment(Base):
    """Deployment model representing application deployments."""
    __tablename__ = "deployments"

    id = Column(String(50), primary_key=True, index=True)
    project_id = Column(String(50), ForeignKey("projects.id"), nullable=False)
    environment = Column(String(20), nullable=False)  # dev, staging, production
    version = Column(String(50), nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    config = Column(JSON, default=dict)
    steps = Column(JSON, default=list)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    url = Column(String(255))
    created_by = Column(String(50), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_deployments_project', 'project_id'),
        Index('idx_deployments_environment', 'environment'),
        Index('idx_deployments_status', 'status'),
        Index('idx_deployments_created', 'created_at'),
        UniqueConstraint('project_id', 'environment', 'version', name='uq_project_env_version'),
    )


# Audit trail model for tracking changes
class DBAuditLog(Base):
    """Audit log model for tracking system changes."""
    __tablename__ = "audit_logs"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id"))
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    resource_type = Column(String(50), nullable=False)  # project, workflow, task, etc.
    resource_id = Column(String(50), nullable=False)
    details = Column(JSON)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_auditlogs_user', 'user_id'),
        Index('idx_auditlogs_resource', 'resource_type', 'resource_id'),
        Index('idx_auditlogs_action', 'action'),
        Index('idx_auditlogs_created', 'created_at'),
    )


# Model imports for alembic
__all__ = [
    "DBUser",
    "DBProject",
    "DBWorkflow",
    "DBTask",
    "DBAgent",
    "DBDeployment",
    "DBAuditLog",
]
