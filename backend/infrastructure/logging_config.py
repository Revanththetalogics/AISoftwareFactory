"""
Logging configuration for Infrastructure module.

This module provides centralized logging configuration with
ELK stack integration support.
"""

from pathlib import Path
from typing import Any, Dict

from backend.core.logging import get_logger

logger = get_logger(__name__)


class LoggingConfig:
    """
    Logging configuration manager.

    Provides centralized logging setup with support for
    file, console, and ELK stack outputs.
    """

    def __init__(self):
        """Initialize the logging configuration."""
        self._logger = get_logger(__name__)

    def generate_logstash_config(self) -> str:
        """Generate Logstash configuration for ELK."""
        config = """
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "ai-factory" {
    json {
      source => "message"
    }
    date {
      match => ["timestamp", "ISO8601"]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "ai-factory-%{+YYYY.MM.dd}"
  }
}
"""
        return config

    def generate_filebeat_config(self) -> Dict[str, Any]:
        """Generate Filebeat configuration."""
        return {
            "filebeat.inputs": [
                {
                    "type": "log",
                    "enabled": True,
                    "paths": [
                        "/var/log/ai-factory/*.log"
                    ],
                    "fields": {
                        "service": "ai-factory"
                    },
                    "fields_under_root": True
                }
            ],
            "output.logstash": {
                "hosts": ["logstash:5044"]
            }
        }

    def generate_log_rotation_config(self) -> str:
        """Generate log rotation configuration."""
        config = """
/var/log/ai-factory/*.log {{
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 app app
    sharedscripts
    postrotate
        /bin/kill -HUP $(cat /var/run/syslogd.pid 2> /dev/null) 2> /dev/null || true
    endscript
}}
"""
        return config

    def generate_structlog_config(self) -> Dict[str, Any]:
        """Generate structlog configuration."""
        return {
            "processors": [
                "structlog.stdlib.filter_by_level",
                "structlog.stdlib.add_logger_name",
                "structlog.stdlib.add_log_level",
                "structlog.stdlib.PositionalArgumentsFormatter",
                "structlog.processors.TimeStamper",
                "structlog.processors.StackInfoRenderer",
                "structlog.processors.format_exc_info",
                "structlog.processors.UnicodeDecoder",
                "structlog.processors.JSONRenderer"
            ],
            "context_class": "dict",
            "logger_factory": "structlog.stdlib.LoggerFactory",
            "wrapper_class": "structlog.stdlib.BoundLogger",
            "cache_logger_on_first_use": True
        }

    def save_configs(self, output_dir: str = "./logging"):
        """
        Save all logging configurations.

        Args:
            output_dir: Output directory
        """
        import json

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Logstash config
        (output_path / "logstash.conf").write_text(
            self.generate_logstash_config()
        )

        # Filebeat config
        (output_path / "filebeat.yml").write_text(
            json.dumps(self.generate_filebeat_config(), indent=2)
        )

        # Log rotation
        (output_path / "logrotate.conf").write_text(
            self.generate_log_rotation_config()
        )

        # Structlog config
        (output_path / "structlog.json").write_text(
            json.dumps(self.generate_structlog_config(), indent=2)
        )

        self._logger.info("Logging configs saved", path=str(output_path))
