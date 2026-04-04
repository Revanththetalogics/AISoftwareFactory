"""
Tests for Resilience utilities.

Tests for CircuitBreaker, with_timeout, with_resilience, and @resilient decorator.
"""

import asyncio
import time

import pytest

from backend.utils.resilience import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    db_circuit_breaker,
    external_http_circuit_breaker,
    llm_circuit_breaker,
    resilient,
    with_resilience,
    with_timeout,
)


class TestCircuitBreaker:
    """Test cases for CircuitBreaker."""

    def test_init(self):
        """Test circuit breaker initialization."""
        cb = CircuitBreaker("test", failure_threshold=3, recovery_timeout=10.0)

        assert cb.name == "test"
        assert cb.failure_threshold == 3
        assert cb.recovery_timeout == 10.0
        assert cb.failure_count == 0
        assert cb.state == "closed"
        assert cb.last_failure_time == 0

    def test_init_defaults(self):
        """Test circuit breaker default values."""
        cb = CircuitBreaker("default")

        assert cb.failure_threshold == 5
        assert cb.recovery_timeout == 30.0

    @pytest.mark.asyncio
    async def test_call_success(self):
        """Test successful call through circuit breaker."""
        cb = CircuitBreaker("test", failure_threshold=3)

        async def success_func():
            return "success"

        result = await cb.call(success_func)

        assert result == "success"
        assert cb.state == "closed"
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_call_failure_increments_count(self):
        """Test that failures increment the failure count."""
        cb = CircuitBreaker("test", failure_threshold=3)

        async def fail_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await cb.call(fail_func)

        assert cb.failure_count == 1
        assert cb.state == "closed"

    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self):
        """Test that circuit opens after failure threshold is reached."""
        cb = CircuitBreaker("test", failure_threshold=3)

        async def fail_func():
            raise ValueError("Test error")

        # Cause failures up to threshold
        for _ in range(3):
            with pytest.raises(ValueError):
                await cb.call(fail_func)

        assert cb.state == "open"
        assert cb.failure_count == 3

    @pytest.mark.asyncio
    async def test_open_circuit_rejects_calls(self):
        """Test that open circuit rejects calls."""
        cb = CircuitBreaker("test", failure_threshold=1, recovery_timeout=60.0)

        async def fail_func():
            raise ValueError("Test error")

        # Trigger circuit open
        with pytest.raises(ValueError):
            await cb.call(fail_func)

        assert cb.state == "open"

        # Next call should be rejected
        async def success_func():
            return "success"

        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            await cb.call(success_func)

        assert "is open" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_half_open_after_timeout(self):
        """Test circuit enters half-open after recovery timeout."""
        cb = CircuitBreaker("test", failure_threshold=1, recovery_timeout=0.1)

        async def fail_func():
            raise ValueError("Test error")

        # Trigger circuit open
        with pytest.raises(ValueError):
            await cb.call(fail_func)

        assert cb.state == "open"

        # Wait for recovery timeout
        await asyncio.sleep(0.15)

        # Next call should be allowed (half-open)
        async def success_func():
            return "success"

        result = await cb.call(success_func)

        assert result == "success"
        assert cb.state == "closed"
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_half_open_failure_reopens(self):
        """Test that failure in half-open state reopens circuit."""
        cb = CircuitBreaker("test", failure_threshold=1, recovery_timeout=0.1)

        async def fail_func():
            raise ValueError("Test error")

        # Trigger circuit open
        with pytest.raises(ValueError):
            await cb.call(fail_func)

        # Wait for recovery timeout
        await asyncio.sleep(0.15)

        # Fail in half-open state
        with pytest.raises(ValueError):
            await cb.call(fail_func)

        # Circuit should be open again
        assert cb.state == "open"

    def test_get_state_value(self):
        """Test get_state_value returns correct numeric values."""
        cb = CircuitBreaker("test")

        cb.state = "closed"
        assert cb.get_state_value() == 0

        cb.state = "half-open"
        assert cb.get_state_value() == 1

        cb.state = "open"
        assert cb.get_state_value() == 2

        cb.state = "unknown"
        assert cb.get_state_value() == 0  # Default

    def test_reset(self):
        """Test reset method."""
        cb = CircuitBreaker("test")
        cb.state = "open"
        cb.failure_count = 5
        cb.last_failure_time = time.time()

        cb.reset()

        assert cb.state == "closed"
        assert cb.failure_count == 0
        assert cb.last_failure_time == 0


class TestPreConfiguredCircuitBreakers:
    """Test pre-configured circuit breakers."""

    def test_llm_circuit_breaker(self):
        """Test LLM circuit breaker configuration."""
        assert llm_circuit_breaker.name == "llm_provider"
        assert llm_circuit_breaker.failure_threshold == 3
        assert llm_circuit_breaker.recovery_timeout == 60.0

    def test_db_circuit_breaker(self):
        """Test database circuit breaker configuration."""
        assert db_circuit_breaker.name == "database"
        assert db_circuit_breaker.failure_threshold == 5
        assert db_circuit_breaker.recovery_timeout == 30.0

    def test_external_http_circuit_breaker(self):
        """Test external HTTP circuit breaker configuration."""
        assert external_http_circuit_breaker.name == "external_http"
        assert external_http_circuit_breaker.failure_threshold == 5
        assert external_http_circuit_breaker.recovery_timeout == 45.0


class TestWithTimeout:
    """Test cases for with_timeout function."""

    @pytest.mark.asyncio
    async def test_success_within_timeout(self):
        """Test successful completion within timeout."""

        async def quick_func():
            return "quick result"

        result = await with_timeout(quick_func(), 1.0, "quick_op")

        assert result == "quick result"

    @pytest.mark.asyncio
    async def test_timeout_exceeded(self):
        """Test that timeout raises TimeoutError."""

        async def slow_func():
            await asyncio.sleep(1.0)
            return "slow result"

        with pytest.raises(TimeoutError) as exc_info:
            await with_timeout(slow_func(), 0.1, "slow_op")

        assert "slow_op" in str(exc_info.value)
        assert "0.1s" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_default_operation_name(self):
        """Test timeout with default operation name."""

        async def slow_func():
            await asyncio.sleep(1.0)

        with pytest.raises(TimeoutError) as exc_info:
            await with_timeout(slow_func(), 0.1)

        assert "operation" in str(exc_info.value)


class TestWithResilience:
    """Test cases for with_resilience function."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Test successful call with resilience."""
        cb = CircuitBreaker("test", failure_threshold=3)

        async def success_func():
            return "result: success"

        result = await with_resilience(success_func, cb, timeout_seconds=5.0, operation_name="test_op")

        assert result == "result: success"

    @pytest.mark.asyncio
    async def test_without_timeout(self):
        """Test with_resilience without timeout."""
        cb = CircuitBreaker("test", failure_threshold=3)

        async def success_func():
            return "no timeout"

        result = await with_resilience(success_func, cb, timeout_seconds=None, operation_name="test_op")

        assert result == "no timeout"

    @pytest.mark.asyncio
    async def test_circuit_breaker_open(self):
        """Test with_resilience when circuit is open."""
        cb = CircuitBreaker("test", failure_threshold=1, recovery_timeout=60.0)

        async def fail_func():
            raise ValueError("Fail")

        # Trip the circuit
        with pytest.raises(ValueError):
            await with_resilience(fail_func, cb)

        # Now circuit should be open
        async def success_func():
            return "success"

        with pytest.raises(CircuitBreakerOpenError):
            await with_resilience(success_func, cb)

    @pytest.mark.asyncio
    async def test_timeout_in_resilience(self):
        """Test timeout within with_resilience."""
        cb = CircuitBreaker("test", failure_threshold=5)

        async def slow_func():
            await asyncio.sleep(1.0)
            return "slow"

        with pytest.raises(TimeoutError):
            await with_resilience(slow_func, cb, timeout_seconds=0.1, operation_name="slow_op")


class TestResilientDecorator:
    """Test cases for @resilient decorator."""

    @pytest.mark.asyncio
    async def test_decorator_success(self):
        """Test resilient decorator with successful call."""
        cb = CircuitBreaker("test", failure_threshold=3)

        @resilient(cb)
        async def decorated_func(x, y):
            return x + y

        result = await decorated_func(1, 2)

        assert result == 3

    @pytest.mark.asyncio
    async def test_decorator_with_timeout(self):
        """Test resilient decorator with timeout."""
        cb = CircuitBreaker("test", failure_threshold=3)

        @resilient(cb, timeout_seconds=0.1)
        async def slow_decorated():
            await asyncio.sleep(1.0)
            return "done"

        with pytest.raises(TimeoutError):
            await slow_decorated()

    @pytest.mark.asyncio
    async def test_decorator_with_operation_name(self):
        """Test resilient decorator with custom operation name."""
        cb = CircuitBreaker("test", failure_threshold=3)

        @resilient(cb, timeout_seconds=0.1, operation_name="custom_op")
        async def slow_decorated():
            await asyncio.sleep(1.0)
            return "done"

        with pytest.raises(TimeoutError) as exc_info:
            await slow_decorated()

        assert "custom_op" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_decorator_uses_func_name_as_default(self):
        """Test that decorator uses function name as default operation name."""
        cb = CircuitBreaker("test", failure_threshold=3)

        @resilient(cb, timeout_seconds=0.1)
        async def my_special_function():
            await asyncio.sleep(1.0)
            return "done"

        with pytest.raises(TimeoutError) as exc_info:
            await my_special_function()

        assert "my_special_function" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function metadata."""
        cb = CircuitBreaker("test")

        @resilient(cb)
        async def documented_func():
            """This is documentation."""
            return "result"

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This is documentation."

    @pytest.mark.asyncio
    async def test_decorator_circuit_breaker_trips(self):
        """Test that decorated function trips circuit breaker on failures."""
        cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout=60.0)

        @resilient(cb)
        async def failing_func():
            raise RuntimeError("Always fails")

        # Cause failures
        for _ in range(2):
            with pytest.raises(RuntimeError):
                await failing_func()

        # Circuit should be open now
        assert cb.state == "open"

        # Next call should raise CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            await failing_func()


class TestCircuitBreakerOpenError:
    """Test CircuitBreakerOpenError exception."""

    def test_exception_message(self):
        """Test exception can be raised with message."""
        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            raise CircuitBreakerOpenError("Test circuit is open")

        assert "Test circuit is open" in str(exc_info.value)

    def test_exception_inheritance(self):
        """Test exception inherits from Exception."""
        assert issubclass(CircuitBreakerOpenError, Exception)
