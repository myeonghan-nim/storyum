from rest_framework import mixins, viewsets, status, permissions
from rest_framework.response import Response

from users.serializers import UserRegistrationSerializer


class UserRegistrationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/v1/users/register/
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

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
