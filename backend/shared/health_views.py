"""Shared health-check endpoints."""

from django.db import connection
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()


@extend_schema(
    responses=OpenApiResponse(
        response=HealthSerializer,
        description="The service is up and the database is reachable.",
        examples=[OpenApiExample("ok", value={"status": "ok"})],
    ),
    auth=[],
    tags=["health"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Liveness/readiness endpoint that verifies the database is reachable."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return Response({"status": "ok"})
