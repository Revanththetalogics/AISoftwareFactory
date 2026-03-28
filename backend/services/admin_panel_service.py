"""
Admin Panel Service

Provides comprehensive administrative capabilities for system management,
user management, configuration, monitoring, and maintenance operations.
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class UserRole(str, Enum):
    """User roles with administrative permissions."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


class SystemStatus(str, Enum):
    """Overall system status indicators."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNSTABLE = "unstable"
    DOWN = "down"


class MaintenanceMode(str, Enum):
    """Maintenance mode states."""
    OFF = "off"
    READ_ONLY = "read_only"
    MAINTENANCE = "maintenance"


@dataclass
class AdminUser:
    """Represents an administrative user."""
    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool
    last_login: str | None
    created_at: str
    permissions: list[str]


@dataclass
class SystemMetrics:
    """Current system performance metrics."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: dict[str, float]
    request_count: int
    error_rate: float
    response_time_avg: float
    uptime: str
    timestamp: str


@dataclass
class SystemHealth:
    """Comprehensive system health status."""
    overall_status: SystemStatus
    services: dict[str, str]  # service_name -> status
    databases: dict[str, str]  # db_name -> status
    external_services: dict[str, str]  # service_name -> status
    alerts: list[dict[str, Any]]
    last_checked: str


@dataclass
class AuditLog:
    """Administrative audit log entry."""
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: dict[str, Any]
    ip_address: str
    user_agent: str
    timestamp: str


@dataclass
class MaintenanceSchedule:
    """Scheduled maintenance window."""
    id: str
    title: str
    description: str
    start_time: str
    end_time: str
    mode: MaintenanceMode
    affected_services: list[str]
    created_by: str
    created_at: str
    is_active: bool


class AdminPanelService:
    """Main service for administrative panel functionality."""

    def __init__(self):
        self.admin_users: dict[str, AdminUser] = {}
        self.audit_logs: list[AuditLog] = []
        self.maintenance_schedules: dict[str, MaintenanceSchedule] = {}
        self._current_maintenance_mode = MaintenanceMode.OFF
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize with sample administrative data."""
        # Sample admin users
        super_admin = AdminUser(
            id="admin_1",
            username="super_admin",
            email="admin@thetaai.com",
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            last_login=datetime.now(UTC).isoformat(),
            created_at=datetime.now(UTC).isoformat(),
            permissions=[
                "manage_users", "manage_system", "view_logs",
                "configure_settings", "perform_maintenance"
            ]
        )

        admin = AdminUser(
            id="admin_2",
            username="system_admin",
            email="sysadmin@thetaai.com",
            role=UserRole.ADMIN,
            is_active=True,
            last_login=(datetime.now(UTC) - timedelta(hours=2)).isoformat(),
            created_at=datetime.now(UTC).isoformat(),
            permissions=["manage_users", "view_logs", "configure_settings"]
        )

        moderator = AdminUser(
            id="admin_3",
            username="content_mod",
            email="mod@thetaai.com",
            role=UserRole.MODERATOR,
            is_active=True,
            last_login=(datetime.now(UTC) - timedelta(days=1)).isoformat(),
            created_at=datetime.now(UTC).isoformat(),
            permissions=["view_logs", "moderate_content"]
        )

        self.admin_users = {
            super_admin.id: super_admin,
            admin.id: admin,
            moderator.id: moderator
        }

        # Sample audit logs
        audit_entries = [
            AuditLog(
                id=f"log_{uuid.uuid4().hex[:8]}",
                user_id="admin_1",
                action="user_created",
                resource_type="user",
                resource_id="user_123",
                details={"username": "new_user", "role": "developer"},
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0...",
                timestamp=(datetime.now(UTC) - timedelta(hours=1)).isoformat()
            ),
            AuditLog(
                id=f"log_{uuid.uuid4().hex[:8]}",
                user_id="admin_1",
                action="system_restarted",
                resource_type="system",
                resource_id="main_server",
                details={"reason": "scheduled_maintenance", "duration": "5 minutes"},
                ip_address="192.168.1.100",
                user_agent="curl/7.68.0",
                timestamp=(datetime.now(UTC) - timedelta(hours=3)).isoformat()
            )
        ]

        self.audit_logs.extend(audit_entries)

    async def authenticate_admin(self, username: str, password: str) -> AdminUser | None:
        """Authenticate administrative user."""
        try:
            # In a real implementation, this would check against a secure auth system
            # For demo, we'll simulate successful authentication for sample users
            for user in self.admin_users.values():
                if user.username == username and user.is_active:
                    user.last_login = datetime.now(UTC).isoformat()
                    logger.info(f"Admin user authenticated: {username}")
                    return user

            logger.warning(f"Admin authentication failed for: {username}")
            return None

        except Exception as e:
            logger.error("Admin authentication error", error=str(e))
            raise

    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics."""
        try:
            # Simulated metrics - in real implementation, would query actual system
            now = datetime.now(UTC)

            metrics = SystemMetrics(
                cpu_usage=23.5,  # Percentage
                memory_usage=67.2,  # Percentage
                disk_usage=45.8,  # Percentage
                network_io={
                    "bytes_in": 1024000.0,
                    "bytes_out": 512000.0
                },
                request_count=1250,
                error_rate=0.02,  # 2%
                response_time_avg=156.7,  # milliseconds
                uptime="15 days, 4:32:18",
                timestamp=now.isoformat()
            )

            return metrics

        except Exception as e:
            logger.error("Failed to get system metrics", error=str(e))
            raise

    async def get_system_health(self) -> SystemHealth:
        """Get comprehensive system health status."""
        try:
            # Simulated health check - in real implementation, would check actual services
            now = datetime.now(UTC)

            health = SystemHealth(
                overall_status=SystemStatus.HEALTHY,
                services={
                    "api_gateway": "healthy",
                    "auth_service": "healthy",
                    "database": "healthy",
                    "redis_cache": "degraded",
                    "message_queue": "healthy"
                },
                databases={
                    "main_db": "healthy",
                    "analytics_db": "healthy",
                    "logs_db": "healthy"
                },
                external_services={
                    "github_api": "healthy",
                    "docker_registry": "healthy",
                    "cloud_storage": "healthy"
                },
                alerts=[
                    {
                        "severity": "warning",
                        "message": "Redis cache performance degraded",
                        "timestamp": (now - timedelta(minutes=15)).isoformat()
                    }
                ],
                last_checked=now.isoformat()
            )

            return health

        except Exception as e:
            logger.error("Failed to get system health", error=str(e))
            raise

    async def get_audit_logs(
        self,
        limit: int = 50,
        user_id: str | None = None,
        action: str | None = None
    ) -> list[AuditLog]:
        """Get administrative audit logs."""
        try:
            logs = self.audit_logs.copy()

            # Apply filters
            if user_id:
                logs = [log for log in logs if log.user_id == user_id]

            if action:
                logs = [log for log in logs if log.action == action]

            # Sort by timestamp (newest first)
            logs.sort(key=lambda x: x.timestamp, reverse=True)

            return logs[:limit]

        except Exception as e:
            logger.error("Failed to get audit logs", error=str(e))
            raise

    async def log_admin_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any],
        ip_address: str,
        user_agent: str
    ) -> AuditLog:
        """Log an administrative action."""
        try:
            log_entry = AuditLog(
                id=f"log_{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.now(UTC).isoformat()
            )

            self.audit_logs.append(log_entry)

            # Keep only last 1000 logs
            if len(self.audit_logs) > 1000:
                self.audit_logs = self.audit_logs[-1000:]

            logger.info(f"Admin action logged: {action}", user_id=user_id)
            return log_entry

        except Exception as e:
            logger.error("Failed to log admin action", error=str(e))
            raise

    async def create_maintenance_schedule(
        self,
        title: str,
        description: str,
        start_time: str,
        end_time: str,
        mode: MaintenanceMode,
        affected_services: list[str],
        created_by: str
    ) -> MaintenanceSchedule:
        """Create a scheduled maintenance window."""
        try:
            schedule_id = f"maint_{uuid.uuid4().hex[:8]}"

            schedule = MaintenanceSchedule(
                id=schedule_id,
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                mode=mode,
                affected_services=affected_services,
                created_by=created_by,
                created_at=datetime.now(UTC).isoformat(),
                is_active=True
            )

            self.maintenance_schedules[schedule_id] = schedule

            logger.info(f"Created maintenance schedule: {title}", schedule_id=schedule_id)
            return schedule

        except Exception as e:
            logger.error("Failed to create maintenance schedule", error=str(e))
            raise

    async def get_maintenance_schedules(
        self,
        active_only: bool = True
    ) -> list[MaintenanceSchedule]:
        """Get maintenance schedules."""
        try:
            schedules = list(self.maintenance_schedules.values())

            if active_only:
                schedules = [s for s in schedules if s.is_active]

            # Sort by start time
            schedules.sort(key=lambda x: x.start_time)

            return schedules

        except Exception as e:
            logger.error("Failed to get maintenance schedules", error=str(e))
            raise

    async def update_maintenance_mode(self, mode: MaintenanceMode) -> bool:
        """Update system maintenance mode."""
        try:
            self._current_maintenance_mode = mode

            logger.info(f"Maintenance mode updated to: {mode.value}")
            return True

        except Exception as e:
            logger.error("Failed to update maintenance mode", error=str(e))
            raise

    async def get_current_maintenance_mode(self) -> MaintenanceMode:
        """Get current maintenance mode."""
        return self._current_maintenance_mode

    async def get_admin_users(self, active_only: bool = True) -> list[AdminUser]:
        """Get list of administrative users."""
        try:
            users = list(self.admin_users.values())

            if active_only:
                users = [u for u in users if u.is_active]

            return users

        except Exception as e:
            logger.error("Failed to get admin users", error=str(e))
            raise

    async def create_admin_user(
        self,
        username: str,
        email: str,
        role: UserRole,
        permissions: list[str],
        created_by: str
    ) -> AdminUser:
        """Create a new administrative user."""
        try:
            # Check if user already exists
            for user in self.admin_users.values():
                if user.username == username or user.email == email:
                    raise ValueError("User with this username or email already exists")

            user_id = f"admin_{uuid.uuid4().hex[:8]}"

            user = AdminUser(
                id=user_id,
                username=username,
                email=email,
                role=role,
                is_active=True,
                last_login=None,
                created_at=datetime.now(UTC).isoformat(),
                permissions=permissions
            )

            self.admin_users[user_id] = user

            # Log the action
            await self.log_admin_action(
                user_id=created_by,
                action="admin_user_created",
                resource_type="admin_user",
                resource_id=user_id,
                details={
                    "username": username,
                    "email": email,
                    "role": role.value
                },
                ip_address="system",
                user_agent="admin_panel"
            )

            logger.info(f"Created admin user: {username}", user_id=user_id)
            return user

        except Exception as e:
            logger.error("Failed to create admin user", error=str(e))
            raise

    async def update_admin_user(
        self,
        user_id: str,
        **updates
    ) -> AdminUser:
        """Update an administrative user."""
        try:
            user = self.admin_users.get(user_id)
            if not user:
                raise ValueError("Admin user not found")

            # Update allowed fields
            updatable_fields = [
                'username', 'email', 'role', 'is_active', 'permissions'
            ]

            for field in updatable_fields:
                if field in updates:
                    setattr(user, field, updates[field])

            logger.info(f"Updated admin user: {user.username}", user_id=user_id)
            return user

        except Exception as e:
            logger.error("Failed to update admin user", error=str(e), user_id=user_id)
            raise

    async def get_system_statistics(self) -> dict[str, Any]:
        """Get comprehensive system statistics."""
        try:
            # Get various system metrics
            metrics = await self.get_system_metrics()
            health = await self.get_system_health()
            users = await self.get_admin_users()
            logs = await self.get_audit_logs(limit=10)
            maintenance = await self.get_maintenance_schedules()

            stats = {
                "system_metrics": metrics.__dict__,
                "system_health": health.__dict__,
                "administrative": {
                    "total_admins": len(users),
                    "active_admins": len([u for u in users if u.is_active]),
                    "roles_distribution": self._get_roles_distribution()
                },
                "activity": {
                    "recent_actions": len(logs),
                    "actions_today": len([log for log in logs if "T" in log.timestamp and log.timestamp.split("T")[0] == datetime.now(UTC).strftime("%Y-%m-%d")]),
                    "unique_users_today": len(set(log.user_id for log in logs if "T" in log.timestamp and log.timestamp.split("T")[0] == datetime.now(UTC).strftime("%Y-%m-%d")))
                },
                "maintenance": {
                    "active_schedules": len([s for s in maintenance if s.is_active]),
                    "current_mode": (await self.get_current_maintenance_mode()).value
                }
            }

            return stats

        except Exception as e:
            logger.error("Failed to get system statistics", error=str(e))
            raise

    async def perform_system_backup(self, backup_type: str = "full") -> dict[str, Any]:
        """Perform system backup operation."""
        try:
            backup_id = f"backup_{uuid.uuid4().hex[:8]}"
            start_time = datetime.now(UTC)

            # Simulate backup process
            # In real implementation, this would trigger actual backup procedures

            end_time = datetime.now(UTC)
            duration = (end_time - start_time).total_seconds()

            backup_info = {
                "backup_id": backup_id,
                "type": backup_type,
                "status": "completed",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "size_bytes": 1024 * 1024 * 150,  # 150 MB simulated
                "files_count": 1250
            }

            # Log the backup action
            await self.log_admin_action(
                user_id="system",
                action="backup_performed",
                resource_type="system",
                resource_id=backup_id,
                details=backup_info,
                ip_address="localhost",
                user_agent="backup_service"
            )

            logger.info(f"System backup completed: {backup_type}", backup_id=backup_id)
            return backup_info

        except Exception as e:
            logger.error("Failed to perform system backup", error=str(e))
            raise

    async def restart_service(self, service_name: str) -> bool:
        """Restart a system service."""
        try:
            # Simulate service restart
            # In real implementation, this would interact with service management

            logger.info(f"Restarting service: {service_name}")

            # Log the restart action
            await self.log_admin_action(
                user_id="system",
                action="service_restarted",
                resource_type="service",
                resource_id=service_name,
                details={"service": service_name},
                ip_address="localhost",
                user_agent="admin_panel"
            )

            return True

        except Exception as e:
            logger.error("Failed to restart service", error=str(e), service_name=service_name)
            raise

    # Private helper methods
    def _get_roles_distribution(self) -> dict[str, int]:
        """Get distribution of admin roles."""
        roles_count = {}
        for user in self.admin_users.values():
            role = user.role.value
            roles_count[role] = roles_count.get(role, 0) + 1
        return roles_count


# Global service instance
admin_panel_service = AdminPanelService()
