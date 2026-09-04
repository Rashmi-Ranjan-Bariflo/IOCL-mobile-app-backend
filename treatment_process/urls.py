from django.urls import path

from .views import (
    TreatmentStageListCreateView,
    TreatmentProcessListCreateView,
    TreatmentBatchListCreateView,
    TreatmentBatchStartView,
    TreatmentBatchCompleteView,
    TreatmentBatchStopView,
    TreatmentBatchCurrentProcessView,
    DosingRecordListCreateView,
    ProcessExecutionLogListCreateView,
)

urlpatterns = [
    # ======================================================
    # TREATMENT STAGE
    # ======================================================
    path(
        "stages/",
        TreatmentStageListCreateView.as_view(),
        name="treatment-stage-list-create",
    ),
    # ======================================================
    # TREATMENT PROCESS
    # ======================================================
    path(
        "processes/",
        TreatmentProcessListCreateView.as_view(),
        name="treatment-process-list-create",
    ),
    # ======================================================
    # TREATMENT BATCH
    # ======================================================
    path(
        "batches/",
        TreatmentBatchListCreateView.as_view(),
        name="treatment-batch-list-create",
    ),
    path(
        "batches/<int:pk>/start/",
        TreatmentBatchStartView.as_view(),
        name="treatment-batch-start",
    ),
    path(
        "batches/<int:pk>/complete/",
        TreatmentBatchCompleteView.as_view(),
        name="treatment-batch-complete",
    ),
    path(
        "batches/<int:pk>/stop/",
        TreatmentBatchStopView.as_view(),
        name="treatment-batch-stop",
    ),
    path(
        "batches/<int:pk>/current-process/",
        TreatmentBatchCurrentProcessView.as_view(),
        name="treatment-batch-current-process",
    ),
    # ======================================================
    # DOSING RECORD
    # ======================================================
    path(
        "dosing/",
        DosingRecordListCreateView.as_view(),
        name="dosing-list-create",
    ),
    # ======================================================
    # PROCESS EXECUTION LOG
    # ======================================================
    path(
        "execution-logs/",
        ProcessExecutionLogListCreateView.as_view(),
        name="execution-log-list-create",
    ),
]
