from rest_framework import serializers

from .models import (
    TreatmentStage,
    TreatmentProcess,
    TreatmentBatch,
    StageExecutionLog,
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
            "user",
            "stage_type",
            "description",
            "sequence",
            "equipments",
            "is_active",
            "process_count",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user",
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

    stage_count = serializers.IntegerField(
        source="stage_execution_logs.count", read_only=True
    )

    completed_stage_count = serializers.SerializerMethodField()

    class Meta:
        model = TreatmentBatch

        fields = [
            "id",
            "batch_number",
            "input_volume_liters",
            "output_volume_liters",
            "status",
            "started_at",
            "completed_at",
            "stage_count",
            "completed_stage_count",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "started_at",
            "completed_at",
            "stage_count",
            "completed_stage_count",
            "created_at",
            "updated_at",
        ]

    def get_completed_stage_count(self, obj):
        return obj.stage_execution_logs.filter(status="COMPLETED").count()


# ==========================================================
# STAGE EXECUTION LOG SERIALIZER
# ==========================================================
class StageExecutionLogSerializer(serializers.ModelSerializer):

    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)

    stage_name = serializers.CharField(source="stage.name", read_only=True)

    stage_type = serializers.CharField(source="stage.stage_type", read_only=True)

    process_count = serializers.IntegerField(
        source="stage.processes.count", read_only=True
    )

    completed_process_count = serializers.SerializerMethodField()

    class Meta:
        model = StageExecutionLog

        fields = [
            "id",
            "batch",
            "batch_number",
            "stage",
            "stage_name",
            "stage_type",
            "status",
            "started_at",
            "completed_at",
            "actual_duration_seconds",
            "process_count",
            "completed_process_count",
            "remarks",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "batch_number",
            "stage_name",
            "stage_type",
            "started_at",
            "completed_at",
            "actual_duration_seconds",
            "process_count",
            "completed_process_count",
            "created_at",
            "updated_at",
        ]

    def get_completed_process_count(self, obj):
        return ProcessExecutionLog.objects.filter(
            batch=obj.batch, process__stage=obj.stage, status="COMPLETED"
        ).count()


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
            "batch_number",
            "created_at",
        ]


# ==========================================================
# PROCESS EXECUTION LOG SERIALIZER
# ==========================================================
class ProcessExecutionLogSerializer(serializers.ModelSerializer):

    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)

    process_name = serializers.CharField(source="process.name", read_only=True)

    process_sequence = serializers.IntegerField(
        source="process.sequence", read_only=True
    )

    stage_name = serializers.CharField(source="process.stage.name", read_only=True)

    stage_type = serializers.CharField(
        source="process.stage.stage_type", read_only=True
    )

    stage_sequence = serializers.IntegerField(
        source="process.stage.sequence", read_only=True
    )

    class Meta:
        model = ProcessExecutionLog

        fields = [
            "id",
            "batch",
            "batch_number",
            "process",
            "process_name",
            "process_sequence",
            "stage_name",
            "stage_type",
            "stage_sequence",
            "status",
            "started_at",
            "completed_at",
            "actual_duration_seconds",
            "remarks",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "batch_number",
            "process_name",
            "process_sequence",
            "stage_name",
            "stage_type",
            "stage_sequence",
            "started_at",
            "completed_at",
            "actual_duration_seconds",
            "created_at",
            "updated_at",
        ]
