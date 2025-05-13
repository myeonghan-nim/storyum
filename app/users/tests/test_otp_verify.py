import pytest
import pyotp
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestOTPVerifyAPI:
    @pytest.fixture(autouse=True)
    def setup(self, django_user_model):
        self.user = django_user_model.objects.create_user(email="user@example.com", password="strong-pass123", username="testuser")
        self.user.otp_secret = pyotp.random_base32()
        self.user.save(update_fields=["otp_secret"])

        self.client = APIClient()
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

        login_url = reverse("users-login-list")
        tokens = self.client.post(login_url, {"email": "user@example.com", "password": "strong-pass123"}, format="json").data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['token']['access']}")

        self.url = reverse("users-otp-verify-list")

    def test_otp_verify_success(self):
        totp = pyotp.TOTP(self.user.otp_secret)
        code = totp.now()

        response = self.client.post(self.url, {"code": code}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "OTP가 활성화되었습니다."

        self.user.refresh_from_db()
        assert self.user.otp_enabled is True

    def test_otp_verify_fail_invalid_code(self):
        response = self.client.post(self.url, {"code": "000000"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "code" in response.data
        assert response.data["code"][0] == "유효하지 않은 OTP 코드입니다."
