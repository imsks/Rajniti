# Multi-stage Dockerfile for Rajniti Election Data API
# Stage 1: Base image with dependencies
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Development image with hot reload
FROM base as development

# Set development environment variables
ENV FLASK_ENV=development \
    FLASK_DEBUG=True

# Copy application code
COPY app/ ./app/
COPY run.py .
COPY alembic.ini .
COPY alembic/ ./alembic/

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Use Flask development server for better hot reload with volume mounts
# Flask's reloader works better with Docker volumes than gunicorn --reload
CMD ["python", "run.py"]

# Stage 3: Production image for GCP Cloud Run
FROM base as production

# Set production environment variables
ENV FLASK_ENV=production \
    FLASK_DEBUG=False

# Copy application code
COPY app/ ./app/
COPY run.py .
COPY alembic.ini .
COPY alembic/ ./alembic/

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (GCP Cloud Run uses PORT env variable)
EXPOSE 8000

# Use gunicorn for production
CMD exec gunicorn --bind :${PORT:-8000} --workers 1 --threads 8 --timeout 0 'app:create_app()'
