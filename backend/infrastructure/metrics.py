"""
Metrics Collection for AI Software Factory.

This module provides comprehensive metrics collection for:
- API endpoint performance
- Database query metrics
- Business KPIs
- System health indicators
- Resource utilization
"""

import asyncio
import time
from collections import defaultdict, deque
from datetime import UTC, datetime
from typing import Any

from prometheus_client import Counter, Gauge, Histogram, Summary

from backend.core.logging import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """
    Central metrics collection service.

    Collects and exposes metrics for monitoring and alerting.
    """

    def __init__(self):
        """Initialize metrics collector."""
        # API Metrics
        self.api_requests_total = Counter(
            'api_requests_total',
            'Total number of API requests',
            ['method', 'endpoint', 'status_code']
        )

        self.api_request_duration = Histogram(
            'api_request_duration_seconds',
            'API request duration in seconds',
            ['method', 'endpoint'],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
        )

        self.api_errors_total = Counter(
            'api_errors_total',
            'Total number of API errors',
            ['method', 'endpoint', 'error_type']
        )

        # Database Metrics
        self.db_queries_total = Counter(
            'db_queries_total',
            'Total number of database queries',
            ['operation', 'table']
        )

        self.db_query_duration = Histogram(
            'db_query_duration_seconds',
            'Database query duration in seconds',
            ['operation', 'table'],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
        )

        # Business Metrics
        self.projects_created_total = Counter(
            'projects_created_total',
            'Total number of projects created',
            ['user_type']
        )

        self.workflows_executed_total = Counter(
            'workflows_executed_total',
            'Total number of workflows executed',
            ['phase']
        )

        self.deployments_total = Counter(
            'deployments_total',
            'Total number of deployments',
            ['environment', 'status']
        )

        # System Metrics
        self.active_users = Gauge(
            'active_users',
            'Number of currently active users'
        )

        self.concurrent_requests = Gauge(
            'concurrent_requests',
            'Number of concurrent requests being processed'
        )

        self.memory_usage_bytes = Gauge(
            'memory_usage_bytes',
            'Current memory usage in bytes'
        )

        self.cpu_usage_percent = Gauge(
            'cpu_usage_percent',
            'Current CPU usage percentage'
        )

        # Custom business metrics
        self.project_completion_rate = Gauge(
            'project_completion_rate',
            'Percentage of projects completed successfully'
        )

        self.average_workflow_duration = Summary(
            'average_workflow_duration_seconds',
            'Average workflow execution time'
        )

        # LLM Metrics
        self.llm_call_total = Counter(
            'llm_call_total',
            'Total LLM API calls',
            ['provider', 'operation', 'status']
        )

        self.llm_call_duration = Histogram(
            'llm_call_duration_seconds',
            'LLM API call duration in seconds',
            ['provider', 'operation'],
            buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0)
        )

        self.llm_tokens_total = Counter(
            'llm_tokens_total',
            'Total tokens processed by LLM',
            ['provider', 'token_type']  # token_type: prompt, completion
        )

        # Circuit Breaker Metrics
        self.circuit_breaker_state = Gauge(
            'circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=half-open, 2=open)',
            ['name']
        )

        self.circuit_breaker_failures = Counter(
            'circuit_breaker_failures_total',
            'Total circuit breaker failures',
            ['name']
        )

        self.circuit_breaker_successes = Counter(
            'circuit_breaker_successes_total',
            'Total circuit breaker successes',
            ['name']
        )

        self.circuit_breaker_rejections = Counter(
            'circuit_breaker_rejections_total',
            'Total requests rejected by open circuit breaker',
            ['name']
        )

        # Timeout Metrics
        self.timeout_total = Counter(
            'timeout_total',
            'Total timeout occurrences',
            ['operation']
        )

        # Internal tracking
        self._active_request_count = 0
        self._user_sessions = defaultdict(int)
        self._recent_errors = deque(maxlen=1000)  # Keep last 1000 errors
        self._start_time = time.time()

        # Start background metrics collection
        self._start_background_collection()

    def _start_background_collection(self):
        """Start background metrics collection tasks."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._collect_system_metrics())
        except RuntimeError:
            pass  # No event loop at import time — metrics task started lazily

    async def _collect_system_metrics(self):
        """Periodically collect system-level metrics."""
        import asyncio
        while True:
            try:
                import psutil
                process = psutil.Process()
                self.memory_usage_bytes.set(process.memory_info().rss)
                self.cpu_usage_percent.set(process.cpu_percent(interval=None))
                self.concurrent_requests.set(self._active_request_count)
            except Exception:  # noqa: S110
                pass
            await asyncio.sleep(15)

    def record_api_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record an API request."""
        self.api_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        self.api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_api_error(self, method: str, endpoint: str, error_type: str):
        """Record an API error."""
        self.api_errors_total.labels(method=method, endpoint=endpoint, error_type=error_type).inc()
        self._recent_errors.append({
            'timestamp': datetime.now(UTC),
            'method': method,
            'endpoint': endpoint,
            'error_type': error_type
        })

    def record_db_query(self, operation: str, table: str, duration: float):
        """Record a database query."""
        self.db_queries_total.labels(operation=operation, table=table).inc()
        self.db_query_duration.labels(operation=operation, table=table).observe(duration)

    def record_project_created(self, user_type: str = "anonymous"):
        """Record project creation."""
        self.projects_created_total.labels(user_type=user_type).inc()

    def record_workflow_execution(self, phase: str):
        """Record workflow execution."""
        self.workflows_executed_total.labels(phase=phase).inc()

    def record_deployment(self, environment: str, status: str):
        """Record deployment."""
        self.deployments_total.labels(environment=environment, status=status).inc()

    def update_active_users(self, count: int):
        """Update active users count."""
        self.active_users.set(count)
        self._cleanup_expired_sessions()

    def add_user_session(self, user_id: str):
        """Add an active user session."""
        self._user_sessions[user_id] = time.time()
        self.update_active_users(len(self._user_sessions))

    def remove_user_session(self, user_id: str):
        """Remove a user session."""
        self._user_sessions.pop(user_id, None)
        self.update_active_users(len(self._user_sessions))

    def _cleanup_expired_sessions(self):
        """Clean up expired user sessions."""
        current_time = time.time()
        expired_sessions = [
            user_id for user_id, timestamp in self._user_sessions.items()
            if current_time - timestamp > 3600  # 1 hour timeout
        ]

        for user_id in expired_sessions:
            self._user_sessions.pop(user_id, None)

        if expired_sessions:
            self.update_active_users(len(self._user_sessions))

    def get_recent_errors(self, limit: int = 50) -> list:
        """Get recent errors for monitoring."""
        return list(self._recent_errors)[-limit:]

    def get_system_health(self) -> dict[str, Any]:
        """Get system health metrics."""
        return {
            'active_users': self.active_users._value.get(),
            'concurrent_requests': self.concurrent_requests._value.get(),
            'api_error_rate': self._calculate_error_rate(),
            'recent_errors': len(self._recent_errors),
            'uptime_seconds': self._get_uptime()
        }

    def _calculate_error_rate(self) -> float:
        """Calculate API error rate."""
        if not self._recent_errors:
            return 0.0

        recent_errors = list(self._recent_errors)[-100:]  # Last 100 requests
        if not recent_errors:
            return 0.0  # pragma: no cover - defensive, list will have items if _recent_errors is truthy

        error_count = len([e for e in recent_errors if e.get('error_type')])
        return error_count / len(recent_errors) if recent_errors else 0.0

    def _get_uptime(self) -> float:
        """Get application uptime in seconds."""
        # This would typically track from application start time
        return time.time() - getattr(self, '_start_time', time.time())

    def update_business_kpis(self, metrics: dict[str, Any]):
        """Update business KPIs."""
        if 'project_completion_rate' in metrics:
            self.project_completion_rate.set(metrics['project_completion_rate'])

        if 'average_workflow_duration' in metrics:
            self.average_workflow_duration.observe(metrics['average_workflow_duration'])

    def record_llm_call(
        self,
        provider: str,
        operation: str,
        duration: float,
        status: str = "success",
        prompt_tokens: int = 0,
        completion_tokens: int = 0
    ):
        """
        Record an LLM API call.

        Args:
            provider: LLM provider name (e.g., "openai", "ollama")
            operation: Operation type (e.g., "generate", "chat", "embed")
            duration: Call duration in seconds
            status: "success" or "error"
            prompt_tokens: Number of prompt tokens (if available)
            completion_tokens: Number of completion tokens (if available)
        """
        self.llm_call_total.labels(
            provider=provider,
            operation=operation,
            status=status
        ).inc()
        self.llm_call_duration.labels(provider=provider, operation=operation).observe(duration)

        if prompt_tokens > 0:
            self.llm_tokens_total.labels(provider=provider, token_type="prompt").inc(prompt_tokens)
        if completion_tokens > 0:
            self.llm_tokens_total.labels(provider=provider, token_type="completion").inc(completion_tokens)

    def record_circuit_breaker_state(self, name: str, state: int):
        """
        Record circuit breaker state.

        Args:
            name: Circuit breaker name
            state: State value (0=closed, 1=half-open, 2=open)
        """
        self.circuit_breaker_state.labels(name=name).set(state)

    def record_circuit_breaker_failure(self, name: str):
        """Record a circuit breaker failure."""
        self.circuit_breaker_failures.labels(name=name).inc()

    def record_circuit_breaker_success(self, name: str):
        """Record a circuit breaker success."""
        self.circuit_breaker_successes.labels(name=name).inc()

    def record_circuit_breaker_rejection(self, name: str):
        """Record a circuit breaker rejection (call blocked by open circuit)."""
        self.circuit_breaker_rejections.labels(name=name).inc()

    def record_timeout(self, operation: str):
        """Record a timeout occurrence."""
        self.timeout_total.labels(operation=operation).inc()


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get metrics collector instance."""
    return metrics_collector


class MetricsMiddleware:
    """
    Middleware for automatic metrics collection.

    Usage:
        app.add_middleware(MetricsMiddleware)
    """

    def __init__(self, app):
        self.app = app
        self.collector = get_metrics_collector()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        method = scope["method"]
        path = scope["path"]

        # Track request — increment active count before processing
        self.collector._active_request_count += 1
        self.collector.concurrent_requests.set(self.collector._active_request_count)

        async def wrapped_send(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.time() - start_time

                # Record actual metrics
                self.collector.record_api_request(method, path, status_code, duration)

                # Decrement concurrent requests counter
                self.collector._active_request_count = max(0, self.collector._active_request_count - 1)
                self.collector.concurrent_requests.set(self.collector._active_request_count)

            await send(message)

        try:
            await self.app(scope, receive, wrapped_send)
        except Exception as exc:
            # Record error
            self.collector.record_api_error(method, path, type(exc).__name__)

            # Decrement concurrent requests counter
            self.collector._active_request_count = max(0, self.collector._active_request_count - 1)
            self.collector.concurrent_requests.set(self.collector._active_request_count)

            raise


# Decorators for easy metrics collection
def track_db_operation(operation: str, table: str):
    """Decorator to track database operations."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                metrics_collector.record_db_query(operation, table, duration)
                return result
            except Exception:
                duration = time.time() - start_time
                metrics_collector.record_db_query(operation, table, duration)
                raise

        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                metrics_collector.record_db_query(operation, table, duration)
                return result
            except Exception:
                duration = time.time() - start_time
                metrics_collector.record_db_query(operation, table, duration)
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
