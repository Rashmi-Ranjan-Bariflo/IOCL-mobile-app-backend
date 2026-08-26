from django.urls import path
from .views import (
    EquipmentTypeListCreateView,
    EquipmentTypeDetailView,
    EquipmentListCreateView,
    EquipmentDetailView,
    EquipmentStageListCreateView,
    EquipmentStageDetailView,
)


urlpatterns = [
    # ======================================================
    #                  EQUIPMENT TYPES
    # ======================================================
    path("types/", EquipmentTypeListCreateView.as_view(), name="equipment-type-list-create",),
    path("types/<int:pk>/", EquipmentTypeDetailView.as_view(), name="equipment-type-detail",),

    # ======================================================
    #                     EQUIPMENT
    # ======================================================
    path("",EquipmentListCreateView.as_view(),name="equipment-list-create",),
    path("<int:pk>/", EquipmentDetailView.as_view(), name="equipment-detail",),

    # ======================================================
    #                  EQUIPMENT STAGES
    # ======================================================
    path("stages/", EquipmentStageListCreateView.as_view(), name="equipment-stage-list-create",),
    path("stages/<int:pk>/", EquipmentStageDetailView.as_view(), name="equipment-stage-detail",),
]