
from django.urls import path

from .views import (
    TreatmentStageListCreateView,
    TreatmentProcessListCreateView,
    TreatmentProcessCompleteView,
    TreatmentBatchListCreateView,
    TreatmentBatchStartView,
    TreatmentBatchCompleteView,
    TreatmentBatchStopView,
    TreatmentBatchCurrentStageView,
    TreatmentBatchCurrentProcessView,
    StageExecutionLogListCreateView,
    DosingRecordListCreateView,
    ProcessExecutionLogListCreateView,
    InletStageEquipmentView,
    TreatmentStageEquipmentListView,
    StageBatchStartView,
    StageBatchStatusView,
    StageBatchStopView,
    StageProcessLogListView,
    TreatmentStageWithBatchesAPIView,
)

urlpatterns = [
    path("stages/", TreatmentStageListCreateView.as_view(), name="treatment-stage-list-create"),
    path("processes/", TreatmentProcessListCreateView.as_view(), name="treatment-process-list-create"),
    path("process-execution/<int:pk>/complete/", TreatmentProcessCompleteView.as_view(), name="treatment-process-execution-complete"),

    path("batches/", TreatmentBatchListCreateView.as_view(), name="treatment-batch-list-create"),
    path("batches/<int:pk>/start/", TreatmentBatchStartView.as_view(), name="treatment-batch-start"),
    path("batches/<int:pk>/complete/", TreatmentBatchCompleteView.as_view(), name="treatment-batch-complete"),
    path("batches/<int:pk>/stop/", TreatmentBatchStopView.as_view(), name="treatment-batch-stop"),
    path("batches/<int:pk>/current-stage/", TreatmentBatchCurrentStageView.as_view(), name="treatment-batch-current-stage"),
    path("batches/<int:pk>/current-process/", TreatmentBatchCurrentProcessView.as_view(), name="treatment-batch-current-process"),

    path("stage-execution-logs/", StageExecutionLogListCreateView.as_view(), name="stage-execution-log-list-create"),
    path("dosing/", DosingRecordListCreateView.as_view(), name="dosing-list-create"),
    path("execution-logs/", ProcessExecutionLogListCreateView.as_view(), name="execution-log-list-create"),

    path("inlet-stages/", InletStageEquipmentView.as_view(), name="inlet-stage-equipment"),
    path("stages/<int:stage_id>/equipments/", TreatmentStageEquipmentListView.as_view(), name="treatment-stage-equipment-list"),

    path("stages/<int:stage_id>/start/", StageBatchStartView.as_view(), name="stage-batch-start"),
    path("stages/<int:stage_id>/status/", StageBatchStatusView.as_view(), name="stage-batch-status"),
    path("stages/<int:stage_id>/stop/", StageBatchStopView.as_view(), name="stage-batch-stop"),
    path("stages/<int:stage_id>/process-logs/", StageProcessLogListView.as_view(), name="stage-process-logs"),

    path("stages-with-batches/", TreatmentStageWithBatchesAPIView.as_view(), name="stages-with-batches"),
]
