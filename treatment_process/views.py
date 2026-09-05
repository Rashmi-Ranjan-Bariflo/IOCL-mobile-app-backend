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
