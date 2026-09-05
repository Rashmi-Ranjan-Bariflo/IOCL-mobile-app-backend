from django.urls import path

from .views import (
    # Treatment Stage
    TreatmentStageListCreateView,
    # Treatment Process
    TreatmentProcessListCreateView,
    TreatmentProcessCompleteView,
    # Treatment Batch
    TreatmentBatchListCreateView,
    TreatmentBatchStartView,
    TreatmentBatchCompleteView,
    TreatmentBatchStopView,
    TreatmentBatchCurrentStageView,
    TreatmentBatchCurrentProcessView,
    # Stage Execution
    StageExecutionLogListCreateView,
    # Dosing
    DosingRecordListCreateView,
    # Process Execution
    ProcessExecutionLogListCreateView,
    # Inlet Stage Equipment
    InletStageEquipmentView,
)

urlpatterns = [
    # ==========================================================
    # TREATMENT STAGE
    # ==========================================================
    path(
        "stages/",
        TreatmentStageListCreateView.as_view(),
        name="treatment-stage-list-create",
    ),
    # ==========================================================
    # TREATMENT PROCESS
    # ==========================================================
    path(
        "processes/",
        TreatmentProcessListCreateView.as_view(),
        name="treatment-process-list-create",
    ),
    # Complete currently running process
    path(
        "process-execution/<int:pk>/complete/",
        TreatmentProcessCompleteView.as_view(),
        name="treatment-process-execution-complete",
    ),
    # ==========================================================
    # TREATMENT BATCH
    # ==========================================================
    # Create / List batches
    path(
        "batches/",
        TreatmentBatchListCreateView.as_view(),
        name="treatment-batch-list-create",
    ),
    # Start batch
    path(
        "batches/<int:pk>/start/",
        TreatmentBatchStartView.as_view(),
        name="treatment-batch-start",
    ),
    # Complete batch
    path(
        "batches/<int:pk>/complete/",
        TreatmentBatchCompleteView.as_view(),
        name="treatment-batch-complete",
    ),
    # Stop batch
    path(
        "batches/<int:pk>/stop/",
        TreatmentBatchStopView.as_view(),
        name="treatment-batch-stop",
    ),
    # Get current running stage
    path(
        "batches/<int:pk>/current-stage/",
        TreatmentBatchCurrentStageView.as_view(),
        name="treatment-batch-current-stage",
    ),
    # Get current running process
    path(
        "batches/<int:pk>/current-process/",
        TreatmentBatchCurrentProcessView.as_view(),
        name="treatment-batch-current-process",
    ),
    # ==========================================================
    # STAGE EXECUTION LOG
    # ==========================================================
    path(
        "stage-execution-logs/",
        StageExecutionLogListCreateView.as_view(),
        name="stage-execution-log-list-create",
    ),
    # ==========================================================
    # DOSING RECORD
    # ==========================================================
    path(
        "dosing/",
        DosingRecordListCreateView.as_view(),
        name="dosing-list-create",
    ),
    # ==========================================================
    # PROCESS EXECUTION LOG
    # ==========================================================
    path(
        "execution-logs/",
        ProcessExecutionLogListCreateView.as_view(),
        name="execution-log-list-create",
    ),
    # ==========================================================
    # INLET STAGE EQUIPMENT
    # ==========================================================
    path(
        "inlet-stages/",
        InletStageEquipmentView.as_view(),
        name="inlet-stage-equipment",
    ),
]
