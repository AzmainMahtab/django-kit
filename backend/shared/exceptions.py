"""Shared exceptions and DRF exception handling."""

from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


class BusinessValidationError(APIException):
    status_code = 400
    default_detail = "Business validation failed."
    default_code = "business_validation_error"


class NotFoundError(APIException):
    status_code = 404
    default_detail = "Resource not found."
    default_code = "not_found"


class PermissionDeniedError(APIException):
    status_code = 403
    default_detail = "Permission denied."
    default_code = "permission_denied"


class AuthenticationFailedError(APIException):
    status_code = 401
    default_detail = "Authentication failed."
    default_code = "authentication_failed"


def custom_exception_handler(exc, context):
    """DRF exception handler that normalizes custom exceptions."""
    response = exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, (BusinessValidationError, NotFoundError, PermissionDeniedError)):
        return Response(
            {"detail": exc.detail, "code": exc.default_code},
            status=exc.status_code,
        )

    return None
