from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from infrastructure.django.models import UserModel


@admin.register(UserModel)
class UserModelAdmin(BaseUserAdmin):
    """Admin configuration for UserModel."""

    # Fields to display in the list view
    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    ]

    # Fields to filter by in the sidebar
    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    ]

    # Fields to search by
    search_fields = ["email", "first_name", "last_name"]

    # Default ordering
    ordering = ["-date_joined"]

    # Fieldsets for the edit form
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Informações Pessoais",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Datas Importantes",
            {"fields": ("last_login", "date_joined", "email_verified_at")},
        ),
        (
            "Informações de Acesso",
            {"fields": ("last_login_ip",)},
        ),
    )

    # Fieldsets for the add form
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    # Read-only fields
    readonly_fields = ["date_joined", "last_login", "last_login_ip"]
