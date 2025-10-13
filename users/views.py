from django.utils.text import slugify
from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from transliterate import translit

from users.models import User, Position
from users.permissions import IsOwner, IsStaff
from users.serializer import UserSerializer, PositionSerializer


class PositionViewSet(viewsets.ModelViewSet):
    """Контроллер для работы со статусами"""
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = (IsAuthenticated, IsStaff)
    swagger_tags = ["Positions"]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        title = data.get('title', '')
        if not data.get('slug') and title:
            data['slug'] = slugify(translit(title, "ru", reversed=True))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserCreateApiView(CreateAPIView):
    """Контроллер для создания (регистрации) нового пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        """метод кеширующий пароль при создании пользователя"""
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UsersListApiView(ListAPIView):
    """Контроллер получения списка пользователей"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)
    ordering_fields = ["email"]


class UserRetrieveApiView(RetrieveAPIView):
    """Контроллер получения детализации пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser | IsOwner,)


class UserUpdateApiView(UpdateAPIView):
    """Контроллер обновления пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser | IsOwner,)

    def perform_update(self, serializer):
        """метод кеширующий пароль при обновлении пользователя"""
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserDestroyApiView(DestroyAPIView):
    """Контроллер удаления пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser | IsOwner,)
