from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    SensorType,
    Sensor,
    SensorReading,
)

from .serializers import (
    SensorTypeSerializer,
    SensorSerializer,
    SensorReadingSerializer,
)


# ==========================================================
#                    SENSOR TYPE LIST / CREATE
# ==========================================================
class SensorTypeListCreateView(APIView):
    # ---------------------------------
    # GET
    # ---------------------------------
    def get(self, request):

        sensor_types = SensorType.objects.all()

        serializer = SensorTypeSerializer(
            sensor_types,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": "Sensor types retrieved successfully.",
                "count": sensor_types.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    # --------------------------------
    # POST
    # --------------------------------
    def post(self, request):

        serializer = SensorTypeSerializer(data=request.data)

        if serializer.is_valid():

            sensor_type = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Sensor type created successfully.",
                    "data": SensorTypeSerializer(sensor_type).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to create sensor type.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
#                    SENSOR TYPE DETAIL
# ==========================================================
class SensorTypeDetailView(APIView):

    def get_object(self, pk):

        try:
            return SensorType.objects.get(pk=pk)

        except SensorType.DoesNotExist:
            return None

    def get(self, request, pk):

        sensor_type = self.get_object(pk)

        if not sensor_type:
            return Response(
                {
                    "success": False,
                    "message": "Sensor type not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SensorTypeSerializer(sensor_type)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):

        sensor_type = self.get_object(pk)

        if not sensor_type:
            return Response(
                {
                    "success": False,
                    "message": "Sensor type not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SensorTypeSerializer(
            sensor_type,
            data=request.data,
        )

        if serializer.is_valid():

            sensor_type = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Sensor type updated successfully.",
                    "data": SensorTypeSerializer(sensor_type).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to update sensor type.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):

        sensor_type = self.get_object(pk)

        if not sensor_type:
            return Response(
                {
                    "success": False,
                    "message": "Sensor type not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SensorTypeSerializer(
            sensor_type,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            sensor_type = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Sensor type updated successfully.",
                    "data": SensorTypeSerializer(sensor_type).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to update sensor type.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):

        sensor_type = self.get_object(pk)

        if not sensor_type:
            return Response(
                {
                    "success": False,
                    "message": "Sensor type not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        sensor_type.delete()

        return Response(
            {
                "success": True,
                "message": "Sensor type deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                       SENSOR LIST / CREATE
# ==========================================================
class SensorListCreateView(APIView):

    def get(self, request):

        sensors = Sensor.objects.select_related(
            "sensor_type",
            "equipment",
        ).all()

        serializer = SensorSerializer(
            sensors,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": "Sensors retrieved successfully.",
                "count": sensors.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = SensorSerializer(data=request.data)

        if serializer.is_valid():

            sensor = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Sensor created successfully.",
                    "data": SensorSerializer(sensor).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to create sensor.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
#                       SENSOR DETAIL
# ==========================================================
class SensorDetailView(APIView):

    def get_object(self, pk):

        try:
            return Sensor.objects.select_related(
                "sensor_type",
                "equipment",
            ).get(pk=pk)

        except Sensor.DoesNotExist:
            return None

    def get(self, request, pk):

        sensor = self.get_object(pk)

        if not sensor:
            return Response(
                {
                    "success": False,
                    "message": "Sensor not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SensorSerializer(sensor)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):

        sensor = self.get_object(pk)

        if not sensor:
            return Response(
                {
                    "success": False,
                    "message": "Sensor not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SensorSerializer(
            sensor,
            data=request.data,
        )

        if serializer.is_valid():

            sensor = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Sensor updated successfully.",
                    "data": SensorSerializer(sensor).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to update sensor.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):

        sensor = self.get_object(pk)

        if not sensor:
            return Response(
                {
                    "success": False,
                    "message": "Sensor not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SensorSerializer(
            sensor,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            sensor = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Sensor updated successfully.",
                    "data": SensorSerializer(sensor).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to update sensor.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):

        sensor = self.get_object(pk)

        if not sensor:
            return Response(
                {
                    "success": False,
                    "message": "Sensor not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        sensor.delete()

        return Response(
            {
                "success": True,
                "message": "Sensor deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                 SENSOR READING LIST / CREATE
# ==========================================================
class SensorReadingListCreateView(APIView):

    def get(self, request):

        readings = SensorReading.objects.select_related(
            "sensor",
        ).all()

        # --------------------------------------------------
        # Optional sensor filter
        # --------------------------------------------------
        sensor_id = request.query_params.get("sensor")

        if sensor_id:
            readings = readings.filter(sensor_id=sensor_id)

        serializer = SensorReadingSerializer(
            readings,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": "Sensor readings retrieved successfully.",
                "count": readings.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = SensorReadingSerializer(data=request.data)

        if serializer.is_valid():

            reading = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Sensor reading created successfully.",
                    "data": SensorReadingSerializer(reading).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to create sensor reading.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
#                    SENSOR READING DETAIL
# ==========================================================
class SensorReadingDetailView(APIView):

    def get_object(self, pk):

        try:
            return SensorReading.objects.select_related(
                "sensor",
            ).get(pk=pk)

        except SensorReading.DoesNotExist:
            return None

    def get(self, request, pk):

        reading = self.get_object(pk)

        if not reading:
            return Response(
                {
                    "success": False,
                    "message": "Sensor reading not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SensorReadingSerializer(reading)

        return Response(
            {
                "success": True,
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
                    "message": "Sensor reading not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SensorReadingSerializer(
            reading,
            data=request.data,
        )

        if serializer.is_valid():

            reading = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Sensor reading updated successfully.",
                    "data": SensorReadingSerializer(reading).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to update sensor reading.",
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
                    "message": "Sensor reading not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SensorReadingSerializer(
            reading,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            reading = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Sensor reading updated successfully.",
                    "data": SensorReadingSerializer(reading).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to update sensor reading.",
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
                    "message": "Sensor reading not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        reading.delete()

        return Response(
            {
                "success": True,
                "message": "Sensor reading deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
