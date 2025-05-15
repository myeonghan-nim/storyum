from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import OTPRegisterSerializer, OTPVerifySerializer, OTPUnregisterSerializer


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


class OTPVerifyViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/v1/users/otp/verify/
    - Request body:
        {
            "code": "123456"
        }
    - Response status: 200 OK
    - Response body:
        {
            "detail": "OTP가 활성화되었습니다."
        }
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OTPVerifySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)


class OTPUnregisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/v1/users/otp/unregister/
    - Request body:
        {
            "code": "123456"
        }
    - Response status: 200 OK
    - Response body:
        {
            "detail": "OTP 등록 해제가 완료되었습니다."
        }
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OTPUnregisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "OTP 등록 해제가 완료되었습니다."}, status=status.HTTP_200_OK)
