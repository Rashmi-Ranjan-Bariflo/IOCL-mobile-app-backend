from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    ChangePasswordView,
    UserProfileView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login",),
    path("logout/", LogoutView.as_view(), name="logout",),
    path("change-password/",ChangePasswordView.as_view(),name="change-password",),
    path("profile/",UserProfileView.as_view(),name="profile",),
]
