"""Django ORM implementation of the user repository."""

from typing import Iterable

from backend.apps.identity.domain.models import User
from backend.apps.identity.domain.repository_interfaces import UserRepositoryInterface


class UserRepository(UserRepositoryInterface):
    """Implements UserRepositoryInterface using Django ORM."""

    def get_by_id(self, user_id: int) -> User:
        return User.objects.get(pk=user_id)

    def get_by_email(self, email: str) -> User:
        return User.objects.get(email__iexact=email)

    def list_users(self, filters: dict = None) -> Iterable[User]:
        qs = User.objects.all().order_by("-date_joined")
        if filters:
            qs = qs.filter(**filters)
        return qs

    def create(self, **kwargs) -> User:
        password = kwargs.pop("password", None)
        user = User(**kwargs)
        if password:
            user.set_password(password)
        user.save()
        return user

    def save(self, user: User, update_fields: list[str] = None) -> User:
        if update_fields:
            user.save(update_fields=update_fields)
        else:
            user.save()
        return user

    def delete(self, user: User) -> None:
        user.delete()
