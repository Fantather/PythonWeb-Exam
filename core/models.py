from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from core.managers import UserManager

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, 
        db_index=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    first_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    avatar = models.ImageField(
        upload_to="users/%Y/%m/%d/",
        blank=True,
        null=True,
        max_length=255,
    )
    birthday = models.DateField(
        null=True,
        blank=True,
    )

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta(TimeStampedModel.Meta):
        verbose_name = "User"
        verbose_name_plural = "Users"


    def __str__(self):
        return f"{self.email}: {self.username}"


    