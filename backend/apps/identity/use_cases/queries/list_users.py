"""List users query."""

from backend.apps.identity.domain.repository_interfaces import UserRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.types import UserDTO


class ListUsersUseCase(UseCase):
    """Pure read: list users with optional filters."""

    def __init__(self, user_repository: UserRepositoryInterface = None):
        if user_repository is None:
            from backend.apps.identity.repositories.user_repository import UserRepository
            self.user_repo = UserRepository()
        else:
            self.user_repo = user_repository

    def execute(self, filters: dict = None) -> list[UserDTO]:
        users = self.user_repo.list_users(filters)
        return [
            UserDTO(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_staff=user.is_staff,
                is_active=user.is_active,
            )
            for user in users
        ]
