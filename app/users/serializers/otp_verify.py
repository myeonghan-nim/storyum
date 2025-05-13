import pyotp
from rest_framework import serializers


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
