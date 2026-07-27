"""Update user command."""

from backend.apps.identity.domain.events import UserUpdated
from backend.apps.identity.domain.models import User
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus
from backend.shared.exceptions import BusinessValidationError, NotFoundError
from backend.shared.types import UserDTO


class UpdateUserUseCase(UseCase):
    """Update an existing user."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def execute(self, user_id: int, **fields) -> UserDTO:
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise NotFoundError(f"User with id {user_id} not found.") from exc

        email = fields.get("email")
        if email and email.lower() != user.email.lower():
            if User.objects.filter(email__iexact=email).exclude(pk=user_id).exists():
                raise BusinessValidationError("A user with this email already exists.")

        username = fields.get("username")
        if username and username.lower() != user.username.lower():
            if User.objects.filter(username__iexact=username).exclude(pk=user_id).exists():
                raise BusinessValidationError("A user with this username already exists.")

        password = fields.pop("password", None)
        for key, value in fields.items():
            if hasattr(user, key):
                setattr(user, key, value)

        if password:
            user.set_password(password)

        user.save()

        self.event_bus.publish(
            UserUpdated(
                aggregate_id=user.id,
                data={"user_id": user.id, "email": user.email, "username": user.username},
            )
        )

        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_staff=user.is_staff,
            is_active=user.is_active,
        )
