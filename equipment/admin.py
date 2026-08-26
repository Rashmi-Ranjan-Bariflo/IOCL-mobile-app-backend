from django.contrib import admin
from .models import (
    EquipmentType,
    Equipment,
    EquipmentStage,
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

    list_filter = ("is_active",)

    ordering = ("name",)

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
        "plant",
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
        "plant",
        "status",
        "is_active",
    )

    ordering = ("name",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "equipment_type",
        "plant",
    )


# ==========================================================
#                  EQUIPMENT STAGE ADMIN
# ==========================================================
@admin.register(EquipmentStage)
class EquipmentStageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "equipment",
        "plant_stage",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "equipment",
    )

    search_fields = (
        "equipment__name",
        "equipment__code",
        "plant_stage__plant__name",
        "plant_stage__treatment_stage__name",
    )

    list_filter = (
        "is_active",
        "plant_stage__plant",
        "plant_stage__treatment_stage",
    )

    ordering = ("equipment__name",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "equipment",
        "plant_stage",
    )
