from django.db import models

# ==========================================================
#                       PLANT
# ==========================================================
class Plant(models.Model):

    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=50, unique=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "plants"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


# ==========================================================
#                    TREATMENT STAGE
# ==========================================================
class TreatmentStage(models.Model):

    name = models.CharField(max_length=150,unique=True)
    code = models.CharField(max_length=50,unique=True)
    description = models.TextField(blank=True,null=True)
    stage_order = models.PositiveIntegerField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "treatment_stages"
        ordering = ["stage_order"]

    def __str__(self):
        return f"{self.stage_order}. {self.name}"


# ==========================================================
#                      PLANT STAGE
# ==========================================================
class PlantStage(models.Model):

    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,related_name="stages")
    treatment_stage = models.ForeignKey(TreatmentStage,on_delete=models.PROTECT,related_name="plants")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "plant_stages"

        constraints = [
            models.UniqueConstraint(
                fields=["plant", "treatment_stage"],
                name="unique_plant_treatment_stage"
            )
        ]

        ordering = ["treatment_stage__stage_order"]

    def __str__(self):
        return (
            f"{self.plant.name} - "
            f"{self.treatment_stage.name}"
        )