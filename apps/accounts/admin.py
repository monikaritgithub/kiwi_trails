"""Admin site registrations for user accounts.
Configures custom user model presentation inside Django admin.
Provides search filtering and field grouping for administrators.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import User


class UserAdmin(BaseUserAdmin):
    list_display = ("email", "full_name", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    ordering = ("email",)
    search_fields = ("email", "full_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name", "phone")}),
        (
            "Permissions",
            {"fields": ("role", "is_active", "is_superuser", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "password", "role"),
            },
        ),
    )


admin.site.register(User, UserAdmin)
