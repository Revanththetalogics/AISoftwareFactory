"""
Structured logging configuration for AI Software Factory backend.

This module provides enterprise-grade structured JSON logging with correlation IDs
for request tracing, enabling better observability and debugging in production.
"""

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

import structlog
from pythonjsonlogger import jsonlogger

from backend.core.config import get_settings

# Context variable for correlation ID across async boundaries
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """
    Get the current correlation ID from context.
    
    Returns:
        str: Current correlation ID or empty string if not set
    """
    return correlation_id.get("")


def set_correlation_id(cid: Optional[str] = None) -> str:
    """
    Set or generate a correlation ID.
    
    Args:
        cid: Optional correlation ID to set. If None, generates a new UUID.
        
    Returns:
        str: The correlation ID that was set
        
    Example:
        >>> set_correlation_id()
        '550e8400-e29b-41d4-a716-446655440000'
        >>> set_correlation_id("custom-id")
        'custom-id'
    """
    cid = cid or str(uuid.uuid4())
    correlation_id.set(cid)
    return cid


def clear_correlation_id() -> None:
    """Clear the current correlation ID from context."""
    correlation_id.set("")


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter that adds correlation ID and trace context to log records.
    
    This filter ensures all log records include the current correlation ID
    and OpenTelemetry trace/span IDs for request tracing across the application.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID and trace context to log record."""
        record.correlation_id = get_correlation_id()
        
        # Add OpenTelemetry trace context if available
        try:
            from backend.infrastructure.tracing import get_current_trace_id, get_current_span_id
            record.trace_id = get_current_trace_id() or ""
            record.span_id = get_current_span_id() or ""
        except Exception:
            record.trace_id = ""
            record.span_id = ""
        
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for structured logging.
    
    Formats log records as JSON with standardized fields for log aggregation
    and analysis in production environments.
    """
    
    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record["timestamp"] = record.created
        
        # Add log level
        log_record["level"] = record.levelname
        
        # Add logger name
        log_record["logger"] = record.name
        
        # Add correlation ID for request tracing
        log_record["correlation_id"] = getattr(record, "correlation_id", "")
        
        # Add OpenTelemetry trace context for distributed tracing
        log_record["trace_id"] = getattr(record, "trace_id", "")
        log_record["span_id"] = getattr(record, "span_id", "")
        
        # Add source location
        log_record["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }
        
        # Rename 'message' to 'msg' for consistency
        if "message" in log_record:
            log_record["msg"] = log_record.pop("message")


def configure_logging() -> None:
    """
    Configure structured logging for the application.
    
    This function sets up both standard library logging and structlog
    for consistent structured JSON output across the application.
    
    The configuration includes:
    - JSON formatting for production log aggregation
    - Correlation ID injection for request tracing
    - Appropriate log levels based on environment
    - Console output for development
    
    Example:
        >>> configure_logging()
        >>> import logging
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Application started")
        {"timestamp": 1234567890.123, "level": "INFO", "msg": "Application started", ...}
    """
    settings = get_settings()
    
    # Get log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
    
    # Configure standard library logging
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Add correlation ID filter
    console_handler.addFilter(CorrelationIdFilter())
    
    if settings.is_development or settings.is_testing:
        # Use human-readable format for development
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(trace_id)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # Use JSON format for production
        formatter = CustomJsonFormatter(
            fmt="%(timestamp)s %(level)s %(name)s %(message)s",
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if not settings.is_development else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name, typically __name__
        
    Returns:
        BoundLogger: Structured logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request", user_id=123)
        {"event": "Processing request", "user_id": 123, ...}
    """
    return structlog.get_logger(name)


class LoggingContext:
    """
    Context manager for temporary logging context.
    
    This is useful for adding context to logs within a specific scope,
    such as a request handler or background task.
    
    Attributes:
        logger: The logger to bind context to
        context: Dictionary of context key-value pairs
        
    Example:
        >>> logger = get_logger(__name__)
        >>> with LoggingContext(logger, request_id="123", user_id="456"):
        ...     logger.info("Processing")  # Includes request_id and user_id
    """
    
    def __init__(self, logger: structlog.stdlib.BoundLogger, **context: Any):
        """
        Initialize logging context.
        
        Args:
            logger: Logger to bind context to
            **context: Key-value pairs to add to log context
        """
        self.logger = logger
        self.context = context
        self.bound_logger: Optional[structlog.stdlib.BoundLogger] = None
    
    def __enter__(self) -> structlog.stdlib.BoundLogger:
        """Enter context and bind logger."""
        self.bound_logger = self.logger.bind(**self.context)
        return self.bound_logger
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context and unbind logger."""
        self.bound_logger = None
