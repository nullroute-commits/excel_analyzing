"""Django workbooks app configuration."""

from django.apps import AppConfig


class WorkbooksConfig(AppConfig):
    """Configuration for the workbooks app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'excel_analyzing.web.apps.workbooks'
    verbose_name = 'Excel Workbooks'