from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    WaterQualityParameter,
    WaterQualityReading,
)
from .serializers import (
    WaterQualityParameterSerializer,
    WaterQualityReadingSerializer,
)

# ==========================================================
#              WATER QUALITY PARAMETERS
# ==========================================================


class WaterQualityParameterListCreateView(APIView):

    def get(self, request):

        parameters = WaterQualityParameter.objects.all()

        serializer = WaterQualityParameterSerializer(parameters, many=True)

        return Response(
            {
                "success": True,
                "count": parameters.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = WaterQualityParameterSerializer(data=request.data)

        if serializer.is_valid():

            parameter = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": ("Water quality parameter " "created successfully."),
                    "data": WaterQualityParameterSerializer(parameter).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
#              WATER QUALITY PARAMETER DETAIL
# ==========================================================


class WaterQualityParameterDetailView(APIView):

    def get_object(self, pk):

        try:
            return WaterQualityParameter.objects.get(pk=pk)

        except WaterQualityParameter.DoesNotExist:
            return None

    def get(self, request, pk):

        parameter = self.get_object(pk)

        if parameter is None:
            return Response(
                {
                    "success": False,
                    "message": ("Water quality parameter " "not found."),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WaterQualityParameterSerializer(parameter)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):

        parameter = self.get_object(pk)

        if parameter is None:
            return Response(
                {
                    "success": False,
                    "message": ("Water quality parameter " "not found."),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WaterQualityParameterSerializer(parameter, data=request.data)

        if serializer.is_valid():

            parameter = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": ("Water quality parameter " "updated successfully."),
                    "data": WaterQualityParameterSerializer(parameter).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):

        parameter = self.get_object(pk)

        if parameter is None:
            return Response(
                {
                    "success": False,
                    "message": ("Water quality parameter " "not found."),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WaterQualityParameterSerializer(
            parameter, data=request.data, partial=True
        )

        if serializer.is_valid():

            parameter = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": ("Water quality parameter " "updated successfully."),
                    "data": WaterQualityParameterSerializer(parameter).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):

        parameter = self.get_object(pk)

        if parameter is None:
            return Response(
                {
                    "success": False,
                    "message": ("Water quality parameter " "not found."),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        parameter.delete()

        return Response(
            {
                "success": True,
                "message": ("Water quality parameter " "deleted successfully."),
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#              WATER QUALITY READINGS
# ==========================================================


class WaterQualityReadingListCreateView(APIView):

    def get(self, request):

        readings = WaterQualityReading.objects.select_related(
            "parameter",
            "plant",
            "plant_stage",
            "sensor",
        ).all()

        # --------------------------------------------------
        # Filter by Plant
        # --------------------------------------------------

        plant_id = request.query_params.get("plant")

        if plant_id:
            readings = readings.filter(plant_id=plant_id)

        # --------------------------------------------------
        # Filter by Plant Stage
        # --------------------------------------------------

        plant_stage_id = request.query_params.get("plant_stage")

        if plant_stage_id:
            readings = readings.filter(plant_stage_id=plant_stage_id)

        # --------------------------------------------------
        # Filter by Parameter
        # --------------------------------------------------

        parameter_id = request.query_params.get("parameter")

        if parameter_id:
            readings = readings.filter(parameter_id=parameter_id)

        # --------------------------------------------------
        # Filter by Sensor
        # --------------------------------------------------

        sensor_id = request.query_params.get("sensor")

        if sensor_id:
            readings = readings.filter(sensor_id=sensor_id)

        # --------------------------------------------------
        # Filter by Source
        # --------------------------------------------------

        source = request.query_params.get("source")

        if source:
            readings = readings.filter(source=source.upper())

        # --------------------------------------------------
        # Filter by Status
        # --------------------------------------------------

        reading_status = request.query_params.get("status")

        if reading_status:
            readings = readings.filter(status=reading_status.upper())

        # --------------------------------------------------
        # Serialize
        # --------------------------------------------------

        serializer = WaterQualityReadingSerializer(readings, many=True)

        return Response(
            {
                "success": True,
                "count": readings.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = WaterQualityReadingSerializer(data=request.data)

        if serializer.is_valid():

            reading = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": ("Water quality reading " "created successfully."),
                    "data": WaterQualityReadingSerializer(reading).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
#              WATER QUALITY READING DETAIL
# ==========================================================


class WaterQualityReadingDetailView(APIView):

    def get_object(self, pk):

        try:
            return WaterQualityReading.objects.select_related(
                "parameter",
                "plant",
                "plant_stage",
                "sensor",
            ).get(pk=pk)

        except WaterQualityReading.DoesNotExist:
            return None

    def get(self, request, pk):

        reading = self.get_object(pk)

        if reading is None:
            return Response(
                {
                    "success": False,
                    "message": ("Water quality reading " "not found."),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WaterQualityReadingSerializer(reading)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):

        reading = self.get_object(pk)

        if reading is None:
            return Response(
                {
                    "success": False,
                    "message": ("Water quality reading " "not found."),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WaterQualityReadingSerializer(reading, data=request.data)

        if serializer.is_valid():

            reading = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": ("Water quality reading " "updated successfully."),
                    "data": WaterQualityReadingSerializer(reading).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):

        reading = self.get_object(pk)

        if reading is None:
            return Response(
                {
                    "success": False,
                    "message": ("Water quality reading " "not found."),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WaterQualityReadingSerializer(
            reading, data=request.data, partial=True
        )

        if serializer.is_valid():

            reading = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": ("Water quality reading " "updated successfully."),
                    "data": WaterQualityReadingSerializer(reading).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):

        reading = self.get_object(pk)

        if reading is None:
            return Response(
                {
                    "success": False,
                    "message": ("Water quality reading " "not found."),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        reading.delete()

        return Response(
            {
                "success": True,
                "message": ("Water quality reading " "deleted successfully."),
            },
            status=status.HTTP_200_OK,
        )
