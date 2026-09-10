from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    TreatmentStage,
    TreatmentProcess,
    TreatmentBatch,
    StageExecutionLog,
    DosingRecord,
    ProcessExecutionLog,
    StageBatch,
    StageBatchProcessExecution
)

from .serializers import (
    TreatmentStageSerializer,
    TreatmentProcessSerializer,
    TreatmentBatchSerializer,
    StageExecutionLogSerializer,
    DosingRecordSerializer,
    ProcessExecutionLogSerializer,
)

from equipment.models import Equipment
from sensors.models import Sensor

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================


def get_stage_for_user(stage_id, user):
    """
    Get treatment stage belonging to logged-in user.
    """
    return TreatmentStage.objects.filter(
        id=stage_id,
        user=user,
    ).first()


def get_process_for_user(process_id, user):
    """
    Get treatment process belonging to logged-in user
    through its treatment stage.
    """
    return (
        TreatmentProcess.objects.filter(
            id=process_id,
            stage__user=user,
        )
        .select_related("stage")
        .first()
    )


def get_batch_for_user(batch_id, user):
    """
    Get treatment batch belonging to the logged-in user.

    A batch does not directly have a user field, so ownership
    is determined through its stage execution logs.
    """

    return (
        TreatmentBatch.objects.filter(
            id=batch_id,
            stage_execution_logs__stage__user=user,
        )
        .distinct()
        .first()
    )


# ==========================================================
# STAGE STATUS UPDATE
# ==========================================================


def update_stage_status(stage_execution):
    """
    Check all processes belonging to the stage for this batch.

    Rules:

    1. If any process FAILED -> stage FAILED
    2. If any process STOPPED -> stage STOPPED
    3. If all processes COMPLETED -> stage COMPLETED
    4. If any process RUNNING/STARTED -> stage RUNNING
    5. Otherwise -> stage remains PENDING
    """

    batch = stage_execution.batch
    stage = stage_execution.stage

    processes = TreatmentProcess.objects.filter(
        stage=stage,
        is_active=True,
    )

    process_logs = ProcessExecutionLog.objects.filter(
        batch=batch,
        process__stage=stage,
    )

    total_processes = processes.count()

    if total_processes == 0:
        return stage_execution

    failed_exists = process_logs.filter(status="FAILED").exists()

    stopped_exists = process_logs.filter(status="STOPPED").exists()

    if failed_exists:
        stage_execution.status = "FAILED"
        stage_execution.completed_at = timezone.now()

    elif stopped_exists:
        stage_execution.status = "STOPPED"
        stage_execution.completed_at = timezone.now()

    else:

        completed_count = process_logs.filter(status="COMPLETED").count()

        running_exists = process_logs.filter(status__in=["STARTED", "RUNNING"]).exists()

        if completed_count == total_processes:
            stage_execution.status = "COMPLETED"
            stage_execution.completed_at = timezone.now()

        elif running_exists:
            stage_execution.status = "RUNNING"

        else:
            stage_execution.status = "PENDING"

    # Calculate duration
    if stage_execution.completed_at and stage_execution.started_at:
        stage_execution.actual_duration_seconds = int(
            (stage_execution.completed_at - stage_execution.started_at).total_seconds()
        )

    stage_execution.save(
        update_fields=[
            "status",
            "completed_at",
            "actual_duration_seconds",
            "updated_at",
        ]
    )

    return stage_execution


# ==========================================================
# BATCH STATUS UPDATE
# ==========================================================


def update_batch_status(batch):
    """
    Check all stage executions of a batch.

    Rules:

    - Any stage FAILED -> batch FAILED
    - Any stage STOPPED -> batch STOPPED
    - All stages COMPLETED -> batch COMPLETED
    - Otherwise -> batch RUNNING/PENDING
    """

    stage_logs = StageExecutionLog.objects.filter(batch=batch)

    total_stages = stage_logs.count()

    if total_stages == 0:
        return batch

    failed_exists = stage_logs.filter(status="FAILED").exists()

    stopped_exists = stage_logs.filter(status="STOPPED").exists()

    completed_count = stage_logs.filter(status="COMPLETED").count()

    running_exists = stage_logs.filter(status__in=["STARTED", "RUNNING"]).exists()

    now = timezone.now()

    if failed_exists:

        batch.status = "FAILED"

        if not batch.completed_at:
            batch.completed_at = now

    elif stopped_exists:

        batch.status = "STOPPED"

        if not batch.completed_at:
            batch.completed_at = now

    elif completed_count == total_stages:

        batch.status = "COMPLETED"

        if not batch.completed_at:
            batch.completed_at = now

    elif running_exists:

        batch.status = "RUNNING"

    else:

        batch.status = "PENDING"

    batch.save(
        update_fields=[
            "status",
            "completed_at",
            "updated_at",
        ]
    )

    return batch


# ==========================================================
# TREATMENT STAGE
# ==========================================================


class TreatmentStageListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        stages = TreatmentStage.objects.filter(user=request.user).prefetch_related(
            "equipments",
            "processes",
        )

        stage_type = request.query_params.get("stage_type")
        is_active = request.query_params.get("is_active")

        if stage_type:
            stages = stages.filter(stage_type=stage_type)

        if is_active is not None:

            stages = stages.filter(is_active=is_active.lower() == "true")

        stages = stages.order_by("sequence")

        serializer = TreatmentStageSerializer(stages, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )

    def post(self, request):

        serializer = TreatmentStageSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save(user=request.user)

            return Response(
                {
                    "success": True,
                    "message": "Treatment stage created successfully.",
                    "data": TreatmentStageSerializer(serializer.instance).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# TREATMENT PROCESS
# ==========================================================


class TreatmentProcessListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        processes = TreatmentProcess.objects.filter(
            stage__user=request.user
        ).select_related("stage")

        stage_id = request.query_params.get("stage")
        is_active = request.query_params.get("is_active")

        if stage_id:

            processes = processes.filter(stage_id=stage_id)

        if is_active is not None:

            processes = processes.filter(is_active=is_active.lower() == "true")

        processes = processes.order_by(
            "stage__sequence",
            "sequence",
        )

        serializer = TreatmentProcessSerializer(processes, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )

    def post(self, request):

        serializer = TreatmentProcessSerializer(data=request.data)

        if serializer.is_valid():

            stage = get_stage_for_user(
                serializer.validated_data["stage"].id,
                request.user,
            )

            if not stage:

                return Response(
                    {
                        "success": False,
                        "message": "Invalid treatment stage.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Treatment process created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# TREATMENT BATCH
# ==========================================================


class TreatmentBatchListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        batches = (
            TreatmentBatch.objects.filter(
                stage_execution_logs__stage__user=request.user
            )
            .prefetch_related(
                "stage_execution_logs",
                "process_execution_logs",
            )
            .distinct()
        )

        stage_id = request.query_params.get("stage")
        batch_status = request.query_params.get("status")

        if stage_id:

            batches = batches.filter(stage_execution_logs__stage_id=stage_id)

        if batch_status:

            batches = batches.filter(status=batch_status)

        batches = batches.order_by("-created_at")

        serializer = TreatmentBatchSerializer(batches, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )

    @transaction.atomic
    def post(self, request):

        serializer = TreatmentBatchSerializer(data=request.data)

        if not serializer.is_valid():

            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        batch = serializer.save()

        # --------------------------------------------------
        # Create StageExecutionLog for all active stages
        # belonging to this user.
        # --------------------------------------------------

        stages = TreatmentStage.objects.filter(
            user=request.user,
            is_active=True,
        ).order_by("sequence")

        stage_logs = []

        for stage in stages:

            stage_logs.append(
                StageExecutionLog(
                    batch=batch,
                    stage=stage,
                    status="PENDING",
                )
            )

        StageExecutionLog.objects.bulk_create(stage_logs)

        return Response(
            {
                "success": True,
                "message": "Treatment batch created successfully.",
                "data": TreatmentBatchSerializer(batch).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# START TREATMENT BATCH
# ==========================================================


class TreatmentBatchStartView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):

        batch = get_batch_for_user(pk, request.user)

        if not batch:

            return Response(
                {
                    "success": False,
                    "message": "Treatment batch not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if batch.status == "RUNNING":

            return Response(
                {
                    "success": False,
                    "message": "Treatment batch is already running.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if batch.status == "COMPLETED":

            return Response(
                {
                    "success": False,
                    "message": "Completed batch cannot be started again.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        batch.status = "RUNNING"
        batch.started_at = now
        batch.completed_at = None

        batch.save(
            update_fields=[
                "status",
                "started_at",
                "completed_at",
                "updated_at",
            ]
        )

        # --------------------------------------------------
        # Get first stage
        # --------------------------------------------------

        stage_execution = (
            StageExecutionLog.objects.filter(
                batch=batch,
                stage__user=request.user,
            )
            .select_related("stage")
            .order_by("stage__sequence")
            .first()
        )

        if not stage_execution:

            return Response(
                {
                    "success": False,
                    "message": "No treatment stages found for this batch.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        stage_execution.status = "RUNNING"
        stage_execution.started_at = now

        stage_execution.save(
            update_fields=[
                "status",
                "started_at",
                "updated_at",
            ]
        )

        # --------------------------------------------------
        # Get first process of first stage
        # --------------------------------------------------

        first_process = (
            TreatmentProcess.objects.filter(
                stage=stage_execution.stage,
                is_active=True,
            )
            .order_by("sequence")
            .first()
        )

        if first_process:

            ProcessExecutionLog.objects.create(
                batch=batch,
                process=first_process,
                status="STARTED",
                started_at=now,
            )

        return Response(
            {
                "success": True,
                "message": "Treatment batch started successfully.",
                "data": TreatmentBatchSerializer(batch).data,
            }
        )


# ==========================================================
# COMPLETE CURRENT PROCESS
# ==========================================================


class TreatmentProcessCompleteView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):

        process_log = (
            ProcessExecutionLog.objects.filter(
                id=pk,
                batch__stage_execution_logs__stage__user=request.user,
            )
            .select_related(
                "batch",
                "process",
                "process__stage",
            )
            .first()
        )

        if not process_log:

            return Response(
                {
                    "success": False,
                    "message": "Process execution log not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if process_log.status == "COMPLETED":

            return Response(
                {
                    "success": False,
                    "message": "Process is already completed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        process_log.status = "COMPLETED"
        process_log.completed_at = now

        if process_log.started_at:

            process_log.actual_duration_seconds = int(
                (now - process_log.started_at).total_seconds()
            )

        process_log.save(
            update_fields=[
                "status",
                "completed_at",
                "actual_duration_seconds",
                "updated_at",
            ]
        )

        # --------------------------------------------------
        # Check current stage
        # --------------------------------------------------

        stage_execution = StageExecutionLog.objects.select_related(
            "batch",
            "stage",
        ).get(
            batch=process_log.batch,
            stage=process_log.process.stage,
        )

        update_stage_status(stage_execution)

        # --------------------------------------------------
        # If stage completed, start next stage
        # --------------------------------------------------

        if stage_execution.status == "COMPLETED":

            next_stage_execution = (
                StageExecutionLog.objects.filter(
                    batch=process_log.batch,
                    stage__sequence__gt=(stage_execution.stage.sequence),
                    status="PENDING",
                )
                .select_related("stage")
                .order_by("stage__sequence")
                .first()
            )

            if next_stage_execution:

                next_stage_execution.status = "RUNNING"
                next_stage_execution.started_at = now

                next_stage_execution.save(
                    update_fields=[
                        "status",
                        "started_at",
                        "updated_at",
                    ]
                )

                next_process = (
                    TreatmentProcess.objects.filter(
                        stage=next_stage_execution.stage,
                        is_active=True,
                    )
                    .order_by("sequence")
                    .first()
                )

                if next_process:

                    ProcessExecutionLog.objects.create(
                        batch=process_log.batch,
                        process=next_process,
                        status="STARTED",
                        started_at=now,
                    )

        # --------------------------------------------------
        # Update batch
        # --------------------------------------------------

        update_batch_status(process_log.batch)

        return Response(
            {
                "success": True,
                "message": "Process completed successfully.",
                "data": ProcessExecutionLogSerializer(process_log).data,
            }
        )


# ==========================================================
# COMPLETE TREATMENT BATCH
# ==========================================================


class TreatmentBatchCompleteView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):

        batch = get_batch_for_user(pk, request.user)

        if not batch:

            return Response(
                {
                    "success": False,
                    "message": "Treatment batch not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if batch.status == "COMPLETED":

            return Response(
                {
                    "success": False,
                    "message": "Treatment batch is already completed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Verify all stages are completed
        # --------------------------------------------------

        stage_logs = StageExecutionLog.objects.filter(batch=batch)

        total_stages = stage_logs.count()

        completed_stages = stage_logs.filter(status="COMPLETED").count()

        if total_stages == 0:

            return Response(
                {
                    "success": False,
                    "message": "No treatment stages found.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if completed_stages != total_stages:

            return Response(
                {
                    "success": False,
                    "message": (
                        "Treatment batch cannot be completed. "
                        "All treatment stages must be completed first."
                    ),
                    "completed_stages": completed_stages,
                    "total_stages": total_stages,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        batch.status = "COMPLETED"
        batch.completed_at = now

        batch.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

        return Response(
            {
                "success": True,
                "message": "Treatment batch completed successfully.",
                "data": TreatmentBatchSerializer(batch).data,
            }
        )


# ==========================================================
# STOP TREATMENT BATCH
# ==========================================================


class TreatmentBatchStopView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):

        batch = get_batch_for_user(pk, request.user)

        if not batch:

            return Response(
                {
                    "success": False,
                    "message": "Treatment batch not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if batch.status != "RUNNING":

            return Response(
                {
                    "success": False,
                    "message": "Only a running batch can be stopped.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        # --------------------------------------------------
        # Stop batch
        # --------------------------------------------------

        batch.status = "STOPPED"
        batch.completed_at = now

        batch.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

        # --------------------------------------------------
        # Stop running stage
        # --------------------------------------------------

        stage_log = (
            StageExecutionLog.objects.filter(
                batch=batch,
                status__in=["STARTED", "RUNNING"],
            )
            .order_by("-created_at")
            .first()
        )

        if stage_log:

            stage_log.status = "STOPPED"
            stage_log.completed_at = now
            stage_log.remarks = "Treatment batch stopped."

            if stage_log.started_at:

                stage_log.actual_duration_seconds = int(
                    (now - stage_log.started_at).total_seconds()
                )

            stage_log.save(
                update_fields=[
                    "status",
                    "completed_at",
                    "actual_duration_seconds",
                    "remarks",
                    "updated_at",
                ]
            )

        # --------------------------------------------------
        # Stop running process
        # --------------------------------------------------

        process_log = (
            ProcessExecutionLog.objects.filter(
                batch=batch,
                status__in=["STARTED", "RUNNING"],
            )
            .order_by("-created_at")
            .first()
        )

        if process_log:

            process_log.status = "STOPPED"
            process_log.completed_at = now
            process_log.remarks = "Treatment batch stopped."

            if process_log.started_at:

                process_log.actual_duration_seconds = int(
                    (now - process_log.started_at).total_seconds()
                )

            process_log.save(
                update_fields=[
                    "status",
                    "completed_at",
                    "actual_duration_seconds",
                    "remarks",
                    "updated_at",
                ]
            )

        return Response(
            {
                "success": True,
                "message": "Treatment batch stopped successfully.",
                "data": TreatmentBatchSerializer(batch).data,
            }
        )


# ==========================================================
# CURRENT STAGE
# ==========================================================


class TreatmentBatchCurrentStageView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        batch = get_batch_for_user(pk, request.user)

        if not batch:

            return Response(
                {
                    "success": False,
                    "message": "Treatment batch not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        stage_log = (
            StageExecutionLog.objects.filter(
                batch=batch,
                status__in=["STARTED", "RUNNING"],
            )
            .select_related("stage")
            .first()
        )

        if not stage_log:

            return Response(
                {
                    "success": True,
                    "message": "No current stage.",
                    "data": None,
                }
            )

        serializer = StageExecutionLogSerializer(stage_log)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )


# ==========================================================
# CURRENT PROCESS
# ==========================================================


class TreatmentBatchCurrentProcessView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        batch = get_batch_for_user(pk, request.user)

        if not batch:

            return Response(
                {
                    "success": False,
                    "message": "Treatment batch not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        process_log = (
            ProcessExecutionLog.objects.filter(
                batch=batch,
                status__in=["STARTED", "RUNNING"],
            )
            .select_related(
                "process",
                "process__stage",
            )
            .order_by("-created_at")
            .first()
        )

        if not process_log:

            return Response(
                {
                    "success": True,
                    "message": "No current process.",
                    "data": None,
                }
            )

        serializer = TreatmentProcessSerializer(process_log.process)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )


# ==========================================================
# STAGE EXECUTION LOG
# ==========================================================


class StageExecutionLogListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        logs = StageExecutionLog.objects.filter(
            stage__user=request.user
        ).select_related(
            "batch",
            "stage",
        )

        batch_id = request.query_params.get("batch")
        stage_id = request.query_params.get("stage")
        log_status = request.query_params.get("status")

        if batch_id:

            logs = logs.filter(batch_id=batch_id)

        if stage_id:

            logs = logs.filter(stage_id=stage_id)

        if log_status:

            logs = logs.filter(status=log_status)

        logs = logs.order_by(
            "batch",
            "stage__sequence",
        )

        serializer = StageExecutionLogSerializer(logs, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )

    def post(self, request):

        serializer = StageExecutionLogSerializer(data=request.data)

        if serializer.is_valid():

            batch = get_batch_for_user(
                serializer.validated_data["batch"].id,
                request.user,
            )

            if not batch:

                return Response(
                    {
                        "success": False,
                        "message": "Invalid treatment batch.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            stage = get_stage_for_user(
                serializer.validated_data["stage"].id,
                request.user,
            )

            if not stage:

                return Response(
                    {
                        "success": False,
                        "message": "Invalid treatment stage.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Stage execution log created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# DOSING RECORD
# ==========================================================


class DosingRecordListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        records = (
            DosingRecord.objects.filter(
                batch__stage_execution_logs__stage__user=request.user
            )
            .select_related(
                "batch",
            )
            .distinct()
        )

        batch_id = request.query_params.get("batch")
        solution_type = request.query_params.get("solution_type")

        if batch_id:

            records = records.filter(batch_id=batch_id)

        if solution_type:

            records = records.filter(solution_type=solution_type)

        records = records.order_by("-dosing_time")

        serializer = DosingRecordSerializer(records, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )

    def post(self, request):

        serializer = DosingRecordSerializer(data=request.data)

        if serializer.is_valid():

            batch = get_batch_for_user(
                serializer.validated_data["batch"].id,
                request.user,
            )

            if not batch:

                return Response(
                    {
                        "success": False,
                        "message": "Invalid treatment batch.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Dosing record created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# PROCESS EXECUTION LOG
# ==========================================================


class ProcessExecutionLogListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        logs = (
            ProcessExecutionLog.objects.filter(
                batch__stage_execution_logs__stage__user=request.user
            )
            .select_related(
                "batch",
                "process",
                "process__stage",
            )
            .distinct()
        )

        batch_id = request.query_params.get("batch")
        process_id = request.query_params.get("process")
        stage_id = request.query_params.get("stage")
        log_status = request.query_params.get("status")

        if batch_id:

            logs = logs.filter(batch_id=batch_id)

        if process_id:

            logs = logs.filter(process_id=process_id)

        if stage_id:

            logs = logs.filter(process__stage_id=stage_id)

        if log_status:

            logs = logs.filter(status=log_status)

        logs = logs.order_by("-created_at")

        serializer = ProcessExecutionLogSerializer(logs, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )

    def post(self, request):

        serializer = ProcessExecutionLogSerializer(data=request.data)

        if serializer.is_valid():

            batch = get_batch_for_user(
                serializer.validated_data["batch"].id,
                request.user,
            )

            if not batch:

                return Response(
                    {
                        "success": False,
                        "message": "Invalid treatment batch.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            process = get_process_for_user(
                serializer.validated_data["process"].id,
                request.user,
            )

            if not process:

                return Response(
                    {
                        "success": False,
                        "message": "Invalid treatment process.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # --------------------------------------------------
            # Make sure process belongs to a stage associated
            # with this batch.
            # --------------------------------------------------

            stage_exists = StageExecutionLog.objects.filter(
                batch=batch,
                stage=process.stage,
            ).exists()

            if not stage_exists:

                return Response(
                    {
                        "success": False,
                        "message": (
                            "This process stage is not associated "
                            "with the selected batch."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Process execution log created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# INLET STAGES WITH EQUIPMENT AND SENSORS
# ==========================================================


class InletStageEquipmentView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # --------------------------------------------------
        # Equipment belonging to logged-in user
        # --------------------------------------------------

        equipment_queryset = (
            Equipment.objects.filter(
                user=request.user,
                is_active=True,
            )
            .select_related(
                "equipment_type",
            )
            .prefetch_related(
                Prefetch(
                    "sensors",
                    queryset=(
                        Sensor.objects.select_related("sensor_type")
                        .filter(is_active=True)
                        .order_by("name")
                    ),
                )
            )
            .order_by("name")
        )

        # --------------------------------------------------
        # Wastewater + Normal Water stages
        # --------------------------------------------------

        stages = (
            TreatmentStage.objects.filter(
                user=request.user,
                stage_type__in=[
                    "WASTEWATER_COLLECTION",
                    "NORMALWATER_COLLECTION",
                ],
                is_active=True,
            )
            .prefetch_related(
                Prefetch(
                    "equipments",
                    queryset=equipment_queryset,
                )
            )
            .order_by("sequence")
        )

        wastewater_stage_data = None
        normalwater_stage_data = None

        # --------------------------------------------------
        # Build response
        # --------------------------------------------------

        for stage in stages:

            equipment_data = []

            for equipment in stage.equipments.all():

                sensors_data = []

                for sensor in equipment.sensors.all():

                    sensors_data.append(
                        {
                            "id": sensor.id,
                            "name": sensor.name,
                            "code": sensor.code,
                            "sensor_type": (
                                sensor.sensor_type.name if sensor.sensor_type else None
                            ),
                            "unit": sensor.unit,
                            "status": sensor.status,
                            "is_active": sensor.is_active,
                        }
                    )

                equipment_data.append(
                    {
                        "id": equipment.id,
                        "name": equipment.name,
                        "code": equipment.code,
                        "equipment_type": (
                            equipment.equipment_type.name
                            if equipment.equipment_type
                            else None
                        ),
                        "description": equipment.description,
                        "location": equipment.location,
                        "status": equipment.status,
                        "is_active": equipment.is_active,
                        "sensors": sensors_data,
                    }
                )

            stage_data = {
                "id": stage.id,
                "name": stage.name,
                "stage_type": stage.stage_type,
                "sequence": stage.sequence,
                "description": stage.description,
                "equipment": equipment_data,
            }

            if stage.stage_type == "WASTEWATER_COLLECTION":

                wastewater_stage_data = stage_data

            elif stage.stage_type == "NORMALWATER_COLLECTION":

                normalwater_stage_data = stage_data

        # --------------------------------------------------
        # Final response
        # --------------------------------------------------

        return Response(
            {
                "success": True,
                "data": {
                    "wastewater_stage": wastewater_stage_data,
                    "normalwater_stage": normalwater_stage_data,
                },
            }
        )




# class TreatmentStageEquipmentListView(APIView):

#     permission_classes = [IsAuthenticated]

#     def get(self, request, stage_id):

#         try:
#             stage = (
#                 TreatmentStage.objects
#                 .filter(
#                     id=stage_id,
#                     user=request.user,
#                     is_active=True,
#                 )
#                 .prefetch_related(
#                     Prefetch(
#                         "equipments",
#                         queryset=Equipment.objects
#                         .filter(is_active=True)
#                         .select_related("equipment_type")
#                         .prefetch_related(
#                             Prefetch(
#                                 "sensors",
#                                 queryset=Sensor.objects
#                                 .filter(is_active=True)
#                                 .select_related("sensor_type")
#                                 .order_by("name"),
#                             )
#                         )
#                         .order_by("name"),
#                     )
#                 )
#                 .first()
#             )

#             if not stage:
#                 return Response(
#                     {
#                         "success": False,
#                         "message": "Treatment stage not found.",
#                     },
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             equipment_data = []

#             for equipment in stage.equipments.all():

#                 sensors = []

#                 for sensor in equipment.sensors.all():
#                     sensors.append(
#                         {
#                             "id": sensor.id,
#                             "name": sensor.name,
#                             "code": sensor.code,
#                             "sensor_type": {
#                                 "id": sensor.sensor_type.id,
#                                 "name": sensor.sensor_type.name,
#                             },
#                             "unit": sensor.unit,
#                             "status": sensor.status,
#                             "location": sensor.location,
#                         }
#                     )

#                 equipment_data.append(
#                     {
#                         "id": equipment.id,
#                         "name": equipment.name,
#                         "code": equipment.code,
#                         "equipment_type": {
#                             "id": equipment.equipment_type.id,
#                             "name": equipment.equipment_type.name,
#                         },
#                         "description": equipment.description,
#                         "location": equipment.location,
#                         "manufacturer": equipment.manufacturer,
#                         "model_number": equipment.model_number,
#                         "serial_number": equipment.serial_number,
#                         "status": equipment.status,
#                         "sensors": sensors,
#                     }
#                 )

#             return Response(
#                 {
#                     "success": True,
#                     "data": {
#                         "stage": {
#                             "id": stage.id,
#                             "name": stage.name,
#                             "stage_type": stage.stage_type,
#                             "sequence": stage.sequence,
#                         },
#                         "equipments": equipment_data,
#                     },
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as e:

#             return Response(
#                 {
#                     "success": False,
#                     "message": "Failed to fetch stage equipment.",
#                     "error": str(e),
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )






# class TreatmentStageEquipmentListView(APIView):

#     permission_classes = [IsAuthenticated]

#     def get(self, request, stage_id):

#         try:
#             # ---------------------------------------------------------
#             # Get treatment stage with:
#             # 1. Active equipments
#             # 2. Equipment type
#             # 3. Active sensors
#             # 4. Sensor type
#             # ---------------------------------------------------------
#             stage = (
#                 TreatmentStage.objects
#                 .filter(
#                     id=stage_id,
#                     user=request.user,
#                     is_active=True,
#                 )
#                 .prefetch_related(
#                     Prefetch(
#                         "equipments",
#                         queryset=Equipment.objects
#                         .filter(is_active=True)
#                         .select_related("equipment_type")
#                         .prefetch_related(
#                             Prefetch(
#                                 "sensors",
#                                 queryset=Sensor.objects
#                                 .filter(is_active=True)
#                                 .select_related("sensor_type")
#                                 .order_by("name"),
#                             )
#                         )
#                         .order_by("name"),
#                     )
#                 )
#                 .first()
#             )

#             # ---------------------------------------------------------
#             # Validate treatment stage
#             # ---------------------------------------------------------
#             if not stage:
#                 return Response(
#                     {
#                         "success": False,
#                         "message": "Treatment stage not found.",
#                     },
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             # ---------------------------------------------------------
#             # Get latest batch created for this stage
#             #
#             # stage.stage_batches comes from:
#             # StageBatch.stage = ForeignKey(
#             #     TreatmentStage,
#             #     related_name="stage_batches"
#             # )
#             #
#             # StageBatch Meta ordering is already:
#             # ordering = ["-created_at"]
#             #
#             # Therefore .first() gives the latest batch.
#             # ---------------------------------------------------------
#             latest_batch = stage.stage_batches.first()

#             # ---------------------------------------------------------
#             # Prepare equipment response
#             # ---------------------------------------------------------
#             equipment_data = []

#             for equipment in stage.equipments.all():

#                 sensors = []

#                 # -----------------------------------------------------
#                 # Get all active sensors linked to this equipment
#                 # -----------------------------------------------------
#                 for sensor in equipment.sensors.all():

#                     sensors.append(
#                         {
#                             "id": sensor.id,
#                             "name": sensor.name,
#                             "code": sensor.code,
#                             "sensor_type": {
#                                 "id": sensor.sensor_type.id,
#                                 "name": sensor.sensor_type.name,
#                             },
#                             "unit": sensor.unit,
#                             "status": sensor.status,
#                             "location": sensor.location,
#                         }
#                     )

#                 # -----------------------------------------------------
#                 # Equipment details
#                 # -----------------------------------------------------
#                 equipment_data.append(
#                     {
#                         "id": equipment.id,
#                         "name": equipment.name,
#                         "code": equipment.code,
#                         "equipment_type": {
#                             "id": equipment.equipment_type.id,
#                             "name": equipment.equipment_type.name,
#                         },
#                         "description": equipment.description,
#                         "location": equipment.location,
#                         "manufacturer": equipment.manufacturer,
#                         "model_number": equipment.model_number,
#                         "serial_number": equipment.serial_number,
#                         "status": equipment.status,
#                         "sensors": sensors,
#                     }
#                 )

#             # ---------------------------------------------------------
#             # Prepare latest batch data
#             #
#             # If no batch has ever been created for this stage,
#             # return None.
#             # ---------------------------------------------------------
#             latest_batch_data = None

#             if latest_batch:
#                 latest_batch_data = {
#                     "id": latest_batch.id,
#                     "batch_number": latest_batch.batch_number,
#                     "status": latest_batch.status,
#                     "started_at": latest_batch.started_at,
#                     "completed_at": latest_batch.completed_at,
#                 }

#             # ---------------------------------------------------------
#             # Final response
#             # ---------------------------------------------------------
#             return Response(
#                 {
#                     "success": True,
#                     "data": {
#                         "stage": {
#                             "id": stage.id,
#                             "name": stage.name,
#                             "stage_type": stage.stage_type,
#                             "sequence": stage.sequence,
#                         },

#                         # -------------------------------------------------
#                         # Latest batch for this stage
#                         #
#                         # Frontend can use latest_batch.id to call
#                         # the stage batch status API if the batch ID
#                         # returned by the START API is not available.
#                         # -------------------------------------------------
#                         "latest_batch": latest_batch_data,

#                         "equipments": equipment_data,
#                     },
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as e:

#             return Response(
#                 {
#                     "success": False,
#                     "message": "Failed to fetch stage equipment.",
#                     "error": str(e),
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


class TreatmentStageEquipmentListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, stage_id):

        try:

            # ---------------------------------------------------------
            # Get treatment stage with active equipments
            # and equipment type.
            # ---------------------------------------------------------
            stage = (
                TreatmentStage.objects
                .filter(
                    id=stage_id,
                    user=request.user,
                    is_active=True,
                )
                .prefetch_related(
                    Prefetch(
                        "equipments",
                        queryset=Equipment.objects
                        .filter(is_active=True)
                        .select_related("equipment_type")
                        .order_by("name"),
                    )
                )
                .first()
            )
            print(stage)

            # ---------------------------------------------------------
            # Validate treatment stage
            # ---------------------------------------------------------
            if not stage:
                return Response(
                    {
                        "success": False,
                        "message": "Treatment stage not found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # ---------------------------------------------------------
            # Group equipments by equipment type
            # ---------------------------------------------------------
            equipment_types = {}

            for equipment in stage.equipments.all():

                equipment_type = equipment.equipment_type

                # -----------------------------------------------------
                # Create equipment type entry if it does not exist
                # -----------------------------------------------------
                if equipment_type.id not in equipment_types:

                    equipment_types[equipment_type.id] = {
                        "equipment_type": {
                            "id": equipment_type.id,
                            "name": equipment_type.name,
                        },
                        "count": 0,
                        "equipments": [],
                    }

                # -----------------------------------------------------
                # Increase equipment count
                # -----------------------------------------------------
                equipment_types[equipment_type.id]["count"] += 1

                # -----------------------------------------------------
                # Add only equipment ID and name
                # -----------------------------------------------------
                equipment_types[equipment_type.id]["equipments"].append(
                    {
                        "id": equipment.id,
                        "name": equipment.name,
                    }
                )

            # ---------------------------------------------------------
            # Convert dictionary to list
            # ---------------------------------------------------------
            equipment_type_data = list(
                equipment_types.values()
            )

            # ---------------------------------------------------------
            # Final response
            # ---------------------------------------------------------
            return Response(
                {
                    "success": True,
                    "data": {
                        "stage": {
                            "id": stage.id,
                            "name": stage.name,
                            "stage_type": stage.stage_type,
                            "sequence": stage.sequence,
                        },
                        "equipment_types": equipment_type_data,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:

            return Response(
                {
                    "success": False,
                    "message": "Failed to fetch stage equipment.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )




from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from treatment_process.models import (
    TreatmentStage,
    StageBatchProcessExecution,
)


class StageProcessLogListView(APIView):
    """
    Get the latest 50 process execution logs
    for a specific treatment stage.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, stage_id):

        try:

            # ---------------------------------------------------------
            # Validate stage
            # ---------------------------------------------------------
            stage = TreatmentStage.objects.filter(
                id=stage_id,
                user=request.user,
                is_active=True,
            ).first()

            if not stage:
                return Response(
                    {
                        "success": False,
                        "message": "Treatment stage not found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # ---------------------------------------------------------
            # Get latest 50 process executions
            # belonging to this stage
            # ---------------------------------------------------------
            process_logs = (
                StageBatchProcessExecution.objects
                .filter(
                    stage_batch__stage=stage,
                )
                .select_related(
                    "stage_batch",
                    "process",
                )
                .order_by("-created_at")[:50]
            )

            data = []

            for log in process_logs:

                data.append(
                    {
                        "id": log.id,

                        "batch_id": log.stage_batch.id,

                        "batch_number": (
                            log.stage_batch.batch_number
                        ),

                        "process_id": log.process.id,

                        "process_name": log.process.name,

                        "sequence": log.process.sequence,

                        "status": log.status,

                        "started_at": log.started_at,

                        "completed_at": log.completed_at,

                        "actual_duration_seconds": (
                            log.actual_duration_seconds
                        ),

                        "remarks": log.remarks,
                    }
                )

            return Response(
                {
                    "success": True,
                    "message": (
                        "Stage process logs "
                        "retrieved successfully."
                    ),
                    "count": len(data),
                    "data": data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:

            return Response(
                {
                    "success": False,
                    "message": (
                        "Failed to retrieve "
                        "stage process logs."
                    ),
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# class StageBatchStartView(APIView):

#     permission_classes = [IsAuthenticated]

#     def post(self, request, stage_id):

#         try:

#             with transaction.atomic():

#                 # --------------------------------------------------
#                 # 1. Get the selected stage
#                 # --------------------------------------------------
#                 stage = (
#                     TreatmentStage.objects
#                     .filter(
#                         id=stage_id,
#                         user=request.user,
#                         is_active=True,
#                     )
#                     .prefetch_related(
#                         "equipments",
#                         "processes",
#                     )
#                     .first()
#                 )

#                 if not stage:
#                     return Response(
#                         {
#                             "success": False,
#                             "message": "Treatment stage not found.",
#                         },
#                         status=status.HTTP_404_NOT_FOUND,
#                     )

#                 # --------------------------------------------------
#                 # 2. Check whether this stage is already running
#                 # --------------------------------------------------
#                 running_batch = StageBatch.objects.filter(
#                     stage=stage,
#                     status="RUNNING",
#                 ).first()

#                 if running_batch:
#                     return Response(
#                         {
#                             "success": False,
#                             "message": (
#                                 "This treatment stage already has "
#                                 "a running batch."
#                             ),
#                             "batch_number": running_batch.batch_number,
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 # --------------------------------------------------
#                 # 3. Get active processes for this stage
#                 # --------------------------------------------------
#                 processes = list(
#                     stage.processes
#                     .filter(is_active=True)
#                     .order_by("sequence")
#                 )

#                 if not processes:
#                     return Response(
#                         {
#                             "success": False,
#                             "message": (
#                                 "No active processes are configured "
#                                 "for this treatment stage."
#                             ),
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 # --------------------------------------------------
#                 # 4. Create unique stage batch number
#                 # --------------------------------------------------
#                 last_batch = (
#                     StageBatch.objects
#                     .filter(batch_number__startswith="STAGE-")
#                     .order_by("-id")
#                     .first()
#                 )

#                 if last_batch:
#                     try:
#                         last_number = int(
#                             last_batch.batch_number.split("-")[-1]
#                         )
#                     except (ValueError, IndexError):
#                         last_number = 0
#                 else:
#                     last_number = 0

#                 batch_number = f"STAGE-{last_number + 1:06d}"

#                 # --------------------------------------------------
#                 # 5. Create StageBatch
#                 # --------------------------------------------------
#                 stage_batch = StageBatch.objects.create(
#                     batch_number=batch_number,
#                     stage=stage,
#                     status="PENDING",
#                 )

#                 # --------------------------------------------------
#                 # 6. Activate all equipment required by this stage
#                 #
#                 # ACTIVE = equipment is enabled/available
#                 # OFF    = equipment is not physically running
#                 #
#                 # We do NOT turn equipment ON here because MQTT /
#                 # hardware communication is not implemented yet.
#                 # --------------------------------------------------
#                 equipments = stage.equipments.filter(
#                     is_active=True
#                 )

#                 for equipment in equipments:

#                     equipment.status = "ACTIVE"
#                     equipment.current_state = "OFF"

#                     equipment.save(
#                         update_fields=[
#                             "status",
#                             "current_state",
#                             "updated_at",
#                         ]
#                     )

#                 # --------------------------------------------------
#                 # 7. Create process execution records
#                 # --------------------------------------------------
#                 process_executions = []

#                 for process in processes:

#                     execution = StageBatchProcessExecution.objects.create(
#                         stage_batch=stage_batch,
#                         process=process,
#                         status="PENDING",
#                     )

#                     process_executions.append(execution)

#                 # --------------------------------------------------
#                 # 8. Start the batch
#                 # --------------------------------------------------
#                 stage_batch.start_batch()

#                 # --------------------------------------------------
#                 # 9. Prepare response
#                 # --------------------------------------------------
#                 process_data = []

#                 for execution in process_executions:

#                     process_data.append(
#                         {
#                             "id": execution.id,
#                             "process_id": execution.process.id,
#                             "process_name": execution.process.name,
#                             "sequence": execution.process.sequence,
#                             "status": execution.status,
#                             "duration_seconds": (
#                                 execution.process.duration_seconds
#                             ),
#                         }
#                     )

#                 equipment_data = []

#                 for equipment in equipments:

#                     equipment_data.append(
#                         {
#                             "id": equipment.id,
#                             "name": equipment.name,
#                             "code": equipment.code,
#                             "status": equipment.status,
#                             "current_state": equipment.current_state,
#                         }
#                     )

#                 return Response(
#                     {
#                         "success": True,
#                         "message": (
#                             "Stage batch started successfully."
#                         ),
#                         "data": {
#                             "batch": {
#                                 "id": stage_batch.id,
#                                 "batch_number": stage_batch.batch_number,
#                                 "stage_id": stage.id,
#                                 "stage_name": stage.name,
#                                 "status": stage_batch.status,
#                                 "started_at": stage_batch.started_at,
#                             },
#                             "equipments": equipment_data,
#                             "processes": process_data,
#                         },
#                     },
#                     status=status.HTTP_201_CREATED,
#                 )

#         except Exception as e:

#             return Response(
#                 {
#                     "success": False,
#                     "message": "Failed to start stage batch.",
#                     "error": str(e),
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )





from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from treatment_process.models import (
    TreatmentStage,
    TreatmentProcess,
    StageBatch,
    StageBatchProcessExecution,
)
from equipment.models import Equipment


from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from treatment_process.models import (
    TreatmentStage,
    TreatmentProcess,
    StageBatch,
    StageBatchProcessExecution,
)
from equipment.models import Equipment
from treatment_process.services.stage_controller import (
    StageExecutionService,
)


from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from treatment_process.models import (
    TreatmentStage,
    TreatmentProcess,
    StageBatch,
    StageBatchProcessExecution,
)

from equipment.models import Equipment

from treatment_process.services.stage_controller import (
    StageExecutionService,
)


import threading

from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from treatment_process.models import (
    TreatmentStage,
    StageBatch,
    StageBatchProcessExecution,
)

from treatment_process.services.stage_execution_runner import (
    run_stage_batch,
)


# class StageBatchStartView(APIView):
#     """
#     Start automatic execution of a TreatmentStage.

#     Important:

#     The API does NOT execute the complete stage directly.

#     It creates the StageBatch and process execution records,
#     then starts the actual execution in a background thread.

#     Therefore the API returns immediately while the stage continues
#     running in the background.
#     """

#     permission_classes = [IsAuthenticated]

#     def post(self, request, stage_id):

#         try:

#             # =====================================================
#             # GET STAGE
#             # =====================================================

#             try:

#                 stage = (
#                     TreatmentStage.objects
#                     .prefetch_related(
#                         "equipments",
#                         "processes__equipments",
#                     )
#                     .get(
#                         id=stage_id,
#                         user=request.user,
#                     )
#                 )

#             except TreatmentStage.DoesNotExist:

#                 return Response(
#                     {
#                         "success": False,
#                         "message": "Treatment stage not found.",
#                     },
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             # =====================================================
#             # CHECK STAGE ACTIVE
#             # =====================================================

#             if not stage.is_active:

#                 return Response(
#                     {
#                         "success": False,
#                         "message": "Treatment stage is inactive.",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # =====================================================
#             # CHECK WHETHER THIS STAGE IS ALREADY RUNNING
#             # =====================================================

#             running_batch = (
#                 StageBatch.objects
#                 .filter(
#                     stage=stage,
#                     status="RUNNING",
#                 )
#                 .first()
#             )

#             if running_batch:

#                 return Response(
#                     {
#                         "success": False,
#                         "message": (
#                             "This treatment stage is already running."
#                         ),
#                         "batch_id": running_batch.id,
#                         "batch_number": running_batch.batch_number,
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # =====================================================
#             # GET STAGE EQUIPMENT
#             # =====================================================

#             stage_equipments = list(
#                 stage.equipments
#                 .filter(
#                     is_active=True,
#                 )
#                 .select_related(
#                     "equipment_type",
#                 )
#                 .all()
#             )

#             if not stage_equipments:

#                 return Response(
#                     {
#                         "success": False,
#                         "message": (
#                             "No active equipment is configured "
#                             "for this stage."
#                         ),
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # =====================================================
#             # VALIDATE STAGE EQUIPMENT
#             # =====================================================

#             for equipment in stage_equipments:

#                 if equipment.status == "MAINTENANCE":

#                     return Response(
#                         {
#                             "success": False,
#                             "message": (
#                                 f"Equipment '{equipment.name}' "
#                                 "is under maintenance."
#                             ),
#                             "equipment_id": equipment.id,
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 if equipment.status == "FAULT":

#                     return Response(
#                         {
#                             "success": False,
#                             "message": (
#                                 f"Equipment '{equipment.name}' "
#                                 "is in fault state."
#                             ),
#                             "equipment_id": equipment.id,
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#             # =====================================================
#             # GET ACTIVE PROCESSES
#             # =====================================================

#             processes = list(
#                 stage.processes
#                 .filter(
#                     is_active=True,
#                 )
#                 .prefetch_related(
#                     "equipments",
#                 )
#                 .order_by(
#                     "sequence",
#                 )
#             )

#             if not processes:

#                 return Response(
#                     {
#                         "success": False,
#                         "message": (
#                             "No active processes are configured "
#                             "for this stage."
#                         ),
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # =====================================================
#             # VALIDATE PROCESS EQUIPMENT
#             # =====================================================

#             for process in processes:

#                 process_equipments = list(
#                     process.equipments
#                     .filter(
#                         is_active=True,
#                     )
#                     .select_related(
#                         "equipment_type",
#                     )
#                     .all()
#                 )

#                 # -------------------------------------------------
#                 # Process must have equipment.
#                 # -------------------------------------------------

#                 if not process_equipments:

#                     return Response(
#                         {
#                             "success": False,
#                             "message": (
#                                 f"No active equipment configured "
#                                 f"for process '{process.name}'."
#                             ),
#                             "process_id": process.id,
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 # -------------------------------------------------
#                 # Validate equipment availability.
#                 #
#                 # NOTE:
#                 # We intentionally DO NOT check whether process
#                 # equipment belongs to stage.equipments.
#                 #
#                 # Process.equipments is the source for process
#                 # execution.
#                 # -------------------------------------------------

#                 for equipment in process_equipments:

#                     if equipment.status == "MAINTENANCE":

#                         return Response(
#                             {
#                                 "success": False,
#                                 "message": (
#                                     f"Equipment '{equipment.name}' "
#                                     "is under maintenance."
#                                 ),
#                                 "process_id": process.id,
#                                 "equipment_id": equipment.id,
#                             },
#                             status=status.HTTP_400_BAD_REQUEST,
#                         )

#                     if equipment.status == "FAULT":

#                         return Response(
#                             {
#                                 "success": False,
#                                 "message": (
#                                     f"Equipment '{equipment.name}' "
#                                     "is in fault state."
#                                 ),
#                                 "process_id": process.id,
#                                 "equipment_id": equipment.id,
#                             },
#                             status=status.HTTP_400_BAD_REQUEST,
#                         )

#             # =====================================================
#             # CREATE BATCH
#             # =====================================================

#             with transaction.atomic():

#                 # -------------------------------------------------
#                 # Generate batch number.
#                 # -------------------------------------------------

#                 last_batch = (
#                     StageBatch.objects
#                     .order_by("-id")
#                     .first()
#                 )

#                 if last_batch:

#                     try:

#                         last_number = int(
#                             last_batch.batch_number
#                             .split("-")[-1]
#                         )

#                     except (ValueError, AttributeError):

#                         last_number = 0

#                 else:

#                     last_number = 0

#                 batch_number = (
#                     f"STAGE-{stage.id}-"
#                     f"{last_number + 1:06d}"
#                 )

#                 # -------------------------------------------------
#                 # Create StageBatch.
#                 # -------------------------------------------------

#                 stage_batch = StageBatch.objects.create(
#                     batch_number=batch_number,
#                     stage=stage,
#                     status="PENDING",
#                 )

#                 # -------------------------------------------------
#                 # Create process execution records.
#                 # -------------------------------------------------

#                 process_executions = []

#                 for process in processes:

#                     process_execution = (
#                         StageBatchProcessExecution.objects.create(
#                             stage_batch=stage_batch,
#                             process=process,
#                             status="PENDING",
#                         )
#                     )

#                     process_executions.append(
#                         process_execution
#                     )

#                 # -------------------------------------------------
#                 # Activate stage equipment.
#                 #
#                 # IMPORTANT:
#                 #
#                 # status = ACTIVE
#                 # current_state = OFF
#                 #
#                 # The execution service will turn equipment ON/OFF
#                 # according to process configuration.
#                 # -------------------------------------------------

#                 for equipment in stage_equipments:

#                     equipment.status = "ACTIVE"
#                     equipment.current_state = "OFF"

#                     equipment.save(
#                         update_fields=[
#                             "status",
#                             "current_state",
#                             "updated_at",
#                         ]
#                     )

#                 # -------------------------------------------------
#                 # Start StageBatch.
#                 # -------------------------------------------------

#                 stage_batch.start_batch()

#                 # -------------------------------------------------
#                 # Start background execution ONLY AFTER the
#                 # database transaction successfully commits.
#                 #
#                 # This is important.
#                 #
#                 # If the transaction fails, we don't want the
#                 # background thread to start using incomplete data.
#                 # -------------------------------------------------

#                 # transaction.on_commit(
#                 #     lambda batch_id=stage_batch.id: (
#                 #         threading.Thread(
#                 #             target=run_stage_batch,
#                 #             args=(batch_id,),
#                 #             daemon=True,
#                 #         ).start()
#                 #     )
#                 # )

#             # =====================================================
#             # PREPARE IMMEDIATE RESPONSE
#             # =====================================================

#             equipment_data = []

#             for equipment in stage_equipments:

#                 equipment_data.append(
#                     {
#                         "id": equipment.id,
#                         "name": equipment.name,
#                         "code": equipment.code,
#                         "equipment_type": (
#                             equipment.equipment_type.name
#                         ),
#                         "status": equipment.status,
#                         "current_state": equipment.current_state,
#                         "start_time": equipment.start_time,
#                         "end_time": equipment.end_time,
#                         "duration_seconds": (
#                             equipment.duration_seconds
#                         ),
#                     }
#                 )

#             process_data = []

#             for process_execution in process_executions:

#                 process_data.append(
#                     {
#                         "id": process_execution.id,
#                         "process_id": (
#                             process_execution.process_id
#                         ),
#                         "process_name": (
#                             process_execution.process.name
#                         ),
#                         "sequence": (
#                             process_execution.process.sequence
#                         ),
#                         "status": process_execution.status,
#                     }
#                 )

#             # =====================================================
#             # RETURN IMMEDIATELY
#             # =====================================================

#             return Response(
#                 {
#                     "success": True,
#                     "message": (
#                         "Stage execution started successfully."
#                     ),
#                     "data": {
#                         "stage_id": stage.id,
#                         "stage_name": stage.name,
#                         "batch_id": stage_batch.id,
#                         "batch_number": (
#                             stage_batch.batch_number
#                         ),
#                         "status": stage_batch.status,
#                         "execution": "RUNNING_IN_BACKGROUND",
#                         "equipments": equipment_data,
#                         "processes": process_data,
#                     },
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as exc:

#             return Response(
#                 {
#                     "success": False,
#                     "message": (
#                         "Failed to start stage execution."
#                     ),
#                     "error": str(exc),
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )




from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from treatment_process.models import (
    TreatmentStage,
    StageBatch,
    StageBatchProcessExecution,
    StageEquipmentConfig,
)


class StageBatchStartView(APIView):
    """
    Start automatic execution of a TreatmentStage.

    Important:

    The API does not execute the complete stage directly.

    It creates the StageBatch and process execution records,
    activates the stage equipment configurations, and starts
    the StageBatch.

    The actual process execution is handled separately by
    the background worker.

    Runtime equipment fields are stored in
    StageEquipmentConfig instead of Equipment.

    Equipment:
        is_active
            -> physical equipment availability.

    StageEquipmentConfig:
        status
            -> stage runtime status
               ACTIVE / INACTIVE / MAINTENANCE / FAULT

        current_state
            -> OFF / ON

        start_time
            -> equipment ON start time

        end_time
            -> equipment OFF time

        duration_seconds
            -> configured equipment duration

    StageBatchProcessEquipmentExecution:
        scheduled_at
            -> worker scheduling time.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, stage_id):

        try:

            # =====================================================
            # GET STAGE
            # =====================================================

            try:

                stage = (
                    TreatmentStage.objects
                    .prefetch_related(
                        "equipments",
                        "processes__equipments",
                    )
                    .get(
                        id=stage_id,
                        user=request.user,
                    )
                )

            except TreatmentStage.DoesNotExist:

                return Response(
                    {
                        "success": False,
                        "message": "Treatment stage not found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # =====================================================
            # CHECK STAGE ACTIVE
            # =====================================================

            if not stage.is_active:

                return Response(
                    {
                        "success": False,
                        "message": "Treatment stage is inactive.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # =====================================================
            # CHECK WHETHER THIS STAGE IS ALREADY RUNNING
            # =====================================================

            running_batch = (
                StageBatch.objects
                .filter(
                    stage=stage,
                    status="RUNNING",
                )
                .first()
            )

            if running_batch:

                return Response(
                    {
                        "success": False,
                        "message": (
                            "This treatment stage is already running."
                        ),
                        "batch_id": running_batch.id,
                        "batch_number": running_batch.batch_number,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # =====================================================
            # GET STAGE EQUIPMENT
            # =====================================================
            #
            # IMPORTANT:
            #
            # We still use Equipment.is_active exactly as before.
            #
            # We do NOT use config.status to decide whether the
            # equipment is active.
            #
            # config.status is checked only for MAINTENANCE / FAULT,
            # just like the old Equipment.status logic.
            #
            # INACTIVE is allowed because START will change it to
            # ACTIVE.
            # =====================================================

            stage_equipments = list(
                stage.equipments
                .filter(
                    is_active=True,
                )
                .select_related(
                    "equipment_type",
                )
                .all()
            )

            if not stage_equipments:

                return Response(
                    {
                        "success": False,
                        "message": (
                            "No active equipment is configured "
                            "for this stage."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # =====================================================
            # GET STAGE EQUIPMENT CONFIGURATIONS
            # =====================================================

            stage_configs = {
                config.equipment_id: config
                for config in StageEquipmentConfig.objects.filter(
                    stage=stage,
                    equipment_id__in=[
                        equipment.id
                        for equipment in stage_equipments
                    ],
                )
            }

            # =====================================================
            # VALIDATE STAGE EQUIPMENT CONFIGURATION
            # =====================================================

            for equipment in stage_equipments:

                config = stage_configs.get(
                    equipment.id
                )

                # -------------------------------------------------
                # Every stage equipment must have a configuration.
                # -------------------------------------------------

                if not config:

                    return Response(
                        {
                            "success": False,
                            "message": (
                                f"No automatic configuration found "
                                f"for equipment '{equipment.name}'."
                            ),
                            "equipment_id": equipment.id,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # -------------------------------------------------
                # Keep the OLD business logic:
                #
                # MAINTENANCE -> cannot start
                # FAULT        -> cannot start
                #
                # INACTIVE is NOT an error.
                #
                # It will become ACTIVE when the stage starts.
                # -------------------------------------------------

                if config.status == "MAINTENANCE":

                    return Response(
                        {
                            "success": False,
                            "message": (
                                f"Equipment '{equipment.name}' "
                                "is under maintenance."
                            ),
                            "equipment_id": equipment.id,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if config.status == "FAULT":

                    return Response(
                        {
                            "success": False,
                            "message": (
                                f"Equipment '{equipment.name}' "
                                "is in fault state."
                            ),
                            "equipment_id": equipment.id,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # =====================================================
            # GET ACTIVE PROCESSES
            # =====================================================

            processes = list(
                stage.processes
                .filter(
                    is_active=True,
                )
                .prefetch_related(
                    "equipments",
                )
                .order_by(
                    "sequence",
                )
            )

            if not processes:

                return Response(
                    {
                        "success": False,
                        "message": (
                            "No active processes are configured "
                            "for this stage."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # =====================================================
            # VALIDATE PROCESS EQUIPMENT
            # =====================================================
            #
            # IMPORTANT:
            #
            # Process.equipments remains the source of equipment
            # for that process.
            #
            # We DO NOT check whether process equipment belongs
            # to stage.equipments.
            #
            # This preserves the old API logic.
            # =====================================================

            for process in processes:

                process_equipments = list(
                    process.equipments
                    .filter(
                        is_active=True,
                    )
                    .select_related(
                        "equipment_type",
                    )
                    .all()
                )

                # -------------------------------------------------
                # Process must have equipment.
                # -------------------------------------------------

                if not process_equipments:

                    return Response(
                        {
                            "success": False,
                            "message": (
                                f"No active equipment configured "
                                f"for process '{process.name}'."
                            ),
                            "process_id": process.id,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # -------------------------------------------------
                # Validate process equipment availability.
                #
                # Same old business rule:
                #
                # MAINTENANCE -> reject
                # FAULT        -> reject
                #
                # INACTIVE is allowed.
                #
                # The process equipment itself remains independent
                # from stage.equipments.
                # -------------------------------------------------

                for equipment in process_equipments:

                    config = (
                        StageEquipmentConfig.objects
                        .filter(
                            stage=stage,
                            equipment=equipment,
                        )
                        .first()
                    )

                    # -------------------------------------------------
                    # If this process equipment has no configuration
                    # for the stage, automatic execution cannot know
                    # its runtime configuration.
                    # -------------------------------------------------

                    if not config:

                        return Response(
                            {
                                "success": False,
                                "message": (
                                    f"No automatic configuration "
                                    f"found for equipment "
                                    f"'{equipment.name}' in stage "
                                    f"'{stage.name}'."
                                ),
                                "process_id": process.id,
                                "equipment_id": equipment.id,
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    if config.status == "MAINTENANCE":

                        return Response(
                            {
                                "success": False,
                                "message": (
                                    f"Equipment '{equipment.name}' "
                                    "is under maintenance."
                                ),
                                "process_id": process.id,
                                "equipment_id": equipment.id,
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    if config.status == "FAULT":

                        return Response(
                            {
                                "success": False,
                                "message": (
                                    f"Equipment '{equipment.name}' "
                                    "is in fault state."
                                ),
                                "process_id": process.id,
                                "equipment_id": equipment.id,
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

            # =====================================================
            # CREATE BATCH
            # =====================================================

            with transaction.atomic():

                # -------------------------------------------------
                # Generate batch number.
                #
                # Keep the old batch-number generation logic.
                # -------------------------------------------------

                last_batch = (
                    StageBatch.objects
                    .order_by("-id")
                    .first()
                )

                if last_batch:

                    try:

                        last_number = int(
                            last_batch.batch_number
                            .split("-")[-1]
                        )

                    except (ValueError, AttributeError):

                        last_number = 0

                else:

                    last_number = 0

                batch_number = (
                    f"STAGE-{stage.id}-"
                    f"{last_number + 1:06d}"
                )

                # -------------------------------------------------
                # Create StageBatch.
                # -------------------------------------------------

                stage_batch = StageBatch.objects.create(
                    batch_number=batch_number,
                    stage=stage,
                    status="PENDING",
                )

                # -------------------------------------------------
                # Create process execution records.
                # -------------------------------------------------

                process_executions = []

                for process in processes:

                    process_execution = (
                        StageBatchProcessExecution.objects.create(
                            stage_batch=stage_batch,
                            process=process,
                            status="PENDING",
                        )
                    )

                    process_executions.append(
                        process_execution
                    )

                # =================================================
                # ACTIVATE STAGE EQUIPMENT
                # =================================================
                #
                # THIS IS THE IMPORTANT OLD BUSINESS LOGIC.
                #
                # Old:
                #
                #     equipment.status = "ACTIVE"
                #     equipment.current_state = "OFF"
                #
                # New:
                #
                #     config.status = "ACTIVE"
                #     config.current_state = "OFF"
                #
                # start_time/end_time are NOT reset here because
                # they represent runtime timing.
                # turn_equipment_on() will set start_time when the
                # equipment actually turns ON.
                # =================================================

                for equipment in stage_equipments:

                    config = stage_configs[
                        equipment.id
                    ]

                    config.status = "ACTIVE"
                    config.current_state = "OFF"

                    config.save(
                        update_fields=[
                            "status",
                            "current_state",
                            "updated_at",
                        ]
                    )

                # -------------------------------------------------
                # Start StageBatch.
                # -------------------------------------------------

                stage_batch.start_batch()

                # -------------------------------------------------
                # The actual execution is handled by the worker.
                #
                # We intentionally do not start a background thread
                # from the HTTP request.
                # -------------------------------------------------

            # =====================================================
            # PREPARE IMMEDIATE RESPONSE
            # =====================================================

            equipment_data = []

            for equipment in stage_equipments:

                config = stage_configs[
                    equipment.id
                ]

                equipment_data.append(
                    {
                        "id": equipment.id,
                        "name": equipment.name,
                        "code": equipment.code,

                        "equipment_type": (
                            equipment.equipment_type.name
                        ),

                        # Physical equipment availability.
                        "is_active": equipment.is_active,

                        # Stage runtime status.
                        "status": config.status,

                        # Current automatic state.
                        "current_state": (
                            config.current_state
                        ),

                        # Runtime start/end times.
                        "start_time": config.start_time,
                        "end_time": config.end_time,

                        # Configured duration.
                        "duration_seconds": (
                            config.duration_seconds
                        ),
                    }
                )

            # =====================================================
            # PROCESS RESPONSE
            # =====================================================

            process_data = []

            for process_execution in process_executions:

                process_data.append(
                    {
                        "id": process_execution.id,
                        "process_id": (
                            process_execution.process_id
                        ),
                        "process_name": (
                            process_execution.process.name
                        ),
                        "sequence": (
                            process_execution.process.sequence
                        ),
                        "status": process_execution.status,
                    }
                )

            # =====================================================
            # RETURN IMMEDIATELY
            # =====================================================

            return Response(
                {
                    "success": True,
                    "message": (
                        "Stage execution started successfully."
                    ),
                    "data": {
                        "stage_id": stage.id,
                        "stage_name": stage.name,

                        "batch_id": stage_batch.id,
                        "batch_number": (
                            stage_batch.batch_number
                        ),

                        "status": stage_batch.status,

                        "execution": "RUNNING_IN_BACKGROUND",

                        "equipments": equipment_data,

                        "processes": process_data,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:

            return Response(
                {
                    "success": False,
                    "message": (
                        "Failed to start stage execution."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



# from django.db import transaction
# from django.utils import timezone

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated

# from treatment_process.models import (
#     TreatmentStage,
#     StageBatch,
#     StageBatchProcessExecution,
#     StageBatchProcessEquipmentExecution,
# )

# from treatment_process.services.stage_controller import (
#     StageExecutionService,
# )




# class StageBatchStopView(APIView):
#     """
#     Stop automatic execution of a treatment stage.

#     STOP flow:

#         1. Find the running StageBatch.
#         2. Stop all PENDING/RUNNING process executions.
#         3. Stop all WAITING/RUNNING equipment executions.
#         4. Turn OFF every stage equipment that is currently ON.
#         5. Deactivate every stage equipment.
#         6. Mark StageBatch as STOPPED.

#     Important:
#         STOP does not wait for equipment duration.

#         If a motor is currently ON and has 30 seconds
#         remaining, STOP turns it OFF immediately.
#     """

#     permission_classes = [IsAuthenticated]

#     def post(self, request, stage_id):

#         try:

#             # =========================================================
#             # 1. GET STAGE
#             # =========================================================

#             stage = (
#                 TreatmentStage.objects
#                 .filter(
#                     id=stage_id,
#                     user=request.user,
#                     is_active=True,
#                 )
#                 .prefetch_related("equipments")
#                 .first()
#             )

#             if not stage:

#                 return Response(
#                     {
#                         "success": False,
#                         "message": "Treatment stage not found.",
#                     },
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             # =========================================================
#             # 2. GET RUNNING STAGE BATCH
#             # =========================================================

#             stage_batch = (
#                 StageBatch.objects
#                 .filter(
#                     stage=stage,
#                     status="RUNNING",
#                 )
#                 .first()
#             )

#             if not stage_batch:

#                 return Response(
#                     {
#                         "success": False,
#                         "message": (
#                             "No running batch found "
#                             "for this treatment stage."
#                         ),
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # =========================================================
#             # 3. LOCK BATCH
#             # =========================================================

#             with transaction.atomic():

#                 stage_batch = (
#                     StageBatch.objects
#                     .select_for_update()
#                     .get(
#                         id=stage_batch.id,
#                     )
#                 )

#                 # -----------------------------------------------------
#                 # Check again after acquiring the lock.
#                 # -----------------------------------------------------

#                 if stage_batch.status != "RUNNING":

#                     return Response(
#                         {
#                             "success": False,
#                             "message": (
#                                 "Stage is no longer running."
#                             ),
#                             "status": stage_batch.status,
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 # =====================================================
#                 # 4. STOP PROCESS EXECUTIONS
#                 # =====================================================
#                 #
#                 # PENDING processes must NEVER execute after STOP.
#                 #
#                 # RUNNING processes are stopped.
#                 #
#                 # COMPLETED processes remain COMPLETED.
#                 # FAILED processes remain FAILED.
#                 # STOPPED processes remain STOPPED.
#                 # =====================================================

#                 process_executions = (
#                     StageBatchProcessExecution.objects
#                     .filter(
#                         stage_batch=stage_batch,
#                         status__in=[
#                             "PENDING",
#                             "STARTED",
#                             "RUNNING",
#                         ],
#                     )
#                 )

#                 process_count = process_executions.count()

#                 for process_execution in process_executions:

#                     process_execution.status = "STOPPED"
#                     process_execution.completed_at = timezone.now()

#                     if process_execution.started_at:

#                         process_execution.actual_duration_seconds = int(
#                             (
#                                 process_execution.completed_at
#                                 - process_execution.started_at
#                             ).total_seconds()
#                         )

#                     process_execution.save(
#                         update_fields=[
#                             "status",
#                             "completed_at",
#                             "actual_duration_seconds",
#                             "updated_at",
#                         ]
#                     )

#                 # =====================================================
#                 # 5. STOP EQUIPMENT EXECUTIONS
#                 # =====================================================
#                 #
#                 # This includes:
#                 #
#                 # PENDING
#                 # RUNNING
#                 # WAITING
#                 #
#                 # The WAITING execution is especially important.
#                 #
#                 # Example:
#                 #
#                 # Pump Motor
#                 #     ON
#                 #     ↓
#                 # WAITING until 08:35:06
#                 #
#                 # User presses STOP at 08:34:30
#                 #
#                 # The waiting execution must NOT resume at 08:35:06.
#                 # =====================================================

#                 equipment_executions = (
#                     StageBatchProcessEquipmentExecution.objects
#                     .filter(
#                         stage_batch_process_execution__stage_batch=(
#                             stage_batch
#                         ),
#                         status__in=[
#                             "PENDING",
#                             "STARTED",
#                             "RUNNING",
#                             "WAITING",
#                         ],
#                     )
#                 )

#                 equipment_execution_count = (
#                     equipment_executions.count()
#                 )

#                 for equipment_execution in equipment_executions:

#                     equipment_execution.status = "STOPPED"
#                     equipment_execution.completed_at = timezone.now()

#                     if equipment_execution.started_at:

#                         equipment_execution.duration_seconds = int(
#                             (
#                                 equipment_execution.completed_at
#                                 - equipment_execution.started_at
#                             ).total_seconds()
#                         )

#                     equipment_execution.save(
#                         update_fields=[
#                             "status",
#                             "completed_at",
#                             "duration_seconds",
#                             "updated_at",
#                         ]
#                     )

#                 # =====================================================
#                 # 6. STOP THE STAGE BATCH
#                 # =====================================================
#                 #
#                 # This is done BEFORE returning to the worker.
#                 #
#                 # The worker checks:
#                 #
#                 #     status == RUNNING
#                 #
#                 # Therefore STOPPED means the worker will not continue
#                 # this stage.
#                 # =====================================================

#                 stage_batch.stop_batch()

#             # =========================================================
#             # 7. TURN OFF ALL CURRENTLY ON EQUIPMENT
#             # =========================================================
#             #
#             # IMPORTANT:
#             #
#             # We do NOT use the normal duration logic here.
#             #
#             # STOP means immediate shutdown.
#             #
#             # Example:
#             #
#             # Pump Motor
#             #     ON
#             #     remaining duration = 20 seconds
#             #
#             # STOP
#             #     ↓
#             # Pump Motor OFF immediately
#             # =========================================================

#             stage_equipments = list(
#                 stage.equipments
#                 .filter(
#                     is_active=True,
#                 )
#                 .all()
#             )

#             service = StageExecutionService(stage_batch)

#             turned_off_equipment = []

#             for equipment in stage_equipments:

#                 # -----------------------------------------------------
#                 # Only turn OFF equipment that is actually ON.
#                 # -----------------------------------------------------

#                 if equipment.current_state == "ON":

#                     service.turn_equipment_off(
#                         equipment
#                     )

#                     turned_off_equipment.append(
#                         {
#                             "id": equipment.id,
#                             "name": equipment.name,
#                             "code": equipment.code,
#                         }
#                     )

#             # =========================================================
#             # 8. DEACTIVATE ALL STAGE EQUIPMENT
#             # =========================================================
#             #
#             # After everything is OFF:
#             #
#             #     current_state = OFF
#             #     status         = INACTIVE
#             #
#             # Your existing service already performs this final state.
#             # =========================================================

#             service.deactivate_stage_equipment()

#             # =========================================================
#             # 9. RESPONSE
#             # =========================================================

#             return Response(
#                 {
#                     "success": True,
#                     "message": (
#                         "Treatment stage stopped successfully."
#                     ),
#                     "data": {
#                         "batch_id": stage_batch.id,
#                         "batch_number": stage_batch.batch_number,
#                         "stage_id": stage.id,
#                         "stage_name": stage.name,
#                         "status": stage_batch.status,
#                         "started_at": stage_batch.started_at,
#                         "completed_at": stage_batch.completed_at,
#                         "stopped_processes": process_count,
#                         "stopped_equipment_executions": (
#                             equipment_execution_count
#                         ),
#                         "turned_off_equipment": (
#                             turned_off_equipment
#                         ),
#                     },
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as exc:

#             return Response(
#                 {
#                     "success": False,
#                     "message": (
#                         "Failed to stop treatment stage."
#                     ),
#                     "error": str(exc),
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )



# from django.db import transaction
# from django.utils import timezone

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated

# from treatment_process.models import (
#     TreatmentStage,
#     StageBatch,
#     StageBatchProcessExecution,
#     StageBatchProcessEquipmentExecution,
#     StageEquipmentConfig,
# )

# from treatment_process.services.stage_controller import (
#     StageExecutionService,
# )


# class StageBatchStopView(APIView):
#     """
#     Stop automatic execution of a treatment stage.

#     STOP flow:

#         1. Find the running StageBatch.
#         2. Stop all PENDING/RUNNING process executions.
#         3. Stop all WAITING/RUNNING equipment executions.
#         4. Turn OFF every stage equipment that is currently ON.
#         5. Deactivate every stage equipment.
#         6. Mark StageBatch as STOPPED.

#     Important:
#         STOP does not wait for equipment duration.

#         If a motor is currently ON and has 30 seconds
#         remaining, STOP turns it OFF immediately.
#     """

#     permission_classes = [IsAuthenticated]

#     def post(self, request, stage_id):

#         try:

#             # =========================================================
#             # 1. GET STAGE
#             # =========================================================

#             stage = (
#                 TreatmentStage.objects
#                 .filter(
#                     id=stage_id,
#                     user=request.user,
#                     is_active=True,
#                 )
#                 .prefetch_related("equipments")
#                 .first()
#             )

#             if not stage:

#                 return Response(
#                     {
#                         "success": False,
#                         "message": "Treatment stage not found.",
#                     },
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             # =========================================================
#             # 2. GET RUNNING STAGE BATCH
#             # =========================================================

#             stage_batch = (
#                 StageBatch.objects
#                 .filter(
#                     stage=stage,
#                     status="RUNNING",
#                 )
#                 .first()
#             )

#             if not stage_batch:

#                 return Response(
#                     {
#                         "success": False,
#                         "message": (
#                             "No running batch found "
#                             "for this treatment stage."
#                         ),
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # =========================================================
#             # 3. LOCK BATCH
#             # =========================================================

#             with transaction.atomic():

#                 stage_batch = (
#                     StageBatch.objects
#                     .select_for_update()
#                     .get(
#                         id=stage_batch.id,
#                     )
#                 )

#                 # -----------------------------------------------------
#                 # Check again after acquiring the lock.
#                 # -----------------------------------------------------

#                 if stage_batch.status != "RUNNING":

#                     return Response(
#                         {
#                             "success": False,
#                             "message": (
#                                 "Stage is no longer running."
#                             ),
#                             "status": stage_batch.status,
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 # =====================================================
#                 # 4. STOP PROCESS EXECUTIONS
#                 # =====================================================
#                 #
#                 # PENDING processes must NEVER execute after STOP.
#                 #
#                 # RUNNING processes are stopped.
#                 #
#                 # COMPLETED processes remain COMPLETED.
#                 # FAILED processes remain FAILED.
#                 # STOPPED processes remain STOPPED.
#                 # =====================================================

#                 process_executions = (
#                     StageBatchProcessExecution.objects
#                     .filter(
#                         stage_batch=stage_batch,
#                         status__in=[
#                             "PENDING",
#                             "STARTED",
#                             "RUNNING",
#                         ],
#                     )
#                 )

#                 process_count = process_executions.count()

#                 for process_execution in process_executions:

#                     process_execution.status = "STOPPED"
#                     process_execution.completed_at = timezone.now()

#                     if process_execution.started_at:

#                         process_execution.actual_duration_seconds = int(
#                             (
#                                 process_execution.completed_at
#                                 - process_execution.started_at
#                             ).total_seconds()
#                         )

#                     process_execution.save(
#                         update_fields=[
#                             "status",
#                             "completed_at",
#                             "actual_duration_seconds",
#                             "updated_at",
#                         ]
#                     )

#                 # =====================================================
#                 # 5. STOP EQUIPMENT EXECUTIONS
#                 # =====================================================
#                 #
#                 # This includes:
#                 #
#                 # PENDING
#                 # STARTED
#                 # RUNNING
#                 # WAITING
#                 #
#                 # The WAITING execution is especially important.
#                 #
#                 # Example:
#                 #
#                 # Pump Motor
#                 #     ON
#                 #     ↓
#                 # WAITING until 08:35:06
#                 #
#                 # User presses STOP at 08:34:30
#                 #
#                 # The waiting execution must NOT resume at 08:35:06.
#                 # =====================================================

#                 equipment_executions = (
#                     StageBatchProcessEquipmentExecution.objects
#                     .filter(
#                         stage_batch_process_execution__stage_batch=(
#                             stage_batch
#                         ),
#                         status__in=[
#                             "PENDING",
#                             "STARTED",
#                             "RUNNING",
#                             "WAITING",
#                         ],
#                     )
#                 )

#                 equipment_execution_count = (
#                     equipment_executions.count()
#                 )

#                 for equipment_execution in equipment_executions:

#                     equipment_execution.status = "STOPPED"
#                     equipment_execution.completed_at = timezone.now()

#                     if equipment_execution.started_at:

#                         equipment_execution.duration_seconds = int(
#                             (
#                                 equipment_execution.completed_at
#                                 - equipment_execution.started_at
#                             ).total_seconds()
#                         )

#                     equipment_execution.save(
#                         update_fields=[
#                             "status",
#                             "completed_at",
#                             "duration_seconds",
#                             "updated_at",
#                         ]
#                     )

#                 # =====================================================
#                 # 6. STOP THE STAGE BATCH
#                 # =====================================================
#                 #
#                 # This is done BEFORE returning to the worker.
#                 #
#                 # The worker checks:
#                 #
#                 #     status == RUNNING
#                 #
#                 # Therefore STOPPED means the worker will not continue
#                 # this stage.
#                 # =====================================================

#                 stage_batch.stop_batch()

#             # =========================================================
#             # 7. TURN OFF ALL CURRENTLY ON EQUIPMENT
#             # =========================================================
#             #
#             # IMPORTANT:
#             #
#             # We do NOT use the normal duration logic here.
#             #
#             # STOP means immediate shutdown.
#             #
#             # Example:
#             #
#             # Pump Motor
#             #     ON
#             #     remaining duration = 20 seconds
#             #
#             # STOP
#             #     ↓
#             # Pump Motor OFF immediately
#             # =========================================================

#             stage_equipments = list(
#                 stage.equipments
#                 .all()
#             )

#             service = StageExecutionService(stage_batch)

#             turned_off_equipment = []

#             for equipment in stage_equipments:

#                 # -----------------------------------------------------
#                 # Get stage-specific equipment configuration.
#                 # -----------------------------------------------------

#                 config = (
#                     StageEquipmentConfig.objects
#                     .filter(
#                         stage=stage,
#                         equipment=equipment,
#                     )
#                     .first()
#                 )

#                 if not config:
#                     continue

#                 # -----------------------------------------------------
#                 # Only turn OFF equipment that is currently ON.
#                 #
#                 # current_state belongs to StageEquipmentConfig.
#                 # -----------------------------------------------------

#                 if config.current_state == "ON":

#                     service.force_turn_equipment_off(
#                         equipment,
#                         config,
#                     )

#                     turned_off_equipment.append(
#                         {
#                             "id": equipment.id,
#                             "name": equipment.name,
#                             "code": equipment.code,
#                         }
#                     )

#             # =========================================================
#             # 8. DEACTIVATE ALL STAGE EQUIPMENT
#             # =========================================================
#             #
#             # After everything is OFF:
#             #
#             #     current_state = OFF
#             #
#             # The existing service performs the final state.
#             # =========================================================

#             service.deactivate_stage_equipment()

#             # =========================================================
#             # 9. RESPONSE
#             # =========================================================

#             return Response(
#                 {
#                     "success": True,
#                     "message": (
#                         "Treatment stage stopped successfully."
#                     ),
#                     "data": {
#                         "batch_id": stage_batch.id,
#                         "batch_number": stage_batch.batch_number,
#                         "stage_id": stage.id,
#                         "stage_name": stage.name,
#                         "status": stage_batch.status,
#                         "started_at": stage_batch.started_at,
#                         "completed_at": stage_batch.completed_at,
#                         "stopped_processes": process_count,
#                         "stopped_equipment_executions": (
#                             equipment_execution_count
#                         ),
#                         "turned_off_equipment": (
#                             turned_off_equipment
#                         ),
#                     },
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as exc:

#             return Response(
#                 {
#                     "success": False,
#                     "message": (
#                         "Failed to stop treatment stage."
#                     ),
#                     "error": str(exc),
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )




from django.db import transaction
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from treatment_process.models import (
    TreatmentStage,
    StageBatch,
    StageBatchProcessExecution,
    StageBatchProcessEquipmentExecution,
    StageEquipmentConfig,
)

from treatment_process.services.stage_controller import (
    StageExecutionService,
)




from django.db import transaction
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from treatment_process.models import (
    TreatmentStage,
    StageBatch,
    StageBatchProcessExecution,
    StageBatchProcessEquipmentExecution,
    StageEquipmentConfig,
)


class StageBatchStopView(APIView):
    """
    Stop automatic execution of a treatment stage.

    STOP flow:

        1. Find the treatment stage.
        2. Find its currently RUNNING StageBatch.
        3. Lock the StageBatch.
        4. Stop PENDING / STARTED / RUNNING processes.
        5. Stop PENDING / STARTED / RUNNING / WAITING
           equipment executions.
        6. Immediately turn OFF every currently ON
           StageEquipmentConfig.
        7. Set StageEquipmentConfig status to INACTIVE.
        8. Mark the StageBatch as STOPPED.

    IMPORTANT:

        STOP does NOT wait for equipment duration.

        Example:

            Pump:
                current_state = ON
                duration_seconds = 30
                remaining duration = 20 seconds

            User presses STOP.

            Result:

                Pump -> OFF immediately

        The normal duration logic is completely bypassed.

    IMPORTANT:

        Runtime equipment fields now belong to
        StageEquipmentConfig.

        Therefore STOP uses:

            config.current_state
            config.end_time
            config.status

        It does NOT use:

            equipment.current_state
            equipment.start_time
            equipment.end_time
            equipment.duration_seconds
            equipment.status

        Equipment.is_active is also NOT used to decide
        whether an already-running equipment should be
        turned OFF.

        STOP is a safety operation, so every relevant
        configuration must be forced OFF.
    """

    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        stage_id,
    ):

        try:

            # =========================================================
            # 1. GET TREATMENT STAGE
            # =========================================================

            stage = (
                TreatmentStage.objects
                .filter(
                    id=stage_id,
                    user=request.user,
                    is_active=True,
                )
                .first()
            )

            if not stage:

                return Response(
                    {
                        "success": False,
                        "message": (
                            "Treatment stage not found."
                        ),
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # =========================================================
            # 2. GET CURRENTLY RUNNING STAGE BATCH
            # =========================================================

            stage_batch = (
                StageBatch.objects
                .filter(
                    stage=stage,
                    status="RUNNING",
                )
                .first()
            )

            if not stage_batch:

                return Response(
                    {
                        "success": False,
                        "message": (
                            "No running batch found "
                            "for this treatment stage."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # =========================================================
            # 3. LOCK THE STAGE BATCH
            # =========================================================
            #
            # This prevents two STOP requests from trying to
            # stop the same batch at the same time.
            #
            # It also prevents a race with the worker.
            # =========================================================

            with transaction.atomic():

                stage_batch = (
                    StageBatch.objects
                    .select_for_update()
                    .select_related(
                        "stage",
                    )
                    .get(
                        id=stage_batch.id,
                    )
                )

                # -----------------------------------------------------
                # Check again after acquiring the lock.
                # -----------------------------------------------------

                if stage_batch.status != "RUNNING":

                    return Response(
                        {
                            "success": False,
                            "message": (
                                "Stage is no longer running."
                            ),
                            "status": stage_batch.status,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # =====================================================
                # 4. STOP PROCESS EXECUTIONS
                # =====================================================
                #
                # These processes have not completed yet.
                #
                # PENDING
                # STARTED
                # RUNNING
                #
                # They must not continue after STOP.
                #
                # COMPLETED / FAILED / STOPPED records are left
                # unchanged.
                # =====================================================

                process_executions = (
                    StageBatchProcessExecution.objects
                    .filter(
                        stage_batch=stage_batch,
                        status__in=[
                            "PENDING",
                            "STARTED",
                            "RUNNING",
                        ],
                    )
                )

                process_count = (
                    process_executions.count()
                )

                stopped_at = timezone.now()

                for process_execution in process_executions:

                    process_execution.status = "STOPPED"

                    process_execution.completed_at = (
                        stopped_at
                    )

                    # -------------------------------------------------
                    # Calculate actual process duration only when
                    # the process had actually started.
                    # -------------------------------------------------

                    if process_execution.started_at:

                        process_execution.actual_duration_seconds = int(
                            (
                                process_execution.completed_at
                                - process_execution.started_at
                            ).total_seconds()
                        )

                    process_execution.save(
                        update_fields=[
                            "status",
                            "completed_at",
                            "actual_duration_seconds",
                            "updated_at",
                        ]
                    )

                # =====================================================
                # 5. STOP EQUIPMENT EXECUTIONS
                # =====================================================
                #
                # This includes WAITING executions.
                #
                # This is especially important for timed equipment.
                #
                # Example:
                #
                #     Pump
                #         ON
                #         ↓
                #         WAITING
                #         ↓
                #         scheduled_at = 10:30:00
                #
                #     User presses STOP at 10:29:40
                #
                # The WAITING record is changed to STOPPED.
                #
                # Therefore the worker will NOT resume it later.
                # =====================================================

                equipment_executions = (
                    StageBatchProcessEquipmentExecution.objects
                    .filter(
                        stage_batch_process_execution__stage_batch=(
                            stage_batch
                        ),
                        status__in=[
                            "PENDING",
                            "STARTED",
                            "RUNNING",
                            "WAITING",
                        ],
                    )
                )

                equipment_execution_count = (
                    equipment_executions.count()
                )

                for equipment_execution in equipment_executions:

                    equipment_execution.status = "STOPPED"

                    equipment_execution.completed_at = (
                        stopped_at
                    )

                    # -------------------------------------------------
                    # DO NOT use:
                    #
                    #     equipment_execution.duration_seconds
                    #
                    # because that is not the runtime duration field
                    # on this execution model.
                    #
                    # We only need to mark the execution STOPPED.
                    # -------------------------------------------------

                    equipment_execution.save(
                        update_fields=[
                            "status",
                            "completed_at",
                            "updated_at",
                        ]
                    )

                # =====================================================
                # 6. STOP THE STAGE BATCH
                # =====================================================
                #
                # Set this before leaving the transaction.
                #
                # The worker only processes StageBatch objects
                # whose status is RUNNING.
                #
                # Therefore after this becomes STOPPED, the worker
                # cannot continue the stage.
                # =====================================================

                stage_batch.stop_batch()

                # =====================================================
                # 7. FORCE ALL STAGE EQUIPMENT OFF
                # =====================================================
                #
                # IMPORTANT:
                #
                # This is NOT normal duration processing.
                #
                # STOP means:
                #
                #     ON  -> OFF immediately
                #
                # even if duration has not completed.
                #
                # We use StageEquipmentConfig because all runtime
                # fields were moved there.
                # =====================================================

                stage_configs = (
                    StageEquipmentConfig.objects
                    .filter(
                        stage=stage,
                    )
                    .select_related(
                        "equipment",
                    )
                )

                turned_off_equipment = []

                for config in stage_configs:

                    equipment = config.equipment

                    # -------------------------------------------------
                    # Only record equipment as "turned off" if it
                    # was actually ON.
                    # -------------------------------------------------

                    was_on = (
                        config.current_state == "ON"
                    )

                    # -------------------------------------------------
                    # Force runtime state OFF.
                    #
                    # We do NOT check duration_seconds here.
                    # -------------------------------------------------

                    config.current_state = "OFF"

                    # -------------------------------------------------
                    # Record the actual STOP/OFF time.
                    # -------------------------------------------------

                    config.end_time = stopped_at.time()

                    # -------------------------------------------------
                    # The stage is no longer running.
                    #
                    # Therefore the stage-specific configuration
                    # becomes INACTIVE.
                    # -------------------------------------------------

                    config.status = "INACTIVE"

                    config.save(
                        update_fields=[
                            "current_state",
                            "end_time",
                            "status",
                            "updated_at",
                        ]
                    )

                    # -------------------------------------------------
                    # Add only equipment that was actually ON.
                    # -------------------------------------------------

                    if was_on:

                        turned_off_equipment.append(
                            {
                                "id": equipment.id,
                                "name": equipment.name,
                                "code": equipment.code,
                            }
                        )

            # =========================================================
            # 8. RESPONSE
            # =========================================================

            return Response(
                {
                    "success": True,
                    "message": (
                        "Treatment stage stopped successfully."
                    ),
                    "data": {
                        "batch_id": stage_batch.id,
                        "batch_number": stage_batch.batch_number,
                        "stage_id": stage.id,
                        "stage_name": stage.name,
                        "status": stage_batch.status,
                        "started_at": stage_batch.started_at,
                        "completed_at": stage_batch.completed_at,
                        "stopped_processes": process_count,
                        "stopped_equipment_executions": (
                            equipment_execution_count
                        ),
                        "turned_off_equipment": (
                            turned_off_equipment
                        ),
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:

            return Response(
                {
                    "success": False,
                    "message": (
                        "Failed to stop treatment stage."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# from treatment_process.models import (
#     TreatmentStage,
#     StageBatch,
#     StageBatchProcessExecution,
# )


# class StageBatchStatusView(APIView):
#     """
#     Get the current execution status of a TreatmentStage.

#     This API returns:

#     1. StageBatch information.
#     2. Current/global equipment state.
#     3. Process execution status.
#     4. Equipment state for each individual process execution.

#     Important distinction:

#         Equipment.current_state
#             -> Current/global state of the equipment.

#         StageBatchProcessEquipmentExecution.state
#             -> State produced by that particular process.
#     """

#     permission_classes = [IsAuthenticated]

#     def get(self, request, stage_id):

#         try:

#             # =====================================================
#             # GET STAGE
#             # =====================================================

#             try:

#                 stage = (
#                     TreatmentStage.objects
#                     .get(
#                         id=stage_id,
#                         user=request.user,
#                     )
#                 )

#             except TreatmentStage.DoesNotExist:

#                 return Response(
#                     {
#                         "success": False,
#                         "message": "Treatment stage not found.",
#                     },
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             # =====================================================
#             # GET LATEST RUNNING BATCH
#             # =====================================================

#             running_batch = (
#                 StageBatch.objects
#                 .filter(
#                     stage=stage,
#                     status="RUNNING",
#                 )
#                 .order_by(
#                     "-created_at",
#                 )
#                 .first()
#             )

#             # =====================================================
#             # IF NO RUNNING BATCH, GET LATEST BATCH
#             # =====================================================

#             if running_batch:

#                 stage_batch = running_batch

#             else:

#                 stage_batch = (
#                     StageBatch.objects
#                     .filter(
#                         stage=stage,
#                     )
#                     .order_by(
#                         "-created_at",
#                     )
#                     .first()
#                 )

#             # =====================================================
#             # NO BATCH FOUND
#             # =====================================================

#             if not stage_batch:

#                 return Response(
#                     {
#                         "success": True,
#                         "message": (
#                             "No stage batch execution found."
#                         ),
#                         "data": {
#                             "stage_id": stage.id,
#                             "stage_name": stage.name,
#                             "stage_type": stage.stage_type,
#                             "status": "NOT_STARTED",
#                             "batch_id": None,
#                             "batch_number": None,
#                             "started_at": None,
#                             "completed_at": None,
#                             "equipment": [],
#                             "processes": [],
#                         },
#                     },
#                     status=status.HTTP_200_OK,
#                 )

#             # =====================================================
#             # GET STAGE EQUIPMENT
#             # =====================================================

#             stage_equipments = (
#                 stage.equipments
#                 .filter(
#                     is_active=True,
#                 )
#                 .select_related(
#                     "equipment_type",
#                 )
#                 .all()
#             )

#             # =====================================================
#             # PREPARE GLOBAL EQUIPMENT DATA
#             # =====================================================

#             equipment_data = []

#             for equipment in stage_equipments:

#                 equipment_data.append(
#                     {
#                         "id": equipment.id,

#                         "name": equipment.name,

#                         "code": equipment.code,

#                         "equipment_type": (
#                             equipment.equipment_type.name
#                         ),

#                         # -------------------------------------------------
#                         # GLOBAL/CURRENT EQUIPMENT STATUS
#                         # -------------------------------------------------

#                         "status": equipment.status,

#                         "current_state": (
#                             equipment.current_state
#                         ),

#                         # -------------------------------------------------
#                         # Equipment timing configuration/runtime
#                         # -------------------------------------------------

#                         "start_time": (
#                             equipment.start_time
#                         ),

#                         "end_time": (
#                             equipment.end_time
#                         ),

#                         "duration_seconds": (
#                             equipment.duration_seconds
#                         ),
#                     }
#                 )

#             # =====================================================
#             # GET PROCESS EXECUTIONS
#             # =====================================================

#             process_executions = (
#                 StageBatchProcessExecution.objects
#                 .filter(
#                     stage_batch=stage_batch,
#                 )
#                 .select_related(
#                     "process",
#                 )
#                 .prefetch_related(
#                     "equipment_executions__equipment__equipment_type",
#                 )
#                 .order_by(
#                     "process__sequence",
#                 )
#             )

#             # =====================================================
#             # PREPARE PROCESS DATA
#             # =====================================================

#             processes_data = []

#             for process_execution in process_executions:

#                 # -------------------------------------------------
#                 # Equipment used by THIS process execution.
#                 #
#                 # IMPORTANT:
#                 #
#                 # We are NOT reading process equipment state from
#                 # Equipment.current_state.
#                 #
#                 # We are reading:
#                 #
#                 # StageBatchProcessEquipmentExecution.state
#                 #
#                 # which stores the state produced by this process.
#                 # -------------------------------------------------

#                 process_equipment_data = []

#                 equipment_executions = (
#                     process_execution
#                     .equipment_executions
#                     .all()
#                 )

#                 for equipment_execution in equipment_executions:

#                     equipment = (
#                         equipment_execution.equipment
#                     )

#                     process_equipment_data.append(
#                         {
#                             "id": equipment.id,

#                             "name": equipment.name,

#                             "code": equipment.code,

#                             "equipment_type": (
#                                 equipment
#                                 .equipment_type
#                                 .name
#                             ),

#                             # -------------------------------------------------
#                             # PROCESS-SPECIFIC STATE
#                             #
#                             # This is the important new field.
#                             # -------------------------------------------------

#                             "state": (
#                                 equipment_execution.state
#                             ),

#                             # -------------------------------------------------
#                             # Process equipment execution timing
#                             # -------------------------------------------------

#                             "started_at": (
#                                 equipment_execution.started_at
#                             ),

#                             "completed_at": (
#                                 equipment_execution.completed_at
#                             ),

#                             # -------------------------------------------------
#                             # GLOBAL/CURRENT EQUIPMENT INFORMATION
#                             #
#                             # This can be different from "state".
#                             # -------------------------------------------------

#                             "current_state": (
#                                 equipment.current_state
#                             ),

#                             "status": (
#                                 equipment.status
#                             ),

#                             "duration_seconds": (
#                                 equipment.duration_seconds
#                             ),
#                         }
#                     )

#                 # -------------------------------------------------
#                 # Add process information.
#                 # -------------------------------------------------

#                 processes_data.append(
#                     {
#                         "execution_id": (
#                             process_execution.id
#                         ),

#                         "process_id": (
#                             process_execution.process_id
#                         ),

#                         "process_name": (
#                             process_execution
#                             .process
#                             .name
#                         ),

#                         "sequence": (
#                             process_execution
#                             .process
#                             .sequence
#                         ),

#                         "status": (
#                             process_execution.status
#                         ),

#                         "started_at": (
#                             process_execution.started_at
#                         ),

#                         "completed_at": (
#                             process_execution.completed_at
#                         ),

#                         "actual_duration_seconds": (
#                             process_execution
#                             .actual_duration_seconds
#                         ),

#                         "remarks": (
#                             process_execution.remarks
#                         ),

#                         "equipment": (
#                             process_equipment_data
#                         ),
#                     }
#                 )

#             # =====================================================
#             # RETURN RESPONSE
#             # =====================================================

#             return Response(
#                 {
#                     "success": True,

#                     "message": (
#                         "Treatment stage status "
#                         "retrieved successfully."
#                     ),

#                     "data": {

#                         # ---------------------------------------------
#                         # BATCH INFORMATION
#                         # ---------------------------------------------

#                         "batch_id": (
#                             stage_batch.id
#                         ),

#                         "batch_number": (
#                             stage_batch.batch_number
#                         ),

#                         # ---------------------------------------------
#                         # STAGE INFORMATION
#                         # ---------------------------------------------

#                         "stage_id": stage.id,

#                         "stage_name": (
#                             stage.name
#                         ),

#                         "stage_type": (
#                             stage.stage_type
#                         ),

#                         # ---------------------------------------------
#                         # BATCH STATUS
#                         # ---------------------------------------------

#                         "status": (
#                             stage_batch.status
#                         ),

#                         "started_at": (
#                             stage_batch.started_at
#                         ),

#                         "completed_at": (
#                             stage_batch.completed_at
#                         ),

#                         # ---------------------------------------------
#                         # CURRENT/GLOBAL EQUIPMENT
#                         # ---------------------------------------------

#                         "equipment": (
#                             equipment_data
#                         ),

#                         # ---------------------------------------------
#                         # PROCESS EXECUTION
#                         # ---------------------------------------------

#                         "processes": (
#                             processes_data
#                         ),
#                     },
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as exc:

#             # =====================================================
#             # UNEXPECTED ERROR
#             # =====================================================

#             return Response(
#                 {
#                     "success": False,
#                     "message": (
#                         "Failed to retrieve treatment "
#                         "stage status."
#                     ),
#                     "error": str(exc),
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from treatment_process.models import (
    TreatmentStage,
    StageBatch,
    StageBatchProcessExecution,
    StageEquipmentConfig,
)


class StageBatchStatusView(APIView):
    """
    Get the current execution status of a TreatmentStage.

    This API returns:

    1. StageBatch information.
    2. Current/global equipment state.
    3. Process execution status.
    4. Equipment state for each individual process execution.

    Important distinction:

        StageEquipmentConfig.current_state
            -> Current/global state of the equipment for this stage.

        StageBatchProcessEquipmentExecution.state
            -> State produced by that particular process.

    Equipment.is_active
        -> Physical equipment availability.

    StageEquipmentConfig.status
        -> Stage-specific runtime/availability status.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, stage_id):

        try:

            # =====================================================
            # GET STAGE
            # =====================================================

            try:

                stage = (
                    TreatmentStage.objects
                    .get(
                        id=stage_id,
                        user=request.user,
                    )
                )

            except TreatmentStage.DoesNotExist:

                return Response(
                    {
                        "success": False,
                        "message": "Treatment stage not found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # =====================================================
            # GET LATEST RUNNING BATCH
            # =====================================================

            running_batch = (
                StageBatch.objects
                .filter(
                    stage=stage,
                    status="RUNNING",
                )
                .order_by(
                    "-created_at",
                )
                .first()
            )

            # =====================================================
            # IF NO RUNNING BATCH, GET LATEST BATCH
            # =====================================================

            if running_batch:

                stage_batch = running_batch

            else:

                stage_batch = (
                    StageBatch.objects
                    .filter(
                        stage=stage,
                    )
                    .order_by(
                        "-created_at",
                    )
                    .first()
                )

            # =====================================================
            # NO BATCH FOUND
            # =====================================================

            if not stage_batch:

                return Response(
                    {
                        "success": True,
                        "message": (
                            "No stage batch execution found."
                        ),
                        "data": {
                            "stage_id": stage.id,
                            "stage_name": stage.name,
                            "stage_type": stage.stage_type,
                            "status": "NOT_STARTED",
                            "batch_id": None,
                            "batch_number": None,
                            "started_at": None,
                            "completed_at": None,
                            "equipment": [],
                            "processes": [],
                        },
                    },
                    status=status.HTTP_200_OK,
                )

            # =====================================================
            # GET STAGE EQUIPMENT
            # =====================================================

            stage_equipments = (
                stage.equipments
                .filter(
                    is_active=True,
                )
                .select_related(
                    "equipment_type",
                )
                .all()
            )

            # =====================================================
            # PREPARE GLOBAL EQUIPMENT DATA
            # =====================================================

            equipment_data = []

            for equipment in stage_equipments:

                # -------------------------------------------------
                # Get the configuration for this equipment in the
                # current stage.
                #
                # Runtime state and timing now belong to
                # StageEquipmentConfig.
                # -------------------------------------------------

                config = (
                    StageEquipmentConfig.objects
                    .filter(
                        stage=stage,
                        equipment=equipment,
                    )
                    .first()
                )

                equipment_data.append(
                    {
                        "id": equipment.id,

                        "name": equipment.name,

                        "code": equipment.code,

                        "equipment_type": (
                            equipment.equipment_type.name
                        ),

                        # -------------------------------------------------
                        # Physical equipment availability
                        # -------------------------------------------------

                        "is_active": equipment.is_active,

                        # -------------------------------------------------
                        # Stage-specific runtime configuration
                        # -------------------------------------------------

                        "status": (
                            config.status
                            if config
                            else None
                        ),

                        "current_state": (
                            config.current_state
                            if config
                            else None
                        ),

                        "start_time": (
                            config.start_time
                            if config
                            else None
                        ),

                        "end_time": (
                            config.end_time
                            if config
                            else None
                        ),

                        "duration_seconds": (
                            config.duration_seconds
                            if config
                            else None
                        ),
                    }
                )

            # =====================================================
            # GET PROCESS EXECUTIONS
            # =====================================================

            process_executions = (
                StageBatchProcessExecution.objects
                .filter(
                    stage_batch=stage_batch,
                )
                .select_related(
                    "process",
                )
                .prefetch_related(
                    "equipment_executions__equipment__equipment_type",
                )
                .order_by(
                    "process__sequence",
                )
            )

            # =====================================================
            # PREPARE PROCESS DATA
            # =====================================================

            processes_data = []

            for process_execution in process_executions:

                # -------------------------------------------------
                # Equipment used by THIS process execution.
                #
                # IMPORTANT:
                #
                # We are NOT reading process equipment state from
                # Equipment.current_state.
                #
                # We are reading:
                #
                # StageBatchProcessEquipmentExecution.state
                #
                # which stores the state produced by this process.
                # -------------------------------------------------

                process_equipment_data = []

                equipment_executions = (
                    process_execution
                    .equipment_executions
                    .all()
                )

                for equipment_execution in equipment_executions:

                    equipment = (
                        equipment_execution.equipment
                    )

                    process_equipment_data.append(
                        {
                            "id": equipment.id,

                            "name": equipment.name,

                            "code": equipment.code,

                            "equipment_type": (
                                equipment
                                .equipment_type
                                .name
                            ),

                            # -------------------------------------------------
                            # PROCESS-SPECIFIC STATE
                            #
                            # This is the important new field.
                            # -------------------------------------------------

                            "state": (
                                equipment_execution.state
                            ),

                            # -------------------------------------------------
                            # Process equipment execution timing
                            # -------------------------------------------------

                            "started_at": (
                                equipment_execution.started_at
                            ),

                            "completed_at": (
                                equipment_execution.completed_at
                            ),

                            # -------------------------------------------------
                            # STAGE-SPECIFIC EQUIPMENT INFORMATION
                            #
                            # The process-specific "state" above comes
                            # from StageBatchProcessEquipmentExecution.
                            #
                            # Runtime/global equipment information now
                            # comes from StageEquipmentConfig.
                            # -------------------------------------------------

                            "current_state": (
                                StageEquipmentConfig.objects
                                .filter(
                                    stage=stage,
                                    equipment=equipment,
                                )
                                .values_list(
                                    "current_state",
                                    flat=True,
                                )
                                .first()
                            ),

                            "status": (
                                StageEquipmentConfig.objects
                                .filter(
                                    stage=stage,
                                    equipment=equipment,
                                )
                                .values_list(
                                    "status",
                                    flat=True,
                                )
                                .first()
                            ),

                            "duration_seconds": (
                                StageEquipmentConfig.objects
                                .filter(
                                    stage=stage,
                                    equipment=equipment,
                                )
                                .values_list(
                                    "duration_seconds",
                                    flat=True,
                                )
                                .first()
                            ),
                        }
                    )

                # -------------------------------------------------
                # Add process information.
                # -------------------------------------------------

                processes_data.append(
                    {
                        "execution_id": (
                            process_execution.id
                        ),

                        "process_id": (
                            process_execution.process_id
                        ),

                        "process_name": (
                            process_execution
                            .process
                            .name
                        ),

                        "sequence": (
                            process_execution
                            .process
                            .sequence
                        ),

                        "status": (
                            process_execution.status
                        ),

                        "started_at": (
                            process_execution.started_at
                        ),

                        "completed_at": (
                            process_execution.completed_at
                        ),

                        "actual_duration_seconds": (
                            process_execution
                            .actual_duration_seconds
                        ),

                        "remarks": (
                            process_execution.remarks
                        ),

                        "equipment": (
                            process_equipment_data
                        ),
                    }
                )

            # =====================================================
            # RETURN RESPONSE
            # =====================================================

            return Response(
                {
                    "success": True,

                    "message": (
                        "Treatment stage status "
                        "retrieved successfully."
                    ),

                    "data": {

                        # ---------------------------------------------
                        # BATCH INFORMATION
                        # ---------------------------------------------

                        "batch_id": (
                            stage_batch.id
                        ),

                        "batch_number": (
                            stage_batch.batch_number
                        ),

                        # ---------------------------------------------
                        # STAGE INFORMATION
                        # ---------------------------------------------

                        "stage_id": stage.id,

                        "stage_name": (
                            stage.name
                        ),

                        "stage_type": (
                            stage.stage_type
                        ),

                        # ---------------------------------------------
                        # BATCH STATUS
                        # ---------------------------------------------

                        "status": (
                            stage_batch.status
                        ),

                        "started_at": (
                            stage_batch.started_at
                        ),

                        "completed_at": (
                            stage_batch.completed_at
                        ),

                        # ---------------------------------------------
                        # CURRENT/STAGE-SPECIFIC EQUIPMENT
                        # ---------------------------------------------

                        "equipment": (
                            equipment_data
                        ),

                        # ---------------------------------------------
                        # PROCESS EXECUTION
                        # ---------------------------------------------

                        "processes": (
                            processes_data
                        ),
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:

            # =====================================================
            # UNEXPECTED ERROR
            # =====================================================

            return Response(
                {
                    "success": False,
                    "message": (
                        "Failed to retrieve treatment "
                        "stage status."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )