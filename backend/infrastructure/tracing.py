"""OpenTelemetry distributed tracing configuration."""
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

logger = logging.getLogger(__name__)


def setup_tracing(app, service_name: str = "theta-ai-backend", otlp_endpoint: str = None):
    """Initialize OpenTelemetry tracing for the FastAPI application."""
    try:
        resource = Resource.create({SERVICE_NAME: service_name})
        provider = TracerProvider(resource=resource)
        
        if otlp_endpoint:
            exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            logger.info(f"OpenTelemetry tracing enabled, exporting to {otlp_endpoint}")
        else:
            logger.info("OpenTelemetry tracing enabled (no exporter configured)")
        
        trace.set_tracer_provider(provider)
        
        # Auto-instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)
        
        return provider
    except Exception as e:
        logger.warning(f"Failed to initialize tracing: {e}")
        return None


def get_tracer(name: str = "theta-ai"):
    """Get a tracer instance."""
    return trace.get_tracer(name)


def get_current_trace_id() -> str:
    """Get current trace ID for log correlation."""
    span = trace.get_current_span()
    if span and span.get_span_context().trace_id:
        return format(span.get_span_context().trace_id, '032x')
    return ""


def get_current_span_id() -> str:
    """Get current span ID for log correlation."""
    span = trace.get_current_span()
    if span and span.get_span_context().span_id:
        return format(span.get_span_context().span_id, '016x')
    return ""
