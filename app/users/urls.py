from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserLoginViewSet,
    UserRegistrationViewSet,
)

router = DefaultRouter()
router.register(r"register", UserRegistrationViewSet, basename="users-register")
router.register(r"login", UserLoginViewSet, basename="users-login")

urlpatterns = [
    path("", include(router.urls)),
]
