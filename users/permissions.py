from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли текущий пользователь владельцем"""

    def has_object_permission(self, request, view, obj):
        return obj.executor == request.user


class IsStaff(permissions.BasePermission):
    """Проверяет, является ли текущий пользователь админом"""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff
