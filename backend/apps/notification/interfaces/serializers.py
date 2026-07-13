"""Notification DRF serializers."""

from rest_framework import serializers


class NotificationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    event_type = serializers.CharField()
    aggregate_type = serializers.CharField()
    aggregate_id = serializers.IntegerField()
    message = serializers.CharField()
    created_at = serializers.DateTimeField()
