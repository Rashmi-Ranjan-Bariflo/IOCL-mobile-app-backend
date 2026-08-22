from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "email",
        "phone",
        "password",
        "reset_otp",
        "reset_otp_created_at",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "email",
    )

    search_fields = (
        "email",
        "phone",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "reset_otp_created_at",
    )