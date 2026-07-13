"""Ordering DRF serializers."""

from rest_framework import serializers


class JobInputSerializer(serializers.Serializer):
    job_id = serializers.CharField(max_length=32)


class OrderCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)
    order_number = serializers.CharField(max_length=32)
    jobs = JobInputSerializer(many=True, allow_empty=False)


class JobStatusTransitionSerializer(serializers.Serializer):
    new_status = serializers.CharField(max_length=32)
    reason = serializers.CharField(max_length=255, required=False, allow_blank=True)


class JobSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    job_id = serializers.CharField()
    job_status = serializers.CharField()
    file_editable = serializers.BooleanField()
    order_id = serializers.IntegerField()


class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    order_number = serializers.CharField()
    user_id = serializers.IntegerField()
    status = serializers.CharField()
    jobs = JobSerializer(many=True)
