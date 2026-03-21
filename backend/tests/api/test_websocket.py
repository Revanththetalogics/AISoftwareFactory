"""
Comprehensive tests for WebSocket API routes.

Covers all WebSocket endpoints and connection management:
- Global WebSocket
- Project WebSocket
- Workflow WebSocket
- Connection manager
- Broadcast functions
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import WebSocket, WebSocketDisconnect

from backend.api.dependencies import User
from backend.api.routes import websocket as ws_module
from backend.api.routes.websocket import (
    ConnectionManager,
    broadcast_project_update,
    broadcast_workflow_update,
    global_websocket,
    project_websocket,
    workflow_websocket,
)


class TestConnectionManager:
    """Tests for ConnectionManager class."""

    @pytest.fixture
    def manager(self):
        """Create a fresh ConnectionManager for each test."""
        return ConnectionManager()

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket."""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_json = AsyncMock()
        ws.receive_json = AsyncMock()
        ws.close = AsyncMock()
        return ws

    @pytest.mark.asyncio
    async def test_connect(self, manager, mock_websocket):
        """Test connecting a WebSocket."""
        await manager.connect(mock_websocket)

        mock_websocket.accept.assert_called_once()
        assert mock_websocket in manager.active_connections

    def test_disconnect(self, manager, mock_websocket):
        """Test disconnecting a WebSocket."""
        manager.active_connections.add(mock_websocket)

        manager.disconnect(mock_websocket)

        assert mock_websocket not in manager.active_connections

    def test_disconnect_nonexistent(self, manager, mock_websocket):
        """Test disconnecting a WebSocket that isn't connected."""
        # Should not raise - uses discard
        manager.disconnect(mock_websocket)
        assert mock_websocket not in manager.active_connections

    @pytest.mark.asyncio
    async def test_broadcast(self, manager, mock_websocket):
        """Test broadcasting message to all connections."""
        manager.active_connections.add(mock_websocket)
        message = {"type": "test", "data": "hello"}

        await manager.broadcast(message)

        mock_websocket.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_removes_disconnected(self, manager):
        """Test that broadcast removes disconnected clients."""
        ws1 = AsyncMock(spec=WebSocket)
        ws1.send_json = AsyncMock()

        ws2 = AsyncMock(spec=WebSocket)
        ws2.send_json = AsyncMock(side_effect=Exception("Connection closed"))

        manager.active_connections.add(ws1)
        manager.active_connections.add(ws2)

        await manager.broadcast({"type": "test"})

        # ws1 should still be connected, ws2 should be removed
        assert ws1 in manager.active_connections
        assert ws2 not in manager.active_connections


class TestGlobalWebSocket:
    """Tests for global WebSocket endpoint."""

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket with client info."""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_json = AsyncMock()
        ws.receive_json = AsyncMock()
        ws.close = AsyncMock()
        ws.client = MagicMock()
        ws.client.host = "127.0.0.1"
        return ws

    @pytest.fixture
    def mock_user(self):
        """Create a mock authenticated user."""
        return User(
            user_id="user-123",
            username="testuser",
            email="test@example.com",
            permissions=["read", "write"]
        )

    @pytest.mark.asyncio
    async def test_global_websocket_unauthenticated(self, mock_websocket):
        """Test global WebSocket rejects unauthenticated connections."""
        with patch('backend.api.routes.websocket.get_websocket_user', return_value=None):
            await global_websocket(mock_websocket)

        mock_websocket.close.assert_called_once_with(
            code=4001, reason="Authentication required"
        )

    @pytest.mark.asyncio
    async def test_global_websocket_ping(self, mock_websocket, mock_user):
        """Test global WebSocket ping/pong."""
        # Set up receive to return ping then disconnect
        mock_websocket.receive_json = AsyncMock(
            side_effect=[
                {"type": "ping"},
                WebSocketDisconnect()
            ]
        )

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await global_websocket(mock_websocket)

        # Check pong was sent
        calls = mock_websocket.send_json.call_args_list
        pong_calls = [c for c in calls if c[0][0].get("type") == "pong"]
        assert len(pong_calls) >= 1

    @pytest.mark.asyncio
    async def test_global_websocket_subscribe(self, mock_websocket, mock_user):
        """Test global WebSocket subscription."""
        mock_websocket.receive_json = AsyncMock(
            side_effect=[
                {"type": "subscribe", "payload": {"topics": ["system", "alerts"]}},
                WebSocketDisconnect()
            ]
        )

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await global_websocket(mock_websocket)

        # Check subscribed response
        calls = mock_websocket.send_json.call_args_list
        sub_calls = [c for c in calls if c[0][0].get("type") == "subscribed"]
        assert len(sub_calls) >= 1

    @pytest.mark.asyncio
    async def test_global_websocket_unknown_message(self, mock_websocket, mock_user):
        """Test global WebSocket handles unknown message types."""
        mock_websocket.receive_json = AsyncMock(
            side_effect=[
                {"type": "unknown_type"},
                WebSocketDisconnect()
            ]
        )

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await global_websocket(mock_websocket)

        # Check error response
        calls = mock_websocket.send_json.call_args_list
        error_calls = [c for c in calls if c[0][0].get("type") == "error"]
        assert len(error_calls) >= 1
        assert "Unknown message type" in str(error_calls[0])

    @pytest.mark.asyncio
    async def test_global_websocket_invalid_json(self, mock_websocket, mock_user):
        """Test global WebSocket handles invalid JSON."""
        mock_websocket.receive_json = AsyncMock(
            side_effect=[
                json.JSONDecodeError("Invalid", "", 0),
                WebSocketDisconnect()
            ]
        )

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await global_websocket(mock_websocket)

        # Check error response for invalid JSON
        calls = mock_websocket.send_json.call_args_list
        error_calls = [c for c in calls if c[0][0].get("type") == "error"]
        assert len(error_calls) >= 1


class TestProjectWebSocket:
    """Tests for project-specific WebSocket endpoint."""

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket."""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_json = AsyncMock()
        ws.receive_json = AsyncMock()
        ws.close = AsyncMock()
        ws.client = MagicMock()
        ws.client.host = "127.0.0.1"
        return ws

    @pytest.fixture
    def mock_user(self):
        """Create a mock authenticated user."""
        return User(
            user_id="user-123",
            username="testuser",
            email="test@example.com",
            permissions=["read", "write"]
        )

    @pytest.mark.asyncio
    async def test_project_websocket_unauthenticated(self, mock_websocket):
        """Test project WebSocket rejects unauthenticated connections."""
        with patch('backend.api.routes.websocket.get_websocket_user', return_value=None):
            await project_websocket(mock_websocket, "project-123")

        mock_websocket.close.assert_called_once_with(
            code=4001, reason="Authentication required"
        )

    @pytest.mark.asyncio
    async def test_project_websocket_ping(self, mock_websocket, mock_user):
        """Test project WebSocket ping/pong."""
        mock_websocket.receive_json = AsyncMock(
            side_effect=[
                {"type": "ping"},
                WebSocketDisconnect()
            ]
        )

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await project_websocket(mock_websocket, "project-123")

        # Check pong was sent
        calls = mock_websocket.send_json.call_args_list
        pong_calls = [c for c in calls if c[0][0].get("type") == "pong"]
        assert len(pong_calls) >= 1

    @pytest.mark.asyncio
    async def test_project_websocket_get_status(self, mock_websocket, mock_user):
        """Test project WebSocket get_status request."""
        mock_websocket.receive_json = AsyncMock(
            side_effect=[
                {"type": "get_status"},
                WebSocketDisconnect()
            ]
        )

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await project_websocket(mock_websocket, "project-123")

        # Check status response
        calls = mock_websocket.send_json.call_args_list
        status_calls = [c for c in calls if c[0][0].get("type") == "status"]
        assert len(status_calls) >= 1
        assert status_calls[0][0][0]["payload"]["project_id"] == "project-123"

    @pytest.mark.asyncio
    async def test_project_websocket_unknown_message(self, mock_websocket, mock_user):
        """Test project WebSocket handles unknown message types."""
        mock_websocket.receive_json = AsyncMock(
            side_effect=[
                {"type": "unknown_type"},
                WebSocketDisconnect()
            ]
        )

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await project_websocket(mock_websocket, "project-123")

        calls = mock_websocket.send_json.call_args_list
        error_calls = [c for c in calls if c[0][0].get("type") == "error"]
        assert len(error_calls) >= 1

    @pytest.mark.asyncio
    async def test_project_websocket_invalid_json(self, mock_websocket, mock_user):
        """Test project WebSocket handles invalid JSON."""
        mock_websocket.receive_json = AsyncMock(
            side_effect=[
                json.JSONDecodeError("Invalid", "", 0),
                WebSocketDisconnect()
            ]
        )

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await project_websocket(mock_websocket, "project-123")

        calls = mock_websocket.send_json.call_args_list
        error_calls = [c for c in calls if c[0][0].get("type") == "error"]
        assert len(error_calls) >= 1

    @pytest.mark.asyncio
    async def test_project_websocket_cleanup_on_disconnect(self, mock_websocket, mock_user):
        """Test project WebSocket removes connection on disconnect."""
        mock_websocket.receive_json = AsyncMock(side_effect=WebSocketDisconnect())

        # Clear any existing connections
        ws_module._project_connections.clear()

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await project_websocket(mock_websocket, "project-cleanup-test")

        # Connection should be cleaned up
        assert "project-cleanup-test" not in ws_module._project_connections or \
               mock_websocket not in ws_module._project_connections.get("project-cleanup-test", set())


class TestWorkflowWebSocket:
    """Tests for workflow-specific WebSocket endpoint."""

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket."""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_json = AsyncMock()
        ws.receive_json = AsyncMock()
        ws.close = AsyncMock()
        ws.client = MagicMock()
        ws.client.host = "127.0.0.1"
        return ws

    @pytest.fixture
    def mock_user(self):
        """Create a mock authenticated user."""
        return User(
            user_id="user-123",
            username="testuser",
            email="test@example.com",
            permissions=["read", "write"]
        )

    @pytest.mark.asyncio
    async def test_workflow_websocket_unauthenticated(self, mock_websocket):
        """Test workflow WebSocket rejects unauthenticated connections."""
        with patch('backend.api.routes.websocket.get_websocket_user', return_value=None):
            await workflow_websocket(mock_websocket, "workflow-123")

        mock_websocket.close.assert_called_once_with(
            code=4001, reason="Authentication required"
        )

    @pytest.mark.asyncio
    async def test_workflow_websocket_ping(self, mock_websocket, mock_user):
        """Test workflow WebSocket ping/pong."""
        mock_websocket.receive_json = AsyncMock(
            side_effect=[
                {"type": "ping"},
                WebSocketDisconnect()
            ]
        )

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await workflow_websocket(mock_websocket, "workflow-123")

        calls = mock_websocket.send_json.call_args_list
        pong_calls = [c for c in calls if c[0][0].get("type") == "pong"]
        assert len(pong_calls) >= 1

    @pytest.mark.asyncio
    async def test_workflow_websocket_get_logs(self, mock_websocket, mock_user):
        """Test workflow WebSocket get_logs request."""
        mock_websocket.receive_json = AsyncMock(
            side_effect=[
                {"type": "get_logs"},
                WebSocketDisconnect()
            ]
        )

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await workflow_websocket(mock_websocket, "workflow-123")

        calls = mock_websocket.send_json.call_args_list
        logs_calls = [c for c in calls if c[0][0].get("type") == "logs"]
        assert len(logs_calls) >= 1
        assert logs_calls[0][0][0]["payload"]["workflow_id"] == "workflow-123"

    @pytest.mark.asyncio
    async def test_workflow_websocket_unknown_message(self, mock_websocket, mock_user):
        """Test workflow WebSocket handles unknown message types."""
        mock_websocket.receive_json = AsyncMock(
            side_effect=[
                {"type": "unknown_type"},
                WebSocketDisconnect()
            ]
        )

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await workflow_websocket(mock_websocket, "workflow-123")

        calls = mock_websocket.send_json.call_args_list
        error_calls = [c for c in calls if c[0][0].get("type") == "error"]
        assert len(error_calls) >= 1

    @pytest.mark.asyncio
    async def test_workflow_websocket_invalid_json(self, mock_websocket, mock_user):
        """Test workflow WebSocket handles invalid JSON."""
        mock_websocket.receive_json = AsyncMock(
            side_effect=[
                json.JSONDecodeError("Invalid", "", 0),
                WebSocketDisconnect()
            ]
        )

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await workflow_websocket(mock_websocket, "workflow-123")

        calls = mock_websocket.send_json.call_args_list
        error_calls = [c for c in calls if c[0][0].get("type") == "error"]
        assert len(error_calls) >= 1

    @pytest.mark.asyncio
    async def test_workflow_websocket_cleanup_on_disconnect(self, mock_websocket, mock_user):
        """Test workflow WebSocket removes connection on disconnect."""
        mock_websocket.receive_json = AsyncMock(side_effect=WebSocketDisconnect())

        # Clear any existing connections
        ws_module._workflow_connections.clear()

        with patch('backend.api.routes.websocket.get_websocket_user',
                   return_value=mock_user):
            await workflow_websocket(mock_websocket, "workflow-cleanup-test")

        assert "workflow-cleanup-test" not in ws_module._workflow_connections or \
               mock_websocket not in ws_module._workflow_connections.get("workflow-cleanup-test", set())


class TestBroadcastFunctions:
    """Tests for broadcast helper functions."""

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket."""
        ws = AsyncMock(spec=WebSocket)
        ws.send_json = AsyncMock()
        return ws

    @pytest.mark.asyncio
    async def test_broadcast_project_update_no_connections(self):
        """Test broadcasting to project with no connections."""
        ws_module._project_connections.clear()

        # Should not raise
        await broadcast_project_update("project-123", {"type": "update"})

    @pytest.mark.asyncio
    async def test_broadcast_project_update_success(self, mock_websocket):
        """Test successful project broadcast."""
        ws_module._project_connections["project-broadcast"] = {mock_websocket}

        await broadcast_project_update("project-broadcast", {"type": "update"})

        mock_websocket.send_json.assert_called_once_with({"type": "update"})

        # Cleanup
        ws_module._project_connections.pop("project-broadcast", None)

    @pytest.mark.asyncio
    async def test_broadcast_project_update_removes_disconnected(self):
        """Test project broadcast removes disconnected clients."""
        ws_good = AsyncMock(spec=WebSocket)
        ws_good.send_json = AsyncMock()

        ws_bad = AsyncMock(spec=WebSocket)
        ws_bad.send_json = AsyncMock(side_effect=Exception("Disconnected"))

        ws_module._project_connections["project-remove"] = {ws_good, ws_bad}

        await broadcast_project_update("project-remove", {"type": "update"})

        assert ws_good in ws_module._project_connections["project-remove"]
        assert ws_bad not in ws_module._project_connections["project-remove"]

        # Cleanup
        ws_module._project_connections.pop("project-remove", None)

    @pytest.mark.asyncio
    async def test_broadcast_workflow_update_no_connections(self):
        """Test broadcasting to workflow with no connections."""
        ws_module._workflow_connections.clear()

        # Should not raise
        await broadcast_workflow_update("workflow-123", {"type": "update"})

    @pytest.mark.asyncio
    async def test_broadcast_workflow_update_success(self, mock_websocket):
        """Test successful workflow broadcast."""
        ws_module._workflow_connections["workflow-broadcast"] = {mock_websocket}

        await broadcast_workflow_update("workflow-broadcast", {"type": "update"})

        mock_websocket.send_json.assert_called_once_with({"type": "update"})

        # Cleanup
        ws_module._workflow_connections.pop("workflow-broadcast", None)

    @pytest.mark.asyncio
    async def test_broadcast_workflow_update_removes_disconnected(self):
        """Test workflow broadcast removes disconnected clients."""
        ws_good = AsyncMock(spec=WebSocket)
        ws_good.send_json = AsyncMock()

        ws_bad = AsyncMock(spec=WebSocket)
        ws_bad.send_json = AsyncMock(side_effect=Exception("Disconnected"))

        ws_module._workflow_connections["workflow-remove"] = {ws_good, ws_bad}

        await broadcast_workflow_update("workflow-remove", {"type": "update"})

        assert ws_good in ws_module._workflow_connections["workflow-remove"]
        assert ws_bad not in ws_module._workflow_connections["workflow-remove"]

        # Cleanup
        ws_module._workflow_connections.pop("workflow-remove", None)
