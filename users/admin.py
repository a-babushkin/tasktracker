from django.contrib import admin

from users.models import User, Position


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "id", "email", "position__title")

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("id", "title")
