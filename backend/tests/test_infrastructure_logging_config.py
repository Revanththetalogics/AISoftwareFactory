"""
Tests for LoggingConfig in infrastructure module.

Covers all uncovered lines: 26, 30-55, 59, 80-95, 99, 124-149
"""

import json
from unittest.mock import Mock, patch


class TestLoggingConfigInit:
    """Tests for LoggingConfig initialization (line 26)."""

    def test_init(self):
        """Test LoggingConfig initialization."""
        with patch('backend.infrastructure.logging_config.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.logging_config import LoggingConfig
            config = LoggingConfig()

            assert config._logger is not None


class TestGenerateLogstashConfig:
    """Tests for generate_logstash_config method (lines 30-55)."""

    def test_generate_logstash_config(self):
        """Test generate_logstash_config generates valid config."""
        with patch('backend.infrastructure.logging_config.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.logging_config import LoggingConfig
            config = LoggingConfig()
            logstash_config = config.generate_logstash_config()

            assert "input {" in logstash_config
            assert "beats {" in logstash_config
            assert "port => 5044" in logstash_config
            assert "filter {" in logstash_config
            assert '[fields][service] == "ai-factory"' in logstash_config
            assert "json {" in logstash_config
            assert 'source => "message"' in logstash_config
            assert "output {" in logstash_config
            assert "elasticsearch {" in logstash_config
            assert 'hosts => ["elasticsearch:9200"]' in logstash_config
            assert 'index => "ai-factory-%{+YYYY.MM.dd}"' in logstash_config


class TestGenerateFilebeatConfig:
    """Tests for generate_filebeat_config method (line 59)."""

    def test_generate_filebeat_config(self):
        """Test generate_filebeat_config generates valid config."""
        with patch('backend.infrastructure.logging_config.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.logging_config import LoggingConfig
            config = LoggingConfig()
            filebeat_config = config.generate_filebeat_config()

            assert "filebeat.inputs" in filebeat_config
            inputs = filebeat_config["filebeat.inputs"]
            assert len(inputs) == 1
            assert inputs[0]["type"] == "log"
            assert inputs[0]["enabled"] is True
            assert "/var/log/ai-factory/*.log" in inputs[0]["paths"]
            assert inputs[0]["fields"]["service"] == "ai-factory"
            assert inputs[0]["fields_under_root"] is True

            assert "output.logstash" in filebeat_config
            assert filebeat_config["output.logstash"]["hosts"] == ["logstash:5044"]


class TestGenerateLogRotationConfig:
    """Tests for generate_log_rotation_config method (lines 80-95)."""

    def test_generate_log_rotation_config(self):
        """Test generate_log_rotation_config generates valid config."""
        with patch('backend.infrastructure.logging_config.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.logging_config import LoggingConfig
            config = LoggingConfig()
            rotation_config = config.generate_log_rotation_config()

            assert "/var/log/ai-factory/*.log" in rotation_config
            assert "daily" in rotation_config
            assert "rotate 30" in rotation_config
            assert "compress" in rotation_config
            assert "delaycompress" in rotation_config
            assert "missingok" in rotation_config
            assert "notifempty" in rotation_config
            assert "create 0644 app app" in rotation_config
            assert "sharedscripts" in rotation_config
            assert "postrotate" in rotation_config
            assert "endscript" in rotation_config


class TestGenerateStructlogConfig:
    """Tests for generate_structlog_config method (line 99)."""

    def test_generate_structlog_config(self):
        """Test generate_structlog_config generates valid config."""
        with patch('backend.infrastructure.logging_config.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.logging_config import LoggingConfig
            config = LoggingConfig()
            structlog_config = config.generate_structlog_config()

            assert "processors" in structlog_config
            processors = structlog_config["processors"]
            assert "structlog.stdlib.filter_by_level" in processors
            assert "structlog.stdlib.add_logger_name" in processors
            assert "structlog.stdlib.add_log_level" in processors
            assert "structlog.stdlib.PositionalArgumentsFormatter" in processors
            assert "structlog.processors.TimeStamper" in processors
            assert "structlog.processors.StackInfoRenderer" in processors
            assert "structlog.processors.format_exc_info" in processors
            assert "structlog.processors.UnicodeDecoder" in processors
            assert "structlog.processors.JSONRenderer" in processors

            assert structlog_config["context_class"] == "dict"
            assert structlog_config["logger_factory"] == "structlog.stdlib.LoggerFactory"
            assert structlog_config["wrapper_class"] == "structlog.stdlib.BoundLogger"
            assert structlog_config["cache_logger_on_first_use"] is True


class TestSaveConfigs:
    """Tests for save_configs method (lines 124-149)."""

    def test_save_configs_creates_directory(self, tmp_path):
        """Test save_configs creates output directory."""
        output_dir = tmp_path / "logging"

        with patch('backend.infrastructure.logging_config.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.logging_config import LoggingConfig
            config = LoggingConfig()
            config.save_configs(str(output_dir))

            assert output_dir.exists()

    def test_save_configs_writes_logstash(self, tmp_path):
        """Test save_configs writes logstash.conf."""
        output_dir = tmp_path / "logging"

        with patch('backend.infrastructure.logging_config.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.logging_config import LoggingConfig
            config = LoggingConfig()
            config.save_configs(str(output_dir))

            logstash_file = output_dir / "logstash.conf"
            assert logstash_file.exists()
            content = logstash_file.read_text()
            assert "input {" in content
            assert "elasticsearch" in content

    def test_save_configs_writes_filebeat(self, tmp_path):
        """Test save_configs writes filebeat.yml."""
        output_dir = tmp_path / "logging"

        with patch('backend.infrastructure.logging_config.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.logging_config import LoggingConfig
            config = LoggingConfig()
            config.save_configs(str(output_dir))

            filebeat_file = output_dir / "filebeat.yml"
            assert filebeat_file.exists()
            content = json.loads(filebeat_file.read_text())
            assert "filebeat.inputs" in content

    def test_save_configs_writes_logrotate(self, tmp_path):
        """Test save_configs writes logrotate.conf."""
        output_dir = tmp_path / "logging"

        with patch('backend.infrastructure.logging_config.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.logging_config import LoggingConfig
            config = LoggingConfig()
            config.save_configs(str(output_dir))

            logrotate_file = output_dir / "logrotate.conf"
            assert logrotate_file.exists()
            content = logrotate_file.read_text()
            assert "daily" in content
            assert "rotate 30" in content

    def test_save_configs_writes_structlog(self, tmp_path):
        """Test save_configs writes structlog.json."""
        output_dir = tmp_path / "logging"

        with patch('backend.infrastructure.logging_config.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.logging_config import LoggingConfig
            config = LoggingConfig()
            config.save_configs(str(output_dir))

            structlog_file = output_dir / "structlog.json"
            assert structlog_file.exists()
            content = json.loads(structlog_file.read_text())
            assert "processors" in content

    def test_save_configs_logs_completion(self, tmp_path):
        """Test save_configs logs completion message."""
        output_dir = tmp_path / "logging"

        with patch('backend.infrastructure.logging_config.get_logger') as mock_logger:
            mock_log_instance = Mock()
            mock_logger.return_value = mock_log_instance

            from backend.infrastructure.logging_config import LoggingConfig
            config = LoggingConfig()
            config.save_configs(str(output_dir))

            mock_log_instance.info.assert_called()

    def test_save_configs_default_path(self, tmp_path, monkeypatch):
        """Test save_configs uses default path when not specified."""
        monkeypatch.chdir(tmp_path)

        with patch('backend.infrastructure.logging_config.get_logger') as mock_logger:
            mock_logger.return_value = Mock()

            from backend.infrastructure.logging_config import LoggingConfig
            config = LoggingConfig()
            config.save_configs()

            default_path = tmp_path / "logging"
            assert default_path.exists()
