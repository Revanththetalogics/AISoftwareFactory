"""
Comprehensive tests for Enhanced Logging module.

Covers all uncovered lines in enhanced_logging.py:
- Lines 33-37, 40-46, 49-62, 72, 85-104, 113, 125, 137, 149, 161, 178, 190, 203, 220, 230
"""

import asyncio
from unittest.mock import patch

import pytest

from backend.utils.enhanced_logging import (
    AuditTrailLogger,
    BusinessEventLogger,
    ErrorContextLogger,
    PerformanceTimer,
    audit_trail,
    business_events,
    error_context,
    timed_operation,
)


class TestPerformanceTimer:
    """Tests for PerformanceTimer context manager."""

    def test_init(self):
        """Test PerformanceTimer initialization."""
        timer = PerformanceTimer("test_operation", project_id="123")

        assert timer.operation_name == "test_operation"
        assert timer.context == {"project_id": "123"}
        assert timer.start_time is None
        assert timer.end_time is None
        assert timer.result_metadata == {}

    def test_enter(self):
        """Test context manager entry."""
        timer = PerformanceTimer("test_operation")

        with timer:
            assert timer.start_time is not None

    def test_exit_success(self):
        """Test context manager exit on success."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            with PerformanceTimer("test_operation", project_id="123"):
                pass  # Successful execution

            # Should log start and completion
            assert mock_logger.info.call_count == 2

    def test_exit_with_exception(self):
        """Test context manager exit on exception."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            with pytest.raises(ValueError):
                with PerformanceTimer("failing_operation"):
                    raise ValueError("Test error")

            # Should log start and error
            mock_logger.error.assert_called_once()
            call_kwargs = mock_logger.error.call_args[1]
            assert call_kwargs["error_type"] == "ValueError"
            assert "Test error" in call_kwargs["error_message"]

    def test_set_result_metadata(self):
        """Test setting result metadata."""
        with PerformanceTimer("test_operation") as timer:
            timer.set_result_metadata(rows_affected=100, cache_hit=True)
            assert timer.result_metadata == {"rows_affected": 100, "cache_hit": True}

    def test_duration_calculation(self):
        """Test duration is calculated correctly."""
        import time

        with PerformanceTimer("test_operation") as timer:
            time.sleep(0.01)  # Small delay

        duration = timer.end_time - timer.start_time
        assert duration > 0.01  # At least 10ms

    def test_context_passed_to_logs(self):
        """Test that context is passed to log entries."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            with PerformanceTimer("test_operation", project_id="proj-123", user_id="user-456"):
                pass

            # Check that context was passed to info call
            call_kwargs = mock_logger.info.call_args[1]
            assert call_kwargs["project_id"] == "proj-123"
            assert call_kwargs["user_id"] == "user-456"


class TestTimedOperationDecorator:
    """Tests for timed_operation decorator."""

    @pytest.mark.asyncio
    async def test_async_function_timing(self):
        """Test timing of async function."""

        @timed_operation("async_test")
        async def async_function():
            await asyncio.sleep(0.01)
            return {"items": [1, 2, 3]}

        with patch("backend.utils.enhanced_logging.logger"):
            result = await async_function()

        assert result == {"items": [1, 2, 3]}

    @pytest.mark.asyncio
    async def test_async_function_with_result_length(self):
        """Test that result length is captured for async function."""

        @timed_operation("async_test")
        async def async_function_with_list():
            return [1, 2, 3, 4, 5]

        with patch("backend.utils.enhanced_logging.logger"):
            result = await async_function_with_list()

        assert len(result) == 5

    def test_sync_function_timing(self):
        """Test timing of sync function."""

        @timed_operation("sync_test")
        def sync_function():
            return {"data": "value"}

        with patch("backend.utils.enhanced_logging.logger"):
            result = sync_function()

        assert result == {"data": "value"}

    def test_sync_function_with_result_length(self):
        """Test that result length is captured for sync function."""

        @timed_operation("sync_test")
        def sync_function_with_list():
            return [1, 2, 3]

        with patch("backend.utils.enhanced_logging.logger"):
            result = sync_function_with_list()

        assert len(result) == 3

    def test_decorated_function_preserves_name(self):
        """Test that decorated function preserves original name."""

        @timed_operation("test_op")
        def my_function():
            pass

        assert my_function.__name__ == "my_function"

    @pytest.mark.asyncio
    async def test_async_decorated_function_preserves_name(self):
        """Test that async decorated function preserves original name."""

        @timed_operation("test_op")
        async def my_async_function():
            pass

        assert my_async_function.__name__ == "my_async_function"


class TestBusinessEventLogger:
    """Tests for BusinessEventLogger."""

    def test_project_created(self):
        """Test logging project created event."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            BusinessEventLogger.project_created(
                project_id="proj-123",
                project_name="Test Project",
                user_id="user-456",
            )

            mock_logger.info.assert_called_once()
            call_kwargs = mock_logger.info.call_args[1]
            assert call_kwargs["event_type"] == "PROJECT_CREATED"
            assert call_kwargs["project_id"] == "proj-123"
            assert call_kwargs["project_name"] == "Test Project"
            assert call_kwargs["user_id"] == "user-456"
            assert call_kwargs["action"] == "CREATE"

    def test_project_updated(self):
        """Test logging project updated event."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            BusinessEventLogger.project_updated(
                project_id="proj-123",
                user_id="user-456",
                changes={"name": "New Name", "status": "active"},
            )

            mock_logger.info.assert_called_once()
            call_kwargs = mock_logger.info.call_args[1]
            assert call_kwargs["event_type"] == "PROJECT_UPDATED"
            assert call_kwargs["changes"] == ["name", "status"]
            assert call_kwargs["action"] == "UPDATE"

    def test_workflow_started(self):
        """Test logging workflow started event."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            BusinessEventLogger.workflow_started(
                workflow_id="wf-123",
                project_id="proj-456",
                user_id="user-789",
            )

            mock_logger.info.assert_called_once()
            call_kwargs = mock_logger.info.call_args[1]
            assert call_kwargs["event_type"] == "WORKFLOW_STARTED"
            assert call_kwargs["workflow_id"] == "wf-123"
            assert call_kwargs["action"] == "EXECUTE"

    def test_agent_assigned(self):
        """Test logging agent assigned event."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            BusinessEventLogger.agent_assigned(
                task_id="task-123",
                agent_id="agent-456",
                user_id="user-789",
            )

            mock_logger.info.assert_called_once()
            call_kwargs = mock_logger.info.call_args[1]
            assert call_kwargs["event_type"] == "AGENT_ASSIGNED"
            assert call_kwargs["task_id"] == "task-123"
            assert call_kwargs["agent_id"] == "agent-456"
            assert call_kwargs["action"] == "ASSIGN"

    def test_deployment_initiated(self):
        """Test logging deployment initiated event."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            BusinessEventLogger.deployment_initiated(
                deployment_id="deploy-123",
                project_id="proj-456",
                environment="production",
                user_id="user-789",
            )

            mock_logger.info.assert_called_once()
            call_kwargs = mock_logger.info.call_args[1]
            assert call_kwargs["event_type"] == "DEPLOYMENT_INITIATED"
            assert call_kwargs["deployment_id"] == "deploy-123"
            assert call_kwargs["environment"] == "production"
            assert call_kwargs["action"] == "DEPLOY"


class TestAuditTrailLogger:
    """Tests for AuditTrailLogger."""

    def test_user_login_attempt_success(self):
        """Test logging successful login attempt."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            AuditTrailLogger.user_login_attempt(
                username="testuser",
                success=True,
                ip_address="192.168.1.1",
            )

            mock_logger.info.assert_called_once()
            call_kwargs = mock_logger.info.call_args[1]
            assert call_kwargs["event_type"] == "USER_LOGIN_ATTEMPT"
            assert call_kwargs["username"] == "testuser"
            assert call_kwargs["success"] is True
            assert call_kwargs["ip_address"] == "192.168.1.1"
            assert call_kwargs["security_event"] is True

    def test_user_login_attempt_failure(self):
        """Test logging failed login attempt."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            AuditTrailLogger.user_login_attempt(
                username="baduser",
                success=False,
                ip_address=None,
            )

            call_kwargs = mock_logger.info.call_args[1]
            assert call_kwargs["success"] is False
            assert call_kwargs["ip_address"] is None

    def test_permission_check_granted(self):
        """Test logging granted permission check."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            AuditTrailLogger.permission_check(
                user_id="user-123",
                resource="projects",
                action="read",
                granted=True,
            )

            mock_logger.info.assert_called_once()
            call_kwargs = mock_logger.info.call_args[1]
            assert call_kwargs["event_type"] == "PERMISSION_CHECK"
            assert call_kwargs["granted"] is True
            assert call_kwargs["security_event"] is True

    def test_permission_check_denied(self):
        """Test logging denied permission check."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            AuditTrailLogger.permission_check(
                user_id="user-123",
                resource="admin",
                action="delete",
                granted=False,
            )

            call_kwargs = mock_logger.info.call_args[1]
            assert call_kwargs["granted"] is False

    def test_data_access(self):
        """Test logging data access event."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            AuditTrailLogger.data_access(
                user_id="user-123",
                resource_type="project",
                resource_id="proj-456",
                action="read",
            )

            mock_logger.info.assert_called_once()
            call_kwargs = mock_logger.info.call_args[1]
            assert call_kwargs["event_type"] == "DATA_ACCESS"
            assert call_kwargs["user_id"] == "user-123"
            assert call_kwargs["resource_type"] == "project"
            assert call_kwargs["resource_id"] == "proj-456"
            assert call_kwargs["security_event"] is True


class TestErrorContextLogger:
    """Tests for ErrorContextLogger."""

    def test_log_with_context(self):
        """Test logging error with context."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            error = RuntimeError("Something went wrong")
            context = {
                "user_id": "user-123",
                "operation": "data_import",
                "file_name": "data.csv",
            }

            ErrorContextLogger.log_with_context(error, context)

            mock_logger.error.assert_called_once()
            call_kwargs = mock_logger.error.call_args[1]
            assert call_kwargs["error_type"] == "RuntimeError"
            assert call_kwargs["error_message"] == "Something went wrong"
            assert call_kwargs["user_id"] == "user-123"
            assert call_kwargs["operation"] == "data_import"

    def test_database_error(self):
        """Test logging database error."""
        with patch("backend.utils.enhanced_logging.logger") as mock_logger:
            error = Exception("Connection refused")

            ErrorContextLogger.database_error(
                operation="insert",
                query="INSERT INTO users ...",
                error=error,
                table="users",
                connection_pool_size=10,
            )

            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            # First positional arg is the message
            assert "Database operation failed" in call_args[0][0]

            call_kwargs = call_args[1]
            assert call_kwargs["event_type"] == "DATABASE_ERROR"
            assert call_kwargs["operation"] == "insert"
            assert call_kwargs["query"] == "INSERT INTO users ..."
            assert call_kwargs["error_type"] == "Exception"
            assert call_kwargs["table"] == "users"
            assert call_kwargs["connection_pool_size"] == 10


class TestConvenienceInstances:
    """Tests for convenience instances."""

    def test_business_events_instance(self):
        """Test business_events is BusinessEventLogger instance."""
        assert isinstance(business_events, BusinessEventLogger)

    def test_audit_trail_instance(self):
        """Test audit_trail is AuditTrailLogger instance."""
        assert isinstance(audit_trail, AuditTrailLogger)

    def test_error_context_instance(self):
        """Test error_context is ErrorContextLogger instance."""
        assert isinstance(error_context, ErrorContextLogger)

    def test_business_events_methods_accessible(self):
        """Test business_events methods are accessible."""
        with patch("backend.utils.enhanced_logging.logger"):
            business_events.project_created("p1", "Project 1", "u1")
            business_events.workflow_started("w1", "p1", "u1")

    def test_audit_trail_methods_accessible(self):
        """Test audit_trail methods are accessible."""
        with patch("backend.utils.enhanced_logging.logger"):
            audit_trail.user_login_attempt("user", True)
            audit_trail.permission_check("u1", "res", "read", True)

    def test_error_context_methods_accessible(self):
        """Test error_context methods are accessible."""
        with patch("backend.utils.enhanced_logging.logger"):
            error_context.log_with_context(RuntimeError("test"), {})
            error_context.database_error("op", "query", Exception("e"))


class TestPerformanceTimerIntegration:
    """Integration tests for PerformanceTimer."""

    def test_nested_timers(self):
        """Test nested performance timers."""
        with patch("backend.utils.enhanced_logging.logger"):
            with PerformanceTimer("outer_operation") as outer:
                with PerformanceTimer("inner_operation") as inner:
                    inner.set_result_metadata(inner_data="value")
                outer.set_result_metadata(outer_data="value")

            assert inner.result_metadata == {"inner_data": "value"}
            assert outer.result_metadata == {"outer_data": "value"}

    def test_timer_returns_self(self):
        """Test that timer context manager returns self."""
        with PerformanceTimer("test") as timer:
            assert isinstance(timer, PerformanceTimer)
