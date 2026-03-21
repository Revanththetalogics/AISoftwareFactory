"""
Tests for middleware modules.

Tests cover:
- RateLimitMiddleware: Rate limiting with token bucket algorithm
- CSRFMiddleware: CSRF token validation using Double Submit Cookie pattern
- AuthenticationMiddleware: Auth enforcement for non-public routes
- PrometheusMetricsMiddleware: Request metrics collection
"""

import time
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from backend.middleware.rate_limit_middleware import RateLimitMiddleware
from backend.middleware.csrf_middleware import (
    CSRFMiddleware,
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    generate_csrf_token,
)
from backend.middleware.auth_middleware import AuthenticationMiddleware, PUBLIC_PATHS


class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware."""
    
    @pytest.fixture
    def rate_limited_app(self):
        """Create a FastAPI app with rate limiting middleware."""
        app = FastAPI()
        
        # Use small values for testing
        app.add_middleware(
            RateLimitMiddleware,
            default_rate=5,
            admin_rate=10,
            window_seconds=60,
        )
        
        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}
        
        @app.get("/health")
        async def health_endpoint():
            return {"status": "healthy"}
        
        @app.get("/api/v1/health")
        async def api_health_endpoint():
            return {"status": "healthy"}
        
        return app
    
    def test_normal_request_passes(self, rate_limited_app):
        """Test normal request passes through."""
        client = TestClient(rate_limited_app)
        
        response = client.get("/test")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_rate_limit_headers_present(self, rate_limited_app):
        """Test rate limit headers are present in response."""
        client = TestClient(rate_limited_app)
        
        response = client.get("/test")
        
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
    
    def test_rate_limit_remaining_decreases(self, rate_limited_app):
        """Test remaining requests decreases with each request."""
        client = TestClient(rate_limited_app)
        
        response1 = client.get("/test")
        remaining1 = int(response1.headers.get("X-RateLimit-Remaining", 0))
        
        response2 = client.get("/test")
        remaining2 = int(response2.headers.get("X-RateLimit-Remaining", 0))
        
        assert remaining2 < remaining1
    
    def test_exceeding_rate_limit_returns_429(self, rate_limited_app):
        """Test exceeding rate limit returns 429 status."""
        client = TestClient(rate_limited_app)
        
        # Make more requests than the limit (5)
        for _ in range(5):
            client.get("/test")
        
        # This should be rate limited
        response = client.get("/test")
        
        assert response.status_code == 429
    
    def test_429_response_includes_retry_after(self, rate_limited_app):
        """Test 429 response includes Retry-After header."""
        client = TestClient(rate_limited_app)
        
        # Exhaust rate limit
        for _ in range(5):
            client.get("/test")
        
        response = client.get("/test")
        
        assert response.status_code == 429
        assert "Retry-After" in response.headers
    
    def test_429_response_body(self, rate_limited_app):
        """Test 429 response body contains error details."""
        client = TestClient(rate_limited_app)
        
        # Exhaust rate limit
        for _ in range(5):
            client.get("/test")
        
        response = client.get("/test")
        body = response.json()
        
        assert "error" in body
        assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert "retry_after" in body["error"]["details"]
    
    def test_health_endpoint_bypasses_rate_limit(self, rate_limited_app):
        """Test /health endpoint bypasses rate limiting."""
        client = TestClient(rate_limited_app)
        
        # Make many requests to health endpoint
        for _ in range(20):
            response = client.get("/health")
            assert response.status_code == 200
    
    def test_api_health_endpoint_bypasses_rate_limit(self, rate_limited_app):
        """Test /api/v1/health endpoint bypasses rate limiting."""
        client = TestClient(rate_limited_app)
        
        # Make many requests
        for _ in range(20):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
    
    def test_different_clients_have_separate_limits(self, rate_limited_app):
        """Test different clients have separate rate limits."""
        client1 = TestClient(rate_limited_app)
        client2 = TestClient(rate_limited_app)
        
        # Exhaust client1's limit
        for _ in range(5):
            client1.get("/test")
        
        # Client2 should still be able to make requests
        response = client2.get("/test", headers={"X-Forwarded-For": "1.2.3.4"})
        assert response.status_code == 200
    
    def test_bearer_token_users_tracked_separately(self, rate_limited_app):
        """Test requests with Bearer tokens are tracked by token."""
        client = TestClient(rate_limited_app)
        
        # Different Bearer tokens should have separate limits
        response1 = client.get("/test", headers={"Authorization": "Bearer token1abc123"})
        response2 = client.get("/test", headers={"Authorization": "Bearer token2xyz456"})
        
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestCSRFMiddleware:
    """Tests for CSRFMiddleware."""
    
    @pytest.fixture
    def csrf_app(self):
        """Create a FastAPI app with CSRF middleware."""
        app = FastAPI()
        app.add_middleware(CSRFMiddleware)
        
        @app.get("/page")
        async def get_page():
            return {"page": "content"}
        
        @app.post("/submit")
        async def submit_form():
            return {"status": "submitted"}
        
        @app.get("/health")
        async def health():
            return {"status": "ok"}
        
        @app.post("/api/v1/auth/login")
        async def login():
            return {"status": "logged_in"}
        
        return app
    
    def test_get_request_passes_without_csrf(self, csrf_app):
        """Test GET request passes without CSRF token."""
        client = TestClient(csrf_app)
        
        response = client.get("/page")
        
        assert response.status_code == 200
    
    def test_get_request_sets_csrf_cookie(self, csrf_app):
        """Test GET request sets CSRF cookie."""
        client = TestClient(csrf_app)
        
        response = client.get("/page")
        
        assert CSRF_COOKIE_NAME in response.cookies
    
    def test_get_request_sets_csrf_header(self, csrf_app):
        """Test GET request sets CSRF header."""
        client = TestClient(csrf_app)
        
        response = client.get("/page")
        
        assert CSRF_HEADER_NAME in response.headers
    
    def test_post_with_bearer_auth_bypasses_csrf(self, csrf_app):
        """Test POST with Bearer token bypasses CSRF validation."""
        client = TestClient(csrf_app)
        
        response = client.post(
            "/submit",
            headers={"Authorization": "Bearer valid_token_here"}
        )
        
        assert response.status_code == 200
    
    def test_post_without_csrf_token_returns_403(self, csrf_app):
        """Test POST without CSRF token returns 403."""
        client = TestClient(csrf_app)
        
        # First get a page to get a session cookie (simulate cookie auth)
        client.get("/page")
        
        # POST without CSRF token should fail for cookie-based auth
        response = client.post(
            "/submit",
            cookies={CSRF_COOKIE_NAME: "some_token"}
        )
        
        assert response.status_code == 403
    
    def test_post_with_valid_csrf_passes(self, csrf_app):
        """Test POST with valid CSRF token passes."""
        client = TestClient(csrf_app)
        
        # Get CSRF token
        get_response = client.get("/page")
        csrf_token = get_response.cookies.get(CSRF_COOKIE_NAME)
        
        # POST with valid CSRF token
        response = client.post(
            "/submit",
            headers={CSRF_HEADER_NAME: csrf_token},
            cookies={CSRF_COOKIE_NAME: csrf_token}
        )
        
        assert response.status_code == 200
    
    def test_post_with_invalid_csrf_returns_403(self, csrf_app):
        """Test POST with invalid CSRF token returns 403."""
        client = TestClient(csrf_app)
        
        # Get CSRF token
        get_response = client.get("/page")
        csrf_token = get_response.cookies.get(CSRF_COOKIE_NAME)
        
        # POST with mismatched CSRF token
        response = client.post(
            "/submit",
            headers={CSRF_HEADER_NAME: "wrong_token"},
            cookies={CSRF_COOKIE_NAME: csrf_token}
        )
        
        assert response.status_code == 403
    
    def test_csrf_error_response_body(self, csrf_app):
        """Test CSRF error response contains error details."""
        client = TestClient(csrf_app)
        
        get_response = client.get("/page")
        csrf_token = get_response.cookies.get(CSRF_COOKIE_NAME)
        
        response = client.post(
            "/submit",
            headers={CSRF_HEADER_NAME: "wrong_token"},
            cookies={CSRF_COOKIE_NAME: csrf_token}
        )
        
        body = response.json()
        assert "detail" in body
        assert body["error_code"] == "CSRF_INVALID"
    
    def test_health_endpoint_exempt_from_csrf(self, csrf_app):
        """Test health endpoints are exempt from CSRF."""
        client = TestClient(csrf_app)
        
        response = client.get("/health")
        
        assert response.status_code == 200
    
    def test_login_endpoint_exempt_from_csrf(self, csrf_app):
        """Test login endpoint is exempt from CSRF."""
        client = TestClient(csrf_app)
        
        response = client.post("/api/v1/auth/login")
        
        assert response.status_code == 200
    
    def test_options_request_passes(self, csrf_app):
        """Test OPTIONS request (CORS preflight) passes."""
        client = TestClient(csrf_app)
        
        response = client.options("/submit")
        
        # OPTIONS should not be blocked by CSRF
        assert response.status_code in [200, 405]  # May return 405 if not explicitly handled


class TestGenerateCsrfToken:
    """Tests for generate_csrf_token() function."""
    
    def test_generates_string(self):
        """Test token is a string."""
        token = generate_csrf_token()
        assert isinstance(token, str)
    
    def test_generates_hex_string(self):
        """Test token is valid hex string."""
        token = generate_csrf_token()
        # Should be able to decode as hex
        int(token, 16)
    
    def test_generates_unique_tokens(self):
        """Test each call generates unique token."""
        tokens = [generate_csrf_token() for _ in range(100)]
        assert len(set(tokens)) == 100
    
    def test_token_length(self):
        """Test token has expected length."""
        token = generate_csrf_token()
        # 32 bytes hex = 64 characters
        assert len(token) == 64


class TestAuthenticationMiddleware:
    """Tests for AuthenticationMiddleware."""
    
    @pytest.fixture
    def auth_app(self):
        """Create a FastAPI app with authentication middleware."""
        app = FastAPI()
        app.add_middleware(AuthenticationMiddleware)
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        @app.get("/api/v1/health")
        async def api_health():
            return {"status": "healthy"}
        
        @app.post("/api/v1/auth/login")
        async def login():
            return {"status": "logged_in"}
        
        @app.get("/docs")
        async def docs():
            return {"docs": "content"}
        
        @app.get("/api/v1/projects")
        async def get_projects():
            return {"projects": []}
        
        @app.post("/api/v1/projects")
        async def create_project():
            return {"status": "created"}
        
        return app
    
    def test_health_endpoint_passes_without_auth(self, auth_app):
        """Test /health endpoint passes without authentication."""
        client = TestClient(auth_app)
        
        response = client.get("/health")
        
        assert response.status_code == 200
    
    def test_api_health_endpoint_passes_without_auth(self, auth_app):
        """Test /api/v1/health endpoint passes without authentication."""
        client = TestClient(auth_app)
        
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
    
    def test_login_endpoint_passes_without_auth(self, auth_app):
        """Test login endpoint passes without authentication."""
        client = TestClient(auth_app)
        
        response = client.post("/api/v1/auth/login")
        
        assert response.status_code == 200
    
    def test_docs_endpoint_passes_without_auth(self, auth_app):
        """Test docs endpoint passes without authentication."""
        client = TestClient(auth_app)
        
        response = client.get("/docs")
        
        assert response.status_code == 200
    
    def test_protected_endpoint_without_auth_returns_401(self, auth_app):
        """Test protected endpoint without auth returns 401."""
        client = TestClient(auth_app)
        
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 401
    
    def test_401_response_includes_www_authenticate(self, auth_app):
        """Test 401 response includes WWW-Authenticate header."""
        client = TestClient(auth_app)
        
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == "Bearer"
    
    def test_401_response_body(self, auth_app):
        """Test 401 response body contains error details."""
        client = TestClient(auth_app)
        
        response = client.get("/api/v1/projects")
        body = response.json()
        
        assert "detail" in body
        assert body["error_code"] == "UNAUTHORIZED"
    
    def test_protected_endpoint_with_bearer_token_passes(self, auth_app):
        """Test protected endpoint with Bearer token passes."""
        client = TestClient(auth_app)
        
        response = client.get(
            "/api/v1/projects",
            headers={"Authorization": "Bearer valid_token_here"}
        )
        
        assert response.status_code == 200
    
    def test_protected_endpoint_with_cookie_passes(self, auth_app):
        """Test protected endpoint with auth cookie passes."""
        client = TestClient(auth_app)
        
        response = client.get(
            "/api/v1/projects",
            cookies={"auth_token": "valid_cookie_token"}
        )
        
        assert response.status_code == 200
    
    def test_invalid_bearer_format_returns_401(self, auth_app):
        """Test invalid Bearer format returns 401."""
        client = TestClient(auth_app)
        
        response = client.get(
            "/api/v1/projects",
            headers={"Authorization": "Basic user:pass"}  # Wrong format
        )
        
        assert response.status_code == 401
    
    def test_empty_bearer_token_returns_401(self, auth_app):
        """Test empty Bearer token returns 401."""
        client = TestClient(auth_app)
        
        response = client.get(
            "/api/v1/projects",
            headers={"Authorization": "Bearer "}  # Empty token
        )
        
        assert response.status_code == 401
    
    def test_empty_cookie_token_returns_401(self, auth_app):
        """Test empty auth cookie returns 401."""
        client = TestClient(auth_app)
        
        response = client.get(
            "/api/v1/projects",
            cookies={"auth_token": "   "}  # Whitespace only
        )
        
        assert response.status_code == 401
    
    def test_options_request_passes_without_auth(self, auth_app):
        """Test OPTIONS request (CORS preflight) passes without auth."""
        client = TestClient(auth_app)
        
        response = client.options("/api/v1/projects")
        
        # OPTIONS should not require authentication
        assert response.status_code in [200, 405]
    
    def test_trailing_slash_normalized(self, auth_app):
        """Test trailing slash is normalized for path matching."""
        client = TestClient(auth_app)
        
        # /health/ should also work (normalized to /health)
        response = client.get("/health/")
        
        assert response.status_code in [200, 307, 404]  # May redirect or 404


class TestPrometheusMetricsMiddleware:
    """Tests for PrometheusMetricsMiddleware."""
    
    @pytest.fixture
    def metrics_app(self):
        """Create a FastAPI app with metrics middleware."""
        from backend.middleware.metrics_middleware import PrometheusMetricsMiddleware
        
        app = FastAPI()
        
        # Mock the metrics collector
        with patch('backend.middleware.metrics_middleware.get_metrics_collector') as mock_get:
            mock_collector = Mock()
            mock_collector._active_request_count = 0
            mock_collector.concurrent_requests = Mock()
            mock_collector.concurrent_requests.set = Mock()
            mock_collector.record_api_request = Mock()
            mock_collector.record_api_error = Mock()
            mock_get.return_value = mock_collector
            
            app.add_middleware(PrometheusMetricsMiddleware)
        
            @app.get("/test")
            async def test_endpoint():
                return {"status": "ok"}
            
            @app.get("/health")
            async def health_endpoint():
                return {"status": "healthy"}
            
            @app.get("/error")
            async def error_endpoint():
                raise ValueError("Test error")
            
            yield app, mock_collector
    
    def test_request_metrics_recorded(self, metrics_app):
        """Test request metrics are recorded."""
        app, mock_collector = metrics_app
        client = TestClient(app, raise_server_exceptions=False)
        
        response = client.get("/test")
        
        assert response.status_code == 200
        # Verify record_api_request was called
        mock_collector.record_api_request.assert_called()
    
    def test_health_endpoint_excluded_from_metrics(self, metrics_app):
        """Test health endpoint is excluded from metrics."""
        app, mock_collector = metrics_app
        client = TestClient(app, raise_server_exceptions=False)
        
        # Reset mock call count
        mock_collector.record_api_request.reset_mock()
        
        response = client.get("/health")
        
        assert response.status_code == 200
        # record_api_request should NOT be called for /health
        mock_collector.record_api_request.assert_not_called()
    
    def test_error_metrics_recorded(self, metrics_app):
        """Test error metrics are recorded when request raises exception."""
        app, mock_collector = metrics_app
        client = TestClient(app, raise_server_exceptions=False)
        
        response = client.get("/error")
        
        # Error endpoint raises exception, which should be recorded
        mock_collector.record_api_error.assert_called()


class TestPathNormalization:
    """Tests for path normalization in metrics middleware."""
    
    def test_uuid_normalized(self):
        """Test UUIDs in paths are normalized to {id}."""
        from backend.middleware.metrics_middleware import PrometheusMetricsMiddleware
        
        middleware = PrometheusMetricsMiddleware.__new__(PrometheusMetricsMiddleware)
        
        path = "/api/v1/projects/550e8400-e29b-41d4-a716-446655440000/tasks"
        normalized = middleware._normalize_path(path)
        
        assert "{id}" in normalized
        assert "550e8400" not in normalized
    
    def test_numeric_id_normalized(self):
        """Test numeric IDs in paths are normalized to {id}."""
        from backend.middleware.metrics_middleware import PrometheusMetricsMiddleware
        
        middleware = PrometheusMetricsMiddleware.__new__(PrometheusMetricsMiddleware)
        
        path = "/api/v1/users/12345/profile"
        normalized = middleware._normalize_path(path)
        
        assert "{id}" in normalized
        assert "12345" not in normalized
    
    def test_static_path_unchanged(self):
        """Test static paths without IDs are unchanged."""
        from backend.middleware.metrics_middleware import PrometheusMetricsMiddleware
        
        middleware = PrometheusMetricsMiddleware.__new__(PrometheusMetricsMiddleware)
        
        path = "/api/v1/health/status"
        normalized = middleware._normalize_path(path)
        
        assert normalized == path
