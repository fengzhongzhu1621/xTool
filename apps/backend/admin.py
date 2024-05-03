from django.contrib import admin

from apps.backend.models import Data


@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ["id", "key", "value", "type", "expire_at"]
