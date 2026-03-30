"""
Comprehensive tests for AdminPanelService to increase coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC, timedelta
import uuid

from backend.services.admin_panel_service import (
    AdminPanelService, UserRole, SystemStatus, MaintenanceMode,
    AdminUser, SystemMetrics, SystemHealth, AuditLog, MaintenanceSchedule
)


class TestAdminPanelService:
    """Comprehensive tests for AdminPanelService."""

    @pytest.fixture
    def admin_service(self):
        """Create AdminPanelService instance."""
        return AdminPanelService()

    def test_init(self, admin_service):
        """Test AdminPanelService initialization."""
        assert admin_service is not None
        assert hasattr(admin_service, 'admin_users')
        assert hasattr(admin_service, 'audit_logs')
        assert hasattr(admin_service, 'maintenance_schedules')
        assert hasattr(admin_service, '_current_maintenance_mode')
        
        # Should have sample data initialized
        assert len(admin_service.admin_users) > 0
        assert len(admin_service.audit_logs) > 0

    def test_sample_data_initialization(self, admin_service):
        """Test that sample data is properly initialized."""
        # Check admin users
        assert len(admin_service.admin_users) >= 3
        
        # Check super admin
        super_admin = admin_service.admin_users.get("admin_1")
        assert super_admin is not None
        assert super_admin.username == "super_admin"
        assert super_admin.role == UserRole.SUPER_ADMIN
        assert super_admin.is_active is True
        
        # Check regular admin
        admin = admin_service.admin_users.get("admin_2")
        assert admin is not None
        assert admin.username == "system_admin"
        assert admin.role == UserRole.ADMIN
        
        # Check moderator
        moderator = admin_service.admin_users.get("admin_3")
        assert moderator is not None
        assert moderator.username == "content_mod"
        assert moderator.role == UserRole.MODERATOR
        
        # Check audit logs
        assert len(admin_service.audit_logs) >= 2
        for log in admin_service.audit_logs:
            assert isinstance(log, AuditLog)
            assert len(log.id) > 0
            assert len(log.user_id) > 0

    @pytest.mark.asyncio
    async def test_authenticate_admin_success(self, admin_service):
        """Test successful admin authentication."""
        result = await admin_service.authenticate_admin("super_admin", "any_password")
        
        assert result is not None
        assert isinstance(result, AdminUser)
        assert result.username == "super_admin"
        assert result.is_active is True
        # Last login should be updated
        assert result.last_login is not None

    @pytest.mark.asyncio
    async def test_authenticate_admin_inactive_user(self, admin_service):
        """Test authentication with inactive user."""
        # Make a user inactive for testing
        user_id = "admin_test"
        inactive_user = AdminUser(
            id=user_id,
            username="inactive_admin",
            email="inactive@test.com",
            role=UserRole.ADMIN,
            is_active=False,  # Inactive
            last_login=None,
            created_at=datetime.now(UTC).isoformat(),
            permissions=[]
        )
        admin_service.admin_users[user_id] = inactive_user
        
        result = await admin_service.authenticate_admin("inactive_admin", "password")
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_admin_user_not_found(self, admin_service):
        """Test authentication with non-existent user."""
        result = await admin_service.authenticate_admin("nonexistent_user", "password")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_system_metrics(self, admin_service):
        """Test getting system metrics."""
        result = await admin_service.get_system_metrics()
        
        assert result is not None
        assert isinstance(result, SystemMetrics)
        assert isinstance(result.cpu_usage, float)
        assert isinstance(result.memory_usage, float)
        assert isinstance(result.disk_usage, float)
        assert isinstance(result.network_io, dict)
        assert isinstance(result.request_count, int)
        assert isinstance(result.error_rate, float)
        assert isinstance(result.response_time_avg, float)
        assert isinstance(result.uptime, str)
        assert isinstance(result.timestamp, str)
        
        # Values should be reasonable
        assert 0 <= result.cpu_usage <= 100
        assert 0 <= result.memory_usage <= 100
        assert 0 <= result.disk_usage <= 100
        assert result.request_count >= 0
        assert 0 <= result.error_rate <= 1

    @pytest.mark.asyncio
    async def test_get_system_health(self, admin_service):
        """Test getting system health."""
        result = await admin_service.get_system_health()
        
        assert result is not None
        assert isinstance(result, SystemHealth)
        assert isinstance(result.overall_status, SystemStatus)
        assert isinstance(result.services, dict)
        assert isinstance(result.databases, dict)
        assert isinstance(result.external_services, dict)
        assert isinstance(result.alerts, list)
        assert isinstance(result.last_checked, str)
        
        # Should have service status information
        assert len(result.services) > 0
        assert len(result.databases) > 0
        assert len(result.external_services) > 0

    @pytest.mark.asyncio
    async def test_get_audit_logs_all(self, admin_service):
        """Test getting all audit logs."""
        result = await admin_service.get_audit_logs()
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        for log in result:
            assert isinstance(log, AuditLog)

    @pytest.mark.asyncio
    async def test_get_audit_logs_filtered_by_user(self, admin_service):
        """Test filtering audit logs by user."""
        result = await admin_service.get_audit_logs(user_id="admin_1")
        
        assert isinstance(result, list)
        # All logs should be from admin_1
        for log in result:
            assert log.user_id == "admin_1"

    @pytest.mark.asyncio
    async def test_get_audit_logs_filtered_by_action(self, admin_service):
        """Test filtering audit logs by action."""
        result = await admin_service.get_audit_logs(action="user_created")
        
        assert isinstance(result, list)
        # All logs should be user_created actions
        for log in result:
            assert log.action == "user_created"

    @pytest.mark.asyncio
    async def test_get_audit_logs_limit(self, admin_service):
        """Test limiting audit logs."""
        result = await admin_service.get_audit_logs(limit=1)
        
        assert isinstance(result, list)
        assert len(result) <= 1

    @pytest.mark.asyncio
    async def test_log_admin_action(self, admin_service):
        """Test logging admin action."""
        initial_log_count = len(admin_service.audit_logs)
        
        result = await admin_service.log_admin_action(
            user_id="admin_1",
            action="test_action",
            resource_type="test_resource",
            resource_id="test_123",
            details={"test": "data"},
            ip_address="192.168.1.1",
            user_agent="test_client"
        )
        
        assert result is not None
        assert isinstance(result, AuditLog)
        assert result.user_id == "admin_1"
        assert result.action == "test_action"
        assert result.resource_type == "test_resource"
        assert result.resource_id == "test_123"
        assert result.details == {"test": "data"}
        assert result.ip_address == "192.168.1.1"
        assert result.user_agent == "test_client"
        
        # Should have been added to logs
        assert len(admin_service.audit_logs) == initial_log_count + 1

    @pytest.mark.asyncio
    async def test_create_maintenance_schedule(self, admin_service):
        """Test creating maintenance schedule."""
        result = await admin_service.create_maintenance_schedule(
            title="Database Maintenance",
            description="Regular database maintenance window",
            start_time="2024-12-01T02:00:00Z",
            end_time="2024-12-01T04:00:00Z",
            mode=MaintenanceMode.READ_ONLY,
            affected_services=["database", "api"],
            created_by="admin_1"
        )
        
        assert result is not None
        assert isinstance(result, MaintenanceSchedule)
        assert result.title == "Database Maintenance"
        assert result.description == "Regular database maintenance window"
        assert result.mode == MaintenanceMode.READ_ONLY
        assert result.is_active is True
        assert "database" in result.affected_services
        assert "api" in result.affected_services
        assert len(result.id) > 0

    @pytest.mark.asyncio
    async def test_get_maintenance_schedules_all(self, admin_service):
        """Test getting all maintenance schedules."""
        # Create a schedule first
        await admin_service.create_maintenance_schedule(
            title="Test Schedule",
            description="Test",
            start_time="2024-12-01T00:00:00Z",
            end_time="2024-12-01T01:00:00Z",
            mode=MaintenanceMode.MAINTENANCE,
            affected_services=["test"],
            created_by="admin_1"
        )
        
        result = await admin_service.get_maintenance_schedules()
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        for schedule in result:
            assert isinstance(schedule, MaintenanceSchedule)

    @pytest.mark.asyncio
    async def test_get_maintenance_schedules_active_only(self, admin_service):
        """Test getting only active maintenance schedules."""
        result = await admin_service.get_maintenance_schedules(active_only=True)
        
        assert isinstance(result, list)
        # All should be active
        for schedule in result:
            assert schedule.is_active is True

    @pytest.mark.asyncio
    async def test_update_maintenance_mode(self, admin_service):
        """Test updating maintenance mode."""
        # Change to maintenance mode
        result = await admin_service.update_maintenance_mode(MaintenanceMode.MAINTENANCE)
        
        assert result is True
        
        # Check current mode
        current_mode = await admin_service.get_current_maintenance_mode()
        assert current_mode == MaintenanceMode.MAINTENANCE

    @pytest.mark.asyncio
    async def test_get_current_maintenance_mode(self, admin_service):
        """Test getting current maintenance mode."""
        result = await admin_service.get_current_maintenance_mode()
        
        assert isinstance(result, MaintenanceMode)
        assert result in [MaintenanceMode.OFF, MaintenanceMode.READ_ONLY, MaintenanceMode.MAINTENANCE]

    @pytest.mark.asyncio
    async def test_get_admin_users_all(self, admin_service):
        """Test getting all admin users."""
        result = await admin_service.get_admin_users()
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        for user in result:
            assert isinstance(user, AdminUser)

    @pytest.mark.asyncio
    async def test_get_admin_users_active_only(self, admin_service):
        """Test getting only active admin users."""
        result = await admin_service.get_admin_users(active_only=True)
        
        assert isinstance(result, list)
        # All should be active
        for user in result:
            assert user.is_active is True

    @pytest.mark.asyncio
    async def test_create_admin_user_success(self, admin_service):
        """Test creating admin user successfully."""
        result = await admin_service.create_admin_user(
            username="new_admin",
            email="new_admin@test.com",
            role=UserRole.ADMIN,
            permissions=["manage_users", "view_logs"],
            created_by="admin_1"
        )
        
        assert result is not None
        assert isinstance(result, AdminUser)
        assert result.username == "new_admin"
        assert result.email == "new_admin@test.com"
        assert result.role == UserRole.ADMIN
        assert result.is_active is True
        assert result.permissions == ["manage_users", "view_logs"]
        assert len(result.id) > 0
        
        # Should be added to admin users
        assert result.id in admin_service.admin_users

    @pytest.mark.asyncio
    async def test_create_admin_user_duplicate_username(self, admin_service):
        """Test creating admin user with duplicate username."""
        with pytest.raises(ValueError) as exc_info:
            await admin_service.create_admin_user(
                username="super_admin",  # Already exists
                email="new@test.com",
                role=UserRole.ADMIN,
                permissions=[],
                created_by="admin_1"
            )
        
        assert "User with this username or email already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_admin_user_duplicate_email(self, admin_service):
        """Test creating admin user with duplicate email."""
        with pytest.raises(ValueError) as exc_info:
            await admin_service.create_admin_user(
                username="new_user",
                email="admin@thetaai.com",  # Already exists
                role=UserRole.ADMIN,
                permissions=[],
                created_by="admin_1"
            )
        
        assert "User with this username or email already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_admin_user_success(self, admin_service):
        """Test updating admin user successfully."""
        # Create a user first
        user = await admin_service.create_admin_user(
            username="update_test",
            email="update@test.com",
            role=UserRole.MODERATOR,
            permissions=["view_logs"],
            created_by="admin_1"
        )
        
        # Update the user
        updates = {
            "role": UserRole.ADMIN,
            "permissions": ["manage_users", "view_logs", "configure_settings"]
        }
        
        result = await admin_service.update_admin_user(user.id, **updates)
        
        assert result is not None
        assert result.role == UserRole.ADMIN
        assert "manage_users" in result.permissions
        assert "configure_settings" in result.permissions

    @pytest.mark.asyncio
    async def test_update_admin_user_not_found(self, admin_service):
        """Test updating non-existent admin user."""
        with pytest.raises(ValueError) as exc_info:
            await admin_service.update_admin_user("nonexistent_id", role=UserRole.ADMIN)
        
        assert "Admin user not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_system_statistics(self, admin_service):
        """Test getting system statistics."""
        result = await admin_service.get_system_statistics()
        
        assert isinstance(result, dict)
        assert "system_metrics" in result
        assert "system_health" in result
        assert "administrative" in result
        assert "activity" in result
        assert "maintenance" in result
        
        # Check administrative stats
        admin_stats = result["administrative"]
        assert "total_admins" in admin_stats
        assert "active_admins" in admin_stats
        assert "roles_distribution" in admin_stats
        assert isinstance(admin_stats["total_admins"], int)
        assert isinstance(admin_stats["active_admins"], int)
        assert isinstance(admin_stats["roles_distribution"], dict)
        
        # Check activity stats
        activity_stats = result["activity"]
        assert "recent_actions" in activity_stats
        assert "actions_today" in activity_stats
        assert "unique_users_today" in activity_stats

    @pytest.mark.asyncio
    async def test_perform_system_backup(self, admin_service):
        """Test performing system backup."""
        result = await admin_service.perform_system_backup(backup_type="full")
        
        assert isinstance(result, dict)
        assert "backup_id" in result
        assert "type" in result
        assert "status" in result
        assert "start_time" in result
        assert "end_time" in result
        assert "duration_seconds" in result
        assert "size_bytes" in result
        assert "files_count" in result
        
        assert result["type"] == "full"
        assert result["status"] == "completed"
        assert isinstance(result["duration_seconds"], float)
        assert result["duration_seconds"] >= 0
        assert result["size_bytes"] > 0
        assert result["files_count"] > 0

    @pytest.mark.asyncio
    async def test_restart_service(self, admin_service):
        """Test restarting service."""
        result = await admin_service.restart_service("test_service")
        
        assert result is True

    def test_get_roles_distribution(self, admin_service):
        """Test getting roles distribution."""
        result = admin_service._get_roles_distribution()
        
        assert isinstance(result, dict)
        assert len(result) > 0
        
        # Should contain keys for each role type that exists
        for role_value in [r.value for r in UserRole]:
            if any(user.role.value == role_value for user in admin_service.admin_users.values()):
                assert role_value in result
                assert isinstance(result[role_value], int)
                assert result[role_value] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])