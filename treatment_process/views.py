from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    TreatmentStage,
    TreatmentProcess,
    TreatmentBatch,
    DosingRecord,
    ProcessExecutionLog,
    Equipment,
)

from .serializers import (
    TreatmentStageSerializer,
    TreatmentProcessSerializer,
    TreatmentBatchSerializer,
    DosingRecordSerializer,
    ProcessExecutionLogSerializer,
)
from django.db.models import Prefetch
from sensors.models import Sensor


# ==========================================================
# TREATMENT STAGE
# ==========================================================
class TreatmentStageListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        stages = TreatmentStage.objects.all()

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

        processes = TreatmentProcess.objects.all().select_related("stage")

        stage_id = request.query_params.get("stage")
        process_status = request.query_params.get("status")
        is_active = request.query_params.get("is_active")

        if stage_id:
            processes = processes.filter(stage_id=stage_id)

        if process_status:
            processes = processes.filter(status=process_status)

        if is_active is not None:
            processes = processes.filter(is_active=is_active.lower() == "true")

        processes = processes.order_by("stage__sequence", "sequence")

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

        batches = TreatmentBatch.objects.all().select_related(
            "process",
            "process__stage",
        )

        process_id = request.query_params.get("process")
        stage_id = request.query_params.get("stage")
        batch_status = request.query_params.get("status")

        if process_id:
            batches = batches.filter(process_id=process_id)

        if stage_id:
            batches = batches.filter(process__stage_id=stage_id)

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
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# START TREATMENT BATCH
# ==========================================================
class TreatmentBatchStartView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        try:
            batch = TreatmentBatch.objects.select_related(
                "process",
                "process__stage",
            ).get(pk=pk)

        except TreatmentBatch.DoesNotExist:

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

        batch.save(
            update_fields=[
                "status",
                "started_at",
                "updated_at",
            ]
        )

        ProcessExecutionLog.objects.create(
            batch=batch,
            process=batch.process,
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
                "process__stage",
            ).get(pk=pk)

        except TreatmentBatch.DoesNotExist:

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
                    "message": "Only a running batch can be completed.",
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

        # Complete the currently running process execution
        log = (
            ProcessExecutionLog.objects.filter(
                batch=batch,
                process=batch.process,
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
            batch = TreatmentBatch.objects.select_related(
                "process",
                "process__stage",
            ).get(pk=pk)

        except TreatmentBatch.DoesNotExist:

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

        batch.status = "STOPPED"

        batch.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # Stop the currently running process execution
        log = (
            ProcessExecutionLog.objects.filter(
                batch=batch,
                process=batch.process,
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
# CURRENT PROCESS
# ==========================================================
class TreatmentBatchCurrentProcessView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        try:
            batch = TreatmentBatch.objects.select_related(
                "process",
                "process__stage",
            ).get(pk=pk)

        except TreatmentBatch.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Treatment batch not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not batch.process:

            return Response(
                {
                    "success": True,
                    "message": "No current process assigned.",
                    "data": None,
                }
            )

        serializer = TreatmentProcessSerializer(batch.process)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )


# ==========================================================
# DOSING RECORD
# ==========================================================
class DosingRecordListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        records = DosingRecord.objects.all().select_related(
            "batch",
            "batch__process",
            "batch__process__stage",
        )

        batch_id = request.query_params.get("batch")
        process_id = request.query_params.get("process")
        stage_id = request.query_params.get("stage")
        solution_type = request.query_params.get("solution_type")

        if batch_id:
            records = records.filter(batch_id=batch_id)

        if process_id:
            records = records.filter(batch__process_id=process_id)

        if stage_id:
            records = records.filter(batch__process__stage_id=stage_id)

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

        logs = ProcessExecutionLog.objects.all().select_related(
            "batch",
            "process",
            "process__stage",
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
#           INLET STAGES WITH EQUIPMENT AND SENSORS
# ==========================================================
class InletStageEquipmentView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # --------------------------------------------------
        # Get only equipment belonging to logged-in user
        # --------------------------------------------------
        print("REQUEST USER:", request.user)
        print("REQUEST USER TYPE:", type(request.user))

        equipment_queryset = (
            Equipment.objects
            .filter(
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
                        Sensor.objects
                        .select_related("sensor_type")
                        .filter(is_active=True)
                        .order_by("name")
                    ),
                )
            )
            .order_by("name")
        )

        # --------------------------------------------------
        # Get two inlet stages
        # --------------------------------------------------

        stages = (
            TreatmentStage.objects
            .filter(
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

        # --------------------------------------------------
        # Response containers
        # --------------------------------------------------

        wastewater_stage_data = None
        normalwater_stage_data = None

        # --------------------------------------------------
        # Process stages
        # --------------------------------------------------

        for stage in stages:

            equipment_data = []

            # ----------------------------------------------
            # Get equipment of this stage
            # ----------------------------------------------

            for equipment in stage.equipments.all():

                sensors_data = []

                # ------------------------------------------
                # Get sensors of equipment
                # ------------------------------------------

                for sensor in equipment.sensors.all():

                    sensors_data.append(
                        {
                            "id": sensor.id,
                            "name": sensor.name,
                            "code": sensor.code,
                            "sensor_type": (
                                sensor.sensor_type.name
                                if sensor.sensor_type
                                else None
                            ),
                            "unit": sensor.unit,
                            "status": sensor.status,
                            "is_active": sensor.is_active,
                        }
                    )

                # ------------------------------------------
                # Equipment data
                # ------------------------------------------

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

            # ----------------------------------------------
            # Stage data
            # ----------------------------------------------

            stage_data = {
                "id": stage.id,
                "name": stage.name,
                "stage_type": stage.stage_type,
                "sequence": stage.sequence,
                "description": stage.description,
                "equipment": equipment_data,
            }

            # ----------------------------------------------
            # Separate stages
            # ----------------------------------------------

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