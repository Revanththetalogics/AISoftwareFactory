"""
Comprehensive tests for Plugin API routes to improve coverage from 22% to 90%+.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.routes.plugins import router


class TestPluginRoutes:
    """Tests for plugin management API routes."""

    @pytest.fixture
    def app(self):
        """Create test app with plugin router."""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_plugin_manager(self):
        """Mock the plugin manager."""
        with patch("backend.api.routes.plugins.plugin_manager") as mock:
            mock.discover_plugins = AsyncMock()
            mock.load_plugin = AsyncMock()
            mock.unload_plugin = AsyncMock()
            mock.get_loaded_plugins = AsyncMock()
            mock.configure_plugin = AsyncMock()
            mock.execute_plugin_action = AsyncMock()
            mock.get_plugin_status = AsyncMock()
            yield mock

    def test_discover_plugins_success(self, client, mock_plugin_manager):
        """Test successful plugin discovery."""
        # Create mock manifests with proper __dict__ attributes
        mock_manifest1 = MagicMock()
        mock_manifest1.__dict__ = {
            "id": "plugin1",
            "name": "Test Plugin 1",
            "version": "1.0.0",
            "description": "A test plugin",
            "type": "feature",
            "author": "Test Author"
        }
        
        mock_manifest2 = MagicMock()
        mock_manifest2.__dict__ = {
            "id": "plugin2",
            "name": "Test Plugin 2",
            "version": "2.0.0",
            "description": "Another test plugin",
            "type": "integration",
            "author": "Another Author"
        }
        
        mock_manifests = [mock_manifest1, mock_manifest2]
        mock_plugin_manager.discover_plugins.return_value = mock_manifests

        response = client.get("/plugins/discover")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert "discovered 2 plugins" in data["message"].lower()

    def test_discover_plugins_empty(self, client, mock_plugin_manager):
        """Test plugin discovery with no plugins found."""
        mock_plugin_manager.discover_plugins.return_value = []

        response = client.get("/plugins/discover")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 0
        assert "discovered 0 plugins" in data["message"].lower()

    def test_discover_plugins_error(self, client, mock_plugin_manager):
        """Test plugin discovery when error occurs."""
        mock_plugin_manager.discover_plugins.side_effect = Exception("Discovery failed")

        response = client.get("/plugins/discover")

        assert response.status_code == 500
        data = response.json()
        assert "failed to discover plugins" in data["detail"].lower()

    def test_load_plugin_success(self, client, mock_plugin_manager):
        """Test successful plugin loading."""
        mock_plugin = MagicMock()
        mock_plugin.manifest = MagicMock(id="test-plugin", name="Test Plugin")
        mock_plugin.status = "loaded"
        mock_plugin_manager.load_plugin.return_value = mock_plugin

        response = client.post(
            "/plugins/test-plugin/load",
            json={"config": {"setting1": "value1", "setting2": "value2"}}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["manifest"]["id"] == "test-plugin"
        assert "loaded successfully" in data["message"].lower()

    def test_load_plugin_no_config(self, client, mock_plugin_manager):
        """Test plugin loading without configuration."""
        mock_plugin = MagicMock()
        mock_plugin.manifest = MagicMock(id="simple-plugin")
        mock_plugin_manager.load_plugin.return_value = mock_plugin

        response = client.post("/plugins/simple-plugin/load")

        assert response.status_code == 200
        # Should call load_plugin with empty config
        mock_plugin_manager.load_plugin.assert_called_with("simple-plugin", {})

    def test_load_plugin_not_found(self, client, mock_plugin_manager):
        """Test loading non-existent plugin."""
        mock_plugin_manager.load_plugin.side_effect = ValueError("Plugin not found")

        response = client.post("/plugins/nonexistent/load")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_load_plugin_internal_error(self, client, mock_plugin_manager):
        """Test plugin loading when internal error occurs."""
        mock_plugin_manager.load_plugin.side_effect = Exception("Load failed")

        response = client.post("/plugins/error-plugin/load")

        assert response.status_code == 500
        data = response.json()
        assert "failed to load plugin" in data["detail"].lower()

    def test_unload_plugin_success(self, client, mock_plugin_manager):
        """Test successful plugin unloading."""
        mock_plugin_manager.unload_plugin.return_value = True

        response = client.post("/plugins/test-plugin/unload")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "unloaded" in data["message"].lower()

    def test_unload_plugin_not_loaded(self, client, mock_plugin_manager):
        """Test unloading plugin that's not loaded."""
        mock_plugin_manager.unload_plugin.side_effect = ValueError("Plugin not loaded")

        response = client.post("/plugins/not-loaded/unload")

        assert response.status_code == 404
        assert "not loaded" in response.json()["detail"].lower()

    def test_unload_plugin_error(self, client, mock_plugin_manager):
        """Test plugin unloading when error occurs."""
        mock_plugin_manager.unload_plugin.side_effect = Exception("Unload failed")

        response = client.post("/plugins/error-plugin/unload")

        assert response.status_code == 500
        data = response.json()
        assert "failed to unload plugin" in data["detail"].lower()

    def test_get_loaded_plugins(self, client, mock_plugin_manager):
        """Test getting list of loaded plugins."""
        mock_plugins = [
            MagicMock(
                id="plugin1",
                name="Loaded Plugin 1",
                status="active",
                manifest=MagicMock(version="1.0.0")
            ),
            MagicMock(
                id="plugin2",
                name="Loaded Plugin 2", 
                status="inactive",
                manifest=MagicMock(version="2.0.0")
            )
        ]
        mock_plugin_manager.get_loaded_plugins.return_value = mock_plugins

        response = client.get("/plugins/loaded")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["id"] == "plugin1"
        assert data["data"][1]["id"] == "plugin2"

    def test_get_loaded_plugins_empty(self, client, mock_plugin_manager):
        """Test getting loaded plugins when none are loaded."""
        mock_plugin_manager.get_loaded_plugins.return_value = []

        response = client.get("/plugins/loaded")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 0

    def test_configure_plugin_success(self, client, mock_plugin_manager):
        """Test successful plugin configuration."""
        mock_plugin_manager.configure_plugin.return_value = True

        response = client.put(
            "/plugins/test-plugin/configure",
            json={"config": {"timeout": 30, "retries": 3}}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "configured" in data["message"].lower()

    def test_configure_plugin_not_found(self, client, mock_plugin_manager):
        """Test configuring non-existent plugin."""
        mock_plugin_manager.configure_plugin.side_effect = ValueError("Plugin not found")

        response = client.put(
            "/plugins/nonexistent/configure",
            json={"config": {"setting": "value"}}
        )

        assert response.status_code == 404

    def test_execute_plugin_action_success(self, client, mock_plugin_manager):
        """Test successful plugin action execution."""
        mock_result = {"status": "completed", "output": "Action executed successfully"}
        mock_plugin_manager.execute_plugin_action.return_value = mock_result

        response = client.post(
            "/plugins/test-plugin/action",
            json={
                "action": "process_data",
                "parameters": {"input_file": "data.csv", "output_format": "json"}
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] == mock_result

    def test_execute_plugin_action_no_parameters(self, client, mock_plugin_manager):
        """Test plugin action execution without parameters."""
        mock_result = {"status": "completed"}
        mock_plugin_manager.execute_plugin_action.return_value = mock_result

        response = client.post(
            "/plugins/test-plugin/action",
            json={"action": "cleanup"}
        )

        assert response.status_code == 200
        # Should call with None parameters
        mock_plugin_manager.execute_plugin_action.assert_called_with(
            "test-plugin", "cleanup", None
        )

    def test_execute_plugin_action_error(self, client, mock_plugin_manager):
        """Test plugin action execution when error occurs."""
        mock_plugin_manager.execute_plugin_action.side_effect = Exception("Action failed")

        response = client.post(
            "/plugins/error-plugin/action",
            json={"action": "invalid_action"}
        )

        assert response.status_code == 500
        assert "failed to execute action" in response.json()["detail"].lower()

    def test_get_plugin_status(self, client, mock_plugin_manager):
        """Test getting plugin status."""
        mock_status = {
            "id": "test-plugin",
            "name": "Test Plugin",
            "status": "active",
            "version": "1.0.0",
            "loaded_at": "2026-03-29T10:30:00Z",
            "last_action": "process_data"
        }
        mock_plugin_manager.get_plugin_status.return_value = mock_status

        response = client.get("/plugins/test-plugin/status")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] == mock_status

    def test_get_plugin_status_not_found(self, client, mock_plugin_manager):
        """Test getting status of non-existent plugin."""
        mock_plugin_manager.get_plugin_status.side_effect = ValueError("Plugin not found")

        response = client.get("/plugins/nonexistent/status")

        assert response.status_code == 404

    def test_upload_plugin_success(self, client, mock_plugin_manager):
        """Test successful plugin upload."""
        mock_plugin_manager.install_plugin_from_file = AsyncMock()
        mock_plugin_manager.install_plugin_from_file.return_value = {
            "id": "uploaded-plugin",
            "name": "Uploaded Plugin",
            "version": "1.0.0"
        }

        # Create a mock file
        from io import BytesIO
        plugin_file = BytesIO(b"plugin content")
        plugin_file.name = "test-plugin.zip"

        response = client.post(
            "/plugins/upload",
            files={"plugin_file": ("test-plugin.zip", plugin_file, "application/zip")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "installed" in data["message"].lower()

    def test_upload_plugin_invalid_file(self, client):
        """Test plugin upload with invalid file."""
        from io import BytesIO
        invalid_file = BytesIO(b"not a zip file")
        invalid_file.name = "test.txt"

        response = client.post(
            "/plugins/upload",
            files={"plugin_file": ("test.txt", invalid_file, "text/plain")}
        )

        # Should reject non-zip files
        assert response.status_code == 400

    def test_list_plugin_types(self, client):
        """Test listing available plugin types."""
        response = client.get("/plugins/types")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    def test_get_plugin_manifest(self, client, mock_plugin_manager):
        """Test getting plugin manifest."""
        mock_manifest = MagicMock(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="A test plugin",
            type="feature",
            author="Test Author",
            dependencies=[]
        )
        mock_plugin_manager.get_plugin_manifest = AsyncMock(return_value=mock_manifest)

        response = client.get("/plugins/test-plugin/manifest")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "test-plugin"

    def test_get_plugin_manifest_not_found(self, client, mock_plugin_manager):
        """Test getting manifest of non-existent plugin."""
        mock_plugin_manager.get_plugin_manifest.side_effect = ValueError("Plugin not found")

        response = client.get("/plugins/nonexistent/manifest")

        assert response.status_code == 404