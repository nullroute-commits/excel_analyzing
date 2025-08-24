"""Django ASGI configuration for excel_analyzing project."""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'excel_analyzing.web.settings.production')

application = get_asgi_application()