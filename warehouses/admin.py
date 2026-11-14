from django.contrib import admin
from .models import (
    Warehouse,
    WarehouseZone,
    WarehouseItem,
    WarehouseStock,
    WarehouseStockMovement,
)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "warehouse_type",
        "user",
        "location",
        "is_active",
        "created_at",
    )
    list_filter = ("warehouse_type", "is_active", "created_at")
    search_fields = ("code", "name", "location", "user__email")
    readonly_fields = ("code", "created_at", "updated_at")
    ordering = ("name",)


@admin.register(WarehouseZone)
class WarehouseZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "warehouse", "is_active", "created_at")
    list_filter = ("is_active", "warehouse__warehouse_type")
    search_fields = ("name", "code", "warehouse__code", "warehouse__name")
    ordering = ("name",)


@admin.register(WarehouseItem)
class WarehouseItemAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "unit",
        "user",
        "equipment",
        "minimum_stock",
        "is_active",
        "created_at",
    )
    list_filter = ("unit", "is_active", "created_at")
    search_fields = (
        "code",
        "name",
        "user__email",
        "equipment__name",
        "equipment__code",
    )
    readonly_fields = ("code", "created_at", "updated_at")
    raw_id_fields = ("equipment",)
    ordering = ("name",)


@admin.register(WarehouseStock)
class WarehouseStockAdmin(admin.ModelAdmin):
    list_display = (
        "item",
        "warehouse",
        "zone",
        "quantity",
        "reserved_quantity",
        "available_quantity_display",
        "updated_at",
    )
    list_filter = ("warehouse__warehouse_type", "warehouse")
    search_fields = ("item__code", "item__name", "warehouse__code", "warehouse__name")
    raw_id_fields = ("item", "warehouse", "zone")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Available")
    def available_quantity_display(self, obj):
        return obj.available_quantity


@admin.register(WarehouseStockMovement)
class WarehouseStockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "movement_type",
        "item",
        "quantity",
        "from_warehouse",
        "to_warehouse",
        "equipment",
        "transaction_date",
        "user",
    )
    list_filter = (
        "movement_type",
        "transaction_date",
        "from_warehouse__warehouse_type",
        "to_warehouse__warehouse_type",
    )
    search_fields = (
        "item__code",
        "item__name",
        "reference_number",
        "remarks",
        "from_warehouse__code",
        "to_warehouse__code",
        "equipment__code",
        "user__email",
    )
    raw_id_fields = (
        "item",
        "from_warehouse",
        "to_warehouse",
        "equipment",
        "treatment_stage",
        "user",
    )
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "transaction_date"
    ordering = ("-transaction_date", "-id")
