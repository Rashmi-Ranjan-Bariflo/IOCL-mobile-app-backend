from rest_framework import serializers
from .models import Plant, TreatmentStage, PlantStage


# ==========================================================
#                         PLANT SERIALIZER
# ==========================================================
class PlantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Plant

        fields = [
            "id",
            "name",
            "code",
            "location",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Plant name is required.")

        return value

    def validate_code(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError("Plant code is required.")

        return value

    def validate_location(self, value):
        if value:
            value = value.strip()

        return value


# ==========================================================
#                  TREATMENT STAGE SERIALIZER
# ==========================================================
class TreatmentStageSerializer(serializers.ModelSerializer):

    class Meta:
        model = TreatmentStage

        fields = [
            "id",
            "name",
            "code",
            "description",
            "stage_order",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Treatment stage name is required.")

        return value

    def validate_code(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError("Treatment stage code is required.")

        return value

    def validate_stage_order(self, value):
        if value <= 0:
            raise serializers.ValidationError("Stage order must be greater than 0.")

        return value


# ==========================================================
#                    PLANT STAGE SERIALIZER
# ==========================================================
class PlantStageSerializer(serializers.ModelSerializer):

    plant_name = serializers.CharField(source="plant.name", read_only=True)

    plant_code = serializers.CharField(source="plant.code", read_only=True)

    treatment_stage_name = serializers.CharField(
        source="treatment_stage.name", read_only=True
    )

    treatment_stage_code = serializers.CharField(
        source="treatment_stage.code", read_only=True
    )

    stage_order = serializers.IntegerField(
        source="treatment_stage.stage_order", read_only=True
    )

    class Meta:
        model = PlantStage

        fields = [
            "id",
            "plant",
            "treatment_stage",
            "plant_name",
            "plant_code",
            "treatment_stage_name",
            "treatment_stage_code",
            "stage_order",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "plant_name",
            "plant_code",
            "treatment_stage_name",
            "treatment_stage_code",
            "stage_order",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        plant = attrs.get("plant")
        treatment_stage = attrs.get("treatment_stage")

        # --------------------------------------------------
        # Check plant is active
        # --------------------------------------------------
        if plant and not plant.is_active:
            raise serializers.ValidationError(
                {"plant": "Cannot assign a stage to an inactive plant."}
            )

        # --------------------------------------------------
        # Check treatment stage is active
        # --------------------------------------------------
        if treatment_stage and not treatment_stage.is_active:
            raise serializers.ValidationError(
                {"treatment_stage": ("Cannot assign an inactive treatment stage.")}
            )

        # --------------------------------------------------
        # Prevent duplicate Plant + Stage
        # --------------------------------------------------
        if plant and treatment_stage:

            queryset = PlantStage.objects.filter(
                plant=plant,
                treatment_stage=treatment_stage,
            )

            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "treatment_stage": (
                            "This treatment stage is already " "assigned to this plant."
                        )
                    }
                )

        return attrs
