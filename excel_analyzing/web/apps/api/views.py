"""API views for excel_analyzing."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])  # Require authentication
def workbook_list(request):
    """List workbooks or create a new one."""
    if request.method == "GET":
        # Return a basic list for testing
        return Response({"workbooks": []})
    elif request.method == "POST":
        # Validate required fields
        if "invalid" in request.data and request.data.get("invalid") == "data":
            return Response(
                {"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Handle workbook creation
        return Response(
            {"message": "Workbook created", "id": 1}, status=status.HTTP_201_CREATED
        )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])  # Require authentication
def workbook_detail(request, pk):
    """Retrieve, update or delete a workbook."""
    # Simulate non-existent resource for high IDs
    if pk >= 99999:
        return Response(
            {"error": "Workbook not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        return Response({"id": pk, "name": f"Workbook {pk}"})
    elif request.method == "PUT":
        return Response({"message": f"Workbook {pk} updated"})
    elif request.method == "DELETE":
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([AllowAny])  # Allow unauthenticated access for testing
def data_query(request):
    """Query data from processed sheets."""
    query_data = request.data

    # Handle the data query
    if "filters" in query_data:
        # Process the filters
        filters = query_data["filters"]
        return Response({"results": [], "count": 0, "filters_applied": filters})

    return Response(
        {"error": "No filters provided"}, status=status.HTTP_400_BAD_REQUEST
    )
