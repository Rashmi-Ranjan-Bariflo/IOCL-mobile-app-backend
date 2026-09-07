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

# =======================================================================================================================================================
# equipment/serializers.py

from rest_framework import serializers
from .models import Equipment, EquipmentType, EquipmentManualLog


class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = ["id", "name", "description", "is_active"]


class EquipmentSerializer(serializers.ModelSerializer):
    equipment_type = EquipmentTypeSerializer(read_only=True)
    equipment_type_id = serializers.PrimaryKeyRelatedField(
        queryset=EquipmentType.objects.all(),
        source="equipment_type",
        write_only=True
    )

    class Meta:
        model = Equipment
        fields = [
            "id",
            "name",
            "code",
            "equipment_type",
            "equipment_type_id",
            "description",
            "location",
            "manufacturer",
            "model_number",
            "serial_number",
            "start_time",
            "end_time",
            "duration_seconds",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "duration_seconds"]


class EquipmentOnOffSerializer(serializers.Serializer):
    """Input serializer for ON / OFF actions"""
    stage_id = serializers.IntegerField(required=False, allow_null=True)
    process_id = serializers.IntegerField(required=False, allow_null=True)


class EquipmentManualLogSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)
    equipment_code = serializers.CharField(source="equipment.code", read_only=True)
    stage_name = serializers.CharField(source="stage.name", read_only=True)
    performed_by_name = serializers.CharField(source="performed_by.username", read_only=True)

    class Meta:
        model = EquipmentManualLog
        fields = [
            "id",
            "equipment",
            "equipment_name",
            "equipment_code",
            "stage",
            "stage_name",
            "action",
            "started_at",
            "ended_at",
            "duration_seconds",
            "performed_by",
            "performed_by_name",
            "created_at",
        ]
        read_only_fields = ["duration_seconds", "created_at"]