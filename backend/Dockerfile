FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user first
RUN useradd -m -u 1000 appuser

# Copy only necessary files from builder to appuser's home
COPY --from=builder /root/.local /home/appuser/.local

# Create backend directory for the application code
RUN mkdir -p /app/backend && chown -R appuser:appuser /app

# Set ownership and permissions
RUN chown -R appuser:appuser /home/appuser/.local /app

# Ensure scripts in .local are usable
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app:/home/appuser/.local/lib/python3.11/site-packages

# Switch to non-root user
USER appuser

# Copy application code into backend directory
COPY --chown=appuser:appuser . /app/backend/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; import json; response = urllib.request.urlopen('http://localhost:8000/api/v1/health/simple', timeout=5); data = json.loads(response.read()); exit(0 if data.get('status') == 'ok' else 1)" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
