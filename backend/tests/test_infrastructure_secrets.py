"""
Tests for SecretsManager in infrastructure module.

Covers lines: 61-68, 76, 80, 82-86, 147-166, 182-191, 201, 214-230, 293-305, 309-332, 344, 357, 366, 380, 394, 405-452
"""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestSecretsManagerDetectBackend:
    """Tests for _detect_backend method (lines 61-68)."""

    def test_detect_backend_vault(self, monkeypatch):
        """Test detect backend returns vault when VAULT_ADDR is set in production."""
        monkeypatch.setenv("VAULT_ADDR", "http://vault:8200")
        monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
        monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)

        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            backend = manager._detect_backend()

            assert backend == "vault"

    def test_detect_backend_aws(self, monkeypatch):
        """Test detect backend returns aws when AWS credentials are set in production."""
        monkeypatch.delenv("VAULT_ADDR", raising=False)
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-key")
        monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)

        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            backend = manager._detect_backend()

            assert backend == "aws"

    def test_detect_backend_azure(self, monkeypatch):
        """Test detect backend returns azure when Azure credentials are set in production."""
        monkeypatch.delenv("VAULT_ADDR", raising=False)
        monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
        monkeypatch.setenv("AZURE_CLIENT_SECRET", "test-secret")

        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            backend = manager._detect_backend()

            assert backend == "azure"

    def test_detect_backend_local_fallback(self, monkeypatch):
        """Test detect backend returns local when no cloud provider in production."""
        monkeypatch.delenv("VAULT_ADDR", raising=False)
        monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
        monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)

        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            backend = manager._detect_backend()

            assert backend == "local"

    def test_detect_backend_env_development(self, monkeypatch):
        """Test detect backend returns env for non-production."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            backend = manager._detect_backend()

            assert backend == "env"


class TestSecretsManagerInitializeBackend:
    """Tests for _initialize_backend method (lines 76, 80, 82-86)."""

    def test_initialize_backend_env(self):
        """Test initialize env backend (no initialization needed)."""
        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="env")
            assert manager.backend == "env"

    def test_initialize_backend_local(self, tmp_path, monkeypatch):
        """Test initialize local encryption backend."""
        monkeypatch.chdir(tmp_path)

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="local")

            assert manager._local_cipher is not None
            assert Path(".secrets_key").exists()


class TestInitLocalEncryption:
    """Tests for _init_local_encryption method (lines 147-166)."""

    def test_init_local_create_new_key(self, tmp_path, monkeypatch):
        """Test local encryption creates new key."""
        monkeypatch.chdir(tmp_path)

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="local")

            key_file = tmp_path / ".secrets_key"
            assert key_file.exists()
            assert manager._local_cipher is not None

    def test_init_local_load_existing_key(self, tmp_path, monkeypatch):
        """Test local encryption loads existing key."""
        from cryptography.fernet import Fernet

        key = Fernet.generate_key()
        (tmp_path / ".secrets_key").write_bytes(key)

        monkeypatch.chdir(tmp_path)

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="local")

            assert manager._local_cipher is not None

    def test_init_local_encryption_exception(self, tmp_path, monkeypatch):
        """Test _init_local_encryption exception handling (lines 164-166)."""
        monkeypatch.chdir(tmp_path)
        # Write an invalid key to force Fernet to fail
        (tmp_path / ".secrets_key").write_bytes(b"not-a-valid-fernet-key")

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            with pytest.raises(Exception):
                SecretsManager(backend="local")


class TestGetSecret:
    """Tests for get_secret method (lines 182-191, 201)."""

    def test_get_secret_env_backend(self, monkeypatch):
        """Test get_secret with env backend."""
        monkeypatch.setenv("MY_SECRET", "secret_value")

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="env")
            value = manager.get_secret("MY_SECRET")

            assert value == "secret_value"

    def test_get_secret_local_backend(self, tmp_path, monkeypatch):
        """Test get_secret with local backend."""
        from cryptography.fernet import Fernet

        key = Fernet.generate_key()
        cipher = Fernet(key)
        (tmp_path / ".secrets_key").write_bytes(key)

        secrets = {"my_key": "local_secret"}
        encrypted = cipher.encrypt(json.dumps(secrets).encode())
        (tmp_path / ".secrets_encrypted").write_bytes(encrypted)

        monkeypatch.chdir(tmp_path)

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="local")
            value = manager.get_secret("my_key")

            assert value == "local_secret"

    def test_get_secret_unknown_backend(self):
        """Test get_secret with unknown backend returns default."""
        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="env")
            manager.backend = "unknown"
            value = manager.get_secret("my_key", default="default_val")

            assert value == "default_val"

    def test_get_secret_required_raises_on_exception(self):
        """Test get_secret with required=True raises when not found."""
        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="env")

            with pytest.raises(ValueError, match="Required secret"):
                manager.get_secret("NONEXISTENT_SECRET_12345", required=True)

    def test_get_secret_exception_returns_default(self):
        """Test get_secret returns default on exception with required=False (line 201)."""
        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
            patch("backend.infrastructure.secrets_manager.os.getenv", side_effect=Exception("OS error")),
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="env")

            # required=False (default), should return default on exception
            result = manager.get_secret("test-key", default="fallback", required=False)

            assert result == "fallback"


class TestSetSecret:
    """Tests for set_secret method (lines 214-230)."""

    def test_set_secret_env_backend(self):
        """Test set_secret with env backend."""
        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="env")
            result = manager.set_secret("MY_KEY", "my_value")

            assert result is True
            assert os.environ.get("MY_KEY") == "my_value"
            del os.environ["MY_KEY"]

    def test_set_secret_local_backend(self, tmp_path, monkeypatch):
        """Test set_secret with local backend."""
        monkeypatch.chdir(tmp_path)

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="local")
            result = manager.set_secret("my_key", "my_value")

            assert result is True
            assert (tmp_path / ".secrets_encrypted").exists()

    def test_set_secret_unknown_backend(self):
        """Test set_secret with unknown backend returns False."""
        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="env")
            manager.backend = "unknown"
            result = manager.set_secret("my_key", "my_value")

            assert result is False

    def test_set_secret_exception_returns_false(self):
        """Test set_secret returns False on exception (lines 228-230)."""
        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="env")

            # Patch os.environ in the secrets_manager module to raise an exception
            import backend.infrastructure.secrets_manager as sm

            original_environ = sm.os.environ

            class FailingEnviron:
                def __setitem__(self, key, value):
                    raise Exception("Cannot set env")

                def __getitem__(self, key):
                    return original_environ.get(key)

                def get(self, key, default=None):
                    return original_environ.get(key, default)

            sm.os.environ = FailingEnviron()
            try:
                result = manager.set_secret("test-key", "test-value")
                assert result is False
            finally:
                sm.os.environ = original_environ


class TestLocalSecretMethods:
    """Tests for _get_local_secret and _set_local_secret (lines 293-332)."""

    def test_get_local_secret_file_not_exists(self, tmp_path, monkeypatch):
        """Test _get_local_secret returns default when file doesn't exist."""
        monkeypatch.chdir(tmp_path)

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="local")
            value = manager._get_local_secret("test_key", "default")

            assert value == "default"

    def test_get_local_secret_exception_returns_default(self, tmp_path, monkeypatch):
        """Test _get_local_secret returns default on exception."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".secrets_encrypted").write_bytes(b"invalid data")

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="local")
            value = manager._get_local_secret("test_key", "default")

            assert value == "default"

    def test_set_local_secret_update_existing(self, tmp_path, monkeypatch):
        """Test _set_local_secret updates existing secrets."""
        from cryptography.fernet import Fernet

        key = Fernet.generate_key()
        cipher = Fernet(key)
        (tmp_path / ".secrets_key").write_bytes(key)

        secrets = {"existing_key": "existing_value"}
        encrypted = cipher.encrypt(json.dumps(secrets).encode())
        (tmp_path / ".secrets_encrypted").write_bytes(encrypted)

        monkeypatch.chdir(tmp_path)

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="local")
            result = manager._set_local_secret("new_key", "new_value")

            assert result is True

    def test_set_local_secret_exception_returns_false(self, tmp_path, monkeypatch):
        """Test _set_local_secret returns False on exception."""
        monkeypatch.chdir(tmp_path)

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="local")
            manager._local_cipher = Mock()
            manager._local_cipher.encrypt.side_effect = Exception("Encryption error")

            result = manager._set_local_secret("test_key", "test_value")

            assert result is False


class TestBulkGetAndRotate:
    """Tests for bulk_get_secrets and rotate_secret (lines 344, 357)."""

    def test_bulk_get_secrets(self, monkeypatch):
        """Test bulk_get_secrets."""
        monkeypatch.setenv("KEY1", "value1")
        monkeypatch.setenv("KEY2", "value2")

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="env")
            result = manager.bulk_get_secrets(["KEY1", "KEY2", "KEY3"])

            assert result["KEY1"] == "value1"
            assert result["KEY2"] == "value2"
            assert result["KEY3"] is None

    def test_rotate_secret(self):
        """Test rotate_secret."""
        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager(backend="env")
            result = manager.rotate_secret("MY_KEY", "new_value")

            assert result is True
            assert os.environ.get("MY_KEY") == "new_value"
            del os.environ["MY_KEY"]


class TestModuleLevelFunctions:
    """Tests for module-level functions (lines 366, 380, 394)."""

    def test_get_secrets_manager(self):
        """Test get_secrets_manager function."""
        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            import importlib

            import backend.infrastructure.secrets_manager as sm

            importlib.reload(sm)

            manager = sm.get_secrets_manager()
            assert manager is not None

    def test_get_secret_function(self, monkeypatch):
        """Test get_secret convenience function."""
        monkeypatch.setenv("TEST_KEY", "test_value")

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            import importlib

            import backend.infrastructure.secrets_manager as sm

            importlib.reload(sm)

            value = sm.get_secret("TEST_KEY")
            assert value == "test_value"

    def test_set_secret_function(self):
        """Test set_secret convenience function."""
        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            import importlib

            import backend.infrastructure.secrets_manager as sm

            importlib.reload(sm)

            result = sm.set_secret("MY_KEY", "my_value")
            assert result is True
            del os.environ["MY_KEY"]


class TestLoadEnvironmentSecrets:
    """Tests for load_environment_secrets function (lines 405-452)."""

    def test_load_environment_secrets_development(self, monkeypatch):
        """Test load_environment_secrets for development."""
        monkeypatch.setenv("SECRET_KEY", "dev_secret")
        monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/dev")
        monkeypatch.setenv("REDIS_URL", "redis://localhost")

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            import importlib

            import backend.infrastructure.secrets_manager as sm

            importlib.reload(sm)

            result = sm.load_environment_secrets("development")

            assert "SECRET_KEY" in result
            assert "DATABASE_URL" in result

    def test_load_environment_secrets_production(self, monkeypatch):
        """Test load_environment_secrets for production."""
        monkeypatch.setenv("SECRET_KEY", "prod_secret")
        monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/prod")
        monkeypatch.setenv("REDIS_URL", "redis://localhost")
        monkeypatch.setenv("SMTP_PASSWORD", "smtp_pass")
        monkeypatch.setenv("THIRD_PARTY_API_KEY", "api_key")
        monkeypatch.setenv("ENCRYPTION_KEY", "enc_key")

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            import importlib

            import backend.infrastructure.secrets_manager as sm

            importlib.reload(sm)

            result = sm.load_environment_secrets("production")

            assert "SMTP_PASSWORD" in result
            assert "THIRD_PARTY_API_KEY" in result

    def test_load_environment_secrets_staging(self, monkeypatch):
        """Test load_environment_secrets for staging."""
        monkeypatch.setenv("SECRET_KEY", "staging_secret")
        monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/staging")
        monkeypatch.setenv("REDIS_URL", "redis://localhost")
        monkeypatch.setenv("STAGING_DATABASE_URL", "postgresql://localhost/staging_db")
        monkeypatch.setenv("STAGING_REDIS_URL", "redis://staging")

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            import importlib

            import backend.infrastructure.secrets_manager as sm

            importlib.reload(sm)

            result = sm.load_environment_secrets("staging")

            assert "STAGING_DATABASE_URL" in result

    def test_load_environment_secrets_missing(self, monkeypatch):
        """Test load_environment_secrets with missing secrets logs warning."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("REDIS_URL", raising=False)

        with (
            patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings,
            patch("backend.infrastructure.secrets_manager.get_logger") as mock_logger,
        ):
            settings = Mock()
            settings.is_production = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            import importlib

            import backend.infrastructure.secrets_manager as sm

            importlib.reload(sm)

            with patch.object(sm, "logger") as module_logger:
                sm.load_environment_secrets("development")

                module_logger.warning.assert_called()
                module_logger.info.assert_called()


class TestVaultBackend:
    """Tests for HashiCorp Vault backend (lines 90-109, 234-250)."""

    def test_init_vault_success(self, monkeypatch):
        """Test successful Vault initialization (lines 90-103)."""
        monkeypatch.setenv("VAULT_ADDR", "http://vault:8200")
        monkeypatch.setenv("VAULT_TOKEN", "test-token")

        mock_hvac = Mock()
        mock_client = Mock()
        mock_client.is_authenticated.return_value = True
        mock_hvac.Client.return_value = mock_client

        with patch.dict("sys.modules", {"hvac": mock_hvac}):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "vault"

                manager._init_vault()

                mock_hvac.Client.assert_called_once_with(url="http://vault:8200", token="test-token")
                mock_client.is_authenticated.assert_called_once()
                assert manager._vault_client == mock_client

    def test_init_vault_missing_credentials(self, monkeypatch):
        """Test Vault initialization fails without credentials (lines 96-97)."""
        monkeypatch.delenv("VAULT_ADDR", raising=False)
        monkeypatch.delenv("VAULT_TOKEN", raising=False)

        mock_hvac = Mock()

        with patch.dict("sys.modules", {"hvac": mock_hvac}):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "vault"

                with pytest.raises(ValueError, match="VAULT_ADDR and VAULT_TOKEN"):
                    manager._init_vault()

    def test_init_vault_exception(self, monkeypatch):
        """Test Vault initialization with exception (lines 107-109)."""
        monkeypatch.setenv("VAULT_ADDR", "http://vault:8200")
        monkeypatch.setenv("VAULT_TOKEN", "test-token")

        mock_hvac = Mock()
        mock_hvac.Client.side_effect = Exception("Connection failed")

        with patch.dict("sys.modules", {"hvac": mock_hvac}):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "vault"

                with pytest.raises(Exception, match="Connection failed"):
                    manager._init_vault()

    def test_get_vault_secret_success(self, monkeypatch):
        """Test getting secret from Vault (lines 234-237)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "vault"
            manager._vault_client = Mock()
            manager._vault_client.secrets.kv.v2.read_secret_version.return_value = {
                "data": {"data": {"value": "secret-value"}}
            }

            result = manager._get_vault_secret("test-key")

            assert result == "secret-value"

    def test_get_vault_secret_exception(self, monkeypatch):
        """Test getting secret from Vault with exception (lines 238-239)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "vault"
            manager._vault_client = Mock()
            manager._vault_client.secrets.kv.v2.read_secret_version.side_effect = Exception("Not found")

            result = manager._get_vault_secret("test-key", "default")

            assert result == "default"

    def test_set_vault_secret_success(self, monkeypatch):
        """Test setting secret in Vault (lines 243-248)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "vault"
            manager._vault_client = Mock()

            result = manager._set_vault_secret("test-key", "test-value")

            assert result is True
            manager._vault_client.secrets.kv.v2.create_or_update_secret.assert_called_once()

    def test_set_vault_secret_exception(self, monkeypatch):
        """Test setting secret in Vault with exception (lines 249-250)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "vault"
            manager._vault_client = Mock()
            manager._vault_client.secrets.kv.v2.create_or_update_secret.side_effect = Exception("Failed")

            result = manager._set_vault_secret("test-key", "test-value")

            assert result is False


class TestAWSBackend:
    """Tests for AWS Secrets Manager backend (lines 113-123, 254-273)."""

    def test_init_aws_success(self, monkeypatch):
        """Test successful AWS Secrets Manager initialization (lines 113-117)."""
        mock_boto3 = Mock()
        mock_client = Mock()
        mock_boto3.client.return_value = mock_client

        with patch.dict("sys.modules", {"boto3": mock_boto3}):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "aws"

                manager._init_aws_secrets_manager()

                mock_boto3.client.assert_called_once_with("secretsmanager")
                assert manager._aws_client == mock_client

    def test_init_aws_exception(self, monkeypatch):
        """Test AWS initialization with exception (lines 121-123)."""
        mock_boto3 = Mock()
        mock_boto3.client.side_effect = Exception("AWS connection failed")

        with patch.dict("sys.modules", {"boto3": mock_boto3}):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "aws"

                with pytest.raises(Exception, match="AWS connection failed"):
                    manager._init_aws_secrets_manager()

    def test_get_aws_secret_string(self, monkeypatch):
        """Test getting string secret from AWS (lines 254-257)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "aws"
            manager._aws_client = Mock()
            manager._aws_client.get_secret_value.return_value = {"SecretString": "my-secret-value"}

            result = manager._get_aws_secret("test-key")

            assert result == "my-secret-value"

    def test_get_aws_secret_binary(self, monkeypatch):
        """Test getting binary secret from AWS (lines 258-260)."""
        import base64

        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "aws"
            manager._aws_client = Mock()
            manager._aws_client.get_secret_value.return_value = {"SecretBinary": base64.b64encode(b"binary-secret")}

            result = manager._get_aws_secret("test-key")

            assert result == "binary-secret"

    def test_get_aws_secret_exception(self, monkeypatch):
        """Test getting secret from AWS with exception (lines 261-262)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "aws"
            manager._aws_client = Mock()
            manager._aws_client.get_secret_value.side_effect = Exception("Not found")

            result = manager._get_aws_secret("test-key", "default")

            assert result == "default"

    def test_set_aws_secret_success(self, monkeypatch):
        """Test setting secret in AWS (lines 266-271)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "aws"
            manager._aws_client = Mock()

            result = manager._set_aws_secret("test-key", "test-value")

            assert result is True
            manager._aws_client.put_secret_value.assert_called_once_with(SecretId="test-key", SecretString="test-value")

    def test_set_aws_secret_exception(self, monkeypatch):
        """Test setting secret in AWS with exception (lines 272-273)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "aws"
            manager._aws_client = Mock()
            manager._aws_client.put_secret_value.side_effect = Exception("Failed")

            result = manager._set_aws_secret("test-key", "test-value")

            assert result is False


class TestAzureBackend:
    """Tests for Azure Key Vault backend (lines 127-143, 277-289)."""

    def test_init_azure_success(self, monkeypatch):
        """Test successful Azure Key Vault initialization (lines 127-137)."""
        monkeypatch.setenv("AZURE_KEY_VAULT_URL", "https://my-vault.vault.azure.net")

        mock_identity = Mock()
        mock_keyvault = Mock()
        mock_credential = Mock()
        mock_client = Mock()
        mock_identity.DefaultAzureCredential.return_value = mock_credential
        mock_keyvault.SecretClient.return_value = mock_client

        with patch.dict(
            "sys.modules",
            {
                "azure": Mock(),
                "azure.identity": mock_identity,
                "azure.keyvault": Mock(),
                "azure.keyvault.secrets": mock_keyvault,
            },
        ):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "azure"

                manager._init_azure_key_vault()

                mock_identity.DefaultAzureCredential.assert_called_once()
                mock_keyvault.SecretClient.assert_called_once()
                assert manager._azure_client == mock_client

    def test_init_azure_missing_url(self, monkeypatch):
        """Test Azure initialization without AZURE_KEY_VAULT_URL (lines 132-133)."""
        monkeypatch.delenv("AZURE_KEY_VAULT_URL", raising=False)

        mock_identity = Mock()
        mock_keyvault = Mock()

        with patch.dict(
            "sys.modules",
            {
                "azure": Mock(),
                "azure.identity": mock_identity,
                "azure.keyvault": Mock(),
                "azure.keyvault.secrets": mock_keyvault,
            },
        ):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "azure"

                with pytest.raises(ValueError, match="AZURE_KEY_VAULT_URL"):
                    manager._init_azure_key_vault()

    def test_init_azure_exception(self, monkeypatch):
        """Test Azure initialization with exception (lines 141-143)."""
        monkeypatch.setenv("AZURE_KEY_VAULT_URL", "https://my-vault.vault.azure.net")

        mock_identity = Mock()
        mock_keyvault = Mock()
        mock_identity.DefaultAzureCredential.side_effect = Exception("Auth failed")

        with patch.dict(
            "sys.modules",
            {
                "azure": Mock(),
                "azure.identity": mock_identity,
                "azure.keyvault": Mock(),
                "azure.keyvault.secrets": mock_keyvault,
            },
        ):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "azure"

                with pytest.raises(Exception, match="Auth failed"):
                    manager._init_azure_key_vault()

    def test_get_azure_secret_success(self, monkeypatch):
        """Test getting secret from Azure (lines 277-279)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "azure"
            manager._azure_client = Mock()
            mock_secret = Mock()
            mock_secret.value = "azure-secret-value"
            manager._azure_client.get_secret.return_value = mock_secret

            result = manager._get_azure_secret("test-key")

            assert result == "azure-secret-value"

    def test_get_azure_secret_exception(self, monkeypatch):
        """Test getting secret from Azure with exception (lines 280-281)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "azure"
            manager._azure_client = Mock()
            manager._azure_client.get_secret.side_effect = Exception("Not found")

            result = manager._get_azure_secret("test-key", "default")

            assert result == "default"

    def test_set_azure_secret_success(self, monkeypatch):
        """Test setting secret in Azure (lines 285-287)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "azure"
            manager._azure_client = Mock()

            result = manager._set_azure_secret("test-key", "test-value")

            assert result is True
            manager._azure_client.set_secret.assert_called_once_with("test-key", "test-value")

    def test_set_azure_secret_exception(self, monkeypatch):
        """Test setting secret in Azure with exception (lines 288-289)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "azure"
            manager._azure_client = Mock()
            manager._azure_client.set_secret.side_effect = Exception("Failed")

            result = manager._set_azure_secret("test-key", "test-value")

            assert result is False


class TestSecretsManagerGetSetWithBackends:
    """Tests for get_secret and set_secret with vault/aws/azure backends (lines 183-191, 219-227)."""

    def test_get_secret_vault_backend(self, monkeypatch):
        """Test get_secret routes to vault backend (line 183)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "vault"
            manager._vault_client = Mock()
            manager._vault_client.secrets.kv.v2.read_secret_version.return_value = {
                "data": {"data": {"value": "vault-value"}}
            }

            result = manager.get_secret("test-key")

            assert result == "vault-value"

    def test_get_secret_aws_backend(self, monkeypatch):
        """Test get_secret routes to aws backend (line 185)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "aws"
            manager._aws_client = Mock()
            manager._aws_client.get_secret_value.return_value = {"SecretString": "aws-value"}

            result = manager.get_secret("test-key")

            assert result == "aws-value"

    def test_get_secret_azure_backend(self, monkeypatch):
        """Test get_secret routes to azure backend (line 187)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "azure"
            manager._azure_client = Mock()
            mock_secret = Mock()
            mock_secret.value = "azure-value"
            manager._azure_client.get_secret.return_value = mock_secret

            result = manager.get_secret("test-key")

            assert result == "azure-value"

    def test_get_secret_unknown_backend(self, monkeypatch):
        """Test get_secret with unknown backend returns default (lines 190-191)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "unknown"

            result = manager.get_secret("test-key", "default-value")

            assert result == "default-value"

    def test_set_secret_vault_backend(self, monkeypatch):
        """Test set_secret routes to vault backend (line 219)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "vault"
            manager._vault_client = Mock()

            result = manager.set_secret("test-key", "test-value")

            assert result is True

    def test_set_secret_aws_backend(self, monkeypatch):
        """Test set_secret routes to aws backend (line 221)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "aws"
            manager._aws_client = Mock()

            result = manager.set_secret("test-key", "test-value")

            assert result is True

    def test_set_secret_azure_backend(self, monkeypatch):
        """Test set_secret routes to azure backend (line 223)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "azure"
            manager._azure_client = Mock()

            result = manager.set_secret("test-key", "test-value")

            assert result is True

    def test_set_secret_unknown_backend(self, monkeypatch):
        """Test set_secret with unknown backend returns False (lines 226-227)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "unknown"

            result = manager.set_secret("test-key", "test-value")

            assert result is False

    def test_set_secret_exception_logs_error(self, monkeypatch):
        """Test set_secret exception handling (lines 228-230)."""
        with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
            settings = Mock()
            settings.is_production = True
            mock_settings.return_value = settings

            from backend.infrastructure.secrets_manager import SecretsManager

            manager = SecretsManager.__new__(SecretsManager)
            manager.settings = settings
            manager.backend = "vault"
            manager._vault_client = Mock()
            manager._vault_client.secrets.kv.v2.create_or_update_secret.side_effect = Exception("Write failed")

            result = manager.set_secret("test-key", "test-value")

            assert result is False


class TestInitializeBackendBranches:
    """Tests for _initialize_backend method branches (lines 76, 78, 80, 84-86)."""

    def test_initialize_backend_vault(self, monkeypatch):
        """Test _initialize_backend calls _init_vault (line 76)."""
        monkeypatch.setenv("VAULT_ADDR", "http://vault:8200")
        monkeypatch.setenv("VAULT_TOKEN", "test-token")

        mock_hvac = Mock()
        mock_client = Mock()
        mock_client.is_authenticated.return_value = True
        mock_hvac.Client.return_value = mock_client

        with patch.dict("sys.modules", {"hvac": mock_hvac}):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "vault"

                manager._initialize_backend()

                mock_hvac.Client.assert_called_once()

    def test_initialize_backend_aws(self, monkeypatch):
        """Test _initialize_backend calls _init_aws_secrets_manager (line 78)."""
        mock_boto3 = Mock()
        mock_boto3.client.return_value = Mock()

        with patch.dict("sys.modules", {"boto3": mock_boto3}):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "aws"

                manager._initialize_backend()

                mock_boto3.client.assert_called_once_with("secretsmanager")

    def test_initialize_backend_azure(self, monkeypatch):
        """Test _initialize_backend calls _init_azure_key_vault (line 80)."""
        monkeypatch.setenv("AZURE_KEY_VAULT_URL", "https://my-vault.vault.azure.net")

        mock_identity = Mock()
        mock_keyvault = Mock()
        mock_identity.DefaultAzureCredential.return_value = Mock()
        mock_keyvault.SecretClient.return_value = Mock()

        with patch.dict(
            "sys.modules",
            {
                "azure": Mock(),
                "azure.identity": mock_identity,
                "azure.keyvault": Mock(),
                "azure.keyvault.secrets": mock_keyvault,
            },
        ):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "azure"

                manager._initialize_backend()

                mock_identity.DefaultAzureCredential.assert_called_once()

    def test_initialize_backend_exception_logs_and_raises(self, monkeypatch):
        """Test _initialize_backend logs error and re-raises (lines 84-86)."""
        monkeypatch.setenv("VAULT_ADDR", "http://vault:8200")
        monkeypatch.setenv("VAULT_TOKEN", "test-token")

        mock_hvac = Mock()
        mock_hvac.Client.side_effect = Exception("Init failed")

        with patch.dict("sys.modules", {"hvac": mock_hvac}):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "vault"

                with pytest.raises(Exception, match="Init failed"):
                    manager._initialize_backend()


class TestSecretsManagerImportErrors:
    """Tests for ImportError handling in cloud provider initialization (lines 106, 120, 140)."""

    def test_vault_import_error_raises_with_message(self, monkeypatch):
        """Test _init_vault raises ImportError with helpful message when hvac not installed (line 106)."""
        monkeypatch.setenv("VAULT_ADDR", "http://vault:8200")
        monkeypatch.setenv("VAULT_TOKEN", "test-token")

        # Remove hvac from sys.modules to simulate not installed
        with patch.dict("sys.modules", {"hvac": None}):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "vault"

                with pytest.raises(ImportError, match="hvac package required"):
                    manager._init_vault()

    def test_aws_import_error_raises_with_message(self):
        """Test _init_aws_secrets_manager raises ImportError when boto3 not installed (line 120)."""
        # Remove boto3 from sys.modules to simulate not installed
        with patch.dict("sys.modules", {"boto3": None}):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "aws"

                with pytest.raises(ImportError, match="boto3 package required"):
                    manager._init_aws_secrets_manager()

    def test_azure_import_error_raises_with_message(self, monkeypatch):
        """Test _init_azure_key_vault raises ImportError when azure packages not installed (line 140)."""
        monkeypatch.setenv("AZURE_KEY_VAULT_URL", "https://vault.azure.net")

        # Remove azure packages from sys.modules to simulate not installed
        with patch.dict("sys.modules", {"azure.identity": None, "azure.keyvault.secrets": None}):
            with patch("backend.infrastructure.secrets_manager.get_settings") as mock_settings:
                settings = Mock()
                settings.is_production = True
                mock_settings.return_value = settings

                from backend.infrastructure.secrets_manager import SecretsManager

                manager = SecretsManager.__new__(SecretsManager)
                manager.settings = settings
                manager.backend = "azure"

                with pytest.raises(ImportError, match="azure-identity and azure-keyvault-secrets"):
                    manager._init_azure_key_vault()
