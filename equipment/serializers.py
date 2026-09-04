from rest_framework import serializers

from .models import (
    EquipmentType,
    Equipment,
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

    class Meta:
        model = Equipment

        fields = [
            "id",
            "name",
            "code",
            "equipment_type",
            "equipment_type_name",
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
