"""Logging utilities and setup."""

import logging
import logging.config
from pathlib import Path
from typing import Any, Dict

from ..core.config import settings


def setup_logging(config: Dict[str, Any] = None) -> None:
    """Set up logging configuration."""
    if config is None:
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": settings.log_format,
                },
                "detailed": {
                    "format": (
                        "%(asctime)s - %(name)s - %(levelname)s - "
                        "%(module)s - %(funcName)s - %(message)s"
                    ),
                },
            },
            "handlers": {
                "console": {
                    "level": settings.log_level,
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                },
                "file": {
                    "level": settings.log_level,
                    "class": "logging.FileHandler",
                    "filename": "excel_analyzing.log",
                    "formatter": "detailed",
                },
            },
            "loggers": {
                "excel_analyzing": {
                    "handlers": ["console", "file"],
                    "level": settings.log_level,
                    "propagate": False,
                },
            },
            "root": {
                "level": settings.log_level,
                "handlers": ["console"],
            },
        }

    # Create log directory if it doesn't exist
    log_file = Path(config["handlers"]["file"]["filename"])
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"excel_analyzing.{name}")


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


def log_execution_time(func):
    """Decorator to log function execution time."""
    import functools
    import time

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.2f} seconds: {e}"
            )
            raise

    return wrapper
