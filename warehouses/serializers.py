from rest_framework import serializers
from .models import (
    Warehouse,
    WarehouseZone,
    WarehouseItem,
    WarehouseStock,
    WarehouseStockMovement,
)


class WarehouseSerializer(serializers.ModelSerializer):
    warehouse_type_display = serializers.CharField(
        source="get_warehouse_type_display", read_only=True
    )

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "name",
            "code",
            "warehouse_type",
            "warehouse_type_display",
            "location",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "code", "created_at", "updated_at"]


class WarehouseZoneSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)

    class Meta:
        model = WarehouseZone
        fields = [
            "id",
            "warehouse",
            "warehouse_name",
            "warehouse_code",
            "name",
            "code",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WarehouseItemSerializer(serializers.ModelSerializer):
    unit_display = serializers.CharField(source="get_unit_display", read_only=True)
    equipment_name = serializers.CharField(source="equipment.name", read_only=True, default=None)
    equipment_code = serializers.CharField(source="equipment.code", read_only=True, default=None)

    class Meta:
        model = WarehouseItem
        fields = [
            "id",
            "name",
            "code",
            "unit",
            "unit_display",
            "description",
            "equipment",
            "equipment_name",
            "equipment_code",
            "minimum_stock",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "code", "created_at", "updated_at"]


class WarehouseStockSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_code = serializers.CharField(source="item.code", read_only=True)
    item_unit = serializers.CharField(source="item.unit", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    warehouse_type = serializers.CharField(source="warehouse.warehouse_type", read_only=True)
    zone_name = serializers.CharField(source="zone.name", read_only=True, default=None)
    available_quantity = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = WarehouseStock
        fields = [
            "id",
            "item",
            "item_name",
            "item_code",
            "item_unit",
            "warehouse",
            "warehouse_name",
            "warehouse_code",
            "warehouse_type",
            "zone",
            "zone_name",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "quantity", "reserved_quantity", "created_at", "updated_at"]


class WarehouseStockMovementSerializer(serializers.ModelSerializer):
    movement_type_display = serializers.CharField(
        source="get_movement_type_display", read_only=True
    )
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_code = serializers.CharField(source="item.code", read_only=True)
    from_warehouse_name = serializers.CharField(
        source="from_warehouse.name", read_only=True, default=None
    )
    from_warehouse_code = serializers.CharField(
        source="from_warehouse.code", read_only=True, default=None
    )
    to_warehouse_name = serializers.CharField(
        source="to_warehouse.name", read_only=True, default=None
    )
    to_warehouse_code = serializers.CharField(
        source="to_warehouse.code", read_only=True, default=None
    )
    equipment_name = serializers.CharField(
        source="equipment.name", read_only=True, default=None
    )
    equipment_code = serializers.CharField(
        source="equipment.code", read_only=True, default=None
    )
    treatment_stage_name = serializers.CharField(
        source="treatment_stage.name", read_only=True, default=None
    )

    class Meta:
        model = WarehouseStockMovement
        fields = [
            "id",
            "item",
            "item_name",
            "item_code",
            "movement_type",
            "movement_type_display",
            "from_warehouse",
            "from_warehouse_name",
            "from_warehouse_code",
            "to_warehouse",
            "to_warehouse_name",
            "to_warehouse_code",
            "quantity",
            "equipment",
            "equipment_name",
            "equipment_code",
            "treatment_stage",
            "treatment_stage_name",
            "reference_number",
            "remarks",
            "transaction_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]



class WarehouseStockInSerializer(serializers.Serializer):
    item = serializers.PrimaryKeyRelatedField(queryset=WarehouseItem.objects.all())
    to_warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all())
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    zone = serializers.PrimaryKeyRelatedField(
        queryset=WarehouseZone.objects.all(), required=False, allow_null=True
    )
    reference_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    transaction_date = serializers.DateTimeField(required=False)


class WarehouseDeploySerializer(serializers.Serializer):
    item = serializers.PrimaryKeyRelatedField(queryset=WarehouseItem.objects.all())
    from_warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all())
    to_warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all())
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    equipment = serializers.IntegerField(required=False, allow_null=True)
    treatment_stage = serializers.IntegerField(required=False, allow_null=True)
    reference_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    transaction_date = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        from equipment.models import Equipment
        from treatment_process.models import TreatmentStage

        equipment_id = attrs.get("equipment")
        if equipment_id is not None:
            try:
                attrs["equipment"] = Equipment.objects.get(pk=equipment_id)
            except Equipment.DoesNotExist:
                raise serializers.ValidationError({"equipment": "Invalid equipment id."})

        stage_id = attrs.get("treatment_stage")
        if stage_id is not None:
            try:
                attrs["treatment_stage"] = TreatmentStage.objects.get(pk=stage_id)
            except TreatmentStage.DoesNotExist:
                raise serializers.ValidationError({"treatment_stage": "Invalid treatment stage id."})

        return attrs


class WarehouseReturnSerializer(serializers.Serializer):
    item = serializers.PrimaryKeyRelatedField(queryset=WarehouseItem.objects.all())
    from_warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all())
    to_warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all())
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    equipment = serializers.IntegerField(required=False, allow_null=True)
    reference_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    transaction_date = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        from equipment.models import Equipment

        equipment_id = attrs.get("equipment")
        if equipment_id is not None:
            try:
                attrs["equipment"] = Equipment.objects.get(pk=equipment_id)
            except Equipment.DoesNotExist:
                raise serializers.ValidationError({"equipment": "Invalid equipment id."})
        return attrs


class WarehouseStockOutSerializer(serializers.Serializer):
    item = serializers.PrimaryKeyRelatedField(queryset=WarehouseItem.objects.all())
    from_warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all())
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    reference_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    transaction_date = serializers.DateTimeField(required=False)


class WarehouseAdjustmentSerializer(serializers.Serializer):
    item = serializers.PrimaryKeyRelatedField(queryset=WarehouseItem.objects.all())
    warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all())
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    transaction_date = serializers.DateTimeField(required=False)

    def validate_quantity(self, value):
        if value == 0:
            raise serializers.ValidationError("Quantity cannot be zero.")
        return value