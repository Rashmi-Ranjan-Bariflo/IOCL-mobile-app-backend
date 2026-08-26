from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Plant, TreatmentStage, PlantStage
from .serializers import (
    PlantSerializer,
    TreatmentStageSerializer,
    PlantStageSerializer,
)


# ==========================================================
#                         PLANT LIST
# ==========================================================
class PlantListView(APIView):

    permission_classes = [IsAuthenticated]
    # -----------------------------------
    # GET
    # -----------------------------------
    def get(self, request):

        plants = Plant.objects.all()

        serializer = PlantSerializer(plants, many=True)

        return Response(
            {
                "success": True,
                "message": "Plants fetched successfully.",
                "count": plants.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    # -----------------------------------
    # POST
    # -----------------------------------
    def post(self, request):

        serializer = PlantSerializer(data=request.data)

        if serializer.is_valid():

            plant = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Plant created successfully.",
                    "data": PlantSerializer(plant).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Invalid plant data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
#                       PLANT DETAIL
# ==========================================================
class PlantDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):

        try:
            return Plant.objects.get(pk=pk)

        except Plant.DoesNotExist:
            return None

    # ------------------------------------------------------
    # GET
    # ------------------------------------------------------
    def get(self, request, pk):

        plant = self.get_object(pk)

        if not plant:
            return Response(
                {
                    "success": False,
                    "message": "Plant not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PlantSerializer(plant)

        return Response(
            {
                "success": True,
                "message": "Plant fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------
    # PUT
    # ------------------------------------------------------
    def put(self, request, pk):

        plant = self.get_object(pk)

        if not plant:
            return Response(
                {
                    "success": False,
                    "message": "Plant not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PlantSerializer(
            plant,
            data=request.data,
        )

        if serializer.is_valid():

            plant = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Plant updated successfully.",
                    "data": PlantSerializer(plant).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Invalid plant data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # PATCH
    # ------------------------------------------------------
    def patch(self, request, pk):

        plant = self.get_object(pk)

        if not plant:
            return Response(
                {
                    "success": False,
                    "message": "Plant not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PlantSerializer(
            plant,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            plant = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Plant updated successfully.",
                    "data": PlantSerializer(plant).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Invalid plant data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # DELETE
    # ------------------------------------------------------
    def delete(self, request, pk):

        plant = self.get_object(pk)

        if not plant:
            return Response(
                {
                    "success": False,
                    "message": "Plant not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        plant.delete()

        return Response(
            {
                "success": True,
                "message": "Plant deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                  TREATMENT STAGE LIST
# ==========================================================
class TreatmentStageListView(APIView):

    permission_classes = [IsAuthenticated]
    # ------------------------------------
    # GET
    # ------------------------------------
    def get(self, request):

        stages = TreatmentStage.objects.all()

        serializer = TreatmentStageSerializer(stages, many=True)

        return Response(
            {
                "success": True,
                "message": "Treatment stages fetched successfully.",
                "count": stages.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    # -----------------------------------
    # POST
    # -----------------------------------
    def post(self, request):

        serializer = TreatmentStageSerializer(data=request.data)

        if serializer.is_valid():

            stage = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Treatment stage created successfully.",
                    "data": TreatmentStageSerializer(stage).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Invalid treatment stage data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
#                TREATMENT STAGE DETAIL
# ==========================================================
class TreatmentStageDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):

        try:
            return TreatmentStage.objects.get(pk=pk)

        except TreatmentStage.DoesNotExist:
            return None

    # ------------------------------------------------------
    # GET
    # ------------------------------------------------------
    def get(self, request, pk):

        stage = self.get_object(pk)

        if not stage:
            return Response(
                {
                    "success": False,
                    "message": "Treatment stage not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TreatmentStageSerializer(stage)

        return Response(
            {
                "success": True,
                "message": "Treatment stage fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------
    # PUT
    # ------------------------------------------------------
    def put(self, request, pk):

        stage = self.get_object(pk)

        if not stage:
            return Response(
                {
                    "success": False,
                    "message": "Treatment stage not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TreatmentStageSerializer(
            stage,
            data=request.data,
        )

        if serializer.is_valid():

            stage = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Treatment stage updated successfully.",
                    "data": TreatmentStageSerializer(stage).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Invalid treatment stage data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # PATCH
    # ------------------------------------------------------
    def patch(self, request, pk):

        stage = self.get_object(pk)

        if not stage:
            return Response(
                {
                    "success": False,
                    "message": "Treatment stage not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TreatmentStageSerializer(
            stage,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            stage = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Treatment stage updated successfully.",
                    "data": TreatmentStageSerializer(stage).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Invalid treatment stage data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # DELETE
    # ------------------------------------------------------
    def delete(self, request, pk):

        stage = self.get_object(pk)

        if not stage:
            return Response(
                {
                    "success": False,
                    "message": "Treatment stage not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        stage.delete()

        return Response(
            {
                "success": True,
                "message": "Treatment stage deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                     PLANT STAGE LIST
# ==========================================================
class PlantStageListView(APIView):

    permission_classes = [IsAuthenticated]
    # ------------------------------------
    # GET
    # ------------------------------------
    def get(self, request):

        plant_stages = PlantStage.objects.select_related(
            "plant",
            "treatment_stage",
        ).all()

        serializer = PlantStageSerializer(plant_stages, many=True)

        return Response(
            {
                "success": True,
                "message": "Plant stages fetched successfully.",
                "count": plant_stages.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    # ---------------------------------
    # POST
    # ---------------------------------
    def post(self, request):

        serializer = PlantStageSerializer(data=request.data)

        if serializer.is_valid():

            plant_stage = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Treatment stage assigned to plant successfully.",
                    "data": PlantStageSerializer(plant_stage).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Invalid plant stage data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
#                   PLANT STAGE DETAIL
# ==========================================================
class PlantStageDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):

        try:
            return PlantStage.objects.select_related(
                "plant",
                "treatment_stage",
            ).get(pk=pk)

        except PlantStage.DoesNotExist:
            return None

    # ------------------------------------------------------
    # GET
    # ------------------------------------------------------
    def get(self, request, pk):

        plant_stage = self.get_object(pk)

        if not plant_stage:
            return Response(
                {
                    "success": False,
                    "message": "Plant stage not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PlantStageSerializer(plant_stage)

        return Response(
            {
                "success": True,
                "message": "Plant stage fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------
    # PUT
    # ------------------------------------------------------
    def put(self, request, pk):

        plant_stage = self.get_object(pk)

        if not plant_stage:
            return Response(
                {
                    "success": False,
                    "message": "Plant stage not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PlantStageSerializer(
            plant_stage,
            data=request.data,
        )

        if serializer.is_valid():

            plant_stage = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Plant stage updated successfully.",
                    "data": PlantStageSerializer(plant_stage).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Invalid plant stage data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # PATCH
    # ------------------------------------------------------
    def patch(self, request, pk):

        plant_stage = self.get_object(pk)

        if not plant_stage:
            return Response(
                {
                    "success": False,
                    "message": "Plant stage not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PlantStageSerializer(
            plant_stage,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            plant_stage = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Plant stage updated successfully.",
                    "data": PlantStageSerializer(plant_stage).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Invalid plant stage data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # DELETE
    # ------------------------------------------------------
    def delete(self, request, pk):

        plant_stage = self.get_object(pk)

        if not plant_stage:
            return Response(
                {
                    "success": False,
                    "message": "Plant stage not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        plant_stage.delete()

        return Response(
            {
                "success": True,
                "message": "Plant stage deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#             PLANT-SPECIFIC STAGES
# ==========================================================
class PlantStagesByPlantView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, plant_id):

        try:
            plant = Plant.objects.get(id=plant_id)

        except Plant.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Plant not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        plant_stages = (
            PlantStage.objects.filter(
                plant=plant,
                is_active=True,
            )
            .select_related(
                "plant",
                "treatment_stage",
            )
            .order_by("treatment_stage__stage_order")
        )

        serializer = PlantStageSerializer(plant_stages, many=True)

        return Response(
            {
                "success": True,
                "message": "Plant stages fetched successfully.",
                "plant": {
                    "id": plant.id,
                    "name": plant.name,
                    "code": plant.code,
                },
                "count": plant_stages.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
