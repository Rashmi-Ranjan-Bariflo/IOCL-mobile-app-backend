from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    AlertType,
    Alert,
    AlertNotification,
)

from .serializers import (
    AlertTypeSerializer,
    AlertSerializer,
    AlertNotificationSerializer,
)

# ==========================================================
#                      ALERT TYPE
# ==========================================================


class AlertTypeListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        alert_types = AlertType.objects.all()

        serializer = AlertTypeSerializer(alert_types, many=True)

        return Response(
            {
                "success": True,
                "message": "Alert types fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = AlertTypeSerializer(data=request.data)

        if serializer.is_valid():

            alert_type = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Alert type created successfully.",
                    "data": AlertTypeSerializer(alert_type).data,
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
#                   ALERT TYPE DETAIL
# ==========================================================


class AlertTypeDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):

        try:
            return AlertType.objects.get(pk=pk)

        except AlertType.DoesNotExist:
            return None

    def get(self, request, pk):

        alert_type = self.get_object(pk)

        if not alert_type:

            return Response(
                {
                    "success": False,
                    "message": "Alert type not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AlertTypeSerializer(alert_type)

        return Response(
            {
                "success": True,
                "message": "Alert type fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):

        alert_type = self.get_object(pk)

        if not alert_type:

            return Response(
                {
                    "success": False,
                    "message": "Alert type not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AlertTypeSerializer(alert_type, data=request.data)

        if serializer.is_valid():

            alert_type = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Alert type updated successfully.",
                    "data": AlertTypeSerializer(alert_type).data,
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

        alert_type = self.get_object(pk)

        if not alert_type:

            return Response(
                {
                    "success": False,
                    "message": "Alert type not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AlertTypeSerializer(alert_type, data=request.data, partial=True)

        if serializer.is_valid():

            alert_type = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Alert type updated successfully.",
                    "data": AlertTypeSerializer(alert_type).data,
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

        alert_type = self.get_object(pk)

        if not alert_type:

            return Response(
                {
                    "success": False,
                    "message": "Alert type not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        alert_type.delete()

        return Response(
            {
                "success": True,
                "message": "Alert type deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                         ALERT
# ==========================================================


class AlertListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        alerts = Alert.objects.select_related(
            "plant",
            "plant_stage",
            "equipment",
            "sensor",
            "parameter",
            "alert_type",
        ).all()

        serializer = AlertSerializer(alerts, many=True)

        return Response(
            {
                "success": True,
                "message": "Alerts fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = AlertSerializer(data=request.data)

        if serializer.is_valid():

            alert = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Alert created successfully.",
                    "data": AlertSerializer(alert).data,
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
#                       ALERT DETAIL
# ==========================================================


class AlertDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):

        try:
            return Alert.objects.select_related(
                "plant",
                "plant_stage",
                "equipment",
                "sensor",
                "parameter",
                "alert_type",
            ).get(pk=pk)

        except Alert.DoesNotExist:
            return None

    def get(self, request, pk):

        alert = self.get_object(pk)

        if not alert:

            return Response(
                {
                    "success": False,
                    "message": "Alert not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AlertSerializer(alert)

        return Response(
            {
                "success": True,
                "message": "Alert fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):

        alert = self.get_object(pk)

        if not alert:

            return Response(
                {
                    "success": False,
                    "message": "Alert not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AlertSerializer(alert, data=request.data)

        if serializer.is_valid():

            alert = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Alert updated successfully.",
                    "data": AlertSerializer(alert).data,
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

        alert = self.get_object(pk)

        if not alert:

            return Response(
                {
                    "success": False,
                    "message": "Alert not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AlertSerializer(alert, data=request.data, partial=True)

        if serializer.is_valid():

            alert = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Alert updated successfully.",
                    "data": AlertSerializer(alert).data,
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

        alert = self.get_object(pk)

        if not alert:

            return Response(
                {
                    "success": False,
                    "message": "Alert not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        alert.delete()

        return Response(
            {
                "success": True,
                "message": "Alert deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                  ALERT NOTIFICATION
# ==========================================================


class AlertNotificationListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        notifications = AlertNotification.objects.select_related("alert").all()

        serializer = AlertNotificationSerializer(notifications, many=True)

        return Response(
            {
                "success": True,
                "message": "Alert notifications fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = AlertNotificationSerializer(data=request.data)

        if serializer.is_valid():

            notification = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Alert notification created successfully.",
                    "data": AlertNotificationSerializer(notification).data,
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
#              ALERT NOTIFICATION DETAIL
# ==========================================================


class AlertNotificationDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):

        try:
            return AlertNotification.objects.select_related("alert").get(pk=pk)

        except AlertNotification.DoesNotExist:
            return None

    def get(self, request, pk):

        notification = self.get_object(pk)

        if not notification:

            return Response(
                {
                    "success": False,
                    "message": "Alert notification not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AlertNotificationSerializer(notification)

        return Response(
            {
                "success": True,
                "message": "Alert notification fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):

        notification = self.get_object(pk)

        if not notification:

            return Response(
                {
                    "success": False,
                    "message": "Alert notification not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AlertNotificationSerializer(notification, data=request.data)

        if serializer.is_valid():

            notification = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Alert notification updated successfully.",
                    "data": AlertNotificationSerializer(notification).data,
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

        notification = self.get_object(pk)

        if not notification:

            return Response(
                {
                    "success": False,
                    "message": "Alert notification not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AlertNotificationSerializer(
            notification, data=request.data, partial=True
        )

        if serializer.is_valid():

            notification = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Alert notification updated successfully.",
                    "data": AlertNotificationSerializer(notification).data,
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

        notification = self.get_object(pk)

        if not notification:

            return Response(
                {
                    "success": False,
                    "message": "Alert notification not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        notification.delete()

        return Response(
            {
                "success": True,
                "message": "Alert notification deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
