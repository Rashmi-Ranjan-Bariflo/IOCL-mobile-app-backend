from django.contrib import admin

from .models import (
    TreatmentStage,
    TreatmentProcess,
    TreatmentBatch,
    StageExecutionLog,
    DosingRecord,
    ProcessExecutionLog,
)


# ==========================================================
# TREATMENT STAGE ADMIN
# ==========================================================
@admin.register(TreatmentStage)
class TreatmentStageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "stage_type",
        "sequence",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    list_filter = (
        "stage_type",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = (
        "sequence",
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    filter_horizontal = ("equipments",)


# ==========================================================
# TREATMENT PROCESS ADMIN
# ==========================================================
@admin.register(TreatmentProcess)
class TreatmentProcessAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "stage",
        "sequence",
        "duration_seconds",
        "target_volume_liters",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    list_filter = (
        "stage",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
        "stage__name",
    )

    ordering = (
        "stage__sequence",
        "sequence",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "stage",
    )


# ==========================================================
# TREATMENT BATCH ADMIN
# ==========================================================
@admin.register(TreatmentBatch)
class TreatmentBatchAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "batch_number",
        "input_volume_liters",
        "output_volume_liters",
        "status",
        "started_at",
        "completed_at",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "batch_number",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "batch_number",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ==========================================================
# STAGE EXECUTION LOG ADMIN
# ==========================================================
@admin.register(StageExecutionLog)
class StageExecutionLogAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "batch",
        "stage",
        "status",
        "started_at",
        "completed_at",
        "actual_duration_seconds",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "batch",
    )

    list_filter = (
        "status",
        "stage",
    )

    search_fields = (
        "batch__batch_number",
        "stage__name",
        "stage__stage_type",
        "remarks",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "batch",
        "stage",
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

    list_display_links = (
        "id",
        "batch",
    )

    list_filter = (
        "solution_type",
        "dosing_time",
    )

    search_fields = (
        "batch__batch_number",
        "notes",
    )

    ordering = ("-dosing_time",)

    readonly_fields = ("created_at",)

    autocomplete_fields = ("batch",)


# ==========================================================
# PROCESS EXECUTION LOG ADMIN
# ==========================================================
@admin.register(ProcessExecutionLog)
class ProcessExecutionLogAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "batch",
        "process",
        "status",
        "started_at",
        "completed_at",
        "actual_duration_seconds",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "batch",
    )

    list_filter = (
        "status",
        "process__stage",
        "process",
    )

    search_fields = (
        "batch__batch_number",
        "process__name",
        "process__stage__name",
        "remarks",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "batch",
        "process",
    )
