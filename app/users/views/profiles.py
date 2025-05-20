from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from users.serializers import ProfileSerializer


class ProfileViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/v1/profiles/
    - Request Body:
        {
            "bio": "This is my bio.",
            "avatar": "sample_avatar.jpg",
            "website": "https://example.com"
        }
    - Response Status: 201 Created
    - Response Body:
        {
            "id": 1,
            "user": {
                "id": 1,
                "email": "sample_user@example.com",
                "username": "sample_user"
            },
            "bio": "This is my bio.",
            "avatar": "https://example.com/media/avatars/sample_avatar.jpg",
            "website": "https://example.com",
            "created_at": "2025-01-01T00:00:00Z"
        }
    """

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response(ProfileSerializer(profile, context={"request": request}).data, status=status.HTTP_201_CREATED)
