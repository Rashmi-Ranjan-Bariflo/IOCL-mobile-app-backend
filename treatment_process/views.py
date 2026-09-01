from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    TreatmentProcess,
    TreatmentStage,
    TreatmentBatch,
    DosingRecord,
    ProcessExecutionLog,
)

from .serializers import (
    TreatmentProcessSerializer,
    TreatmentStageSerializer,
    TreatmentBatchSerializer,
    DosingRecordSerializer,
    ProcessExecutionLogSerializer,
)


# ==========================================================
# TREATMENT PROCESS
# ==========================================================
class TreatmentProcessListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        processes = TreatmentProcess.objects.all().prefetch_related("stages")

        status_value = request.query_params.get("status")
        is_active = request.query_params.get("is_active")

        if status_value:
            processes = processes.filter(status=status_value)

        if is_active is not None:
            processes = processes.filter(is_active=is_active.lower() == "true")

        serializer = TreatmentProcessSerializer(processes, many=True)

        return Response({"success": True, "data": serializer.data})

    def post(self, request):

        serializer = TreatmentProcessSerializer(data=request.data)

        if serializer.is_valid():

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
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# TREATMENT STAGE
# ==========================================================
class TreatmentStageListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        stages = TreatmentStage.objects.all()

        process_id = request.query_params.get("process")
        stage_type = request.query_params.get("stage_type")

        if process_id:
            stages = stages.filter(process_id=process_id)

        if stage_type:
            stages = stages.filter(stage_type=stage_type)

        stages = stages.order_by("process", "sequence")

        serializer = TreatmentStageSerializer(stages, many=True)

        return Response({"success": True, "data": serializer.data})

    def post(self, request):

        serializer = TreatmentStageSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Treatment stage created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# TREATMENT BATCH
# ==========================================================
class TreatmentBatchListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        batches = TreatmentBatch.objects.all().select_related(
            "process",
            "current_stage",
        )

        process_id = request.query_params.get("process")
        batch_status = request.query_params.get("status")

        if process_id:
            batches = batches.filter(process_id=process_id)

        if batch_status:
            batches = batches.filter(status=batch_status)

        serializer = TreatmentBatchSerializer(batches, many=True)

        return Response({"success": True, "data": serializer.data})

    def post(self, request):

        serializer = TreatmentBatchSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Treatment batch created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# START TREATMENT BATCH
# ==========================================================
class TreatmentBatchStartView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        try:
            batch = TreatmentBatch.objects.select_related("process").get(pk=pk)

        except TreatmentBatch.DoesNotExist:

            return Response(
                {"success": False, "message": "Treatment batch not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if batch.status == "RUNNING":

            return Response(
                {"success": False, "message": "Treatment batch is already running."},
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

        first_stage = (
            TreatmentStage.objects.filter(process=batch.process, is_active=True)
            .order_by("sequence")
            .first()
        )

        if not first_stage:

            return Response(
                {"success": False, "message": "No active treatment stage found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        batch.status = "RUNNING"
        batch.started_at = now
        batch.current_stage = first_stage

        batch.save(
            update_fields=[
                "status",
                "started_at",
                "current_stage",
                "updated_at",
            ]
        )

        ProcessExecutionLog.objects.create(
            batch=batch,
            stage=first_stage,
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
# COMPLETE TREATMENT BATCH
# ==========================================================
class TreatmentBatchCompleteView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        try:
            batch = TreatmentBatch.objects.select_related(
                "process",
                "current_stage",
            ).get(pk=pk)

        except TreatmentBatch.DoesNotExist:

            return Response(
                {"success": False, "message": "Treatment batch not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if batch.status != "RUNNING":

            return Response(
                {"success": False, "message": "Only a running batch can be completed."},
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

        if batch.current_stage:

            log = (
                ProcessExecutionLog.objects.filter(
                    batch=batch,
                    stage=batch.current_stage,
                    completed_at__isnull=True,
                )
                .order_by("-created_at")
                .first()
            )

            if log:

                log.status = "COMPLETED"
                log.completed_at = now

                if log.started_at:
                    log.actual_duration_seconds = int(
                        (now - log.started_at).total_seconds()
                    )

                log.save(
                    update_fields=[
                        "status",
                        "completed_at",
                        "actual_duration_seconds",
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

    def post(self, request, pk):

        try:
            batch = TreatmentBatch.objects.select_related("current_stage").get(pk=pk)

        except TreatmentBatch.DoesNotExist:

            return Response(
                {"success": False, "message": "Treatment batch not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if batch.status != "RUNNING":

            return Response(
                {"success": False, "message": "Only a running batch can be stopped."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        batch.status = "STOPPED"

        batch.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        if batch.current_stage:

            log = (
                ProcessExecutionLog.objects.filter(
                    batch=batch,
                    stage=batch.current_stage,
                    completed_at__isnull=True,
                )
                .order_by("-created_at")
                .first()
            )

            if log:

                log.status = "STOPPED"
                log.completed_at = now

                if log.started_at:
                    log.actual_duration_seconds = int(
                        (now - log.started_at).total_seconds()
                    )

                log.remarks = "Treatment batch stopped."

                log.save(
                    update_fields=[
                        "status",
                        "completed_at",
                        "actual_duration_seconds",
                        "remarks",
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

        try:
            batch = TreatmentBatch.objects.select_related("current_stage").get(pk=pk)

        except TreatmentBatch.DoesNotExist:

            return Response(
                {"success": False, "message": "Treatment batch not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not batch.current_stage:

            return Response(
                {"success": True, "message": "No current stage assigned.", "data": None}
            )

        serializer = TreatmentStageSerializer(batch.current_stage)

        return Response({"success": True, "data": serializer.data})


# ==========================================================
# DOSING RECORD
# ==========================================================
class DosingRecordListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        records = DosingRecord.objects.all().select_related("batch")

        batch_id = request.query_params.get("batch")
        solution_type = request.query_params.get("solution_type")

        if batch_id:
            records = records.filter(batch_id=batch_id)

        if solution_type:
            records = records.filter(solution_type=solution_type)

        records = records.order_by("-dosing_time")

        serializer = DosingRecordSerializer(records, many=True)

        return Response({"success": True, "data": serializer.data})

    def post(self, request):

        serializer = DosingRecordSerializer(data=request.data)

        if serializer.is_valid():

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
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# PROCESS EXECUTION LOG
# ==========================================================
class ProcessExecutionLogListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        logs = ProcessExecutionLog.objects.all().select_related(
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

        logs = logs.order_by("-created_at")

        serializer = ProcessExecutionLogSerializer(logs, many=True)

        return Response({"success": True, "data": serializer.data})

    def post(self, request):

        serializer = ProcessExecutionLogSerializer(data=request.data)

        if serializer.is_valid():

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
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
