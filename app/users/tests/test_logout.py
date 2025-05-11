import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestUserLogout:
    @pytest.fixture(autouse=True)
    def setup(self, django_user_model):
        self.user = django_user_model.objects.create_user(email="user@example.com", password="strong-pass123", username="testuser")

        self.client = APIClient()
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

        login_url = reverse("users-login-list")
        resp = self.client.post(login_url, {"email": self.user.email, "password": "strong-pass123"}, format="json")

        self.access_token = resp.data["token"]["access"]
        self.refresh_token = resp.data["token"]["refresh"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_logout_success(self):
        url = reverse("users-logout-list")
        resp = self.client.post(url, {"refresh": self.refresh_token}, format="json")
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_refresh_fail_blacklisted_token(self):
        logout_url = reverse("users-logout-list")
        refresh_url = reverse("token_refresh")

        resp1 = self.client.post(logout_url, {"refresh": self.refresh_token}, format="json")
        assert resp1.status_code == status.HTTP_204_NO_CONTENT

        resp2 = self.client.post(refresh_url, {"refresh": self.refresh_token}, format="json")
        assert resp2.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in resp2.data
