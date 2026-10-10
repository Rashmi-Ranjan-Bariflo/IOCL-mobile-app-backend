from urllib.request import Request

from rest_framework import status
from rest_framework import response
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
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Equipment created successfully.",
                    "data": serializer.data,
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
        print(equipment)
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
        print(stage)
        config, created = StageEquipmentConfig.objects.get_or_create(
            equipment=equipment,
            stage=stage,
            defaults={
                "current_state": "OFF",
                "status": "ACTIVE",
                "is_active": True,
            },
        )
        print(config.equipment)
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
        print(sensors)
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


# =========================================================
#                    STAGE SENSORS
# =========================================================
class StageSensorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, stage_id):
        stage = get_object_or_404(TreatmentStage, id=stage_id)
        print(stage)

        configs = StageEquipmentConfig.objects.filter(
            stage=stage,
            equipment__equipment_type__name__icontains="sensor",
            is_active=True,
        ).select_related(
            "equipment",
            "equipment__equipment_type",
        )
        print(configs)

        data = []

        for config in configs:
            data.append(
                {
                    "config_id": config.id,
                    "equipment_id": config.equipment.id,
                    "name": config.equipment.name,
                    "code": config.equipment.code,
                    "equipment_type": (
                        config.equipment.equipment_type.name
                        if config.equipment.equipment_type
                        else None
                    ),
                    "current_state": config.current_state,
                    "status": config.status,
                    "is_active": config.is_active,
                }
            )

        return Response(
            {
                "success": True,
                "message": "Stage sensors retrieved successfully.",
                "stage": {
                    "id": stage.id,
                    "name": stage.name,
                },
                "sensor_count": len(data),
                "sensors": data,
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



class MergeManualDurationView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, stage_id):
        stage = get_object_or_404(TreatmentStage, id=stage_id)

        equipments = stage.equipments.all()
        merged_data = []

        for equipment in equipments:
            config = StageEquipmentConfig.objects.filter(
                stage=stage,
                equipment=equipment,
                is_active=True,
            ).first()

            if not config:
                continue

            # Only completed OFF logs that already have a duration
            latest_log = (
                EquipmentManualLog.objects.filter(
                    stage=stage,
                    equipment=equipment,
                    action="OFF",
                    duration_seconds__isnull=False,
                    ended_at__isnull=False,
                )
                .order_by("-id")  
                .first()
            )

            if not latest_log:
                continue

            config.duration_seconds = latest_log.duration_seconds
            config.save(update_fields=["duration_seconds", "updated_at"])

            merged_data.append(
                {
                    "config_id": config.id,
                    "equipment_id": equipment.id,
                    "equipment_name": equipment.name,
                    "current_state": config.current_state,
                    "status": config.status,
                    "duration_seconds": config.duration_seconds,
                    "manual_log_id": latest_log.id,
                }
            )

        return Response(
            {
                "success": True,
                "message": "Latest manual duration merged successfully.",
                "stage": {
                    "id": stage.id,
                    "name": stage.name,
                },
                "count": len(merged_data),
                "data": merged_data,
            },
            status=status.HTTP_200_OK,
        )


class StageEquipmentsDurationView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, stage_id):
        stage = get_object_or_404(TreatmentStage, id=stage_id)

        equipments = stage.equipments.select_related("equipment_type").all()

        data = []
        for equipment in equipments:
            config = StageEquipmentConfig.objects.filter(
                equipment=equipment,
                stage=stage,
                is_active=True,
            ).first()

            data.append(
                {
                    "id": equipment.id,
                    "name": equipment.name,
                    "code": equipment.code,
                    "equipment_type": (
                        equipment.equipment_type.name
                        if equipment.equipment_type
                        else None
                    ),
                    "current_state": config.current_state if config else "OFF",
                    "status": config.status if config else "INACTIVE",
                    "is_running": (config.current_state == "ON" if config else False),
                    "duration_seconds": (config.duration_seconds if config else 0),
                }
            )

        return Response(
            {
                "success": True,
                "message": "Equipment durations under stage retrieved successfully.",
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
        )

        if config.current_state == "ON":
            latest_on_log = (
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
                        "log_id": latest_on_log.id if latest_on_log else None,
                        "equipment_id": equipment.id,
                        "equipment_name": equipment.name,
                        "equipment_code": equipment.code,
                        "action": "ON",
                        "status": config.status,
                        "current_state": config.current_state,
                        "started_at": (
                            latest_on_log.started_at if latest_on_log else None
                        ),
                        "ended_at": None,
                        "duration_seconds": 0,
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
                    "status": config.status,
                    "current_state": config.current_state,
                    "started_at": log.started_at,
                    "ended_at": None,
                    "duration_seconds": 0,
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
                    "performed_by": request.user.id,
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

        config = StageEquipmentConfig.objects.filter(
            equipment=equipment,
            stage=stage,
        ).first()

        if not config:
            return Response(
                {
                    "success": False,
                    "detail": "StageEquipmentConfig does not exist for this motor and stage.",
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
                    "detail": "No open ON log found for this motor.",
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
                    "status": config.status,
                    "current_state": config.current_state,
                    "started_at": open_log.started_at,
                    "ended_at": now,
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


# =======================================================
#         COAGULANT DOSING - MOTOR AUTO ON
# =======================================================


class CoagulantDosingMotorAutoOnView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, stage_id, equipment_id):
        stage = get_object_or_404(TreatmentStage, id=stage_id)
        equipment = get_object_or_404(
            Equipment.objects.select_related("equipment_type"),
            id=equipment_id,
        )

        equipment_type = (
            equipment.equipment_type.name.lower() if equipment.equipment_type else ""
        )

        if "motor" not in equipment_type and "pump" not in equipment_type:
            return Response(
                {
                    "success": False,
                    "message": "Selected equipment is not a motor/pump.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "coagulant" not in equipment.name.lower()
            and "dosing" not in equipment.name.lower()
        ):
            return Response(
                {
                    "success": False,
                    "message": "Selected equipment is not a Coagulant Dosing Motor.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        config, created = StageEquipmentConfig.objects.get_or_create(
            equipment=equipment,
            stage=stage,
            defaults={
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
                    "success": True,
                    "message": "Coagulant Dosing Motor is already ON.",
                    "data": {
                        "equipment_id": equipment.id,
                        "equipment_name": equipment.name,
                        "stage_id": stage.id,
                        "stage_name": stage.name,
                        "current_state": config.current_state,
                        "status": config.status,
                        "mode": "AUTO",
                        "is_running": True,
                        "started_at": open_log.started_at if open_log else None,
                    },
                },
                status=status.HTTP_200_OK,
            )

        started_at = timezone.now()

        log = EquipmentManualLog.objects.create(
            equipment=equipment,
            stage=stage,
            action="ON",
            started_at=started_at,
            performed_by=request.user,
        )

        config.current_state = "ON"
        config.save(update_fields=["current_state", "updated_at"])

        return Response(
            {
                "success": True,
                "message": "Coagulant Dosing Motor turned ON in Auto Mode.",
                "data": {
                    "equipment_id": equipment.id,
                    "equipment_name": equipment.name,
                    "equipment_code": equipment.code,
                    "equipment_type": (
                        equipment.equipment_type.name
                        if equipment.equipment_type
                        else None
                    ),
                    "stage_id": stage.id,
                    "stage_name": stage.name,
                    "current_state": config.current_state,
                    "status": config.status,
                    "mode": "AUTO",
                    "is_running": True,
                    "log_id": log.id,
                    "started_at": log.started_at,
                    "ended_at": None,
                    "duration_seconds": 0,
                },
            },
            status=status.HTTP_200_OK,
        )


# ==============================================================
#                           BLOWER ON
# ==============================================================
class BlowerOnView(APIView):
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

        if "blower" not in equipment_type:
            return Response(
                {
                    "detail": (
                        "This equipment is not a Blower. "
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

        stage = get_object_or_404(
            TreatmentStage,
            id=stage_id,
        )

        config, created = StageEquipmentConfig.objects.get_or_create(
            equipment=equipment,
            stage=stage,
        )

        if config.current_state == "ON":
            latest_on_log = (
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
                    "detail": "Blower is already ON.",
                    "data": {
                        "config_id": config.id,
                        "log_id": latest_on_log.id if latest_on_log else None,
                        "equipment_id": equipment.id,
                        "equipment_name": equipment.name,
                        "equipment_code": equipment.code,
                        "action": "ON",
                        "status": config.status,
                        "current_state": config.current_state,
                        "started_at": (
                            latest_on_log.started_at if latest_on_log else None
                        ),
                        "ended_at": None,
                        "duration_seconds": 0,
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
                "message": "Blower turned ON successfully.",
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
                    "status": config.status,
                    "current_state": config.current_state,
                    "started_at": log.started_at,
                    "ended_at": None,
                    "duration_seconds": 0,
                    "stage": {
                        "id": stage.id,
                        "name": stage.name,
                    },
                    "performed_by": request.user.id,
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ==============================================================
#                           BLOWER OFF
# ==============================================================
class BlowerOffView(APIView):
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

        if "blower" not in equipment_type:
            return Response(
                {
                    "detail": (
                        "This equipment is not a Blower. "
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

        stage = get_object_or_404(
            TreatmentStage,
            id=stage_id,
        )

        config = StageEquipmentConfig.objects.filter(
            equipment=equipment,
            stage=stage,
        ).first()

        if not config:
            return Response(
                {
                    "success": False,
                    "detail": "StageEquipmentConfig does not exist for this blower and stage.",
                    "equipment_id": equipment.id,
                    "stage_id": stage.id,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if config.current_state == "OFF":
            return Response(
                {
                    "success": False,
                    "detail": "Blower is already OFF.",
                    "data": {
                        "config_id": config.id,
                        "equipment_id": equipment.id,
                        "stage_id": stage.id,
                        "status": config.status,
                        "current_state": config.current_state,
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
                    "detail": "No open ON log found for this blower.",
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
                "message": "Blower turned OFF successfully.",
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
                    "status": config.status,
                    "current_state": config.current_state,
                    "started_at": open_log.started_at,
                    "ended_at": now,
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







class AssetCategoryCardsAPIView(APIView):
    """
    Returns category summaries and equipment counts.

    An equipment item may be linked to multiple treatment stages.
    Each equipment record is counted only once.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        categories = {}

        # Initialize categories from the existing database records.
        for equipment_type in EquipmentType.objects.filter(
            is_active=True
        ).order_by("name"):
            categories[equipment_type.id] = {
                "id": equipment_type.id,
                "name": equipment_type.name,
                "total_assets": 0,
                "running_count": 0,
                "stopped_count": 0,
                "unclassified_count": 0,
                "equipment_groups": {},
            }

        # Fetch each equipment record once and prefetch its stage
        # configurations to avoid a database query per equipment.
        equipment_records = (
            Equipment.objects
            .filter(
                user=request.user,
                equipment_type__is_active=True,
            )
            .select_related("equipment_type")
            .prefetch_related("stage_configurations")
            .order_by("name", "id")
        )


        for equipment in equipment_records:
            category_id = equipment.equipment_type_id

            # Ignore equipment belonging to an inactive category.
            if category_id not in categories:
                continue

            category = categories[category_id]
            category["total_assets"] += 1

            # An equipment item can have multiple stage configurations.
            # Collect distinct states, but count the equipment only once.
            states = {
                config.current_state
                for config in equipment.stage_configurations.all()
            }

            if "ON" in states:
                display_status = "RUNNING"
                category["running_count"] += 1
            elif states and states == {"OFF"}:
                display_status = "STOPPED"
                category["stopped_count"] += 1
            else:
                display_status = "UNCLASSIFIED"
                category["unclassified_count"] += 1

            # Group repeated equipment names within each category,
            # as shown in the supplied dashboard design.
            groups = category["equipment_groups"]
            group = groups.get(equipment.name)

            if group is None:
                group = {
                    "name": equipment.name,
                    "total_count": 0,
                    "running_count": 0,
                    "stopped_count": 0,
                    "unclassified_count": 0,
                    "equipment_ids": [],
                }
                groups[equipment.name] = group

            group["total_count"] += 1
            group["equipment_ids"].append(equipment.id)

            if display_status == "RUNNING":
                group["running_count"] += 1
            elif display_status == "STOPPED":
                group["stopped_count"] += 1
            else:
                group["unclassified_count"] += 1

        # Convert internal dictionaries into JSON-serializable lists.
        result = []

        for category in categories.values():
            category["equipment"] = list(
                category.pop("equipment_groups").values()
            )
            result.append(category)

        return Response({"categories": result})







from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from .models import Equipment


class AssetDetailsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Only return equipment owned by the logged-in user.
        queryset = (
            Equipment.objects
            .filter(user=request.user)
            .select_related("equipment_type")
            .prefetch_related("stage_configurations")
            .order_by("name", "id")
        )

        # Optional search by equipment name or code.
        search = request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search)
                | models.Q(code__icontains=search)
            )

        # Optional category filter: equipment_type ID.
        category_id = request.query_params.get("category")
        if category_id:
            if not category_id.isdigit():
                return Response(
                    {"error": "category must be a valid category ID."},
                    status=400,
                )
            queryset = queryset.filter(
                equipment_type_id=int(category_id),
                equipment_type__is_active=True,
            )

        # Only include equipment belonging to active categories.
        queryset = queryset.filter(equipment_type__is_active=True)

        requested_status = request.query_params.get(
            "status", ""
        ).strip().upper()

        valid_statuses = {"RUNNING", "STOPPED", "UNCLASSIFIED"}
        if requested_status and requested_status not in valid_statuses:
            return Response(
                {
                    "error": (
                        "Invalid status. Use RUNNING, STOPPED, "
                        "or UNCLASSIFIED."
                    )
                },
                status=400,
            )

        # Build one row per equipment record.
        
        rows = []

        for equipment in queryset:
            states = {
                config.current_state
                for config in equipment.stage_configurations.all()
            }

            if "ON" in states:
                display_status = "RUNNING"
            elif states and states == {"OFF"}:
                display_status = "STOPPED"
            else:
                display_status = "UNCLASSIFIED"

            if requested_status and display_status != requested_status:
                continue

            stages = (
                equipment.treatment_stages
                .filter(is_active=True)
                .order_by("sequence")
                .values("id", "name", "stage_type", "sequence")
            )

            rows.append({
                "id": equipment.id,
                "name": equipment.name,
                "type": equipment.equipment_type.name,
                "stages": list(stages),
                "status": display_status,
            })

        # Pagination.
        try:
            page_number = int(request.query_params.get("page", "1"))
            page_size = int(request.query_params.get("page_size", "10"))
        except (ValueError, TypeError):
            return Response(
                {"error": "page and page_size must be integers."},
                status=400,
            )

        if page_number < 1 or page_size < 1 or page_size > 100:
            return Response(
                {"error": "page must be >= 1; page_size must be 1-100."},
                status=400,
            )

        paginator = Paginator(rows, page_size)

        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            return Response(
                {"error": "Requested page does not exist."},
                status=404,
            )

        results = []
        start_index = page_obj.start_index()

        for index, row in enumerate(page_obj.object_list, start=start_index):
            results.append({
                "s_no": index,
                **row,
            })

        return Response({
            "count": paginator.count,
            "page": page_number,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "results": results,
        })





from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Equipment


class AssetOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        equipment_records = (
            Equipment.objects
            .filter(
                user=request.user,
                equipment_type__is_active=True,
            )
            .prefetch_related("stage_configurations")
            .order_by("id")
        )

        total_assets = 0
        running_count = 0
        stopped_count = 0
        maintenance_count = 0
        fault_count = 0
        unclassified_count = 0

        for equipment in equipment_records:
            total_assets += 1

            configurations = list(
                equipment.stage_configurations.all()
            )

            # No stage configuration means status is unknown.
            if not configurations:
                unclassified_count += 1
                continue

            config_statuses = {
                config.status for config in configurations
            }
            current_states = {
                config.current_state for config in configurations
            }

            # Use a deterministic priority when stage configurations
            # disagree about the equipment's condition.
            if "FAULT" in config_statuses:
                fault_count += 1

            elif "MAINTENANCE" in config_statuses:
                maintenance_count += 1

            elif "ON" in current_states:
                running_count += 1

            elif current_states == {"OFF"}:
                stopped_count += 1

            else:
                unclassified_count += 1

        return Response({
            "total_assets": total_assets,
            "running": running_count,
            "stopped": stopped_count,
            "maintenance": maintenance_count,
            "fault": fault_count,
            "unclassified": unclassified_count,
        })
