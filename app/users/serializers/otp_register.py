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
