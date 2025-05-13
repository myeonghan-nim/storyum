import pytest
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
