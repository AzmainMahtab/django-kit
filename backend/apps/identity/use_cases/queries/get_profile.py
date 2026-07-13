"""Get profile query — read the authenticated user's details."""

from backend.apps.identity.domain.repository_interfaces import UserRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.exceptions import NotFoundError
from backend.shared.types import UserDTO


class GetProfileUseCase(UseCase):
    """Pure read: fetch the current user profile."""

    def __init__(self, user_repository: UserRepositoryInterface = None):
        if user_repository is None:
            from backend.apps.identity.repositories.user_repository import UserRepository
            self.user_repo = UserRepository()
        else:
            self.user_repo = user_repository

    def execute(self, user_id: int) -> UserDTO:
        try:
            user = self.user_repo.get_by_id(user_id)
        except Exception as exc:
            raise NotFoundError(f"User with id {user_id} not found.") from exc

        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_staff=user.is_staff,
            is_active=user.is_active,
        )
