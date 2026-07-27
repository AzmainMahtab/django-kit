"""Django admin configuration for otp."""

from django.contrib import admin

from backend.apps.otp.domain.models import OneTimePassword


@admin.register(OneTimePassword)
class OneTimePasswordAdmin(admin.ModelAdmin):
    """Read-only inspection of issued OTPs.

    ``code_hash`` is a credential and is never rendered. OTPs are issued and
    consumed through the domain use cases, so the admin deliberately offers no
    create or edit path — an operator changing one by hand would bypass the
    hashing, expiry and single-use rules.
    """

    list_display = ("user_id", "otp_type", "is_used", "expired", "expires_at", "created_at")
    list_filter = ("otp_type", "is_used")
    search_fields = ("=user_id",)
    ordering = ("-created_at",)
    exclude = ("code_hash",)
    readonly_fields = (
        "user_id",
        "otp_type",
        "is_used",
        "expires_at",
        "created_at",
        "updated_at",
    )

    @admin.display(boolean=True, description="Expired")
    def expired(self, obj):
        return obj.is_expired

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
