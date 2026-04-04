"""
Comprehensive tests for infrastructure modules to increase coverage.
"""

from unittest.mock import MagicMock, mock_open, patch

import pytest


class TestHealthChecker:
    """Tests for HealthChecker."""

    @pytest.fixture
    def health_checker(self):
        """Create HealthChecker instance."""
        from backend.infrastructure.health_checker import HealthChecker

        return HealthChecker()

    def test_init(self, health_checker):
        """Test HealthChecker initialization."""
        assert hasattr(health_checker, "check_health")
        assert hasattr(health_checker, "register_service")

    def test_register_service_success(self, health_checker):
        """Test registering a service successfully."""
        health_checker.register_service("database", lambda: True)

        assert "database" in health_checker._services

    def test_check_health_all_healthy(self, health_checker):
        """Test checking health when all services are healthy."""
        health_checker.register_service("db", lambda: True)
        health_checker.register_service("cache", lambda: True)

        result = health_checker.check_health()

        assert isinstance(result, dict)
        assert result["status"] == "healthy"
        assert len(result["services"]) == 2

    def test_check_health_some_unhealthy(self, health_checker):
        """Test checking health when some services are unhealthy."""
        health_checker.register_service("db", lambda: True)
        health_checker.register_service("cache", lambda: False)

        result = health_checker.check_health()

        assert isinstance(result, dict)
        assert result["status"] == "unhealthy"
        assert any(s["name"] == "cache" and not s["healthy"] for s in result["services"])

    def test_check_health_empty(self, health_checker):
        """Test checking health with no registered services."""
        result = health_checker.check_health()

        assert isinstance(result, dict)
        assert result["status"] == "healthy"
        assert len(result["services"]) == 0


class TestMetricsCollector:
    """Tests for MetricsCollector."""

    @pytest.fixture
    def metrics_collector(self):
        """Create MetricsCollector instance."""
        from backend.infrastructure.metrics import MetricsCollector

        return MetricsCollector()

    def test_init(self, metrics_collector):
        """Test MetricsCollector initialization."""
        assert hasattr(metrics_collector, "record_metric")
        assert hasattr(metrics_collector, "get_metrics")

    def test_record_metric_counter(self, metrics_collector):
        """Test recording a counter metric."""
        metrics_collector.record_metric("requests_total", 1, metric_type="counter")

        metrics = metrics_collector.get_metrics()

        assert "requests_total" in metrics
        assert metrics["requests_total"]["value"] >= 1

    def test_record_metric_gauge(self, metrics_collector):
        """Test recording a gauge metric."""
        metrics_collector.record_metric("active_users", 50, metric_type="gauge")

        metrics = metrics_collector.get_metrics()

        assert "active_users" in metrics
        assert metrics["active_users"]["value"] == 50

    def test_record_metric_histogram(self, metrics_collector):
        """Test recording a histogram metric."""
        metrics_collector.record_metric("response_time", 0.15, metric_type="histogram")
        metrics_collector.record_metric("response_time", 0.25, metric_type="histogram")

        metrics = metrics_collector.get_metrics()

        assert "response_time" in metrics
        assert metrics["response_time"]["count"] == 2

    def test_get_metrics_empty(self, metrics_collector):
        """Test getting metrics when none recorded."""
        metrics = metrics_collector.get_metrics()

        assert isinstance(metrics, dict)

    def test_reset_metrics(self, metrics_collector):
        """Test resetting metrics."""
        metrics_collector.record_metric("test", 1)
        metrics_collector.reset_metrics()

        metrics = metrics_collector.get_metrics()

        assert len(metrics) == 0


class TestBackupManager:
    """Tests for BackupManager."""

    @pytest.fixture
    def backup_manager(self):
        """Create BackupManager instance."""
        from backend.infrastructure.backup_system import BackupManager

        return BackupManager(backup_dir="/var/backups")  # nosec: B108 - test data only

    def test_init(self, backup_manager):
        """Test BackupManager initialization."""
        assert backup_manager._backup_dir == "/var/backups"  # nosec: B108 - test data only
        assert hasattr(backup_manager, "create_backup")
        assert hasattr(backup_manager, "restore_backup")

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_create_backup_success(self, mock_dump, mock_file, mock_makedirs, backup_manager):
        """Test creating a backup successfully."""
        data = {"key": "value"}

        result = backup_manager.create_backup(data, "test_backup")

        assert result is not None
        assert "test_backup" in result
        mock_makedirs.assert_called_once()

    @patch("os.path.exists", return_value=True)
    @patch("os.listdir", return_value=["backup_1.json"])
    def test_list_backups_success(self, mock_listdir, mock_exists, backup_manager):
        """Test listing backups successfully."""
        backups = backup_manager.list_backups()

        assert isinstance(backups, list)
        assert len(backups) > 0

    @patch("os.path.exists")
    def test_restore_backup_not_found(self, mock_exists, backup_manager):
        """Test restoring non-existent backup."""
        mock_exists.return_value = False

        with pytest.raises(Exception):
            backup_manager.restore_backup("nonexistent")


class TestSecretsManager:
    """Tests for SecretsManager."""

    @pytest.fixture
    def secrets_manager(self):
        """Create SecretsManager instance."""
        from backend.infrastructure.secrets_manager import SecretsManager

        return SecretsManager(vault_path="/var/vault")  # nosec: B108 - test data only

    def test_init(self, secrets_manager):
        """Test SecretsManager initialization."""
        assert hasattr(secrets_manager, "store_secret")
        assert hasattr(secrets_manager, "get_secret")
        assert hasattr(secrets_manager, "delete_secret")

    def test_store_secret_success(self, secrets_manager):
        """Test storing a secret successfully."""
        result = secrets_manager.store_secret("api_key", "secret_value")

        assert result is True

    def test_get_secret_success(self, secrets_manager):
        """Test retrieving a secret successfully."""
        secrets_manager.store_secret("test_key", "test_value")

        value = secrets_manager.get_secret("test_key")

        assert value == "test_value"

    def test_get_secret_not_found(self, secrets_manager):
        """Test retrieving non-existent secret."""
        value = secrets_manager.get_secret("nonexistent")

        assert value is None

    def test_delete_secret_success(self, secrets_manager):
        """Test deleting a secret successfully."""
        secrets_manager.store_secret("to_delete", "value")

        result = secrets_manager.delete_secret("to_delete")

        assert result is True
        assert secrets_manager.get_secret("to_delete") is None

    def test_rotate_secret_success(self, secrets_manager):
        """Test rotating a secret successfully."""
        secrets_manager.store_secret("rotate_me", "old_value")

        result = secrets_manager.rotate_secret("rotate_me", "new_value")

        assert result is True
        assert secrets_manager.get_secret("rotate_me") == "new_value"


class TestDockerComposeManager:
    """Tests for DockerComposeManager."""

    @pytest.fixture
    def docker_manager(self):
        """Create DockerComposeManager instance."""
        from backend.infrastructure.docker_compose import DockerComposeManager

        return DockerComposeManager(compose_file="docker-compose.yml")

    def test_init(self, docker_manager):
        """Test DockerComposeManager initialization."""
        assert docker_manager._compose_file == "docker-compose.yml"
        assert hasattr(docker_manager, "up")
        assert hasattr(docker_manager, "down")

    @patch("subprocess.run")
    def test_up_success(self, mock_run, docker_manager):
        """Test bringing up services successfully."""
        mock_run.return_value = MagicMock(returncode=0)

        result = docker_manager.up()

        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_down_success(self, mock_run, docker_manager):
        """Test bringing down services successfully."""
        mock_run.return_value = MagicMock(returncode=0)

        result = docker_manager.down()

        assert result is True

    @patch("subprocess.run")
    def test_ps_success(self, mock_run, docker_manager):
        """Test getting service status successfully."""
        mock_run.return_value = MagicMock(returncode=0, stdout="Service running")

        result = docker_manager.ps()

        assert result is not None

    @patch("subprocess.run")
    def test_logs_success(self, mock_run, docker_manager):
        """Test getting logs successfully."""
        mock_run.return_value = MagicMock(returncode=0, stdout="Log output")

        result = docker_manager.logs(service="web")

        assert result is not None


class TestMonitoringAgent:
    """Tests for MonitoringAgent."""

    @pytest.fixture
    def monitoring_agent(self):
        """Create MonitoringAgent instance."""
        from backend.infrastructure.monitoring import MonitoringAgent

        return MonitoringAgent()

    def test_init(self, monitoring_agent):
        """Test MonitoringAgent initialization."""
        assert hasattr(monitoring_agent, "start")
        assert hasattr(monitoring_agent, "stop")
        assert hasattr(monitoring_agent, "collect_metrics")

    @patch("backend.infrastructure.monitoring.MonitoringAgent.collect_metrics")
    def test_start_success(self, mock_collect, monitoring_agent):
        """Test starting monitoring agent."""
        monitoring_agent.start()

        assert monitoring_agent._running is True

    def test_stop_success(self, monitoring_agent):
        """Test stopping monitoring agent."""
        monitoring_agent._running = True

        monitoring_agent.stop()

        assert monitoring_agent._running is False

    def test_collect_metrics_cpu(self, monitoring_agent):
        """Test collecting CPU metrics."""
        metrics = monitoring_agent.collect_metrics()

        assert isinstance(metrics, dict)
        assert "cpu_percent" in metrics or "cpu" in str(metrics).lower()

    def test_collect_metrics_memory(self, monitoring_agent):
        """Test collecting memory metrics."""
        metrics = monitoring_agent.collect_metrics()

        assert isinstance(metrics, dict)
        assert "memory" in str(metrics).lower() or "ram" in str(metrics).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
