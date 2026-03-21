"""
Secrets Management for AI Software Factory.

This module provides secure secrets management using:
- Environment variables for development
- HashiCorp Vault integration for production
- AWS Secrets Manager support
- Azure Key Vault integration
- Local encrypted file storage
"""

import base64
import json
import os
from pathlib import Path
from typing import Dict, Optional

from cryptography.fernet import Fernet

from backend.core.config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


class SecretsManager:
    """
    Unified secrets management interface.

    Supports multiple backends:
    - Environment variables (development)
    - Encrypted local files (staging)
    - HashiCorp Vault (production)
    - Cloud provider services (AWS/Azure/GCP)
    """

    def __init__(self, backend: str = "auto"):
        """
        Initialize secrets manager.

        Args:
            backend: Secret storage backend ('auto', 'env', 'vault', 'aws', 'azure', 'local')
        """
        self.backend = backend
        self.settings = get_settings()
        self._vault_client = None
        self._aws_client = None
        self._azure_client = None
        self._local_cipher = None

        # Auto-detect backend based on environment
        if backend == "auto":
            self.backend = self._detect_backend()

        self._initialize_backend()

    def _detect_backend(self) -> str:
        """Auto-detect the appropriate secrets backend."""
        if self.settings.is_production:
            # Check for cloud providers first
            if os.getenv("VAULT_ADDR"):
                return "vault"
            elif os.getenv("AWS_SECRET_ACCESS_KEY"):
                return "aws"
            elif os.getenv("AZURE_CLIENT_SECRET"):
                return "azure"
            else:
                return "local"  # Fallback to encrypted local storage
        else:
            return "env"  # Use environment variables for development

    def _initialize_backend(self):
        """Initialize the selected backend."""
        try:
            if self.backend == "vault":
                self._init_vault()
            elif self.backend == "aws":
                self._init_aws_secrets_manager()
            elif self.backend == "azure":
                self._init_azure_key_vault()
            elif self.backend == "local":
                self._init_local_encryption()
            # env backend requires no initialization
        except Exception as exc:
            logger.error("Failed to initialize secrets backend", backend=self.backend, error=str(exc))
            raise

    def _init_vault(self):
        """Initialize HashiCorp Vault client."""
        try:
            import hvac

            vault_url = os.getenv("VAULT_ADDR")
            vault_token = os.getenv("VAULT_TOKEN")

            if not vault_url or not vault_token:
                raise ValueError("VAULT_ADDR and VAULT_TOKEN environment variables required")

            self._vault_client = hvac.Client(url=vault_url, token=vault_token)

            # Test connection
            self._vault_client.is_authenticated()
            logger.info("Vault client initialized successfully")

        except ImportError:
            raise ImportError("hvac package required for Vault integration. Install with: pip install hvac")
        except Exception as exc:
            logger.error("Vault initialization failed", error=str(exc))
            raise

    def _init_aws_secrets_manager(self):
        """Initialize AWS Secrets Manager client."""
        try:
            import boto3

            self._aws_client = boto3.client('secretsmanager')
            logger.info("AWS Secrets Manager client initialized")

        except ImportError:
            raise ImportError("boto3 package required for AWS integration. Install with: pip install boto3")
        except Exception as exc:
            logger.error("AWS Secrets Manager initialization failed", error=str(exc))
            raise

    def _init_azure_key_vault(self):
        """Initialize Azure Key Vault client."""
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient

            vault_url = os.getenv("AZURE_KEY_VAULT_URL")
            if not vault_url:
                raise ValueError("AZURE_KEY_VAULT_URL environment variable required")

            credential = DefaultAzureCredential()
            self._azure_client = SecretClient(vault_url=vault_url, credential=credential)
            logger.info("Azure Key Vault client initialized")

        except ImportError:
            raise ImportError("azure-identity and azure-keyvault-secrets packages required. Install with: pip install azure-identity azure-keyvault-secrets")
        except Exception as exc:
            logger.error("Azure Key Vault initialization failed", error=str(exc))
            raise

    def _init_local_encryption(self):
        """Initialize local file encryption."""
        try:
            # Generate or load encryption key
            key_file = Path(".secrets_key")

            if key_file.exists():
                with open(key_file, "rb") as f:
                    key = f.read()
            else:
                # Generate new key - WARNING: This should be done securely in production
                key = Fernet.generate_key()
                with open(key_file, "wb") as f:
                    f.write(key)
                key_file.chmod(0o600)  # Restrict permissions

            self._local_cipher = Fernet(key)
            logger.info("Local encryption initialized")

        except Exception as exc:
            logger.error("Local encryption initialization failed", error=str(exc))
            raise

    def get_secret(self, key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
        """
        Get a secret value.

        Args:
            key: Secret key/name
            default: Default value if secret not found

        Returns:
            Secret value or default
        """
        try:
            if self.backend == "env":
                value = os.getenv(key, default)
            elif self.backend == "vault":
                value = self._get_vault_secret(key, default)
            elif self.backend == "aws":
                value = self._get_aws_secret(key, default)
            elif self.backend == "azure":
                value = self._get_azure_secret(key, default)
            elif self.backend == "local":
                value = self._get_local_secret(key, default)
            else:
                value = default

            if required and value is None:
                raise ValueError(f"Required secret '{key}' not found")

            return value
        except Exception as exc:
            logger.error("Failed to get secret", key=key, error=str(exc))
            if required:
                raise ValueError(f"Required secret '{key}' not found") from exc
            return default

    def set_secret(self, key: str, value: str) -> bool:
        """
        Set a secret value.

        Args:
            key: Secret key/name
            value: Secret value

        Returns:
            True if successful
        """
        try:
            if self.backend == "env":
                os.environ[key] = value
                return True
            elif self.backend == "vault":
                return self._set_vault_secret(key, value)
            elif self.backend == "aws":
                return self._set_aws_secret(key, value)
            elif self.backend == "azure":
                return self._set_azure_secret(key, value)
            elif self.backend == "local":
                return self._set_local_secret(key, value)
            else:
                return False
        except Exception as exc:
            logger.error("Failed to set secret", key=key, error=str(exc))
            return False

    def _get_vault_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from HashiCorp Vault."""
        try:
            # Assuming secrets are stored at /secret/data/{key}
            response = self._vault_client.secrets.kv.v2.read_secret_version(path=key)
            return response['data']['data'].get('value', default)
        except Exception:
            return default

    def _set_vault_secret(self, key: str, value: str) -> bool:
        """Set secret in HashiCorp Vault."""
        try:
            self._vault_client.secrets.kv.v2.create_or_update_secret(
                path=key,
                secret={'value': value}
            )
            return True
        except Exception:
            return False

    def _get_aws_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from AWS Secrets Manager."""
        try:
            response = self._aws_client.get_secret_value(SecretId=key)
            if 'SecretString' in response:
                return response['SecretString']
            else:
                # Handle binary secret
                return base64.b64decode(response['SecretBinary']).decode('utf-8')
        except Exception:
            return default

    def _set_aws_secret(self, key: str, value: str) -> bool:
        """Set secret in AWS Secrets Manager."""
        try:
            self._aws_client.put_secret_value(
                SecretId=key,
                SecretString=value
            )
            return True
        except Exception:
            return False

    def _get_azure_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from Azure Key Vault."""
        try:
            secret = self._azure_client.get_secret(key)
            return secret.value
        except Exception:
            return default

    def _set_azure_secret(self, key: str, value: str) -> bool:
        """Set secret in Azure Key Vault."""
        try:
            self._azure_client.set_secret(key, value)
            return True
        except Exception:
            return False

    def _get_local_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from local encrypted storage."""
        try:
            secrets_file = Path(".secrets_encrypted")
            if not secrets_file.exists():
                return default

            with open(secrets_file, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = self._local_cipher.decrypt(encrypted_data)
            secrets = json.loads(decrypted_data.decode('utf-8'))
            return secrets.get(key, default)
        except Exception:
            return default

    def _set_local_secret(self, key: str, value: str) -> bool:
        """Set secret in local encrypted storage."""
        try:
            secrets_file = Path(".secrets_encrypted")

            # Load existing secrets
            if secrets_file.exists():
                with open(secrets_file, "rb") as f:
                    encrypted_data = f.read()
                decrypted_data = self._local_cipher.decrypt(encrypted_data)
                secrets = json.loads(decrypted_data.decode('utf-8'))
            else:
                secrets = {}

            # Update secret
            secrets[key] = value

            # Save encrypted secrets
            encrypted_data = self._local_cipher.encrypt(json.dumps(secrets).encode('utf-8'))
            with open(secrets_file, "wb") as f:
                f.write(encrypted_data)

            secrets_file.chmod(0o600)  # Restrict permissions
            return True
        except Exception:
            return False

    def bulk_get_secrets(self, keys: list[str]) -> Dict[str, Optional[str]]:
        """
        Get multiple secrets at once.

        Args:
            keys: List of secret keys

        Returns:
            Dictionary of key-value pairs
        """
        return {key: self.get_secret(key) for key in keys}

    def rotate_secret(self, key: str, new_value: str) -> bool:
        """
        Rotate a secret value.

        Args:
            key: Secret key
            new_value: New secret value

        Returns:
            True if successful
        """
        return self.set_secret(key, new_value)


# Global secrets manager instance
secrets_manager = SecretsManager()


def get_secrets_manager() -> SecretsManager:
    """Get secrets manager instance."""
    return secrets_manager


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to get a secret.

    Args:
        key: Secret key
        default: Default value

    Returns:
        Secret value or default
    """
    return secrets_manager.get_secret(key, default)


def set_secret(key: str, value: str) -> bool:
    """
    Convenience function to set a secret.

    Args:
        key: Secret key
        value: Secret value

    Returns:
        True if successful
    """
    return secrets_manager.set_secret(key, value)


# Environment-specific secret loading
def load_environment_secrets(environment: str = "development"):
    """
    Load environment-specific secrets.

    Args:
        environment: Environment name (development, staging, production)
    """
    get_settings()

    # Common secrets that should always be loaded
    required_secrets = [
        "SECRET_KEY",
        "DATABASE_URL",
        "REDIS_URL"
    ]

    # Environment-specific secrets
    if environment == "production":
        required_secrets.extend([
            "SMTP_PASSWORD",
            "THIRD_PARTY_API_KEY",
            "ENCRYPTION_KEY"
        ])
    elif environment == "staging":
        required_secrets.extend([
            "STAGING_DATABASE_URL",
            "STAGING_REDIS_URL"
        ])

    # Load secrets
    loaded_secrets = {}
    missing_secrets = []

    for secret_key in required_secrets:
        value = get_secret(secret_key)
        if value:
            loaded_secrets[secret_key] = value
        else:
            missing_secrets.append(secret_key)

    if missing_secrets:
        logger.warning(
            "Missing required secrets",
            environment=environment,
            missing_secrets=missing_secrets
        )

    logger.info(
        "Environment secrets loaded",
        environment=environment,
        loaded_count=len(loaded_secrets),
        missing_count=len(missing_secrets)
    )

    return loaded_secrets
