"""API app configuration."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Configuration for the API app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "excel_analyzing.web.apps.api"
    verbose_name = "Excel Analyzing API"
