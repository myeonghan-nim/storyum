from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import OTPRegisterSerializer


class OTPRegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/v1/users/otp/register/
    - 인증된 사용자의 OTP secret 생성 및 저장하고 프로비저닝 URI를 반환합니다.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OTPRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(context={"request": request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)
