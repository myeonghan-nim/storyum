from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from users.serializers import ProfileSerializer


@extend_schema(
    tags=["Profile"],
    summary="프로필 생성",
    description="사용자가 프로필을 생성합니다.",
    request=ProfileSerializer,
    responses={
        201: OpenApiResponse(
            response=ProfileSerializer,
            description="프로필 생성 성공",
            examples=[
                OpenApiExample(
                    "프로필 생성 성공 예시",
                    summary="정상 프로필 생성 후 반환값",
                    value={
                        "id": 1,
                        "user": {"id": 1, "email": "testuser@example.com", "username": "testuser"},
                        "bio": "This is my bio.",
                        "avatar": "https://example.com/media/avatars/sample_avatar.jpg",
                        "website": "https://example.com",
                        "created_at": "2025-01-01T00:00:00Z",
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(OpenApiTypes.OBJECT, description="잘못된 요청입니다. (field: [error, …] 구조)"),
        401: OpenApiResponse(OpenApiTypes.STR, description="Authentication credentials were not provided."),
    },
    examples=[
        OpenApiExample(
            "프로필 생성 요청 예시",
            summary="요청 페이로드",
            value={"bio": "This is my bio.", "avatar": "sample_avatar.jpg", "website": "https://example.com"},
            request_only=True,
        )
    ],
)
class ProfileViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response(ProfileSerializer(profile, context={"request": request}).data, status=status.HTTP_201_CREATED)
