"""Identity domain models."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model used as the project's AUTH_USER_MODEL."""

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=32, blank=True, default="")
    is_email_verified = models.BooleanField(default=False)
    # Mirrors the legacy Elite4Print user UUID so migrated slice data can
    # preserve the original identifier without changing the internal PK.
    legacy_id = models.UUIDField(null=True, blank=True, unique=True, db_index=True)

    class Meta:
        db_table = "identity_user"
        verbose_name = "user"
        verbose_name_plural = "users"
