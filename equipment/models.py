from django.db import models


# ==========================================================
#                    EQUIPMENT TYPE
# ==========================================================
class EquipmentType(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
    )
    description = models.TextField(
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
        db_table = "equipment_types"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==========================================================
#                       EQUIPMENT
# ==========================================================
class Equipment(models.Model):

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("MAINTENANCE", "Maintenance"),
        ("FAULT", "Fault"),
    ]

    name = models.CharField(
        max_length=150,
    )
    code = models.CharField(
        max_length=100,
        unique=True,
    )
    equipment_type = models.ForeignKey(
        EquipmentType,
        on_delete=models.PROTECT,
        related_name="equipment",
    )
    description = models.TextField(
        blank=True,
        null=True,
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    manufacturer = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )
    model_number = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )
    serial_number = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE",
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
        db_table = "equipment"
        ordering = ["name"]

        indexes = [
            models.Index(
                fields=["code"],
                name="equipment_code_idx",
            ),
            models.Index(
                fields=["status"],
                name="equipment_status_idx",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"
