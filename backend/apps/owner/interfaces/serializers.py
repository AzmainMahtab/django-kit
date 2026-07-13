"""Owner DRF serializers — validation and serialization only."""

from rest_framework import serializers


class CreateOwnerSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)
    address = serializers.CharField(max_length=255)
    date_of_birth = serializers.DateField(required=False, allow_null=True)


class OwnerReadSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    address = serializers.CharField(read_only=True)
    date_of_birth = serializers.DateField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True)
