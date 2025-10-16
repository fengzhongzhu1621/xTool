from django.contrib import admin

from apps.account.models import OperationLog, Users


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


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "request_id",
        "request_modular",
        "request_path",
        "request_body",
        "request_method",
        "request_msg",
        "request_ip",
        "request_browser",
        "request_os",
        "response_code",
        "response_content",
    ]
