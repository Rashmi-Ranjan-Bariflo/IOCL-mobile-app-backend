from django.urls import path
from .views import (
    EquipmentTypeListCreateView,
    EquipmentTypeDetailView,
    EquipmentListCreateView,
    EquipmentDetailView,
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

]