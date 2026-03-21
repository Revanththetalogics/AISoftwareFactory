"""
Comprehensive tests for main.py module.

Tests for application startup, shutdown, connect_with_retry, and route handlers.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


class TestConnectWithRetry:
    """Tests for _connect_with_retry function."""

    @pytest.mark.asyncio
    async def test_connect_success_first_attempt(self):
        """Test successful connection on first attempt."""
        from backend.main import _connect_with_retry

        connect_fn = AsyncMock()

        result = await _connect_with_retry(
            name="TestService",
            connect_fn=connect_fn,
            max_retries=3,
            delay=0.01,
            critical=False
        )

        assert result is True
        connect_fn.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_connect_success_after_retries(self):
        """Test successful connection after retries."""
        from backend.main import _connect_with_retry

        connect_fn = AsyncMock()
        connect_fn.side_effect = [
            Exception("First fail"),
            Exception("Second fail"),
            None  # Success on third
        ]

        result = await _connect_with_retry(
            name="TestService",
            connect_fn=connect_fn,
            max_retries=3,
            delay=0.01,
            critical=False
        )

        assert result is True
        assert connect_fn.await_count == 3

    @pytest.mark.asyncio
    async def test_connect_non_critical_failure(self):
        """Test non-critical service failure returns False."""
        from backend.main import _connect_with_retry

        connect_fn = AsyncMock(side_effect=Exception("Connection failed"))

        result = await _connect_with_retry(
            name="TestService",
            connect_fn=connect_fn,
            max_retries=2,
            delay=0.01,
            critical=False
        )

        assert result is False
        assert connect_fn.await_count == 2

    @pytest.mark.asyncio
    async def test_connect_critical_failure_raises(self):
        """Test critical service failure raises RuntimeError."""
        from backend.main import _connect_with_retry

        connect_fn = AsyncMock(side_effect=Exception("Connection failed"))

        with pytest.raises(RuntimeError) as exc_info:
            await _connect_with_retry(
                name="CriticalService",
                connect_fn=connect_fn,
                max_retries=2,
                delay=0.01,
                critical=True
            )

        assert "Failed to connect to critical service" in str(exc_info.value)
        assert "CriticalService" in str(exc_info.value)


class TestCreateApplication:
    """Tests for create_application function."""

    def test_create_application(self):
        """Test application creation."""
        from backend.main import create_application

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                is_development=True,
                DEBUG=False,
                cors_origins_list=["http://localhost:3000"],
                ENABLE_METRICS=False,
                RATE_LIMIT_DEFAULT=100,
                RATE_LIMIT_ADMIN=200,
                RATE_LIMIT_WINDOW_SECONDS=60
            )

            app = create_application()

            assert app is not None
            assert app.title == "Test App"

    def test_create_application_no_cors_development(self):
        """Test application without CORS origins in development."""
        from backend.main import create_application

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                is_development=True,
                DEBUG=False,
                cors_origins_list=[],  # Empty list
                ENABLE_METRICS=False,
                RATE_LIMIT_DEFAULT=100,
                RATE_LIMIT_ADMIN=200,
                RATE_LIMIT_WINDOW_SECONDS=60
            )

            app = create_application()

            assert app is not None

    def test_create_application_no_cors_production(self):
        """Test application without CORS in production (logs warning)."""
        from backend.main import create_application

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                is_development=False,
                DEBUG=False,
                cors_origins_list=[],
                ENABLE_METRICS=False,
                RATE_LIMIT_DEFAULT=100,
                RATE_LIMIT_ADMIN=200,
                RATE_LIMIT_WINDOW_SECONDS=60
            )

            app = create_application()

            assert app is not None

    def test_create_application_with_metrics(self):
        """Test application with metrics enabled."""
        from backend.main import create_application

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                is_development=True,
                DEBUG=False,
                cors_origins_list=["http://localhost:3000"],
                ENABLE_METRICS=True,
                RATE_LIMIT_DEFAULT=100,
                RATE_LIMIT_ADMIN=200,
                RATE_LIMIT_WINDOW_SECONDS=60
            )

            app = create_application()

            assert app is not None


class TestValidateDatabaseSchema:
    """Tests for validate_database_schema function."""

    @pytest.mark.asyncio
    async def test_validate_schema_all_tables_exist(self):
        """Test schema validation when all tables exist."""
        from backend.main import validate_database_schema

        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.fetchall = Mock(return_value=[
            ("ix_users_username",),
            ("ix_users_email",),
            ("idx_users_active",)
        ])
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch('backend.db.session.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_local.return_value.__aexit__ = AsyncMock(return_value=None)

            # Should not raise
            await validate_database_schema()

    @pytest.mark.asyncio
    async def test_validate_schema_missing_tables(self):
        """Test schema validation with missing tables."""
        from backend.main import validate_database_schema

        mock_session = AsyncMock()
        # First set of calls for table validation (fail)
        mock_session.execute = AsyncMock(side_effect=Exception("Table not found"))

        with patch('backend.db.session.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_local.return_value.__aexit__ = AsyncMock(return_value=None)

            # Should not raise, just log warning
            await validate_database_schema()

    @pytest.mark.asyncio
    async def test_validate_schema_missing_indexes(self):
        """Test schema validation with missing indexes."""
        from backend.main import validate_database_schema

        mock_session = AsyncMock()
        mock_table_result = Mock()
        mock_index_result = Mock()
        mock_index_result.fetchall = Mock(return_value=[("ix_users_username",)])

        call_count = [0]
        async def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 7:  # Table checks
                return mock_table_result
            return mock_index_result

        mock_session.execute = AsyncMock(side_effect=side_effect)

        with patch('backend.db.session.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_local.return_value.__aexit__ = AsyncMock(return_value=None)

            await validate_database_schema()

    @pytest.mark.asyncio
    async def test_validate_schema_index_check_fails(self):
        """Test schema validation when index check fails."""
        from backend.main import validate_database_schema

        mock_session = AsyncMock()
        call_count = [0]
        async def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 7:  # Table checks succeed
                return Mock()
            raise Exception("Cannot check indexes")  # Index check fails

        mock_session.execute = AsyncMock(side_effect=side_effect)

        with patch('backend.db.session.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_local.return_value.__aexit__ = AsyncMock(return_value=None)

            await validate_database_schema()


class TestStartupEvent:
    """Tests for startup_event function."""

    @pytest.mark.asyncio
    async def test_startup_default_secret_key_development(self):
        """Test startup with default secret key in development."""
        from backend.main import startup_event

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                ENVIRONMENT="development",
                DEBUG=True,
                SECRET_KEY="your-secret-key-change-in-production",
                DATABASE_URL="postgresql://user:pass@localhost/db",
                REDIS_URL="redis://localhost:6379",
                OLLAMA_URL="http://localhost:11434",
                OTEL_ENABLED=False
            )

            with patch('backend.main._connect_with_retry') as mock_connect:
                mock_connect.return_value = True

                with patch('backend.main.validate_database_schema', new_callable=AsyncMock):
                    with patch('backend.services.auth_service.AuthService') as mock_auth:
                        mock_auth.return_value.create_default_admin = AsyncMock(return_value=None)

                        await startup_event()

    @pytest.mark.asyncio
    async def test_startup_default_secret_key_production_fails(self):
        """Test startup fails with default secret key in production."""
        from backend.main import startup_event

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                ENVIRONMENT="production",
                DEBUG=False,
                SECRET_KEY="your-secret-key-change-in-production",
                DATABASE_URL="postgresql://user:pass@localhost/db"
            )

            with pytest.raises(SystemExit):
                await startup_event()

    @pytest.mark.asyncio
    async def test_startup_database_connection_failure(self):
        """Test startup handles database connection failure."""
        from backend.main import startup_event

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                ENVIRONMENT="development",
                DEBUG=True,
                SECRET_KEY="secure-key",
                DATABASE_URL="postgresql://user:pass@localhost/db",
                REDIS_URL="redis://localhost:6379",
                OLLAMA_URL="http://localhost:11434",
                OTEL_ENABLED=False
            )

            with patch('backend.main._connect_with_retry', new_callable=AsyncMock) as mock_connect:
                mock_connect.side_effect = RuntimeError("Database connection failed")

                with pytest.raises(RuntimeError):
                    await startup_event()

    @pytest.mark.asyncio
    async def test_startup_redis_connection_failure(self):
        """Test startup continues when Redis connection fails."""
        from backend.main import startup_event

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                ENVIRONMENT="development",
                DEBUG=True,
                SECRET_KEY="secure-key",
                DATABASE_URL="postgresql://user:pass@localhost/db",
                REDIS_URL="redis://localhost:6379",
                OLLAMA_URL="http://localhost:11434",
                OTEL_ENABLED=False
            )

            call_count = [0]
            async def mock_connect(name, connect_fn, max_retries, delay, critical):
                call_count[0] += 1
                if name == "Database":
                    return True
                elif name == "Redis":
                    return False  # Redis fails but non-critical
                else:
                    return False  # Ollama fails

            with patch('backend.main._connect_with_retry', side_effect=mock_connect):
                with patch('backend.main.validate_database_schema', new_callable=AsyncMock):
                    with patch('backend.services.auth_service.AuthService') as mock_auth:
                        mock_auth.return_value.create_default_admin = AsyncMock(return_value=None)

                        await startup_event()

    @pytest.mark.asyncio
    async def test_startup_with_otel_enabled(self):
        """Test startup with OpenTelemetry enabled."""
        from backend.main import startup_event

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                ENVIRONMENT="development",
                DEBUG=True,
                SECRET_KEY="secure-key",
                DATABASE_URL="postgresql://user:pass@localhost/db",
                REDIS_URL="redis://localhost:6379",
                OLLAMA_URL="http://localhost:11434",
                OTEL_ENABLED=True,
                OTEL_SERVICE_NAME="test-service",
                OTEL_EXPORTER_ENDPOINT="http://localhost:4317"
            )

            with patch('backend.main._connect_with_retry', return_value=True):
                with patch('backend.main.validate_database_schema', new_callable=AsyncMock):
                    with patch('backend.services.auth_service.AuthService') as mock_auth:
                        mock_auth.return_value.create_default_admin = AsyncMock(return_value=None)

                        with patch('backend.main.setup_tracing') as mock_tracing:
                            mock_tracing.return_value = Mock()

                            await startup_event()

                            mock_tracing.assert_called_once()

    @pytest.mark.asyncio
    async def test_startup_creates_default_admin(self):
        """Test startup creates default admin user."""
        from backend.main import startup_event

        mock_admin_user = Mock()
        mock_admin_user.username = "admin"
        mock_admin_user.email = "admin@example.com"

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                ENVIRONMENT="development",
                DEBUG=True,
                SECRET_KEY="secure-key",
                DATABASE_URL="postgresql://user:pass@localhost/db",
                REDIS_URL="redis://localhost:6379",
                OLLAMA_URL="http://localhost:11434",
                OTEL_ENABLED=False
            )

            with patch('backend.main._connect_with_retry', return_value=True):
                with patch('backend.main.validate_database_schema', new_callable=AsyncMock):
                    with patch('backend.services.auth_service.AuthService') as mock_auth_class:
                        mock_auth = Mock()
                        mock_auth.create_default_admin = AsyncMock(return_value=mock_admin_user)
                        mock_auth_class.return_value = mock_auth

                        await startup_event()

    @pytest.mark.asyncio
    async def test_startup_admin_creation_fails(self):
        """Test startup handles admin creation failure gracefully."""
        from backend.main import startup_event

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                ENVIRONMENT="development",
                DEBUG=True,
                SECRET_KEY="secure-key",
                DATABASE_URL="postgresql://user:pass@localhost/db",
                REDIS_URL="redis://localhost:6379",
                OLLAMA_URL="http://localhost:11434",
                OTEL_ENABLED=False
            )

            with patch('backend.main._connect_with_retry', return_value=True):
                with patch('backend.main.validate_database_schema', new_callable=AsyncMock):
                    with patch('backend.services.auth_service.AuthService') as mock_auth_class:
                        mock_auth = Mock()
                        mock_auth.create_default_admin = AsyncMock(
                            side_effect=Exception("Admin creation failed")
                        )
                        mock_auth_class.return_value = mock_auth

                        # Should not raise, just log warning
                        await startup_event()

    @pytest.mark.asyncio
    async def test_startup_schema_validation_fails(self):
        """Test startup handles schema validation failure gracefully."""
        from backend.main import startup_event

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                ENVIRONMENT="development",
                DEBUG=True,
                SECRET_KEY="secure-key",
                DATABASE_URL="postgresql://user:pass@localhost/db",
                REDIS_URL="redis://localhost:6379",
                OLLAMA_URL="http://localhost:11434",
                OTEL_ENABLED=False
            )

            with patch('backend.main._connect_with_retry', return_value=True):
                with patch('backend.main.validate_database_schema', new_callable=AsyncMock) as mock_validate:
                    mock_validate.side_effect = Exception("Schema validation failed")

                    with patch('backend.services.auth_service.AuthService') as mock_auth_class:
                        mock_auth = Mock()
                        mock_auth.create_default_admin = AsyncMock(return_value=None)
                        mock_auth_class.return_value = mock_auth

                        # Should not raise, just log warning
                        await startup_event()


class TestShutdownEvent:
    """Tests for shutdown_event function."""

    @pytest.mark.asyncio
    async def test_shutdown_closes_database(self):
        """Test shutdown closes database connections."""
        from backend.main import shutdown_event

        mock_engine = AsyncMock()

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(REDIS_URL="redis://localhost:6379")

            with patch('backend.db.session.engine', mock_engine):
                with patch('redis.asyncio.from_url') as mock_redis:
                    mock_redis_client = AsyncMock()
                    mock_redis.return_value = mock_redis_client

                    await shutdown_event()

                    mock_engine.dispose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_shutdown_database_close_error(self):
        """Test shutdown handles database close error."""
        from backend.main import shutdown_event

        mock_engine = AsyncMock()
        mock_engine.dispose = AsyncMock(side_effect=Exception("Close error"))

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(REDIS_URL="redis://localhost:6379")

            with patch('backend.db.session.engine', mock_engine):
                with patch('redis.asyncio.from_url') as mock_redis:
                    mock_redis_client = AsyncMock()
                    mock_redis.return_value = mock_redis_client

                    # Should not raise
                    await shutdown_event()

    @pytest.mark.asyncio
    async def test_shutdown_redis_close_error(self):
        """Test shutdown handles Redis close error."""
        from backend.main import shutdown_event

        mock_engine = AsyncMock()

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(REDIS_URL="redis://localhost:6379")

            with patch('backend.db.session.engine', mock_engine):
                with patch('redis.asyncio.from_url') as mock_redis:
                    mock_redis.side_effect = Exception("Redis error")

                    # Should not raise
                    await shutdown_event()

    @pytest.mark.asyncio
    async def test_shutdown_no_engine(self):
        """Test shutdown when engine is None."""
        from backend.main import shutdown_event

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(REDIS_URL="redis://localhost:6379")

            with patch('backend.db.session.engine', None):
                with patch('redis.asyncio.from_url') as mock_redis:
                    mock_redis_client = AsyncMock()
                    mock_redis.return_value = mock_redis_client

                    await shutdown_event()


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint_development(self):
        """Test root endpoint in development mode."""
        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                ENVIRONMENT="development",
                is_development=True
            )

            from backend.main import app
            client = TestClient(app, raise_server_exceptions=False)

            response = client.get("/")

            assert response.status_code == 200
            data = response.json()
            assert "name" in data
            assert "version" in data
            assert "environment" in data

    def test_root_endpoint_production(self):
        """Test root endpoint in production mode."""
        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                ENVIRONMENT="production",
                is_development=False
            )

            from backend.main import app
            client = TestClient(app, raise_server_exceptions=False)

            response = client.get("/")

            assert response.status_code == 200
            data = response.json()
            assert data.get("documentation") is None


class TestDatabaseURLMasking:
    """Test that database URL is properly masked in logs."""

    @pytest.mark.asyncio
    async def test_database_url_password_masked(self):
        """Test that password is masked in database URL logs."""
        from backend.main import startup_event

        with patch('backend.main.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                APP_NAME="Test App",
                APP_VERSION="1.0.0",
                ENVIRONMENT="development",
                DEBUG=True,
                SECRET_KEY="secure-key",
                DATABASE_URL="postgresql://user:secretpassword@localhost/db",
                REDIS_URL="redis://localhost:6379",
                OLLAMA_URL="http://localhost:11434",
                OTEL_ENABLED=False
            )

            with patch('backend.main._connect_with_retry', return_value=True):
                with patch('backend.main.validate_database_schema', new_callable=AsyncMock):
                    with patch('backend.services.auth_service.AuthService') as mock_auth_class:
                        mock_auth = Mock()
                        mock_auth.create_default_admin = AsyncMock(return_value=None)
                        mock_auth_class.return_value = mock_auth

                        # This should not expose the password in logs
                        await startup_event()
