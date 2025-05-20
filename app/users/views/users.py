from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.serializers import UserRegistrationSerializer, UserLoginSerializer, UserLogoutSerializer, UserWithdrawalSerializer


@extend_schema(
    tags=["User Management"],
    summary="회원가입",
    description="이메일, 사용자 이름, 비밀번호를 사용하여 회원가입합니다.",
    request=UserRegistrationSerializer,
    responses={
        201: OpenApiResponse(
            response=UserRegistrationSerializer,
            description="회원가입 성공",
            examples=[
                OpenApiExample(
                    "회원가입 성공 예시",
                    summary="정상 가입 후 반환값",
                    value={"id": 1, "email": "testuser@example.com", "username": "testuser", "date_joined": "2025-01-01T00:00:00Z"},
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(OpenApiTypes.OBJECT, description="잘못된 요청입니다. (field: [error, …] 구조)"),
    },
    examples=[
        OpenApiExample(
            "회원가입 요청 예시",
            summary="요청 페이로드",
            value={"email": "testuser@example.com", "username": "testuser", "password": "testpassword", "confirm_password": "testpassword"},
            request_only=True,
        )
    ],
)
class UserRegistrationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
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


@extend_schema(
    tags=["Authentication"],
    summary="로그인",
    description="이메일, 비밀번호를 사용하여 로그인합니다.",
    request=UserLoginSerializer,
    responses={
        200: OpenApiResponse(
            response=UserLoginSerializer,
            description="로그인 성공",
            examples=[
                OpenApiExample(
                    "로그인 성공 예시",
                    summary="정상 로그인 후 반환값",
                    value={
                        "token": {"refresh": "sample_refresh_token", "access": "sample_access_token"},
                        "user": {"id": 1, "email": "testuser@example.com", "username": "testuser"},
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(OpenApiTypes.OBJECT, description="잘못된 요청입니다. (field: [error, …] 구조)"),
    },
    examples=[
        OpenApiExample(
            "로그인 요청 예시",
            summary="요청 페이로드",
            value={"email": "testuser@example.com", "password": "testpassword"},
            request_only=True,
        )
    ],
)
class UserLoginViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
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


@extend_schema(
    tags=["Authentication"],
    summary="로그아웃",
    description="로그인한 사용자가 로그아웃합니다.",
    request=UserLogoutSerializer,
    responses={
        204: OpenApiResponse(
            response=UserLogoutSerializer,
            description="로그아웃 성공",
            examples=[
                OpenApiExample(
                    "로그아웃 성공 예시",
                    summary="정상 로그아웃 후 반환값",
                    value=None,
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(OpenApiTypes.OBJECT, description="잘못된 요청입니다. (field: [error, …] 구조)"),
        401: OpenApiResponse(OpenApiTypes.STR, description="Authentication credentials were not provided."),
    },
    examples=[
        OpenApiExample(
            "로그아웃 요청 예시",
            summary="요청 페이로드",
            value={"refresh": "sample_refresh_token"},
            request_only=True,
        )
    ],
)
class UserLogoutViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLogoutSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["User Management"],
    summary="회원 탈퇴",
    description="회원 탈퇴를 요청합니다.",
    request=UserWithdrawalSerializer,
    responses={
        204: OpenApiResponse(
            response=UserWithdrawalSerializer,
            description="회원 탈퇴 성공",
            examples=[
                OpenApiExample(
                    "회원 탈퇴 성공 예시",
                    summary="정상 탈퇴 후 반환값",
                    value=None,
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(OpenApiTypes.OBJECT, description="잘못된 요청입니다. (field: [error, …] 구조)"),
        401: OpenApiResponse(OpenApiTypes.STR, description="Authentication credentials were not provided."),
    },
    examples=[
        OpenApiExample(
            "회원 탈퇴 요청 예시",
            summary="요청 페이로드",
            value={"otp_code": "sample_otp_code"},
            request_only=True,
        )
    ],
)
class UserWithdrawalViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserWithdrawalSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
