"""Identity domain / authentication exceptions."""

from backend.shared.exceptions import (
    AuthenticationFailedError,
    BusinessValidationError,
)


class InvalidCredentialsError(AuthenticationFailedError):
    default_detail = "Invalid credentials."
    default_code = "invalid_credentials"


class AccountDisabledError(AuthenticationFailedError):
    default_detail = "Account is disabled or inactive."
    default_code = "account_disabled"


class InvalidTokenError(AuthenticationFailedError):
    default_detail = "Invalid token."
    default_code = "invalid_token"


class TokenExpiredError(AuthenticationFailedError):
    default_detail = "Token has expired."
    default_code = "token_expired"


class TokenBlacklistedError(AuthenticationFailedError):
    default_detail = "Token has been revoked."
    default_code = "token_blacklisted"


class EmailAlreadyVerifiedError(BusinessValidationError):
    default_detail = "Email is already verified."
    default_code = "email_already_verified"
