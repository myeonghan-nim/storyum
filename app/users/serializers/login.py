from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = serializers.DictField(read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise serializers.ValidationError({"non_field_errors": ["이메일 또는 비밀번호가 올바르지 않습니다."]})
        if not user.check_password(password):
            raise serializers.ValidationError({"non_field_errors": ["이메일 또는 비밀번호가 올바르지 않습니다."]})

        if not user.is_active:
            raise serializers.ValidationError({"non_field_errors": ["비활성화된 계정입니다."]})

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return {
            "refresh": str(refresh),
            "access": str(access),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            },
        }
