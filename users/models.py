from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from materials.models import Course


class UserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя."""

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if (
            extra_fields.get("is_staff") is not True
            or extra_fields.get("is_superuser") is not True
        ):
            raise ValueError(
                "Суперпользователь должен иметь is_staff=True и is_superuser=True."
            )

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="+7 999 999 99 99",
    )
    city = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Укажите свой город",
    )
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Аватар"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    update_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления"
    )

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]


class Payment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="payments",
    )

    paid_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оплаченный курс",
        related_name="course_payments",
    )

    amount_rub = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма в рублях",
        default=0.0,
    )

    amount_cents = models.PositiveIntegerField(
        verbose_name="Сумма в копейках", default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )

    payment_url = models.URLField(
        verbose_name="Ссылка на оплату", blank=True, null=True, max_length=500
    )

    def __str__(self):
        target = self.paid_course
        return f"Платеж {self.user.email} — {target} — {self.amount_rub} ₽"

    class Meta:
        ordering = ["-created_at"]
