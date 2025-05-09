from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()
