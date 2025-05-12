import pyotp
from rest_framework import serializers


class OTPRegisterSerializer(serializers.Serializer):
    """
    OTP 등록용 Serializer
    생성된 secret, otpauth_url(provisioning URI)을 반환
    """

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
