"""OTP DRF views."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.otp.domain.exceptions import (
    InvalidOtpError,
    OtpAlreadyUsedError,
    OtpExpiredError,
)
from backend.apps.otp.domain.value_objects import OtpType
from backend.apps.otp.interfaces.serializers import (
    GenerateOtpSerializer,
    OtpResponseSerializer,
    ValidateOtpResponseSerializer,
    ValidateOtpSerializer,
)
from backend.core.container import get_container


class GenerateOtpView(APIView):
    permission_classes = (IsAuthenticated,)
    throttle_scope = "otp"

    @extend_schema(
        tags=["OTP"],
        summary="Generate an OTP",
        description="Create a one-time password for a user.",
        request=GenerateOtpSerializer,
        responses={201: OtpResponseSerializer},
    )
    def post(self, request):
        serializer = GenerateOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = get_container().otp.generate_otp(
            user_id=serializer.validated_data["user_id"],
            otp_type=OtpType(serializer.validated_data["otp_type"]),
        )
        return Response(OtpResponseSerializer(otp).data, status=status.HTTP_201_CREATED)


class ValidateOtpView(APIView):
    permission_classes = (IsAuthenticated,)
    throttle_scope = "otp"

    @extend_schema(
        tags=["OTP"],
        summary="Validate an OTP",
        description="Verify a one-time password and mark it as used.",
        request=ValidateOtpSerializer,
        responses={200: ValidateOtpResponseSerializer},
    )
    def post(self, request):
        serializer = ValidateOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = get_container().otp.validate_otp(
                user_id=serializer.validated_data["user_id"],
                otp_type=OtpType(serializer.validated_data["otp_type"]),
                code=serializer.validated_data["code"],
            )
        except (InvalidOtpError, OtpExpiredError, OtpAlreadyUsedError) as exc:
            return Response(
                {"detail": str(exc), "code": "invalid_otp"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(ValidateOtpResponseSerializer(result).data)
