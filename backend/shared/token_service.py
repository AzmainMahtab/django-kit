"""JWT token service for issuing and verifying access/refresh tokens.

Mirrors the contract used by the fast-kit JWTService so the Django kit
can use the same authentication semantics (token type, jti, exp, sub).
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import jwt
from django.conf import settings


class TokenService:
    """HS256 JWT token issuer/verifier with configurable lifetimes."""

    def __init__(
        self,
        secret: str | None = None,
        access_lifetime_seconds: int | None = None,
        refresh_lifetime_seconds: int | None = None,
        algorithm: str = "HS256",
    ):
        self._secret: str = secret or cast(
            str, getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY)
        )
        self._access_lifetime: int = access_lifetime_seconds or cast(
            int, getattr(settings, "JWT_ACCESS_TOKEN_LIFETIME_SECONDS", 900)
        )
        self._refresh_lifetime: int = refresh_lifetime_seconds or cast(
            int, getattr(settings, "JWT_REFRESH_TOKEN_LIFETIME_SECONDS", 604800)
        )
        self._algorithm: str = algorithm

    def create_token_pair(self, user_id: int) -> dict[str, str]:
        """Return a fresh access/refresh token pair for ``user_id``."""
        return {
            "access_token": self._create_token(user_id, "access", self._access_lifetime),
            "refresh_token": self._create_token(user_id, "refresh", self._refresh_lifetime),
        }

    def decode(self, token: str) -> dict[str, Any]:
        """Decode and validate a token. Raises ``jwt.InvalidTokenError`` variants."""
        return jwt.decode(token, self._secret, algorithms=[self._algorithm])

    def _create_token(self, user_id: int, token_type: str, lifetime_seconds: int) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id),
            "type": token_type,
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": now + timedelta(seconds=lifetime_seconds),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)
