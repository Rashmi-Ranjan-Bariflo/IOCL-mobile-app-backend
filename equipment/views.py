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

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Equipment, EquipmentManualLog, EquipmentTest
from .serializers import EquipmentOnOffSerializer, EquipmentSerializer
from treatment_process.models import (
    TreatmentStage,
    TreatmentProcess,
    StageEquipmentConfig,
)


class ValveOnView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, equipment_id):
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )
        if not equipment.equipment_type:
            return Response(
                {"detail": "Equipment type is not configured."},
                status=status.HTTP_400_BAD_REQUEST,
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
        if not stage_id:
            return Response(
                {"detail": "stage_id is required for Valve ON."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        stage = get_object_or_404(TreatmentStage, id=stage_id)
        if process_id:
            get_object_or_404(
                TreatmentProcess,
                id=process_id,
                stage=stage,
            )
        config, created = StageEquipmentConfig.objects.get_or_create(
            equipment=equipment,
            stage=stage,
            defaults={
                "current_state": "OFF",
                "status": "ACTIVE",
                "is_active": True,
            },
        )
        if config.current_state == "ON":
            open_log = (
                EquipmentManualLog.objects.filter(
                    equipment=equipment,
                    stage=stage,
                    action="ON",
                    ended_at__isnull=True,
                )
                .order_by("-started_at", "-id")
                .first()
            )
            return Response(
                {
                    "success": False,
                    "detail": "Valve is already ON.",
                    "data": {
                        "config_id": config.id,
                        "log_id": open_log.id if open_log else None,
                        "equipment_id": equipment.id,
                        "equipment_name": equipment.name,
                        "equipment_code": equipment.code,
                        "action": "ON",
                        "current_state": config.current_state,
                        "status": config.status,
                        "stage": {
                            "id": stage.id,
                            "name": stage.name,
                        },
                    },
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
            config.current_state = "ON"
            config.save(
                update_fields=[
                    "current_state",
                    "updated_at",
                ]
            )
        return Response(
            {
                "success": True,
                "message": "Valve turned ON successfully.",
                "data": {
                    "config_id": config.id,
                    "log_id": log.id,
                    "equipment": {
                        "id": equipment.id,
                        "name": equipment.name,
                        "code": equipment.code,
                        "equipment_type": equipment.equipment_type.name,
                    },
                    "action": "ON",
                    "current_state": config.current_state,
                    "status": config.status,
                    "started_at": log.started_at,
                    "ended_at": log.ended_at,
                    "duration_seconds": log.duration_seconds,
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
                    "performed_by": request.user.id,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class ValveOffView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, equipment_id):
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )
        if not equipment.equipment_type:
            return Response(
                {"detail": "Equipment type is not configured."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "valve" not in equipment.equipment_type.name.lower():
            return Response(
                {
                    "detail": f"This equipment is not a Valve. Current type: {equipment.equipment_type.name}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        stage_id = request.data.get("stage_id")
        if not stage_id:
            return Response(
                {"detail": "stage_id is required for Valve OFF."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        stage = get_object_or_404(
            TreatmentStage,
            id=stage_id,
        )
        config = StageEquipmentConfig.objects.filter(
            equipment=equipment,
            stage=stage,
            is_active=True,
        ).first()
        if not config:
            return Response(
                {
                    "success": False,
                    "detail": "StageEquipmentConfig does not exist for this valve and stage.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if config.current_state == "OFF":
            return Response(
                {
                    "success": False,
                    "detail": "Valve is already OFF.",
                    "data": {
                        "config_id": config.id,
                        "equipment_id": equipment.id,
                        "stage_id": stage.id,
                        "current_state": config.current_state,
                        "status": config.status,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        open_log = (
            EquipmentManualLog.objects.filter(
                equipment=equipment,
                stage=stage,
                action="ON",
                ended_at__isnull=True,
            )
            .order_by("-started_at", "-id")
            .first()
        )
        if not open_log:
            return Response(
                {
                    "success": False,
                    "detail": "No active ON log found for this valve.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        now = timezone.now()
        duration = max(
            0,
            int((now - open_log.started_at).total_seconds()),
        )
        with transaction.atomic():
            open_log.ended_at = now
            open_log.duration_seconds = duration
            open_log.save(
                update_fields=[
                    "ended_at",
                    "duration_seconds",
                ]
            )
            off_log = EquipmentManualLog.objects.create(
                equipment=equipment,
                stage=stage,
                action="OFF",
                started_at=now,
                ended_at=now,
                duration_seconds=duration,
                performed_by=request.user,
            )
            config.current_state = "OFF"
            config.save(
                update_fields=[
                    "current_state",
                    "updated_at",
                ]
            )
        return Response(
            {
                "success": True,
                "message": "Valve turned OFF successfully.",
                "data": {
                    "config_id": config.id,
                    "log_id": off_log.id,
                    "previous_on_log_id": open_log.id,
                    "equipment": {
                        "id": equipment.id,
                        "name": equipment.name,
                        "code": equipment.code,
                        "equipment_type": equipment.equipment_type.name,
                    },
                    "action": "OFF",
                    "current_state": config.current_state,
                    "status": config.status,
                    "started_at": open_log.started_at,
                    "ended_at": off_log.ended_at,
                    "duration_seconds": duration,
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
                    "performed_by": request.user.id,
                },
            },
            status=status.HTTP_200_OK,
        )


class MotorOnView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, equipment_id):
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )
        if not equipment.equipment_type:
            return Response(
                {"detail": "Equipment type is not configured."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        equipment_type = equipment.equipment_type.name.lower()
        if "motor" not in equipment_type and "pump" not in equipment_type:
            return Response(
                {
                    "detail": f"This equipment is not a Motor/Pump. Current type: {equipment.equipment_type.name}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = EquipmentOnOffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stage_id = serializer.validated_data.get("stage_id")
        if not stage_id:
            return Response(
                {"detail": "stage_id is required for Motor ON."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        stage = get_object_or_404(
            TreatmentStage,
            id=stage_id,
        )
        config, created = StageEquipmentConfig.objects.get_or_create(
            equipment=equipment,
            stage=stage,
            defaults={
                "current_state": "OFF",
                "status": "ACTIVE",
                "is_active": True,
            },
        )
        if config.current_state == "ON":
            open_log = (
                EquipmentManualLog.objects.filter(
                    equipment=equipment,
                    stage=stage,
                    action="ON",
                    ended_at__isnull=True,
                )
                .order_by("-started_at", "-id")
                .first()
            )
            return Response(
                {
                    "success": False,
                    "detail": "Motor is already ON.",
                    "data": {
                        "config_id": config.id,
                        "log_id": open_log.id if open_log else None,
                        "equipment_id": equipment.id,
                        "equipment_name": equipment.name,
                        "equipment_code": equipment.code,
                        "action": "ON",
                        "current_state": config.current_state,
                        "status": config.status,
                        "stage": {
                            "id": stage.id,
                            "name": stage.name,
                        },
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        valve_configs = StageEquipmentConfig.objects.filter(
            stage=stage,
            equipment__equipment_type__name__icontains="valve",
            is_active=True,
        ).select_related(
            "equipment",
            "equipment__equipment_type",
        )
        active_valve = valve_configs.filter(current_state="ON").first()
        if not active_valve:
            return Response(
                {
                    "success": False,
                    "detail": "Cannot turn Motor ON. Valve of this stage is not ON.",
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
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
            config.current_state = "ON"
            config.save(
                update_fields=[
                    "current_state",
                    "updated_at",
                ]
            )
            sensors = self._activate_sensors(
                stage,
                request.user,
            )
        return Response(
            {
                "success": True,
                "message": "Motor turned ON successfully.",
                "data": {
                    "config_id": config.id,
                    "log_id": log.id,
                    "equipment": {
                        "id": equipment.id,
                        "name": equipment.name,
                        "code": equipment.code,
                        "equipment_type": equipment.equipment_type.name,
                    },
                    "action": "ON",
                    "current_state": config.current_state,
                    "status": config.status,
                    "started_at": log.started_at,
                    "ended_at": log.ended_at,
                    "duration_seconds": log.duration_seconds,
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
                    "performed_by": request.user.id,
                    "valve": {
                        "config_id": active_valve.id,
                        "equipment_id": active_valve.equipment.id,
                        "name": active_valve.equipment.name,
                        "current_state": active_valve.current_state,
                    },
                    "sensors": sensors,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    def _activate_sensors(self, stage, user):
        sensors = (
            stage.equipments.filter(equipment_type__name__icontains="sensor")
            .exclude(name__icontains="valve")
            .exclude(code__icontains="val")
        )
        activated = []
        for sensor in sensors:
            config, created = StageEquipmentConfig.objects.get_or_create(
                equipment=sensor,
                stage=stage,
                defaults={
                    "current_state": "OFF",
                    "status": "ACTIVE",
                    "is_active": True,
                },
            )
            if config.current_state == "ON":
                continue
            now = timezone.now()
            log = EquipmentManualLog.objects.create(
                equipment=sensor,
                stage=stage,
                action="ON",
                started_at=now,
                performed_by=user,
            )
            config.current_state = "ON"
            config.save(
                update_fields=[
                    "current_state",
                    "updated_at",
                ]
            )
            activated.append(
                {
                    "config_id": config.id,
                    "log_id": log.id,
                    "equipment_id": sensor.id,
                    "name": sensor.name,
                    "code": sensor.code,
                    "equipment_type": (
                        sensor.equipment_type.name if sensor.equipment_type else None
                    ),
                    "action": "ON",
                    "current_state": config.current_state,
                    "status": config.status,
                    "started_at": log.started_at,
                    "ended_at": log.ended_at,
                    "duration_seconds": log.duration_seconds,
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
                    "performed_by": user.id,
                }
            )
        return activated


class MotorOffView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, equipment_id):
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )
        if not equipment.equipment_type:
            return Response(
                {"detail": "Equipment type is not configured."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        equipment_type = equipment.equipment_type.name.lower()
        if "motor" not in equipment_type and "pump" not in equipment_type:
            return Response(
                {
                    "detail": f"This equipment is not a Motor/Pump. Current type: {equipment.equipment_type.name}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        stage_id = request.data.get("stage_id")
        if not stage_id:
            return Response(
                {"detail": "stage_id is required for Motor OFF."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        stage = get_object_or_404(
            TreatmentStage,
            id=stage_id,
        )
        config = StageEquipmentConfig.objects.filter(
            equipment=equipment,
            stage=stage,
            is_active=True,
        ).first()
        if not config:
            return Response(
                {
                    "success": False,
                    "detail": "StageEquipmentConfig does not exist for this motor and stage.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if config.current_state == "OFF":
            return Response(
                {
                    "success": False,
                    "detail": "Motor is already OFF.",
                    "data": {
                        "config_id": config.id,
                        "equipment_id": equipment.id,
                        "stage_id": stage.id,
                        "current_state": config.current_state,
                        "status": config.status,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        open_log = (
            EquipmentManualLog.objects.filter(
                equipment=equipment,
                stage=stage,
                action="ON",
                ended_at__isnull=True,
            )
            .order_by("-started_at", "-id")
            .first()
        )
        if not open_log:
            return Response(
                {
                    "success": False,
                    "detail": "No active ON log found for this motor.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        now = timezone.now()
        duration = max(
            0,
            int((now - open_log.started_at).total_seconds()),
        )
        with transaction.atomic():
            open_log.ended_at = now
            open_log.duration_seconds = duration
            open_log.save(
                update_fields=[
                    "ended_at",
                    "duration_seconds",
                ]
            )
            off_log = EquipmentManualLog.objects.create(
                equipment=equipment,
                stage=stage,
                action="OFF",
                started_at=now,
                ended_at=now,
                duration_seconds=duration,
                performed_by=request.user,
            )
            config.current_state = "OFF"
            config.save(
                update_fields=[
                    "current_state",
                    "updated_at",
                ]
            )
            sensors = self._deactivate_sensors(
                stage,
                request.user,
            )
        return Response(
            {
                "success": True,
                "message": "Motor turned OFF successfully.",
                "data": {
                    "config_id": config.id,
                    "log_id": off_log.id,
                    "previous_on_log_id": open_log.id,
                    "equipment": {
                        "id": equipment.id,
                        "name": equipment.name,
                        "code": equipment.code,
                        "equipment_type": equipment.equipment_type.name,
                    },
                    "action": "OFF",
                    "current_state": config.current_state,
                    "status": config.status,
                    "started_at": open_log.started_at,
                    "ended_at": off_log.ended_at,
                    "duration_seconds": duration,
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
                    "performed_by": request.user.id,
                    "sensors": sensors,
                },
            },
            status=status.HTTP_200_OK,
        )

    def _deactivate_sensors(self, stage, performed_by):
        sensors = (
            stage.equipments.filter(equipment_type__name__icontains="sensor")
            .exclude(name__icontains="valve")
            .exclude(code__icontains="val")
        )
        deactivated = []
        for sensor in sensors:
            config = StageEquipmentConfig.objects.filter(
                equipment=sensor,
                stage=stage,
                is_active=True,
            ).first()
            if not config:
                continue
            if config.current_state == "OFF":
                continue
            open_log = (
                EquipmentManualLog.objects.filter(
                    equipment=sensor,
                    stage=stage,
                    action="ON",
                    ended_at__isnull=True,
                )
                .order_by("-started_at", "-id")
                .first()
            )
            if not open_log:
                continue
            now = timezone.now()
            duration = max(
                0,
                int((now - open_log.started_at).total_seconds()),
            )
            open_log.ended_at = now
            open_log.duration_seconds = duration
            open_log.save(
                update_fields=[
                    "ended_at",
                    "duration_seconds",
                ]
            )
            off_log = EquipmentManualLog.objects.create(
                equipment=sensor,
                stage=stage,
                action="OFF",
                started_at=now,
                ended_at=now,
                duration_seconds=duration,
                performed_by=performed_by,
            )
            config.current_state = "OFF"
            config.save(
                update_fields=[
                    "current_state",
                    "updated_at",
                ]
            )
            deactivated.append(
                {
                    "config_id": config.id,
                    "log_id": off_log.id,
                    "previous_on_log_id": open_log.id,
                    "equipment_id": sensor.id,
                    "name": sensor.name,
                    "code": sensor.code,
                    "equipment_type": (
                        sensor.equipment_type.name if sensor.equipment_type else None
                    ),
                    "action": "OFF",
                    "current_state": config.current_state,
                    "status": config.status,
                    "started_at": open_log.started_at,
                    "ended_at": off_log.ended_at,
                    "duration_seconds": duration,
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
                    "performed_by": performed_by.id,
                }
            )
        return deactivated


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
        current_state_filter = request.query_params.get("current_state")
        if stage_id:
            sensors = sensors.filter(treatment_stages__id=stage_id)
        configs = StageEquipmentConfig.objects.filter(
            equipment__in=sensors,
            is_active=True,
        ).select_related(
            "equipment",
            "equipment__equipment_type",
            "stage",
        )
        if stage_id:
            configs = configs.filter(stage_id=stage_id)
        if status_filter:
            configs = configs.filter(status=status_filter.upper())
        if current_state_filter:
            configs = configs.filter(current_state=current_state_filter.upper())
        data = []
        for config in configs:
            data.append(
                {
                    "config_id": config.id,
                    "equipment": {
                        "id": config.equipment.id,
                        "name": config.equipment.name,
                        "code": config.equipment.code,
                        "equipment_type": (
                            config.equipment.equipment_type.name
                            if config.equipment.equipment_type
                            else None
                        ),
                    },
                    "stage": {
                        "id": config.stage.id,
                        "name": config.stage.name,
                    },
                    "current_state": config.current_state,
                    "status": config.status,
                    "start_time": config.start_time,
                    "end_time": config.end_time,
                    "duration_seconds": config.duration_seconds,
                    "is_active": config.is_active,
                }
            )
        return Response(
            {
                "success": True,
                "message": "Sensors retrieved successfully.",
                "count": len(data),
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


class EquipmentManualLogByEquipmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, equipment_id):
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )
        logs = (
            EquipmentManualLog.objects.select_related(
                "equipment",
                "equipment__equipment_type",
                "stage",
                "performed_by",
            )
            .filter(equipment_id=equipment_id)
            .order_by("-started_at", "-id")
        )
        action = request.query_params.get("action")
        stage_id = request.query_params.get("stage_id")
        if action:
            logs = logs.filter(action=action.upper())
        if stage_id:
            logs = logs.filter(stage_id=stage_id)
        data = []
        for log in logs:
            previous_on_log = None
            if log.action == "OFF":
                previous_on_log = (
                    EquipmentManualLog.objects.filter(
                        equipment_id=log.equipment_id,
                        stage=log.stage,
                        action="ON",
                        started_at__lt=log.started_at,
                    )
                    .order_by("-started_at", "-id")
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
                    "action": log.action,
                    "previous_on_log_id": (
                        previous_on_log.id if previous_on_log else None
                    ),
                    "on_time": (
                        previous_on_log.started_at
                        if previous_on_log
                        else (log.started_at if log.action == "ON" else None)
                    ),
                    "off_time": log.ended_at if log.action == "OFF" else None,
                    "started_at": log.started_at,
                    "ended_at": log.ended_at,
                    "duration_seconds": log.duration_seconds,
                    "performed_by": getattr(
                        log.performed_by, "username", str(log.performed_by)
                    ),
                    "created_at": log.created_at,
                }
            )
        config = (
            StageEquipmentConfig.objects.filter(
                equipment=equipment,
                is_active=True,
            )
            .order_by("-id")
            .first()
        )
        return Response(
            {
                "success": True,
                "message": "Equipment manual logs retrieved successfully.",
                "equipment": {
                    "id": equipment.id,
                    "name": equipment.name,
                    "code": equipment.code,
                    "equipment_type": (
                        equipment.equipment_type.name
                        if equipment.equipment_type
                        else None
                    ),
                },
                "current_state": config.current_state if config else "OFF",
                "status": config.status if config else "INACTIVE",
                "is_running": config.current_state == "ON" if config else False,
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
            config = StageEquipmentConfig.objects.filter(
                equipment=eq,
                stage=stage,
                is_active=True,
            ).first()
            current_state = config.current_state if config else "OFF"
            equipment_status = config.status if config else "INACTIVE"
            latest_log = (
                EquipmentManualLog.objects.filter(
                    equipment=eq,
                    stage=stage,
                    action="ON",
                )
                .order_by("-started_at", "-id")
                .first()
            )
            duration_seconds = 0
            started_at = None
            ended_at = None
            is_running = current_state == "ON"
            if latest_log:
                started_at = latest_log.started_at
                ended_at = latest_log.ended_at
                if current_state == "ON" and latest_log.ended_at is None:
                    duration_seconds = max(
                        0, int((timezone.now() - latest_log.started_at).total_seconds())
                    )
                else:
                    duration_seconds = latest_log.duration_seconds or 0
            data.append(
                {
                    "id": eq.id,
                    "name": eq.name,
                    "code": eq.code,
                    "equipment_type": (
                        eq.equipment_type.name if eq.equipment_type else None
                    ),
                    "current_state": current_state,
                    "status": equipment_status,
                    "is_running": is_running,
                    "latest_duration_seconds": duration_seconds,
                    "started_at": started_at,
                    "ended_at": ended_at,
                }
            )
        return Response(
            {
                "success": True,
                "message": "Equipment durations under stage retrieved successfully.",
                "stage": {"id": stage.id, "name": stage.name},
                "count": len(data),
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#          COAGULANT DOSING - MOTOR ON
# ==========================================================


class CoagulantDosingMotorOnView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, equipment_id):

        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )

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
                        "This equipment is not a Motor/Pump. "
                        f"Current type: {equipment.equipment_type.name}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        stage_id = request.data.get("stage_id")

        if not stage_id:
            return Response(
                {"detail": "stage_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stage = get_object_or_404(TreatmentStage, id=stage_id)

        config, created = StageEquipmentConfig.objects.get_or_create(
            equipment=equipment,
            stage=stage,
            defaults={
                "current_state": "OFF",
                "status": "INACTIVE",
                "is_active": True,
            },
        )

        if config.current_state == "ON":

            latest_on_log = (
                EquipmentManualLog.objects.filter(
                    equipment=equipment,
                    stage=stage,
                    action="ON",
                )
                .order_by("-started_at", "-id")
                .first()
            )

            return Response(
                {
                    "success": False,
                    "detail": "Motor is already ON.",
                    "data": {
                        "config_id": config.id,
                        "log_id": latest_on_log.id if latest_on_log else None,
                        "equipment_id": equipment.id,
                        "equipment_name": equipment.name,
                        "equipment_code": equipment.code,
                        "action": "ON",
                        "status": config.status,
                        "current_state": config.current_state,
                        "start_time": (
                            latest_on_log.started_at
                            if latest_on_log
                            else config.start_time
                        ),
                        "end_time": config.end_time,
                        "duration_seconds": config.duration_seconds,
                        "stage": {
                            "id": stage.id,
                            "name": stage.name,
                        },
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        stage_valves = stage.equipments.filter(equipment_type__name__icontains="valve")

        valve_is_on = False
        active_valve = None

        for valve in stage_valves:
            valve_config = StageEquipmentConfig.objects.filter(
                equipment=valve,
                stage=stage,
                is_active=True,
            ).first()

            if valve_config and valve_config.current_state == "ON":
                valve_is_on = True
                active_valve = valve_config
                break

        if not valve_is_on:
            return Response(
                {
                    "success": False,
                    "detail": "Cannot turn Motor ON. Valve of this stage is not ON.",
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # MOTOR ON
        # ==================================================
        now = timezone.now()

        with transaction.atomic():

            log = EquipmentManualLog.objects.create(
                equipment=equipment,
                stage=stage,
                action="ON",
                started_at=now,
                performed_by=request.user,
            )

            config.current_state = "ON"
            config.status = "ACTIVE"
            config.start_time = now.time()
            config.end_time = None
            config.duration_seconds = None
            config.is_active = True

            config.save(
                update_fields=[
                    "current_state",
                    "status",
                    "start_time",
                    "end_time",
                    "duration_seconds",
                    "is_active",
                    "updated_at",
                ]
            )

        return Response(
            {
                "success": True,
                "message": "Motor turned ON successfully.",
                "data": {
                    "config_id": config.id,
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
                    },
                    "action": "ON",
                    "status": config.status,
                    "current_state": config.current_state,
                    "started_at": log.started_at,
                    "ended_at": None,
                    "duration_seconds": None,
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
                    "performed_by": request.user.id,
                    "valve": (
                        {
                            "config_id": active_valve.id,
                            "equipment_id": active_valve.equipment.id,
                            "name": active_valve.equipment.name,
                            "current_state": active_valve.current_state,
                        }
                        if active_valve
                        else None
                    ),
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
#          COAGULANT DOSING - MOTOR OFF
# ==========================================================
class CoagulantDosingMotorOffView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, equipment_id):

        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )

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
                        "This equipment is not a Motor/Pump. "
                        f"Current type: {equipment.equipment_type.name}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        stage_id = request.data.get("stage_id")

        if not stage_id:
            return Response(
                {"detail": "stage_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stage = get_object_or_404(TreatmentStage, id=stage_id)

        config = (
            StageEquipmentConfig.objects.select_related("equipment", "stage")
            .filter(
                equipment=equipment,
                stage=stage,
                is_active=True,
            )
            .first()
        )

        if not config:
            return Response(
                {
                    "success": False,
                    "detail": (
                        "StageEquipmentConfig does not exist for this motor "
                        "and stage. Turn the motor ON first."
                    ),
                    "equipment_id": equipment.id,
                    "stage_id": stage.id,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if config.current_state == "OFF":
            return Response(
                {
                    "success": False,
                    "detail": "Motor is already OFF.",
                    "data": {
                        "config_id": config.id,
                        "equipment_id": equipment.id,
                        "stage_id": stage.id,
                        "status": config.status,
                        "current_state": config.current_state,
                        "start_time": config.start_time,
                        "end_time": config.end_time,
                        "duration_seconds": config.duration_seconds,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        open_log = (
            EquipmentManualLog.objects.filter(
                equipment=equipment,
                stage=stage,
                action="ON",
            )
            .order_by("-started_at", "-id")
            .first()
        )

        if not open_log:
            return Response(
                {
                    "success": False,
                    "detail": "No ON log found for this motor.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        duration = int((now - open_log.started_at).total_seconds())
        if duration < 0:
            duration = 0

        with transaction.atomic():

            off_log = EquipmentManualLog.objects.create(
                equipment=equipment,
                stage=stage,
                action="OFF",
                started_at=now,
                ended_at=now,
                duration_seconds=duration,
                performed_by=request.user,
            )

            config.current_state = "OFF"
            config.status = "INACTIVE"
            config.end_time = now.time()
            config.duration_seconds = duration
            config.is_active = True

            config.save(
                update_fields=[
                    "current_state",
                    "status",
                    "end_time",
                    "duration_seconds",
                    "is_active",
                    "updated_at",
                ]
            )

        return Response(
            {
                "success": True,
                "message": "Motor turned OFF successfully.",
                "data": {
                    "config_id": config.id,
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
                    },
                    "action": "OFF",
                    "start_time": open_log.started_at,
                    "end_time": off_log.ended_at,
                    "duration_seconds": duration,
                    "status": config.status,
                    "current_state": config.current_state,
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
                    "performed_by": request.user.id,
                },
            },
            status=status.HTTP_200_OK,
        )
