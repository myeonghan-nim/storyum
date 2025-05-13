from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        error_messages={
            "invalid": "이메일 형식이 올바르지 않습니다.",
            "blank": "이메일을 입력해주세요.",
        },
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="이미 사용 중인 이메일입니다.",
            ),
        ],
    )
    username = serializers.CharField(
        max_length=150,
        error_messages={
            "blank": "사용자 이름을 입력해주세요.",
        },
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            "min_length": "비밀번호는 최소 8자 이상이어야 합니다.",
            "blank": "비밀번호를 입력해주세요.",
        },
    )
    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            "min_length": "비밀번호는 최소 8자 이상이어야 합니다.",
            "blank": "비밀번호를 입력해주세요.",
        },
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "confirm_password",
        )

    def validate(self, data):
        if data["password"] != data.pop("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "비밀번호가 일치하지 않습니다."})
        return data

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
        )


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = serializers.DictField(read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
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
