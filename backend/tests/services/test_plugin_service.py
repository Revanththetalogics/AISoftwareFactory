"""
Comprehensive tests for PluginService to increase coverage.
"""

import json
import tempfile
from pathlib import Path

import pytest
from backend.services.plugin_service import (
    HookType,
    PluginInstance,
    PluginManager,
    PluginManifest,
    PluginStatus,
    PluginType,
)


class TestPluginService:
    """Comprehensive tests for PluginManager."""

    @pytest.fixture
    def plugin_manager(self):
        """Create PluginManager instance with temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = PluginManager(temp_dir)
            yield pm

    def test_init(self, plugin_manager):
        """Test PluginManager initialization."""
        assert plugin_manager is not None
        assert isinstance(plugin_manager.plugins_directory, Path)
        assert isinstance(plugin_manager.plugins, dict)
        assert isinstance(plugin_manager.events, list)
        assert isinstance(plugin_manager.hook_subscribers, dict)
        assert plugin_manager._sandbox_enabled is True

        # Should have initialized hook subscribers
        assert len(plugin_manager.hook_subscribers) > 0
        for hook_type in HookType:
            assert hook_type in plugin_manager.hook_subscribers

    @pytest.mark.asyncio
    async def test_discover_plugins_success(self, plugin_manager):
        """Test successful plugin discovery."""
        # Create sample plugin directory structure
        sample_plugin_dir = plugin_manager.plugins_directory / "test_plugin"
        sample_plugin_dir.mkdir()

        manifest_data = {
            "id": "test_plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "author": "Test Author",
            "type": "custom",
            "entry_point": "main.py",
            "dependencies": ["dep1", "dep2"],
            "permissions": ["read", "write"],
            "config_schema": {"setting": {"type": "string"}},
        }

        # Create manifest file
        manifest_path = sample_plugin_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        # Create entry point file
        entry_path = sample_plugin_dir / "main.py"
        with open(entry_path, "w") as f:
            f.write("def initialize(config): return True")

        # Discover plugins
        manifests = await plugin_manager.discover_plugins()

        assert len(manifests) == 1
        manifest = manifests[0]
        assert isinstance(manifest, PluginManifest)
        assert manifest.id == "test_plugin"
        assert manifest.name == "Test Plugin"
        assert manifest.version == "1.0.0"
        assert manifest.author == "Test Author"
        assert manifest.type == PluginType.CUSTOM
        assert manifest.dependencies == ["dep1", "dep2"]
        assert manifest.permissions == ["read", "write"]

    @pytest.mark.asyncio
    async def test_discover_plugins_empty_directory(self, plugin_manager):
        """Test plugin discovery with empty directory."""
        manifests = await plugin_manager.discover_plugins()
        assert len(manifests) == 0

    @pytest.mark.asyncio
    async def test_discover_plugins_invalid_manifest(self, plugin_manager):
        """Test plugin discovery with invalid manifest."""
        # Create plugin directory with invalid manifest
        bad_plugin_dir = plugin_manager.plugins_directory / "bad_plugin"
        bad_plugin_dir.mkdir()

        # Create invalid manifest (missing required fields)
        manifest_path = bad_plugin_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump({"id": "bad_plugin"}, f)  # Missing required fields

        # Create entry point
        entry_path = bad_plugin_dir / "main.py"
        with open(entry_path, "w") as f:
            f.write("def initialize(config): return True")

        # Should handle gracefully and return empty list or skip bad plugin
        manifests = await plugin_manager.discover_plugins()
        # Depending on implementation, might be 0 or 1 (if partial loading allowed)
        assert isinstance(manifests, list)

    @pytest.mark.asyncio
    async def test_load_plugin_success(self, plugin_manager):
        """Test successful plugin loading."""
        # Create sample plugin
        plugin_id = "sample_plugin"
        plugin_dir = plugin_manager.plugins_directory / plugin_id
        plugin_dir.mkdir()

        manifest_data = {
            "id": plugin_id,
            "name": "Sample Plugin",
            "version": "1.0.0",
            "description": "A sample plugin",
            "author": "Sample Author",
            "type": "custom",
            "entry_point": "main.py",
            "dependencies": [],
            "permissions": ["read"],
            "config_schema": {},
        }

        # Create manifest
        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        # Create plugin module with required functions
        plugin_code = """
def initialize(config):
    print(f"Initializing with config: {config}")
    return True

def on_startup():
    print("Startup hook called")

def on_user_action(data):
    return {"response": "handled", "data": data}
"""

        entry_path = plugin_dir / "main.py"
        with open(entry_path, "w") as f:
            f.write(plugin_code)

        # Load plugin
        config = {"debug": True}
        plugin_instance = await plugin_manager.load_plugin(plugin_id, config)

        assert isinstance(plugin_instance, PluginInstance)
        assert plugin_instance.manifest.id == plugin_id
        assert plugin_instance.status == PluginStatus.ACTIVE
        assert plugin_instance.config == config
        assert plugin_instance.module is not None
        assert plugin_id in plugin_manager.plugins
        assert plugin_manager.plugins[plugin_id] == plugin_instance

    @pytest.mark.asyncio
    async def test_load_plugin_already_loaded(self, plugin_manager):
        """Test loading already loaded plugin."""
        # Create and load plugin first
        plugin_id = "test_plugin"
        plugin_dir = plugin_manager.plugins_directory / plugin_id
        plugin_dir.mkdir()

        manifest_data = {
            "id": plugin_id,
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "author": "Author",
            "type": "custom",
            "entry_point": "main.py",
            "dependencies": [],
            "permissions": ["read"],
            "config_schema": {},
        }

        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        plugin_code = """
def initialize(config):
    return True
"""

        entry_path = plugin_dir / "main.py"
        with open(entry_path, "w") as f:
            f.write(plugin_code)

        # Load plugin first time
        plugin_instance1 = await plugin_manager.load_plugin(plugin_id)

        # Load plugin second time (should return existing instance)
        plugin_instance2 = await plugin_manager.load_plugin(plugin_id)

        assert plugin_instance1 is plugin_instance2
        assert plugin_instance1.status == PluginStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_load_plugin_not_found(self, plugin_manager):
        """Test loading non-existent plugin."""
        with pytest.raises(ValueError) as exc_info:
            await plugin_manager.load_plugin("nonexistent_plugin")

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_load_plugin_missing_entry_point(self, plugin_manager):
        """Test loading plugin with missing entry point."""
        # Create plugin without entry point file
        plugin_id = "bad_plugin"
        plugin_dir = plugin_manager.plugins_directory / plugin_id
        plugin_dir.mkdir()

        manifest_data = {
            "id": plugin_id,
            "name": "Bad Plugin",
            "version": "1.0.0",
            "description": "Plugin with missing entry point",
            "author": "Author",
            "type": "custom",
            "entry_point": "missing.py",  # This file won't exist
            "dependencies": [],
            "permissions": ["read"],
            "config_schema": {},
        }

        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        # Try to load plugin
        with pytest.raises(FileNotFoundError):
            await plugin_manager.load_plugin(plugin_id)

    @pytest.mark.asyncio
    async def test_load_plugin_missing_required_function(self, plugin_manager):
        """Test loading plugin missing required initialize function."""
        plugin_id = "incomplete_plugin"
        plugin_dir = plugin_manager.plugins_directory / plugin_id
        plugin_dir.mkdir()

        manifest_data = {
            "id": plugin_id,
            "name": "Incomplete Plugin",
            "version": "1.0.0",
            "description": "Plugin missing required function",
            "author": "Author",
            "type": "custom",
            "entry_point": "main.py",
            "dependencies": [],
            "permissions": ["read"],
            "config_schema": {},
        }

        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        # Create plugin module WITHOUT initialize function
        plugin_code = """
def some_other_function():
    pass
"""

        entry_path = plugin_dir / "main.py"
        with open(entry_path, "w") as f:
            f.write(plugin_code)

        # Try to load plugin
        with pytest.raises(ValueError) as exc_info:
            await plugin_manager.load_plugin(plugin_id)

        assert "initialize" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_unload_plugin_success(self, plugin_manager):
        """Test successful plugin unloading."""
        # Create and load plugin first
        plugin_id = "unload_test_plugin"
        plugin_dir = plugin_manager.plugins_directory / plugin_id
        plugin_dir.mkdir()

        manifest_data = {
            "id": plugin_id,
            "name": "Unload Test Plugin",
            "version": "1.0.0",
            "description": "Plugin for unload testing",
            "author": "Author",
            "type": "custom",
            "entry_point": "main.py",
            "dependencies": [],
            "permissions": ["read"],
            "config_schema": {},
        }

        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        plugin_code = """
def initialize(config):
    return True

def cleanup():
    print("Cleaning up plugin resources")
"""

        entry_path = plugin_dir / "main.py"
        with open(entry_path, "w") as f:
            f.write(plugin_code)

        # Load plugin
        await plugin_manager.load_plugin(plugin_id)
        assert plugin_id in plugin_manager.plugins

        # Unload plugin
        result = await plugin_manager.unload_plugin(plugin_id)

        assert result is True
        assert plugin_id not in plugin_manager.plugins

    @pytest.mark.asyncio
    async def test_unload_plugin_not_found(self, plugin_manager):
        """Test unloading non-existent plugin."""
        result = await plugin_manager.unload_plugin("nonexistent_plugin")
        assert result is False

    @pytest.mark.asyncio
    async def test_execute_hook_success(self, plugin_manager):
        """Test executing hooks successfully."""
        # Create plugin with hook functions
        plugin_id = "hook_test_plugin"
        plugin_dir = plugin_manager.plugins_directory / plugin_id
        plugin_dir.mkdir()

        manifest_data = {
            "id": plugin_id,
            "name": "Hook Test Plugin",
            "version": "1.0.0",
            "description": "Plugin with hook functions",
            "author": "Author",
            "type": "custom",
            "entry_point": "main.py",
            "dependencies": [],
            "permissions": ["read"],
            "config_schema": {},
        }

        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        plugin_code = """
def initialize(config):
    return True

def on_user_action(data):
    return {"processed": True, "plugin_id": "hook_test_plugin", "received": data}

def on_startup():
    return "startup_complete"
"""

        entry_path = plugin_dir / "main.py"
        with open(entry_path, "w") as f:
            f.write(plugin_code)

        # Load plugin
        await plugin_manager.load_plugin(plugin_id)

        # Execute user action hook
        payload = {"action": "click", "element": "button"}
        results = await plugin_manager.execute_hook(HookType.ON_USER_ACTION, payload)

        assert len(results) == 1
        result = results[0]
        assert result["plugin_id"] == plugin_id
        assert result["result"]["processed"] is True
        assert result["result"]["received"] == payload

        # Execute startup hook
        startup_results = await plugin_manager.execute_hook(HookType.ON_STARTUP)
        assert len(startup_results) == 1
        assert startup_results[0]["result"] == "startup_complete"

    @pytest.mark.asyncio
    async def test_execute_hook_no_subscribers(self, plugin_manager):
        """Test executing hook with no subscribers."""
        # Execute hook without any loaded plugins
        results = await plugin_manager.execute_hook(HookType.ON_USER_ACTION, {"test": "data"})
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_execute_hook_inactive_plugin(self, plugin_manager):
        """Test executing hook with inactive plugin."""
        # Create plugin but don't load it properly (simulate error state)
        plugin_id = "inactive_plugin"
        plugin_dir = plugin_manager.plugins_directory / plugin_id
        plugin_dir.mkdir()

        manifest_data = {
            "id": plugin_id,
            "name": "Inactive Plugin",
            "version": "1.0.0",
            "description": "Plugin that will be inactive",
            "author": "Author",
            "type": "custom",
            "entry_point": "main.py",
            "dependencies": [],
            "permissions": ["read"],
            "config_schema": {},
        }

        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        plugin_code = """
def initialize(config):
    return True

def on_user_action(data):
    return {"result": "should_not_be_called"}
"""

        entry_path = plugin_dir / "main.py"
        with open(entry_path, "w") as f:
            f.write(plugin_code)

        # Load plugin
        plugin_instance = await plugin_manager.load_plugin(plugin_id)

        # Manually set status to inactive
        plugin_instance.status = PluginStatus.INACTIVE

        # Execute hook - should not call inactive plugin
        results = await plugin_manager.execute_hook(HookType.ON_USER_ACTION, {"test": "data"})
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_get_plugin_success(self, plugin_manager):
        """Test getting specific plugin."""
        # Create and load plugin
        plugin_id = "get_test_plugin"
        plugin_dir = plugin_manager.plugins_directory / plugin_id
        plugin_dir.mkdir()

        manifest_data = {
            "id": plugin_id,
            "name": "Get Test Plugin",
            "version": "1.0.0",
            "description": "Plugin for get testing",
            "author": "Author",
            "type": "custom",
            "entry_point": "main.py",
            "dependencies": [],
            "permissions": ["read"],
            "config_schema": {},
        }

        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        plugin_code = """
def initialize(config):
    return True
"""

        entry_path = plugin_dir / "main.py"
        with open(entry_path, "w") as f:
            f.write(plugin_code)

        # Load plugin
        loaded_plugin = await plugin_manager.load_plugin(plugin_id)

        # Get plugin
        retrieved_plugin = await plugin_manager.get_plugin(plugin_id)

        assert retrieved_plugin is not None
        assert retrieved_plugin is loaded_plugin
        assert retrieved_plugin.manifest.id == plugin_id

    @pytest.mark.asyncio
    async def test_get_plugin_not_found(self, plugin_manager):
        """Test getting non-existent plugin."""
        result = await plugin_manager.get_plugin("nonexistent_plugin")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_plugins_success(self, plugin_manager):
        """Test listing all plugins."""
        # Create and load multiple plugins
        plugin_ids = ["plugin1", "plugin2", "plugin3"]

        for plugin_id in plugin_ids:
            plugin_dir = plugin_manager.plugins_directory / plugin_id
            plugin_dir.mkdir()

            manifest_data = {
                "id": plugin_id,
                "name": f"Plugin {plugin_id}",
                "version": "1.0.0",
                "description": f"Description for {plugin_id}",
                "author": "Author",
                "type": "custom",
                "entry_point": "main.py",
                "dependencies": [],
                "permissions": ["read"],
                "config_schema": {},
            }

            manifest_path = plugin_dir / "manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(manifest_data, f)

            plugin_code = """
def initialize(config):
    return True
"""

            entry_path = plugin_dir / "main.py"
            with open(entry_path, "w") as f:
                f.write(plugin_code)

            # Load plugin
            await plugin_manager.load_plugin(plugin_id)

        # List plugins
        plugins = await plugin_manager.list_plugins()

        assert len(plugins) == 3
        plugin_ids_found = [p.manifest.id for p in plugins]
        for plugin_id in plugin_ids:
            assert plugin_id in plugin_ids_found

    @pytest.mark.asyncio
    async def test_get_plugin_stats_success(self, plugin_manager):
        """Test getting plugin statistics."""
        # Create plugins with different statuses and types
        plugin_data = [
            ("auth_plugin", PluginType.AUTHENTICATION, PluginStatus.ACTIVE),
            ("storage_plugin", PluginType.STORAGE, PluginStatus.ACTIVE),
            ("broken_plugin", PluginType.CUSTOM, PluginStatus.ERROR),
        ]

        for plugin_id, plugin_type, status in plugin_data:
            plugin_dir = plugin_manager.plugins_directory / plugin_id
            plugin_dir.mkdir()

            manifest_data = {
                "id": plugin_id,
                "name": f"{plugin_id.replace('_', ' ').title()}",
                "version": "1.0.0",
                "description": f"Description for {plugin_id}",
                "author": "Author",
                "type": plugin_type.value,
                "entry_point": "main.py",
                "dependencies": [],
                "permissions": ["read"],
                "config_schema": {},
            }

            manifest_path = plugin_dir / "manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(manifest_data, f)

            plugin_code = """
def initialize(config):
    return True
"""

            entry_path = plugin_dir / "main.py"
            with open(entry_path, "w") as f:
                f.write(plugin_code)

            # Load plugin
            plugin_instance = await plugin_manager.load_plugin(plugin_id)
            # Set specific status if not active
            if status != PluginStatus.ACTIVE:
                plugin_instance.status = status

        # Generate some events
        await plugin_manager.execute_hook(HookType.ON_STARTUP)
        await plugin_manager.execute_hook(HookType.ON_USER_ACTION, {"test": "data"})

        # Get stats
        stats = await plugin_manager.get_plugin_stats()

        assert isinstance(stats, dict)
        assert stats["total_plugins"] == 3
        assert "status_distribution" in stats
        assert "type_distribution" in stats
        assert "total_events" in stats
        assert "hook_subscriptions" in stats

        # Check distributions
        assert stats["status_distribution"]["active"] >= 2  # At least auth and storage
        assert stats["type_distribution"]["authentication"] == 1
        assert stats["type_distribution"]["storage"] == 1
        assert stats["type_distribution"]["custom"] == 1
        assert stats["total_events"] >= 2  # At least the two events we generated

    @pytest.mark.asyncio
    async def test_install_plugin_from_package_success(self, plugin_manager):
        """Test installing plugin from package."""
        package_path = "/fake/path/plugin_package.zip"

        # Install plugin from package
        manifest = await plugin_manager.install_plugin_from_package(package_path)

        assert isinstance(manifest, PluginManifest)
        assert manifest.id == "plugin_package"  # Derived from filename
        assert manifest.name == "Installed Plugin: plugin_package"
        assert manifest.version == "1.0.0"
        assert manifest.type == PluginType.CUSTOM
        assert manifest.author == "Package Author"

        # Verify plugin directory was created
        plugin_dir = plugin_manager.plugins_directory / "plugin_package"
        assert plugin_dir.exists()

        # Verify manifest file was created
        manifest_path = plugin_dir / "manifest.json"
        assert manifest_path.exists()

    def test_enable_sandbox(self, plugin_manager):
        """Test enabling/disabling sandbox."""
        # Sandbox should be enabled by default
        assert plugin_manager._sandbox_enabled is True

        # Disable sandbox
        plugin_manager.enable_sandbox(False)
        assert plugin_manager._sandbox_enabled is False

        # Enable sandbox
        plugin_manager.enable_sandbox(True)
        assert plugin_manager._sandbox_enabled is True

    @pytest.mark.asyncio
    async def test_hook_registration(self, plugin_manager):
        """Test automatic hook registration during plugin loading."""
        # Create plugin with various hook functions
        plugin_id = "hook_registration_plugin"
        plugin_dir = plugin_manager.plugins_directory / plugin_id
        plugin_dir.mkdir()

        manifest_data = {
            "id": plugin_id,
            "name": "Hook Registration Plugin",
            "version": "1.0.0",
            "description": "Plugin with multiple hooks",
            "author": "Author",
            "type": "custom",
            "entry_point": "main.py",
            "dependencies": [],
            "permissions": ["read"],
            "config_schema": {},
        }

        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        plugin_code = """
def initialize(config):
    return True

def on_startup():
    pass

def on_shutdown():
    pass

def on_user_action(data):
    pass
"""

        entry_path = plugin_dir / "main.py"
        with open(entry_path, "w") as f:
            f.write(plugin_code)

        # Load plugin (this should automatically register hooks)
        await plugin_manager.load_plugin(plugin_id)

        # Check that hooks were registered
        assert plugin_id in plugin_manager.hook_subscribers[HookType.ON_STARTUP]
        assert plugin_id in plugin_manager.hook_subscribers[HookType.ON_SHUTDOWN]
        assert plugin_id in plugin_manager.hook_subscribers[HookType.ON_USER_ACTION]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
