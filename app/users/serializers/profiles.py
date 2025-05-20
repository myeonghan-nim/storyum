from rest_framework import serializers
from django.contrib.auth import get_user_model

from users.models import Profile

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    bio = serializers.CharField(max_length=255, allow_blank=True, error_messages={"max_length": "소개는 255자 이하여야 합니다."})
    avatar = serializers.ImageField(required=False, allow_null=True)
    website = serializers.URLField(required=False, allow_blank=True, error_messages={"invalid": "올바른 URL을 입력해주세요."})

    class Meta:
        model = Profile
        fields = ["id", "user", "bio", "avatar", "website", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        if hasattr(user, "profile"):
            raise serializers.ValidationError({"invalid": "프로필이 이미 존재합니다."})
        return attrs

    def validate_website(self, value):
        if value and not (value.startswith("http://") or value.startswith("https://")):
            raise serializers.ValidationError("올바른 URL을 입력해주세요.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        return Profile.objects.create(user=request.user, **validated_data)
