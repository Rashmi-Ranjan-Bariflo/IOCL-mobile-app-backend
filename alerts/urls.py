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
    path("types/", AlertTypeListCreateView.as_view(), name="alert-type-list-create"),
    path("types/<int:pk>/", AlertTypeDetailView.as_view(), name="alert-type-detail"),
    path("", AlertListCreateView.as_view(), name="alert-list-create"),
    path("<int:pk>/", AlertDetailView.as_view(), name="alert-detail"),
    path("stage/<int:stage_id>/", AlertListCreateView.as_view(), name="stage-alert-list"),
    path("notifications/", AlertNotificationListCreateView.as_view(), name="alert-notification-list-create"),
    path("notifications/<int:pk>/", AlertNotificationDetailView.as_view(), name="alert-notification-detail"),
]
