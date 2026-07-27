"""Login command — authenticate and issue a JWT token pair."""

from django.contrib.auth.hashers import check_password

from backend.apps.identity.domain.events import UserLoggedIn
from backend.apps.identity.domain.exceptions import (
    AccountDisabledError,
    InvalidCredentialsError,
)
from backend.apps.identity.domain.models import User
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus
from backend.shared.token_service import TokenService


class LoginUseCase(UseCase):
    """Authenticate a user with email/password and return access/refresh tokens."""

    def __init__(
        self,
        event_bus: EventBus,
        token_service: TokenService | None = None,
    ) -> None:
        self.event_bus = event_bus
        self.token_service = token_service or TokenService()

    def execute(self, email: str, password: str) -> dict[str, str]:
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist as exc:
            raise InvalidCredentialsError() from exc

        if not user.is_active:
            raise AccountDisabledError()

        if not check_password(password, user.password):
            raise InvalidCredentialsError()

        tokens = self.token_service.create_token_pair(user.id)

        self.event_bus.publish(
            UserLoggedIn(
                aggregate_id=user.id,
                data={"user_id": user.id, "email": user.email},
            )
        )

        return tokens
