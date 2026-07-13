"""List owners query."""

from backend.apps.owner.domain.repository_interfaces import OwnerRepositoryInterface
from backend.shared.domain import UseCase


class ListOwnersUseCase(UseCase):
    """Pure read: list all owner profiles."""

    def __init__(self, owner_repository: OwnerRepositoryInterface = None):
        if owner_repository is None:
            from backend.apps.owner.repositories.owner_repository import OwnerRepository

            self.owner_repo = OwnerRepository()
        else:
            self.owner_repo = owner_repository

    def execute(self):
        return self.owner_repo.list_all()
