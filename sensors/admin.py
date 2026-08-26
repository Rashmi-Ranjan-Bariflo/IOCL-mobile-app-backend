from django.contrib import admin

from .models import (
    SensorType,
    Sensor,
    SensorReading,
)


# ==========================================================
#                    SENSOR TYPE ADMIN
# ==========================================================
@admin.register(SensorType)
class SensorTypeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "code",
        "default_unit",
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
        "description",
    )

    list_filter = ("is_active",)

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ==========================================================
#                       SENSOR ADMIN
# ==========================================================
@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "code",
        "sensor_type",
        "equipment",
        "unit",
        "status",
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
        "serial_number",
        "manufacturer",
        "model_number",
        "location",
    )

    list_filter = (
        "status",
        "is_active",
        "sensor_type",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "sensor_type",
        "equipment",
    )


# ==========================================================
#                  SENSOR READING ADMIN
# ==========================================================
@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "sensor",
        "value",
        "unit",
        "status",
        "source",
        "recorded_at",
        "created_at",
    )

    list_display_links = (
        "id",
        "sensor",
    )

    search_fields = (
        "sensor__name",
        "sensor__code",
        "source",
        "raw_value",
    )

    list_filter = (
        "status",
        "source",
        "recorded_at",
    )

    ordering = ("-recorded_at",)

    readonly_fields = ("created_at",)

    autocomplete_fields = ("sensor",)

    date_hierarchy = "recorded_at"
