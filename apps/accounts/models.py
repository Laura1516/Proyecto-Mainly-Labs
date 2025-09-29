from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


# Custom manager to handle user and superuser creation
class CustomManagerUser(UserManager):
    def create_user(self, username, email, password, **extra_fields):
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("role", "superadmin")
        return super().create_superuser(username, email, password, **extra_fields)


# Extended user model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('tech', 'Technician'),
        ('user', 'User'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )

    email = models.EmailField(max_length=100, unique=True, blank=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    avatar = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
        default="profiles/default.jpg"
    )

    def __str__(self):
        return self.username

    objects = CustomManagerUser()
