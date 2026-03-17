"""
Error handler for AgentOS.

This module provides failure recovery with retry logic, escalation,
and circuit breaker pattern.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional, Any
from enum import Enum

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
        self._last_failure: Optional[datetime] = None
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self._state == CircuitState.CLOSED:
            return True
        
        if self._state == CircuitState.OPEN:
            if self._last_failure and \
               (datetime.utcnow() - self._last_failure).total_seconds() > self._recovery_timeout:
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
        self._last_failure = datetime.utcnow()
        
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
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._logger = get_logger(__name__)
    
    async def execute_with_retry(
        self,
        operation: Callable,
        config: Optional[RetryConfig] = None,
        circuit_name: Optional[str] = None,
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
        context: Optional[Dict[str, Any]] = None
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
        # TODO: Implement actual escalation (email, notification, etc.)
