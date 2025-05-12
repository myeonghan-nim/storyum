import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestUserLogoutAPI:
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

        self.url = reverse("users-logout-list")

    def test_logout_success(self):
        response = self.client.post(self.url, {"refresh": self.refresh_token}, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_refresh_fail_blacklisted_token(self):
        response1 = self.client.post(self.url, {"refresh": self.refresh_token}, format="json")
        assert response1.status_code == status.HTTP_204_NO_CONTENT

        refresh_url = reverse("token_refresh")

        response2 = self.client.post(refresh_url, {"refresh": self.refresh_token}, format="json")
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response2.data
