import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestUserLoginAPI:
    @pytest.fixture(autouse=True)
    def setup(self, django_user_model):
        self.user = django_user_model.objects.create_user(email="user@example.com", password="strong-pass123", username="testuser")

        self.client = APIClient()
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

        self.url = reverse("users-login-list")

    def test_login_success(self):
        payload = {"email": "user@example.com", "password": "strong-pass123"}

        response = self.client.post(self.url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "refresh" in response.data["token"]
        assert "access" in response.data["token"]
        assert response.data["user"]["email"] == "user@example.com"

    def test_login_fail_wrong_credentials(self):
        payload = {"email": "user@example.com", "password": "wrongpass"}

        response = self.client.post(self.url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert "이메일 또는 비밀번호가 올바르지 않습니다." in response.data["non_field_errors"][0]

    def test_login_fail_user_inactive(self):
        self.user.is_active = False
        self.user.save()

        payload = {"email": "user@example.com", "password": "strong-pass123"}

        response = self.client.post(self.url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert "비활성화된 계정입니다." in response.data["non_field_errors"][0]
