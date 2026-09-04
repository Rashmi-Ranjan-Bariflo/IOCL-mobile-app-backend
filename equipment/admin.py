from django.contrib import admin

from .models import (
    EquipmentType,
    Equipment,
)


# ==========================================================
#                  EQUIPMENT TYPE ADMIN
# ==========================================================
@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "description",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "description",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ==========================================================
#                     EQUIPMENT ADMIN
# ==========================================================
@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "code",
        "equipment_type",
        "location",
        "manufacturer",
        "model_number",
        "serial_number",
        "status",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "name",
        "code",
    )

    search_fields = (
        "name",
        "code",
        "location",
        "manufacturer",
        "model_number",
        "serial_number",
    )

    list_filter = (
        "equipment_type",
        "status",
        "is_active",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "equipment_type",
    )