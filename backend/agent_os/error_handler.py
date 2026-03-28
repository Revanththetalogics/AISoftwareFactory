"""
Error handler for AgentOS.

This module provides failure recovery with retry logic, escalation,
and circuit breaker pattern.
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RetryConfig:
    """Retry configuration."""
    max_retries: int = 3
    backoff_base: float = 1.0
    backoff_max: float = 60.0
    exponential: bool = True


class CircuitBreaker:
    """Circuit breaker for fault tolerance."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0
    ):
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._last_failure: datetime | None = None

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self._state == CircuitState.CLOSED:
            return True

        if self._state == CircuitState.OPEN:
            if self._last_failure and \
               (datetime.now(UTC) - self._last_failure).total_seconds() > self._recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                return True
            return False

        return True  # HALF_OPEN

    def record_success(self):
        """Record a successful execution."""
        self._failures = 0
        self._state = CircuitState.CLOSED

    def record_failure(self):
        """Record a failed execution."""
        self._failures += 1
        self._last_failure = datetime.now(UTC)

        if self._failures >= self._failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning("Circuit breaker opened")


class ErrorHandler:
    """
    Error handler for agent execution.

    Provides retry with backoff, escalation to human-in-the-loop,
    and circuit breaker pattern.
    """

    def __init__(self):
        """Initialize the error handler."""
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self._logger = get_logger(__name__)

    async def execute_with_retry(
        self,
        operation: Callable,
        config: RetryConfig | None = None,
        circuit_name: str | None = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute an operation with retry logic.

        Args:
            operation: Function to execute
            config: Retry configuration
            circuit_name: Circuit breaker name
            *args: Operation arguments
            **kwargs: Operation keyword arguments

        Returns:
            Operation result

        Raises:
            Exception: If all retries fail
        """
        config = config or RetryConfig()

        # Check circuit breaker
        if circuit_name:
            cb = self._circuit_breakers.get(circuit_name)
            if not cb:
                cb = CircuitBreaker()
                self._circuit_breakers[circuit_name] = cb

            if not cb.can_execute():
                raise Exception(f"Circuit breaker open for {circuit_name}")

        last_exception = None

        for attempt in range(config.max_retries + 1):
            try:
                result = await operation(*args, **kwargs)

                if circuit_name:
                    self._circuit_breakers[circuit_name].record_success()

                return result

            except Exception as e:
                last_exception = e
                self._logger.warning(
                    "Operation failed",
                    attempt=attempt + 1,
                    max_retries=config.max_retries,
                    error=str(e)
                )

                if attempt < config.max_retries:
                    # Calculate backoff
                    if config.exponential:
                        delay = min(
                            config.backoff_base * (2 ** attempt),
                            config.backoff_max
                        )
                    else:
                        delay = config.backoff_base

                    await asyncio.sleep(delay)

        # All retries failed
        if circuit_name:
            self._circuit_breakers[circuit_name].record_failure()

        raise last_exception

    def escalate_to_human(
        self,
        task_id: str,
        error: Exception,
        context: dict[str, Any] | None = None
    ):
        """
        Escalate an error to human-in-the-loop.

        Args:
            task_id: Task ID
            error: Exception that occurred
            context: Additional context
        """
        self._logger.error(
            "Escalating to human",
            task_id=task_id,
            error=str(error),
            context=context
        )
        # Write to structured escalation log
        try:
            import json
            from datetime import datetime
            from pathlib import Path
            log_entry = {
                "task_id": task_id,
                "error": str(error),
                "context": context,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            with open(reports_dir / "escalations.jsonl", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as log_exc:
            self._logger.warning("Failed to write escalation log", error=str(log_exc))
        # Attempt webhook if configured
        try:
            from backend.core.config import get_settings
            webhook_url = getattr(get_settings(), "ESCALATION_WEBHOOK_URL", None)
            if webhook_url:
                import asyncio

                import httpx
                async def _send():
                    async with httpx.AsyncClient() as client:
                        await client.post(webhook_url, json=log_entry, timeout=5.0)
                asyncio.get_event_loop().create_task(_send())
        except Exception as we:
            self._logger.warning("Webhook escalation failed", error=str(we))
