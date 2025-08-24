"""Workbooks app URL configuration."""

from django.urls import path
from . import views

app_name = 'workbooks'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('workbooks/', views.WorkbookListView.as_view(), name='workbook_list'),
    path('workbooks/<int:pk>/', views.WorkbookDetailView.as_view(), name='workbook_detail'),
    path('upload/', views.WorkbookUploadView.as_view(), name='workbook_upload'),
]