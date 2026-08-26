from django.contrib import admin
from .models import Plant, TreatmentStage, PlantStage


# ==========================================================
#                         PLANT ADMIN
# ==========================================================
@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "code",
        "location",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "code",
        "location",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ==========================================================
#                  TREATMENT STAGE ADMIN
# ==========================================================
@admin.register(TreatmentStage)
class TreatmentStageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "stage_order",
        "name",
        "code",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "code",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "stage_order",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ==========================================================
#                     PLANT STAGE ADMIN
# ==========================================================
@admin.register(PlantStage)
class PlantStageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "plant",
        "treatment_stage",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "plant",
    )

    search_fields = (
        "plant__name",
        "plant__code",
        "treatment_stage__name",
        "treatment_stage__code",
    )

    list_filter = (
        "plant",
        "treatment_stage",
        "is_active",
    )

    ordering = (
        "plant",
        "treatment_stage__stage_order",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )