from rest_framework import serializers

from .models import (
    TreatmentProcess,
    TreatmentStage,
    TreatmentBatch,
    DosingRecord,
    ProcessExecutionLog,
)


# ==========================================================
# TREATMENT STAGE SERIALIZER
# ==========================================================
class TreatmentStageSerializer(serializers.ModelSerializer):

    class Meta:
        model = TreatmentStage
        fields = [
            "id",
            "process",
            "name",
            "stage_type",
            "sequence",
            "duration_seconds",
            "target_volume_liters",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# ==========================================================
# TREATMENT PROCESS SERIALIZER
# ==========================================================
class TreatmentProcessSerializer(serializers.ModelSerializer):

    stages = TreatmentStageSerializer(many=True, read_only=True)

    class Meta:
        model = TreatmentProcess
        fields = [
            "id",
            "name",
            "description",
            "status",
            "is_active",
            "stages",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# ==========================================================
# TREATMENT BATCH SERIALIZER
# ==========================================================
class TreatmentBatchSerializer(serializers.ModelSerializer):

    process_name = serializers.CharField(source="process.name", read_only=True)
    current_stage_name = serializers.CharField(source="current_stage.name", read_only=True)

    class Meta:
        model = TreatmentBatch
        fields = [
            "id",
            "process",
            "process_name",
            "batch_number",
            "input_volume_liters",
            "output_volume_liters",
            "current_stage",
            "current_stage_name",
            "status",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]


# ==========================================================
# DOSING RECORD SERIALIZER
# ==========================================================
class DosingRecordSerializer(serializers.ModelSerializer):

    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)

    class Meta:
        model = DosingRecord
        fields = [
            "id",
            "batch",
            "batch_number",
            "solution_type",
            "quantity_ml",
            "dosing_time",
            "notes",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


# ==========================================================
# PROCESS EXECUTION LOG SERIALIZER
# ==========================================================
class ProcessExecutionLogSerializer(serializers.ModelSerializer):

    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)
    stage_name = serializers.CharField(source="stage.name", read_only=True)

    class Meta:
        model = ProcessExecutionLog
        fields = [
            "id",
            "batch",
            "batch_number",
            "stage",
            "stage_name",
            "status",
            "started_at",
            "completed_at",
            "actual_duration_seconds",
            "remarks",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]
