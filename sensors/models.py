from django.db import models


# ==========================================================
#                    SENSOR TYPE
# ==========================================================
class SensorType(models.Model):

    name = models.CharField(max_length=100, unique=True,)
    code = models.CharField(max_length=50, unique=True,)
    description = models.TextField(blank=True, null=True,)
    default_unit = models.CharField(max_length=50, blank=True, null=True,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "sensor_types"
        ordering = ["name"]

        indexes = [
            models.Index(
                fields=["code"],
                name="sensor_type_code_idx",
            ),
            models.Index(
                fields=["is_active"],
                name="sensor_type_active_idx",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


# ==========================================================
#                       SENSOR
# ==========================================================
class Sensor(models.Model):

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("MAINTENANCE", "Maintenance"),
        ("FAULT", "Fault"),
    ]
    name = models.CharField(max_length=150,)
    code = models.CharField(max_length=100, unique=True,)
    sensor_type = models.ForeignKey(SensorType, on_delete=models.PROTECT, related_name="sensors",)
    equipment = models.ForeignKey("equipment.Equipment", on_delete=models.CASCADE, related_name="sensors",)
    description = models.TextField(blank=True, null=True,)
    location = models.CharField(max_length=255, blank=True, null=True,)
    manufacturer = models.CharField(max_length=150, blank=True, null=True,)
    model_number = models.CharField(max_length=150, blank=True, null=True,)
    serial_number = models.CharField(max_length=150, blank=True, null=True,)
    unit = models.CharField(max_length=50, blank=True, null=True,)
    min_value = models.FloatField(blank=True, null=True,)
    max_value = models.FloatField(blank=True, null=True,)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE",)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "sensors"
        ordering = ["name"]

        indexes = [
            models.Index(
                fields=["code"],
                name="sensor_code_idx",
            ),
            models.Index(
                fields=["equipment"],
                name="sensor_equipment_idx",
            ),
            models.Index(
                fields=["status"],
                name="sensor_status_idx",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


# ==========================================================
#                    SENSOR READING
# ==========================================================
class SensorReading(models.Model):

    STATUS_CHOICES = [
        ("NORMAL", "Normal"),
        ("LOW", "Low"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]
    sensor = models.ForeignKey(Sensor,on_delete=models.CASCADE,related_name="readings",)
    value = models.FloatField()
    unit = models.CharField(max_length=50, blank=True, null=True,)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default="NORMAL",)
    recorded_at = models.DateTimeField(db_index=True,)
    source = models.CharField(max_length=50, default="MANUAL", help_text="Example: MANUAL, MQTT, API",)
    raw_value = models.CharField(max_length=255, blank=True, null=True,)
    created_at = models.DateTimeField(auto_now_add=True,)

    class Meta:
        db_table = "sensor_readings"

        ordering = [
            "-recorded_at",
        ]

        indexes = [
            models.Index(
                fields=["sensor", "recorded_at"],
                name="sensor_reading_idx",
            ),
            models.Index(
                fields=["recorded_at"],
                name="reading_recorded_idx",
            ),
            models.Index(
                fields=["status"],
                name="reading_status_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.sensor.name} - "
            f"{self.value} {self.unit or ''} - "
            f"{self.recorded_at}"
        )
