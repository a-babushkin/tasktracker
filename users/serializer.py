from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.models import Position, User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class PositionSerializer(ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Название должность не может быть пустым.")
        return value
