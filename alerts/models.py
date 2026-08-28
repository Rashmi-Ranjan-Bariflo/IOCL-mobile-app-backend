from django.db import models

from plants.models import Plant, PlantStage
from equipment.models import Equipment
from sensors.models import Sensor
from process_monitoring.models import ProcessParameter

# ==========================================================
#                    ALERT TYPE
# ==========================================================


class AlertType(models.Model):

    CATEGORY_CHOICES = [
        ("PROCESS", "Process"),
        ("EQUIPMENT", "Equipment"),
        ("SENSOR", "Sensor"),
        ("WATER_QUALITY", "Water Quality"),
        ("SYSTEM", "System"),
    ]

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alert_types"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


# ==========================================================
#                       ALERT
# ==========================================================


class Alert(models.Model):

    SEVERITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("ACKNOWLEDGED", "Acknowledged"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed"),
    ]

    SOURCE_CHOICES = [
        ("PROCESS", "Process Monitoring"),
        ("WATER_QUALITY", "Water Quality"),
        ("EQUIPMENT", "Equipment"),
        ("SENSOR", "Sensor"),
        ("MANUAL", "Manual"),
        ("SYSTEM", "System"),
    ]

    # ------------------------------------------------------
    # Relationships
    # ------------------------------------------------------

    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name="alerts")
    plant_stage = models.ForeignKey(PlantStage,on_delete=models.SET_NULL,null=True,blank=True,related_name="alerts",)
    equipment = models.ForeignKey(Equipment,on_delete=models.SET_NULL,null=True,blank=True,related_name="alerts",)
    sensor = models.ForeignKey(Sensor, on_delete=models.SET_NULL, null=True, blank=True, related_name="alerts")
    parameter = models.ForeignKey(ProcessParameter,on_delete=models.SET_NULL,null=True,blank=True,related_name="alerts",)
    alert_type = models.ForeignKey(AlertType, on_delete=models.PROTECT, related_name="alerts")

    # ------------------------------------------------------
    # Alert information
    # ------------------------------------------------------

    title = models.CharField(max_length=200)
    message = models.TextField()
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="MEDIUM")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")

    # ------------------------------------------------------
    # Values
    # ------------------------------------------------------

    current_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    limit_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=30, blank=True, null=True)

    triggered_at = models.DateTimeField()
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alerts"
        ordering = ["-triggered_at"]

        indexes = [
            models.Index(
                fields=["plant", "status"],
                name="alert_plant_status_idx",
            ),
            models.Index(
                fields=["severity", "status"],
                name="alert_severity_status_idx",
            ),
            models.Index(
                fields=["triggered_at"],
                name="alert_triggered_idx",
            ),
        ]

    def __str__(self):
        return f"{self.title} - " f"{self.severity} - " f"{self.status}"


# ==========================================================
#                  ALERT NOTIFICATION
# ==========================================================


class AlertNotification(models.Model):

    NOTIFICATION_TYPE_CHOICES = [
        ("APP", "App Notification"),
        ("EMAIL", "Email"),
        ("SMS", "SMS"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SENT", "Sent"),
        ("FAILED", "Failed"),
    ]

    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    recipient = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alert_notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.alert.title} - " f"{self.notification_type} - " f"{self.status}"
