from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import OTPRegisterSerializer


class OTPRegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/v1/users/otp/register/
    - Request body: None
    - Response status: 200 OK
    - Response body:
        {
            "secret": "base32_secret",
            "otpauth_url": "otpauth_url"
        }
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OTPRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(context={"request": request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)
