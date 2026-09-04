from rest_framework import serializers

from .models import (
    TreatmentStage,
    TreatmentProcess,
    TreatmentBatch,
    DosingRecord,
    ProcessExecutionLog,
)


# ==========================================================
# TREATMENT STAGE SERIALIZER
# ==========================================================
class TreatmentStageSerializer(serializers.ModelSerializer):

    process_count = serializers.IntegerField(source="processes.count", read_only=True)

    class Meta:
        model = TreatmentStage

        fields = [
            "id",
            "name",
            "stage_type",
            "description",
            "sequence",
            "is_active",
            "process_count",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "process_count",
            "created_at",
            "updated_at",
        ]


# ==========================================================
# TREATMENT PROCESS SERIALIZER
# ==========================================================
class TreatmentProcessSerializer(serializers.ModelSerializer):

    stage_name = serializers.CharField(source="stage.name", read_only=True)

    stage_type = serializers.CharField(source="stage.stage_type", read_only=True)

    class Meta:
        model = TreatmentProcess

        fields = [
            "id",
            "stage",
            "stage_name",
            "stage_type",
            "name",
            "description",
            "sequence",
            "duration_seconds",
            "target_volume_liters",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "stage_name",
            "stage_type",
            "created_at",
            "updated_at",
        ]


# ==========================================================
# TREATMENT BATCH SERIALIZER
# ==========================================================
class TreatmentBatchSerializer(serializers.ModelSerializer):

    process_name = serializers.CharField(source="process.name", read_only=True)

    stage_name = serializers.CharField(source="process.stage.name", read_only=True)

    stage_type = serializers.CharField(
        source="process.stage.stage_type", read_only=True
    )

    class Meta:
        model = TreatmentBatch

        fields = [
            "id",
            "process",
            "process_name",
            "stage_name",
            "stage_type",
            "batch_number",
            "input_volume_liters",
            "output_volume_liters",
            "status",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "process_name",
            "stage_name",
            "stage_type",
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

    process_name = serializers.CharField(source="batch.process.name", read_only=True)

    stage_name = serializers.CharField(
        source="batch.process.stage.name", read_only=True
    )

    class Meta:
        model = DosingRecord

        fields = [
            "id",
            "batch",
            "batch_number",
            "process_name",
            "stage_name",
            "solution_type",
            "quantity_ml",
            "dosing_time",
            "notes",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "batch_number",
            "process_name",
            "stage_name",
            "created_at",
        ]


# ==========================================================
# PROCESS EXECUTION LOG SERIALIZER
# ==========================================================
class ProcessExecutionLogSerializer(serializers.ModelSerializer):

    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)

    process_name = serializers.CharField(source="process.name", read_only=True)

    stage_name = serializers.CharField(source="process.stage.name", read_only=True)

    stage_type = serializers.CharField(
        source="process.stage.stage_type", read_only=True
    )

    class Meta:
        model = ProcessExecutionLog

        fields = [
            "id",
            "batch",
            "batch_number",
            "process",
            "process_name",
            "stage_name",
            "stage_type",
            "status",
            "started_at",
            "completed_at",
            "actual_duration_seconds",
            "remarks",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "batch_number",
            "process_name",
            "stage_name",
            "stage_type",
            "created_at",
        ]
