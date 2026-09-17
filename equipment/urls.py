from django.urls import path
from .views import (
    CoagulantDosingMotorOffView,
    CoagulantDosingMotorOnView,
    EquipmentManualLogByEquipmentView,
    EquipmentTypeListCreateView,
    EquipmentTypeDetailView,
    EquipmentListCreateView,
    EquipmentDetailView,
    MergeManualDurationView,
    StageSensorListView,
    ValveOnView,
    ValveOffView,
    MotorOnView,
    MotorOffView,
)

urlpatterns = [
    # ======================================================
    #                  EQUIPMENT TYPES
    # ======================================================
    path(
        "types/",
        EquipmentTypeListCreateView.as_view(),
        name="equipment-type-list-create",
    ),
    path(
        "types/<int:pk>/",
        EquipmentTypeDetailView.as_view(),
        name="equipment-type-detail",
    ),
    # ======================================================
    #                     EQUIPMENT
    # ======================================================
    path(
        "",
        EquipmentListCreateView.as_view(),
        name="equipment-list-create",
    ),
    path(
        "<int:pk>/",
        EquipmentDetailView.as_view(),
        name="equipment-detail",
    ),
    # Valve
    path("valve/<int:equipment_id>/on/", ValveOnView.as_view(), name="valve-on"),
    path("valve/<int:equipment_id>/off/", ValveOffView.as_view(), name="valve-off"),
    # Motor
    path("motor/<int:equipment_id>/on/", MotorOnView.as_view(), name="motor-on"),
    path("motor/<int:equipment_id>/off/", MotorOffView.as_view(), name="motor-off"),
    path(
        "stage/<int:stage_id>/sensors/",
        StageSensorListView.as_view(),
        name="stage-sensors",
    ),
    path(
        "manual-logs/<int:equipment_id>/", EquipmentManualLogByEquipmentView.as_view()
    ),
    # Merge manual duration for all equipment of a stage
    path(
        "stages/<int:stage_id>/merge-duration/",
        MergeManualDurationView.as_view(),
        name="merge-manual-duration",
    ),
    path(
        "coagulant-dosing/motor/<int:equipment_id>/on/",
        CoagulantDosingMotorOnView.as_view(),
    ),
    path(
        "coagulant-dosing/motor/<int:equipment_id>/off/",
        CoagulantDosingMotorOffView.as_view(),
    ),
]
