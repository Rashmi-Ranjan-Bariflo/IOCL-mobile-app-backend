from rest_framework import serializers

from .models import (
    ProcessParameter,
    ProcessReading,
    EquipmentStatus,
)

# ==========================================================
#              PROCESS PARAMETER SERIALIZER
# ==========================================================


class ProcessParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcessParameter

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


# ==========================================================
#              PROCESS READING SERIALIZER
# ==========================================================


class ProcessReadingSerializer(serializers.ModelSerializer):

    equipment_name = serializers.CharField(source="equipment.name", read_only=True)

    sensor_name = serializers.CharField(source="sensor.name", read_only=True)

    parameter_name = serializers.CharField(source="parameter.name", read_only=True)

    class Meta:
        model = ProcessReading

        fields = [
            "id",
            # IDs
            "equipment",
            "sensor",
            "parameter",
            # Names
            "equipment_name",
            "sensor_name",
            "parameter_name",
            # Reading data
            "value",
            "unit",
            "source",
            "status",
            "recorded_at",
            "remarks",
            # Timestamps
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "equipment_name",
            "sensor_name",
            "parameter_name",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        parameter = attrs.get("parameter")
        unit = attrs.get("unit")
        value = attrs.get("value")

        # --------------------------------------------------
        # Validate Unit
        # --------------------------------------------------

        if parameter and unit:

            if parameter.unit and parameter.unit != unit:

                raise serializers.ValidationError(
                    {
                        "unit": (
                            f"Unit should be "
                            f"'{parameter.unit}' for "
                            f"{parameter.name}."
                        )
                    }
                )

        # --------------------------------------------------
        # Validate Parameter Range
        # --------------------------------------------------

        if parameter and value is not None:

            if parameter.min_value is not None and value < parameter.min_value:
                attrs["status"] = "WARNING"

            if parameter.max_value is not None and value > parameter.max_value:
                attrs["status"] = "WARNING"

        return attrs


# ==========================================================
#              EQUIPMENT STATUS SERIALIZER
# ==========================================================


class EquipmentStatusSerializer(serializers.ModelSerializer):

    equipment_name = serializers.CharField(source="equipment.name", read_only=True)

    class Meta:
        model = EquipmentStatus

        fields = [
            "id",
            # Equipment
            "equipment",
            "equipment_name",
            # Status
            "status",
            "recorded_at",
            "remarks",
            # Timestamps
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "equipment_name",
            "created_at",
            "updated_at",
        ]
