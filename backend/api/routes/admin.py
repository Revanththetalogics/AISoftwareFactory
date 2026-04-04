"""
Admin Panel API Routes

Provides REST endpoints for administrative functions including system management,
user administration, monitoring, and maintenance operations.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.services.admin_panel_service import MaintenanceMode, UserRole, admin_panel_service

router = APIRouter(prefix="/admin", tags=["Admin Panel"])
logger = get_logger(__name__)


class AdminAuth(BaseModel):
    """Admin authentication request model."""

    username: str
    password: str


class AdminUserCreate(BaseModel):
    """Admin user creation request model."""

    username: str
    email: str
    role: str
    permissions: list[str]


class AdminUserUpdate(BaseModel):
    """Admin user update request model."""

    username: str | None = None
    email: str | None = None
    role: str | None = None
    is_active: bool | None = None
    permissions: list[str] | None = None


class MaintenanceScheduleCreate(BaseModel):
    """Maintenance schedule creation request model."""

    title: str
    description: str
    start_time: str
    end_time: str
    mode: str
    affected_services: list[str]


@router.post("/login", response_model=APIResponse)
async def admin_login(auth_data: AdminAuth):
    """
    Authenticate administrative user.

    Args:
        auth_data: Authentication credentials

    Returns:
        APIResponse with authentication result
    """
    try:
        user = await admin_panel_service.authenticate_admin(auth_data.username, auth_data.password)

        if user:
            user_dict = user.__dict__.copy()
            del user_dict["password"]  # Don't expose password hash

            return APIResponse(
                success=True,
                data={
                    "user": user_dict,
                    "token": "admin_session_token_example",  # In real implementation, return JWT
                    "expires_in": 3600,
                },
                message="Authentication successful",
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    except Exception as e:
        logger.error("Admin login failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.get("/system/metrics", response_model=APIResponse)
async def get_system_metrics():
    """
    Get current system performance metrics.

    Returns:
        APIResponse with system metrics
    """
    try:
        metrics = await admin_panel_service.get_system_metrics()

        return APIResponse(success=True, data=metrics.__dict__, message="Retrieved system metrics")
    except Exception as e:
        logger.error("Failed to get system metrics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")


@router.get("/system/health", response_model=APIResponse)
async def get_system_health():
    """
    Get comprehensive system health status.

    Returns:
        APIResponse with system health information
    """
    try:
        health = await admin_panel_service.get_system_health()

        return APIResponse(success=True, data=health.__dict__, message="Retrieved system health status")
    except Exception as e:
        logger.error("Failed to get system health", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")


@router.get("/system/stats", response_model=APIResponse)
async def get_system_statistics():
    """
    Get comprehensive system statistics.

    Returns:
        APIResponse with system statistics
    """
    try:
        stats = await admin_panel_service.get_system_statistics()

        return APIResponse(success=True, data=stats, message="Retrieved system statistics")
    except Exception as e:
        logger.error("Failed to get system statistics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get system statistics: {str(e)}")


@router.get("/users/", response_model=APIResponse)
async def get_admin_users(active_only: bool = True):
    """
    Get list of administrative users.

    Args:
        active_only: Whether to return only active users

    Returns:
        APIResponse with list of admin users
    """
    try:
        users = await admin_panel_service.get_admin_users(active_only)
        users_data = [user.__dict__ for user in users]

        return APIResponse(success=True, data=users_data, message=f"Retrieved {len(users_data)} admin users")
    except Exception as e:
        logger.error("Failed to get admin users", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get admin users: {str(e)}")


@router.post("/users/", response_model=APIResponse)
async def create_admin_user(user_data: AdminUserCreate):
    """
    Create a new administrative user.

    Args:
        user_data: User creation data

    Returns:
        APIResponse with created user information
    """
    try:
        # For demo purposes, using a fixed creator ID
        created_by = "admin_1"

        user = await admin_panel_service.create_admin_user(
            username=user_data.username,
            email=user_data.email,
            role=UserRole(user_data.role),
            permissions=user_data.permissions,
            created_by=created_by,
        )

        user_dict = user.__dict__.copy()
        del user_dict["password"]  # Don't expose password hash

        return APIResponse(success=True, data=user_dict, message=f"Admin user '{user.username}' created successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create admin user", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create admin user: {str(e)}")


@router.put("/users/{user_id}", response_model=APIResponse)
async def update_admin_user(user_id: str, update_data: AdminUserUpdate):
    """
    Update an administrative user.

    Args:
        user_id: ID of the user to update
        update_data: User update data

    Returns:
        APIResponse with updated user information
    """
    try:
        updates = update_data.dict(exclude_unset=True)
        if "role" in updates:
            updates["role"] = UserRole(updates["role"])

        user = await admin_panel_service.update_admin_user(user_id, **updates)

        user_dict = user.__dict__.copy()
        del user_dict["password"]  # Don't expose password hash

        return APIResponse(success=True, data=user_dict, message=f"Admin user '{user.username}' updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to update admin user", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to update admin user: {str(e)}")


@router.get("/audit/logs/", response_model=APIResponse)
async def get_audit_logs(limit: int = 50, user_id: str | None = None, action: str | None = None):
    """
    Get administrative audit logs.

    Args:
        limit: Maximum number of logs to return
        user_id: Filter by user ID
        action: Filter by action type

    Returns:
        APIResponse with audit logs
    """
    try:
        logs = await admin_panel_service.get_audit_logs(limit, user_id, action)
        logs_data = [log.__dict__ for log in logs]

        return APIResponse(success=True, data=logs_data, message=f"Retrieved {len(logs_data)} audit logs")
    except Exception as e:
        logger.error("Failed to get audit logs", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get audit logs: {str(e)}")


@router.post("/audit/log", response_model=APIResponse)
async def log_admin_action(log_data: dict[str, Any]):
    """
    Manually log an administrative action.

    Args:
        log_data: Audit log data

    Returns:
        APIResponse confirming log entry
    """
    try:
        # For demo purposes, using sample data
        log_entry = await admin_panel_service.log_admin_action(
            user_id=log_data.get("user_id", "admin_1"),
            action=log_data.get("action", "manual_log"),
            resource_type=log_data.get("resource_type", "system"),
            resource_id=log_data.get("resource_id", "unknown"),
            details=log_data.get("details", {}),
            ip_address=log_data.get("ip_address", "127.0.0.1"),
            user_agent=log_data.get("user_agent", "admin_panel"),
        )

        return APIResponse(success=True, data=log_entry.__dict__, message="Action logged successfully")
    except Exception as e:
        logger.error("Failed to log admin action", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to log admin action: {str(e)}")


@router.get("/maintenance/schedules/", response_model=APIResponse)
async def get_maintenance_schedules(active_only: bool = True):
    """
    Get maintenance schedules.

    Args:
        active_only: Whether to return only active schedules

    Returns:
        APIResponse with maintenance schedules
    """
    try:
        schedules = await admin_panel_service.get_maintenance_schedules(active_only)
        schedules_data = [schedule.__dict__ for schedule in schedules]

        return APIResponse(
            success=True, data=schedules_data, message=f"Retrieved {len(schedules_data)} maintenance schedules"
        )
    except Exception as e:
        logger.error("Failed to get maintenance schedules", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get maintenance schedules: {str(e)}")


@router.post("/maintenance/schedules/", response_model=APIResponse)
async def create_maintenance_schedule(schedule_data: MaintenanceScheduleCreate):
    """
    Create a maintenance schedule.

    Args:
        schedule_data: Maintenance schedule data

    Returns:
        APIResponse with created schedule
    """
    try:
        # For demo purposes, using a fixed creator ID
        created_by = "admin_1"

        schedule = await admin_panel_service.create_maintenance_schedule(
            title=schedule_data.title,
            description=schedule_data.description,
            start_time=schedule_data.start_time,
            end_time=schedule_data.end_time,
            mode=MaintenanceMode(schedule_data.mode),
            affected_services=schedule_data.affected_services,
            created_by=created_by,
        )

        return APIResponse(
            success=True,
            data=schedule.__dict__,
            message=f"Maintenance schedule '{schedule.title}' created successfully",
        )
    except Exception as e:
        logger.error("Failed to create maintenance schedule", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create maintenance schedule: {str(e)}")


@router.post("/maintenance/mode/{mode}", response_model=APIResponse)
async def update_maintenance_mode(mode: str):
    """
    Update system maintenance mode.

    Args:
        mode: Maintenance mode to set

    Returns:
        APIResponse confirming mode update
    """
    try:
        maintenance_mode = MaintenanceMode(mode)
        success = await admin_panel_service.update_maintenance_mode(maintenance_mode)

        if success:
            return APIResponse(success=True, message=f"Maintenance mode updated to: {mode}")
        else:
            raise HTTPException(status_code=500, detail="Failed to update maintenance mode")

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid maintenance mode: {mode}")
    except Exception as e:
        logger.error("Failed to update maintenance mode", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to update maintenance mode: {str(e)}")


@router.get("/maintenance/mode", response_model=APIResponse)
async def get_current_maintenance_mode():
    """
    Get current maintenance mode.

    Returns:
        APIResponse with current maintenance mode
    """
    try:
        mode = await admin_panel_service.get_current_maintenance_mode()

        return APIResponse(success=True, data={"mode": mode.value}, message="Retrieved current maintenance mode")
    except Exception as e:
        logger.error("Failed to get maintenance mode", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get maintenance mode: {str(e)}")


@router.post("/system/backup", response_model=APIResponse)
async def perform_system_backup(backup_type: str = "full"):
    """
    Perform system backup.

    Args:
        backup_type: Type of backup to perform

    Returns:
        APIResponse with backup information
    """
    try:
        backup_info = await admin_panel_service.perform_system_backup(backup_type)

        return APIResponse(
            success=True, data=backup_info, message=f"System backup '{backup_type}' completed successfully"
        )
    except Exception as e:
        logger.error("Failed to perform system backup", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to perform system backup: {str(e)}")


@router.post("/services/{service_name}/restart", response_model=APIResponse)
async def restart_service(service_name: str):
    """
    Restart a system service.

    Args:
        service_name: Name of the service to restart

    Returns:
        APIResponse confirming restart
    """
    try:
        success = await admin_panel_service.restart_service(service_name)

        if success:
            return APIResponse(success=True, message=f"Service '{service_name}' restarted successfully")
        else:
            raise HTTPException(status_code=500, detail="Failed to restart service")

    except Exception as e:
        logger.error("Failed to restart service", error=str(e), service_name=service_name)
        raise HTTPException(status_code=500, detail=f"Failed to restart service: {str(e)}")


@router.get("/dashboard", response_model=APIResponse)
async def get_admin_dashboard():
    """
    Get comprehensive admin dashboard data.

    Returns:
        APIResponse with dashboard information
    """
    try:
        # Get all relevant data for dashboard
        metrics = await admin_panel_service.get_system_metrics()
        health = await admin_panel_service.get_system_health()
        users = await admin_panel_service.get_admin_users()
        logs = await admin_panel_service.get_audit_logs(limit=10)
        schedules = await admin_panel_service.get_maintenance_schedules()
        mode = await admin_panel_service.get_current_maintenance_mode()

        dashboard_data = {
            "system_status": {"metrics": metrics.__dict__, "health": health.__dict__, "maintenance_mode": mode.value},
            "administrative": {
                "total_users": len(users),
                "active_users": len([u for u in users if u.is_active]),
                "recent_logs": [log.__dict__ for log in logs],
            },
            "maintenance": {
                "active_schedules": len([s for s in schedules if s.is_active]),
                "upcoming_schedules": [s.__dict__ for s in schedules[:3]],
            },
        }

        return APIResponse(success=True, data=dashboard_data, message="Retrieved admin dashboard data")
    except Exception as e:
        logger.error("Failed to get admin dashboard", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get admin dashboard: {str(e)}")


@router.get("/roles", response_model=APIResponse)
async def get_available_roles():
    """
    Get list of available user roles.

    Returns:
        APIResponse with role information
    """
    try:
        roles = [{"name": role.name, "value": role.value} for role in UserRole]

        return APIResponse(success=True, data=roles, message="Retrieved available roles")
    except Exception as e:
        logger.error("Failed to get roles", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get roles: {str(e)}")


@router.get("/permissions", response_model=APIResponse)
async def get_available_permissions():
    """
    Get list of available permissions.

    Returns:
        APIResponse with permission information
    """
    try:
        permissions = [
            {"name": "manage_users", "description": "Manage user accounts and permissions"},
            {"name": "manage_system", "description": "Configure system settings and parameters"},
            {"name": "view_logs", "description": "View system and audit logs"},
            {"name": "configure_settings", "description": "Modify application configuration"},
            {"name": "perform_maintenance", "description": "Execute maintenance operations"},
            {"name": "moderate_content", "description": "Moderate user-generated content"},
            {"name": "access_reports", "description": "Access system reports and analytics"},
            {"name": "manage_security", "description": "Configure security settings"},
        ]

        return APIResponse(success=True, data=permissions, message="Retrieved available permissions")
    except Exception as e:
        logger.error("Failed to get permissions", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get permissions: {str(e)}")
