from django.contrib import admin

from apps.http_client.models import RequestApiConfig, RequestSystemConfig


@admin.register(RequestSystemConfig)
class RequestSystemConfigAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "code",
        "desc",
        "owners",
        "domain",
        "headers",
    ]


@admin.register(RequestApiConfig)
class RequestApiConfigAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "system_id",
        "code",
        "name",
        "path",
        "method",
        "desc",
        "request_headers",
        "request_params",
        "request_body",
    ]
