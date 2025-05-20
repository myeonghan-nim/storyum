from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import OTPRegisterSerializer, OTPVerifySerializer, OTPUnregisterSerializer


@extend_schema(
    tags=["OTP"],
    summary="OTP 등록",
    description="OTP를 등록합니다.",
    request=OTPRegisterSerializer,
    responses={
        200: OpenApiResponse(
            response=OTPRegisterSerializer,
            description="OTP 등록 성공",
            examples=[
                OpenApiExample(
                    "OTP 등록 성공 예시",
                    summary="정상 등록 후 반환값",
                    value={"secret": "base32_secret", "otpauth_url": "otpauth_url"},
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(OpenApiTypes.STR, description="Authentication credentials were not provided."),
    },
    examples=[
        OpenApiExample(
            "OTP 등록 예시",
            summary="요청 페이로드",
            value=None,
            request_only=True,
        )
    ],
)
class OTPRegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OTPRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(context={"request": request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["OTP"],
    summary="OTP 인증",
    description="OTP 인증을 요청합니다.",
    request=OTPVerifySerializer,
    responses={
        200: OpenApiResponse(
            response=OTPVerifySerializer,
            description="OTP 인증 성공",
            examples=[
                OpenApiExample(
                    "OTP 인증 성공 예시",
                    summary="정상 인증 후 반환값",
                    value={"detail": "OTP가 활성화되었습니다."},
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(OpenApiTypes.OBJECT, description="잘못된 요청입니다. (field: [error, …] 구조)"),
        401: OpenApiResponse(OpenApiTypes.STR, description="Authentication credentials were not provided."),
    },
    examples=[
        OpenApiExample(
            "OTP 인증 예시",
            summary="요청 페이로드",
            value={"code": "123456"},
            request_only=True,
        )
    ],
)
class OTPVerifyViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OTPVerifySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["OTP"],
    summary="OTP 등록 해제",
    description="OTP 등록 해제를 요청합니다.",
    request=OTPUnregisterSerializer,
    responses={
        200: OpenApiResponse(
            response=OTPUnregisterSerializer,
            description="OTP 등록 해제 성공",
            examples=[
                OpenApiExample(
                    "OTP 등록 해제 성공 예시",
                    summary="정상 해제 후 반환값",
                    value={"detail": "OTP 등록 해제가 완료되었습니다."},
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(OpenApiTypes.OBJECT, description="잘못된 요청입니다. (field: [error, …] 구조)"),
        401: OpenApiResponse(OpenApiTypes.STR, description="Authentication credentials were not provided."),
    },
    examples=[
        OpenApiExample(
            "OTP 등록 해제 예시",
            summary="요청 페이로드",
            value={"code": "123456"},
            request_only=True,
        )
    ],
)
class OTPUnregisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OTPUnregisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "OTP 등록 해제가 완료되었습니다."}, status=status.HTTP_200_OK)
