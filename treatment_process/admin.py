from django.contrib import admin

from .models import (
    TreatmentProcess,
    TreatmentStage,
    TreatmentBatch,
    DosingRecord,
    ProcessExecutionLog,
)


# ==========================================================
# TREATMENT PROCESS ADMIN
# ==========================================================
@admin.register(TreatmentProcess)
class TreatmentProcessAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "status",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = ("id",)


# ==========================================================
# TREATMENT STAGE ADMIN
# ==========================================================
@admin.register(TreatmentStage)
class TreatmentStageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "process",
        "sequence",
        "name",
        "stage_type",
        "duration_seconds",
        "target_volume_liters",
        "is_active",
    )

    list_filter = (
        "stage_type",
        "is_active",
        "process",
    )

    search_fields = (
        "name",
        "process__name",
    )

    ordering = (
        "process",
        "sequence",
    )


# ==========================================================
# TREATMENT BATCH ADMIN
# ==========================================================
@admin.register(TreatmentBatch)
class TreatmentBatchAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "batch_number",
        "process",
        "current_stage",
        "input_volume_liters",
        "output_volume_liters",
        "status",
        "started_at",
        "completed_at",
    )

    list_filter = (
        "status",
        "process",
    )

    search_fields = (
        "batch_number",
        "process__name",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ==========================================================
# DOSING RECORD ADMIN
# ==========================================================
@admin.register(DosingRecord)
class DosingRecordAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "batch",
        "solution_type",
        "quantity_ml",
        "dosing_time",
        "created_at",
    )

    list_filter = ("solution_type",)

    search_fields = (
        "batch__batch_number",
        "notes",
    )

    ordering = ("-dosing_time",)

    readonly_fields = ("created_at",)


# ==========================================================
# PROCESS EXECUTION LOG ADMIN
# ==========================================================
@admin.register(ProcessExecutionLog)
class ProcessExecutionLogAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "batch",
        "stage",
        "status",
        "started_at",
        "completed_at",
        "actual_duration_seconds",
    )

    list_filter = (
        "status",
        "stage",
    )

    search_fields = (
        "batch__batch_number",
        "stage__name",
        "remarks",
    )

    ordering = ("-created_at",)

    readonly_fields = ("created_at",)
