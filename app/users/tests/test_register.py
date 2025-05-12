import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestUserRegisterAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_model = get_user_model()

        self.client = APIClient()
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

        self.url = reverse("users-register-list")

    def test_register_success(self):
        payload = {"email": "testuser@example.com", "username": "testuser", "password": "strongPassword123", "confirm_password": "strongPassword123"}

        response = self.client.post(self.url, payload, format="json")
        assert response.status_code == 201

        data = response.data
        assert "id" in data and "date_joined" in data
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]
        assert self.user_model.objects.filter(email=payload["email"]).exists()

    @pytest.mark.parametrize(
        "payload, field, expected",
        [
            ({"email": "", "username": "u", "password": "p" * 8, "confirm_password": "p" * 8}, "email", ["이메일을 입력해주세요."]),
            ({"email": "bad-email", "username": "u", "password": "p" * 8, "confirm_password": "p" * 8}, "email", ["이메일 형식이 올바르지 않습니다."]),
            ({"email": "a@b", "username": "u", "password": "p" * 8, "confirm_password": "p" * 8}, "email", ["이메일 형식이 올바르지 않습니다."]),
            ({"email": "dup@example.com", "username": "u", "password": "p" * 8, "confirm_password": "p" * 8}, "email", ["이미 사용 중인 이메일입니다."]),
            ({"email": "x@example.com", "username": "", "password": "p" * 8, "confirm_password": "p" * 8}, "username", ["사용자 이름을 입력해주세요."]),
            ({"email": "x@example.com", "username": "u", "password": "short", "confirm_password": "short"}, "password", ["비밀번호는 최소 8자 이상이어야 합니다."]),
            ({"email": "x@example.com", "username": "u", "password": "password123", "confirm_password": "pass123"}, "confirm_password", ["비밀번호는 최소 8자 이상이어야 합니다."]),
        ],
    )
    def test_register_fail_validation(self, payload, field, expected):
        if payload.get("email") == "dup@example.com":
            self.user_model.objects.create_user(email="dup@example.com", username="dup", password="dummy1234")

        response = self.client.post(self.url, payload, format="json")
        assert response.status_code == 400
        assert response.data[field] == expected
