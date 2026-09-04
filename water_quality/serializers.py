from rest_framework import serializers

from .models import (
    WaterQualityParameter,
    WaterQualityReading,
)

# ==========================================================
#              WATER QUALITY PARAMETER
# ==========================================================


class WaterQualityParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = WaterQualityParameter

        fields = [
            "id",
            "name",
            "code",
            "unit",
            "description",
            "min_value",
            "max_value",
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
            raise serializers.ValidationError("Parameter name is required.")

        return value

    def validate_code(self, value):

        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError("Parameter code is required.")

        return value

    def validate(self, data):

        min_value = data.get("min_value")
        max_value = data.get("max_value")

        if min_value is not None and max_value is not None and min_value >= max_value:
            raise serializers.ValidationError(
                "Minimum value must be less than maximum value."
            )

        return data


# ==========================================================
#              WATER QUALITY READING
# ==========================================================


class WaterQualityReadingSerializer(serializers.ModelSerializer):

    parameter_name = serializers.CharField(
        source="parameter.name",
        read_only=True,
    )

    parameter_code = serializers.CharField(
        source="parameter.code",
        read_only=True,
    )

    sensor_name = serializers.CharField(
        source="sensor.name",
        read_only=True,
    )

    class Meta:
        model = WaterQualityReading

        fields = [
            "id",
            "parameter",
            "sensor",
            "parameter_name",
            "parameter_code",
            "sensor_name",
            "value",
            "unit",
            "source",
            "status",
            "recorded_at",
            "remarks",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "parameter_name",
            "parameter_code",
            "sensor_name",
            "created_at",
            "updated_at",
        ]

    def validate_value(self, value):

        if value is None:
            raise serializers.ValidationError("Reading value is required.")

        return value

    def validate_unit(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError("Unit is required.")

        return value

    def validate(self, data):

        source = data.get("source", getattr(self.instance, "source", "SENSOR"))

        sensor = data.get("sensor", getattr(self.instance, "sensor", None))

        # Sensor is mandatory for sensor-based readings
        if source == "SENSOR" and sensor is None:

            raise serializers.ValidationError(
                {"sensor": ("Sensor is required when " "source is SENSOR.")}
            )

        # Sensor should not be provided for LAB or MANUAL readings
        if source in ["LAB", "MANUAL"] and sensor is not None:

            raise serializers.ValidationError(
                {"sensor": ("Sensor should be empty for " "LAB or MANUAL readings.")}
            )

        return data
