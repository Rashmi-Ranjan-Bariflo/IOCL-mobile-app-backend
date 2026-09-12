from django.urls import path
from .views import (
    CoagulantDosingMotorOffView,
    CoagulantDosingMotorOnView,
    EquipmentManualLogByEquipmentView,
    EquipmentTypeListCreateView,
    EquipmentTypeDetailView,
    EquipmentListCreateView,
    EquipmentDetailView,
    SensorListView,
    StageEquipmentsDurationView,
    ValveOnView, ValveOffView, MotorOnView, MotorOffView
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

    # Valve
    path("valve/<int:equipment_id>/on/", ValveOnView.as_view(), name="valve-on"),
    path("valve/<int:equipment_id>/off/", ValveOffView.as_view(), name="valve-off"),

    # Motor
    path("motor/<int:equipment_id>/on/", MotorOnView.as_view(), name="motor-on"),
    path("motor/<int:equipment_id>/off/", MotorOffView.as_view(), name="motor-off"),

    path("sensors/", SensorListView.as_view(), name="sensor-list"),

    path("manual-logs/<int:equipment_id>/", EquipmentManualLogByEquipmentView.as_view()),
    path("merge/<int:stage_id>/", StageEquipmentsDurationView.as_view()),

    path("coagulant-dosing/motor/<int:equipment_id>/on/", CoagulantDosingMotorOnView.as_view(),),
    path("coagulant-dosing/motor/<int:equipment_id>/off/", CoagulantDosingMotorOffView.as_view(),),

]