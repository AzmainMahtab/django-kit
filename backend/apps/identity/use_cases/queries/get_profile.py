"""Get profile query — read the authenticated user's details."""

from backend.apps.identity.domain.models import User
from backend.shared.domain import UseCase
from backend.shared.exceptions import NotFoundError
from backend.shared.types import UserDTO


class GetProfileUseCase(UseCase):
    """Pure read: fetch the current user profile."""

    def execute(self, user_id: int) -> UserDTO:
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
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
