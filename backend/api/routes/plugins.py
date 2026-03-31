"""
Plugin Architecture API Routes

Provides REST endpoints for plugin management including discovery, loading,
configuration, and lifecycle management.
"""

from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.services.plugin_service import (
    HookType,
    PluginStatus,
    PluginType,
    plugin_manager,
)

router = APIRouter(prefix="/plugins", tags=["Plugin Architecture"])
logger = get_logger(__name__)


class PluginConfig(BaseModel):
    """Plugin configuration update request model."""
    config: dict[str, Any]


class PluginAction(BaseModel):
    """Plugin action request model."""
    action: str
    parameters: dict[str, Any] | None = None


@router.get("/discover", response_model=APIResponse)
async def discover_plugins():
    """
    Discover available plugins in the system.

    Returns:
        APIResponse with list of discovered plugins
    """
    try:
        manifests = await plugin_manager.discover_plugins()
        manifests_data = [manifest.__dict__ for manifest in manifests]

        return APIResponse(
            success=True,
            data=manifests_data,
            message=f"Discovered {len(manifests_data)} plugins"
        )
    except Exception as e:
        logger.error("Failed to discover plugins", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to discover plugins: {str(e)}")


@router.post("/{plugin_id}/load", response_model=APIResponse)
async def load_plugin(plugin_id: str, config: PluginConfig | None = None):
    """
    Load and initialize a plugin.

    Args:
        plugin_id: ID of the plugin to load
        config: Optional plugin configuration

    Returns:
        APIResponse with loaded plugin information
    """
    try:
        plugin_config = config.config if config else {}
        plugin_instance = await plugin_manager.load_plugin(plugin_id, plugin_config)

        plugin_dict = plugin_instance.__dict__.copy()
        plugin_dict["manifest"] = plugin_instance.manifest.__dict__
        plugin_dict.pop("module", None)  # Don't expose the module object

        return APIResponse(
            success=True,
            data=plugin_dict,
            message=f"Plugin '{plugin_id}' loaded successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to load plugin", error=str(e), plugin_id=plugin_id)
        raise HTTPException(status_code=500, detail=f"Failed to load plugin: {str(e)}")


@router.post("/{plugin_id}/unload", response_model=APIResponse)
async def unload_plugin(plugin_id: str):
    """
    Unload a plugin and clean up resources.

    Args:
        plugin_id: ID of the plugin to unload

    Returns:
        APIResponse confirming unload
    """
    try:
        success = await plugin_manager.unload_plugin(plugin_id)

        if success:
            return APIResponse(
                success=True,
                message=f"Plugin '{plugin_id}' unloaded successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Plugin not found or not loaded")

    except Exception as e:
        logger.error("Failed to unload plugin", error=str(e), plugin_id=plugin_id)
        raise HTTPException(status_code=500, detail=f"Failed to unload plugin: {str(e)}")


@router.get("/", response_model=APIResponse)
async def list_loaded_plugins():
    """
    List all currently loaded plugins.

    Returns:
        APIResponse with list of loaded plugins
    """
    try:
        plugins = await plugin_manager.list_plugins()
        plugins_data = []

        for plugin in plugins:
            plugin_dict = plugin.__dict__.copy()
            plugin_dict["manifest"] = plugin.manifest.__dict__
            plugin_dict.pop("module", None)  # Don't expose the module object
            plugins_data.append(plugin_dict)

        return APIResponse(
            success=True,
            data=plugins_data,
            message=f"Retrieved {len(plugins_data)} loaded plugins"
        )
    except Exception as e:
        logger.error("Failed to list plugins", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list plugins: {str(e)}")


@router.get("/{plugin_id}", response_model=APIResponse)
async def get_plugin(plugin_id: str):
    """
    Get information about a specific plugin.

    Args:
        plugin_id: ID of the plugin

    Returns:
        APIResponse with plugin information
    """
    try:
        plugin = await plugin_manager.get_plugin(plugin_id)

        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")

        plugin_dict = plugin.__dict__.copy()
        plugin_dict["manifest"] = plugin.manifest.__dict__
        plugin_dict.pop("module", None)  # Don't expose the module object

        return APIResponse(
            success=True,
            data=plugin_dict,
            message=f"Retrieved plugin '{plugin_id}'"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get plugin", error=str(e), plugin_id=plugin_id)
        raise HTTPException(status_code=500, detail=f"Failed to get plugin: {str(e)}")


@router.put("/{plugin_id}/config", response_model=APIResponse)
async def update_plugin_config(plugin_id: str, config: PluginConfig):
    """
    Update plugin configuration.

    Args:
        plugin_id: ID of the plugin
        config: New configuration

    Returns:
        APIResponse confirming update
    """
    try:
        plugin = await plugin_manager.get_plugin(plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")

        # For simplicity, we'll just reload the plugin with new config
        # In a real implementation, you'd want more sophisticated config management
        await plugin_manager.unload_plugin(plugin_id)
        updated_plugin = await plugin_manager.load_plugin(plugin_id, config.config)

        plugin_dict = updated_plugin.__dict__.copy()
        plugin_dict["manifest"] = updated_plugin.manifest.__dict__
        plugin_dict.pop("module", None)

        return APIResponse(
            success=True,
            data=plugin_dict,
            message=f"Configuration updated for plugin '{plugin_id}'"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update plugin config", error=str(e), plugin_id=plugin_id)
        raise HTTPException(status_code=500, detail=f"Failed to update plugin config: {str(e)}")


@router.post("/{plugin_id}/execute", response_model=APIResponse)
async def execute_plugin_action(plugin_id: str, action: PluginAction):
    """
    Execute a custom action on a plugin.

    Args:
        plugin_id: ID of the plugin
        action: Action to execute

    Returns:
        APIResponse with action result
    """
    try:
        plugin = await plugin_manager.get_plugin(plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")

        if plugin.status != PluginStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Plugin is not active")

        # Check if plugin has custom execute function
        if not hasattr(plugin.module, 'execute'):
            raise HTTPException(status_code=400, detail="Plugin does not support custom execution")

        execute_func = plugin.module.execute
        result = execute_func(action.action, action.parameters or {})

        return APIResponse(
            success=True,
            data={
                "plugin_id": plugin_id,
                "action": action.action,
                "result": result
            },
            message=f"Executed action '{action.action}' on plugin '{plugin_id}'"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to execute plugin action", error=str(e), plugin_id=plugin_id)
        raise HTTPException(status_code=500, detail=f"Failed to execute plugin action: {str(e)}")


@router.post("/hooks/{hook_type}/execute", response_model=APIResponse)
async def execute_hook(hook_type: str, payload: dict[str, Any] | None = None):
    """
    Execute a system hook across all subscribed plugins.

    Args:
        hook_type: Type of hook to execute
        payload: Optional payload data

    Returns:
        APIResponse with hook execution results
    """
    try:
        hook_enum = HookType(hook_type)
        results = await plugin_manager.execute_hook(hook_enum, payload or {})

        return APIResponse(
            success=True,
            data={
                "hook_type": hook_type,
                "executions": results,
                "total_executions": len(results)
            },
            message=f"Executed hook '{hook_type}' on {len(results)} plugins"
        )
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid hook type: {hook_type}")
    except Exception as e:
        logger.error("Failed to execute hook", error=str(e), hook_type=hook_type)
        raise HTTPException(status_code=500, detail=f"Failed to execute hook: {str(e)}")


@router.get("/hooks/types", response_model=APIResponse)
async def get_hook_types():
    """
    Get list of available hook types.

    Returns:
        APIResponse with list of hook types
    """
    try:
        hook_types = [{"name": hook.name, "value": hook.value} for hook in HookType]

        return APIResponse(
            success=True,
            data=hook_types,
            message="Retrieved available hook types"
        )
    except Exception as e:
        logger.error("Failed to get hook types", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get hook types: {str(e)}")


@router.get("/types", response_model=APIResponse)
async def get_plugin_types():
    """
    Get list of available plugin types.

    Returns:
        APIResponse with list of plugin types
    """
    try:
        plugin_types = [{"name": pt.name, "value": pt.value} for pt in PluginType]

        return APIResponse(
            success=True,
            data=plugin_types,
            message="Retrieved available plugin types"
        )
    except Exception as e:
        logger.error("Failed to get plugin types", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get plugin types: {str(e)}")


@router.get("/stats", response_model=APIResponse)
async def get_plugin_statistics():
    """
    Get plugin system statistics.

    Returns:
        APIResponse with plugin statistics
    """
    try:
        stats = await plugin_manager.get_plugin_stats()

        return APIResponse(
            success=True,
            data=stats,
            message="Retrieved plugin system statistics"
        )
    except Exception as e:
        logger.error("Failed to get plugin stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get plugin stats: {str(e)}")


@router.post("/install", response_model=APIResponse)
async def install_plugin(file: UploadFile = File(...)):
    """
    Install a plugin from an uploaded package file.

    Args:
        file: Plugin package file (ZIP, tar, etc.)

    Returns:
        APIResponse with installed plugin information
    """
    try:
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            temp_path = temp_file.name
            content = await file.read()
            temp_file.write(content)

        # Install plugin from package
        manifest = await plugin_manager.install_plugin_from_package(temp_path)

        # Clean up temporary file
        import os
        os.unlink(temp_path)

        return APIResponse(
            success=True,
            data=manifest.__dict__,
            message=f"Plugin '{manifest.name}' installed successfully"
        )
    except Exception as e:
        logger.error("Failed to install plugin", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to install plugin: {str(e)}")


@router.post("/sandbox/{enabled}", response_model=APIResponse)
async def toggle_sandbox(enabled: bool):
    """
    Enable or disable plugin sandboxing.

    Args:
        enabled: Whether to enable sandboxing

    Returns:
        APIResponse confirming sandbox state
    """
    try:
        plugin_manager.enable_sandbox(enabled)

        return APIResponse(
            success=True,
            message=f"Plugin sandbox {'enabled' if enabled else 'disabled'}"
        )
    except Exception as e:
        logger.error("Failed to toggle sandbox", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to toggle sandbox: {str(e)}")


@router.get("/events/recent", response_model=APIResponse)
async def get_recent_events(limit: int = 50):
    """
    Get recent plugin events and hook executions.

    Args:
        limit: Maximum number of events to return

    Returns:
        APIResponse with recent events
    """
    try:
        # Get recent events from plugin manager
        # This would need to be exposed in the plugin manager
        events = getattr(plugin_manager, 'events', [])[-limit:]
        events_data = []

        for event in events:
            event_dict = event.__dict__.copy()
            events_data.append(event_dict)

        return APIResponse(
            success=True,
            data=events_data,
            message=f"Retrieved {len(events_data)} recent events"
        )
    except Exception as e:
        logger.error("Failed to get recent events", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get recent events: {str(e)}")


@router.delete("/{plugin_id}", response_model=APIResponse)
async def delete_plugin(plugin_id: str):
    """
    Delete a plugin entirely from the system.

    Args:
        plugin_id: ID of the plugin to delete

    Returns:
        APIResponse confirming deletion
    """
    try:
        # First unload if loaded
        await plugin_manager.unload_plugin(plugin_id)

        # Remove plugin directory
        import shutil
        plugin_dir = plugin_manager.plugins_directory / plugin_id
        if plugin_dir.exists():
            shutil.rmtree(plugin_dir)

        return APIResponse(
            success=True,
            message=f"Plugin '{plugin_id}' deleted successfully"
        )
    except Exception as e:
        logger.error("Failed to delete plugin", error=str(e), plugin_id=plugin_id)
        raise HTTPException(status_code=500, detail=f"Failed to delete plugin: {str(e)}")
