"""API URL configurations."""

from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("", views.api_root, name="root"),
    path("workbooks/", views.workbook_list, name="workbook-list"),
    path("workbooks/<int:pk>/", views.workbook_detail, name="workbook-detail"),
    path("health/", views.health_check, name="health"),
]