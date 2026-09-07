from django.db import models
from django.utils import timezone

from equipment.models import Equipment


# ==========================================================
# TREATMENT STAGE
# ==========================================================
class TreatmentStage(models.Model):

    STAGE_CHOICES = [
        ("WASTEWATER_COLLECTION", "Wastewater Collection"),
        ("NORMALWATER_COLLECTION", "NormalWater Collection"),
        ("TREATMENT", "Treatment"),
        ("COAGULATION", "Coagulation"),
        ("FLOCCULATION", "Flocculation"),
        ("FILTER_SCREENING", "Filter / Screening"),
        ("AERATION", "Aeration"),
    ]

    name = models.CharField(max_length=100, unique=True)

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="treatment_stages"
    )

    stage_type = models.CharField(max_length=40, choices=STAGE_CHOICES)

    description = models.TextField(blank=True, null=True)

    # Order in which stages will execute
    sequence = models.PositiveIntegerField()

    # Equipment required for this stage
    equipments = models.ManyToManyField(
        Equipment, related_name="treatment_stages", blank=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "treatment_stages"

        ordering = ["sequence"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "sequence"], name="unique_user_stage_sequence"
            )
        ]

        indexes = [
            models.Index(fields=["sequence"], name="treatment_stage_seq_idx"),
            models.Index(fields=["stage_type"], name="treatment_stage_type_idx"),
            models.Index(fields=["user"], name="treatment_stage_user_idx"),
        ]

    def __str__(self):
        return f"{self.sequence}. {self.name}"


# ==========================================================
# TREATMENT PROCESS
# ==========================================================
class TreatmentProcess(models.Model):

    stage = models.ForeignKey(
        TreatmentStage, on_delete=models.PROTECT, related_name="processes"
    )

    name = models.CharField(max_length=150)

    description = models.TextField(blank=True, null=True)

    # Order of process inside a stage
    sequence = models.PositiveIntegerField()

    # Expected duration
    duration_seconds = models.PositiveIntegerField(
        default=0, help_text="Expected process duration in seconds"
    )

    target_volume_liters = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    equipments = models.ManyToManyField(
        Equipment,
        related_name="treatment_processes",
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "treatment_processes"

        ordering = ["stage__sequence", "sequence"]

        constraints = [
            models.UniqueConstraint(
                fields=["stage", "sequence"], name="unique_stage_process_sequence"
            )
        ]

        indexes = [
            models.Index(
                fields=["stage", "sequence"], name="treatment_process_stage_idx"
            ),
            models.Index(fields=["is_active"], name="treatment_process_active_idx"),
        ]

    def __str__(self):
        return f"{self.stage.name} - {self.name}"


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

    batch_number = models.CharField(max_length=50, unique=True)

    input_volume_liters = models.DecimalField(max_digits=10, decimal_places=2)

    output_volume_liters = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    started_at = models.DateTimeField(blank=True, null=True)

    completed_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def start_batch(self):
        """
        Start treatment batch.
        """
        self.status = "RUNNING"
        self.started_at = timezone.now()

        self.save(update_fields=["status", "started_at", "updated_at"])

    def complete_batch(self):
        """
        Complete treatment batch.
        """
        self.status = "COMPLETED"
        self.completed_at = timezone.now()

        self.save(update_fields=["status", "completed_at", "updated_at"])

    def stop_batch(self):
        """
        Stop treatment batch.
        """
        self.status = "STOPPED"
        self.completed_at = timezone.now()

        self.save(update_fields=["status", "completed_at", "updated_at"])

    def fail_batch(self):
        """
        Mark treatment batch as failed.
        """
        self.status = "FAILED"
        self.completed_at = timezone.now()

        self.save(update_fields=["status", "completed_at", "updated_at"])

    def __str__(self):
        return self.batch_number


# ==========================================================
# STAGE EXECUTION LOG
# ==========================================================
class StageExecutionLog(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("STARTED", "Started"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("STOPPED", "Stopped"),
    ]

    batch = models.ForeignKey(
        TreatmentBatch, on_delete=models.CASCADE, related_name="stage_execution_logs"
    )

    stage = models.ForeignKey(
        TreatmentStage, on_delete=models.PROTECT, related_name="execution_logs"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    started_at = models.DateTimeField(blank=True, null=True)

    completed_at = models.DateTimeField(blank=True, null=True)

    actual_duration_seconds = models.PositiveIntegerField(default=0)

    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stage_execution_logs"

        ordering = ["stage__sequence"]

        # One stage should have one execution record
        # for a particular batch.
        constraints = [
            models.UniqueConstraint(
                fields=["batch", "stage"], name="unique_batch_stage_execution"
            )
        ]

        indexes = [
            models.Index(fields=["batch", "stage"], name="stage_exec_batch_stage_idx"),
            models.Index(fields=["status"], name="stage_exec_status_idx"),
        ]

    def start_stage(self):
        """
        Start treatment stage.
        """
        self.status = "RUNNING"
        self.started_at = timezone.now()

        self.save(update_fields=["status", "started_at", "updated_at"])

    def complete_stage(self):
        """
        Complete treatment stage.

        This should be called only after all
        processes under this stage are completed.
        """

        self.status = "COMPLETED"
        self.completed_at = timezone.now()

        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()

            self.actual_duration_seconds = int(duration)

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "actual_duration_seconds",
                "updated_at",
            ]
        )

    def stop_stage(self):
        """
        Stop treatment stage.
        """
        self.status = "STOPPED"
        self.completed_at = timezone.now()

        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()

            self.actual_duration_seconds = int(duration)

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "actual_duration_seconds",
                "updated_at",
            ]
        )

    def fail_stage(self, remarks=None):
        """
        Mark treatment stage as failed.
        """
        self.status = "FAILED"
        self.completed_at = timezone.now()

        if remarks:
            self.remarks = remarks

        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()

            self.actual_duration_seconds = int(duration)

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "actual_duration_seconds",
                "remarks",
                "updated_at",
            ]
        )

    def __str__(self):
        return f"{self.batch.batch_number} - " f"{self.stage.name}"


# ==========================================================
# DOSING RECORD
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
        ("PENDING", "Pending"),
        ("STARTED", "Started"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("STOPPED", "Stopped"),
    ]

    batch = models.ForeignKey(
        TreatmentBatch, on_delete=models.CASCADE, related_name="process_execution_logs"
    )

    process = models.ForeignKey(
        TreatmentProcess, on_delete=models.PROTECT, related_name="execution_logs"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    started_at = models.DateTimeField(blank=True, null=True)

    completed_at = models.DateTimeField(blank=True, null=True)

    actual_duration_seconds = models.PositiveIntegerField(default=0)

    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "process_execution_logs"

        ordering = ["process__stage__sequence", "process__sequence"]

        constraints = [
            models.UniqueConstraint(
                fields=["batch", "process"], name="unique_batch_process_execution"
            )
        ]

        indexes = [
            models.Index(
                fields=["batch", "process"], name="process_exec_batch_process_idx"
            ),
            models.Index(fields=["status"], name="process_exec_status_idx"),
        ]

    def start_process(self):
        """
        Start process execution.
        """
        self.status = "RUNNING"
        self.started_at = timezone.now()

        self.save(update_fields=["status", "started_at", "updated_at"])

    def complete_process(self):
        """
        Complete process execution.
        """
        self.status = "COMPLETED"
        self.completed_at = timezone.now()

        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()

            self.actual_duration_seconds = int(duration)

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "actual_duration_seconds",
                "updated_at",
            ]
        )

    def stop_process(self):
        """
        Stop process execution.
        """
        self.status = "STOPPED"
        self.completed_at = timezone.now()

        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()

            self.actual_duration_seconds = int(duration)

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "actual_duration_seconds",
                "updated_at",
            ]
        )

    def fail_process(self, remarks=None):
        """
        Mark process execution as failed.
        """
        self.status = "FAILED"
        self.completed_at = timezone.now()

        if remarks:
            self.remarks = remarks

        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()

            self.actual_duration_seconds = int(duration)

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "actual_duration_seconds",
                "remarks",
                "updated_at",
            ]
        )

    def __str__(self):
        return f"{self.batch.batch_number} - " f"{self.process.name}"



# ==========================================================
# STAGE BATCH
# ==========================================================
class StageBatch(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("STOPPED", "Stopped"),
    ]

    batch_number = models.CharField(
        max_length=50,
        unique=True
    )

    stage = models.ForeignKey(
        TreatmentStage,
        on_delete=models.PROTECT,
        related_name="stage_batches"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    started_at = models.DateTimeField(
        blank=True,
        null=True
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "stage_batches"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["stage", "status"],
                name="stage_batch_stage_status_idx"
            ),
            models.Index(
                fields=["status"],
                name="stage_batch_status_idx"
            ),
        ]

    def start_batch(self):
        """
        Start stage batch.
        """
        self.status = "RUNNING"
        self.started_at = timezone.now()

        self.save(
            update_fields=[
                "status",
                "started_at",
                "updated_at",
            ]
        )

    def complete_batch(self):
        """
        Complete stage batch.
        """
        self.status = "COMPLETED"
        self.completed_at = timezone.now()

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

    def stop_batch(self):
        """
        Stop stage batch.
        """
        self.status = "STOPPED"
        self.completed_at = timezone.now()

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

    def fail_batch(self):
        """
        Mark stage batch as failed.
        """
        self.status = "FAILED"
        self.completed_at = timezone.now()

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

    def __str__(self):
        return self.batch_number




# ==========================================================
# STAGE BATCH PROCESS EXECUTION
# ==========================================================
class StageBatchProcessExecution(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("STARTED", "Started"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("STOPPED", "Stopped"),
    ]

    stage_batch = models.ForeignKey(
        StageBatch,
        on_delete=models.CASCADE,
        related_name="process_executions",
    )

    process = models.ForeignKey(
        TreatmentProcess,
        on_delete=models.PROTECT,
        related_name="stage_batch_executions",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    started_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    actual_duration_seconds = models.PositiveIntegerField(
        default=0,
    )

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
        db_table = "stage_batch_process_executions"

        ordering = [
            "stage_batch__created_at",
            "process__sequence",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["stage_batch", "process"],
                name="unique_stage_batch_process_execution",
            )
        ]

        indexes = [
            models.Index(
                fields=["stage_batch", "process"],
                name="stage_batch_process_idx",
            ),
            models.Index(
                fields=["status"],
                name="stage_batch_process_status_idx",
            ),
        ]

    def start_process(self):
        """
        Start process execution.
        """
        self.status = "RUNNING"
        self.started_at = timezone.now()

        self.save(
            update_fields=[
                "status",
                "started_at",
                "updated_at",
            ]
        )

    def complete_process(self):
        """
        Complete process execution.
        """
        self.status = "COMPLETED"
        self.completed_at = timezone.now()

        if self.started_at:
            duration = (
                self.completed_at - self.started_at
            ).total_seconds()

            self.actual_duration_seconds = int(duration)

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "actual_duration_seconds",
                "updated_at",
            ]
        )

    def stop_process(self):
        """
        Stop process execution.
        """
        self.status = "STOPPED"
        self.completed_at = timezone.now()

        if self.started_at:
            duration = (
                self.completed_at - self.started_at
            ).total_seconds()

            self.actual_duration_seconds = int(duration)

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "actual_duration_seconds",
                "updated_at",
            ]
        )

    def fail_process(self, remarks=None):
        """
        Mark process execution as failed.
        """
        self.status = "FAILED"
        self.completed_at = timezone.now()

        if remarks:
            self.remarks = remarks

        if self.started_at:
            duration = (
                self.completed_at - self.started_at
            ).total_seconds()

            self.actual_duration_seconds = int(duration)

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "actual_duration_seconds",
                "remarks",
                "updated_at",
            ]
        )

    def __str__(self):
        return (
            f"{self.stage_batch.batch_number} - "
            f"{self.process.name}"
        )




# class StageBatchProcessEquipmentExecution(models.Model):
#     """
#     Stores the equipment-level execution result for a process.

#     This is different from Equipment.current_state.

#     Equipment.current_state:
#         -> Current/global state of the physical equipment.

#     This model:
#         -> Stores the state produced by a particular process execution.

#     Example:

#         Process: Pump motor start
#         Equipment: PM1
#         State: ON

#         Process: Pump motor stop
#         Equipment: PM1
#         State: OFF
#     """

#     STATE_CHOICES = [
#         ("ON", "On"),
#         ("OFF", "Off"),
#     ]

#     stage_batch_process_execution = models.ForeignKey(
#         StageBatchProcessExecution,
#         on_delete=models.CASCADE,
#         related_name="equipment_executions",
#     )

#     equipment = models.ForeignKey(
#         "equipment.Equipment",
#         on_delete=models.PROTECT,
#         related_name="stage_batch_process_equipment_executions",
#     )

#     state = models.CharField(
#         max_length=10,
#         choices=STATE_CHOICES,
#         blank=True,
#         null=True,
#     )

#     started_at = models.DateTimeField(
#         blank=True,
#         null=True,
#     )

#     completed_at = models.DateTimeField(
#         blank=True,
#         null=True,
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#     )

#     class Meta:
#         db_table = "stage_batch_process_equipment_executions"

#         ordering = [
#             "stage_batch_process_execution__process__sequence",
#             "equipment__name",
#         ]

#         constraints = [
#             models.UniqueConstraint(
#                 fields=[
#                     "stage_batch_process_execution",
#                     "equipment",
#                 ],
#                 name="unique_process_equipment_execution",
#             )
#         ]

#         indexes = [
#             models.Index(
#                 fields=[
#                     "stage_batch_process_execution",
#                     "equipment",
#                 ],
#                 name="stage_process_equipment_idx",
#             ),

#             models.Index(
#                 fields=["equipment"],
#                 name="stage_equipment_idx",
#             ),

#             models.Index(
#                 fields=["state"],
#                 name="stage_process_state_idx",
#             ),
#         ]

#     def start_execution(self):
#         """
#         Mark equipment execution as started.
#         """

#         self.started_at = timezone.now()

#         self.save(
#             update_fields=[
#                 "started_at",
#                 "updated_at",
#             ]
#         )

#     def complete_execution(self, state):
#         """
#         Mark equipment execution as completed and store
#         the final ON/OFF state produced by this process.
#         """

#         self.state = state
#         self.completed_at = timezone.now()

#         self.save(
#             update_fields=[
#                 "state",
#                 "completed_at",
#                 "updated_at",
#             ]
#         )

#     def __str__(self):
#         return (
#             f"{self.stage_batch_process_execution.stage_batch.batch_number} - "
#             f"{self.stage_batch_process_execution.process.name} - "
#             f"{self.equipment.name} - "
#             f"{self.state}"
#         )





from django.db import models
from django.utils import timezone


class StageBatchProcessEquipmentExecution(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("WAITING", "Waiting"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("STOPPED", "Stopped"),
    ]

    STATE_CHOICES = [
        ("ON", "On"),
        ("OFF", "Off"),
    ]

    stage_batch_process_execution = models.ForeignKey(
        "treatment_process.StageBatchProcessExecution",
        on_delete=models.CASCADE,
        related_name="equipment_executions",
    )

    equipment = models.ForeignKey(
        "equipment.Equipment",
        on_delete=models.PROTECT,
        related_name="stage_batch_process_equipment_executions",
    )

    state = models.CharField(
        max_length=10,
        choices=STATE_CHOICES,
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    started_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    scheduled_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Time at which the next equipment operation should happen.",
    )

    actual_duration_seconds = models.PositiveIntegerField(
        default=0,
    )

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
        db_table = "stage_batch_process_equipment_executions"
        ordering = [
            "stage_batch_process_execution__process__sequence",
            "created_at",
        ]

        indexes = [
            models.Index(
                fields=["status", "scheduled_at"],
                name="equipment_exec_due_idx",
            ),
            models.Index(
                fields=["stage_batch_process_execution"],
                name="equipment_exec_process_idx",
            ),
        ]

    def start_execution(self):
        self.status = "RUNNING"
        self.started_at = timezone.now()

        self.save(
            update_fields=[
                "status",
                "started_at",
                "updated_at",
            ]
        )

    def wait_execution(self, scheduled_at):
        self.status = "WAITING"
        self.scheduled_at = scheduled_at

        self.save(
            update_fields=[
                "status",
                "scheduled_at",
                "updated_at",
            ]
        )

    def complete_execution(self, state):
        self.status = "COMPLETED"
        self.state = state
        self.completed_at = timezone.now()

        if self.started_at:
            self.actual_duration_seconds = int(
                (
                    self.completed_at -
                    self.started_at
                ).total_seconds()
            )

        self.save(
            update_fields=[
                "status",
                "state",
                "completed_at",
                "actual_duration_seconds",
                "updated_at",
            ]
        )

    def fail_execution(self, remarks=None):
        self.status = "FAILED"
        self.completed_at = timezone.now()

        if remarks:
            self.remarks = remarks

        if self.started_at:
            self.actual_duration_seconds = int(
                (
                    self.completed_at -
                    self.started_at
                ).total_seconds()
            )

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "actual_duration_seconds",
                "remarks",
                "updated_at",
            ]
        )

    def __str__(self):
        return (
            f"{self.stage_batch_process_execution} - "
            f"{self.equipment.name}"
        )