from django.urls import path
from rest_framework_simplejwt.views import (TokenRefreshView,)
from .views import (
    ResendOTPView,
    SignupView,
    LoginView,
    LogoutView,
    SendOtp,
    ResetPasswordView,
    ChangePasswordView,
    UserProfileView,
    VerifyOTPView
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup",),
    path("login/", LoginView.as_view(), name="login",),
    path("logout/", LogoutView.as_view(), name="logout",),
    path("send-otp/", SendOtp.as_view(),name="forgot-password",),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password",),
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp",),
    path("change-password/", ChangePasswordView.as_view(), name="change-password",),
    path("profile/", UserProfileView.as_view(), name="profile",),
    path("token/refresh/",TokenRefreshView.as_view(),name="token-refresh",),
]