from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import (
    EquipmentTest,
    EquipmentType,
    Equipment,
)

from .serializers import (
    EquipmentTypeSerializer,
    EquipmentSerializer,
)


# ==========================================================
#                  EQUIPMENT TYPE LIST / CREATE
# ==========================================================
class EquipmentTypeListCreateView(APIView):

    permission_classes = [AllowAny]

    # ------------------------------------------------------
    # GET - List Equipment Types
    # ------------------------------------------------------
    def get(self, request):

        equipment_types = EquipmentType.objects.all()

        serializer = EquipmentTypeSerializer(
            equipment_types,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": "Equipment types retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------
    # POST - Create Equipment Type
    # ------------------------------------------------------
    def post(self, request):

        serializer = EquipmentTypeSerializer(data=request.data)

        if serializer.is_valid():

            equipment_type = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Equipment type created successfully.",
                    "data": EquipmentTypeSerializer(equipment_type).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to create equipment type.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
#                 EQUIPMENT TYPE DETAIL
# ==========================================================
class EquipmentTypeDetailView(APIView):

    permission_classes = [AllowAny]

    # ------------------------------------------------------
    # GET - Equipment Type Detail
    # ------------------------------------------------------
    def get(self, request, pk):

        try:
            equipment_type = EquipmentType.objects.get(pk=pk)

        except EquipmentType.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Equipment type not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EquipmentTypeSerializer(equipment_type)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------
    # PUT - Update Equipment Type
    # ------------------------------------------------------
    def put(self, request, pk):

        try:
            equipment_type = EquipmentType.objects.get(pk=pk)

        except EquipmentType.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Equipment type not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EquipmentTypeSerializer(
            equipment_type,
            data=request.data,
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Equipment type updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to update equipment type.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # PATCH - Partial Update Equipment Type
    # ------------------------------------------------------
    def patch(self, request, pk):

        try:
            equipment_type = EquipmentType.objects.get(pk=pk)

        except EquipmentType.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Equipment type not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EquipmentTypeSerializer(
            equipment_type,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Equipment type updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to update equipment type.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # DELETE - Delete Equipment Type
    # ------------------------------------------------------
    def delete(self, request, pk):

        try:
            equipment_type = EquipmentType.objects.get(pk=pk)

        except EquipmentType.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Equipment type not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        equipment_type.delete()

        return Response(
            {
                "success": True,
                "message": "Equipment type deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                  EQUIPMENT LIST / CREATE
# ==========================================================
class EquipmentListCreateView(APIView):

    permission_classes = [AllowAny]

    # ------------------------------------------------------
    # GET - List Equipment
    # ------------------------------------------------------
    def get(self, request):

        equipment = Equipment.objects.select_related(
            "equipment_type",
        ).all()

        serializer = EquipmentSerializer(
            equipment,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": "Equipment retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------
    # POST - Create Equipment
    # ------------------------------------------------------
    def post(self, request):

        serializer = EquipmentSerializer(data=request.data)

        if serializer.is_valid():

            equipment = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Equipment created successfully.",
                    "data": EquipmentSerializer(equipment).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to create equipment.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
#                     EQUIPMENT DETAIL
# ==========================================================
class EquipmentDetailView(APIView):

    permission_classes = [AllowAny]

    # ------------------------------------------------------
    # GET - Equipment Detail
    # ------------------------------------------------------
    def get(self, request, pk):

        try:
            equipment = Equipment.objects.select_related(
                "equipment_type",
            ).get(pk=pk)

        except Equipment.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Equipment not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EquipmentSerializer(equipment)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------
    # PUT - Update Equipment
    # ------------------------------------------------------
    def put(self, request, pk):

        try:
            equipment = Equipment.objects.get(pk=pk)

        except Equipment.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Equipment not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EquipmentSerializer(
            equipment,
            data=request.data,
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Equipment updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to update equipment.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # PATCH - Partial Update Equipment
    # ------------------------------------------------------
    def patch(self, request, pk):

        try:
            equipment = Equipment.objects.get(pk=pk)

        except Equipment.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Equipment not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EquipmentSerializer(
            equipment,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Equipment updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to update equipment.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # DELETE - Delete Equipment
    # ------------------------------------------------------
    def delete(self, request, pk):

        try:
            equipment = Equipment.objects.get(pk=pk)

        except Equipment.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Equipment not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        equipment.delete()

        return Response(
            {
                "success": True,
                "message": "Equipment deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# =================================================================================================

from django.utils import timezone
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404

from .models import Equipment, EquipmentManualLog
from treatment_process.models import TreatmentStage, TreatmentProcess
from .serializers import EquipmentOnOffSerializer


# ==========================================================
#                        VALVE ON
# ==========================================================
class ValveOnView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, equipment_id):
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )

        if "valve" not in equipment.equipment_type.name.lower():
            return Response(
                {
                    "detail": f"This equipment is not a Valve. Current type: {equipment.equipment_type.name}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EquipmentOnOffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stage_id = serializer.validated_data.get("stage_id")
        process_id = serializer.validated_data.get("process_id")

        stage = None
        if stage_id:
            stage = get_object_or_404(TreatmentStage, id=stage_id)
            if process_id:
                get_object_or_404(TreatmentProcess, id=process_id, stage=stage)

        open_log = EquipmentManualLog.objects.filter(
            equipment=equipment, action="ON", ended_at__isnull=True
        ).first()

        if open_log:
            return Response(
                {
                    "detail": "Valve is already ON",
                    "log_id": open_log.id,
                    "start_time": open_log.started_at,
                    "status": "ACTIVE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        with transaction.atomic():
            log = EquipmentManualLog.objects.create(
                equipment=equipment,
                stage=stage,
                action="ON",
                started_at=now,
                performed_by=request.user,
            )

            equipment.status = "ACTIVE"
            equipment.current_state = "ON"
            equipment.start_time = now.time()
            equipment.save(
                update_fields=["status", "current_state", "start_time", "updated_at"]
            )

        return Response(
            {
                "success": True,
                "message": "Valve turned ON successfully",
                "data": {
                    "log_id": log.id,
                    "equipment_id": equipment.id,
                    "equipment_name": equipment.name,
                    "equipment_code": equipment.code,
                    "status": "ACTIVE",
                    "current_state": "ON",
                    "start_time": log.started_at,
                    "stage": stage.name if stage else None,
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
#                        VALVE OFF
# ==========================================================
class ValveOffView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, equipment_id):
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )

        if "valve" not in equipment.equipment_type.name.lower():
            return Response(
                {
                    "detail": f"This equipment is not a Valve. Current type: {equipment.equipment_type.name}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        open_log = (
            EquipmentManualLog.objects.filter(
                equipment=equipment, action="ON", ended_at__isnull=True
            )
            .order_by("-started_at")
            .first()
        )

        if not open_log:
            return Response(
                {"detail": "Valve is already OFF or no active session found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        with transaction.atomic():
            duration = int((now - open_log.started_at).total_seconds())

            open_log.ended_at = now
            open_log.duration_seconds = duration
            open_log.save(update_fields=["ended_at", "duration_seconds"])

            equipment.status = "INACTIVE"
            equipment.current_state = "OFF"
            equipment.end_time = now.time()
            equipment.duration_seconds = duration
            equipment.save(
                update_fields=[
                    "status",
                    "current_state",
                    "end_time",
                    "duration_seconds",
                    "updated_at",
                ]
            )

        return Response(
            {
                "id": open_log.id,
                "equipment": {
                    "id": equipment.id,
                    "name": equipment.name,
                    "code": equipment.code,
                    "status": "INACTIVE",
                    "current_state": "OFF",
                },
                "action": "OFF",
                "started_at": open_log.started_at,
                "ended_at": open_log.ended_at,
                "duration_seconds": open_log.duration_seconds,
                "status": "INACTIVE",
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                        MOTOR ON
# ==========================================================
class MotorOnView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, equipment_id):
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )

        if (
            "motor" not in equipment.equipment_type.name.lower()
            and "pump" not in equipment.equipment_type.name.lower()
        ):
            return Response(
                {
                    "detail": f"This equipment is not a Motor. Current type: {equipment.equipment_type.name}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EquipmentOnOffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stage_id = serializer.validated_data.get("stage_id")
        if not stage_id:
            return Response(
                {"detail": "stage_id is required for Motor ON"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stage = get_object_or_404(TreatmentStage, id=stage_id)

        # Valve of same stage must be ON
        stage_valves = stage.equipments.filter(equipment_type__name__icontains="valve")

        valve_is_on = False
        for valve in stage_valves:
            if EquipmentManualLog.objects.filter(
                equipment=valve,
                action="ON",
                ended_at__isnull=True,
                stage=stage,
            ).exists():
                valve_is_on = True
                break

        if not valve_is_on:
            return Response(
                {
                    "detail": "Cannot turn Motor ON. Valve of this stage is not ON.",
                    "stage": stage.name,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        open_log = EquipmentManualLog.objects.filter(
            equipment=equipment,
            action="ON",
            ended_at__isnull=True,
        ).first()

        if open_log:
            return Response(
                {
                    "detail": "Motor is already ON",
                    "log_id": open_log.id,
                    "started_at": open_log.started_at,
                    "status": "ACTIVE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        with transaction.atomic():
            log = EquipmentManualLog.objects.create(
                equipment=equipment,
                stage=stage,
                action="ON",
                started_at=now,
                performed_by=request.user,
            )

            equipment.status = "ACTIVE"
            equipment.current_state = "ON"
            equipment.save(update_fields=["status", "current_state", "updated_at"])

            sensors = self._activate_sensor(stage, request.user)

        return Response(
            {
                "id": log.id,
                "equipment": {
                    "id": equipment.id,
                    "name": equipment.name,
                    "code": equipment.code,
                    "status": "ACTIVE",
                    "current_state": "ON",
                },
                "action": "ON",
                "started_at": log.started_at,
                "ended_at": None,
                "duration_seconds": None,
                "status": "ACTIVE",
                "stage": stage.name,
                "sensors": sensors,
            },
            status=status.HTTP_201_CREATED,
        )

    def _activate_sensor(self, stage, user):
        sensors = (
            stage.equipments.filter(equipment_type__name__icontains="sensor")
            .exclude(name__icontains="valve")
            .exclude(code__icontains="val")
        )

        activated = []

        for sensor in sensors:
            if EquipmentManualLog.objects.filter(
                equipment=sensor, ended_at__isnull=True
            ).exists():
                continue

            log = EquipmentManualLog.objects.create(
                equipment=sensor,
                stage=stage,
                action="ON",
                started_at=timezone.now(),
                performed_by=user,
            )

            sensor.status = "ACTIVE"
            sensor.current_state = "ON"
            sensor.save(update_fields=["status", "current_state", "updated_at"])

            activated.append(
                {
                    "id": sensor.id,
                    "name": sensor.name,
                    "code": sensor.code,
                    "status": "ACTIVE",
                    "current_state": "ON",
                    "started_at": log.started_at,
                }
            )

        return activated


# ==========================================================
#                        MOTOR OFF
# ==========================================================
class MotorOffView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, equipment_id):
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )

        if (
            "motor" not in equipment.equipment_type.name.lower()
            and "pump" not in equipment.equipment_type.name.lower()
        ):
            return Response(
                {
                    "detail": f"This equipment is not a Motor. Current type: {equipment.equipment_type.name}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        open_log = (
            EquipmentManualLog.objects.filter(
                equipment=equipment,
                action="ON",
                ended_at__isnull=True,
            )
            .order_by("-started_at")
            .first()
        )

        if not open_log:
            return Response(
                {"detail": "Motor is already OFF or no active session found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        stage = open_log.stage

        with transaction.atomic():
            duration = int((now - open_log.started_at).total_seconds())

            open_log.ended_at = now
            open_log.duration_seconds = duration
            open_log.save(update_fields=["ended_at", "duration_seconds"])

            equipment.status = "INACTIVE"
            equipment.current_state = "OFF"
            equipment.save(update_fields=["status", "current_state", "updated_at"])

            sensors = self._deactivate_sensor(stage) if stage else []

        return Response(
            {
                "id": open_log.id,
                "equipment": {
                    "id": equipment.id,
                    "name": equipment.name,
                    "code": equipment.code,
                    "status": "INACTIVE",
                    "current_state": "OFF",
                },
                "action": "OFF",
                "started_at": open_log.started_at,
                "ended_at": open_log.ended_at,
                "duration_seconds": open_log.duration_seconds,
                "status": "INACTIVE",
                "sensors": sensors,
            },
            status=status.HTTP_200_OK,
        )

    def _deactivate_sensor(self, stage):
        if not stage:
            return []

        sensors = (
            stage.equipments.filter(equipment_type__name__icontains="sensor")
            .exclude(name__icontains="valve")
            .exclude(code__icontains="val")
        )

        deactivated = []

        for sensor in sensors:
            open_log = EquipmentManualLog.objects.filter(
                equipment=sensor, ended_at__isnull=True
            ).first()

            if open_log:
                now = timezone.now()
                open_log.ended_at = now
                open_log.duration_seconds = int(
                    (now - open_log.started_at).total_seconds()
                )
                open_log.save(update_fields=["ended_at", "duration_seconds"])

                sensor.status = "INACTIVE"
                sensor.current_state = "OFF"
                sensor.save(update_fields=["status", "current_state", "updated_at"])

                deactivated.append(
                    {
                        "id": sensor.id,
                        "name": sensor.name,
                        "code": sensor.code,
                        "status": "INACTIVE",
                        "current_state": "OFF",
                        "ended_at": open_log.ended_at,
                        "duration_seconds": open_log.duration_seconds,
                    }
                )

        return deactivated


# ==========================================================
#                     SENSOR LIST VIEW
# ==========================================================
class SensorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        sensors = (
            Equipment.objects.select_related("equipment_type")
            .filter(equipment_type__name__icontains="sensor")
            .exclude(name__icontains="valve")
            .exclude(code__icontains="val")
        )

        stage_id = request.query_params.get("stage_id")
        status_filter = request.query_params.get("status")
        current_state = request.query_params.get("current_state")

        if stage_id:
            sensors = sensors.filter(treatment_stages__id=stage_id)

        if status_filter:
            sensors = sensors.filter(status=status_filter.upper())

        if current_state:
            sensors = sensors.filter(current_state=current_state.upper())

        serializer = EquipmentSerializer(sensors, many=True)

        return Response(
            {
                "success": True,
                "message": "Sensors retrieved successfully.",
                "count": sensors.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#           EQUIPMENT MANUAL LOG BY EQUIPMENT ID
# ==========================================================
class EquipmentManualLogByEquipmentView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, equipment_id):

        # Check equipment exists
        equipment = get_object_or_404(Equipment, id=equipment_id)

        logs = (
            EquipmentManualLog.objects.select_related(
                "equipment", "stage", "performed_by"
            )
            .filter(equipment_id=equipment_id)
            .order_by("-started_at")
        )

        action = request.query_params.get("action")
        stage_id = request.query_params.get("stage_id")

        if action:
            logs = logs.filter(action=action.upper())

        if stage_id:
            logs = logs.filter(stage_id=stage_id)

        data = []
        for log in logs:
            data.append(
                {
                    "id": log.id,
                    "equipment": {
                        "id": log.equipment.id,
                        "name": log.equipment.name,
                        "code": log.equipment.code,
                    },
                    "stage": log.stage.name if log.stage else None,
                    "action": log.action,
                    "started_at": log.started_at,
                    "ended_at": log.ended_at,
                    "duration_seconds": log.duration_seconds,
                    "performed_by": getattr(
                        log.performed_by, "username", str(log.performed_by)
                    ),
                    "created_at": log.created_at,
                }
            )

        return Response(
            {
                "success": True,
                "message": "Equipment manual logs retrieved successfully.",
                "equipment": {
                    "id": equipment.id,
                    "name": equipment.name,
                    "code": equipment.code,
                },
                "count": len(data),
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


class StageEquipmentsDurationView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, stage_id):

        stage = get_object_or_404(TreatmentStage, id=stage_id)

        equipments = stage.equipments.select_related("equipment_type").all()

        data = []

        for eq in equipments:

            latest_log = (
                EquipmentManualLog.objects.filter(equipment_id=eq.id, action="ON")
                .order_by("-started_at")
                .first()
            )

            duration_seconds = 0
            is_running = False
            started_at = None
            ended_at = None

            if latest_log:

                started_at = latest_log.started_at
                ended_at = latest_log.ended_at

                if latest_log.ended_at is None:

                    duration_seconds = int(
                        (timezone.now() - latest_log.started_at).total_seconds()
                    )

                    is_running = True

                else:

                    duration_seconds = latest_log.duration_seconds or 0

                    is_running = False

                    self.create_or_update_equipment_test(
                        equipment=eq,
                        stage=stage,
                        manual_log=latest_log,
                        user=request.user,
                    )

            data.append(
                {
                    "id": eq.id,
                    "name": eq.name,
                    "code": eq.code,
                    "equipment_type": (
                        eq.equipment_type.name if eq.equipment_type else None
                    ),
                    "current_state": eq.current_state,
                    "status": eq.status,
                    "is_running": is_running,
                    "latest_duration_seconds": duration_seconds,
                    "started_at": started_at,
                    "ended_at": ended_at,
                }
            )

        return Response(
            {
                "success": True,
                "message": (
                    "Equipment durations under stage " "retrieved successfully."
                ),
                "stage": {
                    "id": stage.id,
                    "name": stage.name,
                },
                "count": len(data),
                "data": data,
            },
            status=status.HTTP_200_OK,
        )

    # ==========================================================
    # CREATE / UPDATE EQUIPMENT TEST
    # ==========================================================

    def create_or_update_equipment_test(self, equipment, stage, manual_log, user):

        test, created = EquipmentTest.objects.get_or_create(
            equipment=equipment,
            stage=stage,
            tested_by=user,
            start_time=manual_log.started_at,
            defaults={
                "end_time": manual_log.ended_at,
                "duration_seconds": (manual_log.duration_seconds or 0),
                "status": "COMPLETED",
                "is_merged": False,
            },
        )

        if not created:

            test.end_time = manual_log.ended_at

            test.duration_seconds = manual_log.duration_seconds or 0

            test.status = "COMPLETED"

            test.save(
                update_fields=[
                    "end_time",
                    "duration_seconds",
                    "status",
                    "updated_at",
                ]
            )

        return test
