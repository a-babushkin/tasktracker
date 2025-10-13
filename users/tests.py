from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User, Position


class BaseUsersApiTests(APITestCase):
    """Базовый класс для начальных настроек приложения Users"""

    def setUp(self):
        """Начальные установки для тестирования"""
        self.user = User.objects.create(
            email="user@mail.ru", is_staff=True, first_name="Arthur", last_name="Conan Doyle"
        )

        self.position1 = Position.objects.create(title="Сотрудник", slug="sotrudnik")
        self.position2 = Position.objects.create(title="Администратор", slug="administrator")

        """Создаем тестовых пользователей и аутентификацию"""
        self.admin_user = User.objects.create(
            email="admin@example.com",
            last_name="Moor",
            first_name="Demy",
            password="password123",
            is_staff=True,
            is_superuser=True,
            position=self.position2
        )
        self.normal_user = User.objects.create(
            email="user@example.com",
            last_name="Kravets",
            first_name="Leny",
            password="password123",
            position=self.position2
        )
        self.access_token = str(AccessToken.for_user(self.user))
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.client.force_authenticate(user=self.admin_user)


class PositionViewSetTests(BaseUsersApiTests):

    def test_list_positions(self):
        """Тестирование получения списка должностей"""
        response = self.client.get("/users/positions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Position.objects.count(), 2)

    def test_create_position(self):
        """Тестирование создания должности"""
        data = {"title": "New Position"}
        response = self.client.post("/users/positions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Position.objects.count(), 3)
        self.assertEqual(Position.objects.get(id=response.data["id"]).title, "New Position")

    def test_update_position(self):
        """Тестирование обновления должности"""
        data = {"title": "Updated Position"}
        response = self.client.put(f"/users/positions/{self.position1.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.position1.refresh_from_db()
        self.assertEqual(self.position1.title, "Updated Position")
        self.assertEqual(self.position1.slug, "sotrudnik")

    def test_delete_position(self):
        """Тестирование удаления должности"""
        response = self.client.delete(f"/users/positions/{self.position1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Position.objects.count(), 1)

    def test_unauthenticated_user_access(self):
        """Тестирование доступа неаутентифицированного пользователя"""
        self.client.logout()
        response = self.client.get("/users/positions/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ditail_position(self):
        """Тестирование вывода информации по конкретному приоритету"""
        response = self.client.get(f"/users/positions/{self.position1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Сотрудник")
        self.assertEqual(str(self.position1), "Сотрудник")


class UserApiTests(BaseUsersApiTests):

    def test_user_create(self):
        """Тест на создание пользователя"""
        data = {"email": "newuser@example.com", "password": "password123"}
        response = self.client.post("/users/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_user_list(self):
        """Тест на получение списка пользователей"""
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_user_retrieve(self):
        """Тест на получение данных пользователя"""
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["email"], "admin@example.com")
        self.assertEqual(str(self.admin_user), 'admin@example.com Demy   Moor - Администратор')

    def test_user_update(self):
        """Тест на обновление пользователя"""
        data = {"email": "updateduser@example.com", "password": "newpassword123"}
        response = self.client.put(f"/users/{self.normal_user.id}/update/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.email, "updateduser@example.com")

    def test_user_delete(self):
        """Тест на удаление пользователя"""
        response = self.client.delete(f"/users/{self.normal_user.id}/delete/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.normal_user.id).exists())
