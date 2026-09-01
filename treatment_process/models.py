from django.db import models
from django.utils import timezone


# ==========================================================
# TREATMENT PROCESS
# ==========================================================
class TreatmentProcess(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("STOPPED", "Stopped"),
    ]

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ==========================================================
# TREATMENT STAGES
# ==========================================================
class TreatmentStage(models.Model):

    STAGE_CHOICES = [
        ("WASTEWATER_COLLECTION", "Wastewater Collection"),
        ("TREATMENT", "Treatment"),
        ("COAGULATION", "Coagulation"),
        ("COAGULATION_MIXING", "Coagulation Mixing"),
        ("COAGULATION_REST", "Coagulation Rest"),
        ("FLOCCULATION", "Flocculation"),
        ("FILTER_SCREENING", "Filter / Screening"),
        ("AERATION", "Aeration"),
    ]

    process = models.ForeignKey(
        TreatmentProcess, on_delete=models.CASCADE, related_name="stages"
    )
    name = models.CharField(max_length=100)
    stage_type = models.CharField(max_length=40, choices=STAGE_CHOICES)
    sequence = models.PositiveIntegerField()
    duration_seconds = models.PositiveIntegerField(
        default=0, help_text="Process duration in seconds"
    )
    target_volume_liters = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["process", "sequence"], name="unique_process_stage_sequence"
            )
        ]

    def __str__(self):
        return f"{self.sequence}. {self.name}"


# ==========================================================
# TREATMENT BATCH
# ==========================================================
class TreatmentBatch(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("STOPPED", "Stopped"),
    ]

    process = models.ForeignKey(
        TreatmentProcess, on_delete=models.PROTECT, related_name="batches"
    )
    batch_number = models.CharField(max_length=50, unique=True)
    input_volume_liters = models.DecimalField(max_digits=10, decimal_places=2)
    output_volume_liters = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    current_stage = models.ForeignKey(
        TreatmentStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_batches",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def start_batch(self):
        self.status = "RUNNING"
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at", "updated_at"])

    def complete_batch(self):
        self.status = "COMPLETED"
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at", "updated_at"])

    def __str__(self):
        return self.batch_number


# ==========================================================
# CHEMICAL / SOLUTION DOSING
# ==========================================================
class DosingRecord(models.Model):

    SOLUTION_CHOICES = [
        ("COAGULANT", "Coagulant Solution"),
        ("FLOCCULANT", "Flocculant Solution"),
    ]

    batch = models.ForeignKey(
        TreatmentBatch, on_delete=models.CASCADE, related_name="dosing_records"
    )
    solution_type = models.CharField(max_length=20, choices=SOLUTION_CHOICES)
    quantity_ml = models.DecimalField(max_digits=10, decimal_places=2)
    dosing_time = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.batch.batch_number} - "
            f"{self.solution_type} - "
            f"{self.quantity_ml} ml"
        )


# ==========================================================
# PROCESS EXECUTION LOG
# ==========================================================
class ProcessExecutionLog(models.Model):

    STATUS_CHOICES = [
        ("STARTED", "Started"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("STOPPED", "Stopped"),
    ]

    batch = models.ForeignKey(
        TreatmentBatch, on_delete=models.CASCADE, related_name="execution_logs"
    )
    stage = models.ForeignKey(
        TreatmentStage, on_delete=models.PROTECT, related_name="execution_logs"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    actual_duration_seconds = models.PositiveIntegerField(default=0)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.batch.batch_number} - " f"{self.stage.name}"
