from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import (PositionViewSet, UserCreateApiView, UserDestroyApiView, UserRetrieveApiView, UsersListApiView,
                         UserUpdateApiView)

app_name = UsersConfig.name

router = SimpleRouter()
router.register(r"positions", PositionViewSet)
urlpatterns = [
    path("", UsersListApiView.as_view(), name="user_list"),
    path("<int:pk>/", UserRetrieveApiView.as_view(), name="user_retrieve"),
    path("register/", UserCreateApiView.as_view(), name="register"),
    path("<int:pk>/delete/", UserDestroyApiView.as_view(), name="user_delete"),
    path("<int:pk>/update/", UserUpdateApiView.as_view(), name="user_update"),
    path(
        "login/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_refresh",
    ),
]
urlpatterns += router.urls
