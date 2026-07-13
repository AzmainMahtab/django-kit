"""Public API for the owner module.

★ THIS IS THE ONLY FILE OTHER MODULES CAN IMPORT FROM THIS APP ★
"""

from backend.apps.owner.use_cases.commands.create_owner import CreateOwnerUseCase
from backend.apps.owner.use_cases.queries.get_owner import (
    GetOwnerByIdUseCase,
    GetOwnerByUserIdUseCase,
    GetOwnerByUuidUseCase,
)
from backend.apps.owner.use_cases.queries.list_owners import ListOwnersUseCase


class OwnerUseCases:
    """Facade exposed through the use-case registry."""

    def __init__(self):
        self.commands = OwnerCommands()
        self.queries = OwnerQueries()

    def create_owner(self, **kwargs):
        return self.commands.create_owner.execute(**kwargs)

    def get_owner_by_id(self, **kwargs):
        return self.queries.get_owner_by_id.execute(**kwargs)

    def get_owner_by_uuid(self, **kwargs):
        return self.queries.get_owner_by_uuid.execute(**kwargs)

    def get_owner_by_user_id(self, **kwargs):
        return self.queries.get_owner_by_user_id.execute(**kwargs)

    def list_owners(self, **kwargs):
        return self.queries.list_owners.execute(**kwargs)


class OwnerCommands:
    def __init__(self):
        self.create_owner = CreateOwnerUseCase()


class OwnerQueries:
    def __init__(self):
        self.get_owner_by_id = GetOwnerByIdUseCase()
        self.get_owner_by_uuid = GetOwnerByUuidUseCase()
        self.get_owner_by_user_id = GetOwnerByUserIdUseCase()
        self.list_owners = ListOwnersUseCase()
