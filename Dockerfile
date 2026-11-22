# ==============================================================================
# Production Dockerfile for PetPal - Pet Adoption Tracker
# Multi-stage security, slim footprint, non-root execution & built-in HEALTHCHECK
# ==============================================================================
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered terminal logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install curl for container health monitoring and cleanup apt cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create a dedicated non-root application user and group for security
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 -m appuser

# Set working directory
WORKDIR /app

# Install Python dependencies first (leverages Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code with appropriate file ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose FastAPI listening port
EXPOSE 8000

# Container Healthcheck (Docker & Kubernetes readiness probe friendly)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Launch production ASGI server via Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
