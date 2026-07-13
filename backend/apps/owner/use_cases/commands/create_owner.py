"""Create owner command."""

from datetime import date

from backend.apps.owner.domain.exceptions import OwnerAlreadyExistsError
from backend.apps.owner.domain.models import Owner
from backend.apps.owner.domain.repository_interfaces import OwnerRepositoryInterface
from backend.shared.domain import UseCase


class CreateOwnerUseCase(UseCase):
    """Create a new owner profile for a user."""

    def __init__(self, owner_repository: OwnerRepositoryInterface = None):
        if owner_repository is None:
            from backend.apps.owner.repositories.owner_repository import OwnerRepository

            self.owner_repo = OwnerRepository()
        else:
            self.owner_repo = owner_repository

    def execute(
        self,
        user_id: int,
        address: str,
        date_of_birth: date | None = None,
    ) -> Owner:
        existing = self.owner_repo.get_by_user_id(user_id)
        if existing:
            raise OwnerAlreadyExistsError(f"Owner for user {user_id} already exists.")

        owner = Owner(user_id=user_id, address=address, date_of_birth=date_of_birth)
        return self.owner_repo.create(owner)
