"""Delete user command."""

from backend.apps.identity.domain.events import UserDeleted
from backend.apps.identity.domain.repository_interfaces import UserRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.event_bus import event_bus
from backend.shared.exceptions import NotFoundError


class DeleteUserUseCase(UseCase):
    """Delete a user."""

    def __init__(self, user_repository: UserRepositoryInterface = None):
        if user_repository is None:
            from backend.apps.identity.repositories.user_repository import UserRepository
            self.user_repo = UserRepository()
        else:
            self.user_repo = user_repository

    def execute(self, user_id: int) -> None:
        try:
            user = self.user_repo.get_by_id(user_id)
        except Exception as exc:
            raise NotFoundError(f"User with id {user_id} not found.") from exc

        self.user_repo.delete(user)

        event_bus.publish(
            UserDeleted(
                aggregate_id=user_id,
                data={"user_id": user_id},
            )
        )
