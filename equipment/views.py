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

        # --------------------------------------------------
        # GET EQUIPMENT
        # --------------------------------------------------
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )

        # --------------------------------------------------
        # CHECK EQUIPMENT TYPE
        # --------------------------------------------------
        if not equipment.equipment_type:
            return Response(
                {"detail": "Equipment type is not configured."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "valve" not in equipment.equipment_type.name.lower():
            return Response(
                {
                    "detail": (
                        f"This equipment is not a Valve. "
                        f"Current type: {equipment.equipment_type.name}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EquipmentOnOffSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        stage_id = serializer.validated_data.get("stage_id")
        process_id = serializer.validated_data.get("process_id")

        # --------------------------------------------------
        # GET STAGE
        # --------------------------------------------------
        stage = None

        if stage_id:

            stage = get_object_or_404(
                TreatmentStage,
                id=stage_id,
            )

            if process_id:
                get_object_or_404(
                    TreatmentProcess,
                    id=process_id,
                    stage=stage,
                )

        if equipment.current_state == "ON":

            # Get latest ON log only for response information
            latest_on_log = (
                EquipmentManualLog.objects.filter(
                    equipment=equipment,
                    action="ON",
                )
                .order_by("-started_at", "-id")
                .first()
            )

            return Response(
                {
                    "detail": "Valve is already ON",
                    "log_id": (latest_on_log.id if latest_on_log else None),
                    "start_time": (
                        latest_on_log.started_at
                        if latest_on_log
                        else equipment.start_time
                    ),
                    "status": "ACTIVE",
                    "current_state": "ON",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # VALVE IS OFF
        # ==================================================

        # If current_state is OFF, create a NEW ON log.

        now = timezone.now()

        with transaction.atomic():

            # --------------------------------------------------
            # CREATE NEW ON LOG
            # --------------------------------------------------
            log = EquipmentManualLog.objects.create(
                equipment=equipment,
                stage=stage,
                action="ON",
                started_at=now,
                performed_by=request.user,
            )

            # --------------------------------------------------
            # UPDATE EQUIPMENT CURRENT STATE
            # --------------------------------------------------
            equipment.status = "ACTIVE"
            equipment.current_state = "ON"
            equipment.start_time = now.time()

            equipment.save(
                update_fields=[
                    "status",
                    "current_state",
                    "start_time",
                    "updated_at",
                ]
            )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------
        return Response(
            {
                "success": True,
                "message": "Valve turned ON successfully",
                "data": {
                    "log_id": log.id,
                    "equipment_id": equipment.id,
                    "equipment_name": equipment.name,
                    "equipment_code": equipment.code,
                    "equipment_type": (
                        equipment.equipment_type.name
                        if equipment.equipment_type
                        else None
                    ),
                    "action": "ON",
                    "status": "ACTIVE",
                    "current_state": "ON",
                    "start_time": log.started_at,
                    "ended_at": None,
                    "duration_seconds": None,
                    "stage": (
                        {
                            "id": stage.id,
                            "name": stage.name,
                        }
                        if stage
                        else None
                    ),
                    "performed_by": request.user.id,
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

            # ------------------------------------------------------
            # CREATE NEW OFF LOG
            # ------------------------------------------------------
            off_log = EquipmentManualLog.objects.create(
                equipment=equipment,
                stage=open_log.stage,
                action="OFF",
                started_at=now,
                ended_at=now,
                duration_seconds=duration,
                performed_by=request.user,
            )

            # ------------------------------------------------------
            # UPDATE EQUIPMENT STATE
            # ------------------------------------------------------
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
                "id": off_log.id,
                "equipment": {
                    "id": equipment.id,
                    "name": equipment.name,
                    "code": equipment.code,
                    "status": "INACTIVE",
                    "current_state": "OFF",
                },
                "action": "OFF",
                "started_at": off_log.started_at,
                "ended_at": off_log.ended_at,
                "duration_seconds": off_log.duration_seconds,
                "status": "INACTIVE",
                "previous_on_log_id": open_log.id,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                        MOTOR ON
# ==========================================================
class MotorOnView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, equipment_id):

        # --------------------------------------------------
        # GET EQUIPMENT
        # --------------------------------------------------
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )

        # --------------------------------------------------
        # CHECK EQUIPMENT TYPE
        # --------------------------------------------------
        if not equipment.equipment_type:
            return Response(
                {"detail": "Equipment type is not configured."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        equipment_type = equipment.equipment_type.name.lower()

        if "motor" not in equipment_type and "pump" not in equipment_type:
            return Response(
                {
                    "detail": (
                        f"This equipment is not a Motor. "
                        f"Current type: {equipment.equipment_type.name}"
                    )
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

        # --------------------------------------------------
        # GET STAGE
        # --------------------------------------------------
        stage = get_object_or_404(
            TreatmentStage,
            id=stage_id,
        )

        if equipment.current_state == "ON":

            latest_on_log = (
                EquipmentManualLog.objects.filter(
                    equipment=equipment,
                    action="ON",
                )
                .order_by("-started_at", "-id")
                .first()
            )

            return Response(
                {
                    "detail": "Motor is already ON",
                    "log_id": (latest_on_log.id if latest_on_log else None),
                    "started_at": (latest_on_log.started_at if latest_on_log else None),
                    "status": "ACTIVE",
                    "current_state": "ON",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        stage_valves = stage.equipments.filter(equipment_type__name__icontains="valve")

        valve_is_on = False

        for valve in stage_valves:

            if valve.current_state == "ON":
                valve_is_on = True
                break

        if not valve_is_on:
            return Response(
                {
                    "detail": (
                        "Cannot turn Motor ON. " "Valve of this stage is not ON."
                    ),
                    "stage": stage.name,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # MOTOR IS OFF
        # ==================================================

        now = timezone.now()

        with transaction.atomic():

            # --------------------------------------------------
            # CREATE MOTOR ON LOG
            # --------------------------------------------------
            log = EquipmentManualLog.objects.create(
                equipment=equipment,
                stage=stage,
                action="ON",
                started_at=now,
                performed_by=request.user,
            )

            # --------------------------------------------------
            # UPDATE MOTOR STATE
            # --------------------------------------------------
            equipment.status = "ACTIVE"
            equipment.current_state = "ON"
            equipment.start_time = now.time()

            equipment.save(
                update_fields=[
                    "status",
                    "current_state",
                    "start_time",
                    "updated_at",
                ]
            )

            # --------------------------------------------------
            # AUTOMATICALLY ACTIVATE SENSORS
            # --------------------------------------------------
            sensors = self._activate_sensor(
                stage=stage,
                user=request.user,
            )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------
        return Response(
            {
                "success": True,
                "message": "Motor turned ON successfully",
                "data": {
                    "log_id": log.id,
                    "equipment": {
                        "id": equipment.id,
                        "name": equipment.name,
                        "code": equipment.code,
                        "equipment_type": (
                            equipment.equipment_type.name
                            if equipment.equipment_type
                            else None
                        ),
                        "status": "ACTIVE",
                        "current_state": "ON",
                    },
                    "action": "ON",
                    "started_at": log.started_at,
                    "ended_at": None,
                    "duration_seconds": None,
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
                    "performed_by": request.user.id,
                    "sensors": sensors,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    # ==========================================================
    #                  ACTIVATE SENSORS
    # ==========================================================
    def _activate_sensor(self, stage, user):

        # --------------------------------------------------
        # GET SENSORS UNDER SAME STAGE
        # --------------------------------------------------
        sensors = (
            stage.equipments.filter(equipment_type__name__icontains="sensor")
            .exclude(name__icontains="valve")
            .exclude(code__icontains="val")
        )

        activated = []

        # --------------------------------------------------
        # ACTIVATE EACH SENSOR
        # --------------------------------------------------
        for sensor in sensors:

            if sensor.current_state == "ON":
                continue

            # --------------------------------------------------
            # CREATE NEW SENSOR ON LOG
            # --------------------------------------------------
            now = timezone.now()

            log = EquipmentManualLog.objects.create(
                equipment=sensor,
                stage=stage,
                action="ON",
                started_at=now,
                performed_by=user,
            )

            # --------------------------------------------------
            # UPDATE SENSOR STATE
            # --------------------------------------------------
            sensor.status = "ACTIVE"
            sensor.current_state = "ON"
            sensor.start_time = now.time()

            sensor.save(
                update_fields=[
                    "status",
                    "current_state",
                    "start_time",
                    "updated_at",
                ]
            )

            # --------------------------------------------------
            # SENSOR RESPONSE
            # --------------------------------------------------
            activated.append(
                {
                    "log_id": log.id,
                    "id": sensor.id,
                    "name": sensor.name,
                    "code": sensor.code,
                    "equipment_type": (
                        sensor.equipment_type.name if sensor.equipment_type else None
                    ),
                    "action": "ON",
                    "status": "ACTIVE",
                    "current_state": "ON",
                    "started_at": log.started_at,
                    "ended_at": None,
                    "duration_seconds": None,
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
                    "performed_by": user.id,
                }
            )

        return activated


# ==========================================================
#                        MOTOR OFF
# ==========================================================
class MotorOffView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, equipment_id):

        # --------------------------------------------------
        # GET MOTOR
        # --------------------------------------------------
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )

        # --------------------------------------------------
        # CHECK EQUIPMENT TYPE
        # --------------------------------------------------
        if not equipment.equipment_type:
            return Response(
                {"detail": "Equipment type is not configured."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        equipment_type = equipment.equipment_type.name.lower()

        if "motor" not in equipment_type and "pump" not in equipment_type:
            return Response(
                {
                    "detail": (
                        f"This equipment is not a Motor. "
                        f"Current type: {equipment.equipment_type.name}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # FIND LATEST ACTIVE MOTOR ON LOG
        #
        # ON log is never updated with ended_at.
        # Therefore, check that no OFF log exists after it.
        # --------------------------------------------------
        on_logs = EquipmentManualLog.objects.filter(
            equipment=equipment,
            action="ON",
        ).order_by("-started_at")

        open_log = None

        for log in on_logs:

            off_exists = EquipmentManualLog.objects.filter(
                equipment=equipment,
                action="OFF",
                started_at__gte=log.started_at,
            ).exists()

            if not off_exists:
                open_log = log
                break

        # --------------------------------------------------
        # NO ACTIVE SESSION
        # --------------------------------------------------
        if not open_log:
            return Response(
                {"detail": "Motor is already OFF or no active session found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # CURRENT TIME
        # --------------------------------------------------
        now = timezone.now()

        stage = open_log.stage

        # --------------------------------------------------
        # CALCULATE MOTOR DURATION
        # --------------------------------------------------
        duration = int((now - open_log.started_at).total_seconds())

        with transaction.atomic():

            # ==================================================
            # CREATE NEW MOTOR OFF LOG
            # ==================================================
            off_log = EquipmentManualLog.objects.create(
                equipment=equipment,
                stage=stage,
                action="OFF",
                started_at=now,
                ended_at=now,
                duration_seconds=duration,
                performed_by=request.user,
            )

            # --------------------------------------------------
            # UPDATE MOTOR CURRENT STATE
            # --------------------------------------------------
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

            # --------------------------------------------------
            # DEACTIVATE SENSORS
            # --------------------------------------------------
            sensors = (
                self._deactivate_sensor(
                    stage=stage,
                    performed_by=request.user,
                )
                if stage
                else []
            )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------
        return Response(
            {
                "success": True,
                "message": "Motor turned OFF successfully.",
                "data": {
                    "log_id": off_log.id,
                    "previous_on_log_id": open_log.id,
                    "equipment": {
                        "id": equipment.id,
                        "name": equipment.name,
                        "code": equipment.code,
                        "equipment_type": (
                            equipment.equipment_type.name
                            if equipment.equipment_type
                            else None
                        ),
                        "status": "INACTIVE",
                        "current_state": "OFF",
                    },
                    "action": "OFF",
                    # Original ON time
                    "started_at": open_log.started_at,
                    # Motor OFF time
                    "ended_at": off_log.ended_at,
                    "duration_seconds": duration,
                    "stage": (
                        {
                            "id": stage.id,
                            "name": stage.name,
                        }
                        if stage
                        else None
                    ),
                    "performed_by": request.user.id,
                    "sensors": sensors,
                },
            },
            status=status.HTTP_200_OK,
        )

    # ==========================================================
    #                  DEACTIVATE SENSORS
    # ==========================================================
    def _deactivate_sensor(self, stage, performed_by):

        if not stage:
            return []

        # --------------------------------------------------
        # GET SENSORS UNDER THE SAME STAGE
        # --------------------------------------------------
        sensors = (
            stage.equipments.filter(equipment_type__name__icontains="sensor")
            .exclude(name__icontains="valve")
            .exclude(code__icontains="val")
        )

        deactivated = []

        # --------------------------------------------------
        # PROCESS EACH SENSOR
        # --------------------------------------------------
        for sensor in sensors:

            # --------------------------------------------------
            # FIND LATEST SENSOR ON LOG
            #
            # ON log remains unchanged.
            # Check whether an OFF log already exists.
            # --------------------------------------------------
            on_logs = EquipmentManualLog.objects.filter(
                equipment=sensor,
                action="ON",
            ).order_by("-started_at")

            open_log = None

            for log in on_logs:

                off_exists = EquipmentManualLog.objects.filter(
                    equipment=sensor,
                    action="OFF",
                    started_at__gte=log.started_at,
                ).exists()

                if not off_exists:
                    open_log = log
                    break

            # --------------------------------------------------
            # SENSOR IS ALREADY OFF
            # --------------------------------------------------
            if not open_log:
                continue

            # --------------------------------------------------
            # SENSOR OFF TIME
            # --------------------------------------------------
            now = timezone.now()

            # --------------------------------------------------
            # SENSOR DURATION
            # --------------------------------------------------
            duration = int((now - open_log.started_at).total_seconds())

            # ==================================================
            # CREATE NEW SENSOR OFF LOG
            # ==================================================
            off_log = EquipmentManualLog.objects.create(
                equipment=sensor,
                stage=stage,
                action="OFF",
                started_at=now,
                ended_at=now,
                duration_seconds=duration,
                performed_by=performed_by,
            )

            # --------------------------------------------------
            # UPDATE SENSOR STATE
            # --------------------------------------------------
            sensor.status = "INACTIVE"
            sensor.current_state = "OFF"
            sensor.end_time = now.time()
            sensor.duration_seconds = duration

            sensor.save(
                update_fields=[
                    "status",
                    "current_state",
                    "end_time",
                    "duration_seconds",
                    "updated_at",
                ]
            )

            # --------------------------------------------------
            # ADD SENSOR RESPONSE
            # --------------------------------------------------
            deactivated.append(
                {
                    "log_id": off_log.id,
                    "previous_on_log_id": open_log.id,
                    "id": sensor.id,
                    "name": sensor.name,
                    "code": sensor.code,
                    "status": "INACTIVE",
                    "current_state": "OFF",
                    "action": "OFF",
                    # Original sensor ON time
                    "started_at": open_log.started_at,
                    # Sensor OFF time
                    "ended_at": off_log.ended_at,
                    "duration_seconds": duration,
                    "performed_by": performed_by.id,
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

        # --------------------------------------------------
        # CHECK EQUIPMENT EXISTS
        # --------------------------------------------------
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )

        # --------------------------------------------------
        # GET MANUAL LOGS
        # --------------------------------------------------
        logs = (
            EquipmentManualLog.objects.select_related(
                "equipment",
                "equipment__equipment_type",
                "stage",
                "performed_by",
            )
            .filter(equipment_id=equipment_id)
            .order_by("-started_at")
        )

        action = request.query_params.get("action")

        if action:
            logs = logs.filter(action=action.upper())

        stage_id = request.query_params.get("stage_id")

        if stage_id:
            logs = logs.filter(stage_id=stage_id)

        # --------------------------------------------------
        # PREPARE RESPONSE
        # --------------------------------------------------
        data = []

        for log in logs:

            # ==================================================
            # ON LOG
            # ==================================================
            if log.action == "ON":

                data.append(
                    {
                        "id": log.id,
                        "equipment": {
                            "id": log.equipment.id,
                            "name": log.equipment.name,
                            "code": log.equipment.code,
                            "equipment_type": (
                                log.equipment.equipment_type.name
                                if log.equipment.equipment_type
                                else None
                            ),
                        },
                        "stage": (
                            {
                                "id": log.stage.id,
                                "name": log.stage.name,
                            }
                            if log.stage
                            else None
                        ),
                        "action": "ON",
                        # ON time
                        "on_time": log.started_at,
                        # ON log does not have OFF time
                        "off_time": None,
                        "started_at": log.started_at,
                        "ended_at": None,
                        # ON log has no duration
                        "duration_seconds": None,
                        "performed_by": getattr(
                            log.performed_by,
                            "username",
                            str(log.performed_by),
                        ),
                        "created_at": log.created_at,
                    }
                )

            # ==================================================
            # OFF LOG
            # ==================================================
            else:
                previous_on_log = (
                    EquipmentManualLog.objects.filter(
                        equipment_id=log.equipment_id,
                        action="ON",
                        started_at__lt=log.started_at,
                    )
                    .order_by("-started_at")
                    .first()
                )

                data.append(
                    {
                        "id": log.id,
                        "equipment": {
                            "id": log.equipment.id,
                            "name": log.equipment.name,
                            "code": log.equipment.code,
                            "equipment_type": (
                                log.equipment.equipment_type.name
                                if log.equipment.equipment_type
                                else None
                            ),
                        },
                        "stage": (
                            {
                                "id": log.stage.id,
                                "name": log.stage.name,
                            }
                            if log.stage
                            else None
                        ),
                        "action": "OFF",
                        # Original ON log
                        "previous_on_log_id": (
                            previous_on_log.id if previous_on_log else None
                        ),
                        # Actual ON time
                        "on_time": (
                            previous_on_log.started_at if previous_on_log else None
                        ),
                        # Actual OFF time
                        "off_time": log.ended_at,
                        "started_at": log.started_at,
                        "ended_at": log.ended_at,
                        # Duration between ON and OFF
                        "duration_seconds": log.duration_seconds,
                        "performed_by": getattr(
                            log.performed_by,
                            "username",
                            str(log.performed_by),
                        ),
                        "created_at": log.created_at,
                    }
                )

        # --------------------------------------------------
        # CURRENT EQUIPMENT STATE
        # --------------------------------------------------
        current_state = equipment.current_state
        equipment_status = equipment.status

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------
        return Response(
            {
                "success": True,
                "message": ("Equipment manual logs retrieved successfully."),
                "equipment": {
                    "id": equipment.id,
                    "name": equipment.name,
                    "code": equipment.code,
                    "equipment_type": (
                        equipment.equipment_type.name
                        if equipment.equipment_type
                        else None
                    ),
                    "status": equipment_status,
                    "current_state": current_state,
                    "is_running": (current_state == "ON"),
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
