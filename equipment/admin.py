from django.contrib import admin
from .models import EquipmentType, Equipment, EquipmentTest, EquipmentManualLog


# ==========================================================
#                  EQUIPMENT TYPE ADMIN
# ==========================================================
@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "description",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_display_links = ("id", "name")
    search_fields = ("name", "description")
    list_filter = ("is_active",)
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


# ==========================================================
#                     EQUIPMENT ADMIN
# ==========================================================
@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "code",
        "equipment_type",
        "description",
        "serial_number",
        "duration_seconds",
        "current_state",
        "get_stages",  # ← Added
        "status",
        "is_active",
        "created_at",
    )

    list_display_links = ("id", "name", "code")

    search_fields = (
        "name",
        "code",
        "location",
        "manufacturer",
        "model_number",
        "serial_number",
    )

    list_filter = (
        "equipment_type",
        "status",
        "is_active",
    )

    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("equipment_type",)

    def get_stages(self, obj):
        """Show all stages this equipment is connected to"""
        stages = obj.treatment_stages.all()
        if stages.exists():
            return ", ".join([stage.name for stage in stages])
        return "-"

    get_stages.short_description = "Stages"


# ==========================================================
#                  EQUIPMENT TEST ADMIN
# ==========================================================
@admin.register(EquipmentTest)
class EquipmentTestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "equipment",
        "stage",
        "start_time",
        "end_time",
        "duration_seconds",
        "status",
        "tested_by",
        "is_merged",
        "merged_at",
    )

    list_filter = ("status", "is_merged", "stage")
    search_fields = ("equipment__name", "equipment__code")
    autocomplete_fields = ("equipment", "stage", "tested_by", "merged_by")


# ==========================================================
#               EQUIPMENT MANUAL LOG ADMIN
# ==========================================================
@admin.register(EquipmentManualLog)
class EquipmentManualLogAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "equipment",
        "get_equipment_type",
        "stage",
        "action",
        "started_at",
        "ended_at",
        "duration_seconds",
        "performed_by",
    )

    list_filter = (
        "action",
        "stage",
        "equipment__equipment_type",
    )

    search_fields = (
        "equipment__name",
        "equipment__code",
        "stage__name",
    )

    autocomplete_fields = (
        "equipment",
        "stage",
        "performed_by",
    )

    readonly_fields = (
        "duration_seconds",
        "created_at",
    )

    ordering = ("-started_at",)

    def get_equipment_type(self, obj):
        return obj.equipment.equipment_type.name if obj.equipment else "-"

    get_equipment_type.short_description = "Equipment Type"
