from rest_framework import mixins, viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.serializers import UserLoginSerializer


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
