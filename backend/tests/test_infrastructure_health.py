"""
Tests for HealthChecker in infrastructure module.

Covers all uncovered lines: 81, 100, 102-115, 142-210, 223-263, 293, 299, 310-312, 320-322
"""

import time
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.infrastructure.health_checker import HealthChecker, HealthCheckResult, HealthStatus


class TestHealthCheckerCheckHealth:
    """Tests for check_health method (lines 81, 100, 102-115)."""

    @pytest.mark.asyncio
    async def test_check_health_with_three_element_return(self):
        """Test check_health handles (status, message, details) return."""
        checker = HealthChecker()

        async def detailed_check():
            return HealthStatus.HEALTHY, "OK", {"key": "value"}

        checker.register_check("detailed", detailed_check)
        result = await checker.check_health()

        assert result["status"] == "healthy"
        assert len(result["components"]) == 1
        assert result["components"][0]["details"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_check_health_with_two_element_return(self):
        """Test check_health handles (status, message) return."""
        checker = HealthChecker()

        async def simple_check():
            return HealthStatus.HEALTHY, "OK"

        checker.register_check("simple", simple_check)
        result = await checker.check_health()

        assert result["status"] == "healthy"
        assert result["components"][0]["details"] == {}

    @pytest.mark.asyncio
    async def test_check_health_unhealthy_status(self):
        """Test check_health with unhealthy component."""
        checker = HealthChecker()

        async def unhealthy_check():
            return HealthStatus.UNHEALTHY, "Service down", {"error": "connection refused"}

        checker.register_check("unhealthy", unhealthy_check)
        result = await checker.check_health()

        assert result["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_check_health_degraded_status(self):
        """Test check_health with degraded component."""
        checker = HealthChecker()

        async def degraded_check():
            return HealthStatus.DEGRADED, "Slow response", {}

        checker.register_check("degraded", degraded_check)
        result = await checker.check_health()

        assert result["status"] == "degraded"

    @pytest.mark.asyncio
    async def test_check_health_exception_handling(self):
        """Test check_health handles exceptions in health checks (lines 104-115)."""
        checker = HealthChecker()

        async def failing_check():
            raise RuntimeError("Check failed")

        checker.register_check("failing", failing_check)
        result = await checker.check_health()

        assert result["status"] == "unhealthy"
        component = result["components"][0]
        assert component["status"] == "unhealthy"
        assert "Check failed" in component["message"]
        assert component["details"]["error_type"] == "RuntimeError"

    @pytest.mark.asyncio
    async def test_check_health_latency_tracking(self):
        """Test check_health tracks latency."""
        checker = HealthChecker()

        async def slow_check():
            time.sleep(0.05)  # 50ms
            return HealthStatus.HEALTHY, "OK"

        checker.register_check("slow", slow_check)
        result = await checker.check_health()

        assert result["total_response_time_ms"] >= 50

    @pytest.mark.asyncio
    async def test_check_health_degraded_overrides_healthy(self):
        """Test degraded status overrides healthy (line 102)."""
        checker = HealthChecker()

        async def healthy_check():
            return HealthStatus.HEALTHY, "OK"

        async def degraded_check():
            return HealthStatus.DEGRADED, "Slow"

        checker.register_check("healthy", healthy_check)
        checker.register_check("degraded", degraded_check)
        result = await checker.check_health()

        assert result["status"] == "degraded"

    @pytest.mark.asyncio
    async def test_check_health_unhealthy_overrides_degraded(self):
        """Test unhealthy status overrides degraded (line 100)."""
        checker = HealthChecker()

        async def degraded_check():
            return HealthStatus.DEGRADED, "Slow"

        async def unhealthy_check():
            return HealthStatus.UNHEALTHY, "Down"

        checker.register_check("degraded", degraded_check)
        checker.register_check("unhealthy", unhealthy_check)
        result = await checker.check_health()

        assert result["status"] == "unhealthy"


class TestCheckDatabase:
    """Tests for check_database method (lines 142-210)."""

    @pytest.mark.asyncio
    async def test_check_database_healthy(self):
        """Test check_database with healthy database."""
        checker = HealthChecker()

        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.fetchone.return_value = (1,)
        mock_session.execute.return_value = mock_result

        # Mock SQLAlchemy inspector
        mock_inspector = Mock()
        mock_inspector.get_table_names.return_value = ['users', 'projects', 'workflows', 'tasks', 'other_table']

        async def mock_run_sync(fn):
            # Create a mock sync session with connection
            mock_sync_session = Mock()
            mock_connection = Mock()
            mock_sync_session.connection = Mock(return_value=mock_connection)
            result = fn(mock_sync_session)
            return result

        mock_session.run_sync = mock_run_sync

        # Patch the inspect function to return our mock inspector
        with patch('sqlalchemy.inspect', return_value=mock_inspector):
            mock_pool = Mock()
            mock_pool.size.return_value = 10
            mock_pool.checkedin.return_value = 8
            mock_pool.checkedout.return_value = 2
            mock_pool.overflow.return_value = 0

            mock_engine = Mock()
            mock_engine.pool = mock_pool

            mock_session_ctx = AsyncMock()
            mock_session_ctx.__aenter__.return_value = mock_session
            mock_session_ctx.__aexit__.return_value = None

            with patch('backend.db.session.AsyncSessionLocal', return_value=mock_session_ctx), \
                 patch('backend.db.session.engine', mock_engine):
                status, message, details = await checker.check_database()

                assert status == HealthStatus.HEALTHY
                assert "Database OK" in message
                assert "pool_stats" in details

    @pytest.mark.asyncio
    async def test_check_database_missing_tables(self):
        """Test check_database with missing tables."""
        checker = HealthChecker()

        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.fetchone.return_value = (1,)

        # Mock SQLAlchemy inspector - simulate missing tables
        mock_inspector = Mock()
        mock_inspector.get_table_names.return_value = ['workflows', 'tasks']  # Missing 'users' and 'projects'

        async def mock_run_sync(fn):
            # Create a mock sync session with connection
            mock_sync_session = Mock()
            mock_connection = Mock()
            mock_sync_session.connection = Mock(return_value=mock_connection)
            result = fn(mock_sync_session)
            return result

        mock_session.run_sync = mock_run_sync

        # Patch the inspect function to return our mock inspector
        with patch('sqlalchemy.inspect', return_value=mock_inspector):
            mock_pool = Mock()
            mock_pool.size.return_value = 10
            mock_pool.checkedin.return_value = 8
            mock_pool.checkedout.return_value = 2
            mock_pool.overflow.return_value = 0

            mock_engine = Mock()
            mock_engine.pool = mock_pool

            mock_session_ctx = AsyncMock()
            mock_session_ctx.__aenter__.return_value = mock_session
            mock_session_ctx.__aexit__.return_value = None

            with patch('backend.db.session.AsyncSessionLocal', return_value=mock_session_ctx), \
                 patch('backend.db.session.engine', mock_engine):
                status, message, details = await checker.check_database()

                # Should be degraded due to missing tables
                assert status == HealthStatus.DEGRADED
                assert "missing tables" in message.lower()
                assert "users" in message
                assert "projects" in message

    @pytest.mark.asyncio
    async def test_check_database_slow_query(self):
        """Test check_database with slow query latency."""
        checker = HealthChecker()

        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.fetchone.return_value = (1,)
        mock_session.execute.return_value = mock_result

        # Mock SQLAlchemy inspector
        mock_inspector = Mock()
        mock_inspector.get_table_names.return_value = ['users', 'projects', 'workflows', 'tasks']

        async def mock_run_sync(fn):
            # Create a mock sync session with connection
            mock_sync_session = Mock()
            mock_connection = Mock()
            mock_sync_session.connection = Mock(return_value=mock_connection)
            result = fn(mock_sync_session)
            return result

        mock_session.run_sync = mock_run_sync

        # Patch the inspect function to return our mock inspector
        with patch('sqlalchemy.inspect', return_value=mock_inspector):
            mock_pool = Mock()
            mock_pool.size.return_value = 10
            mock_pool.checkedin.return_value = 8
            mock_pool.checkedout.return_value = 2
            mock_pool.overflow.return_value = 0

            mock_engine = Mock()
            mock_engine.pool = mock_pool

            mock_session_ctx = AsyncMock()
            mock_session_ctx.__aenter__.return_value = mock_session
            mock_session_ctx.__aexit__.return_value = None

            with patch('backend.db.session.AsyncSessionLocal', return_value=mock_session_ctx), \
                 patch('backend.db.session.engine', mock_engine), \
                 patch('time.time') as mock_time:
                # Simulate 1500ms query time
                mock_time.side_effect = [0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]

                status, message, details = await checker.check_database()

                # Should be degraded due to slow query
                assert status == HealthStatus.DEGRADED
                assert "slow" in message.lower()

    @pytest.mark.asyncio
    async def test_check_database_exception(self):
        """Test check_database handles exceptions (lines 208-214)."""
        checker = HealthChecker()

        with patch('backend.db.session.AsyncSessionLocal', side_effect=Exception("Connection refused")), \
             patch('backend.db.session.engine', Mock()):
            status, message, details = await checker.check_database()

            assert status == HealthStatus.UNHEALTHY
            assert "Connection refused" in str(details.get("error", message))

    @pytest.mark.asyncio
    async def test_check_database_pool_stats_no_methods(self):
        """Test check_database when pool doesn't have stat methods."""
        checker = HealthChecker()

        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.fetchone.return_value = (1,)
        mock_session.execute.return_value = mock_result

        # Pool without stat methods
        mock_pool = Mock(spec=[])

        mock_engine = Mock()
        mock_engine.pool = mock_pool

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__.return_value = mock_session
        mock_session_ctx.__aexit__.return_value = None

        with patch('backend.db.session.AsyncSessionLocal', return_value=mock_session_ctx), \
             patch('backend.db.session.engine', mock_engine):
            status, message, details = await checker.check_database()

            assert details["pool_stats"]["size"] == "N/A"


class TestCheckRedis:
    """Tests for check_redis method (lines 223-263)."""

    @pytest.mark.asyncio
    async def test_check_redis_healthy(self):
        """Test check_redis with healthy Redis."""
        checker = HealthChecker()

        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        mock_client.info.return_value = {"redis_version": "7.0.0"}
        mock_client.close = AsyncMock()

        mock_settings = Mock()
        mock_settings.REDIS_URL = "redis://localhost:6379"

        with patch('redis.asyncio.from_url', return_value=mock_client), \
             patch('backend.core.config.get_settings', return_value=mock_settings):
            status, message, details = await checker.check_redis()

            assert status == HealthStatus.HEALTHY
            assert "Redis OK" in message
            assert details["redis_version"] == "7.0.0"

    @pytest.mark.asyncio
    async def test_check_redis_slow(self):
        """Test check_redis with slow Redis response."""
        checker = HealthChecker()

        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        mock_client.info.return_value = {}
        mock_client.close = AsyncMock()

        mock_settings = Mock()
        mock_settings.REDIS_URL = "redis://localhost:6379"

        with patch('redis.asyncio.from_url', return_value=mock_client), \
             patch('backend.core.config.get_settings', return_value=mock_settings), \
             patch('time.time') as mock_time:
            # Simulate 150ms ping time
            mock_time.side_effect = [0, 0.15, 0.15]

            status, message, details = await checker.check_redis()

            assert status == HealthStatus.DEGRADED
            assert "slow" in message.lower()

    @pytest.mark.asyncio
    async def test_check_redis_info_exception(self):
        """Test check_redis when info() raises exception."""
        checker = HealthChecker()

        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        mock_client.info.side_effect = Exception("Info not available")
        mock_client.close = AsyncMock()

        mock_settings = Mock()
        mock_settings.REDIS_URL = "redis://localhost:6379"

        with patch('redis.asyncio.from_url', return_value=mock_client), \
             patch('backend.core.config.get_settings', return_value=mock_settings):
            status, message, details = await checker.check_redis()

            # Should still be healthy if ping works
            assert status == HealthStatus.HEALTHY
            assert "redis_version" not in details

    @pytest.mark.asyncio
    async def test_check_redis_connection_error(self):
        """Test check_redis with connection error (lines 261-267)."""
        checker = HealthChecker()

        mock_settings = Mock()
        mock_settings.REDIS_URL = "redis://localhost:6379"

        with patch('redis.asyncio.from_url', side_effect=Exception("Connection refused")), \
             patch('backend.core.config.get_settings', return_value=mock_settings):
            status, message, details = await checker.check_redis()

            assert status == HealthStatus.UNHEALTHY
            assert "Connection refused" in str(details.get("error", message))


class TestCheckDiskSpace:
    """Tests for check_disk_space method (lines 293, 299, 310-312)."""

    @pytest.mark.asyncio
    async def test_check_disk_space_healthy(self):
        """Test check_disk_space with plenty of space."""
        checker = HealthChecker()

        # Simulate 100GB total, 50GB used, 50GB free
        with patch('shutil.disk_usage') as mock_disk:
            mock_disk.return_value = (
                100 * 1024**3,  # 100GB total
                50 * 1024**3,   # 50GB used
                50 * 1024**3    # 50GB free
            )

            status, message, details = await checker.check_disk_space()

            assert status == HealthStatus.HEALTHY
            assert details["free_gb"] == 50.0

    @pytest.mark.asyncio
    async def test_check_disk_space_critical(self):
        """Test check_disk_space with critical low space (line 293)."""
        checker = HealthChecker()

        # Simulate less than 1GB free
        with patch('shutil.disk_usage') as mock_disk:
            mock_disk.return_value = (
                100 * 1024**3,   # 100GB total
                99.5 * 1024**3,  # 99.5GB used
                0.5 * 1024**3    # 0.5GB free
            )

            status, message, details = await checker.check_disk_space()

            assert status == HealthStatus.UNHEALTHY
            assert "Critical" in message

    @pytest.mark.asyncio
    async def test_check_disk_space_low(self):
        """Test check_disk_space with low space (line 299)."""
        checker = HealthChecker()

        # Simulate between 1GB and 5GB free
        with patch('shutil.disk_usage') as mock_disk:
            mock_disk.return_value = (
                100 * 1024**3,  # 100GB total
                97 * 1024**3,  # 97GB used
                3 * 1024**3    # 3GB free
            )

            status, message, details = await checker.check_disk_space()

            assert status == HealthStatus.DEGRADED
            assert "Low disk" in message

    @pytest.mark.asyncio
    async def test_check_disk_space_exception(self):
        """Test check_disk_space handles exceptions (lines 310-316)."""
        checker = HealthChecker()

        with patch('shutil.disk_usage') as mock_disk:
            mock_disk.side_effect = OSError("Permission denied")

            status, message, details = await checker.check_disk_space()

            assert status == HealthStatus.UNHEALTHY
            assert "Permission denied" in str(details.get("error", message))


class TestSetupDefaultChecks:
    """Tests for setup_default_checks method (lines 320-322)."""

    def test_setup_default_checks(self):
        """Test setup_default_checks registers all default checks."""
        checker = HealthChecker()
        checker.setup_default_checks()

        assert "database" in checker._checks
        assert "redis" in checker._checks
        assert "disk" in checker._checks
        assert checker._checks["database"] == checker.check_database
        assert checker._checks["redis"] == checker.check_redis
        assert checker._checks["disk"] == checker.check_disk_space


class TestHealthCheckResult:
    """Tests for HealthCheckResult dataclass."""

    def test_health_check_result_creation(self):
        """Test HealthCheckResult creation."""
        result = HealthCheckResult(
            component="test",
            status=HealthStatus.HEALTHY,
            message="OK",
            timestamp=datetime.utcnow(),
            latency_ms=50.0,
            details={"key": "value"}
        )

        assert result.component == "test"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "OK"
        assert result.latency_ms == 50.0
        assert result.details == {"key": "value"}

    def test_health_check_result_default_details(self):
        """Test HealthCheckResult has default empty details."""
        result = HealthCheckResult(
            component="test",
            status=HealthStatus.HEALTHY,
            message="OK",
            timestamp=datetime.utcnow(),
            latency_ms=50.0
        )

        assert result.details == {}


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_health_status_values(self):
        """Test HealthStatus enum values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
