"""
Global authentication middleware for enterprise-grade security.

This middleware provides defense-in-depth by requiring authentication
on all non-public routes. Supports both Bearer token and httpOnly cookie
authentication. Route-level dependencies still perform the actual JWT validation.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.core.logging import get_correlation_id, get_logger

logger = get_logger(__name__)

# Public paths that don't require authentication
PUBLIC_PATHS: set[str] = {
    "/",
    "/health",
    "/ready",
    "/live",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/health",
    "/api/v1/health/simple",
    "/api/v1/ready",
    "/api/v1/live",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/auth/logout",  # Logout should be accessible to clear cookies
}

# Public path prefixes (paths starting with these are public)
PUBLIC_PREFIXES = (
    "/api/v1/health/",
    "/_next/",
    "/static/",
    "/metrics",
)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces authentication on all non-public routes.

    This provides a first-pass defense layer. Routes should still use
    Depends(get_current_user) for actual JWT token validation.

    Supports authentication via:
    - Authorization: Bearer <token> header
    - httpOnly auth_token cookie

    Features:
    - Whitelists known public paths (health checks, auth endpoints, docs)
    - Allows OPTIONS requests for CORS preflight
    - Handles WebSocket upgrade requests appropriately
    - Normalizes paths (strips trailing slashes) for consistent matching
    - Logs unauthorized access attempts with correlation IDs

    Example:
        >>> app.add_middleware(AuthenticationMiddleware)
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process request and enforce authentication.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response from handler or 401 error response
        """
        path = request.url.path

        # Normalize path (remove trailing slash for consistent matching)
        normalized_path = path.rstrip("/") if path != "/" else path

        # Allow public paths (exact match)
        if path in PUBLIC_PATHS or normalized_path in PUBLIC_PATHS:
            return await call_next(request)

        # Allow public path prefixes
        if any(path.startswith(prefix) for prefix in PUBLIC_PREFIXES):
            return await call_next(request)

        # Allow OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Allow WebSocket upgrade requests - they have their own auth handling
        # WebSocket auth is handled in get_websocket_user dependency
        upgrade_header = request.headers.get("upgrade", "").lower()
        if upgrade_header == "websocket":
            return await call_next(request)

        # Check for Authorization header first
        auth_header = request.headers.get("Authorization")

        # Check for httpOnly cookie as fallback
        auth_cookie = request.cookies.get("auth_token")

        if not auth_header and not auth_cookie:
            return self._unauthorized_response(
                request, "Missing authentication (no Authorization header or auth_token cookie)"
            )

        # Validate Bearer token format if header is present
        if auth_header:
            if not auth_header.startswith("Bearer "):
                return self._unauthorized_response(request, "Invalid Authorization header format")

            # Extract token (basic validation that it's not empty)
            token = auth_header[7:]  # Remove "Bearer " prefix
            if not token or token.isspace():
                return self._unauthorized_response(request, "Empty Bearer token")
        elif auth_cookie:
            # Validate cookie token is not empty
            if not auth_cookie or auth_cookie.isspace():
                return self._unauthorized_response(  # pragma: no cover
                    request, "Empty auth_token cookie"
                )

        # Token validation is handled by route-level dependencies
        # This middleware provides defense-in-depth
        response = await call_next(request)
        return response

    def _unauthorized_response(self, request: Request, reason: str) -> JSONResponse:
        """
        Create a 401 Unauthorized response.

        Args:
            request: The HTTP request
            reason: Reason for rejection (for logging)

        Returns:
            JSONResponse with 401 status
        """
        client_ip = self._get_client_ip(request)
        correlation_id = get_correlation_id()

        logger.warning(
            "Unauthorized request blocked by middleware",
            path=request.url.path,
            method=request.method,
            client_ip=client_ip,
            reason=reason,
            correlation_id=correlation_id,
        )

        return JSONResponse(
            status_code=401,
            content={
                "detail": "Authentication required",
                "error_code": "UNAUTHORIZED",
                "correlation_id": correlation_id,
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request.

        Checks X-Forwarded-For header first for proxied requests.

        Args:
            request: HTTP request

        Returns:
            Client IP address string
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return "unknown"
