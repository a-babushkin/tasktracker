

from django.urls import reverse
from django.utils import timezone
from pytz import UTC
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from tracker.models import Project, Priority, Status, Task, Comment
from tracker.services import get_full_name
from users.models import User


class BaseViewSetTests(APITestCase):
    def setUp(self):
        """Начальные установки для тестирования"""
        self.user = User.objects.create(email="user@mail.ru", is_staff=True, first_name="Arthur",
                                        last_name="Conan Doyle")

        self.status_new = Status.objects.create(title="новая", slug="novaja")
        self.status_work = Status.objects.create(title="в работе", slug="v-rabote")
        self.priority_high = Priority.objects.create(title="высокий", slug="vysoliy")
        self.priority_average = Priority.objects.create(title="средний", slug="sredniy")
        self.project1 = Project.objects.create(title="Project 1")

        self.task1 = Task.objects.create(title="Task 1", status=self.status_work, priority=self.priority_average,
                                         project=self.project1, executor=self.user)
        self.task2 = Task.objects.create(title="Task 2", status=self.status_work, priority=self.priority_average,
                                         project=self.project1, executor=self.user)
        self.task3 = Task.objects.create(title="Task 3", status=self.status_new, priority=self.priority_average,
                                         project=self.project1, executor=self.user)

        self.comment1 = Comment.objects.create(text="Comment 1", user=self.user, task=self.task1)

        self.access_token = str(AccessToken.for_user(self.user))
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")


class PriorityViewSetTests(BaseViewSetTests):

    def test_list_priorities(self):
        """Тестирование получения списка приоритетов"""
        response = self.client.get("/tracker/priorities/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Priority.objects.count(), 2)

    def test_create_priority(self):
        """Тестирование создания приоритета"""
        data = {
            "title": "New Priority"
        }
        response = self.client.post("/tracker/priorities/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Priority.objects.count(), 3)
        self.assertEqual(Priority.objects.get(id=response.data["id"]).title, "New Priority")

    def test_update_priority(self):
        """Тестирование обновления приоритета"""
        data = {
            "title": "Updated Priority"
        }
        response = self.client.put(f"/tracker/priorities/{self.priority_average.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.priority_average.refresh_from_db()
        self.assertEqual(self.priority_average.title, "Updated Priority")
        self.assertEqual(self.priority_average.slug, "sredniy")

    def test_delete_priority(self):
        """Тестирование удаления приоритета"""
        response = self.client.delete(f"/tracker/priorities/{self.priority_average.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Priority.objects.count(), 1)

    def test_unauthenticated_user_access(self):
        """Тестирование доступа неаутентифицированного пользователя"""
        self.client.logout()
        response = self.client.get("/tracker/priorities/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ditail_priority(self):
        """Тестирование вывода информации по конкретному приоритету"""
        response = self.client.get(f"/tracker/priorities/{self.priority_average.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "средний")
        self.assertEqual(str(self.priority_average), "средний")


class StatusViewSetTests(BaseViewSetTests):

    def test_list_statuses(self):
        """Тестирование получения списка статусов"""
        response = self.client.get("/tracker/statuses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Status.objects.count(), 2)

    def test_create_status(self):
        """Тестирование создания статуса"""
        data = {
            "title": "New Status"
        }
        response = self.client.post("/tracker/statuses/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Status.objects.count(), 3)
        self.assertEqual(Status.objects.get(id=response.data["id"]).title, "New Status")

    def test_update_status(self):
        """Тестирование обновления статуса"""
        data = {
            "title": "Updated Status"
        }
        response = self.client.put(f"/tracker/statuses/{self.status_new.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.status_new.refresh_from_db()
        self.assertEqual(self.status_new.title, "Updated Status")

    def test_delete_status(self):
        """Тестирование удаления статуса"""
        response = self.client.delete(f"/tracker/statuses/{self.status_new.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Status.objects.count(), 1)

    def test_unauthenticated_user_access(self):
        """Тестирование доступа неаутентифицированного пользователя"""
        self.client.logout()
        response = self.client.get("/tracker/statuses/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ditail_status(self):
        """Тестирование вывода информации по конкретному приоритету"""
        response = self.client.get(f"/tracker/statuses/{self.status_new.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "новая")
        self.assertEqual(str(self.status_new), "новая")


class ProjectViewSetTests(BaseViewSetTests):

    def test_list_projects(self):
        """Тестирование получения списка проектов"""
        response = self.client.get("/tracker/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Project.objects.count(), 1)

    def test_create_project(self):
        """Тестирование создания проекта"""
        data = {
            "title": "New Project",
        }
        response = self.client.post("/tracker/projects/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.get(id=response.data["id"]).title, "New Project")

    def test_update_project(self):
        """Тестирование обновления проекта"""
        data = {"title": "Updated Project"}
        response = self.client.put(f"/tracker/projects/{self.project1.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project1.refresh_from_db()
        self.assertEqual(self.project1.title, "Updated Project")

    def test_delete_project(self):
        """Тестирование удаления проекта"""
        response = self.client.delete(f"/tracker/projects/{self.project1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)

    def test_unauthenticated_user_access(self):
        """Тестирование доступа неаутентифицированного пользователя"""
        self.client.logout()
        response = self.client.get("/tracker/projects/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ditail_project(self):
        """Тестирование вывода информации по конкретному проекту"""
        response = self.client.get(f"/tracker/projects/{self.project1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Project 1")
        self.assertEqual(str(self.project1), "Project 1")


class CommentViewSetTests(BaseViewSetTests):

    def test_list_comments(self):
        """Тестирование получения списка комментариев"""
        response = self.client.get("/tracker/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.count(), 1)

    def test_create_comment(self):
        """Тестирование создания комментария"""
        data = {
            "text": "New Comment",
            "user": self.user.id,
            "task": self.task1.id
        }
        response = self.client.post("/tracker/comments/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.get(id=response.data["id"]).text, "New Comment")

    def test_update_comment(self):
        """Тестирование обновления комментария"""
        data = {
            "text": "Updated Comment",
            "user": self.user.id,
            "task": self.task1.id
        }
        response = self.client.put(f"/tracker/comments/{self.comment1.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment1.refresh_from_db()
        self.assertEqual(self.comment1.text, "Updated Comment")

    def test_delete_comment(self):
        """Тестирование удаления комментария"""
        response = self.client.delete(f"/tracker/comments/{self.comment1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_unauthenticated_user_access(self):
        """Тестирование доступа неаутентифицированного пользователя"""
        self.client.logout()
        response = self.client.get("/tracker/comments/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ditail_comment(self):
        """Тестирование вывода информации по конкретному комментарию"""
        response = self.client.get(f"/tracker/comments/{self.comment1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "Comment 1")
        self.assertEqual(str(self.comment1), "Comment by user@mail.ru")


class TaskViewSetTests(BaseViewSetTests):

    def test_list_tasks(self):
        """Тестирование получения списка задач"""
        response = self.client.get("/tracker/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.count(), 3)

    def test_create_comment(self):
        """Тестирование создания задачи"""
        data = {
            "title": "New Task",
            "status": self.status_new.id,
            "priority": self.priority_average.id,
            "project": self.project1.id
        }
        response = self.client.post("/tracker/tasks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 4)
        self.assertEqual(Task.objects.get(id=response.data["id"]).title, "New Task")

    def test_update_comment(self):
        """Тестирование обновления задачи"""
        data = {
            "title": "Updated Task",
            "status": self.status_new.id,
            "priority": self.priority_average.id,
            "project": self.project1.id
        }
        response = self.client.put(f"/tracker/tasks/{self.task1.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, "Updated Task")

    def test_delete_comment(self):
        """Тестирование удаления задачи"""
        response = self.client.delete(f"/tracker/tasks/{self.task1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 2)

    def test_unauthenticated_user_access(self):
        """Тестирование доступа неаутентифицированного пользователя"""
        self.client.logout()
        response = self.client.get("/tracker/tasks/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ditail_comment(self):
        """Тестирование вывода информации по конкретному комментарию"""
        response = self.client.get(f"/tracker/tasks/{self.task1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Task 1")
        self.assertEqual(str(self.task1), "Task 1")


class TestGetFullName(APITestCase):
    """Тестирование функции формирования полного имени пользователя"""

    class EmpStub:
        def __init__(self, first_name=None, last_name=None, username=None):
            self.first_name = first_name
            self.last_name = last_name
            self.username = username

    def test_full_name_present(self):
        emp = self.EmpStub(first_name="John", last_name="Doe", username="jdoe")
        self.assertEqual(get_full_name(emp), "John Doe")

    def test_first_name_only(self):
        emp = self.EmpStub(first_name="John", last_name=None, username="jdoe")
        self.assertEqual(get_full_name(emp), "John")

    def test_last_name_only(self):
        emp = self.EmpStub(first_name=None, last_name="Doe", username="jdoe")
        self.assertEqual(get_full_name(emp), "Doe")

    def test_no_names(self):
        emp = self.EmpStub(first_name=None, last_name=None, username="jdoe")
        self.assertEqual(get_full_name(emp), "jdoe")


class BusyEmployeesTestCase(BaseViewSetTests):

    def test_busy_employees(self):
        url = reverse('tracker:busy_employees')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = [{
            'executor': 'Arthur Conan Doyle',
            'active_tasks_count': 2,
            'active_tasks_titles': ['Task 1', 'Task 2'],
        }]

        self.assertEqual(response.json(), expected_data)


class ImportantTasksAPITest(BaseViewSetTests):
    def setUp(self):
        super().setUp()
        # Создание родительских задач
        self.parent_task = Task.objects.create(
            title="Parent Task",
            due_date=timezone.datetime(2025, 10, 20, tzinfo=UTC),
            executor=self.user,
            status=self.status_work, project=self.project1,
            priority=self.priority_average
        )

        # Создание зависимой задачи
        self.dependent_task = Task.objects.create(
            title="Dependent Task",
            due_date=timezone.datetime(2025, 10, 25, tzinfo=UTC),
            executor=self.user,
            parent_task=self.parent_task, status=self.status_new,
            project=self.project1, priority=self.priority_average
        )

        self.user2 = User.objects.create(email="user2@mail.ru", is_staff=True, first_name="Morgan",
                                         last_name="Freeman")

    def test_important_tasks(self):
        """Тест для проверки ответа функции important_tasks"""

        # Получаем список важных задач
        response = self.client.get(reverse('tracker:important_tasks'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Response data:", response.data)
        expected_response = [{
            'important_task': 'Dependent Task',
            'due_date': '2025-10-25T00:00:00Z',
            'available_employees': ['Morgan Freeman']
        }]

        # Проверка, что ответ соответствует ожиданиям
        self.assertEqual(response.json(), expected_response)
