from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import UserLogoutSerializer


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
