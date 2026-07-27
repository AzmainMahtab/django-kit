"""Get owner queries."""

from backend.apps.owner.domain.exceptions import OwnerNotFoundError
from backend.apps.owner.domain.models import Owner
from backend.shared.domain import UseCase


class GetOwnerByIdUseCase(UseCase):
    """Pure read: fetch an owner by primary key."""

    def execute(self, owner_id: int) -> Owner:
        try:
            return Owner.objects.get(pk=owner_id)
        except Owner.DoesNotExist as exc:
            raise OwnerNotFoundError(f"Owner with id {owner_id} not found.") from exc


class GetOwnerByUuidUseCase(UseCase):
    """Pure read: fetch an owner by UUID."""

    def execute(self, uuid: str) -> Owner:
        owner = Owner.objects.get_by_uuid(uuid)
        if owner is None:
            raise OwnerNotFoundError(f"Owner with uuid {uuid} not found.")
        return owner


class GetOwnerByUserIdUseCase(UseCase):
    """Pure read: fetch an owner by associated user id."""

    def execute(self, user_id: int) -> Owner:
        owner = Owner.objects.get_by_user_id(user_id)
        if owner is None:
            raise OwnerNotFoundError(f"Owner for user {user_id} not found.")
        return owner
