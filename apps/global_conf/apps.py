from django.apps import AppConfig
from django.db.models.signals import post_migrate


def app_ready_handler(sender, **kwargs):
    pass


class GlobalConfigConfig(AppConfig):
    name = "apps.global_conf"
    verbose_name = "Global Config"

    def ready(self):
        post_migrate.connect(app_ready_handler, sender=self)
