"""Django URLs configuration."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # TODO: Create API app
    path("api/", include("excel_analyzing.web.apps.api.urls")),
    path("", include("excel_analyzing.web.apps.workbooks.urls")),
]
