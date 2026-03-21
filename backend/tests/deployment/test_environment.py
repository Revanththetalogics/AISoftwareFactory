"""
Tests for Environment Manager.
"""


from backend.deployment.environment import (
    EnvironmentConfig,
    EnvironmentManager,
    EnvironmentType,
    EnvironmentVariable,
)


class TestEnvironmentVariable:
    """Test cases for EnvironmentVariable."""

    def test_variable_creation(self):
        """Test creating a variable."""
        var = EnvironmentVariable(
            name="DEBUG",
            value="true",
        )

        assert var.name == "DEBUG"
        assert var.value == "true"
        assert var.is_secret is False

    def test_secret_variable(self):
        """Test creating a secret variable."""
        var = EnvironmentVariable(
            name="API_KEY",
            value="secret123",
            is_secret=True,
        )

        assert var.is_secret is True

    def test_variable_to_dict(self):
        """Test converting variable to dict."""
        var = EnvironmentVariable(
            name="PORT",
            value="8000",
            description="Server port",
        )

        data = var.to_dict()

        assert data["name"] == "PORT"
        assert data["value"] == "8000"

    def test_secret_to_dict_masks_value(self):
        """Test that secret variables are masked in dict."""
        var = EnvironmentVariable(
            name="SECRET",
            value="hidden",
            is_secret=True,
        )

        data = var.to_dict()

        assert data["value"] == "***"


class TestEnvironmentConfig:
    """Test cases for EnvironmentConfig."""

    def test_config_creation(self):
        """Test creating config."""
        config = EnvironmentConfig(
            name="development",
            environment_type=EnvironmentType.DEVELOPMENT,
        )

        assert config.name == "development"
        assert config.environment_type == EnvironmentType.DEVELOPMENT

    def test_config_with_variables(self):
        """Test config with variables."""
        variables = [
            EnvironmentVariable(name="DEBUG", value="true"),
            EnvironmentVariable(name="PORT", value="8000"),
        ]
        config = EnvironmentConfig(
            name="staging",
            environment_type=EnvironmentType.STAGING,
            variables=variables,
        )

        assert len(config.variables) == 2

    def test_get_variable(self):
        """Test getting a variable by name."""
        variables = [
            EnvironmentVariable(name="DEBUG", value="true"),
        ]
        config = EnvironmentConfig(
            name="test",
            environment_type=EnvironmentType.TESTING,
            variables=variables,
        )

        var = config.get_variable("DEBUG")

        assert var is not None
        assert var.value == "true"

    def test_get_nonexistent_variable(self):
        """Test getting a nonexistent variable."""
        config = EnvironmentConfig(
            name="test",
            environment_type=EnvironmentType.TESTING,
        )

        var = config.get_variable("NONEXISTENT")

        assert var is None

    def test_to_dict(self):
        """Test converting config to dict."""
        config = EnvironmentConfig(
            name="prod",
            environment_type=EnvironmentType.PRODUCTION,
            variables=[EnvironmentVariable(name="DEBUG", value="false")],
        )

        data = config.to_dict()

        assert data["name"] == "prod"
        assert data["environment_type"] == "production"
        assert "variables" in data


class TestEnvironmentManager:
    """Test cases for EnvironmentManager."""

    def setup_method(self):
        """Create fresh manager for each test."""
        self.manager = EnvironmentManager()

    def test_manager_initialization(self):
        """Test manager initialization."""
        assert self.manager is not None

    def test_create_environment(self):
        """Test creating an environment."""
        env = self.manager.create_environment(
            name="dev",
            env_type=EnvironmentType.DEVELOPMENT,
        )

        assert env.name == "dev"
        assert env.environment_type == EnvironmentType.DEVELOPMENT

    def test_get_environment(self):
        """Test getting an environment."""
        self.manager.create_environment(
            name="staging",
            env_type=EnvironmentType.STAGING,
        )

        env = self.manager.get_environment("staging")

        assert env is not None
        assert env.name == "staging"

    def test_get_nonexistent_environment(self):
        """Test getting nonexistent environment."""
        env = self.manager.get_environment("nonexistent")

        assert env is None

    def test_list_environments(self):
        """Test listing environments."""
        self.manager.create_environment("dev", EnvironmentType.DEVELOPMENT)
        self.manager.create_environment("prod", EnvironmentType.PRODUCTION)

        envs = self.manager.list_environments()

        assert len(envs) == 2

    def test_add_variable(self):
        """Test adding a variable to environment."""
        self.manager.create_environment("test", EnvironmentType.TESTING)

        result = self.manager.add_variable("test", "DEBUG", "true")

        assert result is True
        env = self.manager.get_environment("test")
        assert env.get_variable("DEBUG") is not None

    def test_add_variable_to_nonexistent_env(self):
        """Test adding variable to nonexistent environment."""
        result = self.manager.add_variable("nonexistent", "DEBUG", "true")

        assert result is False

    def test_generate_env_file(self):
        """Test generating env file."""
        self.manager.create_environment("dev", EnvironmentType.DEVELOPMENT)
        self.manager.add_variable("dev", "DEBUG", "true")
        self.manager.add_variable("dev", "PORT", "8000")

        content = self.manager.generate_env_file("dev")

        assert content is not None
        assert "DEBUG=true" in content
        assert "PORT=8000" in content

    def test_generate_docker_env(self):
        """Test generating Docker env file."""
        self.manager.create_environment("prod", EnvironmentType.PRODUCTION)
        self.manager.add_variable("prod", "NODE_ENV", "production")

        content = self.manager.generate_docker_env("prod")

        assert content is not None
        # Content may be dict or string depending on implementation
        assert "NODE_ENV" in str(content)
        assert "production" in str(content)

    def test_generate_kubernetes_configmap(self):
        """Test generating Kubernetes ConfigMap."""
        self.manager.create_environment("staging", EnvironmentType.STAGING)
        self.manager.add_variable("staging", "API_URL", "https://api.example.com")

        yaml_content = self.manager.generate_kubernetes_configmap("staging")

        assert yaml_content is not None
        assert "apiVersion: v1" in yaml_content
        assert "ConfigMap" in yaml_content

    def test_generate_kubernetes_secret(self):
        """Test generating Kubernetes Secret."""
        self.manager.create_environment("prod", EnvironmentType.PRODUCTION)
        self.manager.add_variable("prod", "DB_PASSWORD", "secret123", is_secret=True)

        yaml_content = self.manager.generate_kubernetes_secret("prod")

        assert yaml_content is not None
        assert "Secret" in yaml_content
