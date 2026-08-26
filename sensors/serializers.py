from rest_framework import serializers

from .models import (
    SensorType,
    Sensor,
    SensorReading,
)


# ==========================================================
#                    SENSOR TYPE SERIALIZER
# ==========================================================
class SensorTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = SensorType

        fields = [
            "id",
            "name",
            "code",
            "description",
            "default_unit",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Sensor type name is required.")

        return value

    def validate_code(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError("Sensor type code is required.")

        return value

    def validate_default_unit(self, value):
        if value:
            return value.strip()

        return value


# ==========================================================
#                       SENSOR SERIALIZER
# ==========================================================
class SensorSerializer(serializers.ModelSerializer):

    sensor_type_name = serializers.CharField(
        source="sensor_type.name",
        read_only=True,
    )

    equipment_name = serializers.CharField(
        source="equipment.name",
        read_only=True,
    )

    class Meta:
        model = Sensor

        fields = [
            "id",
            "name",
            "code",
            "sensor_type",
            "sensor_type_name",
            "equipment",
            "equipment_name",
            "description",
            "location",
            "manufacturer",
            "model_number",
            "serial_number",
            "unit",
            "min_value",
            "max_value",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "sensor_type_name",
            "equipment_name",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Sensor name is required.")

        return value

    def validate_code(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError("Sensor code is required.")

        return value

    def validate_min_value(self, value):
        if value is not None:
            max_value = self.initial_data.get("max_value")

            if max_value is not None:
                try:
                    if float(value) >= float(max_value):
                        raise serializers.ValidationError(
                            "Minimum value must be less than maximum value."
                        )
                except (ValueError, TypeError):
                    pass

        return value

    def validate(self, attrs):

        min_value = attrs.get(
            "min_value",
            getattr(self.instance, "min_value", None) if self.instance else None,
        )

        max_value = attrs.get(
            "max_value",
            getattr(self.instance, "max_value", None) if self.instance else None,
        )

        if min_value is not None and max_value is not None and min_value >= max_value:
            raise serializers.ValidationError(
                {"max_value": ("Maximum value must be greater " "than minimum value.")}
            )

        return attrs


# ==========================================================
#                  SENSOR READING SERIALIZER
# ==========================================================
class SensorReadingSerializer(serializers.ModelSerializer):

    sensor_name = serializers.CharField(
        source="sensor.name",
        read_only=True,
    )

    sensor_code = serializers.CharField(
        source="sensor.code",
        read_only=True,
    )

    class Meta:
        model = SensorReading

        fields = [
            "id",
            "sensor",
            "sensor_name",
            "sensor_code",
            "value",
            "unit",
            "status",
            "recorded_at",
            "source",
            "raw_value",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "sensor_name",
            "sensor_code",
            "created_at",
        ]

    def validate_source(self, value):
        value = value.strip().upper()

        allowed_sources = [
            "MANUAL",
            "MQTT",
            "API",
        ]

        if value not in allowed_sources:
            raise serializers.ValidationError("Source must be MANUAL, MQTT or API.")

        return value

    def validate(self, attrs):

        sensor = attrs.get(
            "sensor",
            getattr(self.instance, "sensor", None) if self.instance else None,
        )

        value = attrs.get(
            "value",
            getattr(self.instance, "value", None) if self.instance else None,
        )

        if sensor and value is not None:

            if sensor.min_value is not None and value < sensor.min_value:
                attrs["status"] = "LOW"

            elif sensor.max_value is not None and value > sensor.max_value:
                attrs["status"] = "HIGH"

            else:
                attrs["status"] = "NORMAL"

        return attrs
