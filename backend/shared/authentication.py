"""DRF authentication backend that validates JWT access tokens.

This is shared infrastructure and can be referenced from DRF settings.
"""

import jwt
from django.contrib.auth import get_user_model
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import authentication, exceptions

from backend.shared.cache_service import CacheService
from backend.shared.token_service import TokenService


class JWTAuthentication(authentication.BaseAuthentication):
    """Authenticate requests via ``Authorization: Bearer <token>``.

    Validates the token signature, type, and blacklist status.
    """

    keyword = "Bearer"

    def __init__(self):
        self.token_service = TokenService()
        self.cache = CacheService()

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).split()
        if not header or header[0].lower() != self.keyword.lower().encode():
            return None

        if len(header) != 2:
            raise exceptions.AuthenticationFailed("Invalid Authorization header format.")

        token = header[1].decode("utf-8")
        return self._authenticate_credentials(token)

    def _authenticate_credentials(self, token: str):
        try:
            payload = self.token_service.decode(token)
        except jwt.ExpiredSignatureError as exc:
            raise exceptions.AuthenticationFailed("Token has expired.") from exc
        except jwt.InvalidTokenError as exc:
            raise exceptions.AuthenticationFailed(f"Invalid token: {exc}") from exc

        if payload.get("type") != "access":
            raise exceptions.AuthenticationFailed("Token is not an access token.")

        jti = payload.get("jti")
        if jti and self.cache.exists(f"token:blacklist:{jti}"):
            raise exceptions.AuthenticationFailed("Token has been revoked.")

        user_id = payload.get("sub")
        if not user_id:
            raise exceptions.AuthenticationFailed("Token contains no user identifier.")

        user_model = get_user_model()
        try:
            user = user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("User not found.") from exc

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User account is disabled.")

        return (user, token)


class JWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """Describe :class:`JWTAuthentication` to drf-spectacular.

    Without this, every view using the custom authenticator emits a W001 warning
    and the generated schema carries no security scheme — leaving Swagger UI's
    "Authorize" button unable to send a token.
    """

    target_class = JWTAuthentication
    name = "jwtAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
