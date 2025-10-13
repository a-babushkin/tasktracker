from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tracker.apps import TrackerConfig

from .views import (CommentViewSet, PriorityViewSet, ProjectViewSet, StatusViewSet, TaskViewSet, busy_employees,
                    important_tasks)

app_name = TrackerConfig.name
router = DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"priorities", PriorityViewSet)
router.register(r"statuses", StatusViewSet)
router.register(r"comments", CommentViewSet)
router.register(r"tasks", TaskViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("busy_employees/", busy_employees, name="busy_employees"),
    path("important_tasks/", important_tasks, name="important_tasks"),
]
