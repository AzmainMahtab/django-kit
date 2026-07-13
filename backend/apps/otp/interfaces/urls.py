"""OTP URL configuration."""

from django.urls import path

from backend.apps.otp.interfaces.views import GenerateOtpView, ValidateOtpView

urlpatterns = [
    path("generate/", GenerateOtpView.as_view(), name="otp-generate"),
    path("validate/", ValidateOtpView.as_view(), name="otp-validate"),
]
