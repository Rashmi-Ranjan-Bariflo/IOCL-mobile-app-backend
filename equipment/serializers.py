from rest_framework import serializers

from .models import (
    EquipmentType,
    Equipment,
    EquipmentStage,
)


# ==========================================================
#                  EQUIPMENT TYPE SERIALIZER
# ==========================================================
class EquipmentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EquipmentType

        fields = [
            "id",
            "name",
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

    # ------------------------------------------------------
    # Validate Name
    # ------------------------------------------------------
    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError("Equipment type name is required.")

        return value


# ==========================================================
#                     EQUIPMENT SERIALIZER
# ==========================================================
class EquipmentSerializer(serializers.ModelSerializer):

    equipment_type_name = serializers.CharField(
        source="equipment_type.name",
        read_only=True,
    )

    plant_name = serializers.CharField(
        source="plant.name",
        read_only=True,
    )

    class Meta:
        model = Equipment

        fields = [
            "id",
            "name",
            "code",
            "equipment_type",
            "equipment_type_name",
            "plant",
            "plant_name",
            "description",
            "location",
            "manufacturer",
            "model_number",
            "serial_number",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "equipment_type_name",
            "plant_name",
            "created_at",
            "updated_at",
        ]

    # ------------------------------------------------------
    # Validate Name
    # ------------------------------------------------------
    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError("Equipment name is required.")

        return value

    # ------------------------------------------------------
    # Validate Code
    # ------------------------------------------------------
    def validate_code(self, value):

        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError("Equipment code is required.")

        # Check duplicate code during create/update
        queryset = Equipment.objects.filter(code__iexact=value)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("Equipment code already exists.")

        return value

    # ------------------------------------------------------
    # Validate Status
    # ------------------------------------------------------
    def validate_status(self, value):

        valid_statuses = [
            "ACTIVE",
            "INACTIVE",
            "MAINTENANCE",
            "FAULT",
        ]

        if value not in valid_statuses:
            raise serializers.ValidationError("Invalid equipment status.")

        return value


# ==========================================================
#                  EQUIPMENT STAGE SERIALIZER
# ==========================================================
class EquipmentStageSerializer(serializers.ModelSerializer):

    equipment_name = serializers.CharField(
        source="equipment.name",
        read_only=True,
    )

    equipment_code = serializers.CharField(
        source="equipment.code",
        read_only=True,
    )

    plant_stage_name = serializers.CharField(
        source="plant_stage.name",
        read_only=True,
    )

    class Meta:
        model = EquipmentStage

        fields = [
            "id",
            "equipment",
            "equipment_name",
            "equipment_code",
            "plant_stage",
            "plant_stage_name",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "equipment_name",
            "equipment_code",
            "plant_stage_name",
            "created_at",
            "updated_at",
        ]

    # ------------------------------------------------------
    # Validate Equipment + Stage Combination
    # ------------------------------------------------------
    def validate(self, attrs):

        equipment = attrs.get(
            "equipment",
            getattr(
                self.instance,
                "equipment",
                None,
            ),
        )

        plant_stage = attrs.get(
            "plant_stage",
            getattr(
                self.instance,
                "plant_stage",
                None,
            ),
        )

        if equipment and plant_stage:

            queryset = EquipmentStage.objects.filter(
                equipment=equipment,
                plant_stage=plant_stage,
            )

            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            "This equipment is already assigned " "to this plant stage."
                        ]
                    }
                )

        return attrs
