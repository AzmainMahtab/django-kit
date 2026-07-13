"""Car DRF serializers — validation and serialization only."""

from rest_framework import serializers


class CreateCarSerializer(serializers.Serializer):
    owner_id = serializers.IntegerField(min_value=1)
    make = serializers.CharField(max_length=50)
    model = serializers.CharField(max_length=50)
    year = serializers.IntegerField(min_value=1900, max_value=2100)
    color = serializers.CharField(max_length=30)
    license_plate = serializers.CharField(max_length=20)


class CarReadSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    owner_id = serializers.IntegerField(read_only=True)
    make = serializers.CharField(read_only=True)
    model = serializers.CharField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    color = serializers.CharField(read_only=True)
    license_plate = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True)
