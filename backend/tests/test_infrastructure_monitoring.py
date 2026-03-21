"""
Tests for MonitoringSetup in infrastructure module.

Covers all uncovered lines: 25, 29-48, 52, 67, 107-135, 144-168
"""

import json
from unittest.mock import Mock, patch


class TestMonitoringSetupInit:
    """Tests for MonitoringSetup initialization (line 25)."""

    def test_init(self):
        """Test MonitoringSetup initialization."""
        with patch('backend.infrastructure.monitoring.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.monitoring import MonitoringSetup
            setup = MonitoringSetup()

            assert setup._logger is not None


class TestGeneratePrometheusConfig:
    """Tests for generate_prometheus_config method (lines 29-48)."""

    def test_generate_prometheus_config(self):
        """Test generate_prometheus_config generates valid YAML."""
        with patch('backend.infrastructure.monitoring.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.monitoring import MonitoringSetup
            setup = MonitoringSetup()
            config = setup.generate_prometheus_config()

            assert "global:" in config
            assert "scrape_interval: 15s" in config
            assert "scrape_configs:" in config
            assert "job_name: 'prometheus'" in config
            assert "job_name: 'backend'" in config
            assert "job_name: 'node-exporter'" in config
            assert "metrics_path: '/metrics'" in config


class TestGenerateGrafanaDataSource:
    """Tests for generate_grafana_datasource method (line 52)."""

    def test_generate_grafana_datasource(self):
        """Test generate_grafana_datasource generates valid config."""
        with patch('backend.infrastructure.monitoring.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.monitoring import MonitoringSetup
            setup = MonitoringSetup()
            config = setup.generate_grafana_datasource()

            assert config["apiVersion"] == 1
            assert len(config["datasources"]) == 1
            ds = config["datasources"][0]
            assert ds["name"] == "Prometheus"
            assert ds["type"] == "prometheus"
            assert ds["url"] == "http://prometheus:9090"
            assert ds["access"] == "proxy"
            assert ds["isDefault"] is True


class TestGenerateDashboardConfig:
    """Tests for generate_dashboard_config method (line 67)."""

    def test_generate_dashboard_config(self):
        """Test generate_dashboard_config generates valid config."""
        with patch('backend.infrastructure.monitoring.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.monitoring import MonitoringSetup
            setup = MonitoringSetup()
            config = setup.generate_dashboard_config()

            assert "dashboard" in config
            assert config["dashboard"]["title"] == "AI Software Factory"
            assert len(config["dashboard"]["panels"]) == 3

            # Verify panel titles
            panel_titles = [p["title"] for p in config["dashboard"]["panels"]]
            assert "Request Rate" in panel_titles
            assert "Response Time" in panel_titles
            assert "Error Rate" in panel_titles


class TestGenerateAlertRules:
    """Tests for generate_alert_rules method (lines 107-135)."""

    def test_generate_alert_rules(self):
        """Test generate_alert_rules generates valid rules."""
        with patch('backend.infrastructure.monitoring.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.monitoring import MonitoringSetup
            setup = MonitoringSetup()
            rules = setup.generate_alert_rules()

            assert "groups:" in rules
            assert "name: ai_factory_alerts" in rules
            assert "alert: HighErrorRate" in rules
            assert "alert: HighResponseTime" in rules
            assert "alert: ServiceDown" in rules
            assert "severity: critical" in rules
            assert "severity: warning" in rules


class TestSaveConfigs:
    """Tests for save_configs method (lines 144-168)."""

    def test_save_configs_creates_directory(self, tmp_path):
        """Test save_configs creates output directory."""
        output_dir = tmp_path / "monitoring"

        with patch('backend.infrastructure.monitoring.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.monitoring import MonitoringSetup
            setup = MonitoringSetup()
            setup.save_configs(str(output_dir))

            assert output_dir.exists()

    def test_save_configs_writes_prometheus(self, tmp_path):
        """Test save_configs writes prometheus.yml."""
        output_dir = tmp_path / "monitoring"

        with patch('backend.infrastructure.monitoring.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.monitoring import MonitoringSetup
            setup = MonitoringSetup()
            setup.save_configs(str(output_dir))

            prometheus_file = output_dir / "prometheus.yml"
            assert prometheus_file.exists()
            content = prometheus_file.read_text()
            assert "scrape_configs" in content

    def test_save_configs_writes_alert_rules(self, tmp_path):
        """Test save_configs writes alert_rules.yml."""
        output_dir = tmp_path / "monitoring"

        with patch('backend.infrastructure.monitoring.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.monitoring import MonitoringSetup
            setup = MonitoringSetup()
            setup.save_configs(str(output_dir))

            alert_file = output_dir / "alert_rules.yml"
            assert alert_file.exists()
            content = alert_file.read_text()
            assert "HighErrorRate" in content

    def test_save_configs_writes_datasource(self, tmp_path):
        """Test save_configs writes datasource.yml."""
        output_dir = tmp_path / "monitoring"

        with patch('backend.infrastructure.monitoring.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.monitoring import MonitoringSetup
            setup = MonitoringSetup()
            setup.save_configs(str(output_dir))

            datasource_file = output_dir / "datasource.yml"
            assert datasource_file.exists()
            content = json.loads(datasource_file.read_text())
            assert content["datasources"][0]["name"] == "Prometheus"

    def test_save_configs_writes_dashboard(self, tmp_path):
        """Test save_configs writes dashboard.json."""
        output_dir = tmp_path / "monitoring"

        with patch('backend.infrastructure.monitoring.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.monitoring import MonitoringSetup
            setup = MonitoringSetup()
            setup.save_configs(str(output_dir))

            dashboard_file = output_dir / "dashboard.json"
            assert dashboard_file.exists()
            content = json.loads(dashboard_file.read_text())
            assert content["dashboard"]["title"] == "AI Software Factory"

    def test_save_configs_logs_completion(self, tmp_path):
        """Test save_configs logs completion message."""
        output_dir = tmp_path / "monitoring"

        with patch('backend.infrastructure.monitoring.get_logger') as mock_logger:
            mock_log_instance = Mock()
            mock_logger.return_value = mock_log_instance

            from backend.infrastructure.monitoring import MonitoringSetup
            setup = MonitoringSetup()
            setup.save_configs(str(output_dir))

            mock_log_instance.info.assert_called()

    def test_save_configs_default_path(self, tmp_path, monkeypatch):
        """Test save_configs uses default path when not specified."""
        monkeypatch.chdir(tmp_path)

        with patch('backend.infrastructure.monitoring.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.monitoring import MonitoringSetup
            setup = MonitoringSetup()
            setup.save_configs()

            default_path = tmp_path / "monitoring"
            assert default_path.exists()
