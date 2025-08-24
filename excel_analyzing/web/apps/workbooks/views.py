"""Workbooks app views."""

from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

from ...models.database import WorkbookModel


class IndexView(TemplateView):
    """Home page view."""
    
    template_name = 'workbooks/index.html'
    
    def get_context_data(self, **kwargs):
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Excel Analyzing - Home'
        return context


class WorkbookListView(ListView):
    """List view for workbooks."""
    
    model = WorkbookModel
    template_name = 'workbooks/workbook_list.html'
    context_object_name = 'workbooks'
    paginate_by = 20
    ordering = ['-created_at']
    
    def get_context_data(self, **kwargs):
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Workbooks'
        return context


class WorkbookDetailView(DetailView):
    """Detail view for a workbook."""
    
    model = WorkbookModel
    template_name = 'workbooks/workbook_detail.html'
    context_object_name = 'workbook'
    
    def get_context_data(self, **kwargs):
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Workbook: {self.object.file_name}'
        return context


class WorkbookUploadView(TemplateView):
    """Upload view for workbooks."""
    
    template_name = 'workbooks/workbook_upload.html'
    
    def get_context_data(self, **kwargs):
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Upload Workbook'
        return context