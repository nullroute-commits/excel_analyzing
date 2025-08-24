"""Test settings."""

from .base import *  # noqa: F403, F401
from ...core.config import settings as app_settings

# Test specific settings
DEBUG = False

# Use test database with hostname-based configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": app_settings.database_name,
        "USER": app_settings.database_user,
        "PASSWORD": app_settings.database_password,
        "HOST": app_settings.database_host,
        "PORT": app_settings.database_port,
        "TEST": {
            "NAME": "test_excel_analyzing",
        },
    }
}

# Password hashers (faster for tests)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


# Disable migrations for tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Cache using hostname-based configuration
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": app_settings.redis_url,
    }
}

# Email backend for testing
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Celery (if used)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
