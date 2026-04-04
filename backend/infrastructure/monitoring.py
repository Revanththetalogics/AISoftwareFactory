"""
Monitoring setup for Infrastructure module.

This module provides Prometheus and Grafana configuration
for observability and monitoring.
"""

from pathlib import Path
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class MonitoringSetup:
    """
    Monitoring setup for Prometheus and Grafana.

    Provides configuration for metrics collection and visualization.
    """

    def __init__(self):
        """Initialize the monitoring setup."""
        self._logger = get_logger(__name__)

    def generate_prometheus_config(self) -> str:
        """Generate Prometheus configuration."""
        config = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
"""
        return config

    def generate_grafana_datasource(self) -> dict[str, Any]:
        """Generate Grafana datasource configuration."""
        return {
            "apiVersion": 1,
            "datasources": [
                {
                    "name": "Prometheus",
                    "type": "prometheus",
                    "url": "http://prometheus:9090",
                    "access": "proxy",
                    "isDefault": True,
                }
            ],
        }

    def generate_dashboard_config(self) -> dict[str, Any]:
        """Generate Grafana dashboard configuration."""
        return {
            "dashboard": {
                "title": "AI Software Factory",
                "panels": [
                    {
                        "title": "Request Rate",
                        "type": "graph",
                        "targets": [
                            {"expr": "rate(http_requests_total[5m])", "legendFormat": "{{method}} {{endpoint}}"}
                        ],
                    },
                    {
                        "title": "Response Time",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                                "legendFormat": "95th percentile",
                            }
                        ],
                    },
                    {
                        "title": "Error Rate",
                        "type": "graph",
                        "targets": [{"expr": 'rate(http_requests_total{status=~"5.."}[5m])', "legendFormat": "Errors"}],
                    },
                ],
            }
        }

    def generate_alert_rules(self) -> str:
        """Generate Prometheus alert rules."""
        rules = """
groups:
  - name: ai_factory_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
"""
        return rules

    def save_configs(self, output_dir: str = "./monitoring"):
        """
        Save all monitoring configurations.

        Args:
            output_dir: Output directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Prometheus config
        (output_path / "prometheus.yml").write_text(self.generate_prometheus_config())

        # Alert rules
        (output_path / "alert_rules.yml").write_text(self.generate_alert_rules())

        # Grafana datasource
        import json

        (output_path / "datasource.yml").write_text(json.dumps(self.generate_grafana_datasource(), indent=2))

        # Grafana dashboard
        (output_path / "dashboard.json").write_text(json.dumps(self.generate_dashboard_config(), indent=2))

        self._logger.info("Monitoring configs saved", path=str(output_path))


class MonitoringAgent:
    """
    Monitoring agent for collecting and reporting system metrics.

    Collects CPU, memory, and other system metrics and reports them
    to the monitoring backend.
    """

    def __init__(self, interval_seconds: int = 15):
        """
        Initialize the monitoring agent.

        Args:
            interval_seconds: Collection interval in seconds
        """
        self._interval = interval_seconds
        self._running = False
        self._metrics: dict = {}
        self._logger = get_logger(__name__)

    def start(self) -> None:
        """Start the monitoring agent."""
        self._running = True
        self._logger.info("Monitoring agent started", interval=self._interval)

    def stop(self) -> None:
        """Stop the monitoring agent."""
        self._running = False
        self._logger.info("Monitoring agent stopped")

    def collect_metrics(self) -> dict:
        """
        Collect current system metrics.

        Returns:
            Dictionary of metric name to value
        """
        metrics = {}
        try:
            import psutil

            metrics["cpu_percent"] = psutil.cpu_percent(interval=None)
            metrics["memory_percent"] = psutil.virtual_memory().percent
            metrics["memory_used_mb"] = psutil.virtual_memory().used / (1024 * 1024)
            metrics["disk_percent"] = psutil.disk_usage("/").percent
        except ImportError:
            metrics["cpu_percent"] = 0.0
            metrics["memory_percent"] = 0.0
            metrics["memory_used_mb"] = 0.0
            metrics["disk_percent"] = 0.0

        self._metrics = metrics
        return metrics

    @property
    def is_running(self) -> bool:
        """Check if the agent is running."""
        return self._running
