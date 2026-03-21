"""
Enhanced Logging Utilities for AI Software Factory.

This module provides advanced logging capabilities including:
- Performance timing decorators
- Business event logging
- Audit trail logging
- Error context enrichment
"""

import asyncio
import functools
import time
from typing import Any, Callable, Dict, Optional

from backend.core.logging import get_logger

logger = get_logger(__name__)


class PerformanceTimer:
    """
    Context manager for timing operations and logging performance metrics.

    Usage:
        with PerformanceTimer("database_query", project_id="123") as timer:
            # Some operation
            result = expensive_operation()
            timer.set_result_metadata(rows_affected=len(result))
    """

    def __init__(self, operation_name: str, **context):
        self.operation_name = operation_name
        self.context = context
        self.start_time = None
        self.end_time = None
        self.result_metadata = {}

    def __enter__(self):
        self.start_time = time.perf_counter()
        logger.info(
            f"Starting {self.operation_name}",
            operation=self.operation_name,
            **self.context
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        duration_ms = (self.end_time - self.start_time) * 1000

        if exc_type is not None:
            logger.error(
                f"Operation {self.operation_name} failed",
                operation=self.operation_name,
                duration_ms=round(duration_ms, 2),
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                **self.context
            )
        else:
            logger.info(
                f"Operation {self.operation_name} completed",
                operation=self.operation_name,
                duration_ms=round(duration_ms, 2),
                **self.result_metadata,
                **self.context
            )

    def set_result_metadata(self, **metadata):
        """Add metadata about the operation result."""
        self.result_metadata.update(metadata)


def timed_operation(operation_name: str):
    """
    Decorator for timing function execution.

    Usage:
        @timed_operation("user_authentication")
        async def authenticate_user(username: str, password: str):
            # Authentication logic
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with PerformanceTimer(operation_name, function=func.__name__) as timer:
                result = await func(*args, **kwargs)
                if hasattr(result, '__len__'):
                    timer.set_result_metadata(result_count=len(result))
                return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with PerformanceTimer(operation_name, function=func.__name__) as timer:
                result = func(*args, **kwargs)
                if hasattr(result, '__len__'):
                    timer.set_result_metadata(result_count=len(result))
                return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


class BusinessEventLogger:
    """Logger for business events and user actions."""

    @staticmethod
    def project_created(project_id: str, project_name: str, user_id: str):
        """Log project creation event."""
        logger.info(
            "Project created",
            event_type="PROJECT_CREATED",
            project_id=project_id,
            project_name=project_name,
            user_id=user_id,
            action="CREATE"
        )

    @staticmethod
    def project_updated(project_id: str, user_id: str, changes: Dict[str, Any]):
        """Log project update event."""
        logger.info(
            "Project updated",
            event_type="PROJECT_UPDATED",
            project_id=project_id,
            user_id=user_id,
            changes=list(changes.keys()),
            action="UPDATE"
        )

    @staticmethod
    def workflow_started(workflow_id: str, project_id: str, user_id: str):
        """Log workflow start event."""
        logger.info(
            "Workflow started",
            event_type="WORKFLOW_STARTED",
            workflow_id=workflow_id,
            project_id=project_id,
            user_id=user_id,
            action="EXECUTE"
        )

    @staticmethod
    def agent_assigned(task_id: str, agent_id: str, user_id: str):
        """Log agent assignment event."""
        logger.info(
            "Agent assigned to task",
            event_type="AGENT_ASSIGNED",
            task_id=task_id,
            agent_id=agent_id,
            user_id=user_id,
            action="ASSIGN"
        )

    @staticmethod
    def deployment_initiated(deployment_id: str, project_id: str, environment: str, user_id: str):
        """Log deployment initiation event."""
        logger.info(
            "Deployment initiated",
            event_type="DEPLOYMENT_INITIATED",
            deployment_id=deployment_id,
            project_id=project_id,
            environment=environment,
            user_id=user_id,
            action="DEPLOY"
        )


class AuditTrailLogger:
    """Logger for security and compliance audit events."""

    @staticmethod
    def user_login_attempt(username: str, success: bool, ip_address: Optional[str] = None):
        """Log user login attempt."""
        logger.info(
            "User login attempt",
            event_type="USER_LOGIN_ATTEMPT",
            username=username,
            success=success,
            ip_address=ip_address,
            security_event=True
        )

    @staticmethod
    def permission_check(user_id: str, resource: str, action: str, granted: bool):
        """Log permission check result."""
        logger.info(
            "Permission check",
            event_type="PERMISSION_CHECK",
            user_id=user_id,
            resource=resource,
            action=action,
            granted=granted,
            security_event=True
        )

    @staticmethod
    def data_access(user_id: str, resource_type: str, resource_id: str, action: str):
        """Log data access events."""
        logger.info(
            "Data access",
            event_type="DATA_ACCESS",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            security_event=True
        )


class ErrorContextLogger:
    """Logger for enriching error context with operational data."""

    @staticmethod
    def log_with_context(error: Exception, context: Dict[str, Any]):
        """Log error with additional context."""
        logger.error(
            "Operation failed with error",
            error_type=type(error).__name__,
            error_message=str(error),
            **context
        )

    @staticmethod
    def database_error(operation: str, query: str, error: Exception, **context):
        """Log database-related errors."""
        logger.error(
            f"Database operation failed: {operation}",
            event_type="DATABASE_ERROR",
            operation=operation,
            query=query,
            error_type=type(error).__name__,
            error_message=str(error),
            **context
        )


# Convenience instances
business_events = BusinessEventLogger()
audit_trail = AuditTrailLogger()
error_context = ErrorContextLogger()
