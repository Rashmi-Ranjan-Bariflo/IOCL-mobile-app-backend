from django.urls import path

from .views import (
    TreatmentProcessListCreateView,
    TreatmentStageListCreateView,
    TreatmentBatchListCreateView,
    TreatmentBatchStartView,
    TreatmentBatchCompleteView,
    TreatmentBatchStopView,
    TreatmentBatchCurrentStageView,
    DosingRecordListCreateView,
    ProcessExecutionLogListCreateView,
)

urlpatterns = [
    # ======================================================
    # TREATMENT PROCESS
    # ======================================================
    path(
        "processes/",
        TreatmentProcessListCreateView.as_view(),
        name="treatment-process-list-create",
    ),
    # ======================================================
    # TREATMENT STAGE
    # ======================================================
    path(
        "stages/",
        TreatmentStageListCreateView.as_view(),
        name="treatment-stage-list-create",
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
        "batches/<int:pk>/current-stage/",
        TreatmentBatchCurrentStageView.as_view(),
        name="treatment-batch-current-stage",
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
