from rest_framework import serializers

from tracker.models import Project, Status, Priority, Task, Comment
from tracker.services import get_full_name


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    status_title = serializers.ReadOnlyField(source='status.title')
    priority_title = serializers.ReadOnlyField(source='priority.title')
    project_title = serializers.ReadOnlyField(source='project.title')
    executor_full_name = serializers.SerializerMethodField()

    def get_executor_full_name(self, obj):
        return get_full_name(obj.executor)

    class Meta:
        model = Task
        fields = ("id", "title", "description", "start_date", "due_date", "status", "status_title", "priority","priority_title",
                  "project", "project_title", "executor", "executor_full_name")


class CommentSerializer(serializers.ModelSerializer):
    task_title = serializers.ReadOnlyField(source='task.title')
    user_full_name = serializers.SerializerMethodField()

    def get_user_full_name(self, obj):
        return get_full_name(obj.user)

    class Meta:
        model = Comment
        fields = ("id", "text", "task", "task_title", "user", "user_full_name")
