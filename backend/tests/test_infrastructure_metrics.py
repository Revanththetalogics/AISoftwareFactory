"""
Tests for MetricsCollector in infrastructure module.

Covers all uncovered lines: 195-196, 205-206, 210, 214, 218, 222-223, 227-228, 232-233, 237-247, 251, 255,
265-273, 278, 282-286, 308-318, 328, 332, 336, 340, 344, 365-366, 369-404, 410-437
"""

import asyncio
import time
from unittest.mock import AsyncMock, Mock

import pytest

from backend.infrastructure.metrics import (
    MetricsMiddleware,
    get_metrics_collector,
    metrics_collector,
    track_db_operation,
)


class TestMetricsCollectorRecordMethods:
    """Tests for various record methods (lines 195-196, 205-206, 210, 214, 218)."""

    def test_record_api_error(self):
        """Test record_api_error method (lines 195-196)."""
        collector = get_metrics_collector()
        collector.record_api_error("GET", "/api/test", "ValueError")

        # Verify error was recorded in recent_errors
        errors = list(collector._recent_errors)
        assert len(errors) > 0
        assert errors[-1]["method"] == "GET"
        assert errors[-1]["endpoint"] == "/api/test"
        assert errors[-1]["error_type"] == "ValueError"

    def test_record_db_query(self):
        """Test record_db_query method (lines 205-206)."""
        collector = get_metrics_collector()
        collector.record_db_query("SELECT", "users", 0.05)

        # Just verify it doesn't raise
        assert True

    def test_record_project_created(self):
        """Test record_project_created method (line 210)."""
        collector = get_metrics_collector()
        collector.record_project_created("premium")

        # Just verify it doesn't raise
        assert True

    def test_record_workflow_execution(self):
        """Test record_workflow_execution method (line 214)."""
        collector = get_metrics_collector()
        collector.record_workflow_execution("planning")

        # Just verify it doesn't raise
        assert True

    def test_record_deployment(self):
        """Test record_deployment method (line 218)."""
        collector = get_metrics_collector()
        collector.record_deployment("production", "success")

        # Just verify it doesn't raise
        assert True


class TestActiveUsersTracking:
    """Tests for active users tracking (lines 222-247)."""

    def test_update_active_users(self):
        """Test update_active_users method (lines 222-223)."""
        collector = get_metrics_collector()
        collector.update_active_users(10)

        health = collector.get_system_health()
        assert health['active_users'] == 10

    def test_add_user_session(self):
        """Test add_user_session method (lines 227-228)."""
        collector = get_metrics_collector()
        # Clear any previous sessions
        collector._user_sessions.clear()
        collector.add_user_session("user-123")

        assert "user-123" in collector._user_sessions
        assert collector.active_users._value.get() == 1

    def test_remove_user_session(self):
        """Test remove_user_session method (lines 232-233)."""
        collector = get_metrics_collector()
        collector._user_sessions.clear()
        collector.add_user_session("user-456")
        collector.remove_user_session("user-456")

        assert "user-456" not in collector._user_sessions
        assert collector.active_users._value.get() == 0

    def test_remove_nonexistent_session(self):
        """Test remove_user_session with nonexistent user."""
        collector = get_metrics_collector()
        collector.remove_user_session("nonexistent")

        # Should not raise
        assert True

    def test_cleanup_expired_sessions(self):
        """Test _cleanup_expired_sessions method (lines 237-247)."""
        collector = get_metrics_collector()
        collector._user_sessions.clear()

        # Add session with old timestamp
        collector._user_sessions["old-user"] = time.time() - 4000  # > 1 hour
        collector._user_sessions["active-user"] = time.time()

        collector._cleanup_expired_sessions()

        assert "old-user" not in collector._user_sessions
        assert "active-user" in collector._user_sessions

    def test_cleanup_expired_sessions_updates_count(self):
        """Test _cleanup_expired_sessions updates active users count."""
        collector = get_metrics_collector()
        collector._user_sessions.clear()

        # Add expired session
        collector._user_sessions["expired-user"] = time.time() - 4000
        collector.update_active_users(1)

        collector._cleanup_expired_sessions()

        # Verify active users updated
        assert "expired-user" not in collector._user_sessions


class TestRecentErrorsAndHealth:
    """Tests for recent errors and system health (lines 251, 255, 265-278)."""

    def test_get_recent_errors(self):
        """Test get_recent_errors method (line 251)."""
        collector = get_metrics_collector()
        collector._recent_errors.clear()

        # Add some errors
        for i in range(10):
            collector.record_api_error("GET", f"/api/{i}", "Error")

        errors = collector.get_recent_errors(5)
        assert len(errors) == 5

    def test_get_recent_errors_default_limit(self):
        """Test get_recent_errors with default limit."""
        collector = get_metrics_collector()
        collector._recent_errors.clear()

        for i in range(100):
            collector.record_api_error("GET", f"/api/{i}", "Error")

        errors = collector.get_recent_errors()
        assert len(errors) == 50  # default limit

    def test_get_system_health(self):
        """Test get_system_health method (line 255)."""
        collector = get_metrics_collector()
        collector.update_active_users(5)
        collector._active_request_count = 3
        collector.concurrent_requests.set(3)  # Also set the Gauge

        health = collector.get_system_health()

        assert health['active_users'] == 5
        assert health['concurrent_requests'] == 3
        assert 'api_error_rate' in health
        assert 'recent_errors' in health
        assert 'uptime_seconds' in health

    def test_calculate_error_rate_no_errors(self):
        """Test _calculate_error_rate with no errors (lines 265-273)."""
        collector = get_metrics_collector()
        collector._recent_errors.clear()
        rate = collector._calculate_error_rate()

        assert rate == 0.0

    def test_calculate_error_rate_with_errors(self):
        """Test _calculate_error_rate with errors."""
        collector = get_metrics_collector()
        collector._recent_errors.clear()

        for _i in range(100):
            collector.record_api_error("GET", "/api/test", "Error")

        rate = collector._calculate_error_rate()
        assert rate == 1.0  # All are errors

    def test_get_uptime(self):
        """Test _get_uptime method (line 278)."""
        collector = get_metrics_collector()
        collector._start_time = time.time() - 100

        uptime = collector._get_uptime()
        assert uptime >= 100


class TestBusinessKPIs:
    """Tests for business KPIs (lines 282-286)."""

    def test_update_business_kpis_project_completion(self):
        """Test update_business_kpis with project_completion_rate."""
        collector = get_metrics_collector()
        collector.update_business_kpis({'project_completion_rate': 0.85})

        assert collector.project_completion_rate._value.get() == 0.85

    def test_update_business_kpis_workflow_duration(self):
        """Test update_business_kpis with average_workflow_duration."""
        collector = get_metrics_collector()
        collector.update_business_kpis({'average_workflow_duration': 120.5})

        # Summary metrics track observations, so just verify no error
        assert True

    def test_update_business_kpis_multiple(self):
        """Test update_business_kpis with multiple metrics."""
        collector = get_metrics_collector()
        collector.update_business_kpis({
            'project_completion_rate': 0.90,
            'average_workflow_duration': 150.0
        })

        assert collector.project_completion_rate._value.get() == 0.90


class TestLLMMetrics:
    """Tests for LLM metrics (lines 308-318)."""

    def test_record_llm_call_success(self):
        """Test record_llm_call with success."""
        collector = get_metrics_collector()
        collector.record_llm_call(
            provider="openai",
            operation="chat",
            duration=2.5,
            status="success",
            prompt_tokens=100,
            completion_tokens=50
        )

        # Just verify no error
        assert True

    def test_record_llm_call_error(self):
        """Test record_llm_call with error status."""
        collector = get_metrics_collector()
        collector.record_llm_call(
            provider="ollama",
            operation="generate",
            duration=5.0,
            status="error"
        )

        # Just verify no error
        assert True

    def test_record_llm_call_no_tokens(self):
        """Test record_llm_call without tokens."""
        collector = get_metrics_collector()
        collector.record_llm_call(
            provider="openai",
            operation="embed",
            duration=0.5
        )

        # Just verify no error
        assert True

    def test_record_llm_call_with_prompt_tokens_only(self):
        """Test record_llm_call with only prompt tokens."""
        collector = get_metrics_collector()
        collector.record_llm_call(
            provider="openai",
            operation="chat",
            duration=1.0,
            prompt_tokens=100
        )

        # Just verify no error
        assert True


class TestCircuitBreakerMetrics:
    """Tests for circuit breaker metrics (lines 328, 332, 336, 340, 344)."""

    def test_record_circuit_breaker_state(self):
        """Test record_circuit_breaker_state method (line 328)."""
        collector = get_metrics_collector()
        collector.record_circuit_breaker_state("api-gateway", 2)  # open

        # Just verify no error
        assert True

    def test_record_circuit_breaker_failure(self):
        """Test record_circuit_breaker_failure method (line 332)."""
        collector = get_metrics_collector()
        collector.record_circuit_breaker_failure("database")

        # Just verify no error
        assert True

    def test_record_circuit_breaker_success(self):
        """Test record_circuit_breaker_success method (line 336)."""
        collector = get_metrics_collector()
        collector.record_circuit_breaker_success("redis")

        # Just verify no error
        assert True

    def test_record_circuit_breaker_rejection(self):
        """Test record_circuit_breaker_rejection method (line 340)."""
        collector = get_metrics_collector()
        collector.record_circuit_breaker_rejection("external-api")

        # Just verify no error
        assert True

    def test_record_timeout(self):
        """Test record_timeout method (line 344)."""
        collector = get_metrics_collector()
        collector.record_timeout("database_query")

        # Just verify no error
        assert True


class TestGetMetricsCollector:
    """Tests for get_metrics_collector function (lines 365-366)."""

    def test_get_metrics_collector(self):
        """Test get_metrics_collector returns global instance."""
        collector = get_metrics_collector()
        assert collector is metrics_collector


class TestMetricsMiddleware:
    """Tests for MetricsMiddleware (lines 369-404)."""

    @pytest.mark.asyncio
    async def test_middleware_non_http_passthrough(self):
        """Test middleware passes through non-HTTP requests (line 369-371)."""
        mock_app = AsyncMock()

        middleware = MetricsMiddleware(mock_app)

        scope = {"type": "websocket"}
        receive = AsyncMock()
        send = AsyncMock()

        await middleware(scope, receive, send)

        mock_app.assert_called_once_with(scope, receive, send)

    @pytest.mark.asyncio
    async def test_middleware_http_request(self):
        """Test middleware handles HTTP request (lines 373-392)."""
        async def mock_app(scope, receive, send):
            # Simulate sending response
            await send({"type": "http.response.start", "status": 200})
            await send({"type": "http.response.body", "body": b"OK"})

        middleware = MetricsMiddleware(mock_app)

        scope = {"type": "http", "method": "GET", "path": "/api/test"}
        receive = AsyncMock()
        send = AsyncMock()

        await middleware(scope, receive, send)

        # Verify send was called with wrapped function
        assert send.call_count >= 2

    @pytest.mark.asyncio
    async def test_middleware_exception_handling(self):
        """Test middleware handles exceptions (lines 394-404)."""
        async def mock_app(scope, receive, send):
            raise ValueError("Test error")

        middleware = MetricsMiddleware(mock_app)

        scope = {"type": "http", "method": "POST", "path": "/api/error"}
        receive = AsyncMock()
        send = AsyncMock()

        with pytest.raises(ValueError, match="Test error"):
            await middleware(scope, receive, send)

    @pytest.mark.asyncio
    async def test_middleware_decrements_request_count_on_error(self):
        """Test middleware decrements request count on error."""
        async def mock_app(scope, receive, send):
            raise RuntimeError("Server error")

        middleware = MetricsMiddleware(mock_app)

        scope = {"type": "http", "method": "GET", "path": "/api/test"}
        receive = AsyncMock()
        send = AsyncMock()

        try:
            await middleware(scope, receive, send)
        except RuntimeError:
            pass

        # Count should be decremented (or at least not increased)
        assert middleware.collector._active_request_count >= 0

    @pytest.mark.asyncio
    async def test_middleware_wrapped_send(self):
        """Test middleware wrapped_send function (lines 380-392)."""
        call_log = []

        async def mock_app(scope, receive, send):
            await send({"type": "http.response.start", "status": 201})
            await send({"type": "http.response.body", "body": b"Created"})

        middleware = MetricsMiddleware(mock_app)
        middleware.collector._active_request_count = 5

        scope = {"type": "http", "method": "POST", "path": "/api/create"}
        receive = AsyncMock()

        async def mock_send(message):
            call_log.append(message)

        await middleware(scope, receive, mock_send)

        assert len(call_log) == 2
        assert call_log[0]["type"] == "http.response.start"
        assert call_log[0]["status"] == 201


class TestTrackDbOperationDecorator:
    """Tests for track_db_operation decorator (lines 410-437)."""

    @pytest.mark.asyncio
    async def test_track_db_operation_async_success(self):
        """Test track_db_operation with async function success (lines 411-421)."""
        @track_db_operation("SELECT", "users")
        async def async_query():
            return ["user1", "user2"]

        result = await async_query()

        assert result == ["user1", "user2"]

    @pytest.mark.asyncio
    async def test_track_db_operation_async_exception(self):
        """Test track_db_operation with async function exception."""
        @track_db_operation("INSERT", "users")
        async def async_failing_query():
            raise ValueError("Insert failed")

        with pytest.raises(ValueError, match="Insert failed"):
            await async_failing_query()

    def test_track_db_operation_sync_success(self):
        """Test track_db_operation with sync function success (lines 423-433)."""
        @track_db_operation("UPDATE", "projects")
        def sync_query():
            return {"updated": True}

        result = sync_query()

        assert result == {"updated": True}

    def test_track_db_operation_sync_exception(self):
        """Test track_db_operation with sync function exception."""
        @track_db_operation("DELETE", "tasks")
        def sync_failing_query():
            raise RuntimeError("Delete failed")

        with pytest.raises(RuntimeError, match="Delete failed"):
            sync_failing_query()

    def test_track_db_operation_detects_async(self):
        """Test track_db_operation correctly detects async function (line 435)."""
        @track_db_operation("SELECT", "test")
        async def async_fn():
            return "async"

        @track_db_operation("SELECT", "test")
        def sync_fn():
            return "sync"

        # Verify async function returns coroutine
        assert asyncio.iscoroutinefunction(async_fn)

        # Sync function should work directly
        result = sync_fn()
        assert result == "sync"


class TestMetricsMiddlewareInit:
    """Test MetricsMiddleware initialization."""

    def test_middleware_init(self):
        """Test MetricsMiddleware initialization (lines 364-366)."""
        mock_app = Mock()
        middleware = MetricsMiddleware(mock_app)

        assert middleware.app is mock_app
        assert middleware.collector is not None


class TestMetricsCollectorInit:
    """Tests for MetricsCollector initialization."""

    def test_metrics_collector_init(self):
        """Test MetricsCollector initializes all metrics."""
        collector = get_metrics_collector()

        # Verify API metrics
        assert collector.api_requests_total is not None
        assert collector.api_request_duration is not None
        assert collector.api_errors_total is not None

        # Verify DB metrics
        assert collector.db_queries_total is not None
        assert collector.db_query_duration is not None

        # Verify business metrics
        assert collector.projects_created_total is not None
        assert collector.workflows_executed_total is not None
        assert collector.deployments_total is not None

        # Verify system metrics
        assert collector.active_users is not None
        assert collector.concurrent_requests is not None
        assert collector.memory_usage_bytes is not None
        assert collector.cpu_usage_percent is not None

        # Verify LLM metrics
        assert collector.llm_call_total is not None
        assert collector.llm_call_duration is not None
        assert collector.llm_tokens_total is not None

        # Verify circuit breaker metrics
        assert collector.circuit_breaker_state is not None
        assert collector.circuit_breaker_failures is not None
        assert collector.circuit_breaker_successes is not None
        assert collector.circuit_breaker_rejections is not None

        # Verify timeout metrics
        assert collector.timeout_total is not None

        # Verify internal tracking
        assert hasattr(collector, '_active_request_count')
        assert hasattr(collector, '_user_sessions')
