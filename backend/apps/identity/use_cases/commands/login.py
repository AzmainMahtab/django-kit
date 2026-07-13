"""Login command — authenticate and issue a JWT token pair."""

from django.contrib.auth.hashers import check_password

from backend.apps.identity.domain.events import UserLoggedIn
from backend.apps.identity.domain.exceptions import (
    AccountDisabledError,
    InvalidCredentialsError,
)
from backend.apps.identity.domain.repository_interfaces import UserRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.event_bus import event_bus
from backend.shared.token_service import TokenService


class LoginUseCase(UseCase):
    """Authenticate a user with email/password and return access/refresh tokens."""

    def __init__(
        self,
        user_repository: UserRepositoryInterface = None,
        token_service: TokenService = None,
    ):
        if user_repository is None:
            from backend.apps.identity.repositories.user_repository import UserRepository
            self.user_repo = UserRepository()
        else:
            self.user_repo = user_repository
        self.token_service = token_service or TokenService()

    def execute(self, email: str, password: str) -> dict[str, str]:
        try:
            user = self.user_repo.get_by_email(email)
        except Exception as exc:
            raise InvalidCredentialsError() from exc

        if not user.is_active:
            raise AccountDisabledError()

        if not check_password(password, user.password):
            raise InvalidCredentialsError()

        tokens = self.token_service.create_token_pair(user.id)

        event_bus.publish(
            UserLoggedIn(
                aggregate_id=user.id,
                data={"user_id": user.id, "email": user.email},
            )
        )

        return tokens
