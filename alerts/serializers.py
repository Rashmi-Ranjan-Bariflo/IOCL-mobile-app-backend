from rest_framework import serializers

from .models import (
    AlertType,
    Alert,
    AlertNotification,
)

# ==========================================================
#                      ALERT TYPE
# ==========================================================


class AlertTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AlertType
        fields = [
            "id",
            "name",
            "code",
            "category",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# ==========================================================
#                         ALERT
# ==========================================================


class AlertSerializer(serializers.ModelSerializer):

    # Display related object names in GET response
    plant_name = serializers.CharField(source="plant.name", read_only=True)
    plant_stage_name = serializers.CharField(source="plant_stage.name", read_only=True)
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)
    sensor_name = serializers.CharField(source="sensor.name", read_only=True)
    parameter_name = serializers.CharField(source="parameter.name", read_only=True)
    alert_type_name = serializers.CharField(source="alert_type.name", read_only=True)

    class Meta:
        model = Alert

        fields = [
            "id",
            # Relationships
            "plant",
            "plant_name",
            "plant_stage",
            "plant_stage_name",
            "equipment",
            "equipment_name",
            "sensor",
            "sensor_name",
            "parameter",
            "parameter_name",
            "alert_type",
            "alert_type_name",
            # Alert information
            "title",
            "message",
            "source",
            "severity",
            "status",
            # Values
            "current_value",
            "limit_value",
            "unit",
            # Time
            "triggered_at",
            "acknowledged_at",
            "resolved_at",
            # Additional
            "remarks",
            # System
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):

        current_value = data.get(
            "current_value", getattr(self.instance, "current_value", None)
        )

        limit_value = data.get(
            "limit_value", getattr(self.instance, "limit_value", None)
        )

        if current_value is not None and limit_value is not None:
            try:
                float(current_value)
                float(limit_value)
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    "Current value and limit value must be valid numbers."
                )

        return data


# ==========================================================
#                  ALERT NOTIFICATION
# ==========================================================


class AlertNotificationSerializer(serializers.ModelSerializer):

    alert_title = serializers.CharField(source="alert.title", read_only=True)

    class Meta:
        model = AlertNotification

        fields = [
            "id",
            "alert",
            "alert_title",
            "notification_type",
            "recipient",
            "status",
            "sent_at",
            "error_message",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
