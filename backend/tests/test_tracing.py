"""
Comprehensive tests for Tracing infrastructure module.

Covers all uncovered lines in tracing.py:
- Lines 16-35, 40, 47, 55
"""

from unittest.mock import MagicMock, patch

from fastapi import FastAPI

from backend.infrastructure.tracing import (
    get_current_span_id,
    get_current_trace_id,
    get_tracer,
    setup_tracing,
)


class TestSetupTracing:
    """Tests for setup_tracing function."""

    def test_setup_tracing_without_endpoint(self):
        """Test setting up tracing without OTLP endpoint."""
        app = FastAPI()

        with patch("backend.infrastructure.tracing.TracerProvider") as mock_provider_cls:
            with patch("backend.infrastructure.tracing.trace") as mock_trace:
                with patch(
                    "backend.infrastructure.tracing.FastAPIInstrumentor"
                ) as mock_instrumentor:
                    mock_provider = MagicMock()
                    mock_provider_cls.return_value = mock_provider

                    result = setup_tracing(app, service_name="test-service")

                    assert result == mock_provider
                    mock_trace.set_tracer_provider.assert_called_once_with(mock_provider)
                    mock_instrumentor.instrument_app.assert_called_once_with(app)

    def test_setup_tracing_with_endpoint(self):
        """Test setting up tracing with OTLP endpoint."""
        app = FastAPI()

        with patch("backend.infrastructure.tracing.TracerProvider") as mock_provider_cls:
            with patch("backend.infrastructure.tracing.OTLPSpanExporter") as mock_exporter_cls:
                with patch("backend.infrastructure.tracing.BatchSpanProcessor") as mock_processor_cls:
                    with patch("backend.infrastructure.tracing.trace"):
                        with patch("backend.infrastructure.tracing.FastAPIInstrumentor"):
                            mock_provider = MagicMock()
                            mock_provider_cls.return_value = mock_provider

                            mock_exporter = MagicMock()
                            mock_exporter_cls.return_value = mock_exporter

                            mock_processor = MagicMock()
                            mock_processor_cls.return_value = mock_processor

                            result = setup_tracing(
                                app,
                                service_name="test-service",
                                otlp_endpoint="http://localhost:4317",
                            )

                            assert result == mock_provider
                            mock_exporter_cls.assert_called_once_with(
                                endpoint="http://localhost:4317", insecure=True
                            )
                            mock_processor_cls.assert_called_once_with(mock_exporter)
                            mock_provider.add_span_processor.assert_called_once_with(
                                mock_processor
                            )

    def test_setup_tracing_exception(self):
        """Test setup_tracing handles exceptions gracefully."""
        app = FastAPI()

        with patch("backend.infrastructure.tracing.TracerProvider") as mock_provider_cls:
            mock_provider_cls.side_effect = Exception("Tracing setup failed")

            result = setup_tracing(app, service_name="test-service")

            assert result is None

    def test_setup_tracing_default_service_name(self):
        """Test setup_tracing uses default service name."""
        app = FastAPI()

        with patch("backend.infrastructure.tracing.TracerProvider") as mock_provider_cls:
            with patch("backend.infrastructure.tracing.Resource") as mock_resource_cls:
                with patch("backend.infrastructure.tracing.trace"):
                    with patch("backend.infrastructure.tracing.FastAPIInstrumentor"):
                        mock_resource = MagicMock()
                        mock_resource_cls.create.return_value = mock_resource
                        mock_provider = MagicMock()
                        mock_provider_cls.return_value = mock_provider

                        setup_tracing(app)

                        # Check that default service name was used
                        mock_resource_cls.create.assert_called_once()
                        call_args = mock_resource_cls.create.call_args[0][0]
                        from opentelemetry.sdk.resources import SERVICE_NAME

                        assert call_args[SERVICE_NAME] == "theta-ai-backend"


class TestGetTracer:
    """Tests for get_tracer function."""

    def test_get_tracer_default_name(self):
        """Test getting tracer with default name."""
        with patch("backend.infrastructure.tracing.trace") as mock_trace:
            mock_tracer = MagicMock()
            mock_trace.get_tracer.return_value = mock_tracer

            result = get_tracer()

            assert result == mock_tracer
            mock_trace.get_tracer.assert_called_once_with("theta-ai")

    def test_get_tracer_custom_name(self):
        """Test getting tracer with custom name."""
        with patch("backend.infrastructure.tracing.trace") as mock_trace:
            mock_tracer = MagicMock()
            mock_trace.get_tracer.return_value = mock_tracer

            result = get_tracer("custom-tracer")

            assert result == mock_tracer
            mock_trace.get_tracer.assert_called_once_with("custom-tracer")


class TestGetCurrentTraceId:
    """Tests for get_current_trace_id function."""

    def test_get_current_trace_id_with_active_span(self):
        """Test getting trace ID when there's an active span."""
        with patch("backend.infrastructure.tracing.trace") as mock_trace:
            mock_span = MagicMock()
            mock_span_context = MagicMock()
            mock_span_context.trace_id = 0x12345678901234567890123456789012
            mock_span.get_span_context.return_value = mock_span_context

            mock_trace.get_current_span.return_value = mock_span

            result = get_current_trace_id()

            assert result == "12345678901234567890123456789012"

    def test_get_current_trace_id_no_span(self):
        """Test getting trace ID when there's no active span."""
        with patch("backend.infrastructure.tracing.trace") as mock_trace:
            mock_trace.get_current_span.return_value = None

            result = get_current_trace_id()

            assert result == ""

    def test_get_current_trace_id_no_trace_id(self):
        """Test getting trace ID when span has no trace_id."""
        with patch("backend.infrastructure.tracing.trace") as mock_trace:
            mock_span = MagicMock()
            mock_span_context = MagicMock()
            mock_span_context.trace_id = 0  # Invalid/no trace ID

            mock_span.get_span_context.return_value = mock_span_context
            mock_trace.get_current_span.return_value = mock_span

            result = get_current_trace_id()

            assert result == ""


class TestGetCurrentSpanId:
    """Tests for get_current_span_id function."""

    def test_get_current_span_id_with_active_span(self):
        """Test getting span ID when there's an active span."""
        with patch("backend.infrastructure.tracing.trace") as mock_trace:
            mock_span = MagicMock()
            mock_span_context = MagicMock()
            mock_span_context.span_id = 0x1234567890123456

            mock_span.get_span_context.return_value = mock_span_context
            mock_trace.get_current_span.return_value = mock_span

            result = get_current_span_id()

            assert result == "1234567890123456"

    def test_get_current_span_id_no_span(self):
        """Test getting span ID when there's no active span."""
        with patch("backend.infrastructure.tracing.trace") as mock_trace:
            mock_trace.get_current_span.return_value = None

            result = get_current_span_id()

            assert result == ""

    def test_get_current_span_id_no_span_id(self):
        """Test getting span ID when span has no span_id."""
        with patch("backend.infrastructure.tracing.trace") as mock_trace:
            mock_span = MagicMock()
            mock_span_context = MagicMock()
            mock_span_context.span_id = 0  # Invalid/no span ID

            mock_span.get_span_context.return_value = mock_span_context
            mock_trace.get_current_span.return_value = mock_span

            result = get_current_span_id()

            assert result == ""


class TestTracingIntegration:
    """Integration tests for tracing module."""

    def test_full_tracing_setup_flow(self):
        """Test complete tracing setup flow."""
        app = FastAPI()

        with patch("backend.infrastructure.tracing.TracerProvider") as mock_provider_cls:
            with patch("backend.infrastructure.tracing.OTLPSpanExporter") as mock_exporter_cls:
                with patch("backend.infrastructure.tracing.BatchSpanProcessor") as mock_processor_cls:
                    with patch("backend.infrastructure.tracing.trace") as mock_trace:
                        with patch(
                            "backend.infrastructure.tracing.FastAPIInstrumentor"
                        ) as mock_instrumentor:
                            mock_provider = MagicMock()
                            mock_provider_cls.return_value = mock_provider

                            mock_exporter = MagicMock()
                            mock_exporter_cls.return_value = mock_exporter

                            mock_processor = MagicMock()
                            mock_processor_cls.return_value = mock_processor

                            # Setup tracing
                            provider = setup_tracing(
                                app,
                                service_name="integration-test",
                                otlp_endpoint="http://jaeger:4317",
                            )

                            # Verify provider was created
                            assert provider is not None

                            # Verify exporter was configured
                            mock_exporter_cls.assert_called_with(
                                endpoint="http://jaeger:4317", insecure=True
                            )

                            # Verify processor was added
                            mock_provider.add_span_processor.assert_called()

                            # Verify tracer provider was set
                            mock_trace.set_tracer_provider.assert_called_with(mock_provider)

                            # Verify FastAPI was instrumented
                            mock_instrumentor.instrument_app.assert_called_with(app)

    def test_tracer_usage(self):
        """Test typical tracer usage pattern."""
        with patch("backend.infrastructure.tracing.trace") as mock_trace:
            mock_tracer = MagicMock()
            mock_trace.get_tracer.return_value = mock_tracer

            tracer = get_tracer("my-service")

            # Simulate creating a span
            mock_span = MagicMock()
            mock_tracer.start_span.return_value = mock_span

            with tracer.start_span("my-operation") as span:
                span.set_attribute("key", "value")

            mock_tracer.start_span.assert_called_with("my-operation")

    def test_trace_id_format(self):
        """Test that trace ID is formatted correctly."""
        with patch("backend.infrastructure.tracing.trace") as mock_trace:
            mock_span = MagicMock()
            mock_span_context = MagicMock()
            # Use a 128-bit trace ID (32 hex characters)
            mock_span_context.trace_id = 0xABCDEF1234567890ABCDEF1234567890

            mock_span.get_span_context.return_value = mock_span_context
            mock_trace.get_current_span.return_value = mock_span

            result = get_current_trace_id()

            # Should be 32 characters (128 bits / 4 bits per hex char)
            assert len(result) == 32
            assert result == "abcdef1234567890abcdef1234567890"

    def test_span_id_format(self):
        """Test that span ID is formatted correctly."""
        with patch("backend.infrastructure.tracing.trace") as mock_trace:
            mock_span = MagicMock()
            mock_span_context = MagicMock()
            # Use a 64-bit span ID (16 hex characters)
            mock_span_context.span_id = 0xABCDEF1234567890

            mock_span.get_span_context.return_value = mock_span_context
            mock_trace.get_current_span.return_value = mock_span

            result = get_current_span_id()

            # Should be 16 characters (64 bits / 4 bits per hex char)
            assert len(result) == 16
            assert result == "abcdef1234567890"
