from django.urls import path

from .views import (
    AlertTypeListCreateView,
    AlertTypeDetailView,
    AlertListCreateView,
    AlertDetailView,
    AlertNotificationListCreateView,
    AlertNotificationDetailView,
)

urlpatterns = [
    # ======================================================
    # ALERT TYPES
    # ======================================================
    path(
        "types/",
        AlertTypeListCreateView.as_view(),
        name="alert-type-list-create",
    ),
    path(
        "types/<int:pk>/",
        AlertTypeDetailView.as_view(),
        name="alert-type-detail",
    ),
    # ======================================================
    # ALERTS
    # ======================================================
    path(
        "alerts/",
        AlertListCreateView.as_view(),
        name="alert-list-create",
    ),
    path(
        "alerts/<int:pk>/",
        AlertDetailView.as_view(),
        name="alert-detail",
    ),
    # ======================================================
    # ALERT NOTIFICATIONS
    # ======================================================
    path(
        "notifications/",
        AlertNotificationListCreateView.as_view(),
        name="alert-notification-list-create",
    ),
    path(
        "notifications/<int:pk>/",
        AlertNotificationDetailView.as_view(),
        name="alert-notification-detail",
    ),
]
