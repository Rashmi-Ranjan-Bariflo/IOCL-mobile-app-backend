import random

from datetime import timedelta

from django.core.mail import send_mail
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import CustomJWTAuthentication
from .models import User
from .serializers import UserSerializer


# ==========================================================
#                      SIGN UP
# ==========================================================
class SignupView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        email = request.data.get("email")
        phone = request.data.get("phone")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        # --------------------------------------------------
        # Validate required fields
        # --------------------------------------------------
        if not email or not password or not confirm_password:
            return Response(
                {
                    "success": False,
                    "message": (
                        "Email, password and confirm password " "are required."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = str(email).strip().lower()

        # --------------------------------------------------
        # Check password confirmation
        # --------------------------------------------------
        if password != confirm_password:
            return Response(
                {
                    "success": False,
                    "message": ("Password and confirm password " "do not match."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Password length
        # --------------------------------------------------
        if len(password) < 6:
            return Response(
                {
                    "success": False,
                    "message": ("Password must be at least 6 characters."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Check email already exists
        # --------------------------------------------------
        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {
                    "success": False,
                    "message": "Email is already registered.",
                },
                status=status.HTTP_409_CONFLICT,
            )

        # --------------------------------------------------
        # Validate phone
        # --------------------------------------------------
        if phone:

            phone = str(phone).strip()

            if not phone.isdigit():
                return Response(
                    {
                        "success": False,
                        "message": ("Phone number must contain " "only digits."),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if len(phone) < 10 or len(phone) > 15:
                return Response(
                    {
                        "success": False,
                        "message": (
                            "Phone number must be between " "10 and 15 digits."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # --------------------------------------------------
        # Create user
        # --------------------------------------------------
        user = User(
            email=email,
            phone=phone,
            is_active=True,
        )

        user.set_password(password)
        user.save()

        # --------------------------------------------------
        # Generate JWT
        # --------------------------------------------------
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "message": "Account created successfully.",
                "data": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
#                      SIGN IN / LOGIN
# ==========================================================
class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        email = request.data.get("email")
        password = request.data.get("password")

        # --------------------------------------------------
        # Validate input
        # --------------------------------------------------
        if email is None or password is None:
            return Response(
                {
                    "success": False,
                    "message": ("Email and password are required."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = str(email).strip().lower()
        password = str(password)

        # --------------------------------------------------
        # Find user
        # --------------------------------------------------
        try:
            user = User.objects.get(email__iexact=email)

        except User.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Invalid email or password.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # --------------------------------------------------
        # Check active
        # --------------------------------------------------
        if not user.is_active:

            return Response(
                {
                    "success": False,
                    "message": "User account is inactive.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------
        # Check password
        # --------------------------------------------------
        if not user.check_password(password):

            return Response(
                {
                    "success": False,
                    "message": "Invalid email or password.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # --------------------------------------------------
        # Generate JWT
        # --------------------------------------------------
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "data": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                      USER LOGOUT
# ==========================================================
class LogoutView(APIView):

    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:

            return Response(
                {
                    "success": False,
                    "message": "Refresh token is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            token = RefreshToken(refresh_token)

            # Enable this if JWT blacklist is configured.
            #
            # token.blacklist()

        except TokenError:

            return Response(
                {
                    "success": False,
                    "message": ("Invalid or expired refresh token."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "message": "Logout successful.",
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                  FORGOT PASSWORD & SEND OTP
# ==========================================================
class SendOtp(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        email = request.data.get("email")

        # --------------------------------------------------
        # Validate email
        # --------------------------------------------------
        if not email:

            return Response(
                {
                    "success": False,
                    "message": "Email is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = str(email).strip().lower()

        # --------------------------------------------------
        # Find user
        # --------------------------------------------------
        try:

            user = User.objects.get(email__iexact=email)

        except User.DoesNotExist:

            return Response(
                {
                    "success": True,
                    "message": ("If the email is registered, " "an OTP has been sent."),
                },
                status=status.HTTP_200_OK,
            )

        # --------------------------------------------------
        # Check active
        # --------------------------------------------------
        if not user.is_active:

            return Response(
                {
                    "success": False,
                    "message": "User account is inactive.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------
        # Generate 6 digit OTP
        # --------------------------------------------------
        otp = str(random.randint(100000, 999999))

        # --------------------------------------------------
        # Save OTP
        # --------------------------------------------------
        user.reset_otp = otp
        user.reset_otp_created_at = timezone.now()

        user.save(
            update_fields=[
                "reset_otp",
                "reset_otp_created_at",
                "updated_at",
            ]
        )

        # --------------------------------------------------
        # Send email
        # --------------------------------------------------
        send_mail(
            subject="Password Reset OTP",
            message=(
                f"Hello,\n\n"
                f"Your password reset OTP is: {otp}\n\n"
                f"This OTP is valid for 10 minutes.\n\n"
                f"If you did not request a password reset, "
                f"please ignore this email.\n\n"
                f"Regards,\n"
                f"Bariflo Labs Technical Team"
            ),
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {
                "success": True,
                "message": ("OTP has been sent to your " "registered email."),
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                  RESET PASSWORD & VERIFY OTP
# ==========================================================
class ResetPasswordView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        # --------------------------------------------------
        # Validate input
        # --------------------------------------------------
        if not all(
            [
                email,
                otp,
                new_password,
                confirm_password,
            ]
        ):

            return Response(
                {
                    "success": False,
                    "message": (
                        "Email, OTP, new password and " "confirm password are required."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = str(email).strip().lower()
        otp = str(otp).strip()

        # --------------------------------------------------
        # Find user
        # --------------------------------------------------
        try:

            user = User.objects.get(email__iexact=email)

        except User.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Invalid reset request.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Check OTP exists
        # --------------------------------------------------
        if not user.reset_otp:

            return Response(
                {
                    "success": False,
                    "message": "Invalid or expired OTP.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Check OTP
        # --------------------------------------------------
        if user.reset_otp != otp:

            return Response(
                {
                    "success": False,
                    "message": "Invalid OTP.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Check OTP creation time
        # --------------------------------------------------
        if not user.reset_otp_created_at:

            return Response(
                {
                    "success": False,
                    "message": "Invalid or expired OTP.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # OTP expiry - 10 minutes
        # --------------------------------------------------
        otp_expiry = user.reset_otp_created_at + timedelta(minutes=10)

        if timezone.now() > otp_expiry:

            user.reset_otp = None
            user.reset_otp_created_at = None

            user.save(
                update_fields=[
                    "reset_otp",
                    "reset_otp_created_at",
                    "updated_at",
                ]
            )

            return Response(
                {
                    "success": False,
                    "message": ("OTP has expired. " "Please request a new OTP."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Check password match
        # --------------------------------------------------
        if new_password != confirm_password:

            return Response(
                {
                    "success": False,
                    "message": ("New password and confirm password " "do not match."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Password length
        # --------------------------------------------------
        if len(new_password) < 6:

            return Response(
                {
                    "success": False,
                    "message": ("Password must be at least " "6 characters."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Set new password
        # --------------------------------------------------
        user.set_password(new_password)

        # Clear OTP
        user.reset_otp = None
        user.reset_otp_created_at = None

        user.save(
            update_fields=[
                "password",
                "reset_otp",
                "reset_otp_created_at",
                "updated_at",
            ]
        )

        return Response(
            {
                "success": True,
                "message": ("Password reset successfully."),
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                    RESEND OTP
# ==========================================================
class ResendOTPView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        email = request.data.get("email")

        # --------------------------------------------------
        # Validate email
        # --------------------------------------------------
        if not email:
            return Response(
                {
                    "success": False,
                    "message": "Email is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = str(email).strip().lower()

        # --------------------------------------------------
        # Find user
        # --------------------------------------------------
        try:
            user = User.objects.get(email__iexact=email)

        except User.DoesNotExist:

            return Response(
                {
                    "success": True,
                    "message": (
                        "If the email is registered, " "a new OTP has been sent."
                    ),
                },
                status=status.HTTP_200_OK,
            )

        # --------------------------------------------------
        # Check active
        # --------------------------------------------------
        if not user.is_active:
            return Response(
                {
                    "success": False,
                    "message": "User account is inactive.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------
        # Generate new OTP
        # --------------------------------------------------
        otp = str(random.randint(100000, 999999))

        # --------------------------------------------------
        # Update OTP
        # --------------------------------------------------
        user.reset_otp = otp
        user.reset_otp_created_at = timezone.now()

        user.save(
            update_fields=[
                "reset_otp",
                "reset_otp_created_at",
                "updated_at",
            ]
        )

        # --------------------------------------------------
        # Send email
        # --------------------------------------------------
        send_mail(
            subject="Password Reset OTP",
            message=(
                f"Hello,\n\n"
                f"Your new password reset OTP is: {otp}\n\n"
                f"This OTP is valid for 10 minutes.\n\n"
                f"If you did not request a password reset, "
                f"please ignore this email.\n\n"
                f"Regards,\n"
                f"Bariflo Labs Technical Team"
            ),
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {
                "success": True,
                "message": ("A new OTP has been sent to your " "registered email."),
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                      CHANGE PASSWORD
# ==========================================================
class ChangePasswordView(APIView):

    authentication_classes = [CustomJWTAuthentication]

    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user

        old_password = request.data.get("old_password")

        new_password = request.data.get("new_password")

        confirm_password = request.data.get("confirm_password")

        # --------------------------------------------------
        # Validate input
        # --------------------------------------------------
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

        # --------------------------------------------------
        # Check old password
        # --------------------------------------------------
        if not user.check_password(old_password):

            return Response(
                {
                    "success": False,
                    "message": "Old password is incorrect.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Check new password
        # --------------------------------------------------
        if new_password != confirm_password:

            return Response(
                {
                    "success": False,
                    "message": ("New password and confirm password " "do not match."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Check password length
        # --------------------------------------------------
        if len(new_password) < 6:

            return Response(
                {
                    "success": False,
                    "message": ("Password must be at least " "6 characters."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Check same password
        # --------------------------------------------------
        if user.check_password(new_password):

            return Response(
                {
                    "success": False,
                    "message": ("New password must be different " "from old password."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Update password
        # --------------------------------------------------
        user.set_password(new_password)

        user.save(
            update_fields=[
                "password",
                "updated_at",
            ]
        )

        return Response(
            {
                "success": True,
                "message": ("Password changed successfully."),
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
#                      USER PROFILE
# ==========================================================
class UserProfileView(APIView):

    authentication_classes = [CustomJWTAuthentication]

    permission_classes = [IsAuthenticated]

    # ------------------------------------------------------
    # GET PROFILE
    # ------------------------------------------------------
    def get(self, request):

        user = request.user

        return Response(
            {
                "success": True,
                "data": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------
    # UPDATE PROFILE
    # ------------------------------------------------------
    def put(self, request):

        user = request.user

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
                "message": ("Profile updated successfully."),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
