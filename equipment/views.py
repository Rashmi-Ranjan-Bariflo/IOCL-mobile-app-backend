from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import (
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

        # Check if already ON
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
            equipment.is_active = True
            equipment.start_time = now.time()
            equipment.save(
                update_fields=["status", "is_active", "start_time", "updated_at"]
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
            equipment.is_active = False
            equipment.end_time = now.time()
            equipment.duration_seconds = duration
            equipment.save(
                update_fields=[
                    "status",
                    "is_active",
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

        # Validate Motor
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

        # ==========================================================
        # RULE: Valve of the SAME STAGE must be ON
        # ==========================================================
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

        # Check if Motor is already ON
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
            equipment.is_active = True
            equipment.save(update_fields=["status", "is_active", "updated_at"])

            # Activate only sensors of this stage
            sensors = self._activate_sensor(stage, request.user)

        return Response(
            {
                "id": log.id,
                "equipment": {
                    "id": equipment.id,
                    "name": equipment.name,
                    "code": equipment.code,
                    "status": "ACTIVE",
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
            stage.equipments.filter(equipment_type__name__iexact="Sensor")
            .exclude(name__icontains="valve")
            .exclude(code__icontains="valv")
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
            sensor.is_active = True
            sensor.save(update_fields=["status", "is_active", "updated_at"])

            activated.append(
                {
                    "id": sensor.id,
                    "name": sensor.name,
                    "code": sensor.code,
                    "status": "ACTIVE",
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
            equipment.is_active = False
            equipment.save(update_fields=["status", "is_active", "updated_at"])

            # Deactivate only sensors of this stage
            sensors = self._deactivate_sensor(stage)

        return Response(
            {
                "id": open_log.id,
                "equipment": {
                    "id": equipment.id,
                    "name": equipment.name,
                    "code": equipment.code,
                    "status": "INACTIVE",
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
            stage.equipments.filter(equipment_type__name__iexact="Sensor")
            .exclude(name__icontains="valve")
            .exclude(code__icontains="valv")
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
                sensor.is_active = False
                sensor.save(update_fields=["status", "is_active", "updated_at"])

                deactivated.append(
                    {
                        "id": sensor.id,
                        "name": sensor.name,
                        "code": sensor.code,
                        "status": "INACTIVE",
                        "ended_at": open_log.ended_at,
                        "duration_seconds": open_log.duration_seconds,
                    }
                )

        return deactivated
