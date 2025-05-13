import pyotp
from rest_framework import serializers


class OTPRegisterSerializer(serializers.Serializer):
    secret = serializers.CharField(read_only=True)
    otpauth_url = serializers.CharField(read_only=True)

    def create(self, validated_data):
        user = self.context["request"].user

        secret = pyotp.random_base32()
        user.otp_secret = secret
        user.otp_enabled = False
        user.save(update_fields=["otp_secret", "otp_enabled"])

        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=user.email, issuer_name="storyum")

        return {"secret": secret, "otpauth_url": uri}


class OTPVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)

    def validate_code(self, value):
        user = self.context["request"].user

        secret = getattr(user, "otp_secret", None)
        if not secret:
            raise serializers.ValidationError("OTP secret이 등록되지 않았습니다.")

        totp = pyotp.TOTP(secret)
        if not totp.verify(value):
            raise serializers.ValidationError("유효하지 않은 OTP 코드입니다.")

        return value

    def save(self):
        user = self.context["request"].user
        user.otp_enabled = True
        user.save(update_fields=["otp_enabled"])
        return {"detail": "OTP가 활성화되었습니다."}
