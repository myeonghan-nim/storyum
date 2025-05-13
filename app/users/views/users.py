from rest_framework import mixins, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.serializers import UserRegistrationSerializer, UserLoginSerializer, UserLogoutSerializer


class UserRegistrationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/v1/users/register/
    - Request body:
        {
            "email": "sampleuser@email.com",
            "username": "sampleuser",
            "password": "samplepassword",
            "confirm_password": "samplepassword"
        }
    - Response status: 201 Created
    - Response body:
        {
            "id": 1,
            "email": "sampleuser@email.com",
            "username": "sampleuser",
            "date_joined": "2025-01-01T00:00:00Z"
        }
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "date_joined": user.date_joined,
            },
            status=status.HTTP_201_CREATED,
        )


class UserLoginViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/v1/users/login/
    - Request body:
        {
            "email": "sampleuser@email.com",
            "password": "samplepassword"
        }
    - Response status: 200 OK
    - Response:
        {
            "token": {
                "refresh": "sample_refresh_token",
                "access": "sample_access_token"
            },
            "user": {
                "id": 1,
                "email": "sampleuser@email.com",
                "username": "sampleuser",
            }
        }
    """

    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(
            {
                "token": {
                    "refresh": data["refresh"],
                    "access": data["access"],
                },
                "user": data["user"],
            },
            status=status.HTTP_200_OK,
        )


class UserLogoutViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    POST /api/v1/users/logout/
    - Request body:
        {
            "refresh": "refresh_token"
        }
    - Response status: 204 NO CONTENT
    - Response body: None
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserLogoutSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
