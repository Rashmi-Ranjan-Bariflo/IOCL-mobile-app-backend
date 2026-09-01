from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("plants/", include("plants.urls")),
    path("sensors/", include("sensors.urls")),
    path("equipment/",include("equipment.urls")),
    path("water-quality/", include("water_quality.urls")),
    path("process-monitoring/", include("process_monitoring.urls")),
    path("alerts/", include("alerts.urls")),
    path("treatment-process/", include("treatment_process.urls")),
]
