"""Create user command."""

from backend.apps.identity.domain.events import UserCreated
from backend.apps.identity.domain.models import User
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus
from backend.shared.exceptions import BusinessValidationError
from backend.shared.types import UserDTO


class CreateUserUseCase(UseCase):
    """Create a new user and publish a domain event."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def execute(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        phone: str = "",
        is_staff: bool = False,
        is_active: bool = True,
    ) -> UserDTO:
        if User.objects.filter(email__iexact=email).exists():
            raise BusinessValidationError("A user with this email already exists.")

        if User.objects.filter(username__iexact=username).exists():
            raise BusinessValidationError("A user with this username already exists.")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            is_staff=is_staff,
            is_active=is_active,
        )

        self.event_bus.publish(
            UserCreated(
                aggregate_id=user.id,
                data={
                    "user_id": user.id,
                    "email": user.email,
                    "username": user.username,
                },
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
