"""Unit tests for CreateOwnerUseCase."""

import pytest

from backend.apps.owner.domain.exceptions import OwnerAlreadyExistsError
from backend.apps.owner.domain.models import Owner
from backend.apps.owner.use_cases.commands.create_owner import CreateOwnerUseCase


class MockOwnerRepository:
    def __init__(self, existing_user_ids=None):
        self._owners = {}
        self._next_id = 1
        self._existing_user_ids = set(existing_user_ids or [])

    def get_by_id(self, owner_id: int) -> Owner:
        return self._owners[owner_id]

    def get_by_uuid(self, uuid: str):
        for owner in self._owners.values():
            if str(owner.uuid) == str(uuid):
                return owner
        return None

    def get_by_user_id(self, user_id: int):
        if user_id in self._existing_user_ids:
            owner = Owner(user_id=user_id, address="123 Existing St")
            owner.id = self._next_id
            return owner
        return None

    def create(self, owner: Owner) -> Owner:
        owner.id = self._next_id
        self._next_id += 1
        self._owners[owner.id] = owner
        self._existing_user_ids.add(owner.user_id)
        return owner

    def list_all(self):
        return list(self._owners.values())


def test_create_owner_success():
    repo = MockOwnerRepository()
    use_case = CreateOwnerUseCase(owner_repository=repo)

    owner = use_case.execute(user_id=1, address="123 Main St")

    assert owner.user_id == 1
    assert owner.address == "123 Main St"


def test_create_owner_duplicate_user_raises():
    repo = MockOwnerRepository(existing_user_ids=[1])
    use_case = CreateOwnerUseCase(owner_repository=repo)

    with pytest.raises(OwnerAlreadyExistsError) as exc:
        use_case.execute(user_id=1, address="123 Main St")

    assert "already exists" in str(exc.value)
