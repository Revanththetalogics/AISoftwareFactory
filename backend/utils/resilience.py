"""
Resilience utilities for enterprise-grade fault tolerance.

This module provides circuit breaker pattern, timeout utilities,
and resilience wrappers for external service calls.
"""

import asyncio
import functools
import time
from typing import Any, Callable, Optional, TypeVar

from backend.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and call is rejected."""
    pass


class CircuitBreaker:
    """
    Circuit breaker for external service calls.

    Implements the circuit breaker pattern to prevent cascading failures
    when external services are unavailable.

    States:
        - closed: Normal operation, requests pass through
        - open: Service is failing, requests are rejected immediately
        - half-open: Testing if service recovered, limited requests allowed

    Attributes:
        name: Identifier for this circuit breaker
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery

    Example:
        >>> cb = CircuitBreaker("llm_provider", failure_threshold=3, recovery_timeout=60.0)
        >>> result = await cb.call(some_async_func, arg1, arg2)
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Identifier for logging and metrics
            failure_threshold: Failures before opening (default: 5)
            recovery_timeout: Seconds before half-open test (default: 30.0)
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: float = 0
        self.state = "closed"  # closed, open, half-open
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function through the circuit breaker.

        Args:
            func: Async function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Result from the function

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Any exception from the wrapped function
        """
        async with self._lock:
            if self.state == "open":
                if (time.time() - self.last_failure_time) > self.recovery_timeout:
                    self.state = "half-open"
                    logger.info(
                        "Circuit breaker entering half-open state",
                        circuit_name=self.name
                    )
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is open"
                    )

        try:
            result = await func(*args, **kwargs)

            async with self._lock:
                if self.state == "half-open":
                    self.state = "closed"
                    self.failure_count = 0
                    logger.info(
                        "Circuit breaker closed (recovered)",
                        circuit_name=self.name
                    )

            return result

        except Exception as e:
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
                    logger.warning(
                        "Circuit breaker opened",
                        circuit_name=self.name,
                        failure_count=self.failure_count,
                        error=str(e)
                    )
            raise

    def get_state_value(self) -> int:
        """
        Get numeric state for metrics.

        Returns:
            0 for closed, 1 for half-open, 2 for open
        """
        state_map = {"closed": 0, "half-open": 1, "open": 2}
        return state_map.get(self.state, 0)

    def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        self.state = "closed"
        self.failure_count = 0
        self.last_failure_time = 0
        logger.info("Circuit breaker reset", circuit_name=self.name)


# Pre-configured circuit breakers for external services
llm_circuit_breaker = CircuitBreaker(
    "llm_provider",
    failure_threshold=3,
    recovery_timeout=60.0
)

db_circuit_breaker = CircuitBreaker(
    "database",
    failure_threshold=5,
    recovery_timeout=30.0
)

external_http_circuit_breaker = CircuitBreaker(
    "external_http",
    failure_threshold=5,
    recovery_timeout=45.0
)


async def with_timeout(
    coro,
    timeout_seconds: float,
    operation_name: str = "operation"
) -> Any:
    """
    Execute a coroutine with timeout.

    Args:
        coro: Coroutine to execute
        timeout_seconds: Maximum execution time in seconds
        operation_name: Name for logging (default: "operation")

    Returns:
        Result from the coroutine

    Raises:
        TimeoutError: If operation exceeds timeout

    Example:
        >>> result = await with_timeout(
        ...     some_async_func(),
        ...     timeout_seconds=30.0,
        ...     operation_name="LLM completion"
        ... )
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.error(
            "Operation timed out",
            operation=operation_name,
            timeout_seconds=timeout_seconds
        )
        raise TimeoutError(f"{operation_name} timed out after {timeout_seconds}s")


async def with_resilience(
    func: Callable,
    circuit_breaker: CircuitBreaker,
    timeout_seconds: Optional[float] = None,
    operation_name: str = "operation",
    *args,
    **kwargs
) -> Any:
    """
    Execute a function with circuit breaker and optional timeout.

    Combines circuit breaker protection with timeout for comprehensive
    resilience against external service failures.

    Args:
        func: Async function to execute
        circuit_breaker: Circuit breaker instance to use
        timeout_seconds: Optional timeout (None means no timeout)
        operation_name: Name for logging
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Result from the function

    Raises:
        CircuitBreakerOpenError: If circuit is open
        TimeoutError: If operation times out
        Exception: Any exception from the wrapped function

    Example:
        >>> result = await with_resilience(
        ...     llm_client.generate,
        ...     llm_circuit_breaker,
        ...     timeout_seconds=30.0,
        ...     operation_name="LLM generation",
        ...     prompt="Hello"
        ... )
    """
    async def wrapped():
        return await func(*args, **kwargs)

    # Apply circuit breaker
    async def cb_wrapped():
        return await circuit_breaker.call(wrapped)

    # Apply timeout if specified
    if timeout_seconds is not None:
        return await with_timeout(
            cb_wrapped(),
            timeout_seconds,
            operation_name
        )
    else:
        return await cb_wrapped()


def resilient(
    circuit_breaker: CircuitBreaker,
    timeout_seconds: Optional[float] = None,
    operation_name: Optional[str] = None
):
    """
    Decorator to add resilience to async functions.

    Args:
        circuit_breaker: Circuit breaker to use
        timeout_seconds: Optional timeout in seconds
        operation_name: Name for logging (defaults to function name)

    Returns:
        Decorated function

    Example:
        >>> @resilient(llm_circuit_breaker, timeout_seconds=30.0)
        ... async def call_llm(prompt: str) -> str:
        ...     return await llm_client.generate(prompt)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            return await with_resilience(
                func,
                circuit_breaker,
                timeout_seconds,
                op_name,
                *args,
                **kwargs
            )
        return wrapper
    return decorator
