from django.urls import path

from .views import (
    PlantListView,
    PlantDetailView,
    TreatmentStageListView,
    TreatmentStageDetailView,
    PlantStageListView,
    PlantStageDetailView,
    PlantStagesByPlantView,
)

urlpatterns = [
    # ======================================================
    # PLANTS
    # ======================================================
    path(
        "",
        PlantListView.as_view(),
        name="plant-list",
    ),
    path(
        "<int:pk>/",
        PlantDetailView.as_view(),
        name="plant-detail",
    ),
    # ======================================================
    # PLANT STAGES
    # ======================================================
    path(
        "<int:plant_id>/stages/",
        PlantStagesByPlantView.as_view(),
        name="plant-stages-by-plant",
    ),
    # ======================================================
    # TREATMENT STAGES
    # ======================================================
    path(
        "treatment-stages/",
        TreatmentStageListView.as_view(),
        name="treatment-stage-list",
    ),
    path(
        "treatment-stages/<int:pk>/",
        TreatmentStageDetailView.as_view(),
        name="treatment-stage-detail",
    ),
    # ======================================================
    # PLANT STAGE MAPPING
    # ======================================================
    path(
        "plant-stages/",
        PlantStageListView.as_view(),
        name="plant-stage-list",
    ),
    path(
        "plant-stages/<int:pk>/",
        PlantStageDetailView.as_view(),
        name="plant-stage-detail",
    ),
]
