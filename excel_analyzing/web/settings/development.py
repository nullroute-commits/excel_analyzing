"""Development settings."""

from .base import *  # noqa: F403, F401

# Development specific settings
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ["*"]

# Database - use local PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "excel_analyzing_dev",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# Development tools (optional)
try:
    import django_extensions
    INSTALLED_APPS += [  # noqa: F405
        "django_extensions",
    ]
except ImportError:
    pass  # django_extensions not available

# Disable CSRF for API development
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
