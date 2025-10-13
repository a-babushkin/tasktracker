from django.contrib.auth.models import AbstractUser
from django.db import models
from transliterate import translit, slugify

from tracker.services import get_full_name


class Position(models.Model):
    """Модель Должности"""
    title = models.CharField(verbose_name="Должность", max_length=100, unique=True)
    slug = models.SlugField(verbose_name="Slug", max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(translit(self.title, "ru", reversed=True))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"
        ordering = ["title"]


class User(AbstractUser):
    """Модель сотрудника"""
    username = None
    surname = models.CharField(
        verbose_name="Отчество",
        max_length=20,
        blank=True,
        null=True,
        help_text="Введите отчество",
    )
    email = models.EmailField(
        verbose_name="E-mail",
        unique=True,
        help_text="Введите электронную почту"
    )
    position = models.ForeignKey(
        Position,
        verbose_name="Должность",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="users/avatars/",
        blank=True,
        null=True,
        help_text="Загрузите свое фото",
    )
    phone_number = models.CharField(
        verbose_name="Телефон",
        max_length=15,
        blank=True,
        null=True,
        help_text="Введите номер телефона",
    )
    tg_chat_id = models.CharField(
        verbose_name="Chat ID",
        max_length=100,
        blank=True,
        null=True,
        help_text="Укажите chat ID в Телеграм",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} {get_full_name(self)} - {self.position.title if self.position else 'Без должности'}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]
