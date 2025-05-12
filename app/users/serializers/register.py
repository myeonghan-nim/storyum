from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

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
