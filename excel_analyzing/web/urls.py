"""Django URLs configuration."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('excel_analyzing.web.apps.api.urls')),
    path('', include('excel_analyzing.web.apps.workbooks.urls')),
]