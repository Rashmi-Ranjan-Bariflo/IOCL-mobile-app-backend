from django.contrib import admin

from .models import (
    WaterQualityParameter,
    WaterQualityReading,
)

# ==========================================================
#                WATER QUALITY PARAMETER
# ==========================================================


@admin.register(WaterQualityParameter)
class WaterQualityParameterAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "code",
        "unit",
        "min_value",
        "max_value",
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
        "code",
    )

    list_filter = ("is_active",)

    ordering = ("name",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ==========================================================
#                WATER QUALITY READING
# ==========================================================


@admin.register(WaterQualityReading)
class WaterQualityReadingAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "parameter",
        "sensor",
        "value",
        "unit",
        "source",
        "status",
        "recorded_at",
        "created_at",
    )

    list_display_links = (
        "id",
        "parameter",
    )

    search_fields = (
        "parameter__name",
        "parameter__code",
        "sensor__name",
        "sensor__code",
    )

    list_filter = (
        "source",
        "status",
        "recorded_at",
    )

    ordering = ("-recorded_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "parameter",
        "sensor",
    )
