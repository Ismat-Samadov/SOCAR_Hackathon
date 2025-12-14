# SOCAR Hackathon - Complete AI System Dockerfile
# Multi-stage build for optimized image size
# Includes OCR, LLM, and frontend capabilities

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY app/ ./app/

# Add local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Expose port (Render uses $PORT dynamically)
EXPOSE 8000

# Health check (disabled for Render compatibility - Render has its own health checks)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
#     CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run the application (use $PORT for Render/cloud compatibility, default to 8000)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
