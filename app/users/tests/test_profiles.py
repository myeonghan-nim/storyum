import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from io import BytesIO
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from users.models import Profile


@pytest.mark.django_db
class TestProfileAPI:
    @pytest.fixture(autouse=True)
    def setup(self, django_user_model):
        self.user = django_user_model.objects.create_user(email="user@example.com", password="strong-pass123", username="testuser")

        self.client = APIClient()
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

        login_url = reverse("users-login-list")
        resp = self.client.post(login_url, {"email": self.user.email, "password": "strong-pass123"}, format="json")
        token = resp.data["token"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        self.url = reverse("users-profiles-list")

    def _make_image_file(self, name="avatar.png"):
        buf = BytesIO()
        Image.new("RGB", (100, 100), color="blue").save(buf, format="PNG")
        buf.seek(0)
        return SimpleUploadedFile(name, buf.read(), content_type="image/png")

    def test_profile_create_success(self):
        data = {"bio": "Hello, Storyum!", "website": "https://storyum.example.com", "avatar": self._make_image_file()}
        response = self.client.post(self.url, data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["id"] == self.user.id
        assert response.data["bio"] == "Hello, Storyum!"
        assert response.data["website"] == "https://storyum.example.com"
        assert response.data["avatar"] == f"https://testserver:80/media/avatars/{response.data['avatar'].split('/')[-1]}"

        self.user.refresh_from_db()
        assert hasattr(self.user, "profile")
        assert self.user.profile.bio == "Hello, Storyum!"
        assert self.user.profile.website == "https://storyum.example.com"
        assert self.user.profile.avatar.name.startswith("avatars/")
        assert self.user.profile.avatar.url.startswith(settings.MEDIA_URL + "avatars/")
        assert self.user.profile.avatar.url.endswith(response.data["avatar"].split("/")[-1])

    def test_profile_create_fail_already_exists(self):
        Profile.objects.create(user=self.user, bio="Existing")

        data = {"bio": "New Bio"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid" in response.data
        assert response.data["invalid"][0] == "프로필이 이미 존재합니다."

    def test_profile_create_fail_invalid_website(self):
        data = {"bio": "Test", "website": "ftp://invalid.url"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "website" in response.data
        assert response.data["website"][0] == "올바른 URL을 입력해주세요."

    def test_profile_create_fail_long_bio(self):
        data = {"bio": "a" * 256, "website": "https://storyum.example.com"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "bio" in response.data
        assert response.data["bio"][0] == "소개는 255자 이하여야 합니다."
