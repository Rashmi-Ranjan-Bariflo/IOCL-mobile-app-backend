from django.urls import path

from .views import (
    SensorTypeListCreateView,
    SensorTypeDetailView,
    SensorListCreateView,
    SensorDetailView,
    SensorReadingListCreateView,
    SensorReadingDetailView,
)

urlpatterns = [
    # ======================================================
    #                    SENSOR TYPES
    # ======================================================
    path(
        "types/",
        SensorTypeListCreateView.as_view(),
        name="sensor-type-list-create",
    ),
    path(
        "types/<int:pk>/",
        SensorTypeDetailView.as_view(),
        name="sensor-type-detail",
    ),
    # ======================================================
    #                       SENSORS
    # ======================================================
    path(
        "",
        SensorListCreateView.as_view(),
        name="sensor-list-create",
    ),
    path(
        "<int:pk>/",
        SensorDetailView.as_view(),
        name="sensor-detail",
    ),
    # ======================================================
    #                   SENSOR READINGS
    # ======================================================
    path(
        "readings/",
        SensorReadingListCreateView.as_view(),
        name="sensor-reading-list-create",
    ),
    path(
        "readings/<int:pk>/",
        SensorReadingDetailView.as_view(),
        name="sensor-reading-detail",
    ),
]
