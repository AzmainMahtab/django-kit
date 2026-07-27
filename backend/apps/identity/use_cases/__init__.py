"""Public API for the identity module.

★ THIS IS THE ONLY FILE OTHER MODULES CAN IMPORT FROM THIS APP ★
"""

from backend.apps.identity.use_cases.commands.create_user import CreateUserUseCase
from backend.apps.identity.use_cases.commands.delete_user import DeleteUserUseCase
from backend.apps.identity.use_cases.commands.login import LoginUseCase
from backend.apps.identity.use_cases.commands.logout import LogoutUseCase
from backend.apps.identity.use_cases.commands.refresh_token import RefreshTokenUseCase
from backend.apps.identity.use_cases.commands.update_user import UpdateUserUseCase
from backend.apps.identity.use_cases.queries.get_profile import GetProfileUseCase
from backend.apps.identity.use_cases.queries.get_user import GetUserUseCase
from backend.apps.identity.use_cases.queries.list_users import ListUsersUseCase
from backend.shared.event_bus import EventBus


class IdentityUseCases:
    """Facade that other modules use. Internal structure is hidden."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self.commands = IdentityCommands(event_bus=event_bus)
        self.queries = IdentityQueries()

    def create_user(self, **kwargs):
        return self.commands.create_user.execute(**kwargs)

    def update_user(self, **kwargs):
        return self.commands.update_user.execute(**kwargs)

    def delete_user(self, **kwargs):
        return self.commands.delete_user.execute(**kwargs)

    def login(self, **kwargs):
        return self.commands.login.execute(**kwargs)

    def logout(self, **kwargs):
        return self.commands.logout.execute(**kwargs)

    def refresh_token(self, **kwargs):
        return self.commands.refresh_token.execute(**kwargs)

    def get_user(self, **kwargs):
        return self.queries.get_user.execute(**kwargs)

    def list_users(self, **kwargs):
        return self.queries.list_users.execute(**kwargs)

    def get_profile(self, **kwargs):
        return self.queries.get_profile.execute(**kwargs)


class IdentityCommands:
    def __init__(self, event_bus: EventBus) -> None:
        self.create_user = CreateUserUseCase(event_bus=event_bus)
        self.update_user = UpdateUserUseCase(event_bus=event_bus)
        self.delete_user = DeleteUserUseCase(event_bus=event_bus)
        self.login = LoginUseCase(event_bus=event_bus)
        self.logout = LogoutUseCase(event_bus=event_bus)
        self.refresh_token = RefreshTokenUseCase(event_bus=event_bus)


class IdentityQueries:
    def __init__(self):
        self.get_user = GetUserUseCase()
        self.list_users = ListUsersUseCase()
        self.get_profile = GetProfileUseCase()
