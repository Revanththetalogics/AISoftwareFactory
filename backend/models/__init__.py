"""
Data models for AI Software Factory backend.

This module contains Pydantic models for workflows, tasks, and other data structures
used throughout the application. It also exports SQLAlchemy ORM models for database
operations and Alembic migration discovery.
"""

# Pydantic models for API/validation
from backend.models.workflow import (
    Workflow,
    WorkflowStatus,
    WorkflowStep,
    WorkflowTrigger,
)
from backend.models.task import (
    Task,
    TaskStatus,
    TaskPriority,
    TaskResult,
)

# SQLAlchemy ORM models for database operations
# These are imported to ensure Alembic can discover all models
from backend.models.database import (
    DBUser,
    DBProject,
    DBWorkflow,
    DBTask,
    DBAgent,
    DBDeployment,
    DBAuditLog,
)

__all__ = [
    # Pydantic workflow models
    "Workflow",
    "WorkflowStatus",
    "WorkflowStep",
    "WorkflowTrigger",
    # Pydantic task models
    "Task",
    "TaskStatus",
    "TaskPriority",
    "TaskResult",
    # SQLAlchemy ORM models
    "DBUser",
    "DBProject",
    "DBWorkflow",
    "DBTask",
    "DBAgent",
    "DBDeployment",
    "DBAuditLog",
]
