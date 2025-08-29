"""API views for RESTful endpoints."""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint."""
    return Response(
        {
            "message": "Excel Analyzing API",
            "version": "1.0",
            "endpoints": {"workbooks": "/api/workbooks/", "health": "/api/health/"},
        }
    )


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def workbook_list(request):
    """List workbooks or create new workbook."""
    if request.method == "GET":
        return Response({"workbooks": []})
    elif request.method == "POST":
        return Response({"message": "Workbook created"}, status=201)


@api_view(["GET", "PUT", "DELETE"])
def workbook_detail(request, pk):
    """Retrieve, update or delete a workbook."""
    if request.method == "GET":
        return Response({"id": pk, "name": f"Workbook {pk}"})
    elif request.method == "PUT":
        return Response({"message": f"Workbook {pk} updated"})
    elif request.method == "DELETE":
        return Response({"message": f"Workbook {pk} deleted"})


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({"status": "healthy", "service": "excel-analyzing"})
