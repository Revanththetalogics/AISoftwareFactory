"""
Comprehensive tests for Real-time Monitoring API routes.
This file aims to achieve high coverage (>90%) for realtime.py module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from backend.api.routes.realtime import router
from backend.monitoring.realtime import MonitorEventType


class TestRealtimeRoutes:
    """Tests for real-time monitoring API routes."""

    @pytest.fixture
    def app(self):
        """Create test app with realtime router."""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_realtime_monitor(self):
        """Mock the realtime monitor."""
        with patch("backend.api.routes.realtime.realtime_monitor") as mock:
            mock._is_running = True
            mock.active_connections = set()
            mock.subscribed_clients = set()
            mock._event_buffer = []
            mock.METRIC_UPDATE_INTERVAL = 5
            mock.SYSTEM_METRIC_INTERVAL = 30
            mock.CLUSTER_METRIC_INTERVAL = 60
            yield mock

    def test_subscribe_to_monitoring(self, client, mock_realtime_monitor):
        """Test subscribing to monitoring topics."""
        subscription_data = {"topics": ["cpu", "memory", "disk"], "client_id": "test-client-123"}

        response = client.post("/realtime/subscribe", json=subscription_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "topics" in data["message"]

    def test_subscribe_to_monitoring_no_client_id(self, client, mock_realtime_monitor):
        """Test subscribing without client ID."""
        subscription_data = {"topics": ["cpu", "memory"]}

        response = client.post("/realtime/subscribe", json=subscription_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_unsubscribe_from_monitoring(self, client, mock_realtime_monitor):
        """Test unsubscribing from monitoring topics."""
        subscription_data = {"topics": ["cpu", "memory"], "client_id": "test-client-123"}

        response = client.post("/realtime/unsubscribe", json=subscription_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "unsubscribed" in data["message"].lower()

    def test_get_current_snapshot(self, client, mock_realtime_monitor):
        """Test getting current system snapshot."""
        mock_snapshot = {
            "cpu_percent": 45.2,
            "memory_percent": 67.8,
            "disk_percent": 23.1,
            "timestamp": "2026-03-29T10:30:00Z",
        }
        mock_realtime_monitor._collect_system_snapshot = AsyncMock(return_value=mock_snapshot)

        response = client.get("/realtime/snapshot")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] == mock_snapshot
        assert "snapshot" in data["message"].lower()

    def test_get_current_snapshot_error(self, client, mock_realtime_monitor):
        """Test getting snapshot when error occurs."""
        mock_realtime_monitor._collect_system_snapshot = AsyncMock(side_effect=Exception("Database error"))

        response = client.get("/realtime/snapshot")

        assert response.status_code == 500
        data = response.json()
        assert "failed" in data["detail"].lower()

    def test_get_recent_events(self, client, mock_realtime_monitor):
        """Test getting recent events."""
        mock_events = [
            MagicMock(
                event_type=MonitorEventType.METRIC_UPDATE,
                timestamp=MagicMock(isoformat=lambda: "2026-03-29T10:30:00Z"),
                data={"usage": 85.5},
                severity="warning",
            ),
            MagicMock(
                event_type=MonitorEventType.ALERT_TRIGGERED,
                timestamp=MagicMock(isoformat=lambda: "2026-03-29T10:31:00Z"),
                data={"usage": 92.1},
                severity="critical",
            ),
        ]
        mock_realtime_monitor.get_recent_events.return_value = mock_events

        response = client.get("/realtime/events/recent?limit=50")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["events"]) == 2
        assert data["data"]["total_count"] == 2

    def test_get_recent_events_with_filtering(self, client, mock_realtime_monitor):
        """Test getting recent events with filtering."""
        mock_events = [
            MagicMock(
                event_type=MonitorEventType.METRIC_UPDATE,
                timestamp=MagicMock(isoformat=lambda: "2026-03-29T10:30:00Z"),
                data={"usage": 85.5},
                severity="warning",
            )
        ]
        mock_realtime_monitor.get_recent_events.return_value = mock_events

        response = client.get(
            "/realtime/events/recent",
            params={
                "limit": 10,
                "filter": {"event_types": ["metric_update"], "severity_levels": ["warning"], "time_range_minutes": 30},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "filters_applied" in data["data"]

    def test_trigger_alert_event(self, client, mock_realtime_monitor):
        """Test manually triggering an alert event."""
        with patch("backend.api.routes.realtime.MonitoringEventTrigger.trigger_alert", new=AsyncMock()) as mock_trigger:
            response = client.post(
                "/realtime/events/trigger/alert",
                json={
                    "alert_name": "High CPU Usage",
                    "severity": "warning",
                    "details": {"threshold": 80, "current": 85.5},
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "high cpu usage" in data["message"].lower()
            mock_trigger.assert_called_once()

    def test_trigger_service_status_event(self, client, mock_realtime_monitor):
        """Test manually triggering a service status change event."""
        with patch(
            "backend.api.routes.realtime.MonitoringEventTrigger.trigger_service_status_change", new=AsyncMock()
        ) as mock_trigger:
            response = client.post(
                "/realtime/events/trigger/service-status",
                json={"service_name": "database", "old_status": "healthy", "new_status": "degraded"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "database" in data["message"].lower()
            mock_trigger.assert_called_once()

    def test_get_active_connections(self, client, mock_realtime_monitor):
        """Test getting active connection information."""
        mock_realtime_monitor.active_connections = {"conn1", "conn2"}
        mock_realtime_monitor.subscribed_clients = {"client1"}

        response = client.get("/realtime/connections")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["active_connections"] == 2
        assert data["data"]["subscribed_clients"] == 1

    def test_start_monitoring_broadcast(self, client, mock_realtime_monitor):
        """Test starting monitoring broadcast."""
        mock_realtime_monitor.start_monitoring = AsyncMock()

        response = client.post("/realtime/control/start")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "started" in data["message"].lower()
        mock_realtime_monitor.start_monitoring.assert_called_once()

    def test_stop_monitoring_broadcast(self, client, mock_realtime_monitor):
        """Test stopping monitoring broadcast."""
        mock_realtime_monitor.stop_monitoring = AsyncMock()

        response = client.post("/realtime/control/stop")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "stopped" in data["message"].lower()
        mock_realtime_monitor.stop_monitoring.assert_called_once()

    def test_get_live_metrics(self, client, mock_realtime_monitor):
        """Test getting live metrics configuration."""
        response = client.get("/realtime/metrics/live")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "update_intervals" in data["data"]
        assert "available_metrics" in data["data"]
        assert "broadcast_status" in data["data"]

    @pytest.mark.skip(
        reason="WebSocket test calls real realtime_monitoring_endpoint which has an infinite message loop; needs proper mock of the endpoint function itself"
    )
    def test_websocket_connection(self, client, mock_realtime_monitor):
        """Test WebSocket connection endpoint."""
        mock_realtime_monitor.connect = AsyncMock()

        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/realtime/monitor?client_id=test-123"):
                pass

        mock_realtime_monitor.connect.assert_called()

    @pytest.mark.skip(
        reason="WebSocket test calls real realtime_monitoring_endpoint which has an infinite message loop; needs proper mock of the endpoint function itself"
    )
    def test_websocket_connection_auto_client_id(self, client, mock_realtime_monitor):
        """Test WebSocket connection with auto-generated client ID."""
        mock_realtime_monitor.connect = AsyncMock()

        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/realtime/monitor"):
                pass

        mock_realtime_monitor.connect.assert_called()


class TestRealtimeErrorHandling:
    """Tests for error handling in real-time routes."""

    @pytest.fixture
    def app(self):
        """Create test app with realtime router."""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_subscribe_internal_error(self, client):
        """Test subscription when internal error occurs."""
        # Make the logger.error raise an exception to simulate internal error
        with patch("backend.api.routes.realtime.logger") as mock_logger:
            mock_logger.info.side_effect = Exception("Internal logging error")

            response = client.post("/realtime/subscribe", json={"topics": ["cpu"]})

            assert response.status_code == 500
            assert "subscription failed" in response.json()["detail"].lower()

    def test_unsubscribe_internal_error(self, client):
        """Test unsubscription when internal error occurs."""
        with patch("backend.api.routes.realtime.logger") as mock_logger:
            mock_logger.info.side_effect = Exception("Internal logging error")

            response = client.post("/realtime/unsubscribe", json={"topics": ["cpu"]})

            assert response.status_code == 500
            assert "unsubscription failed" in response.json()["detail"].lower()

    def test_trigger_alert_error(self, client):
        """Test alert trigger when error occurs."""
        with patch("backend.api.routes.realtime.MonitoringEventTrigger") as mock_trigger:
            mock_trigger.trigger_alert = AsyncMock(side_effect=Exception("Trigger failed"))

            response = client.post(
                "/realtime/events/trigger/alert", json={"alert_name": "Test Alert", "severity": "info", "details": {}}
            )

            assert response.status_code == 500
            assert "failed to trigger alert" in response.json()["detail"].lower()

    def test_trigger_service_status_error(self, client):
        """Test service status trigger when error occurs."""
        with patch("backend.api.routes.realtime.MonitoringEventTrigger") as mock_trigger:
            mock_trigger.trigger_service_status_change = AsyncMock(side_effect=Exception("Trigger failed"))

            response = client.post(
                "/realtime/events/trigger/service-status",
                json={"service_name": "test-service", "old_status": "unknown", "new_status": "healthy"},
            )

            assert response.status_code == 500
            assert "failed to trigger event" in response.json()["detail"].lower()

    def test_start_monitoring_error(self, client):
        """Test starting monitoring when error occurs."""
        with patch("backend.api.routes.realtime.realtime_monitor") as mock_monitor:
            mock_monitor.start_monitoring = AsyncMock(side_effect=Exception("Start failed"))

            response = client.post("/realtime/control/start")

            assert response.status_code == 500
            assert "failed to start monitoring" in response.json()["detail"].lower()

    def test_stop_monitoring_error(self, client):
        """Test stopping monitoring when error occurs."""
        with patch("backend.api.routes.realtime.realtime_monitor") as mock_monitor:
            mock_monitor.stop_monitoring = AsyncMock(side_effect=Exception("Stop failed"))

            response = client.post("/realtime/control/stop")

            assert response.status_code == 500
            assert "failed to stop monitoring" in response.json()["detail"].lower()

    @pytest.mark.skip(
        reason="MagicMock is not a property descriptor; type(mock).attr = MagicMock(side_effect=...) does not reliably raise on attribute access"
    )
    def test_get_connections_error(self, client):
        """Test getting connections when error occurs."""
        with patch("backend.api.routes.realtime.realtime_monitor") as mock_monitor:
            type(mock_monitor).active_connections = MagicMock(side_effect=Exception("Access failed"))

            response = client.get("/realtime/connections")

            assert response.status_code == 500
            assert "failed to get connections" in response.json()["detail"].lower()

    @pytest.mark.skip(
        reason="MagicMock is not a property descriptor; type(mock).attr = MagicMock(side_effect=...) does not reliably raise on attribute access"
    )
    def test_get_metrics_error(self, client):
        """Test getting metrics when error occurs."""
        with patch("backend.api.routes.realtime.realtime_monitor") as mock_monitor:
            type(mock_monitor).METRIC_UPDATE_INTERVAL = MagicMock(side_effect=Exception("Access failed"))

            response = client.get("/realtime/metrics/live")

            assert response.status_code == 500
            assert "failed to get metrics info" in response.json()["detail"].lower()
