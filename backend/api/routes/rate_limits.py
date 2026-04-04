"""
Enhanced Rate Limiting API Endpoints.

Provides endpoints for configuring and monitoring rate limits.
"""

import time

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.middleware.rate_limit_middleware import RateLimitMiddleware

logger = get_logger(__name__)
router = APIRouter(prefix="/rate-limits", tags=["Rate Limits"])

# Global rate limit middleware instance (this would need to be shared)
rate_limit_middleware: RateLimitMiddleware | None = None


class RateLimitConfig(BaseModel):
    """Rate limit configuration model."""

    default_rate: int
    admin_rate: int
    window_seconds: int
    enabled: bool = True


class RateLimitInfo(BaseModel):
    """Rate limit information for a user/client."""

    user_key: str
    current_count: int
    rate_limit: int
    window_start: float
    window_end: float
    remaining_requests: int
    reset_time: float


class RateLimitUpdate(BaseModel):
    """Rate limit update request."""

    user_key: str
    new_limit: int
    duration_seconds: int | None = 3600  # 1 hour default


# In-memory storage for custom rate limits (would use Redis in production)
custom_limits: dict[str, tuple[int, float, int]] = {}  # user_key: (limit, expiration, original_limit)


@router.get("/config")
async def get_rate_limit_config():
    """Get current rate limit configuration."""
    if not rate_limit_middleware:
        raise HTTPException(status_code=503, detail="Rate limiting not configured")

    config = {
        "default_rate": rate_limit_middleware.default_rate,
        "admin_rate": rate_limit_middleware.admin_rate,
        "window_seconds": rate_limit_middleware.window_seconds,
        "active_buckets": len(rate_limit_middleware.buckets),
        "custom_limits_count": len(custom_limits),
    }

    return APIResponse(success=True, data=config, message="Rate limit configuration retrieved")


@router.put("/config")
async def update_rate_limit_config(config: RateLimitConfig):
    """Update global rate limit configuration."""
    global rate_limit_middleware

    if not rate_limit_middleware:
        raise HTTPException(status_code=503, detail="Rate limiting not configured")

    # Update configuration
    rate_limit_middleware.default_rate = config.default_rate
    rate_limit_middleware.admin_rate = config.admin_rate
    rate_limit_middleware.window_seconds = config.window_seconds

    logger.info(
        "Rate limit configuration updated",
        extra={
            "default_rate": config.default_rate,
            "admin_rate": config.admin_rate,
            "window_seconds": config.window_seconds,
        },
    )

    return APIResponse(success=True, data=config.dict(), message="Rate limit configuration updated successfully")


@router.get("/status")
async def get_rate_limit_status(
    user_key: str | None = Query(None, description="Filter by specific user key"),
    limit: int = Query(50, ge=1, le=1000, description="Number of entries to return"),
):
    """Get current rate limit status for all users or specific user."""
    if not rate_limit_middleware:
        raise HTTPException(status_code=503, detail="Rate limiting not configured")

    now = time.time()
    statuses = []

    # Get buckets to check
    buckets_to_check = (
        [(user_key, rate_limit_middleware.buckets[user_key])]
        if user_key
        else list(rate_limit_middleware.buckets.items())
    )

    for key, (count, window_start) in buckets_to_check[:limit]:
        # Determine rate limit for this user
        rate_limit = rate_limit_middleware.admin_rate if "admin" in key else rate_limit_middleware.default_rate

        # Check for custom limits
        if key in custom_limits:
            custom_limit, expiration, _ = custom_limits[key]
            if now < expiration:
                rate_limit = custom_limit

        window_end = window_start + rate_limit_middleware.window_seconds
        remaining = max(0, rate_limit - count)
        reset_time = window_start + rate_limit_middleware.window_seconds

        status = RateLimitInfo(
            user_key=key,
            current_count=count,
            rate_limit=rate_limit,
            window_start=window_start,
            window_end=window_end,
            remaining_requests=remaining,
            reset_time=reset_time,
        )
        statuses.append(status)

    return APIResponse(
        success=True,
        data={
            "statuses": [status.dict() for status in statuses],
            "total_active": len(rate_limit_middleware.buckets),
            "timestamp": now,
        },
        message="Rate limit status retrieved",
    )


@router.post("/adjust")
async def adjust_user_rate_limit(update: RateLimitUpdate):
    """Temporarily adjust rate limit for a specific user."""
    if not rate_limit_middleware:
        raise HTTPException(status_code=503, detail="Rate limiting not configured")

    now = time.time()
    expiration = now + update.duration_seconds

    # Store original limit if not already stored
    if update.user_key not in custom_limits:
        original_limit = (
            rate_limit_middleware.admin_rate if "admin" in update.user_key else rate_limit_middleware.default_rate
        )
        custom_limits[update.user_key] = (original_limit, 0, original_limit)  # expiration=0 means permanent

    # Set new custom limit
    custom_limits[update.user_key] = (update.new_limit, expiration, custom_limits[update.user_key][2])

    logger.info(
        "User rate limit adjusted",
        extra={
            "user_key": update.user_key,
            "new_limit": update.new_limit,
            "duration_seconds": update.duration_seconds,
            "expiration": expiration,
        },
    )

    return APIResponse(
        success=True,
        data={
            "user_key": update.user_key,
            "new_limit": update.new_limit,
            "expires_at": expiration,
            "duration_seconds": update.duration_seconds,
        },
        message=f"Rate limit for {update.user_key} adjusted to {update.new_limit} requests",
    )


@router.delete("/adjust/{user_key}")
async def remove_user_rate_adjustment(user_key: str):
    """Remove custom rate limit adjustment for a user."""
    if user_key in custom_limits:
        original_limit = custom_limits[user_key][2]
        del custom_limits[user_key]

        logger.info("User rate limit adjustment removed", extra={"user_key": user_key})

        return APIResponse(
            success=True,
            data={"user_key": user_key, "restored_limit": original_limit},
            message=f"Rate limit adjustment removed for {user_key}",
        )

    raise HTTPException(status_code=404, detail=f"No custom rate limit found for {user_key}")


@router.get("/top-users")
async def get_top_rate_limited_users(limit: int = Query(10, ge=1, le=100, description="Number of users to return")):
    """Get users with highest request counts."""
    if not rate_limit_middleware:
        raise HTTPException(status_code=503, detail="Rate limiting not configured")

    now = time.time()
    user_stats = []

    for user_key, (count, window_start) in rate_limit_middleware.buckets.items():
        # Determine rate limit
        rate_limit = rate_limit_middleware.admin_rate if "admin" in user_key else rate_limit_middleware.default_rate

        # Check custom limits
        if user_key in custom_limits:
            custom_limit, expiration, _ = custom_limits[user_key]
            if now < expiration:
                rate_limit = custom_limit

        utilization = (count / rate_limit) * 100 if rate_limit > 0 else 0
        window_age = now - window_start

        user_stats.append(
            {
                "user_key": user_key,
                "request_count": count,
                "rate_limit": rate_limit,
                "utilization_percent": round(utilization, 2),
                "window_age_seconds": round(window_age, 2),
                "is_near_limit": utilization > 80,
            }
        )

    # Sort by utilization and take top users
    user_stats.sort(key=lambda x: x["utilization_percent"], reverse=True)
    top_users = user_stats[:limit]

    return APIResponse(
        success=True,
        data={"top_users": top_users, "total_monitored": len(rate_limit_middleware.buckets), "timestamp": now},
        message="Top rate limited users retrieved",
    )


@router.post("/reset/{user_key}")
async def reset_user_rate_limit(user_key: str):
    """Reset rate limit counter for a specific user."""
    if not rate_limit_middleware:
        raise HTTPException(status_code=503, detail="Rate limiting not configured")

    if user_key in rate_limit_middleware.buckets:
        del rate_limit_middleware.buckets[user_key]

        logger.info("User rate limit reset", extra={"user_key": user_key})

        return APIResponse(
            success=True, data={"user_key": user_key}, message=f"Rate limit counter reset for {user_key}"
        )

    raise HTTPException(status_code=404, detail=f"No rate limit data found for {user_key}")


@router.get("/statistics")
async def get_rate_limit_statistics():
    """Get comprehensive rate limiting statistics."""
    if not rate_limit_middleware:
        raise HTTPException(status_code=503, detail="Rate limiting not configured")

    now = time.time()
    total_buckets = len(rate_limit_middleware.buckets)

    # Calculate statistics
    near_limit_count = 0
    exceeded_count = 0
    total_requests = 0

    for user_key, (count, _window_start) in rate_limit_middleware.buckets.items():
        # Determine applicable rate limit
        rate_limit = rate_limit_middleware.admin_rate if "admin" in user_key else rate_limit_middleware.default_rate

        # Check custom limits
        if user_key in custom_limits:
            custom_limit, expiration, _ = custom_limits[user_key]
            if now < expiration:
                rate_limit = custom_limit

        utilization = count / rate_limit if rate_limit > 0 else 0
        total_requests += count

        if utilization >= 1.0:
            exceeded_count += 1
        elif utilization >= 0.8:
            near_limit_count += 1

    stats = {
        "total_active_users": total_buckets,
        "total_requests_tracked": total_requests,
        "users_near_limit": near_limit_count,
        "users_exceeded_limit": exceeded_count,
        "custom_rate_limits": len(custom_limits),
        "default_rate": rate_limit_middleware.default_rate,
        "admin_rate": rate_limit_middleware.admin_rate,
        "window_seconds": rate_limit_middleware.window_seconds,
        "timestamp": now,
    }

    return APIResponse(success=True, data=stats, message="Rate limit statistics retrieved")


# Utility function to set the middleware instance
def set_rate_limit_middleware(middleware: RateLimitMiddleware):
    """Set the global rate limit middleware instance."""
    global rate_limit_middleware
    rate_limit_middleware = middleware
