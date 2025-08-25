"""Django URLs configuration."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("api/", include("excel_analyzing.web.apps.api.urls")),  # TODO: Create API app
    path("", include("excel_analyzing.web.apps.workbooks.urls")),
]
