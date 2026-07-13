"""OTP DRF serializers."""

from rest_framework import serializers

from backend.apps.otp.domain.value_objects import OtpType


class GenerateOtpSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)
    otp_type = serializers.ChoiceField(choices=[(t.value, t.value) for t in OtpType])


class OtpResponseSerializer(serializers.Serializer):
    otp_id = serializers.IntegerField()
    code = serializers.CharField()
    expires_at = serializers.DateTimeField()


class ValidateOtpSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)
    otp_type = serializers.ChoiceField(choices=[(t.value, t.value) for t in OtpType])
    code = serializers.CharField(min_length=4, max_length=8)


class ValidateOtpResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
