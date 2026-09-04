from django.contrib import admin

from .models import (
    AlertType,
    Alert,
    AlertNotification,
)

# ==========================================================
#                      ALERT TYPE
# ==========================================================


@admin.register(AlertType)
class AlertTypeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "code",
        "category",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
        "description",
    )

    ordering = ("name",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ==========================================================
#                         ALERT
# ==========================================================


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "equipment",
        "sensor",
        "parameter",
        "alert_type",
        "source",
        "severity",
        "status",
        "current_value",
        "limit_value",
        "triggered_at",
    )

    list_filter = (
        "source",
        "severity",
        "status",
        "alert_type",
        "triggered_at",
    )

    search_fields = (
        "title",
        "message",
        "remarks",
        "equipment__name",
        "sensor__name",
        "parameter__name",
        "alert_type__name",
    )

    ordering = ("-triggered_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Alert Source",
            {
                "fields": (
                    "equipment",
                    "sensor",
                    "parameter",
                    "alert_type",
                    "source",
                )
            },
        ),
        (
            "Alert Details",
            {
                "fields": (
                    "title",
                    "message",
                    "severity",
                    "status",
                )
            },
        ),
        (
            "Measured Values",
            {
                "fields": (
                    "current_value",
                    "limit_value",
                    "unit",
                )
            },
        ),
        (
            "Time Information",
            {
                "fields": (
                    "triggered_at",
                    "acknowledged_at",
                    "resolved_at",
                )
            },
        ),
        (
            "Additional Information",
            {"fields": ("remarks",)},
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


# ==========================================================
#                  ALERT NOTIFICATION
# ==========================================================


@admin.register(AlertNotification)
class AlertNotificationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "alert",
        "notification_type",
        "recipient",
        "status",
        "sent_at",
        "created_at",
    )

    list_filter = (
        "notification_type",
        "status",
        "created_at",
    )

    search_fields = (
        "recipient",
        "alert__title",
        "alert__message",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Notification",
            {
                "fields": (
                    "alert",
                    "notification_type",
                    "recipient",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "status",
                    "sent_at",
                    "error_message",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
