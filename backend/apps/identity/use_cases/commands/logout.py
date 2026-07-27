"""Logout command — revoke access and refresh tokens by blacklisting their JTIs."""

from datetime import UTC, datetime

import jwt

from backend.apps.identity.domain.events import UserLoggedOut
from backend.apps.identity.domain.exceptions import InvalidTokenError
from backend.shared.cache_service import CacheService
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus
from backend.shared.token_service import TokenService


class LogoutUseCase(UseCase):
    """Blacklist the provided refresh and access tokens."""

    def __init__(
        self,
        event_bus: EventBus,
        token_service: TokenService | None = None,
        cache_service: CacheService | None = None,
    ) -> None:
        self.event_bus = event_bus
        self.token_service = token_service or TokenService()
        self.cache = cache_service or CacheService()

    def execute(self, refresh_token: str, access_token: str | None = None) -> None:
        user_id = None
        refresh_jti = self._blacklist_token(refresh_token, "refresh")
        if refresh_jti:
            payload = self._decode_safely(refresh_token)
            if payload is not None:
                user_id = payload.get("sub")

        access_jti = self._blacklist_token(access_token, "access")
        if access_jti:
            payload = self._decode_safely(access_token)
            if payload is not None and not user_id:
                user_id = payload.get("sub")

        if user_id:
            self.event_bus.publish(
                UserLoggedOut(
                    aggregate_id=user_id,
                    data={"user_id": user_id, "refresh_jti": refresh_jti, "access_jti": access_jti},
                )
            )

    def _blacklist_token(self, token: str | None, expected_type: str) -> str | None:
        if not token:
            return None

        payload = self._decode_safely(token)
        if payload is None:
            raise InvalidTokenError(f"Invalid {expected_type} token.")

        if payload.get("type") != expected_type:
            raise InvalidTokenError(f"Token is not a {expected_type} token.")

        jti = payload.get("jti")
        if not jti:
            raise InvalidTokenError("Token is missing jti.")

        remaining = int(payload["exp"] - datetime.now(UTC).timestamp())
        self.cache.set(f"token:blacklist:{jti}", "1", timeout=max(remaining, 1))
        return jti

    def _decode_safely(self, token: str | None) -> dict | None:
        if token is None:
            return None
        try:
            return self.token_service.decode(token)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenError() from exc
