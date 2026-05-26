from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager

from core.models import TimeStampedModel

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email field must be set")
        if not username:
            raise ValueError("Username field must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)
    

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