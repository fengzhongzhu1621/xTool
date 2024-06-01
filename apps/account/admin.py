from django.contrib import admin

from apps.account.models import Users


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "username",
        "first_name",
        "last_name",
        "gender",
        "email",
        "mobile",
        "avatar",
        "user_type",
        "dept_id",
        "is_superuser",
        "is_staff",
        "is_active",
        "last_login",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
