from django.contrib import admin

from .models import (
    ProcessParameter,
    ProcessReading,
    EquipmentStatus,
)

# ==========================================================
#              PROCESS PARAMETER ADMIN
# ==========================================================


@admin.register(ProcessParameter)
class ProcessParameterAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "code",
        "unit",
        "min_value",
        "max_value",
        "is_active",
        "created_at",
    )

    list_filter = ("is_active",)

    search_fields = (
        "name",
        "code",
        "description",
    )

    ordering = ("name",)


# ==========================================================
#              PROCESS READING ADMIN
# ==========================================================


@admin.register(ProcessReading)
class ProcessReadingAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "equipment",
        "sensor",
        "parameter",
        "value",
        "unit",
        "source",
        "status",
        "recorded_at",
    )

    list_filter = (
        "source",
        "status",
        "parameter",
        "recorded_at",
    )

    search_fields = (
        "equipment__name",
        "sensor__name",
        "parameter__name",
    )

    ordering = ("-recorded_at",)

    date_hierarchy = "recorded_at"

    list_select_related = (
        "equipment",
        "sensor",
        "parameter",
    )


# ==========================================================
#              EQUIPMENT STATUS ADMIN
# ==========================================================


@admin.register(EquipmentStatus)
class EquipmentStatusAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "equipment",
        "status",
        "recorded_at",
        "created_at",
    )

    list_filter = (
        "status",
        "recorded_at",
    )

    search_fields = (
        "equipment__name",
        "remarks",
    )

    ordering = ("-recorded_at",)

    date_hierarchy = "recorded_at"

    list_select_related = ("equipment",)
