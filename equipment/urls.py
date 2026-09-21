from django.urls import path
from .views import (
    BlowerOffView,
    BlowerOnView,
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
    path("types/", EquipmentTypeListCreateView.as_view(),),
    path("types/<int:pk>/", EquipmentTypeDetailView.as_view(),),
    # ======================================================
    #                     EQUIPMENT
    # ======================================================
    path("", EquipmentListCreateView.as_view(),),
    path("<int:pk>/",EquipmentDetailView.as_view(),),
    # Valve
    path("valve/<int:equipment_id>/on/", ValveOnView.as_view(),),
    path("valve/<int:equipment_id>/off/", ValveOffView.as_view(),),
    # Motor
    path("pump/<int:equipment_id>/on/", MotorOnView.as_view(),),
    path("pump/<int:equipment_id>/off/", MotorOffView.as_view(),),

    path("stage/<int:stage_id>/sensors/", StageSensorListView.as_view(),),

    path("manual-logs/<int:equipment_id>/", EquipmentManualLogByEquipmentView.as_view()),
    # Merge manual duration for all equipment of a stage
    path("stages/<int:stage_id>/merge-duration/", MergeManualDurationView.as_view(),),

    path("motor/<int:equipment_id>/on/", CoagulantDosingMotorOnView.as_view(),),
    path("motor/<int:equipment_id>/off/", CoagulantDosingMotorOffView.as_view(),),

    path("blower/<int:equipment_id>/on/", BlowerOnView.as_view(),),
    path("blower/<int:equipment_id>/off/", BlowerOffView.as_view(),),
]

