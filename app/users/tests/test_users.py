import pyotp
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
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
        assert response.status_code == status.HTTP_201_CREATED

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
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data[field] == expected


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

    def test_logout_fail_no_refresh_token(self):
        response = self.client.post(self.url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "refresh" in response.data

    def test_logout_fail_invalid_refresh_token(self):
        response = self.client.post(self.url, {"refresh": "invalid-token"}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.data

    def test_logout_fail_blacklisted_token(self):
        response1 = self.client.post(self.url, {"refresh": self.refresh_token}, format="json")
        assert response1.status_code == status.HTTP_204_NO_CONTENT

        response2 = self.client.post(self.url, {"refresh": self.refresh_token}, format="json")
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response2.data

    def test_refresh_fail_blacklisted_token(self):
        response1 = self.client.post(self.url, {"refresh": self.refresh_token}, format="json")
        assert response1.status_code == status.HTTP_204_NO_CONTENT

        refresh_url = reverse("token_refresh")

        response2 = self.client.post(refresh_url, {"refresh": self.refresh_token}, format="json")
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response2.data


@pytest.mark.django_db
class TestUserWithdrawalAPI:
    @pytest.fixture(autouse=True)
    def setup(self, django_user_model):
        self.user_model = django_user_model
        self.user = self.user_model.objects.create_user(email="user@example.com", password="strong-pass123", username="testuser")

        self.client = APIClient()
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

        login_url = reverse("users-login-list")
        response = self.client.post(login_url, {"email": self.user.email, "password": "strong-pass123"}, format="json")
        self.access_token = response.data["token"]["access"]
        self.refresh_token = response.data["token"]["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.url = reverse("users-withdraw-list")

    def test_withdraw_success_without_otp(self):
        assert not getattr(self.user, "otp_enabled", False)

        response = self.client.post(self.url, {}, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        with pytest.raises(self.user_model.DoesNotExist):
            self.user_model.objects.get(pk=self.user.pk)

    def test_withdraw_success_with_otp(self):
        secret = pyotp.random_base32()
        self.user.otp_secret = secret
        self.user.otp_enabled = True
        self.user.save()

        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        response = self.client.post(self.url, {"otp_code": valid_code}, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        with pytest.raises(self.user_model.DoesNotExist):
            self.user_model.objects.get(pk=self.user.pk)

    def test_withdraw_fail_missing_otp_code(self):
        secret = pyotp.random_base32()
        self.user.otp_secret = secret
        self.user.otp_enabled = True
        self.user.save()

        response = self.client.post(self.url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "otp_code" in response.data

    def test_withdraw_fail_invalid_otp_code(self):
        secret = pyotp.random_base32()
        self.user.otp_secret = secret
        self.user.otp_enabled = True
        self.user.save()

        response = self.client.post(self.url, {"otp_code": "000000"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "유효하지 않은 OTP 코드입니다." in response.data["otp_code"][0]
