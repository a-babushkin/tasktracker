from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from tracker.models import Comment, Priority, Project, Status, Task
from users.models import Position, User


class Command(BaseCommand):
    """Команда для настройки групп"""

    def handle(self, *args, **options):
        # Создаем группы, если их еще нет
        users, created = Group.objects.get_or_create(name="Пользователи")
        admins, created = Group.objects.get_or_create(name="Администраторы")

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

        # Начальные установки должностей
        position_titles = [
            ("Администратор", "administrator"),
            ("Менеджер", "menedger"),
            ("Сотрудник", "sotrudnik"),
        ]

        for title, slug in position_titles:
            position, created = Position.objects.get_or_create(title=title, slug=slug)

        # Создаем суперпользователя, если он еще не существует
        user, created = User.objects.get_or_create(
            email="admin@mail.ru",
            defaults={
                "last_name": "Бабушкин",
                "first_name": "Андрей",
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
                "position_id": 1,
            },
        )
        if created:
            user.set_password("12345")
            user.save()
            user.groups.add(admins)

        user, created = User.objects.get_or_create(
            email="user@mail.ru",
            defaults={
                "last_name": "Филенков",
                "first_name": "Василий",
                "is_active": True,
                "is_staff": True,
                "position_id": 3,
            },
        )
        if created:
            user.set_password("12345")
            user.save()
            user.groups.add(users)

        project, created = Project.objects.get_or_create(title="Строительство дома")
        if created:
            project.save()

        task1, created = Task.objects.get_or_create(
            title="Task 1",
            status=status,
            priority=priority,
            project=project,
            executor=user,
        )
        if created:
            task1.save()

        task2, created = Task.objects.get_or_create(
            title="Task 2",
            status=status,
            priority=priority,
            project=project,
            executor=user,
        )
        if created:
            task2.save()

        task3, created = Task.objects.get_or_create(
            title="Task 3",
            status=status,
            priority=priority,
            project=project,
            executor=user,
        )
        if created:
            task3.save()

        comment1 = Comment.objects.create(text="Comment 1", user=user, task=task1)
        if created:
            comment1.save()

        parent_task, created = Task.objects.get_or_create(
            title="Parent Task",
            status=status,
            priority=priority,
            project=project,
            executor=user,
        )
        if created:
            parent_task.save()

        # Создание зависимой задачи
        dependent_task, created = Task.objects.get_or_create(
            title="Dependent Task",
            status=status,
            priority=priority,
            project=project,
            executor=user,
        )
        if created:
            dependent_task.save()
