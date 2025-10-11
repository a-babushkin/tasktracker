from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserApiTests(APITestCase):

    def setUp(self):
        """Создаем тестовых пользователей и аутентификацию"""
        self.admin_user = User.objects.create(
            email="admin@example.com", password="password123", is_staff=True, is_superuser=True
        )
        self.normal_user = User.objects.create(email="user@example.com", password="password123")
        self.client.force_authenticate(user=self.admin_user)

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
        self.assertEqual(str(self.admin_user), response.data["results"][0]["email"])

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
