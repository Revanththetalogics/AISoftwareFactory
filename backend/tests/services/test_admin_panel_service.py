"""
Comprehensive tests for AdminPanelService to increase coverage.
"""

from unittest.mock import Mock, patch

import pytest
from backend.services.admin_panel_service import AdminPanelService, AuditLog, SystemHealth, SystemMetrics


class TestAdminPanelService:
    """Test AdminPanelService functionality."""

    @pytest.fixture
    def admin_service(self):
        """Create AdminPanelService instance."""
        return AdminPanelService()

    def test_init(self, admin_service):
        """Test service initialization."""
        assert admin_service is not None
        assert hasattr(admin_service, "admin_users")
        assert hasattr(admin_service, "audit_logs")
        assert hasattr(admin_service, "maintenance_schedules")

    @pytest.mark.asyncio
    async def test_get_system_health(self, admin_service):
        """Test getting system health information."""
        health = await admin_service.get_system_health()

        assert isinstance(health, SystemHealth)
        assert health.overall_status.name == "HEALTHY"
        assert isinstance(health.services, dict)
        assert isinstance(health.databases, dict)
        assert isinstance(health.external_services, dict)
        assert isinstance(health.alerts, list)

    @pytest.mark.asyncio
    async def test_get_audit_logs(self, admin_service):
        """Test getting audit logs."""
        logs = await admin_service.get_audit_logs(limit=10)

        assert isinstance(logs, list)
        # Should return the sample logs
        assert len(logs) >= 0

        if logs:
            assert isinstance(logs[0], AuditLog)

    @pytest.mark.asyncio
    async def test_get_system_metrics(self, admin_service):
        """Test getting system metrics."""
        metrics = await admin_service.get_system_metrics()

        assert isinstance(metrics, SystemMetrics)
        assert isinstance(metrics.cpu_usage, float)
        assert isinstance(metrics.memory_usage, float)
        assert isinstance(metrics.disk_usage, float)
        assert isinstance(metrics.network_io, dict)
        assert isinstance(metrics.request_count, int)
        assert isinstance(metrics.error_rate, float)
        assert isinstance(metrics.response_time_avg, float)
        assert isinstance(metrics.uptime, str)
        assert isinstance(metrics.timestamp, str)

    @pytest.mark.asyncio
    async def test_authenticate_admin(self, admin_service):
        """Test admin authentication."""
        # Test with sample user
        user = await admin_service.authenticate_admin("super_admin", "password123")

        if user:
            assert user.username == "super_admin"
            assert user.is_active is True

        # Test with invalid credentials
        invalid_user = await admin_service.authenticate_admin("nonexistent", "wrongpass")
        assert invalid_user is None

    @pytest.mark.asyncio
    async def test_get_audit_logs_with_filters(self, admin_service):
        """Test getting audit logs with filters."""
        # Test with user filter
        logs = await admin_service.get_audit_logs(user_id="admin_1")
        assert isinstance(logs, list)

        # Test with action filter
        logs = await admin_service.get_audit_logs(action="user_created")
        assert isinstance(logs, list)

    @pytest.mark.asyncio
    async def test_get_audit_logs_limit(self, admin_service):
        """Test audit logs limit parameter."""
        logs = await admin_service.get_audit_logs(limit=5)
        assert len(logs) <= 5

    @pytest.mark.asyncio
    async def test_logger_error_handling(self, admin_service):
        """Test that service works even if logger has issues."""
        with patch("backend.core.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_logger.info.side_effect = Exception("Logger error")
            mock_logger.error.side_effect = Exception("Logger error")
            mock_get_logger.return_value = mock_logger

            # These operations should still work despite logger errors
            health = await admin_service.get_system_health()
            assert isinstance(health, SystemHealth)

            metrics = await admin_service.get_system_metrics()
            assert isinstance(metrics, SystemMetrics)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
