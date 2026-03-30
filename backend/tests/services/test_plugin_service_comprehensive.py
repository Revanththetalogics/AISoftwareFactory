"""
Comprehensive tests for PluginManager to increase coverage.
"""

import pytest
import tempfile
import json
import sys
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from pathlib import Path
from datetime import datetime, UTC

from backend.services.plugin_service import (
    PluginManager, PluginType, PluginStatus, HookType,
    PluginManifest, PluginInstance, PluginEvent
)


class TestPluginManager:
    """Comprehensive tests for PluginManager."""

    @pytest.fixture
    def plugin_manager(self):
        """Create PluginManager instance with temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = PluginManager(temp_dir)
            yield manager

    def test_init(self, plugin_manager):
        """Test PluginManager initialization."""
        assert plugin_manager is not None
        assert hasattr(plugin_manager, 'plugins_directory')
        assert isinstance(plugin_manager.plugins_directory, Path)
        assert plugin_manager.plugins_directory.exists()
        assert hasattr(plugin_manager, 'plugins')
        assert isinstance(plugin_manager.plugins, dict)
        assert hasattr(plugin_manager, 'events')
        assert isinstance(plugin_manager.events, list)
        assert hasattr(plugin_manager, 'hook_subscribers')
        assert isinstance(plugin_manager.hook_subscribers, dict)
        assert hasattr(plugin_manager, '_sandbox_enabled')
        
        # Should have sample plugin created
        sample_plugin_dir = plugin_manager.plugins_directory / "sample_plugin"
        assert sample_plugin_dir.exists()
        assert (sample_plugin_dir / "manifest.json").exists()
        assert (sample_plugin_dir / "main.py").exists()

    def test_initialize_plugins_directory_creates_sample(self, plugin_manager):
        """Test that plugins directory initialization creates sample plugin."""
        # Sample plugin should exist
        sample_dir = plugin_manager.plugins_directory / "sample_plugin"
        assert sample_dir.exists()
        
        # Check manifest content
        manifest_path = sample_dir / "manifest.json"
        assert manifest_path.exists()
        
        with open(manifest_path) as f:
            manifest = json.load(f)
            assert manifest["id"] == "sample_plugin"
            assert manifest["name"] == "Sample Plugin"
            assert manifest["type"] == "custom"
            
        # Check main.py exists
        main_path = sample_dir / "main.py"
        assert main_path.exists()

    def test_load_builtin_hooks(self, plugin_manager):
        """Test that built-in hooks are initialized."""
        # All hook types should have empty subscriber lists
        for hook_type in HookType:
            assert hook_type in plugin_manager.hook_subscribers
            assert isinstance(plugin_manager.hook_subscribers[hook_type], list)
            assert len(plugin_manager.hook_subscribers[hook_type]) == 0

    @pytest.mark.asyncio
    async def test_discover_plugins_success(self, plugin_manager):
        """Test discovering plugins successfully."""
        result = await plugin_manager.discover_plugins()
        
        assert isinstance(result, list)
        assert len(result) >= 1  # Should find at least the sample plugin
        
        # Check sample plugin manifest
        sample_manifest = next((m for m in result if m.id == "sample_plugin"), None)
        assert sample_manifest is not None
        assert isinstance(sample_manifest, PluginManifest)
        assert sample_manifest.name == "Sample Plugin"
        assert sample_manifest.type == PluginType.CUSTOM
        assert sample_manifest.entry_point == "main.py"
        assert isinstance(sample_manifest.dependencies, list)
        assert isinstance(sample_manifest.permissions, list)
        assert isinstance(sample_manifest.config_schema, dict)

    @pytest.mark.asyncio
    async def test_discover_plugins_no_additional_plugins(self, plugin_manager):
        """Test discovering plugins in directory with only default sample plugin."""
        # The PluginManager automatically creates a sample plugin during initialization
        # So we test that it discovers at least the sample plugin
        result = await plugin_manager.discover_plugins()
        
        assert isinstance(result, list)
        # Should find at least the sample plugin that's automatically created
        assert len(result) >= 1
        
        # Verify sample plugin is present
        sample_plugin = next((p for p in result if p.id == "sample_plugin"), None)
        assert sample_plugin is not None

    @pytest.mark.asyncio
    async def test_discover_plugins_invalid_manifest(self, plugin_manager):
        """Test discovering plugins with invalid manifest."""
        # Create plugin with invalid manifest
        invalid_plugin_dir = plugin_manager.plugins_directory / "invalid_plugin"
        invalid_plugin_dir.mkdir()
        
        invalid_manifest_path = invalid_plugin_dir / "manifest.json"
        with open(invalid_manifest_path, 'w') as f:
            f.write("invalid json content")
        
        result = await plugin_manager.discover_plugins()
        
        # Should still return valid plugins, ignore invalid ones
        assert isinstance(result, list)
        # Sample plugin should still be discovered
        sample_manifest = next((m for m in result if m.id == "sample_plugin"), None)
        assert sample_manifest is not None

    @pytest.mark.asyncio
    async def test_load_plugin_success(self, plugin_manager):
        """Test loading plugin successfully."""
        with patch('importlib.util.spec_from_file_location') as mock_spec_from_file:
            with patch('importlib.util.module_from_spec') as mock_module_from_spec:
                # Mock the module and its functions
                mock_module = MagicMock()
                mock_module.initialize = MagicMock(return_value=True)
                mock_module.on_startup = MagicMock()
                mock_module.on_user_action = MagicMock(return_value={"response": "handled"})
                
                mock_spec = MagicMock()
                mock_spec.loader = MagicMock()
                mock_spec_from_file.return_value = mock_spec
                mock_module_from_spec.return_value = mock_module
                
                result = await plugin_manager.load_plugin("sample_plugin", {"debug": True})
                
                assert result is not None
                assert isinstance(result, PluginInstance)
                assert result.manifest.id == "sample_plugin"
                assert result.status == PluginStatus.ACTIVE
                assert result.config == {"debug": True}
                assert result.module == mock_module
                assert "sample_plugin" in plugin_manager.plugins
                assert len(result.loaded_at) > 0

    @pytest.mark.asyncio
    async def test_load_plugin_already_loaded(self, plugin_manager):
        """Test loading already loaded plugin."""
        # First load
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec'):
                mock_module = MagicMock()
                mock_module.initialize = MagicMock(return_value=True)
                
                with patch('backend.services.plugin_service.importlib.util.module_from_spec', return_value=mock_module):
                    first_result = await plugin_manager.load_plugin("sample_plugin")
                    
                    # Second load should return the same instance
                    second_result = await plugin_manager.load_plugin("sample_plugin")
                    
                    assert first_result is second_result
                    assert first_result.status == PluginStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_load_plugin_not_found(self, plugin_manager):
        """Test loading non-existent plugin."""
        with pytest.raises(ValueError) as exc_info:
            await plugin_manager.load_plugin("nonexistent_plugin")
        
        assert "Plugin nonexistent_plugin not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_load_plugin_missing_entry_point(self, plugin_manager):
        """Test loading plugin with missing entry point."""
        # Modify sample plugin manifest to have non-existent entry point
        sample_dir = plugin_manager.plugins_directory / "sample_plugin"
        manifest_path = sample_dir / "manifest.json"
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        manifest["entry_point"] = "nonexistent.py"
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f)
        
        with pytest.raises(FileNotFoundError) as exc_info:
            await plugin_manager.load_plugin("sample_plugin")
        
        assert "Entry point nonexistent.py not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_load_plugin_missing_required_function(self, plugin_manager):
        """Test loading plugin missing required functions."""
        with patch('importlib.util.spec_from_file_location') as mock_spec_from_file:
            with patch('importlib.util.module_from_spec') as mock_module_from_spec:
                # Mock module without required initialize function
                mock_module = MagicMock()
                delattr(mock_module, 'initialize')  # Remove initialize function
                
                mock_spec = MagicMock()
                mock_spec.loader = MagicMock()
                mock_spec_from_file.return_value = mock_spec
                mock_module_from_spec.return_value = mock_module
                
                with pytest.raises(ValueError) as exc_info:
                    await plugin_manager.load_plugin("sample_plugin")
                
                assert "Plugin missing required function: initialize" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_load_plugin_initialization_failure(self, plugin_manager):
        """Test loading plugin that fails initialization."""
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec'):
                mock_module = MagicMock()
                mock_module.initialize = MagicMock(return_value=False)  # Fail initialization
                
                with patch('backend.services.plugin_service.importlib.util.module_from_spec', return_value=mock_module):
                    with pytest.raises(RuntimeError) as exc_info:
                        await plugin_manager.load_plugin("sample_plugin")
                    
                    assert "Plugin initialization failed" in str(exc_info.value)
                    
                    # Plugin should be in error state
                    plugin_instance = plugin_manager.plugins.get("sample_plugin")
                    assert plugin_instance is not None
                    assert plugin_instance.status == PluginStatus.ERROR
                    assert plugin_instance.error_message is not None

    @pytest.mark.asyncio
    async def test_unload_plugin_success(self, plugin_manager):
        """Test unloading plugin successfully."""
        # First load a plugin
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec'):
                mock_module = MagicMock()
                mock_module.initialize = MagicMock(return_value=True)
                mock_module.cleanup = MagicMock()
                
                with patch('backend.services.plugin_service.importlib.util.module_from_spec', return_value=mock_module):
                    await plugin_manager.load_plugin("sample_plugin")
                    
                    # Verify it's loaded
                    assert "sample_plugin" in plugin_manager.plugins
                    
                    # Unload it
                    result = await plugin_manager.unload_plugin("sample_plugin")
                    
                    assert result is True
                    assert "sample_plugin" not in plugin_manager.plugins
                    # Cleanup should have been called
                    mock_module.cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_unload_plugin_not_found(self, plugin_manager):
        """Test unloading non-existent plugin."""
        result = await plugin_manager.unload_plugin("nonexistent_plugin")
        assert result is False

    @pytest.mark.asyncio
    async def test_unload_plugin_cleanup_failure(self, plugin_manager):
        """Test unloading plugin when cleanup fails."""
        # Load a plugin
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec'):
                mock_module = MagicMock()
                mock_module.initialize = MagicMock(return_value=True)
                mock_module.cleanup = MagicMock(side_effect=Exception("Cleanup failed"))
                
                with patch('backend.services.plugin_service.importlib.util.module_from_spec', return_value=mock_module):
                    await plugin_manager.load_plugin("sample_plugin")
                    
                    # Unload should still succeed despite cleanup failure
                    result = await plugin_manager.unload_plugin("sample_plugin")
                    
                    assert result is True
                    assert "sample_plugin" not in plugin_manager.plugins

    @pytest.mark.asyncio
    async def test_register_plugin_hooks(self, plugin_manager):
        """Test registering plugin hooks."""
        # Load a plugin first
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec'):
                mock_module = MagicMock()
                mock_module.initialize = MagicMock(return_value=True)
                # Add some hook functions
                mock_module.on_startup = MagicMock()
                mock_module.on_user_action = MagicMock()
                
                with patch('backend.services.plugin_service.importlib.util.module_from_spec', return_value=mock_module):
                    plugin_instance = await plugin_manager.load_plugin("sample_plugin")
                    
                    # Check that hooks were registered
                    assert "sample_plugin" in plugin_manager.hook_subscribers[HookType.ON_STARTUP]
                    assert "sample_plugin" in plugin_manager.hook_subscribers[HookType.ON_USER_ACTION]
                    assert len(plugin_manager.hook_subscribers[HookType.ON_STARTUP]) == 1
                    assert len(plugin_manager.hook_subscribers[HookType.ON_USER_ACTION]) == 1

    @pytest.mark.asyncio
    async def test_execute_hook_success(self, plugin_manager):
        """Test executing hook successfully."""
        # Load a plugin with hook functions
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec'):
                mock_module = MagicMock()
                mock_module.initialize = MagicMock(return_value=True)
                mock_module.on_user_action = MagicMock(return_value={"processed": True})
                
                with patch('backend.services.plugin_service.importlib.util.module_from_spec', return_value=mock_module):
                    await plugin_manager.load_plugin("sample_plugin")
                    
                    # Execute the hook
                    payload = {"action": "test_action", "user_id": "123"}
                    results = await plugin_manager.execute_hook(HookType.ON_USER_ACTION, payload)
                    
                    assert isinstance(results, list)
                    assert len(results) == 1
                    assert results[0]["plugin_id"] == "sample_plugin"
                    assert results[0]["result"] == {"processed": True}
                    assert results[0]["execution_time"] >= 0
                    
                    # Should have created event record
                    assert len(plugin_manager.events) == 1
                    event = plugin_manager.events[0]
                    assert isinstance(event, PluginEvent)
                    assert event.plugin_id == "sample_plugin"
                    assert event.hook_type == HookType.ON_USER_ACTION
                    assert event.payload == payload
                    assert event.result == {"processed": True}

    @pytest.mark.asyncio
    async def test_execute_hook_multiple_plugins(self, plugin_manager):
        """Test executing hook with multiple plugins."""
        # Create second plugin
        second_plugin_dir = plugin_manager.plugins_directory / "second_plugin"
        second_plugin_dir.mkdir()
        
        second_manifest = {
            "id": "second_plugin",
            "name": "Second Plugin",
            "version": "1.0.0",
            "description": "Second test plugin",
            "author": "Test Author",
            "type": "custom",
            "entry_point": "main.py",
            "dependencies": [],
            "permissions": [],
            "config_schema": {}
        }
        
        with open(second_plugin_dir / "manifest.json", 'w') as f:
            json.dump(second_manifest, f)
        
        with open(second_plugin_dir / "main.py", 'w') as f:
            f.write("def initialize(config): return True\ndef on_user_action(data): return {'second': True}")
        
        # Load both plugins
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec'):
                # Mock first plugin
                mock_module1 = MagicMock()
                mock_module1.initialize = MagicMock(return_value=True)
                mock_module1.on_user_action = MagicMock(return_value={"first": True})
                
                # Mock second plugin
                mock_module2 = MagicMock()
                mock_module2.initialize = MagicMock(return_value=True)
                mock_module2.on_user_action = MagicMock(return_value={"second": True})
                
                with patch('backend.services.plugin_service.importlib.util.module_from_spec') as mock_module_factory:
                    # Return different modules for different plugins
                    mock_module_factory.side_effect = [mock_module1, mock_module2, mock_module1, mock_module2]
                    
                    await plugin_manager.load_plugin("sample_plugin")
                    await plugin_manager.load_plugin("second_plugin")
                    
                    # Execute hook
                    results = await plugin_manager.execute_hook(HookType.ON_USER_ACTION)
                    
                    assert len(results) == 2
                    plugin_ids = [r["plugin_id"] for r in results]
                    assert "sample_plugin" in plugin_ids
                    assert "second_plugin" in plugin_ids

    @pytest.mark.asyncio
    async def test_execute_hook_inactive_plugin(self, plugin_manager):
        """Test executing hook with inactive plugin."""
        # Load plugin
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec'):
                mock_module = MagicMock()
                mock_module.initialize = MagicMock(return_value=True)
                mock_module.on_user_action = MagicMock(return_value={"result": "test"})
                
                with patch('backend.services.plugin_service.importlib.util.module_from_spec', return_value=mock_module):
                    plugin_instance = await plugin_manager.load_plugin("sample_plugin")
                    
                    # Set plugin to inactive
                    plugin_instance.status = PluginStatus.INACTIVE
                    
                    # Execute hook - should not execute for inactive plugin
                    results = await plugin_manager.execute_hook(HookType.ON_USER_ACTION)
                    
                    assert len(results) == 0
                    assert len(plugin_manager.events) == 0

    @pytest.mark.asyncio
    async def test_execute_hook_plugin_error(self, plugin_manager):
        """Test executing hook when plugin throws error."""
        # Load plugin
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec'):
                mock_module = MagicMock()
                mock_module.initialize = MagicMock(return_value=True)
                mock_module.on_user_action = MagicMock(side_effect=Exception("Plugin error"))
                
                with patch('backend.services.plugin_service.importlib.util.module_from_spec', return_value=mock_module):
                    await plugin_manager.load_plugin("sample_plugin")
                    
                    # Execute hook - should handle error gracefully
                    results = await plugin_manager.execute_hook(HookType.ON_USER_ACTION)
                    
                    assert len(results) == 0  # No successful results
                    assert len(plugin_manager.events) == 1  # But event should be recorded
                    event = plugin_manager.events[0]
                    assert event.error is not None
                    assert "Plugin error" in event.error

    @pytest.mark.asyncio
    async def test_get_plugin_success(self, plugin_manager):
        """Test getting specific plugin."""
        # Load a plugin
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec'):
                mock_module = MagicMock()
                mock_module.initialize = MagicMock(return_value=True)
                
                with patch('backend.services.plugin_service.importlib.util.module_from_spec', return_value=mock_module):
                    loaded_plugin = await plugin_manager.load_plugin("sample_plugin")
                    
                    # Get the plugin
                    result = await plugin_manager.get_plugin("sample_plugin")
                    
                    assert result is not None
                    assert result is loaded_plugin

    @pytest.mark.asyncio
    async def test_get_plugin_not_found(self, plugin_manager):
        """Test getting non-existent plugin."""
        result = await plugin_manager.get_plugin("nonexistent_plugin")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_plugins(self, plugin_manager):
        """Test listing all plugins."""
        # Initially empty
        result = await plugin_manager.list_plugins()
        assert isinstance(result, list)
        assert len(result) == 0
        
        # Load a plugin
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec'):
                mock_module = MagicMock()
                mock_module.initialize = MagicMock(return_value=True)
                
                with patch('backend.services.plugin_service.importlib.util.module_from_spec', return_value=mock_module):
                    await plugin_manager.load_plugin("sample_plugin")
                    
                    # List plugins
                    result = await plugin_manager.list_plugins()
                    
                    assert isinstance(result, list)
                    assert len(result) == 1
                    assert result[0].manifest.id == "sample_plugin"

    @pytest.mark.asyncio
    async def test_get_plugin_stats(self, plugin_manager):
        """Test getting plugin statistics."""
        # Load plugins of different types and statuses
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec'):
                # Mock successful plugin
                mock_module1 = MagicMock()
                mock_module1.initialize = MagicMock(return_value=True)
                
                # Mock failed plugin
                mock_module2 = MagicMock()
                mock_module2.initialize = MagicMock(return_value=False)
                
                with patch('backend.services.plugin_service.importlib.util.module_from_spec') as mock_module_factory:
                    mock_module_factory.side_effect = [mock_module1, mock_module2, mock_module1]
                    
                    try:
                        await plugin_manager.load_plugin("sample_plugin")
                    except:
                        pass  # Expected to fail
                    
                    # Create second plugin directory manually for discovery
                    second_plugin_dir = plugin_manager.plugins_directory / "storage_plugin"
                    second_plugin_dir.mkdir()
                    second_manifest = {
                        "id": "storage_plugin", "name": "Storage Plugin", "version": "1.0.0",
                        "description": "", "author": "", "type": "storage", "entry_point": "main.py",
                        "dependencies": [], "permissions": [], "config_schema": {}
                    }
                    with open(second_plugin_dir / "manifest.json", 'w') as f:
                        json.dump(second_manifest, f)
                    with open(second_plugin_dir / "main.py", 'w') as f:
                        f.write("def initialize(config): return True")
                    
                    # Load second plugin successfully
                    mock_module_factory.side_effect = [MagicMock(initialize=MagicMock(return_value=True))]
                    await plugin_manager.load_plugin("storage_plugin")
                    
                    # Get stats
                    stats = await plugin_manager.get_plugin_stats()
                    
                    assert isinstance(stats, dict)
                    assert "total_plugins" in stats
                    assert "status_distribution" in stats
                    assert "type_distribution" in stats
                    assert "total_events" in stats
                    assert "hook_subscriptions" in stats
                    assert stats["total_plugins"] >= 1
                    assert isinstance(stats["status_distribution"], dict)
                    assert isinstance(stats["type_distribution"], dict)

    @pytest.mark.asyncio
    async def test_install_plugin_from_package(self, plugin_manager):
        """Test installing plugin from package."""
        # Mock Path object properly
        with patch('pathlib.Path') as mock_path_class:
            mock_path_instance = MagicMock()
            mock_path_instance.stem = "test_package"
            mock_path_class.return_value = mock_path_instance
            
            result = await plugin_manager.install_plugin_from_package("/path/to/test_package.zip")
            
            assert result is not None
            assert isinstance(result, PluginManifest)
            assert result.id == "test_package"
            assert result.name == "Installed Plugin: test_package"
            assert result.type == PluginType.CUSTOM

    def test_enable_sandbox(self, plugin_manager):
        """Test enabling/disabling sandbox."""
        # Initially enabled
        assert plugin_manager._sandbox_enabled is True
        
        # Disable
        plugin_manager.enable_sandbox(False)
        assert plugin_manager._sandbox_enabled is False
        
        # Enable
        plugin_manager.enable_sandbox(True)
        assert plugin_manager._sandbox_enabled is True

    def test_plugin_instance_post_init(self):
        """Test PluginInstance post-initialization."""
        manifest = PluginManifest(
            id="test", name="Test", version="1.0.0", description="Test",
            author="Author", type=PluginType.CUSTOM, entry_point="main.py",
            dependencies=[], permissions=[], config_schema={},
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat()
        )
        
        # Without hooks
        instance = PluginInstance(
            manifest=manifest,
            module=None,
            status=PluginStatus.INACTIVE,
            config={},
            loaded_at=datetime.now(UTC).isoformat()
        )
        assert instance.hooks == {}  # Should initialize empty dict
        
        # With hooks provided
        hooks_dict = {HookType.ON_STARTUP: []}
        instance_with_hooks = PluginInstance(
            manifest=manifest,
            module=None,
            status=PluginStatus.INACTIVE,
            config={},
            loaded_at=datetime.now(UTC).isoformat(),
            hooks=hooks_dict
        )
        assert instance_with_hooks.hooks is hooks_dict

    def test_enum_values(self):
        """Test enum values are correctly defined."""
        # Test PluginType values
        assert PluginType.AUTHENTICATION.value == "authentication"
        assert PluginType.STORAGE.value == "storage"
        assert PluginType.NOTIFICATION.value == "notification"
        
        # Test PluginStatus values
        assert PluginStatus.ACTIVE.value == "active"
        assert PluginStatus.INACTIVE.value == "inactive"
        assert PluginStatus.ERROR.value == "error"
        
        # Test HookType values
        assert HookType.ON_STARTUP.value == "on_startup"
        assert HookType.ON_SHUTDOWN.value == "on_shutdown"
        assert HookType.BEFORE_REQUEST.value == "before_request"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])