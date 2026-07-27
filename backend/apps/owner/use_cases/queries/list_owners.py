"""List owners query."""

from backend.apps.owner.domain.models import Owner
from backend.shared.domain import UseCase


class ListOwnersUseCase(UseCase):
    """Pure read: list all owner profiles."""

    def execute(self):
        return Owner.objects.all().order_by("-created_at")
