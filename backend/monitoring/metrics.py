"""
Enhanced Prometheus Metrics and Monitoring

Provides comprehensive metrics collection, custom metrics, and alerting rules
for system monitoring and observability.
"""

import asyncio
import time
from datetime import UTC, datetime

import psutil
from backend.core.config import get_settings
from backend.core.logging import get_logger
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Summary,
    generate_latest,
)

logger = get_logger(__name__)
settings = get_settings()


class MetricsCollector:
    """Centralized metrics collection and management."""

    def __init__(self):
        # Create registry
        self.registry = CollectorRegistry()

        # HTTP Request Metrics
        self.http_requests_total = Counter(
            "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"], registry=self.registry
        )

        self.http_request_duration = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            registry=self.registry,
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
        )

        self.http_request_size = Summary(
            "http_request_size_bytes", "HTTP request size in bytes", ["method", "endpoint"], registry=self.registry
        )

        self.http_response_size = Summary(
            "http_response_size_bytes", "HTTP response size in bytes", ["method", "endpoint"], registry=self.registry
        )

        # System Metrics
        self.system_cpu_percent = Gauge("system_cpu_percent", "System CPU usage percentage", registry=self.registry)

        self.system_memory_percent = Gauge(
            "system_memory_percent", "System memory usage percentage", registry=self.registry
        )

        self.system_disk_percent = Gauge("system_disk_percent", "System disk usage percentage", registry=self.registry)

        # Application Metrics
        self.active_users = Gauge("active_users", "Number of currently active users", registry=self.registry)

        self.database_connections = Gauge("database_connections", "Active database connections", registry=self.registry)

        self.redis_connections = Gauge("redis_connections", "Active Redis connections", registry=self.registry)

        self.queue_length = Gauge("queue_length", "Length of processing queues", ["queue_name"], registry=self.registry)

        # Business Metrics
        self.projects_created = Counter(
            "projects_created_total", "Total number of projects created", registry=self.registry
        )

        self.code_generations = Counter(
            "code_generations_total",
            "Total number of code generations",
            ["language", "framework"],
            registry=self.registry,
        )

        self.simulations_run = Counter(
            "simulations_run_total", "Total number of simulations run", registry=self.registry
        )

        self.knowledge_documents = Gauge(
            "knowledge_documents_total", "Total number of knowledge base documents", registry=self.registry
        )

        # Performance Metrics
        self.api_latency = Histogram(
            "api_latency_seconds",
            "API endpoint latency",
            ["endpoint", "method"],
            registry=self.registry,
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
        )

        self.database_query_duration = Histogram(
            "database_query_duration_seconds",
            "Database query duration",
            ["query_type"],
            registry=self.registry,
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
        )

        self.cache_hit_ratio = Gauge("cache_hit_ratio", "Cache hit ratio percentage", registry=self.registry)

        # Error Metrics
        self.errors_total = Counter(
            "errors_total", "Total number of errors", ["error_type", "endpoint"], registry=self.registry
        )

        self.retry_attempts = Counter(
            "retry_attempts_total", "Total number of retry attempts", ["operation"], registry=self.registry
        )

        # Custom metrics collectors
        self._collectors = []
        self._monitoring_task = None

    def register_collector(self, collector_func):
        """Register a custom metrics collector function."""
        self._collectors.append(collector_func)

    async def start_monitoring(self):
        """Start background monitoring tasks."""
        if self._monitoring_task and not self._monitoring_task.done():
            return

        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Metrics monitoring started")

    async def stop_monitoring(self):
        """Stop background monitoring tasks."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Metrics monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while True:
            try:
                await self._collect_system_metrics()
                await self._collect_custom_metrics()
                await asyncio.sleep(settings.METRICS_COLLECTION_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(settings.METRICS_COLLECTION_INTERVAL)

    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        try:
            # CPU usage
            self.system_cpu_percent.set(psutil.cpu_percent())

            # Memory usage
            memory = psutil.virtual_memory()
            self.system_memory_percent.set(memory.percent)

            # Disk usage
            disk = psutil.disk_usage("/")
            self.system_disk_percent.set((disk.used / disk.total) * 100)

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")

    async def _collect_custom_metrics(self):
        """Collect custom metrics from registered collectors."""
        for collector in self._collectors:
            try:
                await collector()
            except Exception as e:
                logger.error(f"Custom metric collector failed: {e}")

    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        self.http_requests_total.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()
        self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_api_call(self, endpoint: str, method: str, duration: float):
        """Record API call latency."""
        self.api_latency.labels(endpoint=endpoint, method=method).observe(duration)

    def record_database_query(self, query_type: str, duration: float):
        """Record database query duration."""
        self.database_query_duration.labels(query_type=query_type).observe(duration)

    def increment_error(self, error_type: str, endpoint: str = "unknown"):
        """Increment error counter."""
        self.errors_total.labels(error_type=error_type, endpoint=endpoint).inc()

    def get_metrics_text(self) -> bytes:
        """Get metrics in Prometheus text format."""
        return generate_latest(self.registry)

    def get_metrics_registry(self) -> CollectorRegistry:
        """Get the metrics registry."""
        return self.registry


# Global metrics collector instance
metrics_collector = MetricsCollector()


# Metrics middleware
class MetricsMiddleware:
    """Middleware for collecting HTTP metrics."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        method = scope["method"]
        path = scope["path"]

        # Track request
        metrics_collector.http_requests_total.labels(method=method, endpoint=path, status_code="unknown").inc()

        async def wrapped_send(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.time() - start_time

                # Update metrics with actual status code
                metrics_collector.record_http_request(method, path, status_code, duration)

                # Add metrics header
                headers = list(message.get("headers", []))
                headers.append((b"x-response-time-ms", str(int(duration * 1000)).encode()))
                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, wrapped_send)


# Alerting system
class AlertRule:
    """Represents an alert rule for monitoring."""

    def __init__(self, name: str, query: str, threshold: float, duration: str, severity: str, description: str):
        self.name = name
        self.query = query
        self.threshold = threshold
        self.duration = duration
        self.severity = severity
        self.description = description
        self.last_triggered = None
        self.active = False


class AlertManager:
    """Manages alert rules and notifications."""

    def __init__(self):
        self.rules: list[AlertRule] = []
        self._alerting_task = None
        self._notifications = []

    def add_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self.rules.append(rule)
        logger.info(f"Alert rule added: {rule.name}")

    def add_notification_channel(self, channel_func):
        """Add notification channel."""
        self._notifications.append(channel_func)

    async def start_alerting(self):
        """Start alert evaluation."""
        if self._alerting_task and not self._alerting_task.done():
            return

        self._alerting_task = asyncio.create_task(self._alerting_loop())
        logger.info("Alert manager started")

    async def stop_alerting(self):
        """Stop alert evaluation."""
        if self._alerting_task:
            self._alerting_task.cancel()
            try:
                await self._alerting_task
            except asyncio.CancelledError:
                pass
        logger.info("Alert manager stopped")

    async def _alerting_loop(self):
        """Main alerting loop."""
        while True:
            try:
                await self._evaluate_rules()
                await asyncio.sleep(settings.ALERT_EVALUATION_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Alert evaluation error: {e}")
                await asyncio.sleep(settings.ALERT_EVALUATION_INTERVAL)

    async def _evaluate_rules(self):
        """Evaluate all alert rules."""
        for rule in self.rules:
            try:
                # In a real implementation, this would query the metrics
                # For now, we'll use dummy evaluations
                triggered = await self._evaluate_rule(rule)
                if triggered and not rule.active:
                    await self._trigger_alert(rule)
                elif not triggered and rule.active:
                    await self._resolve_alert(rule)
            except Exception as e:
                logger.error(f"Failed to evaluate rule {rule.name}: {e}")

    async def _evaluate_rule(self, rule: AlertRule) -> bool:
        """Evaluate a single alert rule."""
        # Dummy implementation - in reality this would query Prometheus
        # For demonstration, we'll create some sample evaluations
        if rule.name == "high_cpu_usage":
            cpu_percent = psutil.cpu_percent()
            return cpu_percent > rule.threshold
        elif rule.name == "high_memory_usage":
            memory = psutil.virtual_memory()
            return memory.percent > rule.threshold
        elif rule.name == "high_error_rate":
            # This would query actual error metrics
            return False
        return False

    async def _trigger_alert(self, rule: AlertRule):
        """Trigger an alert."""
        rule.active = True
        rule.last_triggered = datetime.now(UTC)

        alert_data = {
            "name": rule.name,
            "severity": rule.severity,
            "description": rule.description,
            "threshold": rule.threshold,
            "timestamp": rule.last_triggered.isoformat(),
        }

        logger.warning(f"Alert triggered: {rule.name}")

        # Send notifications
        for notification_func in self._notifications:
            try:
                await notification_func(alert_data)
            except Exception as e:
                logger.error(f"Notification failed: {e}")

    async def _resolve_alert(self, rule: AlertRule):
        """Resolve an alert."""
        rule.active = False
        logger.info(f"Alert resolved: {rule.name}")


# Global alert manager instance
alert_manager = AlertManager()


# Predefined alert rules
def setup_default_alerts():
    """Setup default alert rules."""
    alert_manager.add_rule(
        AlertRule(
            name="high_cpu_usage",
            query="system_cpu_percent > 80",
            threshold=80.0,
            duration="5m",
            severity="warning",
            description="CPU usage is above 80%",
        )
    )

    alert_manager.add_rule(
        AlertRule(
            name="high_memory_usage",
            query="system_memory_percent > 85",
            threshold=85.0,
            duration="5m",
            severity="warning",
            description="Memory usage is above 85%",
        )
    )

    alert_manager.add_rule(
        AlertRule(
            name="high_error_rate",
            query="rate(errors_total[5m]) > 10",
            threshold=10.0,
            duration="5m",
            severity="critical",
            description="Error rate is above 10 errors per minute",
        )
    )

    alert_manager.add_rule(
        AlertRule(
            name="service_unavailable",
            query="up == 0",
            threshold=0.0,
            duration="1m",
            severity="critical",
            description="Service is down",
        )
    )


# Initialize default alerts
setup_default_alerts()
