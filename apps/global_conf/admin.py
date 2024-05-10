from django.contrib import admin

from apps.global_conf.models import GlobalConfig


@admin.register(GlobalConfig)
class GlobalConfAdmin(admin.ModelAdmin):
    list_display = ("name", "value_type", "value", "description")
