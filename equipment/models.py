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

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="equipment",
    )
    # treatment_process = models.ForeignKey(
    #     "treatment_process.TreatmentStage",
    #     on_delete=models.CASCADE,
    #     related_name="equipment",
    # )
    
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
    start_time = models.TimeField(
        blank=True,
        null=True
    )

    end_time = models.TimeField(
        blank=True,
        null=True
    )

    duration_seconds = models.PositiveIntegerField(
        blank=True,
        null=True
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




class EquipmentTest(models.Model):
    STATUS_CHOICES = [
        ("TESTING", "Testing"),
        ("COMPLETED", "Completed"),
        ("MERGED", "Merged"),
        ("CANCELLED", "Cancelled"),
    ]

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="tests"
    )

    stage = models.ForeignKey(
        "treatment_process.TreatmentStage",
        on_delete=models.CASCADE,
        related_name="equipment_tests"
    )

    start_time = models.TimeField(
        blank=True,
        null=True
    )

    end_time = models.TimeField(
        blank=True,
        null=True
    )

    duration_seconds = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="TESTING"
    )

    tested_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="equipment_tests"
    )

    is_merged = models.BooleanField(default=False)

    merged_at = models.DateTimeField(
        blank=True,
        null=True
    )

    merged_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="merged_equipment_tests",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "equipment_tests"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["equipment", "stage"],
                name="equipment_test_stage_idx"
            ),
            models.Index(
                fields=["status"],
                name="equipment_test_status_idx"
            ),
        ]

    def __str__(self):
        return f"{self.equipment.name} - Test"





class EquipmentManualLog(models.Model):
    ACTION_CHOICES = [
        ("ON", "ON"),
        ("OFF", "OFF"),
    ]

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="manual_logs"
    )

    stage = models.ForeignKey(
        "treatment_process.TreatmentStage",
        on_delete=models.CASCADE,
        related_name="equipment_manual_logs"
    )

    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES
    )

    started_at = models.DateTimeField()

    ended_at = models.DateTimeField(
        blank=True,
        null=True
    )

    duration_seconds = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    performed_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="equipment_manual_logs"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "equipment_manual_logs"
        ordering = ["-started_at"]
        indexes = [
            models.Index(
                fields=["equipment", "started_at"],
                name="equipment_manual_log_idx"
            ),
            models.Index(
                fields=["stage", "started_at"],
                name="stage_manual_log_idx"
            ),
        ]

    def __str__(self):
        return f"{self.equipment.name} - {self.action}"