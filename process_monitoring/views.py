from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    ProcessParameter,
    ProcessReading,
    EquipmentStatus,
)
from .serializers import (
    ProcessParameterSerializer,
    ProcessReadingSerializer,
    EquipmentStatusSerializer,
)

# ==========================================================
#              PROCESS PARAMETER
# ==========================================================


class ProcessParameterListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        parameters = ProcessParameter.objects.all()
        serializer = ProcessParameterSerializer(parameters, many=True)

        return Response(
            {
                "success": True,
                "message": "Process parameters fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = ProcessParameterSerializer(data=request.data)
        if serializer.is_valid():
            parameter = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Process parameter created successfully.",
                    "data": ProcessParameterSerializer(parameter).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
#              PROCESS PARAMETER DETAIL
# ==========================================================


class ProcessParameterDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):

        try:
            return ProcessParameter.objects.get(pk=pk)

        except ProcessParameter.DoesNotExist:
            return None

    def get(self, request, pk):

        parameter = self.get_object(pk)

        if not parameter:

            return Response(
                {
                    "success": False,
                    "message": "Process parameter not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProcessParameterSerializer(parameter)

        return Response(
            {
                "success": True,
                "message": "Process parameter fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):

        parameter = self.get_object(pk)

        if not parameter:

            return Response(
                {
                    "success": False,
                    "message": "Process parameter not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProcessParameterSerializer(parameter, data=request.data)

        if serializer.is_valid():

            parameter = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Process parameter updated successfully.",
                    "data": ProcessParameterSerializer(parameter).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):

        parameter = self.get_object(pk)

        if not parameter:

            return Response(
                {
                    "success": False,
                    "message": "Process parameter not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProcessParameterSerializer(
            parameter, data=request.data, partial=True
        )

        if serializer.is_valid():

            parameter = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Process parameter updated successfully.",
                    "data": ProcessParameterSerializer(parameter).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):

        parameter = self.get_object(pk)

        if not parameter:

            return Response(
                {
                    "success": False,
                    "message": "Process parameter not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        parameter.delete()

        return Response(
            {
                "success": True,
                "message": "Process parameter deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#              PROCESS READING
# ==========================================================


class ProcessReadingListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        readings = ProcessReading.objects.select_related(
            "plant",
            "plant_stage",
            "equipment",
            "sensor",
            "parameter",
        ).all()

        serializer = ProcessReadingSerializer(readings, many=True)

        return Response(
            {
                "success": True,
                "message": "Process readings fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = ProcessReadingSerializer(data=request.data)

        if serializer.is_valid():

            reading = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Process reading created successfully.",
                    "data": ProcessReadingSerializer(reading).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
#              PROCESS READING DETAIL
# ==========================================================


class ProcessReadingDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):

        try:
            return ProcessReading.objects.select_related(
                "plant",
                "plant_stage",
                "equipment",
                "sensor",
                "parameter",
            ).get(pk=pk)

        except ProcessReading.DoesNotExist:
            return None

    def get(self, request, pk):

        reading = self.get_object(pk)

        if not reading:

            return Response(
                {
                    "success": False,
                    "message": "Process reading not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProcessReadingSerializer(reading)

        return Response(
            {
                "success": True,
                "message": "Process reading fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):

        reading = self.get_object(pk)

        if not reading:

            return Response(
                {
                    "success": False,
                    "message": "Process reading not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProcessReadingSerializer(reading, data=request.data)

        if serializer.is_valid():

            reading = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Process reading updated successfully.",
                    "data": ProcessReadingSerializer(reading).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):

        reading = self.get_object(pk)

        if not reading:

            return Response(
                {
                    "success": False,
                    "message": "Process reading not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProcessReadingSerializer(reading, data=request.data, partial=True)

        if serializer.is_valid():

            reading = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Process reading updated successfully.",
                    "data": ProcessReadingSerializer(reading).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):

        reading = self.get_object(pk)

        if not reading:

            return Response(
                {
                    "success": False,
                    "message": "Process reading not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        reading.delete()

        return Response(
            {
                "success": True,
                "message": "Process reading deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#              EQUIPMENT STATUS
# ==========================================================


class EquipmentStatusListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        statuses = EquipmentStatus.objects.select_related(
            "plant",
            "plant_stage",
            "equipment",
        ).all()

        serializer = EquipmentStatusSerializer(statuses, many=True)

        return Response(
            {
                "success": True,
                "message": "Equipment statuses fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = EquipmentStatusSerializer(data=request.data)

        if serializer.is_valid():

            equipment_status = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Equipment status created successfully.",
                    "data": EquipmentStatusSerializer(equipment_status).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
#              EQUIPMENT STATUS DETAIL
# ==========================================================


class EquipmentStatusDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):

        try:
            return EquipmentStatus.objects.select_related(
                "plant",
                "plant_stage",
                "equipment",
            ).get(pk=pk)

        except EquipmentStatus.DoesNotExist:
            return None

    def get(self, request, pk):

        equipment_status = self.get_object(pk)

        if not equipment_status:

            return Response(
                {
                    "success": False,
                    "message": "Equipment status not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EquipmentStatusSerializer(equipment_status)

        return Response(
            {
                "success": True,
                "message": "Equipment status fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):

        equipment_status = self.get_object(pk)

        if not equipment_status:

            return Response(
                {
                    "success": False,
                    "message": "Equipment status not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EquipmentStatusSerializer(equipment_status, data=request.data)

        if serializer.is_valid():

            equipment_status = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Equipment status updated successfully.",
                    "data": EquipmentStatusSerializer(equipment_status).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):

        equipment_status = self.get_object(pk)

        if not equipment_status:

            return Response(
                {
                    "success": False,
                    "message": "Equipment status not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EquipmentStatusSerializer(
            equipment_status, data=request.data, partial=True
        )

        if serializer.is_valid():

            equipment_status = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Equipment status updated successfully.",
                    "data": EquipmentStatusSerializer(equipment_status).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):

        equipment_status = self.get_object(pk)

        if not equipment_status:

            return Response(
                {
                    "success": False,
                    "message": "Equipment status not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        equipment_status.delete()

        return Response(
            {
                "success": True,
                "message": "Equipment status deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
