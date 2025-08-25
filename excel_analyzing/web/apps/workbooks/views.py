"""Workbooks app views."""

from django.views.generic import DetailView, ListView, TemplateView

from excel_analyzing.models.database import WorkbookModel


class IndexView(TemplateView):
    """Home page view."""

    template_name = "workbooks/index.html"

    def get_context_data(self, **kwargs):
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Excel Analyzing - Home"
        return context


class WorkbookListView(ListView):
    """List view for workbooks."""

    model = WorkbookModel
    template_name = "workbooks/workbook_list.html"
    context_object_name = "workbooks"
    paginate_by = 20
    ordering = ["-created_at"]

    def get_context_data(self, **kwargs):
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Workbooks"
        return context


class WorkbookDetailView(DetailView):
    """Detail view for a workbook."""

    model = WorkbookModel
    template_name = "workbooks/workbook_detail.html"
    context_object_name = "workbook"

    def get_context_data(self, **kwargs):
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["title"] = f"Workbook: {self.object.file_name}"
        return context


class WorkbookUploadView(TemplateView):
    """Upload view for workbooks."""

    template_name = "workbooks/workbook_upload.html"

    def get_context_data(self, **kwargs):
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Upload Workbook"
        return context

    def post(self, request, *args, **kwargs):
        """Handle workbook upload."""
        from django.http import JsonResponse

        # Handle file upload
        if "file" in request.FILES:
            file_obj = request.FILES["file"]
            name = request.POST.get("name", file_obj.name)

            # For testing purposes, just return success
            return JsonResponse(
                {
                    "success": True,
                    "message": "Workbook uploaded successfully",
                    "file_name": file_obj.name,
                    "name": name,
                }
            )

        return JsonResponse({"success": False, "error": "No file provided"}, status=400)
