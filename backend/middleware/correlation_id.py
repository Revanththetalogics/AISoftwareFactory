"""
Correlation ID middleware for request tracing.

This middleware ensures every request has a correlation ID for distributed tracing,
either from an incoming header or generated fresh.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.core.logging import set_correlation_id, clear_correlation_id, get_correlation_id


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to manage correlation IDs across requests.
    
    This middleware:
    1. Extracts correlation ID from incoming X-Correlation-ID header
    2. Generates a new correlation ID if not provided
    3. Sets the correlation ID in the logging context
    4. Adds the correlation ID to the response headers
    5. Clears the correlation ID after request completion
    
    Attributes:
        header_name: Name of the correlation ID header
        
    Example:
        >>> app.add_middleware(CorrelationIdMiddleware)
        >>> # Request with X-Correlation-ID: abc-123
        >>> # Response includes X-Correlation-ID: abc-123
    """
    
    def __init__(self, app, header_name: str = "X-Correlation-ID"):
        """
        Initialize middleware.
        
        Args:
            app: FastAPI application
            header_name: Header name for correlation ID
        """
        super().__init__(app)
        self.header_name = header_name
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """
        Process request with correlation ID management.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain
            
        Returns:
            Response with correlation ID header
        """
        try:
            # Extract or generate correlation ID
            correlation_id = request.headers.get(self.header_name.lower())
            if not correlation_id:
                correlation_id = request.headers.get(self.header_name)
            
            # Set correlation ID in context
            set_correlation_id(correlation_id)
            
            # Process request
            response = await call_next(request)
            
            # Add correlation ID to response
            response.headers[self.header_name] = get_correlation_id()
            
            return response
            
        finally:
            # Always clear correlation ID
            clear_correlation_id()
