from django.apps import AppConfig


class PeriodicTaskConfig(AppConfig):
    name = "apps.periodic_task"

    def ready(self):
        pass
