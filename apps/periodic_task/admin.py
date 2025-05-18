from django.contrib import admin

from apps.periodic_task.models import MultiTypePeriodicTask


@admin.register(MultiTypePeriodicTask)
class PeriodicTaskAdmin(admin.ModelAdmin):
    list_display = ["name", "task"]
    search_fields = ["name"]
    list_filter = ["task_type", "is_frozen"]
    raw_id_fields = ["task"]
