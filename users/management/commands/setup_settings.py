from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from tracker.models import Status, Priority
from users.models import User


class Command(BaseCommand):
    """Команда для настройки групп"""

    def handle(self, *args, **options):
        # Создаем группы, если их еще нет
        users, created = Group.objects.get_or_create(name="Пользователи")
        admins, created = Group.objects.get_or_create(name="Администраторы")

        # Создаем суперпользователя, если он еще не существует
        user, created = User.objects.get_or_create(email="admin@mail.ru", defaults={
            'is_active': True,
            'is_staff': True,
            'is_superuser': True
        })
        if created:
            user.set_password("12345")
            user.save()
            user.groups.add(admins)

        # Начальные установки статусов
        status_titles = [
            ("новая", "novaja"),
            ("в работе", "v-rabote"),
            ("Завершена", "zavershena"),
            ]

        for title, slug in status_titles:
            status, created = Status.objects.get_or_create(title=title, slug=slug)

        # Начальные установки приоритетов
        priority_titles = [
            ("Низкий", "nizkij"),
            ("Средний", "srednij"),
            ("Высокий", "vysokij"),
        ]

        for title, slug in priority_titles:
            priority, created = Priority.objects.get_or_create(title=title, slug=slug)
