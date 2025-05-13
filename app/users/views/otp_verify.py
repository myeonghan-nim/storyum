from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import OTPVerifySerializer


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
