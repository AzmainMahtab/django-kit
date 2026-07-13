"""Django ORM implementation of the owner repository."""

from typing import Iterable

from backend.apps.owner.domain.models import Owner
from backend.apps.owner.domain.repository_interfaces import OwnerRepositoryInterface


class OwnerRepository(OwnerRepositoryInterface):
    """Implements OwnerRepositoryInterface using Django ORM."""

    def get_by_id(self, owner_id: int) -> Owner:
        return Owner.objects.get(pk=owner_id)

    def get_by_uuid(self, uuid: str) -> Owner | None:
        try:
            return Owner.objects.get(uuid=uuid)
        except Owner.DoesNotExist:
            return None

    def get_by_user_id(self, user_id: int) -> Owner | None:
        try:
            return Owner.objects.get(user_id=user_id)
        except Owner.DoesNotExist:
            return None

    def create(self, owner: Owner) -> Owner:
        owner.save()
        return owner

    def list_all(self) -> Iterable[Owner]:
        return Owner.objects.all().order_by("-created_at")
