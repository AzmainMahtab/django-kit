"""Refresh token command — rotate a refresh token into a new token pair."""

from datetime import UTC, datetime

import jwt

from backend.apps.identity.domain.events import TokenRefreshed
from backend.apps.identity.domain.exceptions import (
    AccountDisabledError,
    InvalidTokenError,
    TokenBlacklistedError,
    TokenExpiredError,
)
from backend.apps.identity.domain.models import User
from backend.shared.cache_service import CacheService
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus
from backend.shared.token_service import TokenService


class RefreshTokenUseCase(UseCase):
    """Validate a refresh token, blacklist it, and issue a fresh token pair."""

    def __init__(
        self,
        event_bus: EventBus,
        token_service: TokenService | None = None,
        cache_service: CacheService | None = None,
    ) -> None:
        self.event_bus = event_bus
        self.token_service = token_service or TokenService()
        self.cache = cache_service or CacheService()

    def execute(self, refresh_token: str) -> dict[str, str]:
        try:
            payload = self.token_service.decode(refresh_token)
        except jwt.ExpiredSignatureError as exc:
            raise TokenExpiredError() from exc
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenError() from exc

        if payload.get("type") != "refresh":
            raise InvalidTokenError("Token is not a refresh token.")

        jti = payload.get("jti")
        if self.cache.exists(f"token:blacklist:{jti}"):
            raise TokenBlacklistedError()

        user_id = int(payload["sub"])
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise InvalidTokenError("User not found.") from exc

        if not user.is_active:
            raise AccountDisabledError()

        remaining = int(payload["exp"] - datetime.now(UTC).timestamp())
        self.cache.set(f"token:blacklist:{jti}", "1", timeout=max(remaining, 1))

        tokens = self.token_service.create_token_pair(user.id)

        self.event_bus.publish(
            TokenRefreshed(
                aggregate_id=user.id,
                data={"user_id": user.id, "old_jti": jti},
            )
        )

        return tokens
