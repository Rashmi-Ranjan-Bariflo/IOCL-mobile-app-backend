from django.urls import path
from .views import (
    ProcessParameterListCreateView,
    ProcessParameterDetailView,
    ProcessReadingListCreateView,
    ProcessReadingDetailView,
    EquipmentStatusListCreateView,
    EquipmentStatusDetailView,
)

urlpatterns = [
    # ======================================================
    # PROCESS PARAMETERS
    # ======================================================
    path(
        "parameters/",
        ProcessParameterListCreateView.as_view(),
        name="process-parameter-list-create",
    ),
    path(
        "parameters/<int:pk>/",
        ProcessParameterDetailView.as_view(),
        name="process-parameter-detail",
    ),
    # ======================================================
    # PROCESS READINGS
    # ======================================================
    path(
        "readings/",
        ProcessReadingListCreateView.as_view(),
        name="process-reading-list-create",
    ),
    path(
        "readings/<int:pk>/",
        ProcessReadingDetailView.as_view(),
        name="process-reading-detail",
    ),
    # ======================================================
    # EQUIPMENT STATUS
    # ======================================================
    path(
        "equipment-status/",
        EquipmentStatusListCreateView.as_view(),
        name="equipment-status-list-create",
    ),
    path(
        "equipment-status/<int:pk>/",
        EquipmentStatusDetailView.as_view(),
        name="equipment-status-detail",
    ),
]
