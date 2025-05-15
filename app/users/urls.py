from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    OTPRegisterViewSet,
    OTPVerifyViewSet,
    OTPUnregisterViewSet,
    UserLoginViewSet,
    UserLogoutViewSet,
    UserRegistrationViewSet,
)

router = DefaultRouter()
router.register(r"otp/register", OTPRegisterViewSet, basename="users-otp-register")
router.register(r"otp/verify", OTPVerifyViewSet, basename="users-otp-verify")
router.register(r"otp/unregister", OTPUnregisterViewSet, basename="users-otp-unregister")
router.register(r"register", UserRegistrationViewSet, basename="users-register")
router.register(r"login", UserLoginViewSet, basename="users-login")
router.register(r"logout", UserLogoutViewSet, basename="users-logout")

urlpatterns = [
    path("", include(router.urls)),
    # 3rd-party JWT views
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
