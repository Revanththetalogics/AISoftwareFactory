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
    CustomJsonFormatter,
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

    def test_filter_handles_tracing_import_error(self):
        """Test filter handles import error for tracing module (lines 76-78)."""
        import sys

        filter_instance = CorrelationIdFilter()
        record = MagicMock()

        clear_correlation_id()

        # Create a mock module that raises an exception when attributes are accessed
        class FailingModule:
            def __getattr__(self, name):
                raise ImportError("Simulated tracing import failure")

        # Replace the module to trigger the exception
        original_module = sys.modules.get("backend.infrastructure.tracing")
        sys.modules["backend.infrastructure.tracing"] = FailingModule()

        try:
            result = filter_instance.filter(record)
        finally:
            # Restore the original module
            if original_module:
                sys.modules["backend.infrastructure.tracing"] = original_module
            else:
                sys.modules.pop("backend.infrastructure.tracing", None)

        assert result is True
        assert record.correlation_id == ""
        # trace_id and span_id should default to empty string on error
        assert record.trace_id == ""
        assert record.span_id == ""


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


class TestCustomJsonFormatter:
    """Test cases for CustomJsonFormatter (lines 98-125)."""

    def test_add_fields_basic(self):
        """Test add_fields adds all required fields."""
        formatter = CustomJsonFormatter()

        # Create a mock log record
        record = MagicMock()
        record.created = 1234567890.123
        record.levelname = "INFO"
        record.name = "test.logger"
        record.correlation_id = "corr-123"
        record.trace_id = "trace-456"
        record.span_id = "span-789"
        record.pathname = "/path/to/file.py"
        record.lineno = 42
        record.funcName = "test_function"

        log_record = {}
        message_dict = {}

        formatter.add_fields(log_record, record, message_dict)

        assert log_record["timestamp"] == 1234567890.123
        assert log_record["level"] == "INFO"
        assert log_record["logger"] == "test.logger"
        assert log_record["correlation_id"] == "corr-123"
        assert log_record["trace_id"] == "trace-456"
        assert log_record["span_id"] == "span-789"
        assert log_record["source"]["file"] == "/path/to/file.py"
        assert log_record["source"]["line"] == 42
        assert log_record["source"]["function"] == "test_function"

    def test_add_fields_missing_attributes(self):
        """Test add_fields handles missing attributes with defaults."""
        formatter = CustomJsonFormatter()

        # Create a record without correlation_id, trace_id, span_id
        record = MagicMock(spec=["created", "levelname", "name", "pathname", "lineno", "funcName"])
        record.created = 1234567890.123
        record.levelname = "WARNING"
        record.name = "test.logger"
        record.pathname = "/path/to/file.py"
        record.lineno = 100
        record.funcName = "another_function"

        # Make getattr return default for missing attributes
        type(record).correlation_id = property(lambda self: getattr(self, "_correlation_id", ""))
        type(record).trace_id = property(lambda self: getattr(self, "_trace_id", ""))
        type(record).span_id = property(lambda self: getattr(self, "_span_id", ""))

        log_record = {}
        message_dict = {}

        formatter.add_fields(log_record, record, message_dict)

        assert log_record["timestamp"] == 1234567890.123
        assert log_record["level"] == "WARNING"
        # Correlation ID should default to empty string
        assert log_record["correlation_id"] == ""
        assert log_record["trace_id"] == ""
        assert log_record["span_id"] == ""

    def test_add_fields_renames_message(self):
        """Test add_fields renames 'message' to 'msg' (line 124-125)."""
        formatter = CustomJsonFormatter()

        # Create a real LogRecord for more realistic testing
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test log message",
            args=(),
            exc_info=None,
        )
        record.correlation_id = ""
        record.trace_id = ""
        record.span_id = ""

        log_record = {"message": "Test log message"}
        message_dict = {}

        formatter.add_fields(log_record, record, message_dict)

        # After add_fields, 'message' should be renamed to 'msg'
        assert "message" not in log_record
        assert "msg" in log_record

    def test_add_fields_without_message(self):
        """Test add_fields when no message field present initially."""
        formatter = CustomJsonFormatter()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.DEBUG,
            pathname="/test.py",
            lineno=1,
            msg="Log message",
            args=(),
            exc_info=None,
        )
        record.correlation_id = "corr-id"
        record.trace_id = ""
        record.span_id = ""

        log_record = {}  # No 'message' key initially
        message_dict = {}

        formatter.add_fields(log_record, record, message_dict)

        # The formatter may add 'message' via super().add_fields() and then rename it
        # Just verify we have the standard fields
        assert log_record["timestamp"] == record.created
        assert log_record["level"] == "DEBUG"

    def test_add_fields_with_source_location(self):
        """Test add_fields includes complete source location."""
        formatter = CustomJsonFormatter()

        record = MagicMock()
        record.created = 1234567890.123
        record.levelname = "ERROR"
        record.name = "my.module"
        record.correlation_id = ""
        record.trace_id = ""
        record.span_id = ""
        record.pathname = "/home/user/project/module.py"
        record.lineno = 999
        record.funcName = "error_handler"

        log_record = {}
        message_dict = {}

        formatter.add_fields(log_record, record, message_dict)

        source = log_record["source"]
        assert source["file"] == "/home/user/project/module.py"
        assert source["line"] == 999
        assert source["function"] == "error_handler"
