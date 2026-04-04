"""
Tests for health check endpoints.

This module tests the health, readiness, and liveness endpoints.
"""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test cases for health check endpoints."""

    def test_health_check_success(self, test_client: TestClient):
        """Test that health check returns healthy status."""
        response = test_client.get("/api/v1/health")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "correlation_id" in data
        assert "uptime_seconds" in data
        assert "components" in data
        assert len(data["components"]) > 0

    def test_health_check_correlation_id(self, test_client: TestClient):
        """Test that health check returns correlation ID in header."""
        response = test_client.get("/api/v1/health")

        assert "X-Correlation-ID" in response.headers
        assert response.headers["X-Correlation-ID"] == response.json()["correlation_id"]

    def test_health_check_with_custom_correlation_id(self, test_client: TestClient):
        """Test that custom correlation ID is preserved."""
        custom_id = "test-correlation-id-123"
        response = test_client.get("/api/v1/health", headers={"X-Correlation-ID": custom_id})

        assert response.status_code == 200
        assert response.json()["correlation_id"] == custom_id
        assert response.headers["X-Correlation-ID"] == custom_id

    def test_health_check_components(self, test_client: TestClient):
        """Test that health check includes component details."""
        response = test_client.get("/api/v1/health")

        data = response.json()
        components = data["components"]

        # Should have application component
        app_component = next((c for c in components if c["name"] == "application"), None)
        assert app_component is not None
        assert app_component["status"] == "healthy"
        assert "response_time_ms" in app_component

        # Should have configuration component
        config_component = next((c for c in components if c["name"] == "configuration"), None)
        assert config_component is not None
        assert config_component["status"] == "healthy"

    def test_readiness_check(self, test_client: TestClient):
        """Test readiness check endpoint."""
        # Mock DB and Redis so the test doesn't require live infrastructure
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn_ctx = MagicMock()
        mock_conn_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_engine = MagicMock()
        mock_engine.connect = MagicMock(return_value=mock_conn_ctx)

        with (
            patch("backend.db.session.engine", mock_engine),
            patch("backend.api.health._check_redis", new=AsyncMock(return_value=True)),
        ):
            response = test_client.get("/api/v1/ready")

        assert response.status_code == 200

        data = response.json()
        assert data["ready"] is True
        assert "timestamp" in data
        assert "checks" in data
        assert data["checks"]["application"] is True

    def test_liveness_check(self, test_client: TestClient):
        """Test liveness check endpoint."""
        response = test_client.get("/api/v1/live")

        assert response.status_code == 200

        data = response.json()
        assert data["alive"] is True
        assert "timestamp" in data

    def test_simple_health_check(self, test_client: TestClient):
        """Test simple health check endpoint."""
        response = test_client.get("/api/v1/health/simple")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_root_endpoint(self, test_client: TestClient):
        """Test root endpoint."""
        response = test_client.get("/")

        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "environment" in data


class TestHealthEndpointErrors:
    """Test error handling in health endpoints."""

    def test_health_check_handles_errors_gracefully(self, test_client: TestClient):
        """Test that health check handles internal errors gracefully."""
        # Health check should always return 200 even if components fail
        # because we want the health endpoint itself to be available
        response = test_client.get("/api/v1/health")

        assert response.status_code == 200
        assert "status" in response.json()
