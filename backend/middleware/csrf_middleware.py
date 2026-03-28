"""
CSRF Protection Middleware for AI Software Factory.

Implements the Double Submit Cookie pattern for CSRF protection:
- On GET requests: Sets a CSRF token in both a cookie and response header
- On state-changing requests: Validates that the token from header matches the cookie

This approach is suitable for SPA + API architecture with httpOnly session cookies.
The SameSite=Lax cookie attribute provides the primary CSRF defense.
"""

import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from backend.core.logging import get_logger

logger = get_logger(__name__)

# CSRF token configuration
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_TOKEN_LENGTH = 32

# Paths exempt from CSRF protection
CSRF_EXEMPT_PATHS: set[str] = {
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
    "/api/v1/auth/register",
    "/api/v1/codegen/generate",  # Temporarily exempt for development
    "/api/v1/codegen/validate",  # Temporarily exempt for development
    "/api/v1/codegen/history",   # Temporarily exempt for development
    "/api/v1/codegen/languages", # Temporarily exempt for development
}

# Path prefixes exempt from CSRF protection
CSRF_EXEMPT_PREFIXES: tuple[str, ...] = (
    "/api/v1/health/",
    "/api/v1/webhooks/",  # Webhooks typically have their own auth
    "/_next/",
    "/static/",
    "/metrics",
)

# Methods that require CSRF validation (state-changing)
CSRF_PROTECTED_METHODS: set[str] = {"POST", "PUT", "PATCH", "DELETE"}


def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token."""
    return secrets.token_hex(CSRF_TOKEN_LENGTH)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection middleware using Double Submit Cookie pattern.

    For GET/HEAD/OPTIONS requests:
    - Generates a new CSRF token if none exists
    - Sets the token in a cookie and X-CSRF-Token response header

    For POST/PUT/PATCH/DELETE requests:
    - If using Bearer token auth: CSRF is bypassed (token auth is CSRF-immune)
    - If using cookie auth: Validates X-CSRF-Token header matches csrf_token cookie
    - Returns 403 Forbidden if validation fails for cookie-based auth

    The frontend should:
    1. Read the X-CSRF-Token from response headers
    2. Include it in subsequent state-changing requests when using cookie auth

    Example:
        >>> app.add_middleware(CSRFMiddleware)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with CSRF protection.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response with CSRF token or 403 error
        """
        path = request.url.path
        method = request.method

        # Check if path is exempt
        if self._is_exempt(path):
            return await call_next(request)

        # Allow OPTIONS (CORS preflight)
        if method == "OPTIONS":
            return await call_next(request)

        # Allow WebSocket upgrades
        if request.headers.get("upgrade", "").lower() == "websocket":
            return await call_next(request)

        # For state-changing methods, validate CSRF token
        if method in CSRF_PROTECTED_METHODS:
            # Skip CSRF validation if using Bearer token auth
            # Bearer tokens are inherently CSRF-immune as they must be explicitly
            # included in the request header
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                # Using Bearer token - no CSRF validation needed
                pass
            elif not self._validate_csrf(request):
                logger.warning(
                    "CSRF validation failed",
                    path=path,
                    method=method,
                    client_ip=self._get_client_ip(request),
                )
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "CSRF validation failed",
                        "error_code": "CSRF_INVALID",
                    }
                )

        # Process request
        response = await call_next(request)

        # For safe methods, ensure CSRF token is set
        if method in ("GET", "HEAD"):
            self._set_csrf_token(request, response)

        return response

    def _is_exempt(self, path: str) -> bool:
        """Check if path is exempt from CSRF protection."""
        # Normalize path
        normalized_path = path.rstrip("/") if path != "/" else path

        # Check exact matches
        if path in CSRF_EXEMPT_PATHS or normalized_path in CSRF_EXEMPT_PATHS:
            return True

        # Check prefix matches
        if any(path.startswith(prefix) for prefix in CSRF_EXEMPT_PREFIXES):
            return True

        return False

    def _validate_csrf(self, request: Request) -> bool:
        """
        Validate CSRF token using Double Submit Cookie pattern.

        Args:
            request: HTTP request

        Returns:
            True if validation passes, False otherwise
        """
        # Get token from cookie
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        if not cookie_token:
            logger.debug("CSRF cookie not found")
            return False

        # Get token from header
        header_token = request.headers.get(CSRF_HEADER_NAME)
        if not header_token:
            logger.debug("CSRF header not found")
            return False

        # Compare tokens (constant-time comparison)
        if not secrets.compare_digest(cookie_token, header_token):
            logger.debug("CSRF tokens do not match")
            return False

        return True

    def _set_csrf_token(self, request: Request, response: Response) -> None:
        """
        Set CSRF token in cookie and response header.

        Args:
            request: HTTP request (for scheme detection)
            response: HTTP response to modify
        """
        # Check if token already exists in cookie
        existing_token = request.cookies.get(CSRF_COOKIE_NAME)

        if existing_token:
            # Use existing token
            token = existing_token
        else:
            # Generate new token
            token = generate_csrf_token()

        # Determine if secure flag should be set
        is_secure = request.url.scheme == "https"

        # Set token in cookie (accessible to JavaScript for header inclusion)
        response.set_cookie(
            key=CSRF_COOKIE_NAME,
            value=token,
            httponly=False,  # Must be readable by JavaScript
            secure=is_secure,
            samesite="lax",
            max_age=3600,  # 1 hour
            path="/"
        )

        # Set token in response header
        response.headers[CSRF_HEADER_NAME] = token

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        if request.client:
            return request.client.host

        return "unknown"
