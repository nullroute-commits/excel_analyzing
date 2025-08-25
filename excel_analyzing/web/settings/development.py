"""Development settings."""

from ...core.config import settings as app_settings
from .base import *  # noqa: F403, F401

# Development specific settings
DEBUG = True

# Database - use hostname-based configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": app_settings.database_name,
        "USER": app_settings.database_user,
        "PASSWORD": app_settings.database_password,
        "HOST": app_settings.database_host,
        "PORT": app_settings.database_port,
    }
}

# Development tools
INSTALLED_APPS += [  # noqa: F405
    "django_extensions",
]

# CSRF trusted origins using hostname-based URLs
CSRF_TRUSTED_ORIGINS = [
    app_settings.frontend_url,
    "http://dev-web-service:8000",
]

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Cache using hostname-based configuration
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": app_settings.redis_url,
    }
}
