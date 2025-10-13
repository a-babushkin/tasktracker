from django.utils import timezone
from rest_framework import serializers

from tracker.models import Comment, Priority, Project, Status, Task
from tracker.services import get_full_name


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Название проекта не может быть пустым.")
        return value

    def validate(self, data):
        start_date = data.get("start_date") or getattr(self.instance, "start_date", None)
        end_date = data.get("end_date") or getattr(self.instance, "end_date", None)
        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError("Дата завершения не может быть раньше даты начала задачи.")
        return data


class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = "__all__"

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Название приоритета не может быть пустым.")
        return value


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = "__all__"

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Название статуса не может быть пустым.")
        return value


class TaskSerializer(serializers.ModelSerializer):
    status_title = serializers.ReadOnlyField(source="status.title")
    priority_title = serializers.ReadOnlyField(source="priority.title")
    project_title = serializers.ReadOnlyField(source="project.title")
    executor_full_name = serializers.SerializerMethodField()

    def get_executor_full_name(self, obj):
        return get_full_name(obj.executor)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "start_date",
            "due_date",
            "status",
            "status_title",
            "priority",
            "priority_title",
            "project",
            "project_title",
            "executor",
            "executor_full_name",
        )

    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("Заголовок задачи не может быть пустым.")
        return value

    def validate_due_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Дата исполнения не может быть в прошлом.")
        return value

    def validate(self, data):
        start_date = data.get("start_date") or getattr(self.instance, "start_date", None)
        due_date = data.get("due_date") or getattr(self.instance, "due_date", None)
        if due_date and start_date and due_date < start_date:
            raise serializers.ValidationError("Дата исполнения не может быть раньше даты создания задачи.")
        return data


class CommentSerializer(serializers.ModelSerializer):
    task_title = serializers.ReadOnlyField(source="task.title")
    user_full_name = serializers.SerializerMethodField()

    def get_user_full_name(self, obj):
        return get_full_name(obj.user)

    class Meta:
        model = Comment
        fields = ("id", "text", "task", "task_title", "user", "user_full_name")

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("Текст комментария не может быть пустым.")
        return value
