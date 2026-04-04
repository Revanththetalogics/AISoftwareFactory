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


class TestEnvironmentConfigAdditional:
    """Additional test cases for EnvironmentConfig."""

    def test_get_secret(self):
        """Test getting a secret by name (line 77)."""
        config = EnvironmentConfig(
            name="prod",
            environment_type=EnvironmentType.PRODUCTION,
            secrets={"DB_PASSWORD": "secret123"},
        )

        secret = config.get_secret("DB_PASSWORD")
        assert secret == "secret123"

        non_secret = config.get_secret("NONEXISTENT")
        assert non_secret is None

    def test_to_env_file_with_descriptions(self):
        """Test to_env_file with variable descriptions (line 85)."""
        variables = [
            EnvironmentVariable(name="DEBUG", value="true", description="Enable debug mode"),
            EnvironmentVariable(
                name="PORT",
                value="8000",
                description="",  # No description
            ),
        ]
        config = EnvironmentConfig(
            name="dev",
            environment_type=EnvironmentType.DEVELOPMENT,
            variables=variables,
        )

        content = config.to_env_file()

        assert "# Enable debug mode" in content
        assert "DEBUG=true" in content
        assert "PORT=8000" in content

    def test_to_env_file_with_secrets(self):
        """Test to_env_file includes secrets (line 89)."""
        config = EnvironmentConfig(
            name="prod",
            environment_type=EnvironmentType.PRODUCTION,
            variables=[EnvironmentVariable(name="DEBUG", value="false")],
            secrets={"DB_PASSWORD": "supersecret", "API_KEY": "key123"},
        )

        content = config.to_env_file()

        assert "DEBUG=false" in content
        assert "DB_PASSWORD=supersecret" in content
        assert "API_KEY=key123" in content


class TestEnvironmentManagerAdditional:
    """Additional test cases for EnvironmentManager."""

    def setup_method(self):
        """Create fresh manager for each test."""
        self.manager = EnvironmentManager()

    def test_add_secret(self):
        """Test add_secret method (line 236)."""
        self.manager.create_environment("prod", EnvironmentType.PRODUCTION)

        result = self.manager.add_secret("prod", "DB_PASSWORD", "secret123")

        assert result is True
        env = self.manager.get_environment("prod")
        assert "DB_PASSWORD" in env.secrets
        assert env.secrets["DB_PASSWORD"] == "secret123"

    def test_add_secret_to_nonexistent_env(self):
        """Test add_secret to nonexistent environment."""
        result = self.manager.add_secret("nonexistent", "SECRET", "value")

        assert result is False

    def test_remove_variable(self):
        """Test remove_variable method (lines 254-267)."""
        self.manager.create_environment("dev", EnvironmentType.DEVELOPMENT)
        self.manager.add_variable("dev", "DEBUG", "true")
        self.manager.add_variable("dev", "PORT", "8000")

        result = self.manager.remove_variable("dev", "DEBUG")

        assert result is True
        env = self.manager.get_environment("dev")
        assert env.get_variable("DEBUG") is None
        assert env.get_variable("PORT") is not None

    def test_remove_variable_removes_secret_too(self):
        """Test remove_variable also removes from secrets."""
        self.manager.create_environment("prod", EnvironmentType.PRODUCTION)
        self.manager.add_secret("prod", "DB_PASSWORD", "secret")

        result = self.manager.remove_variable("prod", "DB_PASSWORD")

        assert result is True
        env = self.manager.get_environment("prod")
        assert "DB_PASSWORD" not in env.secrets

    def test_remove_variable_from_nonexistent_env(self):
        """Test remove_variable from nonexistent environment."""
        result = self.manager.remove_variable("nonexistent", "VAR")

        assert result is False

    def test_generate_env_file_nonexistent(self):
        """Test generate_env_file for nonexistent env returns None (line 281)."""
        content = self.manager.generate_env_file("nonexistent")

        assert content is None

    def test_generate_docker_env_nonexistent(self):
        """Test generate_docker_env for nonexistent env returns None (line 300)."""
        content = self.manager.generate_docker_env("nonexistent")

        assert content is None

    def test_generate_docker_env_with_secrets(self):
        """Test generate_docker_env includes secrets (line 308)."""
        self.manager.create_environment("prod", EnvironmentType.PRODUCTION)
        self.manager.add_variable("prod", "DEBUG", "false")
        self.manager.add_secret("prod", "DB_PASSWORD", "secret123")

        result = self.manager.generate_docker_env("prod")

        assert result is not None
        assert result["DEBUG"] == "false"
        assert result["DB_PASSWORD"] == "secret123"

    def test_generate_kubernetes_configmap_nonexistent(self):
        """Test generate_kubernetes_configmap for nonexistent env returns None (line 329)."""
        content = self.manager.generate_kubernetes_configmap("nonexistent")

        assert content is None

    def test_generate_kubernetes_secret_nonexistent(self):
        """Test generate_kubernetes_secret for nonexistent env returns None (line 362)."""
        content = self.manager.generate_kubernetes_secret("nonexistent")

        assert content is None

    def test_generate_kubernetes_secret_with_is_secret_vars(self):
        """Test generate_kubernetes_secret encodes is_secret variables (lines 382-384)."""
        self.manager.create_environment("prod", EnvironmentType.PRODUCTION)
        # Add a regular secret
        self.manager.add_secret("prod", "DB_PASSWORD", "dbpass")
        # Add a variable marked as is_secret=True (but stored in variables list)
        env = self.manager.get_environment("prod")
        env.variables.append(EnvironmentVariable(name="API_TOKEN", value="tokenvalue", is_secret=True))

        yaml_content = self.manager.generate_kubernetes_secret("prod")

        assert yaml_content is not None
        assert "Secret" in yaml_content
        # Check base64 encoded values are present
        import base64

        db_encoded = base64.b64encode(b"dbpass").decode()
        token_encoded = base64.b64encode(b"tokenvalue").decode()
        assert db_encoded in yaml_content
        assert token_encoded in yaml_content

    def test_clone_environment(self):
        """Test clone_environment method (lines 409-437)."""
        self.manager.create_environment("source", EnvironmentType.DEVELOPMENT)
        self.manager.add_variable("source", "DEBUG", "true", description="Debug mode")
        self.manager.add_secret("source", "SECRET_KEY", "secretvalue")
        # Add metadata
        source_env = self.manager.get_environment("source")
        source_env.metadata["version"] = "1.0"

        target = self.manager.clone_environment(
            source_name="source", target_name="target", target_type=EnvironmentType.STAGING
        )

        assert target is not None
        assert target.name == "target"
        assert target.environment_type == EnvironmentType.STAGING
        # Check variables are cloned
        debug_var = target.get_variable("DEBUG")
        assert debug_var is not None
        assert debug_var.value == "true"
        # Check secrets are cloned
        assert target.secrets["SECRET_KEY"] == "secretvalue"
        # Check metadata is cloned
        assert target.metadata["version"] == "1.0"

    def test_clone_environment_preserves_source_type(self):
        """Test clone_environment preserves source type when target_type is None."""
        self.manager.create_environment("source", EnvironmentType.PRODUCTION)

        target = self.manager.clone_environment(source_name="source", target_name="target", target_type=None)

        assert target.environment_type == EnvironmentType.PRODUCTION

    def test_clone_environment_nonexistent_source(self):
        """Test clone_environment returns None for nonexistent source."""
        target = self.manager.clone_environment(source_name="nonexistent", target_name="target")

        assert target is None

    def test_validate_environment_not_found(self):
        """Test validate_environment for nonexistent env (lines 449-451)."""
        result = self.manager.validate_environment("nonexistent")

        assert result["valid"] is False
        assert result["error"] == "Environment not found"

    def test_validate_environment_empty_variable_value(self):
        """Test validate_environment detects empty variable values (lines 456-458)."""
        self.manager.create_environment("dev", EnvironmentType.DEVELOPMENT)
        env = self.manager.get_environment("dev")
        env.variables.append(EnvironmentVariable(name="EMPTY_VAR", value=""))

        result = self.manager.validate_environment("dev")

        assert "Variable 'EMPTY_VAR' has empty value" in result["issues"]

    def test_validate_environment_production_needs_secrets(self):
        """Test validate_environment warns production without secrets (lines 461-463)."""
        self.manager.create_environment("prod", EnvironmentType.PRODUCTION)

        result = self.manager.validate_environment("prod")

        assert "Production environment should have secrets defined" in result["issues"]

    def test_validate_environment_missing_recommended_vars(self):
        """Test validate_environment warns about missing recommended vars (lines 466-471)."""
        self.manager.create_environment("dev", EnvironmentType.DEVELOPMENT)

        result = self.manager.validate_environment("dev")

        assert "Recommended variable 'DATABASE_URL' not defined" in result["issues"]
        assert "Recommended variable 'SECRET_KEY' not defined" in result["issues"]
        assert "Recommended variable 'API_URL' not defined" in result["issues"]

    def test_validate_environment_valid(self):
        """Test validate_environment returns valid for complete environment."""
        self.manager.create_environment("prod", EnvironmentType.PRODUCTION)
        self.manager.add_variable("prod", "DATABASE_URL", "postgres://localhost/db")
        self.manager.add_variable("prod", "API_URL", "https://api.example.com")
        self.manager.add_secret("prod", "SECRET_KEY", "mysecret")

        result = self.manager.validate_environment("prod")

        assert result["valid"] is True
        assert len(result["issues"]) == 0
        assert result["variable_count"] == 2
        assert result["secret_count"] == 1
