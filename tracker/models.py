from django.db import models
from transliterate import slugify, translit

from users.models import User


class Project(models.Model):
    """Описание модели Проекта"""

    title = models.CharField(verbose_name="Название", max_length=255)
    description = models.TextField(verbose_name="Описание", blank=True)
    start_date = models.DateTimeField(verbose_name="Создан", auto_now_add=True)
    end_date = models.DateTimeField(verbose_name="Завершен", blank=True, null=True)
    is_active = models.BooleanField(verbose_name="Активный", default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["start_date"]


class Priority(models.Model):
    """Описание модели Приоритета"""

    title = models.CharField(verbose_name="Название", max_length=20, unique=True)
    slug = models.SlugField(verbose_name="Slug", max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(translit(self.title, "ru", reversed=True))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Приоритет"
        verbose_name_plural = "Приоритеты"
        ordering = ["title"]


class Status(models.Model):
    """Описание модели Статуса"""

    title = models.CharField(verbose_name="Название", max_length=20, unique=True)
    slug = models.SlugField(verbose_name="Slug", max_length=20, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(translit(self.title, "ru", reversed=True))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ["title"]


class Task(models.Model):
    """Описание модели Задачи"""

    title = models.CharField(verbose_name="Название", max_length=200)
    description = models.TextField(verbose_name="Описание", blank=True)
    start_date = models.DateTimeField(verbose_name="Создана", auto_now_add=True)
    due_date = models.DateTimeField(verbose_name="Дата исполнения", null=True, blank=True)
    status = models.ForeignKey(Status, verbose_name="Статус", related_name="tasks", on_delete=models.CASCADE)
    priority = models.ForeignKey(Priority, verbose_name="Приоритет", related_name="tasks", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, verbose_name="Проект", related_name="tasks", on_delete=models.CASCADE)
    executor = models.ForeignKey(
        User, verbose_name="Исполнитель", related_name="tasks", on_delete=models.SET_NULL, null=True, blank=True
    )
    parent_task = models.ForeignKey(
        "self",
        verbose_name="Родительская задача",
        related_name="subtasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["title"]


class Comment(models.Model):
    """Описание модели Комментария"""

    text = models.TextField(
        verbose_name="Текст комментария",
    )
    created_at = models.DateTimeField(verbose_name="Создан", auto_now_add=True)
    task = models.ForeignKey(Task, verbose_name="Задача", related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="Исполнитель", related_name="comments", on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.user.email}"

    class Meta:
        verbose_name = "Коментарий"
        verbose_name_plural = "Коментарии"
        ordering = ["text"]
