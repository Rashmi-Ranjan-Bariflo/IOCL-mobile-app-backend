from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {
                    "success": False,
                    "message": "Email and password are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = email.strip().lower()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Invalid email or password.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {
                    "success": False,
                    "message": "User account is inactive.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.check_password(password):
            return Response(
                {
                    "success": False,
                    "message": "Invalid email or password.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "data": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(
            {
                "success": True,
                "message": "Logout successful.",
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not email:
            return Response(
                {
                    "success": False,
                    "message": "Email is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not old_password or not new_password or not confirm_password:
            return Response(
                {
                    "success": False,
                    "message": (
                        "Old password, new password and "
                        "confirm password are required."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = email.strip().lower()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "User not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not user.check_password(old_password):
            return Response(
                {
                    "success": False,
                    "message": "Old password is incorrect.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {
                    "success": False,
                    "message": ("New password and confirm password " "do not match."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_password) < 8:
            return Response(
                {
                    "success": False,
                    "message": "Password must be at least 8 characters.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if old_password == new_password:
            return Response(
                {
                    "success": False,
                    "message": ("New password must be different " "from old password."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])

        return Response(
            {
                "success": True,
                "message": "Password changed successfully.",
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get("email")

        if not email:
            return Response(
                {
                    "success": False,
                    "message": "Email is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email.strip().lower())
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "User not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "data": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {
                    "success": False,
                    "message": "Email is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email.strip().lower())
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "User not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserSerializer(
            user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Profile updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
