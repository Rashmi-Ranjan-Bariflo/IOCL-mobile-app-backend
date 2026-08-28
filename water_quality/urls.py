from django.urls import path
from .views import (
    WaterQualityParameterListCreateView,
    WaterQualityParameterDetailView,
    WaterQualityReadingListCreateView,
    WaterQualityReadingDetailView,
)


urlpatterns = [

    # ======================================================
    # WATER QUALITY PARAMETERS
    # ======================================================

    path(
        "parameters/",
        WaterQualityParameterListCreateView.as_view(),
        name="water-quality-parameter-list-create",
    ),

    path(
        "parameters/<int:pk>/",
        WaterQualityParameterDetailView.as_view(),
        name="water-quality-parameter-detail",
    ),


    # ======================================================
    # WATER QUALITY READINGS
    # ======================================================

    path(
        "readings/",
        WaterQualityReadingListCreateView.as_view(),
        name="water-quality-reading-list-create",
    ),

    path(
        "readings/<int:pk>/",
        WaterQualityReadingDetailView.as_view(),
        name="water-quality-reading-detail",
    ),
]