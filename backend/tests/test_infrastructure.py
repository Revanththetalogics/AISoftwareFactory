"""
Tests for Infrastructure components.
"""


import pytest

from backend.infrastructure.docker_compose import DockerComposeGenerator
from backend.infrastructure.health_checker import HealthChecker, HealthStatus
from backend.infrastructure.secrets_manager import SecretsManager


class TestDockerComposeGenerator:
    """Tests for DockerComposeGenerator."""

    def test_generate_development_config(self):
        """Test generating development config."""
        generator = DockerComposeGenerator()

        config = generator.generate_development_config()

        assert "services" in config
        assert "backend" in config["services"]
        assert "frontend" in config["services"]
        assert "db" in config["services"]
        assert "redis" in config["services"]

    def test_generate_production_config(self):
        """Test generating production config."""
        generator = DockerComposeGenerator()

        config = generator.generate_production_config()

        assert "services" in config
        assert "nginx" in config["services"]

        # Check for deploy configs
        backend = config["services"]["backend"]
        assert "deploy" in backend

    def test_save_config(self, tmp_path):
        """Test save_config method (lines 190-194)."""
        generator = DockerComposeGenerator()
        config = generator.generate_development_config()

        output_file = tmp_path / "docker-compose.yml"
        result = generator.save_config(config, str(output_file))

        assert result == str(output_file)
        assert output_file.exists()

        # Verify content is valid YAML
        import yaml
        with open(output_file) as f:
            loaded = yaml.safe_load(f)
        assert loaded["services"]["backend"] is not None

    def test_save_config_default_path(self, tmp_path, monkeypatch):
        """Test save_config uses default path."""
        monkeypatch.chdir(tmp_path)

        generator = DockerComposeGenerator()
        config = generator.generate_production_config()

        result = generator.save_config(config)

        assert result == "docker-compose.yml"
        assert (tmp_path / "docker-compose.yml").exists()

    def test_generator_custom_project_name(self):
        """Test generator with custom project name."""
        generator = DockerComposeGenerator(project_name="custom-project")

        assert generator._project_name == "custom-project"


class TestSecretsManager:
    """Tests for SecretsManager."""

    def test_get_secret_from_env(self, monkeypatch):
        """Test getting secret from environment."""
        monkeypatch.setenv("TEST_SECRET", "secret_value")

        manager = SecretsManager()
        value = manager.get_secret("TEST_SECRET")

        assert value == "secret_value"

    def test_get_secret_with_default(self):
        """Test getting secret with default value."""
        manager = SecretsManager()

        value = manager.get_secret("NONEXISTENT", default="default_value")

        assert value == "default_value"

    def test_get_required_secret_missing(self):
        """Test getting required secret when missing."""
        manager = SecretsManager()

        with pytest.raises(ValueError):
            manager.get_secret("THIS_SECRET_SHOULD_NOT_EXIST_AT_ALL_12345", required=True)


class TestHealthChecker:
    """Tests for HealthChecker."""

    def test_register_check(self):
        """Test registering a health check."""
        checker = HealthChecker()

        async def dummy_check():
            return HealthStatus.HEALTHY, "OK"

        checker.register_check("test", dummy_check)

        assert "test" in checker._checks

    @pytest.mark.asyncio
    async def test_check_health(self):
        """Test running health checks."""
        checker = HealthChecker()

        async def healthy_check():
            return HealthStatus.HEALTHY, "All good"

        checker.register_check("component1", healthy_check)

        result = await checker.check_health()

        assert result["status"] == "healthy"
        assert len(result["components"]) == 1

    def test_check_disk_space(self):
        """Test disk space check returns valid status."""
        checker = HealthChecker()

        # Just verify it runs without error
        import asyncio
        status, message, details = asyncio.run(checker.check_disk_space())

        assert status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]
        assert isinstance(message, str)
        assert isinstance(details, dict)
        assert "free_gb" in details
