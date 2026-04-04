"""
Environment Manager for AI Software Factory.

This module provides environment configuration management for deployments.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class EnvironmentType(StrEnum):
    """Environment types."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class EnvironmentVariable:
    """
    Environment variable.

    Attributes:
        name: Variable name
        value: Variable value
        is_secret: Whether variable is sensitive
        description: Variable description
    """

    name: str
    value: str
    is_secret: bool = False
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": "***" if self.is_secret else self.value,
            "is_secret": self.is_secret,
            "description": self.description,
        }


@dataclass
class EnvironmentConfig:
    """
    Environment configuration.

    Attributes:
        name: Environment name
        environment_type: Type of environment
        variables: Environment variables
        secrets: Secret values (not serialized)
        metadata: Additional metadata
    """

    name: str
    environment_type: EnvironmentType
    variables: list[EnvironmentVariable] = field(default_factory=list)
    secrets: dict[str, str] = field(default_factory=dict, repr=False)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_variable(self, name: str) -> EnvironmentVariable | None:
        """Get a variable by name."""
        for var in self.variables:
            if var.name == name:
                return var
        return None

    def get_secret(self, name: str) -> str | None:
        """Get a secret value."""
        return self.secrets.get(name)

    def to_env_file(self) -> str:
        """Generate .env file content."""
        lines = []

        for var in self.variables:
            if var.description:
                lines.append(f"# {var.description}")
            lines.append(f"{var.name}={var.value}")

        for name, value in self.secrets.items():
            lines.append(f"{name}={value}")

        return "\n".join(lines) + "\n"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "environment_type": self.environment_type.value,
            "variables": [v.to_dict() for v in self.variables],
            "metadata": self.metadata,
        }


class EnvironmentManager:
    """
    Environment configuration manager.

    This class provides:
    - Environment variable management
    - Secret management
    - Environment file generation
    - Configuration validation

    Example:
        >>> manager = EnvironmentManager()
        >>> env = manager.create_environment(
        ...     name="production",
        ...     env_type=EnvironmentType.PRODUCTION
        ... )
        >>> manager.add_variable(env.name, "API_URL", "https://api.example.com")
    """

    def __init__(self):
        """Initialize the environment manager."""
        self._environments: dict[str, EnvironmentConfig] = {}
        self._logger = get_logger(__name__)

    def create_environment(
        self,
        name: str,
        env_type: EnvironmentType,
        metadata: dict[str, Any] | None = None,
    ) -> EnvironmentConfig:
        """
        Create a new environment.

        Args:
            name: Environment name
            env_type: Environment type
            metadata: Additional metadata

        Returns:
            Created environment config
        """
        env = EnvironmentConfig(
            name=name,
            environment_type=env_type,
            metadata=metadata or {},
        )

        self._environments[name] = env

        self._logger.info(
            "Environment created",
            name=name,
            type=env_type.value,
        )

        return env

    def get_environment(self, name: str) -> EnvironmentConfig | None:
        """
        Get an environment by name.

        Args:
            name: Environment name

        Returns:
            EnvironmentConfig or None
        """
        return self._environments.get(name)

    def add_variable(
        self,
        env_name: str,
        var_name: str,
        value: str,
        is_secret: bool = False,
        description: str = "",
    ) -> bool:
        """
        Add a variable to an environment.

        Args:
            env_name: Environment name
            var_name: Variable name
            value: Variable value
            is_secret: Whether it's a secret
            description: Variable description

        Returns:
            True if successful
        """
        env = self._environments.get(env_name)
        if not env:
            return False

        # Remove existing variable with same name
        env.variables = [v for v in env.variables if v.name != var_name]

        if is_secret:
            env.secrets[var_name] = value
        else:
            env.variables.append(
                EnvironmentVariable(
                    name=var_name,
                    value=value,
                    is_secret=False,
                    description=description,
                )
            )

        self._logger.info(
            "Variable added",
            environment=env_name,
            variable=var_name,
            is_secret=is_secret,
        )

        return True

    def add_secret(
        self,
        env_name: str,
        secret_name: str,
        value: str,
    ) -> bool:
        """
        Add a secret to an environment.

        Args:
            env_name: Environment name
            secret_name: Secret name
            value: Secret value

        Returns:
            True if successful
        """
        return self.add_variable(
            env_name=env_name,
            var_name=secret_name,
            value=value,
            is_secret=True,
        )

    def remove_variable(self, env_name: str, var_name: str) -> bool:
        """
        Remove a variable from an environment.

        Args:
            env_name: Environment name
            var_name: Variable name

        Returns:
            True if successful
        """
        env = self._environments.get(env_name)
        if not env:
            return False

        env.variables = [v for v in env.variables if v.name != var_name]
        env.secrets.pop(var_name, None)

        self._logger.info(
            "Variable removed",
            environment=env_name,
            variable=var_name,
        )

        return True

    def generate_env_file(self, env_name: str) -> str | None:
        """
        Generate .env file content for an environment.

        Args:
            env_name: Environment name

        Returns:
            .env file content or None
        """
        env = self._environments.get(env_name)
        if not env:
            return None

        return env.to_env_file()

    def generate_docker_env(
        self,
        env_name: str,
    ) -> dict[str, str] | None:
        """
        Generate Docker environment configuration.

        Args:
            env_name: Environment name

        Returns:
            Dictionary of environment variables
        """
        env = self._environments.get(env_name)
        if not env:
            return None

        result = {}

        for var in env.variables:
            result[var.name] = var.value

        for name, value in env.secrets.items():
            result[name] = value

        return result

    def generate_kubernetes_configmap(
        self,
        env_name: str,
        namespace: str = "default",
    ) -> str | None:
        """
        Generate Kubernetes ConfigMap YAML.

        Args:
            env_name: Environment name
            namespace: Kubernetes namespace

        Returns:
            ConfigMap YAML or None
        """
        env = self._environments.get(env_name)
        if not env:
            return None

        yaml = f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {env_name}-config
  namespace: {namespace}
data:
"""

        for var in env.variables:
            if not var.is_secret:
                yaml += f'  {var.name}: "{var.value}"\n'

        return yaml

    def generate_kubernetes_secret(
        self,
        env_name: str,
        namespace: str = "default",
    ) -> str | None:
        """
        Generate Kubernetes Secret YAML.

        Args:
            env_name: Environment name
            namespace: Kubernetes namespace

        Returns:
            Secret YAML or None
        """
        env = self._environments.get(env_name)
        if not env:
            return None

        import base64

        yaml = f"""apiVersion: v1
kind: Secret
metadata:
  name: {env_name}-secrets
  namespace: {namespace}
type: Opaque
data:
"""

        # Add secrets
        for name, value in env.secrets.items():
            encoded = base64.b64encode(value.encode()).decode()
            yaml += f"  {name}: {encoded}\n"

        # Add secret variables
        for var in env.variables:
            if var.is_secret:
                encoded = base64.b64encode(var.value.encode()).decode()
                yaml += f"  {var.name}: {encoded}\n"

        return yaml

    def list_environments(self) -> list[str]:
        """List all environment names."""
        return list(self._environments.keys())

    def clone_environment(
        self,
        source_name: str,
        target_name: str,
        target_type: EnvironmentType | None = None,
    ) -> EnvironmentConfig | None:
        """
        Clone an environment.

        Args:
            source_name: Source environment name
            target_name: Target environment name
            target_type: Optional new environment type

        Returns:
            Cloned environment or None
        """
        source = self._environments.get(source_name)
        if not source:
            return None

        target = EnvironmentConfig(
            name=target_name,
            environment_type=target_type or source.environment_type,
            variables=[
                EnvironmentVariable(
                    name=v.name,
                    value=v.value,
                    is_secret=v.is_secret,
                    description=v.description,
                )
                for v in source.variables
            ],
            secrets=source.secrets.copy(),
            metadata=source.metadata.copy(),
        )

        self._environments[target_name] = target

        self._logger.info(
            "Environment cloned",
            source=source_name,
            target=target_name,
        )

        return target

    def validate_environment(self, env_name: str) -> dict[str, Any]:
        """
        Validate environment configuration.

        Args:
            env_name: Environment name

        Returns:
            Validation results
        """
        env = self._environments.get(env_name)
        if not env:
            return {"valid": False, "error": "Environment not found"}

        issues = []

        # Check for empty values
        for var in env.variables:
            if not var.value:
                issues.append(f"Variable '{var.name}' has empty value")

        # Check for missing secrets in production
        if env.environment_type == EnvironmentType.PRODUCTION:
            if not env.secrets:
                issues.append("Production environment should have secrets defined")

        # Check for common required variables
        required_vars = ["DATABASE_URL", "SECRET_KEY", "API_URL"]
        var_names = {v.name for v in env.variables} | set(env.secrets.keys())

        for req in required_vars:
            if req not in var_names:
                issues.append(f"Recommended variable '{req}' not defined")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "variable_count": len(env.variables),
            "secret_count": len(env.secrets),
        }
