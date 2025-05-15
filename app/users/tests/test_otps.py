import pytest
import pyotp
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestOTPRegisterAPI:
    @pytest.fixture(autouse=True)
    def setup(self, django_user_model):
        self.user = django_user_model.objects.create_user(email="user@example.com", password="strong-pass123", username="testuser")

        self.client = APIClient()
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

        login_url = reverse("users-login-list")
        response = self.client.post(login_url, {"email": self.user.email, "password": "strong-pass123"}, format="json")
        self.access_token = response.data["token"]["access"]
        self.refresh_token = response.data["token"]["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.url = reverse("users-otp-register-list")

    def test_otp_register_success(self):
        response = self.client.post(self.url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "secret" in data and isinstance(data["secret"], str)
        assert "otpauth_url" in data and data["otpauth_url"].startswith("otpauth://")

        self.user.refresh_from_db()
        assert self.user.otp_secret == data["secret"]
        assert self.user.otp_enabled is False

    def test_otp_register_success_with_rotated_secret(self):
        response1 = self.client.post(self.url)
        secret1 = response1.json()["secret"]

        response2 = self.client.post(self.url)
        secret2 = response2.json()["secret"]

        assert secret1 != secret2

        self.user.refresh_from_db()
        assert self.user.otp_secret == secret2

    def test_otp_register_fail_unauthenticated(self):
        self.client.credentials()

        response = self.client.post(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_otp_register_fail_invalid_method(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


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


@pytest.mark.django_db
class OTPUnregisterAPI:
    @pytest.fixture(autouse=True)
    def setup(self, django_user_model):
        self.user = django_user_model.objects.create_user(email="user@example.com", password="strong-pass123", username="testuser")
        secret = pyotp.random_base32()
        self.user.otp_secret = secret
        self.user.otp_enabled = True
        self.user.save(update_fields=["otp_secret", "otp_enabled"])

        self.client = APIClient()
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

        login_url = reverse("users-login-list")
        tokens = self.client.post(login_url, {"email": "user@example.com", "password": "strong-pass123"}, format="json").data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['token']['access']}")

        self.url = reverse("users-otp-unregister-list")

    def test_unregister_success(self):
        totp = pyotp.TOTP(self.user.otp_secret)
        valid_code = totp.now()

        response = self.client.post(self.url, {"code": valid_code}, format="json")
        assert response.status_code == 200
        assert response.data.get("detail") == "OTP 등록 해제가 완료되었습니다."

        self.user.refresh_from_db()
        assert self.user.otp_secret == ""
        assert self.user.otp_enabled is False

    def test_unregister_fail_no_otp(self):
        self.user.otp_secret = ""
        self.user.otp_enabled = False
        self.user.save(update_fields=["otp_secret", "otp_enabled"])

        response = self.client.post(self.url, {"code": "123456"}, format="json")
        assert response.status_code == 400
        assert "code" in response.data
        assert response.data["code"][0] == "등록된 OTP가 없습니다."

    def test_unregister_fail_invalid_code(self):
        response = self.client.post(self.url, {"code": "000000"}, format="json")
        assert response.status_code == 400
        assert "code" in response.data
        assert response.data["code"][0] == "유효하지 않은 OTP 코드입니다."
