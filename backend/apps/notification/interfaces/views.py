"""Notification DRF views."""

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.notification.interfaces.serializers import NotificationSerializer
from backend.shared.use_case_registry import get_notification


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Notification"],
        summary="List notifications",
        description="Returns notifications generated from domain events.",
        responses={200: NotificationSerializer(many=True)},
    )
    def get(self, request):
        notification = get_notification()
        result = notification.queries.list_notifications.execute()
        return Response(NotificationSerializer(result, many=True).data)
