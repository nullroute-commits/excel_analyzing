"""API URLs configuration."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "api"

router = DefaultRouter()
# router.register(r'workbooks', views.WorkbookViewSet)

urlpatterns = [
    path("workbooks/", views.workbook_list, name="workbook-list"),
    path("workbooks/<int:pk>/", views.workbook_detail, name="workbook-detail"),
    path("query/", views.data_query, name="data-query"),
] + router.urls