"""OTP value objects and configuration."""

from enum import StrEnum


class OtpType(StrEnum):
    LOGIN = "login-otp"
    PASSWORD_RESET = "password-reset-otp"
    EMAIL_VERIFY = "email-verify-otp"
    PHONE_VERIFY = "phone-verify-otp"


OTP_EXPIRY_SECONDS: dict[OtpType, int] = {
    OtpType.LOGIN: 300,
    OtpType.PASSWORD_RESET: 600,
    OtpType.EMAIL_VERIFY: 3600,
    OtpType.PHONE_VERIFY: 3600,
}

OTP_LENGTH: dict[OtpType, int] = {
    OtpType.LOGIN: 6,
    OtpType.PASSWORD_RESET: 6,
    OtpType.EMAIL_VERIFY: 6,
    OtpType.PHONE_VERIFY: 6,
}
