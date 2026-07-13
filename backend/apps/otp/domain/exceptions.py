"""OTP domain exceptions."""


class OtpError(Exception):
    """Base OTP error."""


class InvalidOtpError(OtpError):
    """Provided OTP code does not match."""


class OtpExpiredError(OtpError):
    """OTP has expired."""


class OtpAlreadyUsedError(OtpError):
    """OTP has already been consumed."""
