"""Test settings."""

from .base import *  # noqa: F403, F401
from ...core.config import settings as app_settings

# Test specific settings
DEBUG = False

# Use SQLite for testing to avoid database connection issues
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Password hashers (faster for tests)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Override SECRET_KEY for security tests  
SECRET_KEY = "test-secret-key-that-is-definitely-long-enough-for-security-testing-requirements"


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
