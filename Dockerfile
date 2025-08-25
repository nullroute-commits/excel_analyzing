# Multi-stage Dockerfile for Excel Analyzing
# Stage 1: Base image with system dependencies
FROM python:3.12-alpine AS base

# Install system dependencies required for Python packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    curl \
    && rm -rf /var/cache/apk/*

# Stage 2: Dependencies builder
FROM base AS dependencies

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Copy requirements files
COPY requirements-prod.txt requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-prod.txt

# Stage 3: Application builder
FROM dependencies AS builder

# Set environment variable for setuptools_scm to avoid git dependency
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_EXCEL_ANALYZING=0.1.0

# Copy project source code
COPY . .

# Install the package
RUN pip install -e .

# Stage 4: Production image
FROM python:3.12-alpine AS production

# Install runtime dependencies only
RUN apk add --no-cache \
    postgresql-client \
    curl \
    && rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1000 excel && \
    adduser -u 1000 -G excel -s /bin/sh -D excel

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Copy Python packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application from builder stage
COPY --from=builder /app .

# Create directories for logs and data
RUN mkdir -p /app/logs /app/staticfiles && \
    chown -R excel:excel /app

# Switch to non-root user
USER excel

# Collect static files
RUN python manage.py collectstatic --noinput --settings=excel_analyzing.web.settings.production || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "excel_analyzing.web.wsgi:application"]