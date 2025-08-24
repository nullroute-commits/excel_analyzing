"""Django WSGI configuration for excel_analyzing project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "excel_analyzing.web.settings.production"
)

application = get_wsgi_application()
