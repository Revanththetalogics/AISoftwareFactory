"""
Comprehensive tests for ErrorHandlerMiddleware module.

Covers all uncovered lines in error_handler.py:
- Lines 64-70, 87-110, 133-169, 197-217, 228-261
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core.exceptions import (
    AISoftwareFactoryException,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
)
from backend.middleware.error_handler import (
    ErrorHandlerMiddleware,
    setup_exception_handlers,
)


class TestErrorHandlerMiddleware:
    """Comprehensive tests for ErrorHandlerMiddleware."""

    @pytest.fixture
    def app(self):
        """Create a test FastAPI app with middleware."""
        app = FastAPI()
        app.add_middleware(ErrorHandlerMiddleware)
        return app

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        with patch("backend.middleware.error_handler.get_settings") as mock:
            settings = MagicMock()
            settings.is_development = True
            settings.is_testing = True
            mock.return_value = settings
            yield settings

    def test_middleware_init(self, mock_settings):
        """Test middleware initialization."""
        app = FastAPI()
        middleware = ErrorHandlerMiddleware(app)

        assert middleware.settings is not None

    @pytest.mark.asyncio
    async def test_dispatch_success(self, mock_settings):
        """Test that successful requests pass through."""
        app = FastAPI()
        app.add_middleware(ErrorHandlerMiddleware)

        @app.get("/health")
        async def health():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_dispatch_custom_exception(self, mock_settings):
        """Test handling of custom AISoftwareFactoryException."""
        app = FastAPI()
        app.add_middleware(ErrorHandlerMiddleware)

        @app.get("/error")
        async def raise_error():
            raise ResourceNotFoundError(
                resource_type="Project",
                resource_id="123",
            )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/error")

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
        assert "request_id" in data

    @pytest.mark.asyncio
    async def test_dispatch_unexpected_exception_development(self, mock_settings):
        """Test handling of unexpected exception in development mode."""
        mock_settings.is_development = True
        mock_settings.is_testing = True

        app = FastAPI()
        app.add_middleware(ErrorHandlerMiddleware)

        @app.get("/unexpected")
        async def raise_unexpected():
            raise RuntimeError("Unexpected error occurred")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/unexpected")

        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "INTERNAL_ERROR"
        assert "Unexpected error occurred" in data["error"]["message"]
        assert "stack_trace" in data["error"]["details"]
        assert "type" in data["error"]["details"]

    @pytest.mark.asyncio
    async def test_dispatch_unexpected_exception_production(self):
        """Test handling of unexpected exception in production mode."""
        with patch("backend.middleware.error_handler.get_settings") as mock:
            settings = MagicMock()
            settings.is_development = False
            settings.is_testing = False
            mock.return_value = settings

            app = FastAPI()
            app.add_middleware(ErrorHandlerMiddleware)

            @app.get("/unexpected")
            async def raise_unexpected():
                raise RuntimeError("Sensitive error details")

            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/unexpected")

            assert response.status_code == 500
            data = response.json()
            assert data["error"]["code"] == "INTERNAL_ERROR"
            # Should not expose error details in production
            assert "Sensitive error details" not in data["error"]["message"]
            assert "unexpected error occurred" in data["error"]["message"].lower()
            assert data["error"]["details"] == {}

    @pytest.mark.asyncio
    async def test_handle_custom_exception_with_details(self, mock_settings):
        """Test handling custom exception with additional details."""
        app = FastAPI()
        app.add_middleware(ErrorHandlerMiddleware)

        @app.get("/validation-error")
        async def raise_validation():
            raise ValidationError(
                message="Invalid input",
                errors=[
                    {"field": "email", "message": "Invalid email format"},
                    {"field": "age", "message": "Must be positive"},
                ],
            )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/validation-error")

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "errors" in data["error"]["details"]

    @pytest.mark.asyncio
    async def test_handle_authentication_error(self, mock_settings):
        """Test handling authentication error."""
        app = FastAPI()
        app.add_middleware(ErrorHandlerMiddleware)

        @app.get("/auth-error")
        async def raise_auth():
            raise AuthenticationError(message="Invalid token")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/auth-error")

        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "AUTHENTICATION_ERROR"


class TestSetupExceptionHandlers:
    """Tests for setup_exception_handlers function."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        with patch("backend.middleware.error_handler.get_settings") as mock:
            settings = MagicMock()
            settings.is_development = True
            settings.is_testing = True
            mock.return_value = settings
            yield settings

    def test_setup_exception_handlers(self, mock_settings):
        """Test setting up exception handlers on app."""
        app = FastAPI()
        setup_exception_handlers(app)

        # Verify handlers are registered
        assert AISoftwareFactoryException in app.exception_handlers
        assert Exception in app.exception_handlers

    @pytest.mark.asyncio
    async def test_custom_exception_handler(self, mock_settings):
        """Test custom exception handler via setup_exception_handlers."""
        app = FastAPI()
        setup_exception_handlers(app)

        @app.get("/not-found")
        async def raise_not_found():
            raise ResourceNotFoundError(
                resource_type="User",
                resource_id="user-456",
            )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/not-found")

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
        assert "request_id" in data

    @pytest.mark.asyncio
    async def test_general_exception_handler_development(self, mock_settings):
        """Test general exception handler in development."""
        mock_settings.is_development = True
        mock_settings.is_testing = True

        app = FastAPI()
        setup_exception_handlers(app)

        @app.get("/general-error")
        async def raise_general():
            raise ValueError("Some value error")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/general-error")

        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "INTERNAL_ERROR"
        assert "Some value error" in data["error"]["message"]
        assert "stack_trace" in data["error"]["details"]

    @pytest.mark.asyncio
    async def test_general_exception_handler_production(self):
        """Test general exception handler in production."""
        with patch("backend.middleware.error_handler.get_settings") as mock:
            settings = MagicMock()
            settings.is_development = False
            settings.is_testing = False
            mock.return_value = settings

            app = FastAPI()
            setup_exception_handlers(app)

            @app.get("/general-error")
            async def raise_general():
                raise ValueError("Sensitive details here")

            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/general-error")

            assert response.status_code == 500
            data = response.json()
            assert data["error"]["code"] == "INTERNAL_ERROR"
            # Should not expose sensitive details
            assert "Sensitive details here" not in data["error"]["message"]
            assert data["error"]["details"] == {}


class TestErrorHandlerEdgeCases:
    """Edge case tests for error handling."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        with patch("backend.middleware.error_handler.get_settings") as mock:
            settings = MagicMock()
            settings.is_development = True
            settings.is_testing = True
            mock.return_value = settings
            yield settings

    @pytest.mark.asyncio
    async def test_exception_with_empty_details(self, mock_settings):
        """Test exception handling with empty details."""
        app = FastAPI()
        app.add_middleware(ErrorHandlerMiddleware)

        @app.get("/empty-details")
        async def raise_empty():
            raise AISoftwareFactoryException(
                message="Error with no details",
                error_code="CUSTOM_ERROR",
                status_code=400,
                details=None,
            )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/empty-details")

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["details"] == {}

    @pytest.mark.asyncio
    async def test_correlation_id_in_response(self, mock_settings):
        """Test that correlation ID is included in error response."""
        with patch("backend.middleware.error_handler.get_correlation_id") as mock_corr:
            mock_corr.return_value = "test-correlation-id-123"

            app = FastAPI()
            app.add_middleware(ErrorHandlerMiddleware)

            @app.get("/correlation-test")
            async def raise_error():
                raise RuntimeError("Test error")

            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/correlation-test")

            data = response.json()
            assert data["request_id"] == "test-correlation-id-123"

    @pytest.mark.asyncio
    async def test_multiple_exceptions_same_request_type(self, mock_settings):
        """Test multiple different exception types."""
        app = FastAPI()
        app.add_middleware(ErrorHandlerMiddleware)

        @app.get("/error/{error_type}")
        async def raise_by_type(error_type: str):
            if error_type == "validation":
                raise ValidationError("Validation failed")
            elif error_type == "auth":
                raise AuthenticationError("Auth failed")
            elif error_type == "notfound":
                raise ResourceNotFoundError(resource_type="Item", resource_id="1")
            else:
                raise RuntimeError("Unknown error type")

        client = TestClient(app, raise_server_exceptions=False)

        # Test validation error
        resp = client.get("/error/validation")
        assert resp.status_code == 400

        # Test auth error
        resp = client.get("/error/auth")
        assert resp.status_code == 401

        # Test not found error
        resp = client.get("/error/notfound")
        assert resp.status_code == 404

        # Test runtime error
        resp = client.get("/error/other")
        assert resp.status_code == 500
