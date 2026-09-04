from django.db import models

from sensors.models import Sensor

# ==========================================================
#                  WATER QUALITY PARAMETER
# ==========================================================


class WaterQualityParameter(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    code = models.CharField(
        max_length=50,
        unique=True,
    )

    unit = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    min_value = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        blank=True,
        null=True,
    )

    max_value = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "water_quality_parameters"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


# ==========================================================
#                  WATER QUALITY READING
# ==========================================================


class WaterQualityReading(models.Model):

    SOURCE_CHOICES = [
        ("SENSOR", "Sensor"),
        ("LAB", "Laboratory"),
        ("MANUAL", "Manual"),
    ]

    STATUS_CHOICES = [
        ("NORMAL", "Normal"),
        ("WARNING", "Warning"),
        ("CRITICAL", "Critical"),
    ]

    parameter = models.ForeignKey(
        WaterQualityParameter,
        on_delete=models.CASCADE,
        related_name="readings",
    )

    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="water_quality_readings",
    )

    value = models.DecimalField(
        max_digits=12,
        decimal_places=4,
    )

    unit = models.CharField(
        max_length=30,
    )

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="SENSOR",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="NORMAL",
    )

    recorded_at = models.DateTimeField()

    remarks = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "water_quality_readings"
        ordering = ["-recorded_at"]

        indexes = [
            models.Index(
                fields=["parameter", "recorded_at"],
                name="wq_param_date_idx",
            ),
            models.Index(
                fields=["sensor", "recorded_at"],
                name="wq_sensor_date_idx",
            ),
        ]

    def __str__(self):
        return f"{self.parameter.name} - {self.value} {self.unit}"
