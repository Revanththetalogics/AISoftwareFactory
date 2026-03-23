"""
Per-user rate limiting middleware using token bucket algorithm.

This middleware provides rate limiting functionality to protect API endpoints
from excessive requests. It supports different rate limits for different user types.
"""

import logging
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.core.config import get_settings
from backend.core.logging import get_correlation_id

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting per user with token bucket algorithm.

    This middleware tracks request counts per user within a time window
    and returns 429 Too Many Requests when limits are exceeded.

    Attributes:
        default_rate: Default requests per window for regular users
        admin_rate: Requests per window for admin users
        window_seconds: Time window duration in seconds
        buckets: Dictionary storing request counts per user

    Example:
        >>> app.add_middleware(
        ...     RateLimitMiddleware,
        ...     default_rate=100,
        ...     admin_rate=500,
        ...     window_seconds=60
        ... )
    """

    def __init__(
        self,
        app,
        default_rate: int = None,
        admin_rate: int = None,
        window_seconds: int = None,
    ):
        """
        Initialize the rate limit middleware.

        Args:
            app: ASGI application
            default_rate: Requests per window for regular users (default from config)
            admin_rate: Requests per window for admin users (default from config)
            window_seconds: Time window in seconds (default from config)
        """
        super().__init__(app)
        settings = get_settings()

        self.default_rate = default_rate or getattr(settings, 'RATE_LIMIT_DEFAULT', 100)
        self.admin_rate = admin_rate or getattr(settings, 'RATE_LIMIT_ADMIN', 500)
        self.window_seconds = window_seconds or getattr(settings, 'RATE_LIMIT_WINDOW_SECONDS', 60)

        # Format: {user_key: (request_count, window_start)}
        self.buckets: dict[str, tuple[int, float]] = defaultdict(lambda: (0, 0.0))

        logger.info(
            "Rate limit middleware initialized",
            extra={
                "default_rate": self.default_rate,
                "admin_rate": self.admin_rate,
                "window_seconds": self.window_seconds,
            }
        )

    def _get_user_key(self, request: Request) -> str:
        """
        Extract user identifier from request.

        Priority:
        1. JWT token hash (if Authorization header present)
        2. Client IP address (fallback)

        Args:
            request: The incoming request

        Returns:
            str: Unique identifier for rate limiting
        """
        # Try JWT user_id first
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # Use token hash as key (lightweight)
            token_prefix = auth_header[7:27]  # First 20 chars of token
            return f"token:{hash(token_prefix)}"

        # Fallback to IP
        client = request.client
        ip = client.host if client else "unknown"

        # Handle X-Forwarded-For for proxied requests
        forwarded_for = request.headers.get("X-Forwarded-For", "")
        if forwarded_for:
            # Take the first IP in the chain (original client)
            ip = forwarded_for.split(",")[0].strip()

        return f"ip:{ip}"

    def _get_rate_limit(self, request: Request) -> int:
        """
        Get rate limit for this request based on user role.

        Args:
            request: The incoming request

        Returns:
            int: Rate limit for this request
        """
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                import jwt as pyjwt
                token = auth_header[7:]
                payload = pyjwt.decode(token, options={"verify_signature": False})
                if payload.get("role") == "admin":
                    return self.admin_rate
            except Exception:  # noqa: S110
                pass
        return self.default_rate

    def _is_rate_limited(self, user_key: str, rate_limit: int) -> tuple[bool, int]:
        """
        Check if user is rate limited using sliding window algorithm.

        Args:
            user_key: User identifier
            rate_limit: Maximum requests allowed per window

        Returns:
            Tuple[bool, int]: (is_limited, remaining_requests)
        """
        now = time.time()
        count, window_start = self.buckets[user_key]

        if now - window_start > self.window_seconds:
            # New window - reset counter
            self.buckets[user_key] = (1, now)
            return False, rate_limit - 1

        if count >= rate_limit:
            return True, 0

        self.buckets[user_key] = (count + 1, window_start)
        return False, rate_limit - count - 1

    def _cleanup_old_buckets(self) -> None:
        """Remove expired bucket entries to prevent memory growth."""
        now = time.time()
        expired_keys = [
            key for key, (_, window_start) in self.buckets.items()
            if now - window_start > self.window_seconds * 2
        ]
        for key in expired_keys:
            del self.buckets[key]

    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.

        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain

        Returns:
            Response from handler or 429 error response
        """
        # Skip rate limiting for health checks and metrics
        path = request.url.path
        excluded_paths = (
            "/health", "/ready", "/live", "/metrics",
            "/api/v1/health", "/docs", "/redoc", "/openapi.json"
        )
        if path in excluded_paths:
            return await call_next(request)

        user_key = self._get_user_key(request)
        rate_limit = self._get_rate_limit(request)
        is_limited, remaining = self._is_rate_limited(user_key, rate_limit)

        # Periodic cleanup of old buckets
        if len(self.buckets) > 10000:
            self._cleanup_old_buckets()  # pragma: no cover

        if is_limited:
            request_id = get_correlation_id()
            retry_after = self.window_seconds

            logger.warning(
                "Rate limit exceeded",
                extra={
                    "user_key": user_key,
                    "path": path,
                    "rate_limit": rate_limit,
                    "request_id": request_id,
                }
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                        "details": {
                            "retry_after": retry_after,
                        },
                    },
                    "request_id": request_id,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after),
                }
            )

        response = await call_next(request)

        # Add rate limit headers to successful responses
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time()) + self.window_seconds
        )

        return response
