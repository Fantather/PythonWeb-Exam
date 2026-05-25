from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.managers import UserManager


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, 
        db_index=True,
        verbose_name=_("Created at")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at")
    )

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("First name")
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("Last name")
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        verbose_name=_("Username")
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name=_("Email address")
    )
    avatar = models.ImageField(
        upload_to="users/%Y/%m/%d/",
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_("Avatar")
    )
    birthday = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Birthday")
    )
    
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("Staff status"),
        help_text=_("Designates whether the user can log into this admin site.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Designates whether this user should be treated as active.")
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:     # pyright: ignore[reportIncompatibleVariableOverride]
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return f"{self.email}: {self.username}"