from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True, help_text="블랙리스트 처리할 리프레시 토큰")

    default_error_messages = {"bad_token": "유효하지 않거나 이미 블랙리스트된 토큰입니다."}

    def validate(self, attrs):
        self.token = attrs.get("refresh")
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail("bad_token")
