# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r excel && useradd -r -g excel excel

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy project
COPY . .

# Install the package
RUN pip install -e .

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