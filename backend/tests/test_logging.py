"""
Tests for structured logging functionality.

This module tests the logging configuration, correlation ID management,
and structured logging output.
"""

import logging
import uuid
from unittest.mock import MagicMock, patch

from backend.core.logging import (
    CorrelationIdFilter,
    LoggingContext,
    clear_correlation_id,
    configure_logging,
    get_correlation_id,
    get_logger,
    set_correlation_id,
)


class TestCorrelationId:
    """Test cases for correlation ID management."""

    def test_set_correlation_id_generates_uuid(self):
        """Test that set_correlation_id generates a UUID when not provided."""
        clear_correlation_id()

        cid = set_correlation_id()

        # Should be a valid UUID
        assert uuid.UUID(cid)
        assert get_correlation_id() == cid

    def test_set_correlation_id_uses_provided_value(self):
        """Test that set_correlation_id uses provided value."""
        custom_id = "my-custom-id"

        cid = set_correlation_id(custom_id)

        assert cid == custom_id
        assert get_correlation_id() == custom_id

    def test_clear_correlation_id(self):
        """Test that clear_correlation_id clears the ID."""
        set_correlation_id("test-id")
        assert get_correlation_id() == "test-id"

        clear_correlation_id()
        assert get_correlation_id() == ""

    def test_get_correlation_id_returns_empty_string_by_default(self):
        """Test that get_correlation_id returns empty string when not set."""
        clear_correlation_id()

        assert get_correlation_id() == ""


class TestCorrelationIdFilter:
    """Test cases for CorrelationIdFilter."""

    def test_filter_adds_correlation_id(self):
        """Test that filter adds correlation_id attribute."""
        filter_instance = CorrelationIdFilter()
        record = MagicMock()

        set_correlation_id("test-correlation-id")
        result = filter_instance.filter(record)

        assert result is True
        assert record.correlation_id == "test-correlation-id"

    def test_filter_adds_empty_string_when_not_set(self):
        """Test that filter adds empty string when correlation ID not set."""
        filter_instance = CorrelationIdFilter()
        record = MagicMock()

        clear_correlation_id()
        result = filter_instance.filter(record)

        assert result is True
        assert record.correlation_id == ""


class TestConfigureLogging:
    """Test cases for logging configuration."""

    @patch("backend.core.logging.get_settings")
    def test_configure_logging_sets_up_handlers(self, mock_get_settings):
        """Test that configure_logging sets up handlers."""
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.is_development = False
        mock_settings.is_testing = False
        mock_get_settings.return_value = mock_settings

        configure_logging()

        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0

    @patch("backend.core.logging.get_settings")
    def test_configure_logging_development_format(self, mock_get_settings):
        """Test that development uses human-readable format."""
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "DEBUG"
        mock_settings.is_development = True
        mock_settings.is_testing = False
        mock_get_settings.return_value = mock_settings

        configure_logging()

        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        assert isinstance(handler.formatter, logging.Formatter)


class TestGetLogger:
    """Test cases for get_logger function."""

    def test_get_logger_returns_bound_logger_proxy(self):
        """Test that get_logger returns a structlog logger proxy."""
        logger = get_logger("test_logger")

        # structlog returns a lazy proxy that becomes a BoundLogger on first use
        assert hasattr(logger, "bind")
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")

    def test_get_logger_has_bind_method(self):
        """Test that returned logger has bind method."""
        logger = get_logger("test_logger")

        assert hasattr(logger, "bind")
        assert callable(logger.bind)


class TestLoggingContext:
    """Test cases for LoggingContext context manager."""

    def test_logging_context_binds_context(self):
        """Test that LoggingContext binds context to logger."""
        logger = get_logger("test_context")

        with LoggingContext(logger, request_id="123", user_id="456") as ctx_logger:
            # The bound logger should have the context
            assert ctx_logger is not None

    def test_logging_context_clears_on_exit(self):
        """Test that LoggingContext clears context on exit."""
        logger = get_logger("test_context")

        with LoggingContext(logger, request_id="123") as ctx_logger:
            bound_logger = ctx_logger

        # After exit, the context should be cleared
        # (We can't directly test this, but we verify no exception is raised)
        assert bound_logger is not None
