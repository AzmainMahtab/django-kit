"""List users query."""

from backend.apps.identity.domain.models import User
from backend.shared.domain import UseCase
from backend.shared.types import UserDTO


class ListUsersUseCase(UseCase):
    """Pure read: list users with optional filters."""

    def execute(self, filters: dict | None = None) -> list[UserDTO]:
        qs = User.objects.all().order_by("-date_joined")
        if filters:
            qs = qs.filter(**filters)

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
            for user in qs
        ]
